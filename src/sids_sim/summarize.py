"""Quick marginals + crude odds ratio from a simulated cohort.

These are the eyeball checks for Phase 1 -- do the generated rates land in a sane
neighbourhood of the real world? Formal calibration against data/calibration/
targets.json is Phase 2.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def crude_prone_or(df: pd.DataFrame) -> float:
    """Case-control odds ratio for prone, using deaths as cases and survivors as
    controls (the design the historical studies used). 0.5 continuity correction.
    """
    cases = df[df.death == 1]
    controls = df[df.death == 0]
    a = (cases.prone == 1).sum() + 0.5      # prone deaths
    b = (cases.prone == 0).sum() + 0.5      # non-prone deaths
    c = (controls.prone == 1).sum() + 0.5   # prone survivors
    d = (controls.prone == 0).sum() + 0.5   # non-prone survivors
    return float((a / b) / (c / d))


def summarize(df: pd.DataFrame) -> dict:
    n = len(df)
    deaths = int(df.death.sum())
    return {
        "world": df.world.iloc[0],
        "era": df.era.iloc[0],
        "n": n,
        "death_rate_per_1000": round(1000 * deaths / n, 3),
        "prone_prev_overall": round(float(df.prone.mean()), 3),
        "prone_prev_in_cases": round(float(df.loc[df.death == 1, "prone"].mean()), 3),
        "prone_prev_in_controls": round(float(df.loc[df.death == 0, "prone"].mean()), 3),
        "smoke_prev": round(float(df.smoke.mean()), 3),
        "vuln_prev_overall": round(float(df.vulnerable.mean()), 3),
        "vuln_prev_in_cases": round(float(df.loc[df.death == 1, "vulnerable"].mean()), 3),
        "crude_prone_OR": round(crude_prone_or(df), 2),
    }


def summary_frame(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows).set_index(["world", "era"])
