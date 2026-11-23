---
name: academic-publication
description: >-
  Manage the academic publication lifecycle: venue selection, double-blind
  anonymization and PDF metadata audits, NeurIPS/ICLR/ACL submission checklists,
  Broader Impact & Ethics statements, clean arXiv `.tar.gz` source packaging
  (stripping `%` comments and bundling `.bbl`), OpenReview author rebuttals, and
  camera-ready preparation. Use this skill when preparing a paper for conference,
  journal, or arXiv submission, writing rebuttals, or finalizing camera-ready copies.
---

# Academic Publication, Submission, arXiv & Rebuttal

Use this skill to move a completed manuscript safely through double-blind conference submission, arXiv release, peer-review rebuttal, and camera-ready publication without desk-rejection hazards or identity leaks.

## 1. Pre-Submission Double-Blind & Compliance Audit

Desk rejections most commonly stem from page-limit violations, template margin tampering (`\vspace{-...}` abuse), missing checklists, or accidental anonymity leaks (non-anonymous GitHub/WandB links, `\thanks{}`, PDF `/Author` metadata, or first-person self-citations).

1. **Run the Double-Blind & Source Hygiene Audit** ([package_arxiv_and_audit.py](./scripts/package_arxiv_and_audit.py)):
   ```bash
   python3 skills/academic-publication/scripts/package_arxiv_and_audit.py audit \
     --workdir paper_output_my_study/latex_writeup \
     --tex raw_draft_paper.tex \
     --pdf paper_output_my_study/final_paper.pdf
   ```
2. **Complete the Venue Submission Checklist**:
   - Copy and fill [submission_checklist_template.md](./resources/submission_checklist_template.md) (aligned with the NeurIPS / ICLR / ICML Paper Checklist and ACL ARR Responsible NLP criteria) verifying claims-to-evidence match, error bars, compute reporting, asset licenses, and ethics/broader impacts.

## 2. Clean arXiv Source Packaging (`.tar.gz`)

> **Critical arXiv Warning:** arXiv publicly serves your uploaded `.tex` source tarball to anyone! Private `% TODO`, `% reviewer 2`, internal paths, or commented-out author names inside `.tex` files become permanently public unless stripped prior to upload. Furthermore, arXiv does **not** run BibTeX on `.bib` files—you **must** include the compiled `<main>.bbl` matching arXiv's TeX Live `natbib`/`biblatex` version.

Build a clean, comment-stripped arXiv tarball containing only referenced figures, macros, `.sty`/`.bst`, and `<main>.bbl`:

```bash
python3 skills/academic-publication/scripts/package_arxiv_and_audit.py package-arxiv \
  --workdir paper_output_my_study/latex_writeup \
  --tex raw_draft_paper.tex \
  --out paper_output_my_study/arxiv_submission.tar.gz
```

## 3. High-Conversion OpenReview Rebuttals & Author Responses

When reviews arrive, read [rebuttal_and_camera_ready_guide.md](./references/rebuttal_and_camera_ready_guide.md) and draft responses from [rebuttal_template.md](./resources/rebuttal_template.md):

1. **Build a Cross-Reviewer Issue Matrix First**: Cluster overlapping concerns across Reviewers 1–4 (`Shared Concern A`, `Shared Concern B`) so your **Global General Response** resolves shared bottlenecks upfront with one compact new-experiment table.
2. **Follow the 4-Part Per-Weakness Formula**:
   - *Acknowledge & Restate* (1 line showing you understood the exact concern)
   - *Direct Answer / Verdict* (lead with the conclusion + new numbers immediately)
   - *Evidence* (compact table or theoretical clarification—run missing ablations via `scientific-research` / `end-to-end-research-workflow`!)
   - *Exact Manuscript Revision* (cite section/line/table changed in the revised PDF, colored in `\textcolor{blue}{...}` if the venue permits revision uploads).

## 4. Camera-Ready & Artifact Release

See [rebuttal_and_camera_ready_guide.md](./references/rebuttal_and_camera_ready_guide.md) for final de-anonymization macros (`\cvprfinalcopy`, `\iclrfinalcopy`, `[final]`), funding acknowledgments, camera-ready page allowance (+1 page at ICLR/NeurIPS/ICML when applicable), ORCID/BibTeX verification, and clean code/checkpoint release checklists.
