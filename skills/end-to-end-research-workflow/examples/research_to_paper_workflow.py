"""Example Antigravity `run_workflow` script orchestrating parallel ablations into PaperOrchestra.

Run via the `run_workflow` tool:
  run_workflow(
      ScriptPath="/abs/path/to/.agents/skills/end-to-end-research-workflow/examples/research_to_paper_workflow.py",
      Description="Run ablation suite, compile experimental_log.md, and validate PaperOrchestra inputs",
      Args={
          "project_slug": "my_study",
          "ablations": ["full_model", "no_temporal_branch", "no_adapter"],
      },
  )
"""

project_slug = args.get("project_slug", "demo_study")
ablations = args.get("ablations", ["full_model", "ablation_a", "ablation_b"])
raw_dir = f"projects/{project_slug}/raw_materials"

phase("1. Scaffold & Hypothesis")
await agent(
    f"Use the `research-ideation-and-prep` skill to ensure `{raw_dir}` is initialized and `idea_sparse.md` clearly documents the hypothesis and planned ablations: {ablations}.",
    schema={"type": "string"},
    role="Hypothesis Architect",
)

phase("2. Parallel Ablation Runs")
ablation_SCHEMA = {
    "type": "object",
    "properties": {
        "variant": {"type": "string"},
        "metrics": {"type": "object"},
        "notes": {"type": "string"},
    },
    "required": ["variant", "metrics", "notes"],
}

results = await parallel(
    ablations,
    lambda variant: agent(
        f"Execute experiment variant `{variant}` for project `{project_slug}`, save raw logs under `projects/{project_slug}/runs/{variant}/`, and return the exact measured evaluation metrics.",
        schema=ablation_SCHEMA,
        role=f"Run {variant}",
    ),
)
log(f"Collected {len(results)} experiment runs.")

phase("3. Compile & Validate Raw Materials")
summary = await agent(
    f"Aggregate these verified experiment results into `{raw_dir}/experimental_log.md` following `research-ideation-and-prep`, then run `prepare_raw_materials.py validate --dir {raw_dir}`:\n\n{results}",
    schema={"type": "string"},
    role="Experiment Log Synthesizer",
)
log(summary)
