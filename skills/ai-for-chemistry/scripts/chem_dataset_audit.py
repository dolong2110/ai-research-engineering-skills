#!/usr/bin/env python3
"""Audit molecular CSV datasets for invalid SMILES, unstripped salts, and train/test leakage.

Uses RDKit (canonical SMILES + Bemis-Murcko scaffolds) automatically if installed;
falls back to pure-Python SMILES structural checks when RDKit is absent.
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path


def try_import_rdkit():
    try:
        from rdkit import Chem  # type: ignore
        from rdkit.Chem.Scaffolds import MurckoScaffold  # type: ignore

        return Chem, MurckoScaffold
    except ImportError:
        return None, None


def fallback_normalize_smiles(smi: str) -> tuple[bool, str, str, bool]:
    """Pure-Python basic balance check + largest fragment extraction when RDKit is not installed."""
    s = smi.strip()
    if not s or " " in s:
        return (False, "", "", False)
    if s.count("(") != s.count(")") or s.count("[") != s.count("]"):
        return (False, "", "", False)
    has_salt = "." in s
    largest_frag = max(s.split("."), key=len) if has_salt else s
    # Rough ring-topology proxy when RDKit MurckoScaffold is unavailable
    ring_digits = sum(ch.isdigit() for ch in largest_frag)
    aromatic = sum(ch in "cnospb" for ch in largest_frag)
    pseudo_scaffold = f"frag_rings{ring_digits // 2}_arom{aromatic}"
    return (True, largest_frag, pseudo_scaffold, has_salt)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit molecular CSV for chemical validity & split leakage.")
    parser.add_argument("--input", required=True, help="Path to CSV file.")
    parser.add_argument("--smiles-col", default="smiles", help="Column containing SMILES strings.")
    parser.add_argument("--split-col", default="split", help="Optional column with train/val/test labels.")
    args = parser.parse_args()

    csv_path = Path(args.input).resolve()
    if not csv_path.exists():
        print(f"[FAIL] CSV not found: {csv_path}")
        return 1

    Chem, MurckoScaffold = try_import_rdkit()
    backend = "RDKit (full canonical SMILES + Bemis-Murcko scaffolds)" if Chem else "Pure-Python fallback (install RDKit for full canonicalization)"

    total = 0
    invalid = 0
    salt_count = 0
    by_split_mols: dict[str, set[str]] = defaultdict(set)
    by_split_scaffolds: dict[str, set[str]] = defaultdict(set)
    all_canon: list[str] = []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        has_split = reader.fieldnames is not None and args.split_col in reader.fieldnames
        for row in reader:
            total += 1
            raw_smi = (row.get(args.smiles_col) or "").strip()
            split = (row.get(args.split_col) or "all").strip().lower() if has_split else "all"

            if Chem is not None:
                mol = Chem.MolFromSmiles(raw_smi)
                if mol is None:
                    invalid += 1
                    continue
                if "." in raw_smi:
                    salt_count += 1
                    frags = Chem.GetMolFrags(mol, asMols=True, sanitizeFrags=True)
                    mol = max(frags, key=lambda m: m.GetNumHeavyAtoms())
                canon = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
                scaf = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False) or "<acyclic>"
            else:
                ok, canon, scaf, has_salt = fallback_normalize_smiles(raw_smi)
                if not ok:
                    invalid += 1
                    continue
                if has_salt:
                    salt_count += 1

            all_canon.append(canon)
            by_split_mols[split].add(canon)
            by_split_scaffolds[split].add(scaf)

    unique_mols = len(set(all_canon))
    dup_total = len(all_canon) - unique_mols

    print(f"=== Molecular Dataset Audit ({csv_path.name}) ===")
    print(f"Backend        : {backend}")
    print(f"Total Rows     : {total} | Valid: {len(all_canon)} | Invalid SMILES: {invalid}")
    print(f"Unique Mols    : {unique_mols} ({dup_total} duplicate row(s) after normalization)")
    if salt_count:
        print(f"Salt/Mixtures  : {salt_count} row(s) contained multi-fragment `.` salts (parent fragment extracted).")

    exit_code = 1 if invalid > 0 else 0
    splits = sorted(by_split_mols.keys())
    if len(splits) > 1:
        print("\n--- Cross-Split Leakage & Scaffold Overlap ---")
        for i in range(len(splits)):
            for j in range(i + 1, len(splits)):
                s1, s2 = splits[i], splits[j]
                mol_overlap = by_split_mols[s1] & by_split_mols[s2]
                scaf_overlap = by_split_scaffolds[s1] & by_split_scaffolds[s2]
                if mol_overlap:
                    print(f"  [FAIL] {len(mol_overlap)} identical molecule(s) leaked across `{s1}` and `{s2}`!")
                    exit_code = 1
                else:
                    print(f"  [OK] Zero molecule leakage between `{s1}` and `{s2}`.")
                if Chem is not None:
                    scaf_pct = (len(scaf_overlap) / max(1, len(by_split_scaffolds[s2]))) * 100.0
                    print(f"       Shared Bemis-Murcko scaffolds (`{s1}` ∩ `{s2}`): {len(scaf_overlap)} ({scaf_pct:.1f}% of `{s2}` scaffolds)")
                    if scaf_pct > 25.0 and "test" in {s1, s2}:
                        print("       [WARN] High scaffold overlap (>25%) — split looks random rather than scaffold-disjoint!")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
