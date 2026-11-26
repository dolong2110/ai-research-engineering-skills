#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== 1/6 Validating plugin.json, skills, and subagents ==="
python3 - <<'PY'
import json, pathlib, yaml

root = pathlib.Path(".")
manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
allowed = {
    "name", "displayName", "version", "description", "logo",
    "suggestedPrompts", "author", "homepage", "repository", "disabled",
}
unknown = set(manifest.keys()) - allowed
assert not unknown, f"Unknown plugin.json fields: {unknown}"

skills = sorted((root / "skills").glob("*/SKILL.md"))
assert skills, "No skills found"
for s in skills:
    parts = s.read_text(encoding="utf-8").split("---", 2)
    assert len(parts) >= 3, f"Missing YAML frontmatter: {s}"
    meta = yaml.safe_load(parts[1])
    assert meta["name"] == s.parent.name, f"Name mismatch in {s}"
    assert len(meta["description"]) > 20, f"Short description in {s}"

agents = sorted((root / "agents").glob("*.md"))
for a in agents:
    parts = a.read_text(encoding="utf-8").split("---", 2)
    meta = yaml.safe_load(parts[1])
    assert meta["name"] == a.stem, f"Agent name mismatch: {a}"
    assert meta["subagent"] is True and meta["mainAgent"] is False

print(f"[OK] Validated {len(skills)} skills and {len(agents)} subagents (v{manifest['version']}).")
PY

echo ""
echo "=== 2/6 GitHub Repo Readiness Audit ==="
python3 skills/github-repo-and-collaboration/scripts/init_github_repo.py audit --repo .

echo ""
echo "=== 3/6 GitHub Actions Workflow Lint ==="
python3 skills/github-actions-cicd/scripts/lint_workflows.py --repo .

echo ""
echo "=== 4/6 Python & ML Static Code Audit ==="
python3 skills/python-ml-engineering/scripts/ml_code_check.py --path skills

echo ""
echo "=== 5/6 Security & Production Readiness Scan ==="
python3 skills/security-and-production-ops/scripts/security_static_scan.py --path skills

echo ""
echo "=== 6/6 Algorithm, Math, Serving, Causal, RL, Conformal & Roofline Self-Tests ==="
python3 skills/algorithms-and-data-structures/scripts/benchmark_and_complexity.py --self-test --sizes 200,400,800
python3 skills/math-proofs-and-theoretical-analysis/scripts/verify_math_numerically.py --self-test
python3 skills/model-serving-and-inference-optimization/scripts/benchmark_inference_latency.py --self-test
python3 skills/causal-inference-and-econometrics/scripts/causal_diagnostics.py --self-test
python3 skills/reinforcement-learning-and-decision-making/scripts/rliable_eval.py --self-test
python3 skills/bayesian-uncertainty-and-active-learning/scripts/calibration_and_conformal.py --self-test
python3 skills/systems-cpp-rust-triton-kernels/scripts/roofline_analyzer.py --self-test

echo ""
echo "ALL LOCAL CI CHECKS PASSED."
