---
name: latex-template-and-build
description: >-
  Add or customize conference LaTeX templates (`templates/<venue>/`), compile `.tex`
  manuscripts via `pdflatex` + `bibtex`, diagnose overfull boxes and missing
  references, check double-blind anonymity, and render 2x2 PDF page grids for visual
  layout inspection. Use this skill when onboarding NeurIPS/ICML/ACL/AAAI templates,
  fixing LaTeX build errors, or polishing page limits and layout.
---

# LaTeX Templates, Compilation & Visual Layout QA

## 1. Onboarding a New Conference Template (`templates/<venue>/`)

PaperOrchestra includes `templates/cvpr2025` and `templates/iclr2025`. To add any new venue (e.g. `templates/neurips2026`, `templates/icml2026`, `templates/acl2026`):

Create `templates/<venue>/` with these required files (checked by assertions in `methods/paper_writer*.py`):
1. `template.tex`: Skeleton document with conference `\usepackage` setup, anonymous placeholder author block, section scaffolding, and `\bibliography{references}`.
2. `guidelines.md`: Markdown summary of venue-specific rules—double-blind policy, main-body page limit (excluding references), column format, `\cref{}` / `natbib` citation style (`\citet` vs `\citep`), table (`booktabs`) & figure conventions, and the two mandatory PaperOrchestra rules:
   - Keep existing packages in `template.tex` unchanged (never rename `cleveref` to `cleverref`).
   - Always reference images via `figures/<filename>` inside `\includegraphics`.
3. `references.bib`: Initial (can be empty) BibTeX database.
4. All required `.sty`, `.bst`, and helper `.tex` macro files (e.g. `math_commands.tex`).

## 2. Compile, Lint & Export Visual Inspection Grids

Run [compile_and_check_latex.py](./scripts/compile_and_check_latex.py) to execute the 4-pass build (`pdflatex` -> `bibtex` -> `pdflatex` -> `pdflatex`), scan `.tex` and `.log` for double-blind leaks, missing figures, undefined citations/labels, and overfull `\hbox`/`\vbox` warnings, and optionally render 2x2 page grid PNGs (`utils/pdf_utils.py:pdf_to_grid_images`) that you can view directly with `read_file`:

```bash
# Offline static lint only (works even when pdflatex is not yet installed)
python3 skills/latex-template-and-build/scripts/compile_and_check_latex.py \
  --workdir paper_output_my_study/latex_writeup \
  --tex raw_draft_paper.tex \
  --lint-only

# Full compile + 2x2 visual grid export
conda run -n paper_orchestra python skills/latex-template-and-build/scripts/compile_and_check_latex.py \
  --workdir paper_output_my_study/latex_writeup \
  --tex raw_draft_paper.tex \
  --out-pdf paper_output_my_study/preview.pdf \
  --grid-dir paper_output_my_study/layout_grids
```

After generating `--grid-dir`, inspect `grid_1.png`, `grid_2.png`, etc. with `read_file` to catch clipped equations, wide tables overflowing column boundaries, orphan headings, or page-limit overruns.

## 3. Common LaTeX Fixes in PaperOrchestra Drafts

- **Wide tables overflowing a single column**: Wrap `\begin{tabular}` in `\resizebox{\linewidth}{!}{...}` or promote multi-column benchmark tables to `\begin{table*}[t] ... \end{table*}`.
- **Unescaped `_` or `%` in generated prose/captions**: Escape literal underscores (`\_`) and percent signs (`\%`, e.g., `43.43\%`) outside math mode.
- **Missing figure file errors**: Confirm the file exists under `<workdir>/figures/` and `\includegraphics` includes the `figures/` prefix.
