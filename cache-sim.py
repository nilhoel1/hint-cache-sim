import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Start the Alias gui.')
parser.add_argument('tracefile', metavar='N', type=str,
					help='Textfile containing the trace from Dynamorio.')
args = parser.parse_args()

progBar = True

#Cache Definitions
linesize =64 #Bit One instr per line assumed.
associativity = 4 
sets = 256 

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

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	"""
	Call in a loop to create terminal progress bar
	@params:
		iteration   - Required  : current iteration (Int)
		total       - Required  : total iterations (Int)
		prefix      - Optional  : prefix string (Str)
		suffix      - Optional  : suffix string (Str)
		decimals    - Optional  : positive number of decimals in percent complete (Int)
		length      - Optional  : character length of bar (Int)
		fill        - Optional  : bar fill character (Str)
		printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
	"""
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
	# Print New Line on Complete
	if iteration == total: 
		print()



def parseTrace(filename=args.tracefile):
	'''
	traces are generated with DynamoRIO and parsed with the follwoing command
	 "zcat trace/drmemtrace.a.out.85440.4382.trace.gz  | od -A x -t x2 -w12 | awk ' {printf "%s %s %s %s%s%s%s\n", $1, $2, $3, $7, $6, $5, $4}' >> trace.txt"
	The data format is as follows:
		Offset, type, size, addr
	types are:
		0x19 header
		0x16 thread
		0x18 pid
		0x1c marker: 2=timestamp; 3=cpuid
		0x0a instr (non-cti)
		0x0e direct call
		0x00 load
		0x01 store
		0x1d: non-fetched instr
		0x1a footer
		type_is_instr: 0xa-0x10 + 0x1e
	'''
	array_from_file = np.genfromtxt(filename, dtype=str)

	#Get all instruction adresses.
	row_a, col = np.where(array_from_file == '0x000a')
	row_b, col = np.where(array_from_file == '0x000b')
	row_c, col = np.where(array_from_file == '0x000c')
	row_d, col = np.where(array_from_file == '0x000d')
	row_e, col = np.where(array_from_file == '0x000e')
	row_10, col = np.where(array_from_file == '0x0010')
	row_1e, col = np.where(array_from_file == '0x001e')
	col = None
	#contains all indices of instruction adresses
	instr_rows = np.sort(
		np.concatenate(
			(row_a, row_b, row_c, row_d, row_e, row_10, row_1e)))

	#Writing instruction adresses into the trace as integers.
	iTrace = []
	for x in range(instr_rows.size):
		iTrace.append(int(array_from_file[instr_rows[x]][3], 0))

	#Clean up
	array_from_file = None
	row_10 = None
	row_1e = None
	row_a = None
	row_b = None
	row_c = None
	row_d = None
	row_e = None
	return np.array(iTrace)


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
def highestForwardDistanceOld(cacheSet, iTrace, x):
	maxDistance = [-1,-1]
	#Walk Trace only once and check with addresses.
	#If a fdistance was found for all except one, just evince furthest.
	for y in range(cacheSet.size):
		addr = cacheSet[y]
		fd = forwardDistance(iTrace, x, addr)
		if fd == -1:
			return y
		elif fd > maxDistance[1]:
			maxDistance[0] = y
			maxDistance[1] = fd
	return maxDistance[0]

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

def opt(iTrace):
	popTrace = {}
	hits = 0
	misses = 0
	for x in range(len(iTrace)):
		updateDistances(cacheDist)
		if progBar:
			printProgressBar(x, len(iTrace)-1, prefix = 'OPT-Sim:', suffix = 'Complete', length = 50)
		#Check the Set
		cacheSetNr = iTrace[x] % sets
		cacheSet = cache[cacheSetNr]
		#check for hit
		hit = np.where(cacheSet == iTrace[x])
		if hit[0].size == 0: 
			#Miss
			misses += 1
			#CacheSet is full, compute highest distance.
			ind = highestForwardDistance(cacheDist, cacheSetNr)
			cacheSet[ind] = iTrace[x]
			cacheDist[cacheSetNr][ind] = forwardDistance(iTrace, x, iTrace[x])
		else:
			#Hit
			hits += 1
			#Update Distance for hitted entry
			cacheDist[cacheSetNr][hit[0]] = forwardDistance(iTrace, x, iTrace[x])
	if progBar:
		print()
	return hits, misses


#Test.txt returns Hits: 18, Misses: 61
print(opt(parseTrace()))
#print(distanceTraceBrute(parseTrace()))