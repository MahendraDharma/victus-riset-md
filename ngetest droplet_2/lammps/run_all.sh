#!/bin/bash
cd "/mnt/c/Mahen LAMMPS/ngetest droplet_2/lammps"

# 0EG — semua suhu
for TEMP in 383 433 483 503; do
    echo ">>> Mulai: 0EG T=${TEMP}K"
    mpirun -np 32 lmp -var TEMP ${TEMP} -in in_0EG.lammps \
        > ../output/log_0EG_T${TEMP}.txt 2>&1
    echo "<<< Selesai: 0EG T=${TEMP}K"
done

# 10EG dan 20EG — semua suhu
for EG in 10 20; do
    for TEMP in 383 433 483 503; do
        echo ">>> Mulai: ${EG}EG T=${TEMP}K"
        mpirun -np 32 lmp -var EG ${EG} -var TEMP ${TEMP} -in in_EG.lammps \
            > ../output/log_${EG}EG_T${TEMP}.txt 2>&1
        echo "<<< Selesai: ${EG}EG T=${TEMP}K"
    done
done

echo "=== SEMUA SIMULASI SELESAI ==="
