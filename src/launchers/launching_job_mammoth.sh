#!/bin/bash
#PBS -l nodes=1:ppn=1 
#PBS -l walltime=00:10:00
#PBS -A ymj-002-aa

module unload intel64/12.0.5.220
module unload pgi64/11.10
module unload pathscale/4.0.12.1
module load intel64/13.1.3.192
module load pathscale/5.0.5
module load pgi64/12.5
module load openmpi_intel64/1.6.5

echo 'launching python3 '$LAUNCHING_SCRIPT' '$SIMULATION_CONFIGS

cd $LAUNCHING_DIRECTORY

python3 $LAUNCHING_SCRIPT $SIMULATION_CONFIGS
