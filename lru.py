import numpy as np

from progressBar import printProgressBar

def initCache(sets, associativity):
	#generate a dictionary for the cache
	cache = {}
	for x in range(sets):
		cache[x] = np.array(np.zeros(associativity, dtype=int))
	return cache

def isHit(cacheSet, addr):
	for x in range(cacheSet.size):
		if cacheSet[x] == addr:
			return x
	return -1

def cacheLRUMissUpdate(addr, cacheSet):#Checked
	#LRU Update
	for x in range(cacheSet.size-1, 0, -1):
		cacheSet[x] = cacheSet[x-1]
	cacheSet[0] = addr

def cacheLRUHitUpdate(addr, cacheSet):#Checked
	found = False
	for x in range(cacheSet.size-1, 0, -1):
		if cacheSet[x] == addr or found:
			found = True
			cacheSet[x] = cacheSet[x-1]
	cacheSet[0] = addr


def lru(iTrace, sets, associativity, progBar):
	cache = initCache(sets, associativity)
	hits = 0
	misses = 0
	for x in range(len(iTrace)):
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'Hint-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		addr = iTrace[x]
		cacheSetNr = addr % len(cache)
		cacheSet = cache[cacheSetNr]
		#check for hit
		hit = isHit(cacheSet, addr)
		if hit == -1: 
			#Miss
			misses +=1
			cacheLRUMissUpdate(addr, cacheSet)
		else:
			#Hit
			hits +=1
			cacheLRUHitUpdate(addr, cacheSet)
	if progBar:
		print()
	return hits, misses