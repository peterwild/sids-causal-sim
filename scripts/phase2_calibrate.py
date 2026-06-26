"""Phase 2: staged calibration of all three worlds; report achieved-vs-target.

Run:  python scripts/phase2_calibrate.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.calibrate import calibrate, loss_terms  # noqa: E402
from sids_sim.scm import World  # noqa: E402

N_FINAL = 500_000


def report(world: World):
    t0 = time.time()
    res, names = calibrate(world)
    terms, p = loss_terms(world, names, res.x, n=N_FINAL, seed=101)  # fresh seed
    total = sum(v[2] for v in terms.values())

    print(f"\n{'='*72}\n{world.value}   (final loss {total:.4f}, {time.time()-t0:.0f}s)\n{'='*72}")
    print(f"{'metric':<24}{'era':<6}{'target':>9}{'achieved':>11}   flag")
    for (metric, era), (ach, tgt, _) in terms.items():
        rel = abs(ach - tgt) / max(abs(tgt), 1e-9)
        flag = "OK" if rel < 0.15 else ("MISS" if rel < 0.4 else "FAIL")
        print(f"{metric:<24}{era:<6}{tgt:>9.3f}{ach:>11.3f}   {flag}")
    print("  key fitted params:")
    for nm in ["w_prone", "w_smoke", "w_bedding", "w_ses",
               "prone_pre_ses_slope", "prone_post_ses_slope",
               "w_vuln", "triple_vuln_bonus", "triple_nonvuln_floor",
               "hazard_intercept"]:
        if hasattr(p, nm):
            print(f"    {nm:<24}{getattr(p, nm):+.3f}")
    return world.value, total


def main():
    print("Staged calibration -> three worlds vs six historical targets (both eras).")
    print("Watch H2_marker's adjusted_prone_or: can confounding alone fake it?\n")
    results = [report(w) for w in (World.CAUSAL, World.TRIPLE, World.MARKER)]
    print(f"\n{'='*72}\nSUMMARY (lower loss = better fit to history)\n{'='*72}")
    for name, total in sorted(results, key=lambda r: r[1]):
        print(f"  {name:<14}{total:.4f}")


if __name__ == "__main__":
    main()
