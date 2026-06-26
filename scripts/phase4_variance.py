"""Phase 4: variance decomposition + PCA on the calibrated worlds.

Run:  python scripts/phase4_variance.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402

from sids_sim.calibrate import calibrate, _finalize  # noqa: E402
from sids_sim.scm import Era, SimConfig, World, attach_hazard, simulate_covariates  # noqa: E402
from sids_sim.variance import lmg_table, pca_loadings  # noqa: E402

N = 500_000
OBSERVABLE = ["prone", "smoke", "heavy_smoke", "soft_bedding", "ses"]
FULL = OBSERVABLE + ["vulnerable"]


def calibrate_once(world: World, seed: int = 11):
    """Calibrate the world a single time; return finalized Params (intercepts solved)."""
    res, names = calibrate(world, seed=seed)
    return _finalize(world, names, res.x, n=70_000, seed=seed)


def cohort_from_params(p, world: World, era: Era):
    cov = simulate_covariates(SimConfig(n=N, era=era, world=world, seed=202, params=p))
    return attach_hazard(cov, world, p, np.random.default_rng(303))


def show_lmg(df, label, predictors):
    t = lmg_table(df, "death", predictors)
    print(f"\n  {label}  (total explained R^2 = {t.attrs['total_r2']:.4f})")
    print(f"    {'factor':<14}{'share of explained':>20}")
    for factor, row in t.iterrows():
        bar = "#" * int(round(row.pct_of_explained * 30))
        print(f"    {factor:<14}{row.pct_of_explained:>9.1%}   {bar}")


def show_pca(df, label, predictors):
    evr, load = pca_loadings(df, predictors)
    print(f"\n  PCA loadings -- {label}")
    print(f"    explained var: " + "  ".join(f"PC{i+1} {v:.0%}" for i, v in enumerate(evr)))
    print("    " + load.round(2).to_string().replace("\n", "\n    "))


def main():
    print("Phase 4 -- is prone the principal component of risk?\n")
    print("Using the calibrated TRIPLE-RISK world (H3), pre vs post campaign.")
    print("Calibrating H3 once ...")
    p = calibrate_once(World.TRIPLE)

    for era in (Era.PRE, Era.POST):
        df = cohort_from_params(p, World.TRIPLE, era)
        print(f"\n{'='*68}\nERA: {era.value.upper()}   (deaths = {int(df.death.sum())})\n{'='*68}")

        print("\n[1] OUTCOME-VARIANCE DECOMPOSITION (Shapley / LMG share of death R^2)")
        show_lmg(df, "observable factors only (what studies measure)", OBSERVABLE)
        show_lmg(df, "FULL incl. latent vulnerability", FULL)

        print("\n[2] PCA on the risk-factor matrix (does prone get its own axis?)")
        show_pca(df, "observable factors", OBSERVABLE)

    print("\n" + "=" * 68)
    print("Read: PC1 of the observable factors is the social-adversity bundle;")
    print("watch whether 'prone' loads onto it (esp. post-era) rather than")
    print("standing alone -- and whether vulnerability dominates the FULL R^2.")


if __name__ == "__main__":
    main()
