# IEEE Formatting Specifications

Reference specifications for standard IEEE conference (`\documentclass[conference]{IEEEtran}`) and Transactions journal (`\documentclass[journal]{IEEEtran}`) manuscripts.

## 1. Page Layout & Typography

- **Document Class**: `\documentclass[conference]{IEEEtran}` (or `journal` / `compsoc` as required by the venue).
- **Page Size & Columns**: Two-column body layout with 4.22 mm (`0.166 in`) column separation; A4 (210 mm × 297 mm) or US Letter (`8.5 in × 11 in`) per venue CFP.
- **Margins (IEEE A4 conference baseline)**: Top `19 mm`, Bottom `43 mm`, Left/Right `14.32 mm`.
- **Typeface**: Times / Times New Roman (`newtxtext`/`newtxmath` or `IEEEtran` default):
  - Paper Title: `24 pt` bold (title case)
  - Author Names: `11 pt` regular; Affiliations: `10 pt` italic
  - Section Headings (Level 1): `10 pt` small-caps / bold, Roman-numeral numbered (`I. INTRODUCTION`) or Arabic (`1.`) depending on template
  - Subsection Headings (Level 2): `10 pt` italic (`A. Experimental Setup` or `1.1`)
  - Body Text: `10 pt`, single-spaced
  - Figure & Table Captions: `8 pt`
  - Footnotes & References: `8 pt`

## 2. Figures, Tables & Equations

- **Figures**: Centered (`\centering`), captions placed **below** the figure (`Fig. 1. ...`). Use `figure*` for full-width two-column visuals. Reference in prose as `Fig.~\ref{fig:...}` (or `Figure~\ref{...}` at the start of a sentence).
- **Tables**: Centered (`\centering`), captions placed **above** the table (`TABLE I` in small caps). Avoid vertical rules; use `booktabs` horizontal rules.
- **Equations**: Numbered sequentially on the right margin `(1)`, `(2)`. Reference as `(1)` mid-sentence or `Equation (1)` at the start of a sentence.

## 3. IEEE Citations & References (`IEEEtran.bst`)

- **In-Text**: Numbered in square brackets in order of first appearance: `Recent work [1], [2] shows...` or range `[3]--[5]`; section pinpoint: `[5, Sec. III]`.
- **Reference Entries**:
  ```text
  [1] A. Author, B. Author, and C. Author, "Title of paper," in Proc. IEEE Conf. Name, Year, pp. 123–132, doi: 10.1109/....
  [2] D. Author, "Title of journal article," IEEE Trans. Journal Name, vol. X, no. Y, pp. 123–145, Month Year.
  [3] E. Author, Book Title, 2nd ed. City, Country: Publisher, Year.
  ```
- Include **Index Terms (Keywords)** immediately after the Abstract (`\begin{IEEEkeywords}...\end{IEEEkeywords}`).
