# Academic Style, Notation & LaTeX Anti-Patterns

## 1. Banned AI-isms & Reviewer Red-Flag Phrasing

| Avoid (AI-Slop / Vague Hype) | Prefer (Direct Scientific Prose) |
| :--- | :--- |
| "In recent years, deep learning has witnessed remarkable progress..." | Start directly with the task and open bottleneck. |
| "delve into", "tapestry", "testament to", "pivotal", "realm", "foster", "underscore" | "analyze", "demonstrate", "central", "domain", "enable", "confirm" |
| "Our novel and groundbreaking framework..." | Let Contribution bullets and empirical deltas establish novelty; use "novel" at most once in the paper. |
| "outperforms baselines by a huge / dramatic / significant margin" | "improves Unseen $\mathcal{J}$ by $+5.04\%$ over EEMC ($p < 0.01$)" |
| "As can be clearly seen in Table 1, Table 1 shows that..." | "**TSAM improves unseen generalization.** Our method surpasses EEMC by $+5.04\%$ $\mathcal{J}$ (\cref{tab:main})..." |
| "obviously", "trivially", "it is easy to see" | State the 1-line derivation or cite the lemma. |

## 2. Mathematical Notation Consistency Table

Keep one consistent convention across prose, equations, and figures:
- **Scalars / indices**: Italic lowercase/uppercase ($x, i, t, N, T, k, \lambda$).
- **Vectors**: Bold lowercase ($\mathbf{x}, \mathbf{q}_i \in \mathbb{R}^d$).
- **Matrices / Tensors**: Bold uppercase ($\mathbf{X} \in \mathbb{R}^{N \times d}$, $\mathbf{F}_t \in \mathbb{R}^{H \times W \times C}$).
- **Sets / Spaces / Losses**: Calligraphic ($\mathcal{D}, \mathcal{V}, \mathcal{L}_{\text{IoU}}$) or blackboard bold ($\mathbb{R}, \mathbb{E}, \mathbb{P}$).
- **Multi-letter operators**: Roman upright (`\log`, `\exp`, `\sin`, `\max`, `\min`, `\arg\min`, `\operatorname{MLP}`, `\operatorname{Attn}`, `\operatorname{LN}`), never `$MLP(x)$` (which typesets as $M \cdot L \cdot P \cdot (x)$).
- **Norms & Inner Products**: Paired delimiters (`\| \mathbf{x} \|_2`, `\langle \mathbf{u}, \mathbf{v} \rangle`) rather than `||x||`.

## 3. LaTeX Micro-Typography Checklist

1. **Quotation marks**: Use `` ``...'' `` rather than straight `"..."`.
2. **Dashes**: Hyphen `-` for compound words (`cross-modal`), en-dash `--` for numeric ranges and named pairs (`pages 1--8`, ` Kullback--Leibler`), em-dash `---` for parenthetical clauses.
3. **Non-breaking spaces**: Use `~` before `\cite`, `\citep`, `\ref`, and `\eqref` (`Method~\cite{key}`, `Section~\ref{sec:intro}`), or use `\cref{sec:intro}` from `cleveref`.
4. **Percentages & units**: Escape `\%` (`43.4\%`) and separate numbers from units with `\,` (`10\,\text{ms}`, `8\,\text{GPUs}`).
5. **Tables**: Always use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`, `\cmidrule(lr){2-4}`); never use `\hline` or vertical column dividers `|`. Right-align or decimal-align numeric columns and put units/`↑`/`↓` in the column header, not repeated in every cell.
