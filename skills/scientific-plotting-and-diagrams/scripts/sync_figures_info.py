#!/usr/bin/env python3
"""Scan a `figures/` directory and create/update `figures/info.json` for SectionWritingAgent."""

import argparse
import json
import sys
from pathlib import Path

VALID_EXTS = {".pdf", ".png", ".jpg", ".jpeg"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync figures/ directory with figures/info.json.")
    parser.add_argument("--figures-dir", required=True, help="Path to figures/ directory.")
    parser.add_argument(
        "--prune-missing",
        action="store_true",
        help="Remove entries from info.json whose image files no longer exist.",
    )
    args = parser.parse_args()

    fig_dir = Path(args.figures_dir).resolve()
    if not fig_dir.is_dir():
        print(f"[FAIL] Figures directory does not exist: {fig_dir}")
        return 1

    info_path = fig_dir / "info.json"
    existing_by_name: dict[str, dict] = {}
    if info_path.exists():
        try:
            loaded = json.loads(info_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                for item in loaded:
                    if isinstance(item, dict) and "name" in item:
                        existing_by_name[item["name"]] = item
        except json.JSONDecodeError as exc:
            print(f"[WARN] Existing info.json had invalid JSON ({exc}); rebuilding.")

    disk_files = sorted(
        f.name for f in fig_dir.iterdir() if f.is_file() and f.suffix.lower() in VALID_EXTS
    )

    updated: list[dict] = []
    added = 0
    for fname in disk_files:
        if fname in existing_by_name:
            updated.append(existing_by_name[fname])
        else:
            stem_label = Path(fname).stem.replace("_", " ").replace("-", " ").capitalize()
            updated.append(
                {
                    "name": fname,
                    "caption": f"TODO: Provide descriptive caption for {stem_label} ({fname}).",
                }
            )
            added += 1

    missing_on_disk = [k for k in existing_by_name if k not in set(disk_files)]
    if missing_on_disk and not args.prune_missing:
        for k in missing_on_disk:
            updated.append(existing_by_name[k])
        print(
            f"[WARN] {len(missing_on_disk)} entry/entries in info.json missing on disk ({', '.join(missing_on_disk)}). Pass --prune-missing to drop them."
        )

    info_path.write_text(json.dumps(updated, indent=4) + "\n", encoding="utf-8")
    todo_count = sum(1 for x in updated if str(x.get("caption", "")).startswith("TODO:"))
    print(f"[OK] Synced {info_path} ({len(updated)} total figure(s), {added} newly added).")
    if todo_count:
        print(f"[INFO] {todo_count} figure(s) have placeholder 'TODO:' captions — update them in {info_path} before running SectionWritingAgent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
