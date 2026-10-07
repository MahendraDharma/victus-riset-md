#!/usr/bin/env python3
# ============================================================================
# merge_pdb.py
# Menggabungkan DUA file terpisah menjadi satu LAMMPS data (atom_style full):
#   (1) slab Cu hasil ATOMSK  : Cu_slab_natural.lmp  (atom_style atomic)
#   (2) droplet air hasil PACKMOL : droplet_0EG_spce.pdb  (O,H,H per molekul)
#
# Format output meniru system_0EG.data Anda:
#   Atoms  # full  ->  id  mol  type  charge  x  y  z
#   Tipe : 1=Cu (q=0)  2=OW (q=-0.8476)  3=HW (q=+0.4238)
#   Cu mol-ID = 0 ; tiap molekul air mol-ID = 1,2,3,...
#   Bonds  : O-H, O-H (tipe 1)   Angles: H-O-H (tipe 1)
# ============================================================================
import numpy as np

# -------------------- INPUT / OUTPUT --------------------
SLAB_FILE = "Cu_slab_natural.lmp"   # slab Cu dari ATOMSK
PDB_FILE  = "droplet_0EG_spce.pdb"       # droplet dari Packmol
OUT_FILE  = "system_0EG_Cu_spce.data"

# Tinggi total kotak arah-z (ruang vakum + impact). 197.192 = sama spt referensi.
Z_BOX_HI  = 197.192

# Muatan & massa SPC/E
Q_O, Q_H       = -0.8476, 0.4238
M_CU, M_O, M_H = 63.546, 15.999, 1.008
# --------------------------------------------------------

# 1) BACA SLAB Cu (atom_style atomic: id type x y z) -------------------------
lines = open(SLAB_FILE).read().splitlines()
box = {}
cu = []
i = 0
while i < len(lines):
    L = lines[i]
    if "xlo xhi" in L: p = L.split(); box['x'] = (float(p[0]), float(p[1]))
    elif "ylo yhi" in L: p = L.split(); box['y'] = (float(p[0]), float(p[1]))
    elif "zlo zhi" in L: p = L.split(); box['z'] = (float(p[0]), float(p[1]))
    elif L.strip().startswith("Atoms"):
        i += 1
        while i < len(lines) and not lines[i].strip():  # lewati baris kosong
            i += 1
        while i < len(lines) and lines[i].strip():
            p = lines[i].split()
            cu.append([float(p[2]), float(p[3]), float(p[4])])  # x y z
            i += 1
        break
    i += 1
cu = np.array(cu)
xlo, xhi = box['x']; ylo, yhi = box['y']
zlo = box['z'][0]
print(f"Slab Cu : {len(cu)} atom | top z = {cu[:,2].max():.2f} A | "
      f"kotak x[{xlo:.2f},{xhi:.2f}] y[{ylo:.2f},{yhi:.2f}]")

# 2) BACA DROPLET PDB (urutan O,H,H per molekul) -----------------------------
wat = []
for ln in open(PDB_FILE):
    if ln.startswith("ATOM") or ln.startswith("HETATM"):
        # kolom PDB fixed-width: x[30:38] y[38:46] z[46:54]
        wat.append([float(ln[30:38]), float(ln[38:46]), float(ln[46:54])])
wat = np.array(wat)
assert len(wat) % 3 == 0, "Jumlah atom air bukan kelipatan 3!"
n_w = len(wat) // 3
print(f"Droplet : {n_w} molekul ({len(wat)} atom) | "
      f"z[{wat[:,2].min():.2f},{wat[:,2].max():.2f}]")

# 3) RANGKAI ATOMS ------------------------------------------------------------
atoms, bonds, angles = [], [], []
aid = 0

# 3a) Cu : mol 0, type 1, charge 0
for (x, y, z) in cu:
    aid += 1
    atoms.append(f"{aid} 0 1 0.0000 {x:.6f} {y:.6f} {z:.6f}")
n_cu = aid

# 3b) Air : tiap molekul O,H,H -> type 2/3, mol berurutan
for m in range(n_w):
    o  = wat[3*m + 0]
    h1 = wat[3*m + 1]
    h2 = wat[3*m + 2]
    mol = m + 1
    oid = aid + 1
    atoms.append(f"{oid} {mol} 2 {Q_O:.4f} {o[0]:.6f} {o[1]:.6f} {o[2]:.6f}")
    h1id = aid + 2
    atoms.append(f"{h1id} {mol} 3 {Q_H:.4f} {h1[0]:.6f} {h1[1]:.6f} {h1[2]:.6f}")
    h2id = aid + 3
    atoms.append(f"{h2id} {mol} 3 {Q_H:.4f} {h2[0]:.6f} {h2[1]:.6f} {h2[2]:.6f}")
    bonds.append((oid, h1id))
    bonds.append((oid, h2id))
    angles.append((h1id, oid, h2id))
    aid += 3

n_atoms  = len(atoms)
n_bonds  = len(bonds)
n_angles = len(angles)

# 4) TULIS DATA FILE ----------------------------------------------------------
with open(OUT_FILE, "w") as f:
    f.write("# LAMMPS Data — Cu slab + droplet 0% EG\n")
    f.write("# Surface: Cu FCC (Mishin EAM) | Water: SPC/E\n\n")
    f.write(f"{n_atoms} atoms\n{n_bonds} bonds\n{n_angles} angles\n\n")
    f.write("3 atom types\n1 bond types\n1 angle types\n\n")
    f.write(f"{xlo:.6f}  {xhi:.6f}  xlo xhi\n")
    f.write(f"{ylo:.6f}  {yhi:.6f}  ylo yhi\n")
    f.write(f"{zlo:.6f}  {Z_BOX_HI:.6f}  zlo zhi\n\n")
    f.write(f"Masses\n\n  1  {M_CU}  # Cu\n  2  {M_O}  # OW\n  3  {M_H}  # HW\n\n")
    f.write("Bond Coeffs\n\n  1  1000.0   1.000  # O-H water\n\n")
    f.write("Angle Coeffs\n\n  1  100.0  109.47  # H-O-H water\n\n")
    f.write("Atoms  # full\n\n" + "\n".join(atoms) + "\n\n")
    f.write("Bonds\n\n" + "\n".join(f"{k} 1 {a} {b}" for k,(a,b) in enumerate(bonds,1)) + "\n\n")
    f.write("Angles\n\n" + "\n".join(f"{k} 1 {a} {b} {c}" for k,(a,b,c) in enumerate(angles,1)) + "\n")

print(f"\nTotal   : {n_atoms} atom ({n_cu} Cu + {len(wat)} air) | "
      f"{n_bonds} bond | {n_angles} angle")
print(f"Kotak z : [{zlo:.2f}, {Z_BOX_HI:.2f}] A")
print(f"Ditulis : {OUT_FILE}")
