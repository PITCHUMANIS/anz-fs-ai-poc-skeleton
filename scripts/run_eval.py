#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anz_fs_poc.config import get_settings
from anz_fs_poc.eval.runner import run_golden_set


def main() -> None:
    settings = get_settings()
    report = run_golden_set(settings.golden_set_path)
    print(json.dumps(report, indent=2))
    # Gate the PoC on the pre-agreed thresholds (article §7.3), not just on
    # whether every case happened to pass.
    if not report["gate"]["all_met"]:
        print("\nGATE: NOT MET — thresholds below target.", file=sys.stderr)
        sys.exit(1)
    if report["failed"]:
        print("\nGATE: thresholds met but individual case(s) failed — review.", file=sys.stderr)
        sys.exit(1)
    print("\nGATE: MET — all thresholds satisfied.", file=sys.stderr)


if __name__ == "__main__":
    main()
