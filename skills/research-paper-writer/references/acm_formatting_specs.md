# ACM Formatting Specifications (`acmart`)

Reference specifications for ACM conference proceedings (`\documentclass[sigconf]{acmart}`) and ACM journals (`\documentclass[acmsmall]{acmart}`).

## 1. Document Class & Mandatory Metadata Blocks

- **Conference Proceedings**: `\documentclass[sigconf,review,anonymous]{acmart}` (for double-blind submission; remove `review,anonymous` for camera-ready).
- **Journals (TOIS, TIST, TKDD, PACM)**: `\documentclass[acmsmall]{acmart}` (single-column journal layout).
- **Mandatory Post-Abstract Sections**:
  1. **CCS Concepts**: Structured taxonomy block generated from the ACM Computing Classification System (`\begin{CCSXML}...\end{CCSXML}` + `\ccsdesc[500]{...}`).
  2. **Keywords**: Comma-separated terms via `\keywords{...}`.
- **Title & Teaser**: Supports an optional full-width `\begin{teaserfigure}...\end{teaserfigure}` rendered directly beneath the author block before `\maketitle`.

## 2. Layout, Headings & Visuals

- **Abstract & Body**: In `sigconf`, title/authors span full width while the abstract and main body use a two-column layout; `acmsmall` uses single-column layout.
- **Headings**: Arabic numbered (`1 Introduction`, `1.1 Motivation`).
- **Tables**: Captions **above** the table using `booktabs` (`\toprule`, `\midrule`, `\bottomrule`); never use vertical borders.
- **Figures**: Captions **below** the figure; include `\Description{...}` inside every `\begin{figure}` for screen-reader accessibility (required for ACM camera-ready!).

## 3. ACM Reference Format (`ACM-Reference-Format.bst`)

- Use `\bibliographystyle{ACM-Reference-Format}` with `natbib` (`\cite{key}` for numbered conferences like KDD/SIGIR/CHI/WWW, or author-year `\citet`/`\citep` for journals like TOIS/TOG).
- Always include full author names (ACM prefers full first names over initials), complete venue title, year, page range or article number, and DOI.
- Never alter `acmart` margins, font sizes, or bibliography spacing—TAPS (The ACM Publishing System) validates package whitelist compliance automatically at camera-ready.
