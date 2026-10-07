VALIDASI BULK SPC/E (NPT) -- cek densitas
==========================================
HASIL TERUJI: densitas rata-rata = 0.9979 g/cm3 @ 298K, 1atm
Referensi SPC/E: ~0.998 g/cm3  -> COCOK. Setup FF valid.

Urutan:
1. packmol < pack_bulk.inp           -> bulk_packed.pdb (1000 air, box 33A)
2. moltemplate.sh -pdb bulk_packed.pdb system.lt  -> system.data
3. lmp -in min_only.in               -> minimized.data (hapus overlap)
4. lmp -in npt2.in                   -> densitas setimbang

Pelajaran kunci:
- Minimisasi WAJIB sebelum NPT (overlap packing bikin tekanan meledak).
  SHAKE dimatikan saat minimize, dinyalakan lagi sesudahnya.
- Densitas konvergen dari 0.83 (packing) -> ~0.998 (bulk) dalam ~5 ps.
