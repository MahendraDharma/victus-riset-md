#!/bin/bash

## MPI for CPUs
#BSUB -n 8
#BSUB -o tmp/
#BSUB -q guest2
#BSUB -J MDsemi


mpirun /usr/local/bin/lmp -i in.0EG_T383_110C_FIXED.lammps

