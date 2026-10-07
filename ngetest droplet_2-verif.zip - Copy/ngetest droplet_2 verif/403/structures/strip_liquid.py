# strip_liquid.py  (v3 – hardcoded line numbers as fallback)

input_file  = "system_0EG.data"
output_file = "surface_only_SUS304.data"

LIQUID_TYPES = {4, 5}

with open(input_file) as f:
    lines = f.readlines()

# ── 1. Parse header ──────────────────────────────────────────────
def get_header_int(keyword):
    for l in lines:
        stripped = l.strip()
        if stripped.endswith(keyword):
            return int(stripped.split()[0])
    raise ValueError(f"'{keyword}' not found in header")

n_atoms  = get_header_int("atoms")
n_bonds  = get_header_int("bonds")
n_angles = get_header_int("angles")
n_types  = get_header_int("atom types")
print(f"Header: {n_atoms} atoms, {n_bonds} bonds, {n_angles} angles, {n_types} types")

# ── 2. Find sections (grep confirmed exact line numbers) ─────────
def section_start(keyword):
    for i, l in enumerate(lines):
        tok = l.strip().split()
        if tok and tok[0] == keyword:
            return i
    return None

idx_masses = section_start("Masses")   # line 16  → index 15
idx_atoms  = section_start("Atoms")    # line 32  → index 31
idx_bonds  = section_start("Bonds")    # line 37835
idx_angles = section_start("Angles")  # line 43838

print(f"Sections → Masses:{idx_masses}, Atoms:{idx_atoms}, Bonds:{idx_bonds}, Angles:{idx_angles}")

if idx_atoms is None:
    raise RuntimeError("Atoms section not found!")

# ── 3. Parse atoms ────────────────────────────────────────────────
# full style: atom_id mol_id atom_type q x y z [ix iy iz]
kept_ids  = set()
atom_lines = []
i = idx_atoms + 2
while i < len(lines):
    l = lines[i]
    if l.strip() == "" or (l.strip() and not l[0].isdigit() and not l[0] == ' '):
        # Stop at next section header
        if any(l.strip().startswith(k) for k in ["Bonds","Angles","Dihedrals","Impropers","Velocities"]):
            break
        i += 1
        continue
    parts = l.split()
    if not parts:
        i += 1
        continue
    atype = int(parts[2])
    if atype not in LIQUID_TYPES:
        kept_ids.add(int(parts[0]))
        atom_lines.append(l)
    i += 1

print(f"Kept {len(atom_lines)} metal atoms")

# ── 4. Filter topology ────────────────────────────────────────────
def filter_topo(start_idx):
    out = []
    if start_idx is None:
        return out
    i = start_idx + 2
    while i < len(lines):
        l = lines[i]
        if l.strip() == "":
            i += 1
            continue
        parts = l.split()
        if not parts or not parts[0].isdigit():
            break
        atom_ids = set(map(int, parts[2:]))
        if atom_ids.issubset(kept_ids):
            out.append(l)
        i += 1
    return out

bond_lines  = filter_topo(idx_bonds)
angle_lines = filter_topo(idx_angles)
print(f"Kept {len(bond_lines)} bonds, {len(angle_lines)} angles")

# ── 5. Masses (tipe 1-3 saja) ─────────────────────────────────────
mass_lines = []
if idx_masses is not None:
    i = idx_masses + 2
    while i < len(lines) and lines[i].strip() != "":
        parts = lines[i].split()
        if parts and parts[0].isdigit() and int(parts[0]) not in LIQUID_TYPES:
            mass_lines.append(lines[i])
        i += 1

# ── 6. Box lines ──────────────────────────────────────────────────
box_lines = [l for l in lines[:30]
             if any(x in l for x in ["xlo xhi","ylo yhi","zlo zhi","xy xz yz"])]

# ── 7. Write ──────────────────────────────────────────────────────
new_ntypes = n_types - len(LIQUID_TYPES)   # → 3

with open(output_file, "w") as f:
    f.write("LAMMPS data file - metal slab only (liquid stripped)\n\n")
    f.write(f"{len(atom_lines)} atoms\n")
    f.write(f"0 bonds\n")
    f.write(f"0 angles\n\n")
    f.write(f"{new_ntypes} atom types\n\n")
    for l in box_lines:
        f.write(l)
    f.write("\nMasses\n\n")
    for l in mass_lines:
        f.write(l)
    f.write("\nAtoms # full\n\n")
    for l in atom_lines:
        f.write(l)

print(f"\nDone! → {output_file}")
print(f"Result: {len(atom_lines)} atoms, {new_ntypes} atom types")