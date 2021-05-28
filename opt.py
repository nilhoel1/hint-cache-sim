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

#Not used Stack method (Is be a lot faster but uses exponential RAM!)
def distanceTraceStack(iTrace):
	print("Start distance Trace")
	#calculate distances
	distTrace = [[np.array([iTrace[len(iTrace)-1]])]]
	#Walk iTrace backwards and add distances
	for x in range(len(iTrace)-2, -1, -1):
		stack = distTrace[len(iTrace)-x-2].copy()
		try:
			indi = np.where(stack == iTrace[x])
			stack = np.delete(stack, indi)
			indi = None
		except:
			stack = stack
		stack = np.append(stack, [iTrace[x]])
		distTrace.append(stack)
		stack = None
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

#Reduces the forward distances of all objects in the cache by one
def updateDistances(cacheDist):
	for x in range(len(cacheDist)):
		for y in range(cacheDist[x].size):
			if cacheDist[x][y] > -1:
				cacheDist[x][y] -= 1
				assert (cacheDist[x][y] > -1),"This should not be possible!"

#Checks if the popped entry has the highest forward distance.
#This is very compute intensive, as distances are recomputed to check.
def integrityCheck(cacheDist, cacheSetNr, pos, iTrace, cache, pop):
	maxi = -1
	for y in range(cacheDist[cacheSetNr].size):
			check = forwardDistance(iTrace, pos, cache[cacheSetNr][y])
			if check > maxi:
				maxi = check
			#print(pos)
			if check != cacheDist[cacheSetNr][y]:
				print("Check:", check, "Dist:",  cacheDist[cacheSetNr][y])
			assert check == cacheDist[cacheSetNr][y]
	if pop != -1: #pop = -1, means nothings been popped
		fdPop = forwardDistance(iTrace, pos, pop)
		if fdPop != -1: # distance = -1, means infinity.
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
		cacheSetNr = iTrace[x] % len(cache)
		opt_cache_trace.append(cache[0].copy())
		#check for hit
		hit = isHit(cache[cacheSetNr], iTrace[x])
		if hit == -1: 
			#Miss
			misses += 1
			opt_hits.append(0)
			#get highest distances.
			ind = highestForwardDistance(cacheDist, cacheSetNr)
			fdInd = cacheDist[cacheSetNr][ind] #Forward distance of object with highest distance
			fdAddr = forwardDistance(iTrace, x, iTrace[x])
			#Always replace fdInd= -1 as it might be a empty cache entry
			#When fdAddr is higher fdInd replace Ind, remember -1 = infty
			if (((fdAddr < fdInd) or (fdInd == -1)) and (fdAddr != -1)): 
				#replace highest distance entry wirt iTrace[x]
				popTrace.append(cache[cacheSetNr][ind])
				cache[cacheSetNr][ind] = iTrace[x]
				cacheDist[cacheSetNr][ind] = fdAddr
			else:
				#Do nothing cache content has smaller distances
				popTrace.append(iTrace[x]) 
		else:
			#Hit
			hits += 1
			opt_hits.append(1)
			popTrace.append(-1)
			#Update Distance for hitted entry
			cacheDist[cacheSetNr][hit] = forwardDistance(iTrace, x, iTrace[x])
		if checkIntegrity:
			integrityCheck(cacheDist, cacheSetNr, x, iTrace, cache, popTrace[x])
	if progBar:
		print()
	return hits, misses, popTrace, opt_hits, opt_cache_trace