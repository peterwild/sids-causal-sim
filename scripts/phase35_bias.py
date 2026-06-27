"""Phase 3.5 -- how much of the historical prone OR is a study artifact?

Plants the calibrated causal effect, then runs the flawed retrospective design on
top (recall + control-selection bias) and compares to the true do-effect.

Run:  python scripts/phase35_bias.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sids_sim.bias import bias_decomposition  # noqa: E402
from sids_sim.scm import Era, World  # noqa: E402
from phase45_linchpin import calibrated_triple_params  # noqa: E402


def main():
    print("Phase 3.5 -- biased case-control replication (study-artifact accounting).\n")
    print("Calibrating triple-risk world ...")
    p = calibrated_triple_params()

    for era in (Era.PRE, Era.POST):
        d = bias_decomposition(World.TRIPLE, p, era=era)
        print(f"\n=== {era.value.upper()} era ===")
        print(f"  TRUE do-effect OR (planted)      : {d['true_do_or']:.2f}")
        print(f"  clean design (no bias)           : {d['clean_design_or']:.2f}")
        print(f"  + recall bias only               : {d['recall_only_or']:.2f}")
        print(f"  + control-selection bias only    : {d['selection_only_or']:.2f}")
        print(f"  + BOTH biases (what a study sees): {d['both_biases_or']:.2f}")
        print(f"  inflation factor (reported/true) : {d['inflation_factor']:.2f}x")

    print("\n" + "=" * 70)
    print("READING IT: the clean design recovers ~the true do-effect; recall +")
    print("selection bias INFLATE the reported OR above the truth. So the famous")
    print("historical ORs are partly artifact -- but the effect does NOT vanish")
    print("when bias is removed (the do-effect stays well above 1). Pete's")
    print("skepticism about the studies is justified in DEGREE, not in kind: the")
    print("number is inflated, the cause is still real.")


if __name__ == "__main__":
    main()
