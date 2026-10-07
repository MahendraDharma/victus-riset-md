PIPELINE DROPLET AIR MURNI (SPC/E) -- Packmol + moltemplate + LAMMPS
====================================================================
Urutan jalankan:

1. packmol < pack.inp
   -> menghasilkan droplet_packed.pdb (5991 molekul dalam bola R=36 A)

2. moltemplate.sh -pdb droplet_packed.pdb system.lt
   -> menghasilkan: system.data, system.in.init, system.in.settings

3. lmp -in equil_production.in
   -> pra-relaksasi (nve/limit) lalu NVT 298 K
   -> menghasilkan droplet_equil.data + droplet.lammpstrj

File:
- water.pdb            : template 1 molekul (urutan O,H1,H2 cocok spce.lt)
- pack.inp             : input Packmol
- spce.lt              : definisi SPC/E kanonik (dari moltemplate)
- system.lt            : 5991 molekul + definisi kotak
- equil_production.in  : skrip ekuilibrasi LAMMPS (sudah ada pra-relaksasi)

Catatan penting:
- equil_production.in pakai PPPM (lj/charmm/coul/long) -- akurat tapi MAHAL
  di kotak vakum besar. Untuk uji cepat bisa ganti ke coul/cut, tapi
  produksi pakai PPPM.
- Pra-relaksasi nve/limit WAJIB: tanpa itu suhu meledak dari kontak rapat
  hasil packing.
- Untuk campuran water-ethanol: tambahkan molekul ethanol di pack.inp
  (number, inside sphere) dan import "ethanol.lt" di system.lt.
