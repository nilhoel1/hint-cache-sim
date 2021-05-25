import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Start the Alias gui.')
parser.add_argument('tracefile', metavar='N', type=str,
                    help='Textfile containing the trace from Dynamorio.')
args = parser.parse_args()

#Cache Definitions
linesize =64 #Bit One instr per line assumed.
associativity = 4 
sets = 256 

#generate a dictionary for the cache
cache = {}
for x in range(sets):
    cache[x] = np.array(np.zeros(associativity))


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


def distanceTraceBruteOld(iTrace):
    #calculate distances
    distTrace = [[iTrace[len(iTrace)-1]]]
    print(distTrace)
    #Walk itrace backwards and add distances
    for x in range(len(iTrace)-2, -1, -1):
        stack = distTrace[len(iTrace)-x-2].copy()
        try:
            stack.remove(iTrace[x])
        except:
            stack = stack
        #print(x)
        stack.append(iTrace[x])
        distTrace.append(stack)
    #print(distTrace)
    return distTrace


def distanceTraceBrute(iTrace):
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
def forwardDistance(iTrace, x, addr):
    distance = 0
    for x in range(x+1, len(iTrace)):
        if iTrace[x] != addr:
            distance += 1
        else:
            return distance
    return -1

#return index to address with highest fd, -1 should never be returned
def highestForwardDistance(cacheSet, iTrace, x):
    maxDistance = [-1,-1]
    for y in range(cacheSet.size):
        addr = cacheSet[y]
        fd = forwardDistance(iTrace, x, addr)
        if fd == -1:
            return y
        elif fd > maxDistance[1]:
            maxDistance[0] = y
            maxDistance[1] = fd
    return maxDistance[0]


#Returns index of first found empty space, otherwise 0
def cacheHasEmptySpace(cacheSet):
    for x in range(cacheSet.size):
        if cacheSet[x] == 0:
            return x
    return 0

def opt(iTrace):
    popTrace = {}
    hits = 0
    misses = 0
    for x in range(len(iTrace)):
        printProgressBar(x, len(iTrace), prefix = 'OPT-Sim:', suffix = 'Complete', length = 50)
        cacheSetNr = iTrace[x] % sets
        cacheSet = cache[cacheSetNr]
        i = np.where(cacheSet == iTrace[x])
        if i[0].size == 0: #Adress is not in Cache
            misses += 1
            #TODO add to pop Trace for hints.
            space = cacheHasEmptySpace(cacheSet)
            if space != 0:
                #CacheSet was not full and address can be added
                cacheSet[space] = iTrace[x]
            else:
                #CacheSet is full, compute highest distance.
                ind = highestForwardDistance(cacheSet, iTrace, x)
                cacheSet[ind] = iTrace[x]
        else:
            hits += 1
        
    return hits, misses

print(opt(parseTrace()))
#print(distanceTraceBrute(parseTrace()))