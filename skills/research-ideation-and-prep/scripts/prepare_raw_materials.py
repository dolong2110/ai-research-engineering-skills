#!/usr/bin/env python3
"""Scaffold, unpack, or validate PaperOrchestra `raw_materials/` directories."""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
RESOURCES_DIR = SKILL_DIR / "resources"


def cmd_init(args: argparse.Namespace) -> int:
    dest = Path(args.dest).resolve()
    figures_dir = dest / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    idea_path = dest / args.idea_file
    log_path = dest / args.log_file

    if not idea_path.exists() or args.overwrite:
        shutil.copyfile(RESOURCES_DIR / "idea_template.md", idea_path)
        print(f"[OK] Created {idea_path}")
    else:
        print(f"[SKIP] {idea_path} already exists (pass --overwrite to replace)")

    if not log_path.exists() or args.overwrite:
        shutil.copyfile(RESOURCES_DIR / "experimental_log_template.md", log_path)
        print(f"[OK] Created {log_path}")
    else:
        print(f"[SKIP] {log_path} already exists (pass --overwrite to replace)")

    print(f"[OK] Figures folder ready at {figures_dir}")
    return 0


def cmd_from_json(args: argparse.Namespace) -> int:
    json_path = Path(args.json).resolve()
    if not json_path.exists():
        print(f"[FAIL] JSON file not found: {json_path}")
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    dest = Path(args.dest).resolve()
    figures_dir = dest / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    idea_text = data.get("idea", "").strip()
    log_text = data.get("log", "").strip()
    if not idea_text or not log_text:
        print("[FAIL] JSON must contain non-empty 'idea' and 'log' fields.")
        return 1

    idea_path = dest / args.idea_file
    log_path = dest / args.log_file
    idea_path.write_text(idea_text + "\n", encoding="utf-8")
    log_path.write_text(log_text + "\n", encoding="utf-8")
    print(f"[OK] Wrote {idea_path} ({len(idea_text)} chars)")
    print(f"[OK] Wrote {log_path} ({len(log_text)} chars)")

    fig_rel = data.get("figure_path")
    if fig_rel:
        src_fig = (json_path.parent / fig_rel).resolve()
        if src_fig.exists():
            dst_fig = figures_dir / src_fig.name
            shutil.copyfile(src_fig, dst_fig)
            info = [{"name": src_fig.name, "caption": data.get("figure_caption", "")}]
            (figures_dir / "info.json").write_text(
                json.dumps(info, indent=2) + "\n", encoding="utf-8"
            )
            print(f"[OK] Copied figure {dst_fig} and wrote figures/info.json")
        else:
            print(f"[WARN] Referenced figure_path not found at {src_fig}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    raw_dir = Path(args.dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not raw_dir.is_dir():
        print(f"[FAIL] Directory does not exist: {raw_dir}")
        return 1

    idea_path = raw_dir / args.idea_file
    log_path = raw_dir / args.log_file

    for label, path in [("Idea file", idea_path), ("Experimental log", log_path)]:
        if not path.exists():
            errors.append(f"{label} missing at {path}")
            continue
        content = path.read_text(encoding="utf-8").strip()
        if len(content) < 200:
            warnings.append(f"{label} ({path.name}) is very short ({len(content)} chars).")
        if "..." in content and "[Dataset Name]" in content:
            warnings.append(f"{label} ({path.name}) still contains unfilled template placeholders.")

    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8")
        has_md_table = bool(re.search(r"^\|.+\|\s*$", log_text, re.MULTILINE))
        if not has_md_table:
            warnings.append(
                "experimental_log.md has no Markdown tables (`| col | col |`); numeric tables strongly improve PlottingAgent and SectionWritingAgent accuracy."
            )

    figs_dir = raw_dir / "figures"
    fig_files = (
        [
            f.name
            for f in figs_dir.iterdir()
            if f.is_file() and f.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}
        ]
        if figs_dir.is_dir()
        else []
    )
    if fig_files:
        print(f"[OK] Found {len(fig_files)} figure(s) in {figs_dir}: {', '.join(fig_files)}")
    else:
        print("[INFO] No pre-made figures in `figures/` — run `paper_writing_cli.py` with `--use_plotting true`.")

    for w in warnings:
        print(f"[WARN] {w}")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return 1

    print(f"[OK] Raw materials directory `{raw_dir}` passed validation.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or validate PaperOrchestra raw_materials.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Scaffold a new raw_materials directory from templates.")
    p_init.add_argument("--dest", required=True, help="Destination raw_materials directory.")
    p_init.add_argument("--idea-file", default="idea_sparse.md")
    p_init.add_argument("--log-file", default="experimental_log.md")
    p_init.add_argument("--overwrite", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_json = sub.add_parser("from-json", help="Unpack a JSON example (e.g. cvpr_example.json) into raw_materials.")
    p_json.add_argument("--json", required=True, help="Path to input JSON file.")
    p_json.add_argument("--dest", required=True, help="Destination raw_materials directory.")
    p_json.add_argument("--idea-file", default="idea_sparse.md")
    p_json.add_argument("--log-file", default="experimental_log.md")
    p_json.set_defaults(func=cmd_from_json)

    p_val = sub.add_parser("validate", help="Validate an existing raw_materials directory.")
    p_val.add_argument("--dir", required=True, help="Path to raw_materials directory.")
    p_val.add_argument("--idea-file", default="idea_sparse.md")
    p_val.add_argument("--log-file", default="experimental_log.md")
    p_val.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
