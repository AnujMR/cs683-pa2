#!/bin/bash
p=$1; t=$2; th=$3
if [ "$p" = "dyn" ]; then
  DYN_IRRIP_THRESH=$th ./bin/dyn -warmup_instructions 25000000 -simulation_instructions 25000000 -traces ../traces/$t.gz > results/sweep/dyn_${t}_th${th}.txt 2>&1
else
  ./bin/rrip -warmup_instructions 25000000 -simulation_instructions 25000000 -traces ../traces/$t.gz > results/rrip_${t}.txt 2>&1
fi
