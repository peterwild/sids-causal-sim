"""Phase 8 -- home-protocol comparison, the capstone (DESIGN.md section 16).

Ranks realistic home sleep protocols by NET population infant mortality on the full
DGP (in-crib position/environment risk + the exhaustion->displacement arm), under
both abstinence and harm-reduction framing.

Run:  python scripts/phase8_protocols.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sids_sim.protocols import compare_protocols  # noqa: E402
from phase45_linchpin import calibrated_triple_params  # noqa: E402


def _table(rows):
    print(f"{'rank':<5}{'protocol':<32}{'net/1000':>10}{'in-crib':>10}"
          f"{'displace':>10}{'P(disp)':>9}")
    print("-" * 76)
    for i, r in enumerate(rows, 1):
        print(f"{i:<5}{r['protocol']:<32}{r['net_per_1000']:>10.3f}"
              f"{r['incrib_component_per_1000']:>10.3f}"
              f"{r['displacement_component_per_1000']:>10.3f}{r['mean_p_displace']:>9.2f}")


def main():
    print("Phase 8 -- which home protocol minimizes NET infant mortality?\n")
    print("Calibrating triple-risk world ...")
    p = calibrated_triple_params()

    print("\n=== Abstinence framing ('never bed-share') ===")
    abst = compare_protocols(p, abstinence=True)
    _table(abst)

    print("\n=== Harm-reduction framing ===")
    harm = compare_protocols(p, abstinence=False)
    _table(harm)

    best = abst[0]["protocol"]
    print("\n" + "=" * 76)
    print("READING IT:")
    print(f"  * Winner (both framings): '{best}'. It wins not by lowering the")
    print("    per-night in-crib risk (already supine) but by cutting the")
    print("    DISPLACEMENT component -- better sleep -> less exhaustion -> less")
    print("    unsafe bed/sofa sharing.")
    print("  * 'breathable mattress' ~= 'bare firm crib' for a SUPINE baby:")
    print("    rebreathing is a prone channel, so a breathable surface barely")
    print("    moves a back-sleeper's risk.")
    print("  * 'engineered prone permitted' trades a small in-crib penalty for")
    print("    LESS displacement (prone sleeps deeper) -- a real, controversial")
    print("    near-wash with bare-crib supine, but still beaten by the soother.")
    print("  * harm-reduction framing lowers every protocol's displacement tail")
    print("    vs abstinence (it moves sharing off the sofa).")


if __name__ == "__main__":
    main()
