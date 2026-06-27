"""Phase 7 -- exhaustion / bed-sharing displacement (DESIGN.md sections 12, 14).

Shows that the supine recommendation can go net-harmful for exhausted families,
that abstinence framing makes it worse and harm-reduction framing helps, and that
an enforced-supine soother (SNOO-like) defuses the loop.

Run:  python scripts/phase7_displacement.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.displacement import (Family, evaluate_family,  # noqa: E402
                                   solve_exhaustion_threshold)
from sids_sim.mediation import Profile  # noqa: E402

# reuse the Phase 4.5 calibrated triple-world params
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from phase45_linchpin import calibrated_triple_params  # noqa: E402


def _p1000(x):
    return f"{x * 1000:.3f}/1000"


def main():
    print("Phase 7 -- does the supine recommendation backfire via exhaustion?\n")
    print("Calibrating triple-risk world ...")
    p = calibrated_triple_params()
    prof = Profile.low_risk()

    print("\n--- Three example families (low-risk infant), abstinence framing ---")
    fams = {
        "advantaged, supported": Family(ses=1.5, no_support=0, multiparity=0),
        "average":               Family(ses=0.0, no_support=0, multiparity=0),
        "deprived, solo, twins": Family(ses=-1.5, no_support=1, multiparity=1),
    }
    print(f"{'family':<24}{'P(displace)':>12}{'supine adv':>12}{'prone hist':>12}"
          f"{'+soother':>11}{'net':>11}")
    for name, fam in fams.items():
        o = evaluate_family(p, prof, fam, abstinence=True)
        flag = "  HARMFUL" if o.net_advice_minus_prone > 0 else ""
        print(f"{name:<24}{o.p_displace_supine:>12.2f}"
              f"{_p1000(o.risk_supine_advice):>12}{_p1000(o.risk_prone_historical):>12}"
              f"{_p1000(o.risk_supine_plus_soother):>11}"
              f"{o.net_advice_minus_prone*1000:>+11.3f}{flag}")

    print("\n  (net = risk[supine advice] - risk[uncontrolled prone permitted]; ")
    print("   net > 0 means the back-sleep recommendation INCREASES expected death")
    print("   for that family, because exhaustion-driven displacement outweighs the")
    print("   in-crib protection. '+soother' is back-sleep WITH a SNOO-like device.)")

    print("\n--- Where does supine advice flip to net-harmful? (exhaustion threshold) ---")
    for abst in (True, False):
        r = solve_exhaustion_threshold(p, prof, abstinence=abst)
        framing = "abstinence ('never bed-share')" if abst else "harm-reduction"
        flip = r["ses_at_flip"]
        where = (f"flips at ses = {flip:.2f} (more deprived than this => harmful)"
                 if flip is not None else "never flips across the scanned range")
        print(f"  {framing:<34}: {where}")
        print(f"      net at advantaged end {r['net_at_most_advantaged_per_1000']:+.3f}/1000"
              f"  ->  deprived end {r['net_at_most_deprived_per_1000']:+.3f}/1000")

    print("\n" + "=" * 70)
    print("READING IT: for advantaged/supported families the back-sleep")
    print("recommendation is clearly net-protective. For exhausted, unsupported")
    print("families under abstinence framing it can flip net-harmful -- the")
    print("displacement loop. Harm-reduction framing pushes the flip further out;")
    print("an enforced-supine soother removes it by cutting fragmentation. This is")
    print("the §14 payload: the policy's sign is heterogeneous, and framing + a")
    print("soother are the levers that keep it protective for everyone.")


if __name__ == "__main__":
    main()
