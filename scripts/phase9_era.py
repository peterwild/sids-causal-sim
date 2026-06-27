"""Phase 9 -- does adding the parallel era trends (smoking down, breastfeeding up)
close the post-campaign death-decline and smoking-PAF gap?

Run:  python scripts/phase9_era.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sids_sim.era import era_report  # noqa: E402
from phase45_linchpin import calibrated_triple_params  # noqa: E402


def main():
    print("Phase 9 -- closing the era-model gap (smoking decline + breastfeeding).\n")
    print("Calibrating base triple-risk world ...")
    base = calibrated_triple_params()
    print("Solving era overlay + re-leveling PRE to 1.2 ...\n")
    r = era_report(base)
    b, e, t = r["base"], r["enriched"], r["targets"]

    print(f"  (POST smoking prevalence driven to {e['post_smoke_prev']:.2f} via "
          f"smoke_post_shift={e['smoke_post_shift']:.2f})\n")
    print(f"{'metric':<22}{'target':>9}{'base model':>12}{'era-enriched':>14}")
    print("-" * 57)
    print(f"{'PRE death /1000':<22}{t['pre_rate']:>9.2f}{b['pre_rate']:>12.2f}{e['pre_rate']:>14.2f}")
    print(f"{'POST death /1000':<22}{t['post_rate']:>9.2f}{b['post_rate']:>12.2f}{e['post_rate']:>14.2f}")
    print(f"{'PRE smoking PAF':<22}{t['pre_paf']:>9.2f}{b['pre_paf']:>12.2f}{e['pre_paf']:>14.2f}")
    print(f"{'POST smoking PAF':<22}{t['post_paf']:>9.2f}{b['post_paf']:>12.2f}{e['post_paf']:>14.2f}")

    drop_base = b["pre_rate"] - b["post_rate"]
    drop_enr = e["pre_rate"] - e["post_rate"]
    print(f"\n  post-era death DROP: target {t['pre_rate']-t['post_rate']:.2f}, "
          f"base {drop_base:.2f}, enriched {drop_enr:.2f} (per 1000)")
    paf_rise_base = b["post_paf"] - b["pre_paf"]
    paf_rise_enr = e["post_paf"] - e["pre_paf"]
    print(f"  smoking-PAF RISE   : target +{t['post_paf']-t['pre_paf']:.2f}, "
          f"base {paf_rise_base:+.2f}, enriched {paf_rise_enr:+.2f}")

    print("\n" + "=" * 70)
    print("READING IT (honest, split verdict):")
    print("  * DEATH-RATE gap: largely CLOSES. Adding breastfeeding + smoking")
    print("    decline pulls POST from ~0.91 toward 0.4 (most of the excess gone).")
    print("    So that gap was a missing-mechanism artifact -- the era switch had")
    print("    only been moving prone+bedding.")
    print("  * SMOKING-PAF RISE: does NOT reproduce. It stays ~flat (even falls if")
    print("    smoking declines). The historical 50->80% rise needs the *remaining*")
    print("    post-era deaths to concentrate in smokers far harder than this DGP")
    print("    allows (e.g. smoking x vulnerability interaction, or prone-removal")
    print("    sparing mostly non-smoking infants). A real, narrower open gap.")
    print("  * Neither bears on the causal verdict, which is era-internal (the OR")
    print("    discriminator), not a function of absolute death levels.")


if __name__ == "__main__":
    main()
