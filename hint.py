#from numba import jit
import numpy as np

from progressBar import printProgressBar
from lru import cacheLRUHitUpdate
from lru import cacheLRUMissUpdate
from lru import initCache
from lru import isHit

#This function generates hints from an Pop trace of OPT.
def popToHint(popTrace, iTrace):
	hints = []
	toHint = [] #Dict of address:bool
	assert len(iTrace) == len(popTrace), "PopTrace calculated wrong!"
	#Walk PopTrace backwards
	for x in range(len(popTrace)-1, -1, -1):
		#Add poped elemts to toHint
		if (popTrace[x] > -1) and (popTrace[x] != 0):
			#Popped empty entrties are not hinted.
			#Sth was popped at x -> add popped element to dict
			toHint.append(popTrace[x])
		#Handle Hints
		if (iTrace[x] in toHint) :
			#adress has been seen on popTrace, so its hinted
			hints.append(1)
			toHint.remove(iTrace[x])
		else:
			hints.append(0)
	#Final Checks
	assert len(iTrace) == len(hints), "Hints calculated wrong!"
	assert len(toHint) == 0, "All hints should be given!"
	hints.reverse()
	return(hints)

#@jit
def cacheHintHitUpdate(addr, cacheSet, ind):#Checked
	for x in range(ind,cacheSet.size-1):
		cacheSet[x] = cacheSet[x+1]
	cacheSet[cacheSet.size-1] = addr

def hint(iTrace, hints, sets, associativity, progBar):
	cache = initCache(sets, associativity)
	hint_hits = []
	#hint_cache_trace = []
	hits = 0
	misses = 0
	for x in range(len(iTrace)):
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'Hint-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % len(cache)
		#hint_cache_trace.append(cache[0].copy())
		#check for hit
		hit = isHit(cache[cacheSetNr], iTrace[x])
		if hit == -1: #Miss
			misses += 1
			hint_hits.append(0)
			if hints[x] != 1 :
				# No Hint on Hit-> do LRU
				cacheLRUMissUpdate(iTrace[x], cache[cacheSetNr])
			#Hint on Hit -> Don't add addr
		else:#Hit
			hits +=1
			hint_hits.append(1)
			if hints[x] == 1:
				#Hint on Miss-> age addr to max
				cacheHintHitUpdate(iTrace[x], cache[cacheSetNr], hit)
			else:
				#No Hint on Miss-> do LRU
				cacheLRUHitUpdate(iTrace[x], cache[cacheSetNr])
	#END For Loop
	if progBar:
		print()
	return hits, misses, hint_hits#, hint_cache_trace
