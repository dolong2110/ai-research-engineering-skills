#!/usr/bin/env python3
"""CLI wrapper for PaperOrchestra's AgentReview ensemble reviewer and SxS PDF comparator."""

import argparse
import json
import sys
from pathlib import Path

def _add_paper_orchestra_to_path() -> None:
    for base in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (base / "autoraters" / "agent_review.py").exists():
            if str(base) not in sys.path:
                sys.path.insert(0, str(base))
            return
    parents = Path(__file__).resolve().parents
    if len(parents) > 4 and (parents[4] / "autoraters" / "agent_review.py").exists():
        if str(parents[4]) not in sys.path:
            sys.path.insert(0, str(parents[4]))


_add_paper_orchestra_to_path()


def format_review_markdown(review: dict, pdf_name: str, model: str, ensemble: int) -> str:
    lines = [
        f"# Peer Review Report: `{pdf_name}`",
        "",
        f"- **Evaluator Model:** `{model}` (Ensemble size: {ensemble})",
        f"- **Overall Score:** **{review.get('Overall', 'N/A')} / 10**",
        f"- **Decision:** **{review.get('Decision', 'N/A')}** (Confidence: {review.get('Confidence', 'N/A')}/5)",
        f"- **Sub-scores (1–4):** Originality `{review.get('Originality', '-')}` | Quality `{review.get('Quality', '-')}` | Clarity `{review.get('Clarity', '-')}` | Significance `{review.get('Significance', '-')}` | Soundness `{review.get('Soundness', '-')}` | Presentation `{review.get('Presentation', '-')}` | Contribution `{review.get('Contribution', '-')}`",
        "",
        "## Summary",
        str(review.get("Summary", "")),
        "",
    ]
    for section in ["Strengths", "Weaknesses", "Questions", "Limitations"]:
        val = review.get(section, [])
        lines.append(f"## {section}")
        if isinstance(val, list):
            for item in val:
                lines.append(f"- {item}")
        else:
            lines.append(str(val))
        lines.append("")
    return "\n".join(lines)


def cmd_review(args: argparse.Namespace) -> int:
    from utils.pdf_utils import load_paper
    from autoraters.agent_review import perform_review_agentreview

    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"[FAIL] PDF not found: {pdf_path}")
        return 1

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    paper_text = load_paper(str(pdf_path))
    review = perform_review_agentreview(
        text=paper_text,
        model_name=args.model,
        num_review_ensemble=args.ensemble,
    )

    json_path = out_dir / "review_report.json"
    md_path = out_dir / "review_report.md"
    json_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(
        format_review_markdown(review, pdf_path.name, args.model, args.ensemble),
        encoding="utf-8",
    )
    print(f"[OK] Saved structured review to {json_path}")
    print(f"[OK] Saved Markdown report to {md_path}")
    print(f"     Overall: {review.get('Overall')}/10 | Decision: {review.get('Decision')}")
    return 0


def cmd_sxs(args: argparse.Namespace) -> int:
    from autoraters.sxs_paper_quality import rate_sxs_paper_quality

    pdf_a = Path(args.pdf_a).resolve()
    pdf_b = Path(args.pdf_b).resolve()
    for p in (pdf_a, pdf_b):
        if not p.exists():
            print(f"[FAIL] PDF not found: {p}")
            return 1

    res = rate_sxs_paper_quality(str(pdf_a), str(pdf_b), model_name=args.model)
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Saved SxS comparison to {out_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AgentReview or SxS evaluation on PDFs.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_rev = sub.add_parser("review", help="Run ensemble AgentReview on a single PDF.")
    p_rev.add_argument("--pdf", required=True, help="Path to target PDF.")
    p_rev.add_argument("--model", default="gemini-3.1-pro-preview")
    p_rev.add_argument("--ensemble", type=int, default=3)
    p_rev.add_argument("--out-dir", default="./review_output")
    p_rev.set_defaults(func=cmd_review)

    p_sxs = sub.add_parser("sxs", help="Compare two PDFs side by side.")
    p_sxs.add_argument("--pdf-a", required=True, help="First PDF (Paper 1).")
    p_sxs.add_argument("--pdf-b", required=True, help="Second PDF (Paper 2).")
    p_sxs.add_argument("--model", default="gemini-3.1-pro-preview")
    p_sxs.add_argument("--out", default="./sxs_result.json")
    p_sxs.set_defaults(func=cmd_sxs)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
