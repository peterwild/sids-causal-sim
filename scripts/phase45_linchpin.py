"""Phase 4.5 -- the linchpin challenge-toggle experiment (DESIGN.md sections 11,17,18).

Takes the calibrated triple-risk world (the best-supported mechanism from Phase 2)
and decomposes its single prone effect into mechanism channels, then asks: for a
LOW-RISK infant, how much of prone's excess absolute risk survives a fully
engineered home environment (breathable surface + cool room)? Reports a band across
three functional forms and a "form E-value".

Run:  python scripts/phase45_linchpin.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.calibrate import _finalize, calibrate  # noqa: E402
from sids_sim.mediation import Profile, run_linchpin  # noqa: E402
from sids_sim.scm import Params, World  # noqa: E402


def calibrated_triple_params(seed: int = 11, n: int = 70_000) -> Params:
    """Phase-2 calibrated triple-world params (prone + hazard intercepts solved)."""
    res, names = calibrate(World.TRIPLE, seed=seed)
    return _finalize(World.TRIPLE, names, res.x, n=n, seed=seed)


def _fmt(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def main():
    print("Phase 4.5 -- linchpin: does the arousal deficit kill without a challenge?\n")
    print("Calibrating triple-risk world (this takes a moment) ...")
    p = calibrated_triple_params()
    print(f"  calibrated w_prone (total prone log-odds effect) = {p.w_prone:.3f}")
    print(f"  => historical prone OR ~ exp(w_prone) = {pow(2.718281828, p.w_prone):.2f}")
    print(f"  hazard_intercept={p.hazard_intercept:.2f}  "
          f"triple_vuln_bonus={p.triple_vuln_bonus:.2f}  p_vuln={p.p_vulnerable:.2f}")

    prof = Profile.low_risk()
    print(f"\nProfile (low-risk): non-smoking, firm/bare crib, advantaged "
          f"(ses=+{prof.ses:.0f}).")
    print("Excess ABSOLUTE risk = P(death|prone) - P(death|supine), per 1000, "
          "marginal over the\nunknown vulnerability phenotype.\n")

    res = run_linchpin(p, prof)

    print(f"{'form':<12}{'unaccust. OR':>13}{'hist excess':>13}"
          f"{'eng excess':>12}{'removable':>11}")
    print(f"{'':12}{'(target ~19)':>13}{'/1000':>13}{'/1000':>12}{'frac':>11}")
    print("-" * 61)
    for name, f in res["forms"].items():
        print(f"{name:<12}{f['unaccustomed_or_check']:>13.1f}"
              f"{f['excess_historical_per_1000']:>13.3f}"
              f"{f['excess_engineered_per_1000']:>12.3f}"
              f"{f['removable_fraction']:>11.0%}")

    print("\nApportionment of the calibrated prone effect (log-odds units):")
    print(f"{'form':<12}{'rebr':>7}{'therm':>7}{'obstr':>7}{'arousal':>8}{'endo':>7}")
    for name, f in res["forms"].items():
        a = f["apportionment"]
        print(f"{name:<12}{a.b_rebr:>7.2f}{a.b_therm:>7.2f}{a.b_obstr:>7.2f}"
              f"{a.lambda_ar:>8.2f}{a.b_endo:>7.2f}")

    print("\nForm E-value -- free-standing arousal share needed to push the")
    print("ENGINEERED-prone excess risk above each decision threshold:")
    for key, ev in res["form_evalues"].items():
        thr = ev["threshold_per_1000"]
        req = ev["required_arousal_share"]
        print(f"  threshold {thr}/1000:")
        print(f"    engineered excess at lambda=0 (Horne anchor): "
              f"{ev['residual_at_zero_lambda_per_1000']:.3f}/1000")
        if req is None:
            print(f"    required arousal share to cross: UNREACHABLE even at max "
                  f"(eng excess maxes at {ev['residual_at_max_lambda_per_1000']:.3f}/1000)")
        else:
            print(f"    required arousal share to cross: {req:.0%} of the total "
                  f"prone effect")
            print(f"      (Horne 2001 anchors this at ~0%; a large required share "
                  f"=> conclusion robust)")

    print("\n" + "=" * 70)
    print("READING IT: under the gated form G (Horne-anchored, lambda~0), most of")
    print("prone's risk is engineerable; the residual is obstruction + endogenous")
    print("autonomic events in vulnerable infants -- who cannot be identified in")
    print("advance. Whether that residual sits below your decision threshold is the")
    print("whole question, and it is now a NUMBER, not an odds ratio.")


if __name__ == "__main__":
    main()
