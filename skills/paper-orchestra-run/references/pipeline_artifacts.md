# PaperOrchestra Stage Artifacts & Selective Rerun Guide

Every single-paper run (`--output_dir <base_dir>`) produces a deterministic folder layout:

```text
<base_dir>/
├── raw_materials/                        # Snapshot copy of input materials
│   ├── idea_sparse.md
│   ├── experimental_log.md
│   └── figures/                          # Pre-supplied figures (if --use_plotting false)
├── outline.json                          # Stage 1 (OutlineAgent); overwritten by outline_v1.json after Stage 2
├── literature_agent_output/              # Stage 2A (HybridLiteratureAgent)
│   ├── outline_v1.json                   # Enriched outline with grounded citations
│   ├── updated_template.tex              # Template with Related Work / Intro citations wired
│   ├── references.bib                    # Verified BibTeX bibliography
│   └── citation_map.json                 # Registry mapping citation_key -> PaperData metadata
├── plotting_results.json                 # Stage 2B (PlottingAgent, when --use_plotting true)
├── figures/                              # Generated figures prior to copy into latex_writeup/figures/
├── latex_writeup/                        # Stage 3 (SectionWritingAgent)
│   ├── template.tex                      # Active conference template
│   ├── guidelines.md                     # Conference formatting rules
│   ├── references.bib                    # Copied from literature_agent_output/
│   ├── figures/                          # Final figures + info.json manifest
│   │   └── info.json                     # [{"name": "...", "caption": "..."}]
│   └── raw_draft_paper.tex               # Complete initial LaTeX draft before refinement
├── content_refinement_workdir/           # Stage 4 (ContentRefinementAgent)
│   ├── peer_reviews/
│   │   └── review_v0.json ...            # AgentReview scores & feedback per iteration
│   └── pdf_screenshots/
│       ├── content_refinement/
│       └── format_refinement/            # 2x2 page grids evaluated by VLM
├── time_breakdown.json                   # Per-stage wall-clock runtime (seconds)
└── final_paper.pdf                       # Final compiled submission-ready manuscript
```

## Rerunning Only Stage 3 (`SectionWritingAgent`)

If `outline.json`, `literature_agent_output/citation_map.json`, and `latex_writeup/figures/info.json` already exist:

```python
from methods.agents.section_writing_agent import SectionWritingAgent

base = "./paper_output_my_study"
agent = SectionWritingAgent(
    outline_path=f"{base}/outline.json",
    template_path=f"{base}/latex_writeup/template.tex",
    idea_path=f"{base}/raw_materials/idea_sparse.md",
    experimental_log_path=f"{base}/raw_materials/experimental_log.md",
    citation_map_path=f"{base}/literature_agent_output/citation_map.json",
    figures_info_path=f"{base}/latex_writeup/figures/info.json",
    guidelines_path=f"{base}/latex_writeup/guidelines.md",
    model_name="gemini-3.1-pro-preview",
)
agent.run(output_path=f"{base}/latex_writeup/raw_draft_paper.tex")
```

## Rerunning Only Stage 4 (`ContentRefinementAgent`)

If Stage 4 failed solely because `pdflatex`/`bibtex` was missing earlier, install TeX Live and rerun Stage 4 directly without paying for Stages 1–3 again:

```python
import shutil
from methods.agents.content_refinement_agent import ContentRefinementAgent

base = "./paper_output_my_study"
workdir = f"{base}/content_refinement_workdir"
shutil.copytree(f"{base}/latex_writeup", workdir, dirs_exist_ok=True)

refiner = ContentRefinementAgent(
    experimental_log_path=f"{base}/raw_materials/experimental_log.md",
    citation_map_path=f"{base}/literature_agent_output/citation_map.json",
    guidelines_path=f"{base}/latex_writeup/guidelines.md",
    model_name="gemini-3.1-pro-preview",
    max_reflections=3,
    work_dir=workdir,
)
pdf_out = refiner.run(texfile_path=f"{base}/latex_writeup/raw_draft_paper.tex")
shutil.copy(pdf_out, f"{base}/final_paper.pdf")
```
