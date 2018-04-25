#!/bin/bash
#PBS -l procs=9
#PBS -l walltime=00:30:00
#PBS -A ymj-002-aa
#PBS -q debug

module load gcc/4.9.1
module load MKL/11.2
module load openmpi/1.8.3-gcc

echo 'simulating on Guillimin: python '$SIMULATION_BATCH_ROOT' 9 '$SIMULATION_CONFIGS

cd $SIMULATION_DIRECTORY

python $SIMULATION_BATCH_ROOT 9 $SIMULATION_CONFIGS
