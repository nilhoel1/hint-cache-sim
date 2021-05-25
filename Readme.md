## How to generate usable Traces
 Cache traces are generated by Dynamorio with:

```/opt/dynamorio/bin64/drrun -t drcachesim -offline -- a.out 1000```

After that run drcachesim on the file with:

``` bin64/drrun -t drcachesim -indir drmemtrace.app.pid.xxxx.dir/```

And packed in a Human Readable format with:
```zcat drmemtrace.tool.drcacheoff.burst_malloc.211917.2237.dir/trace/drmemtrace.tool.drcacheoff.burst_malloc.211917.8542.trace.gz  | od -A x -t x2 -w12 | awk '{printf "0x%s 0x%s 0x%s 0x%s%s%s%s\n", $1, $2, $3, $7, $6, $5, $4}' >> trace.txt```
## How to use the tool
Currently only the trace can be given as an argument.
```python cache-sim.py <traceFile>```
