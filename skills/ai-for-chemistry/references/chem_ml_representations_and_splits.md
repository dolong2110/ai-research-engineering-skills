# Chemical Representations, Symmetries & Evaluation Reference

## 1. Representation Trade-Off Matrix

| Modality | Common Encodings / Backbones | Strengths | Key Failure Modes |
| :--- | :--- | :--- | :--- |
| **1D Sequence (Chemical LLMs)** | Canonical SMILES, **SELFIES**, DeepSMILES, InChI | Native LLM/Transformer compatibility, fast autoregressive generation & reaction translation | Non-canonical SMILES augmentation needed; graph-adjacent atoms can sit far apart in 1D tokens; stereochemistry hallucination |
| **2D Molecular Graph** | ECFP4/RDKit descriptors, D-MPNN (Chemprop), GIN, GPS / Graphormer | Fast, conformer-free, strong on ADMET / Bioactivity | 1-WL GNN expressivity limits on ring counts/chirality without tetrahedral stereo tags |
| **3D Geometric / Quantum** | SchNet, PaiNN, NequIP, MACE, EquiformerV2, Uni-Mol | Captures conformer Boltzmann ensembles, steric clashes, H-bonds, DFT energies/forces | Requires accurate 3D conformer generation (ETKDGv3 / GFN2-xTB) at inference; costly $O(N_{\text{neighbors}} L^6)$ tensor products |

## 2. Chemical Units & Error Tolerance Conventions

- **Quantum Chemistry (QM9 / rMD17 / SPICE)**:
  - Know **chemical accuracy**: $1\,\text{kcal/mol} \approx 43.36\,\text{meV} \approx 1.594\,\text{mHa}$. Never mix $\text{eV}$, $\text{kcal/mol}$, and $\text{Hartree}$ without explicit conversion checks!
  - Subtract atomic reference energies (atomization energy) before fitting neural potentials so dynamic range isn't dominated by core electron offsets.
- **Bioactivity ($K_i, K_d, \text{IC}_{50}, \text{EC}_{50}$)**:
  - Always transform molar concentrations to logarithmic $\text{pIC}_{50} = -\log_{10}(\text{IC}_{50}\text{ [M]})$ before regression; flag censored `>` / `<` assay qualifiers rather than treating `>100 uM` as exact `100 uM`!

## 3. Target Venues

- **ML Conferences**: NeurIPS, ICML, ICLR (plus AI4Science / ML4Molecules workshops).
- **Chemistry & Interdisciplinary Journals**: *Nature Machine Intelligence*, *Nature Computational Science*, *Journal of Chemical Information and Modeling (ACS JCIM)*, *Chemical Science (RSC)*, *Digital Discovery (RSC)*.
