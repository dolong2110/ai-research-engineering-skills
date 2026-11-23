---
name: scientific-plotting-and-diagrams
description: >-
  Generate, critique, and register publication-grade statistical plots (Matplotlib)
  and conceptual architecture diagrams (`PlottingAgent`, `paper_banana_utils.py`, or
  standalone scripts), and synchronize `figures/info.json`. Use this skill when
  creating paper figures, editing plots, preparing pre-made visuals for
  `--use_plotting false`, or fixing figure inclusion issues in LaTeX.
---

# Scientific Plotting & Conceptual Diagrams

PaperOrchestra supports two figure workflows:
1. **Automated (`--use_plotting true`)**: `PlottingAgent` (`methods/agents/plotting_agent.py` + `utils/paper_banana_utils.py`) reads figure plans from `outline.json`, selects `"plot"` (executes generated Matplotlib code via `execute_plot_code_worker`) or `"diagram"` (calls `generate_image_with_gemini` without baked-in titles), runs up to `max_critic_rounds` multimodal VLM critiques, generates captions, and writes `<writeup_dir>/figures/info.json`.
2. **Pre-supplied / Custom (`--use_plotting false` or post-draft upgrades)**: Place `.pdf`, `.png`, or `.jpg` files in `<raw_materials_dir>/figures/` (or `<writeup_dir>/figures/`) and synchronize `figures/info.json`.

## Publication Figure Standards (Enforced by Conference Guidelines)

When writing custom Matplotlib/Seaborn scripts or delegating diagram creation:
- **Accessibility**: Never rely on color alone (especially red vs. green) to distinguish series—pair colorblind-safe palettes (Okabe-Ito / Viridis / Tableau Colorblind) with distinct markers (`o`, `s`, `^`, `D`) and line styles (`-`, `--`, `-.`).
- **Typography**: Match figure axis/tick/legend font sizes to 9–10pt conference body text when scaled to column width (`\linewidth` ~3.25 in) or full width (`\textwidth` ~6.875 in). Avoid embedding a top title inside the image itself—the LaTeX `\caption{...}` carries the title.
- **High-DPI / Vector Export**: Prefer vector `.pdf` (with `plt.rcParams["pdf.fonttype"] = 42` so TrueType fonts embed cleanly) or `dpi=300` `.png` with `bbox_inches="tight"`.
- **LaTeX Path Rule**: Every `\includegraphics` in PaperOrchestra templates MUST use `figures/<filename>` (never bare `<filename>`), and `\centering` rather than `\begin{center}...\end{center}`.

## Synchronizing `figures/info.json`

`SectionWritingAgent` reads `<writeup_dir>/figures/info.json` (`[{"name": "<file>", "caption": "<description>"}]`) to know which visual assets exist and where to place `\begin{figure}` / `\begin{figure*}` blocks.

Run [sync_figures_info.py](./scripts/sync_figures_info.py) whenever you add, rename, or replace figures manually:

```bash
python3 skills/scientific-plotting-and-diagrams/scripts/sync_figures_info.py \
  --figures-dir paper_output_my_study/latex_writeup/figures
```

## Standalone Single-Figure Generation via `PlottingAgent`

To regenerate a single figure from an existing `outline.json` plan without rerunning all figures:

```python
from methods.agents.plotting_agent import process_single_figure

fig_plan = {
    "figure_id": "fig_ablation",
    "title": "Component Ablation on Unseen Split",
    "plot_type": "plot",          # "plot" (Matplotlib) or "diagram" (Gemini Image)
    "data_source": "experimental_log.md",
    "objective": "Grouped bar chart comparing Full model vs. ablations on Seen and Unseen J/F.",
    "aspect_ratio": "16:9",
}
result = process_single_figure(
    fig_plan=fig_plan,
    raw_materials_dir="projects/my_study/raw_materials",
    model_name="gemini-3.1-pro-preview",
    image_model_name="gemini-3-pro-image-preview",
    max_critic_rounds=3,
)
```
