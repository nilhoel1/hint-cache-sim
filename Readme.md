# Hint-Cache-Sim
This is a small cache simulator, written in pyhtin. It is able to simulate an Optimal trace based on the OPT or Belady algorithm. It will also simulate a HINT policy based on OPT and LRU.
## How to use the tool
Currently only the trace can be given as an argument.

```python cache-sim.py <traceFile.txt.gz> <#associativity> <#sets> <ProgBar>```

An example to ru the simulator on a 2 associativity and 4 sets cache with a ProgressBar:

```python cache-sim.py traces/short.txt.gz 2 4 1```

## How to generate usable Traces
 Cache traces are generated by Dynamorio with:

```/opt/dynamorio/bin64/drrun -t drcachesim -offline -- a.out 1000```

After that run drcachesim on the file with:

``` bin64/drrun -t drcachesim -indir drmemtrace.app.pid.xxxx.dir/```

And packed in a Human Readable format with:

```zcat drmemtrace.tool.drcacheoff.burst_malloc.211917.2237.dir/trace/drmemtrace.tool.drcacheoff.burst_malloc.211917.8542.trace.gz  | od -A x -t x2 -w12 | awk '{printf "0x%s 0x%s 0x%s 0x%s%s%s%s\n", $1, $2, $3, $7, $6, $5, $4}' >> trace.txt```

It is recommended to pack the traces (They are very big):

``` gzip trace.txt```


## Current Status of the tool 
Only used and tested with versions >= python3.7.

At the moment cache lines are ignored, or at least line size = adress size is assumed.