#!/bin/bash

for file in *; do
    echo "associativity, sets, diffs, ohits, omisses, hhits, hmisses, lhits, lmisses" >> ../out/$file.out
    python ../cache-sim.py ../traces_val/$file 1 1 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 4 16 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 8 32 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 16 64 0 >> ../out/$file.out &

    python ../cache-sim.py ../traces_val/$file 1 16 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 4 32 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 8 64 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 16 1 0 >> ../out/$file.out &

    python ../cache-sim.py ../traces_val/$file 1 32 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 4 64 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 8 1 0 >> ../out/$file.out  &
    python ../cache-sim.py ../traces_val/$file 16 16 0 >> ../out/$file.out &

    python ../cache-sim.py ../traces_val/$file 1 64 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 4 1 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 8 16 0 >> ../out/$file.out  &
    python ../cache-sim.py ../traces_val/$file 16 32 0 >> ../out/$file.out &

    python ../cache-sim.py ../traces_val/$file 1 128 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 4 128 0 >> ../out/$file.out &
    python ../cache-sim.py ../traces_val/$file 8 128 0 >> ../out/$file.out  &
    python ../cache-sim.py ../traces_val/$file 16 128 0 >> ../out/$file.out &
    wait -n
done
