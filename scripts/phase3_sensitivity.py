"""Phase 3: how strong must the HIDDEN vulnerability->prone channel be for a
no-real-effect marker world to fake the historical adjusted odds ratio?

Run:  python scripts/phase3_sensitivity.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.scm import Era  # noqa: E402
from sids_sim.sensitivity import (analytic_evalue, calibrated_marker_base,  # noqa: E402
                                  marker_metrics_at_gamma, solve_gamma_for_or)

TARGET_OR_PRE = 2.86
TARGET_OR_POST = 3.93


def main():
    print("Phase 3 -- sensitivity of the marker world to a hidden V->prone channel.\n")
    print("Calibrating marker base (gamma=0) ...")
    base = calibrated_marker_base()

    print("\nSweep: adjusted prone OR as the hidden channel (gamma) grows.")
    print(f"{'gamma':>6}{'OR(V->prone)':>14}{'OR(V->death)':>14}"
          f"{'prone|vuln':>12}{'prone|non':>11}{'ADJ prone OR':>14}")
    for g in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]:
        m = marker_metrics_at_gamma(base, g, Era.PRE)
        print(f"{g:>6.1f}{m['leg_V_to_prone_or']:>14.2f}{m['leg_V_to_death_or']:>14.2f}"
              f"{m['prone_in_vuln']:>12.3f}{m['prone_in_nonvuln']:>11.3f}"
              f"{m['adjusted_prone_or']:>14.2f}")

    print("\nSolving for the gamma* that fakes each historical OR (pre era):")
    g_pre = solve_gamma_for_or(base, TARGET_OR_PRE, Era.PRE)
    g_post = solve_gamma_for_or(base, TARGET_OR_POST, Era.PRE)
    for label, tgt, g in [("pre OR 2.86", TARGET_OR_PRE, g_pre),
                          ("post OR 3.93", TARGET_OR_POST, g_post)]:
        if g is None:
            print(f"  {label}: UNREACHABLE even at gamma=6 (marker cannot fake it)")
            continue
        m = marker_metrics_at_gamma(base, g, Era.PRE)
        print(f"  {label}: gamma* = {g:.2f}")
        print(f"      => vulnerable babies placed prone {m['prone_in_vuln']:.0%} "
              f"vs {m['prone_in_nonvuln']:.0%} for non-vulnerable")
        print(f"      => hidden V->prone association OR = {m['leg_V_to_prone_or']:.2f}")
        print(f"      => (the other leg, V->death, OR = {m['leg_V_to_death_or']:.2f})")

    print("\nAnalytic VanderWeele-Ding E-values (both legs must exceed these):")
    print(f"  observed OR {TARGET_OR_PRE}  -> E-value {analytic_evalue(TARGET_OR_PRE):.2f}")
    print(f"  observed OR {TARGET_OR_POST} -> E-value {analytic_evalue(TARGET_OR_POST):.2f}")
    print("\nPlausibility yardsticks (known SIDS associations, ORs):")
    print("  maternal smoking ~2 (light) to ~12.7 (>20/day); bed-sharing ~2;")
    print("  not breastfeeding ~1.5-1.9. A confounder needs BOTH legs above the")
    print("  E-value to fully explain the prone effect away.")


if __name__ == "__main__":
    main()
