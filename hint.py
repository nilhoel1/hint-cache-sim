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
		if popTrace[x] > -1 and popTrace[x] != 0:
			#Sth was popped at x -> add popped element to dict
			toHint.append(popTrace[x])
	assert len(iTrace) == len(hints), "Hints calculated wrong!"
	#assert len(toHint) == 0, "All hints should be given!"
	hints.reverse()
	return(hints)


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

def cacheHintHitUpdate(addr, cacheSet):
	found = False
	for x in range(cacheSet.size-1):
		if cacheSet[x] == addr or found:
			found = True
			cacheSet[x] = cacheSet[x+1]
	cacheSet[cacheSet.size-1] = addr#TODO this should be ... = addr

def cacheHintHitUpdate(addr, cacheSet, ind):#Checked
	for x in range(ind,cacheSet.size-1):
		cacheSet[x] = cacheSet[x+1]	
	cacheSet[cacheSet.size-1] = addr

def hint(iTrace, hints, sets, associativity, progBar):
	cache = initCache(sets, associativity)
	hint_hits = []
	hits = 0
	misses = 0
	for x in range(len(iTrace)):
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'Hint-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % len(cache)
		cacheSet = cache[cacheSetNr]
		addr = iTrace[x]
		#check for hit
		hit = isHit(cacheSet, addr)
#		if 75 >= x >= 72:
#			print("HintSet:", cacheSet ,", Pos:", x, ", Addr:", addr, ", Set Nr.:", cacheSetNr, ", Hit:", hit)
		if hit == -1: 
			#Miss
			misses += 1
			hint_hits.append(0)
			if hints[x] != 1:
				cacheLRUMissUpdate(addr, cacheSet)
			#For a hint addr, wont get added
		else:
			#Hit
			hits +=1
			hint_hits.append(1)
			if hints[x] == 1:
				cacheHintHitUpdate(addr, cacheSet, hit)
			else:
				cacheLRUHitUpdate(addr, cacheSet)
	if progBar:
		print()
	return hits, misses, hint_hits
