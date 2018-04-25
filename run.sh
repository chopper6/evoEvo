#!/bin/bash

num_workers = $1
input_file = $2

nohup mpirun --mca mpi_warn_on_fork 0 -n $num_workers python3 /home/2014/choppe1/Documents/evoEvo/src/simulators/evolve_root.py /home/2014/choppe1/Documents/evoEvo/data/input/$input_file > /home/2014/choppe1/Documents/evoEvo/data/output/serverout &
