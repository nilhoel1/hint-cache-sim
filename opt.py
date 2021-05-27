import numpy as np
from progressBar import printProgressBar

checkIntegrity = False

def initCache(sets, associativity):
	#generate a dictionary for the cache
	cache = {}
	for x in range(sets):
		cache[x] = np.array(np.zeros(associativity, dtype=int))
	#generate a dictionary for the cache distances
	cacheDist = {}
	for x in range(sets):
		cacheDist[x] = np.array(np.zeros(associativity, dtype=int))
		for y in range(associativity):
			cacheDist[x][y] = -1
	return cache, cacheDist

def isHit(cacheSet, addr):
	for x in range(cacheSet.size):
		if cacheSet[x] == addr:
			return x
	return -1

def distanceTraceStack(iTrace):
	print("Start distance Trace")
	#calculate distances
	distTrace = [[np.array([iTrace[len(iTrace)-1]])]]
	#print(distTrace)
	#Walk itrace backwards and add distances
	for x in range(len(iTrace)-2, -1, -1):
		stack = distTrace[len(iTrace)-x-2].copy()
		try:
			indi = np.where(stack == iTrace[x])
			stack = np.delete(stack, indi)
			indi = None
		except:
			stack = stack
		#print(x)
		stack = np.append(stack, [iTrace[x]])
		distTrace.append(stack)
		stack = None
	#print(distTrace)
	return distTrace

#returns forward distance, -1 is infinity
def forwardDistance(iTrace, start, addr):
	distance = 1
	for x in range(start+1, len(iTrace), 1):
		if iTrace[x] != addr:
			distance += 1
		else:
			return distance
	return -1

#return index to address with highest fd, -1 should never be returned
def highestForwardDistance(cacheDist, setNr):
	indMaxDist = -1
	maxDist = -1
	for x in range(cacheDist[setNr].size):
		if cacheDist[setNr][x] == -1:
			return x
		elif cacheDist[setNr][x] > maxDist:
			indMaxDist = x
			maxDist = cacheDist[setNr][x]
	assert (indMaxDist > -1),"This should not be possible!"
	return indMaxDist

#Returns index of first found empty space, otherwise 0
def cacheHasEmptySpace(cacheSet):
	for x in range(cacheSet.size):
		if cacheSet[x] == 0:
			return x
	return 0

def updateDistances(cacheDist):
	for x in range(len(cacheDist)):
		for y in range(cacheDist[x].size):
			if cacheDist[x][y] > -1:
				cacheDist[x][y] -= 1
				assert (cacheDist[x][y] > -1),"This should not be possible!"

def integrityCheck(cacheDist, addr, pos, iTrace, cache, pop):
	maxi = -1
	for x in range(len(cacheDist)):
		for y in range(cacheDist[x].size):
				check = forwardDistance(iTrace, pos, cache[x][y])
				if check > maxi:
					maxi = check
				#print(pos)
				if check != cacheDist[x][y]:
					print("Check:", check, "Dist:",  cacheDist[x][y])
				assert check == cacheDist[x][y]
	if pop != -1: #pop = -1, means nothings been popped
		fdPop = forwardDistance(iTrace, pos, pop)
		if fdPop != -1: # distance = -1, means infinity.
#			print("dP:",fdPop,"Max:", maxi, "Pos:", pos)
			assert fdPop >= maxi
	return maxi



def opt(iTrace, sets, associativity, progBar):
	popTrace = []
	opt_hits = []
	opt_cache_trace = []
	hits = 0
	misses = 0
	cache, cacheDist = initCache(sets, associativity)
	for x in range(len(iTrace)):
		updateDistances(cacheDist)
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'OPT-Sim:', suffix = 'Complete', length = 50)
		addr = iTrace[x]
		cacheSetNr = addr % len(cache)
		cacheSet = cache[cacheSetNr]
		opt_cache_trace.append(cache[0].copy())
		#check for hit
		hit = isHit(cacheSet, addr)
		if hit == -1: 
			#Miss
			misses += 1
			opt_hits.append(0)
			#CacheSet is full, compute highest distance.
			ind = highestForwardDistance(cacheDist, cacheSetNr)
			fdInd = cacheDist[cacheSetNr][ind] #Forward distance of object with highest distance
			fdAddr = forwardDistance(iTrace, x, addr)
			#fd of add is smaller than fd of object in cache
			# remember -1 = infinity!
			if (fdAddr < fdInd) or ((fdInd == -1) and (fdAddr != -1)): 
				popTrace.append(cacheSet[ind])
				assert cacheSet[ind] != addr
				cacheSet[ind] = addr
				cacheDist[cacheSetNr][ind] = fdAddr
			else:
				#fdAddr is higher than fd of entries.
				popTrace.append(addr) 
		else:
			#Hit
			hits += 1
			opt_hits.append(1)
			popTrace.append(-1)
			#Update Distance for hitted entry
			cacheDist[cacheSetNr][hit] = forwardDistance(iTrace, x, addr)
			#For a hit addr == cacheSet[hit]
		if checkIntegrity:
			integrityCheck(cacheDist, addr, x, iTrace, cache, popTrace[x])
	if progBar:
		print()
	return hits, misses, popTrace, opt_hits, opt_cache_trace