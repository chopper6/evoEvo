#!/bin/bash
#/usr/bin/env

# num_threads = #workers + 1

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters. Need #threads, then input_file."
fi

nohup mpirun --mca mpi_warn_on_fork 0 -n $1 python3 /home/2014/choppe1/Documents/evoEvo/src/evolve.py /home/2014/choppe1/Documents/evoEvo/data/input/$2 > /home/2014/choppe1/Documents/evoEvo/data/output/slog &
