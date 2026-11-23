---
name: ai-for-chemistry
description: >-
  Conduct rigorous AI, GNN, geometric deep learning, and chemical LLM research for
  Chemistry, Molecular Property Prediction, Drug Discovery, Retrosynthesis, and
  Materials Science. Enforces SMILES/SELFIES canonicalization & salt stripping,
  Bemis-Murcko scaffold & Tanimoto cluster splits (over naive random splits),
  E(3)/SE(3) physical symmetries & energy conservation, activity-cliff evaluation,
  and generative validity/novelty/PMO sample-efficiency metrics. Use this skill
  whenever working on cheminformatics, molecular ML, 3D force fields, or chemical LLMs.
---

# AI / ML / DL / LLM for Chemistry & Molecular Science

Reviewers at NeurIPS, ICML, ICLR, *Nature Machine Intelligence*, *Journal of Chemical Information and Modeling (JCIM)*, and *Chemical Science* enforce strict chemical validity, physical symmetry, and out-of-distribution structural split standards.

> **Installed Plugin Synergy:** Pair this research-methodology skill with the global **Chemistry** plugin skills (`cheminformatics-core`, `cheminformatics-ml`, `cheminformatics-physics`, `cheminformatics-reactions`, `cheminformatics-cofolding`, `cheminformatics-doc2mol`, `rdkit-general`, `chembl-database`, and `pubchem-database`) for live ChEMBL/PubChem retrieval, RDKit descriptors, MMPA/QSAR modeling, 3D conformers/docking, and ACS-styled 2D depictions.

## 1. Chemical Data Hygiene & Non-Leaky Splits

Read [chem_ml_representations_and_splits.md](./references/chem_ml_representations_and_splits.md) before training or benchmarking on molecular datasets. Core rules:

1. **Canonicalize Before Deduplicating or Splitting**:
   - Two different non-canonical SMILES strings (or protonation states / counter-ion salts like `.Cl` / `.Na`) often represent the **exact same molecule**!
   - Always sanitize with RDKit (`Chem.MolFromSmiles` -> salt/solvent strip -> charge neutralization -> canonical isomeric SMILES / InChIKey) *before* computing splits or generative Novelty.
2. **Never Rely on Random Splits Alone**:
   - Random splits place congeneric analogs (differing by a single `-CH3` or `-F`) into both train and test, inflating ROC-AUC/MAE via nearest-neighbor memorization.
   - Always report **Bemis–Murcko Scaffold Split** (standard structural generalization) and/or **Butina / Tanimoto Similarity Cluster Split** (max test-to-train ECFP4 Tanimoto $< 0.4$) or **Temporal Assay Split**, plus **Activity Cliff** subsets (e.g., MoleculeACE) when modeling potency ($K_i, \text{IC}_{50}$).
3. **Strong Classical Baselines Are Mandatory**:
   - Every 2D molecular property or chemical LLM paper **must** benchmark against **ECFP4 (Morgan radius=2, 2048 bits) + Random Forest / XGBoost / LightGBM** and a standard **D-MPNN (Chemprop) / GIN**—fingerprint + GBDT frequently beats complex GNNs and LLMs on small ADMET tables!

## 2. Physical Symmetries & Subfield Rigor

- **3D Potential Energy Surfaces & Force Fields (MD17, OC20, QM9, Matbench)**:
  - Enforce translational invariance and rotational $E(3)$/$SE(3)$ invariance for scalar energy $E$, and **conservative force derivation** ($\mathbf{F}_i = -\nabla_{\mathbf{r}_i} E$) so molecular dynamics trajectories conserve energy (non-conservative direct force heads violate Newton's third law / energy conservation in long NVE rollouts!).
  - Distinguish $E(3)$ (reflection-invariant) from $SE(3)$ (chiral-sensitive) when stereochemistry / enantiomers matter!
- **De Novo Molecular Generation & Optimization**:
  - Report Validity, Uniqueness, **Canonical Novelty vs. Train**, Internal Diversity, Fréchet ChemNet Distance (FCD), PoseBusters 3D physical plausibility (for 3D pocket generation!), synthetic accessibility (**SA Score**), and **PMO AUC Top-10 within 10,000 oracle calls**.
- **Reaction Prediction & Retrosynthesis (USPTO-50k / Pistachio)**:
  - **Strip atom-mapping numbers** from input SMILES before feeding reactants/products (`[CH3:1]` -> `C`)—leaked atom maps reveal the exact reaction center trivially! Compare canonicalized Top-$k$ accuracy ($k \in \{1, 3, 5, 10\}$).

## 3. Automated Chemical Split & Duplicate Audit CLI

Run [chem_dataset_audit.py](./scripts/chem_dataset_audit.py) on molecular CSVs (`smiles,split,target`) to check invalid structures, salt mixtures, exact/canonical cross-split leakage, and scaffold overlap (uses RDKit automatically when installed, with a pure-Python SMILES sanitizer check fallback):

```bash
python3 skills/ai-for-chemistry/scripts/chem_dataset_audit.py \
  --input data/molecules.csv \
  --smiles-col smiles \
  --split-col split
```
