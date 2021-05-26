import numpy as np
from progressBar import printProgressBar

def initCache(sets, associativity):
	#generate a dictionary for the cache
	cache = {}
	for x in range(sets):
		cache[x] = np.array(np.zeros(associativity))
	#generate a dictionary for the cache distances
	cacheDist = {}
	for x in range(sets):
		cacheDist[x] = np.array(np.zeros(associativity))
		for y in range(associativity):
			cacheDist[x][y] = -1
	return cache, cacheDist

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
	for x in range(start+1, len(iTrace)):
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
	hits = 0
	misses = 0
	cache, cacheDist = initCache(sets, associativity)
	for x in range(len(iTrace)):
		updateDistances(cacheDist)
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'OPT-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % len(cache)
		cacheSet = cache[cacheSetNr]
		#check for hit
		hit = np.where(cacheSet == iTrace[x])
		if hit[0].size == 0: 
			#Miss
			misses += 1
			#CacheSet is full, compute highest distance.
			ind = highestForwardDistance(cacheDist, cacheSetNr)
			popTrace.append(cacheSet[ind])
			cacheSet[ind] = iTrace[x]
			cacheDist[cacheSetNr][ind] = forwardDistance(iTrace, x, iTrace[x])
		else:
			#Hit
			hits += 1
			popTrace.append(-1)
			#Update Distance for hitted entry
			cacheDist[cacheSetNr][hit[0]] = forwardDistance(iTrace, x, iTrace[x])
	if progBar:
		print()
	return hits, misses, popTrace