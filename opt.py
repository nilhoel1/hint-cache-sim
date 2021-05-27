import numpy as np
from progressBar import printProgressBar

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
				assert (cacheDist[x][y] > -2),"This should not be possible!"

def opt(iTrace, sets, associativity, progBar):
	popTrace = []
	opt_hits = []
	hits = 0
	misses = 0
	cache, cacheDist = initCache(sets, associativity)
	for x in range(len(iTrace)):
		updateDistances(cacheDist)
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'OPT-Sim:', suffix = 'Complete', length = 50)
#		if 75 >= x >= 72:
#			print("Hi")
		#Check the Set
		addr = iTrace[x]
		cacheSetNr = addr % len(cache)
		cacheSet = cache[cacheSetNr]
		#check for hit
		hit = isHit(cacheSet, addr)
#		if 75 >= x >= 72:
#			print("OptSet:", cacheSet ,", Pos:", x, ", Addr:", addr, ", Set Nr.:", cacheSetNr, ", Hit:", hit)
		if hit == -1: 
			#Miss
			misses += 1
			opt_hits.append(0)
			#CacheSet is full, compute highest distance.
			ind = highestForwardDistance(cacheDist, cacheSetNr)
			fdInd = cacheDist[cacheSetNr][ind] #Forward distance of object with highest distance
			fdAddr = forwardDistance(iTrace, x, addr)
			if fdAddr < fdInd or fdInd == -1: #fd of add is smaller than fd of object in cache
				popTrace.append(cacheSet[ind])
				cacheSet[ind] = addr
				cacheDist[cacheSetNr][ind] = fdAddr
			else:
				popTrace.append(addr)
		else:
			#Hit
			hits += 1
			opt_hits.append(1)
			popTrace.append(-1)
			#Update Distance for hitted entry
			cacheDist[cacheSetNr][hit] = forwardDistance(iTrace, x, addr)
	if progBar:
		print()
	return hits, misses, popTrace, opt_hits