---
name: paper-orchestra-run
description: >-
  Execute PaperOrchestra's multi-agent paper generation pipeline via CLI
  (`paper_writing_cli.py`), parallel batch runner (`run_batch_writeup`), or the
  Streamlit web UI (`frontend/app.py`). Use this skill when generating a manuscript,
  selecting writer/reflection/plotting/image models, monitoring background pipeline
  runs, or inspecting and resuming intermediate stage outputs.
---

# Running PaperOrchestra Pipelines

## 1. Pre-Run Checklist

1. Run `skills/paper-orchestra-setup/scripts/preflight_check.py` to confirm credentials and `pdflatex`/`bibtex` are ready.
2. Validate your `<raw_materials_dir>` with `skills/research-ideation-and-prep/scripts/prepare_raw_materials.py validate --dir <raw_materials_dir>`.

## 2. Single-Paper CLI Execution (`paper_writing_cli.py`)

Run inside the `paper_orchestra` Conda environment. Because a full 5-stage run takes several minutes and makes external LLM + Semantic Scholar API calls, run with `WaitMsBeforeAsync: 500` (and `BypassSandbox: true` if network access is required) so Antigravity tracks the run asynchronously via `manage_task`:

```bash
conda run --no-capture-output -n paper_orchestra python paper_writing_cli.py \
  --raw_materials_dir projects/my_study/raw_materials \
  --latex_template_dir templates/cvpr2025 \
  --output_dir ./paper_output_my_study \
  --idea_filename idea_sparse.md \
  --experimental_log_filename experimental_log.md \
  --use_plotting true
```

### Key CLI Flags & Model Overrides

| Flag | Default | Notes |
| :--- | :--- | :--- |
| `--raw_materials_dir` | *(required)* | Folder containing idea markdown, experimental log markdown, and optional `figures/`. |
| `--latex_template_dir` | *(required)* | Target conference template folder (e.g. `templates/cvpr2025`, `templates/iclr2025`). |
| `--output_dir` | `./paper_output_<timestamp>` | Destination folder for all stage artifacts and `final_paper.pdf`. |
| `--use_plotting` | `False` | Set `true` to invoke `PlottingAgent` (Matplotlib plots + Gemini conceptual diagrams). Set `false` if pre-made figures already exist in `<raw_materials_dir>/figures/`. |
| `--writer_model_name` | `gemini-3.1-pro-preview` | Model for `OutlineAgent`, `HybridLiteratureAgent`, and `SectionWritingAgent` (also supports OpenAI `gpt-*`/`o3*` for writer/outline stages). |
| `--reflection_model_name` | `gemini-3.1-pro-preview` | Model for `ContentRefinementAgent` and `AgentReview` loop. |
| `--plotting_model_name` | `gemini-3.1-pro-preview` | Reasoning/code model for `PlottingAgent`. |
| `--image_model_name` | `gemini-3-pro-image-preview` | Image generation model for conceptual diagrams (e.g. `gemini-nano-banana-2.1` or `gemini-3-pro-image`). |
| `--plotting_max_critic_rounds` | `3` | Self-correction rounds per generated figure. |
| `--research_cutoff` | Current `YYYY-MM` | Filters Semantic Scholar papers published on or after `YYYY-MM-01` (useful for historical benchmarks or backtesting). |

## 3. Inspecting Intermediate Outputs & Partial Reruns

Avoid re-running the entire pipeline when debugging a single stage! Read [pipeline_artifacts.md](./references/pipeline_artifacts.md) for the exact output directory tree and Python snippets to rerun individual agents (`OutlineAgent`, `HybridLiteratureAgent`, `PlottingAgent`, `SectionWritingAgent`, or `ContentRefinementAgent`) on an existing `--output_dir`.

## 4. Batch Paper Generation (`run_batch_writeup`)

To process multiple papers in parallel with automatic checkpoint/resume (`paper_writing_log.json`), call `methods.paper_writer_with_plotting.run_batch_writeup` (or `methods.paper_writer.run_batch_writeup` without plotting):

```python
from methods.paper_writer_with_plotting import run_batch_writeup

run_batch_writeup(
    latex_template_dir="templates/iclr2025",
    process_root_folder=False,
    paper_info_path="datasets/papers_manifest.json",
    output_dir="./paper_output_batch",
    max_workers=4,
)
```

## 5. Launching the Interactive Streamlit Frontend

Start the server as a daemon (`IsDaemon: true`, `WaitMsBeforeAsync: 3000`):

```bash
conda run --no-capture-output -n paper_orchestra streamlit run frontend/app.py
```

If the user asks to open or interact with the Streamlit app visually, immediately delegate `http://localhost:8501` to Antigravity's `browser` subagent after starting the server. Clean up orphan background runs if needed via `pkill -f paper_writing_cli.py`.
