"""Phase 1 smoke test: simulate all three worlds x both eras, print marginals.

Run:  python scripts/phase1_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from sids_sim.scm import Era, SimConfig, World, simulate_cohort  # noqa: E402
from sids_sim.summarize import summarize, summary_frame  # noqa: E402

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def main() -> None:
    rows = []
    for world in World:
        for era in Era:
            df = simulate_cohort(SimConfig(n=400_000, era=era, world=world, seed=7))
            rows.append(summarize(df))

    table = summary_frame(rows)
    print("\n=== Phase 1 marginals (hand-set params, NOT yet calibrated) ===\n")
    print(table.to_string())

    print("\n--- Real-world targets for reference (DESIGN.md section 5) ---")
    print("  death_rate_per_1000 : pre 1.2  -> post 0.4")
    print("  prone_prev_in_cases : pre 0.84 -> post 0.485")
    print("  prone_prev_controls : pre ~0.50 -> post 0.246")
    print("  crude_prone_OR      : pre ~2.86 -> post ~3.93 (should RISE)")
    print("  vuln_prev_in_cases  : ~0.83  | vuln_prev_overall ~0.37")


if __name__ == "__main__":
    main()
