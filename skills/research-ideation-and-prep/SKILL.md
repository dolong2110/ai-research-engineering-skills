---
name: research-ideation-and-prep
description: >-
  Structure raw research ideas, hypotheses, codebase experiments, training logs,
  and CSV metrics into PaperOrchestra's `raw_materials/` input format (`idea_sparse.md`
  or `idea_dense.md`, `experimental_log.md`, and `figures/`). Use this skill when
  starting a new research paper project, converting real experimental outputs into
  structured logs, unpacking JSON examples, or validating `raw_materials/` before
  running PaperOrchestra.
---

# Research Ideation & Raw Materials Preparation

PaperOrchestra starts from a `<raw_materials_dir>` containing:
1. **Idea document** (`idea_sparse.md` by default on CLI, or `idea_dense.md`): Problem statement, core hypothesis, technical methodology, and expected contributions.
2. **Experimental log** (`experimental_log.md` by default): Datasets/splits, evaluation metrics, baselines, implementation/hyperparameter details, raw numeric Markdown tables, and qualitative/ablation observations.
3. **Optional pre-made figures** (`figures/*.pdf|*.png|*.jpg`): Required when running `--use_plotting false`; optional when `--use_plotting true`.

## Workflows

### A. Scaffold a New Research Project's `raw_materials/`

Run [prepare_raw_materials.py](./scripts/prepare_raw_materials.py) with `init` to create a clean workspace under `projects/<project_slug>/raw_materials/` pre-populated from [idea_template.md](./resources/idea_template.md) and [experimental_log_template.md](./resources/experimental_log_template.md):

```bash
python3 skills/research-ideation-and-prep/scripts/prepare_raw_materials.py init \
  --dest projects/my_study/raw_materials
```

### B. Unpack a JSON Example (e.g. `frontend/examples/cvpr_example.json`)

To test PaperOrchestra quickly or inspect a gold-standard input bundle:

```bash
python3 skills/research-ideation-and-prep/scripts/prepare_raw_materials.py from-json \
  --json frontend/examples/cvpr_example.json \
  --dest projects/cvpr_tsam_demo/raw_materials
```

### C. Harvest Real Codebase & Experiment Logs into `experimental_log.md`

When converting a user's real ML/scientific repository, WandB/TensorBoard exports, CSVs, or notebooks into `raw_materials/`:

1. **Extract exact configurations** from training scripts/configs: backbone/model initialization, dataset splits & sizes, optimizer, learning rate, batch size, epochs/steps, hardware, and random seeds.
2. **Compile lossless numeric Markdown tables** in `## 2. Raw Numeric Data`:
   - Include main comparison tables (ours vs. baselines, clearly marking metric direction with `↑` or `↓`), component ablations, and hyperparameter sensitivity sweeps.
   - **Never invent, interpolate, or round away anomalous results.** If a baseline or ablation is missing, flag it explicitly to the user (or run the experiment first using `end-to-end-research-workflow`) rather than guessing.
3. **Document honest anomalies** in `## 3. Qualitative Observations` (for example, edge cases or subsets where a baseline wins and the technical reason why—`OutlineAgent` and `SectionWritingAgent` use these for grounded discussion and limitations sections).
4. **Match `PlottingAgent` data-source hooks**: `methods/agents/plotting_agent.py` matches `.md` filenames containing `"idea"` or `"experiment"` when gathering raw data for diagrams and Matplotlib plots—keep filenames named `idea_sparse.md` (or `idea_dense.md`) and `experimental_log.md`.

## Validation

Always validate `<raw_materials_dir>` before invoking `paper_writing_cli.py`:

```bash
python3 skills/research-ideation-and-prep/scripts/prepare_raw_materials.py validate \
  --dir projects/my_study/raw_materials \
  --idea-file idea_sparse.md \
  --log-file experimental_log.md
```
