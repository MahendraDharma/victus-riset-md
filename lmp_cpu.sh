#!/bin/bash

## MPI for CPUs
#BSUB -n 8
#BSUB -o tmp/
#BSUB -q guest2
#BSUB -J MDsemi


mpirun /usr/local/bin/lmp -i
