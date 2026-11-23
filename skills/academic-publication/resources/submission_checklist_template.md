# Pre-Submission Compliance & Responsible Research Checklist

## A. Double-Blind & Desk-Reject Gate
- [ ] Author block uses anonymous template macro (`Anonymous Authors` / paper ID populated if required by CVPR/ECCV).
- [ ] Zero Acknowledgments, grant IDs, or institution names in main text or supplementary material.
- [ ] All code/demo URLs anonymized (no `github.com/<username>`, `wandb.ai/<entity>`, or HuggingFace user handles).
- [ ] Self-citations written strictly in third person.
- [ ] Main text within strict page limit (excluding References); zero forbidden `\vspace` / margin / font-size overrides.
- [ ] PDF metadata (`/Author`, `/Title`, `/Subject`) checked and clean.

## B. Scientific Claims & Reproducibility Gate (NeurIPS / ICLR / ICML Standard)
- [ ] **Claims Match Evidence**: Abstract and Introduction claims accurately reflect experimental scope and theoretical assumptions.
- [ ] **Limitations Section Included**: Dedicated subsection discussing failure modes, scaling limits, and assumptions.
- [ ] **Theory Completeness** *(if applicable)*: All theorems/propositions state explicit assumptions and link to complete proofs in main text or Appendix.
- [ ] **Experimental Reproducibility**: Architecture details, dataset splits, data preprocessing, optimizer/hyperparameters, and evaluation protocol fully specified.
- [ ] **Statistical Error Bars**: Multi-seed `mean ± std` or confidence intervals reported for main experiments, with seed count and source of variance stated.
- [ ] **Compute Resources Reported**: Hardware type (e.g., A100-80GB × 8), wall-clock training/inference hours, and approximate total compute for full project reported.
- [ ] **Code & Data Licenses**: Licenses and citations provided for all external datasets, pretrained checkpoints, and codebases used.
- [ ] **Broader Impacts & Ethics**: Potential misuse, privacy/PII considerations, human-subject/annotator compensation (if any), and dataset consent addressed.
