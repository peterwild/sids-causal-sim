"""Phase 5 -- discrimination report: which world(s) reproduce ALL targets?

Scores each calibrated world against data/calibration/targets.json and prints a
pass/fail matrix plus the falsification-gate verdict.

Run:  python scripts/phase5_discrimination.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.discrimination import discriminate  # noqa: E402

_MARK = {True: "PASS", False: "FAIL"}


def main():
    print("Phase 5 -- discrimination report (falsification engine verdict).\n")
    print("Calibrating and scoring three worlds against the published targets ...\n")
    report = discriminate()
    shared_gaps = report.pop("_shared_gaps", [])

    worlds = list(report)
    # header
    print(f"{'target':<28}{'comp':<10}{'expected':>10}  " +
          "".join(f"{w:>16}" for w in worlds))
    print("-" * (48 + 16 * len(worlds)))

    # one row per check (components share target ids; iterate by first world's list)
    checks0 = report[worlds[0]]["checks"]
    for i, c0 in enumerate(checks0):
        gate = " *" if c0.is_gate else ""
        row = f"{c0.target_id + gate:<28}{c0.component:<10}{c0.expected:>10.3f}  "
        for w in worlds:
            c = report[w]["checks"][i]
            cell = f"{c.achieved:.2f} {_MARK[c.passed]}"
            row += f"{cell:>16}"
        print(row)

    print("\nFalsification-gate rise (post must exceed pre):")
    for w in worlds:
        g = report[w]["gate_rise_ok"]
        print(f"  {w:<16} prone-OR rise: {_MARK[g['prone_adjusted_or']]:<6}"
              f"  smoking-PAF rise: {_MARK[g['smoking_attributable_risk']]}")

    print("\nShared model gap (targets reproduced by NO world -- non-discriminating,")
    print("the documented era-model limitation in FINDINGS):")
    print("  " + (", ".join(shared_gaps) if shared_gaps else "(none)"))

    print("\n" + "=" * 78)
    print("DISCRIMINATOR = prone adjusted OR at both eras + its rise across the")
    print("campaign. Only a real prone effect passes it; a pure-marker world cannot.")
    print("-" * 78)
    print(f"{'world':<16}{'calib loss':>12}{'discriminator':>15}{'VERDICT':>12}")
    for w in worlds:
        r = report[w]
        verdict = "SURVIVES" if r["survives"] else "REJECTED"
        disc = _MARK[r["discriminator_pass"]]
        print(f"{w:<16}{r['calib_loss']:>12.2f}{disc:>15}{verdict:>12}")
        other = ", ".join(r["other_failures"])
        if other:
            print(f"{'':16}  (minor out-of-sample misfits: {other})")

    print("\n(* = falsification gate.  External check not scored here: the")
    print(" unaccustomed-prone OR ~19 -- reproduced by the gated mechanism in")
    print(" Phase 4.5, and unreachable by the marker world (see FINDINGS section 3).)")


if __name__ == "__main__":
    main()
