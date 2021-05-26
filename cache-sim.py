import numpy as np
import argparse
from timeit import default_timer as timer
from datetime import timedelta

from opt import opt
from hint import popToHint, hint

parser = argparse.ArgumentParser(description='Start the Alias gui.')
parser.add_argument('tracefile', metavar='N', type=str,
					help='Textfile containing the trace from Dynamorio.')
args = parser.parse_args()

progBar = True

#Cache Definitions
linesize =64 #Bit One instr per line assumed.
associativity = 4 
sets = 256 

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
	start = timer()

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


	end = timer()
	n = timedelta(seconds=end-start)
	est = n * len(iTrace)/2
	#print(est, "n: ", n)
	return np.array(iTrace)

#Test.txt returns Hits: 18, Misses: 61
iTrace = parseTrace()
hits, misses, popTrace = opt(iTrace, sets, associativity, progBar)
#print(popTrace)
hints = popToHint(popTrace, iTrace)
#print()

assert len(popTrace) == len(hints) == len(iTrace), "Schould always be True!"

hhits, hmisses = hint(iTrace, hints, sets, associativity, progBar)
print("OPT:")
print("Hits: ", hits, ", Misses: ", misses)
print("HINT:")
print("Hits: ", hhits, "Misses: ", hmisses)
#print(distanceTraceBrute(parseTrace()))