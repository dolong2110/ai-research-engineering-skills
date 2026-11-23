---
name: end-to-end-research-workflow
description: >-
  Combine Antigravity's native agent orchestration (`run_workflow`, custom subagents,
  and swarms) with PaperOrchestra to conduct end-to-end AI/scientific research: gap
  discovery, hypothesis design, code implementation, parallel ablations, metric
  harvesting, paper writing, and reviewer-driven iteration. Use this skill when the
  user wants to run an actual research project from scratch or close the loop between
  experiments and manuscript writing.
---

# End-to-End Research Workflow (Antigravity + PaperOrchestra)

PaperOrchestra automates the **downstream synthesis half** of research (`raw_materials/` -> literature grounding -> figures -> LaTeX draft -> peer-review refinement). **Antigravity** provides the **upstream discovery & experimentation half** (surveying literature, writing code, running baselines/ablations, and analyzing logs). Together, they form a closed-loop research system:

```text
[1. Literature & Gap Scout]  (Antigravity `literature-scout` / Gemini Deep Research)
            │
            ▼
[2. Hypothesis & Plan]       (`projects/<slug>/raw_materials/idea_sparse.md`)
            │
            ▼
[3. Code & Parallel Runs]    (Antigravity `run_workflow` / `experiment-analyst`)
            │
            ▼
[4. Verified Experiment Log] (`projects/<slug>/raw_materials/experimental_log.md`)
            │
            ▼
[5. Manuscript Synthesis]    (`paper_writing_cli.py` -> `final_paper.pdf`)
            │
            ▼
[6. Peer-Review Loop]        (`AgentReview` -> new ablations in Step 3 if needed)
```

## Executing Each Phase

### Phase 1: Literature Scouting & Gap Identification
- Delegate to `agents/literature-scout.md` via `invoke_subagent`, or run Gemini Deep Research (`gemini-api agent run ... --agent deep-research-preview-04-2026 --background`) when the `gemini-api-cli` skill is available.
- Output a falsifiable hypothesis, explicit baseline comparison list, and ablation matrix into `projects/<slug>/raw_materials/idea_sparse.md` using `research-ideation-and-prep`.

### Phase 2: Parallel Experimentation & Ablations (`run_workflow`)
- When running multiple baselines, seeds, or component ablations across code files or configs, read Antigravity's built-in `run-workflow` skill and adapt [research_to_paper_workflow.py](./examples/research_to_paper_workflow.py).
- Use `workspace="branch"` when parallel agents modify model architectures concurrently, or `workspace="inherit"` when sweeping CLI flags into separate output directories.
- Aggregate only **actual measured metrics** (mean ± std across seeds where applicable) into `projects/<slug>/raw_materials/experimental_log.md`.

### Phase 3: Paper Synthesis & Grounded Citations
- Validate `raw_materials/` and launch `paper_writing_cli.py` (`paper-orchestra-run`).
- Audit citations (`literature-and-citations`) and visually inspect 2x2 page grids (`latex-template-and-build`).

### Phase 4: Reviewer-Driven Iteration
- Run `paper-peer-review-and-eval` (`ensemble=3`).
- If reviewers flag an unsupported claim or missing ablation (`Soundness < 3` or `Overall < 7`), loop back to Phase 2 to execute the missing experiment rather than weakening rigor with hand-wavy text.

## Helpful Antigravity Slash Commands to Recommend
- `/boost` or `/plan`: Before designing complex experimental protocols and ablation matrices.
- `/teamwork`: When coordinating long-running multi-agent research teams across implementation, benchmarking, and analysis.
- `/goal`: For autonomous multi-hour experiment-and-refinement sweeps with clear stopping criteria.
