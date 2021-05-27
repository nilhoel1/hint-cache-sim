import numpy as np
import argparse
import gzip

from opt import opt
from hint import popToHint, hint
from lru import lru

parser = argparse.ArgumentParser(description='Start the Alias gui.')
parser.add_argument('tracefile', metavar='N', type=str,
					help='Textfile containing the trace from Dynamorio.')
parser.add_argument('associativity', metavar='a', type=int,
					help='Specify cache Associativity.')
parser.add_argument('sets', metavar='s', type=int,
					help='Specify cache Sets.')
args = parser.parse_args()

progBar = True
printErrors = False
#Cache Definitions
#linesize =64 #Currently not Implemented, One instr per line assumed.
associativity = args.associativity
sets = args.sets

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

	array_from_file = np.genfromtxt(gzip.open(filename), dtype=str)

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


#Test.txt returns Hits: 18, Misses: 61
iTrace = parseTrace()
ohits, omisses, popTrace, opt_hits, opt_cache_trace = opt(iTrace, sets, associativity, progBar)
#print(popTrace)
hints = popToHint(popTrace, iTrace)
#print()

assert len(popTrace) == len(hints) == len(iTrace), "Should always be True!"

hhits, hmisses, hint_hits, hint_cache_trace = hint(iTrace, hints, sets, associativity, progBar)

lhits, lmisses = lru(iTrace, sets, associativity, progBar)

diffs = 0
annomalies = []
for x in range(len(opt_hits)):
	if opt_hits[x] != hint_hits[x]:
		print("Diff at:", x, ", Position in %:", round((x/len(opt_hits))*100, 2))
		diffs += 1
		annomalies.append(x)
		if printErrors:
			print("Addr:", iTrace[x], "@:", x)
			print("H-Cache", hint_cache_trace[x], "@", x-1, "Hit:", hint_hits[x-1])
			print("H-Cache", hint_cache_trace[x], "@", x, "Hit:", hint_hits[x])
			print("H-Cache", hint_cache_trace[x], "@", x+1, "Hit:", hint_hits[x+1])
			print("__________________________________________________________________")
			print("O-Cache", opt_cache_trace[x], "@", x-1, "Hit:", opt_hits[x-1], "Pop:", popTrace[x-1])
			print("O-Cache", opt_cache_trace[x], "@", x, "Hit:", opt_hits[x], "Pop:", popTrace[x])
			print("O-Cache", opt_cache_trace[x], "@", x+1, "Hit:", opt_hits[x+1], "Pop:", popTrace[x+1])


print("Number of Errors:", diffs, ", Errors in %:", round((diffs/len(opt_hits))*100,4), ", Hit diff", abs(hhits-ohits))
print("Sets:", sets, ", Associativity:", associativity, ", Trace:", args.tracefile)
print("OPT-L1:")
print("Hits:", ohits, ", Misses:", omisses)
print("HINT-L1:")
print("Hits:", hhits, "Misses:", hmisses)
print("LRU-L1:")
print("Hits:", lhits, "Misses:", lmisses)
#print(distanceTraceBrute(parseTrace()))