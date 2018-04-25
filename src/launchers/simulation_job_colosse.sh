#!/bin/bash
#PBS -l nodes=8:ppn=8 
#PBS -l walltime=01:00:00
#PBS -A ymj-002-aa
#PBS -q short
#PBS -M mosha5581@gmail.com
# PBS -m abe

module load compilers/intel/14.0
module load mpi/openmpi/1.6.5
module load libs/mkl/11.1

echo 'simulating: python '$SIMULATION_BATCH_ROOT' 64 '$SIMULATION_CONFIGS

cd $SIMULATION_DIRECTORY

python $SIMULATION_BATCH_ROOT 64 $SIMULATION_CONFIGS
