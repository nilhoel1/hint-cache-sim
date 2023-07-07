#from numba import jit
import numpy as np

from progressBar import printProgressBar

def initCache(sets, associativity):
	#generate a dictionary for the cache
	cache = {}
	for x in range(sets):
		cache[x] = np.array(np.zeros(associativity, dtype=int))
	return cache

#@jit
def isHit(cacheSet, addr):
	for x in range(cacheSet.size):
		if cacheSet[x] == addr:
			return x
	return -1

#@jit
def cacheLRUMissUpdate(addr, cacheSet):#Checked
	#LRU Update
	for x in range(cacheSet.size-1, 0, -1):
		cacheSet[x] = cacheSet[x-1]
	cacheSet[0] = addr

#@jit
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
			printProgressBar(x, len(iTrace)-1, prefix = 'LRU-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % len(cache)
		#check for hit
		hit = isHit(cache[cacheSetNr], iTrace[x])
		if hit == -1:
			#Miss
			misses +=1
			cacheLRUMissUpdate(iTrace[x], cache[cacheSetNr])
		else:
			#Hit
			hits +=1
			cacheLRUHitUpdate(iTrace[x], cache[cacheSetNr])
	if progBar:
		print()
	return hits, misses
