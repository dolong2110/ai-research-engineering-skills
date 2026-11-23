# OpenReview Rebuttal Strategy & Camera-Ready Guide

## 1. Anatomy of Rebuttals That Flip Borderline Scores (5 -> 7 / 6 -> 8)

Area Chairs (ACs) read the **Global Response** and **inter-reviewer discussion** far more closely than 5,000-word walls of text. Keep responses scannable and evidence-dense:

### Rules of Engagement
1. **Front-load New Empirical Evidence**: Put new baseline comparisons or ablations in the **first 15 lines** of the Global Response as a clean Markdown table.
2. **Never Blame the Reviewer**: If a reviewer missed something already on page 5, say *"Thank you—we agree this transition in Sec. 3.2 was not prominent enough. As noted in Eq. (4) (and now clarified upfront in Sec. 3.1, highlighted in blue), ..."* rather than *"This is already in Section 3.2."*
3. **Strict Character Limits**: OpenReview often caps individual comments at 5,000–8,000 characters. Budget ~2,500 chars for the Global Response and ~3,500–4,500 chars per reviewer.
4. **Distinguish Scope vs. Flaw Politely**: When a reviewer asks for an out-of-domain task (e.g., 3D LiDAR segmentation in an audio-visual 2D segmentation paper), run a lightweight feasibility probe if cheap, or clearly justify the scope boundary via problem definition and add it explicitly to Limitations.

## 2. Desk-Rejection Prevention Rules (Before Initial Submission)

- **Formatting Tampering**: Never shrink `\baselinestretch`, modify `\textwidth`/`\columnsep`, or insert global negative `\vspace` around captions/headings beyond template rules—automated PDF checkers at CVPR/NeurIPS/AAAI flag margin and line-spacing violations immediately.
- **Page Count Split**: Main body ends strictly at the venue limit (e.g., 8 pages CVPR, 9 pages NeurIPS/ICLR); References and Ethics/Reproducibility statements start cleanly as permitted by the venue call for papers, and Supplementary Appendix lives either after References (single-PDF venues like ICLR/NeurIPS) or in a separate `supp.pdf` (CVPR/ICCV/ECCV).
- **Self-Citations**: Always write *"Radman et al. [12] introduced..."* rather than *"In our prior work [12], we introduced..."*.

## 3. Camera-Ready Finalization Checklist

1. Toggle final mode in `template.tex` (`\iclrfinalcopy`, `\usepackage[final]{neurips_2025}`, or remove `[review]` in `cvpr.sty`).
2. Populate accurate author names, equal-contribution footnotes (`*`), affiliations, and correspondence emails.
3. Add **Acknowledgments** (grants, compute credits, helpful discussions—never present during double-blind review).
4. Remove blue revision coloring (`\textcolor{blue}{...}`) from rebuttal diffs.
5. Replace anonymous repository URLs (`anonymous.4open.science/...`) with permanent public GitHub + Zenodo/HuggingFace links containing a `README.md`, `LICENSE`, environment lockfile, and exact command to reproduce Table 1.
6. Re-verify font embedding (`pdffonts final_paper.pdf` — all fonts should show `emb = yes` and Type 1 / TrueType, no Type 3 bitmap fonts from Matplotlib). To avoid Type 3 fonts in Matplotlib PDFs, set:
   ```python
   plt.rcParams["pdf.fonttype"] = 42
   plt.rcParams["ps.fonttype"] = 42
   ```
