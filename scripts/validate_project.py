from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.ensure_data_files import SCHEMAS


def main() -> None:
    failures = []
    summary = {}
    for filename, required in SCHEMAS.items():
        path = ROOT / "data" / filename
        if not path.exists():
            failures.append(f"missing: data/{filename}")
            continue
        try:
            df = pd.read_csv(path)
        except Exception as exc:
            failures.append(f"unreadable data/{filename}: {exc}")
            continue
        missing = [c for c in required if c not in df.columns]
        if missing:
            failures.append(f"data/{filename} missing columns: {missing}")
        summary[filename] = {"rows": len(df), "columns": list(df.columns)}
    for rel in [
        ".github/workflows/update-and-deploy.yml",
        ".github/workflows/backfill-crowding.yml",
        "scripts/update_data.py",
        "scripts/build_site.py",
        "src/pipeline.py",
        "src/providers.py",
        "src/extended_providers.py",
        "public/index.html",
    ]:
        if not (ROOT / rel).exists():
            failures.append(f"missing: {rel}")
    result = {"ok": not failures, "failures": failures, "data": summary}
    (ROOT / "data" / "manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
