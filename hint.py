import numpy as np

from progressBar import printProgressBar

def initCache(sets, associativity):
	#generate a dictionary for the cache
	cache = {}
	for x in range(sets):
		cache[x] = np.array(np.zeros(associativity))
	return cache

def popToHint(popTrace, iTrace):
	hints = []
	toHint = [] #Dict of address:bool
	assert len(iTrace) == len(popTrace), "PopTrace calculated wrong!"
	#Walk PopTrace backwards
	for x in range(len(popTrace)-1, -1, -1):
		#Handle Hints
		if iTrace[x] in toHint: 
			#adress has been seen on popTrace, so its hinted
			hints.append(1)
			toHint.remove(iTrace[x])
		else:
			hints.append(0)
		#Add poped elemts to toHint
		if popTrace[x] > 0:
			#Sth was popped at x -> add popped element to dict
			toHint.append(popTrace[x])
	assert len(iTrace) == len(hints), "Hints calculated wrong!"
	hints.reverse()
	return(hints)


def cacheLRUMissUpdate(addr, cacheSet):
	#LRU Update
	for x in range(cacheSet.size-1, 0, -1):
		cacheSet[x] = cacheSet[x-1]
	cacheSet[0] = addr

def cacheLRUHitUpdate(addr, cacheSet):
	found = False
	for x in range(cacheSet.size-1, 0, -1):
		if cacheSet[x] == addr or found:
			found = True
			cacheSet[x] = cacheSet[x-1]
	cacheSet[0] = addr

def cacheHintHitUpdate(addr, cacheSet):
	found = False
	for x in range(cacheSet.size-1):
		if cacheSet[x] == addr or found:
			found = True
			cacheSet[x] = cacheSet[x+1]
	cacheSet[cacheSet.size-1] = cacheSet[x]

def cacheHintHitUpdate(addr, cacheSet, ind):
	cacheSet[ind]

def hint(iTrace, hints, sets, associativity, progBar):
	cache = initCache(sets, associativity)
	hits = 0
	misses = 0
	for x in range(len(iTrace)):
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'Hint-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % len(cache)
		cacheSet = cache[cacheSetNr]
		#check for hit
		hit = np.where(cacheSet == iTrace[x])
		if hit[0].size == 0: 
			#Miss
			misses += 1
			if hints[x] != 1:
				cacheLRUMissUpdate(iTrace[x], cacheSet)
			#For a hint addr, wont get added
		else:
			#Hit
			hits +=1
			if hints[x] == 1:
				cacheHintHitUpdate(iTrace[x], cacheSet, hit[0])
			else:
				cacheLRUHitUpdate(iTrace[x], cacheSet)
	if progBar:
		print()
	return hits, misses