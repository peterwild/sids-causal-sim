"""Phase 9 -- closing the era-model gap (DESIGN.md section 5, FINDINGS limitations).

Earlier phases changed only prone + bedding across the Back-to-Sleep era, so no
world reproduced the FULL post-campaign death decline (1.2 -> 0.4) or smoking's
rising attributable share (50% -> 80%). The real era also rode TWO parallel public-
health trends: maternal smoking fell, and breastfeeding rose (protective). This
module turns those on (via the additive, default-off SCM knobs added in scm.py),
re-levels the PRE hazard so the pre-era rate stays 1.2, and measures how much of the
gap closes.

The verdict (prone is causal) does NOT depend on this -- it rests on the OR
discriminator, which is era-internal. This phase only tests whether the documented
DEATH-RATE / PAF gap was a missing-era-mechanism artifact rather than a model flaw.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from .scm import (Era, Params, SimConfig, World, _sigmoid, pdeath,
                  simulate_covariates)

_W = World.TRIPLE
_N = 150_000
_SEED = 11


def _cov(p: Params, era: Era, n: int = _N):
    return simulate_covariates(SimConfig(n=n, era=era, world=_W, seed=_SEED, params=p))


def _expected_rate(p: Params, cov) -> float:
    pr = pdeath(_W, p, vulnerable=cov.vulnerable.to_numpy(), smoke=cov.smoke.to_numpy(),
                heavy_smoke=cov.heavy_smoke.to_numpy(), soft_bedding=cov.soft_bedding.to_numpy(),
                prone=cov.prone.to_numpy(), ses=cov.ses.to_numpy(),
                breastfeeding=cov.breastfeeding.to_numpy())
    return float(1000.0 * pr.mean())


def _paf_smoking(p: Params, cov) -> float:
    common = dict(vulnerable=cov.vulnerable.to_numpy(), soft_bedding=cov.soft_bedding.to_numpy(),
                  prone=cov.prone.to_numpy(), ses=cov.ses.to_numpy(),
                  breastfeeding=cov.breastfeeding.to_numpy())
    actual = pdeath(_W, p, smoke=cov.smoke.to_numpy(), heavy_smoke=cov.heavy_smoke.to_numpy(), **common)
    nosmoke = pdeath(_W, p, smoke=np.zeros(len(cov)), heavy_smoke=np.zeros(len(cov)), **common)
    return float(1.0 - nosmoke.sum() / actual.sum())


def solve_hazard_intercept_bf(p: Params, cov, target_rate: float = 1.2) -> float:
    """Bisect the hazard intercept so the PRE expected rate hits target, WITH
    breastfeeding active (which otherwise lowers the pre-era rate)."""
    lo, hi = -22.0, 2.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        rate = _expected_rate(replace(p, hazard_intercept=mid), cov)
        if rate < target_rate:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def solve_smoke_post_shift(p: Params, target_prev: float = 0.23, n: int = _N) -> float:
    """Bisect the POST smoking-intercept shift to hit a target POST prevalence."""
    cov = _cov(p, Era.POST, n)
    ses = cov.ses.to_numpy()
    lo, hi = -5.0, 2.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        prev = _sigmoid(p.smoke_intercept + p.smoke_ses_slope * ses + mid).mean()
        if prev > target_prev:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def make_era_params(base: Params, *, smoke_post_shift: float,
                    bf_intercept: float = 0.0, bf_ses_slope: float = 0.3,
                    bf_post_shift: float = 0.95, w_bf: float = 0.51,
                    n: int = _N) -> Params:
    """Base triple params + era overlay, re-leveled so PRE rate stays 1.2."""
    p = replace(base, smoke_post_shift=smoke_post_shift, bf_intercept=bf_intercept,
                bf_ses_slope=bf_ses_slope, bf_post_shift=bf_post_shift, w_bf=w_bf)
    p = replace(p, hazard_intercept=solve_hazard_intercept_bf(p, _cov(p, Era.PRE, n)))
    return p


def era_report(base: Params, n: int = _N) -> dict:
    """Compare death rate + smoking PAF across eras, base model vs era-enriched."""
    # base (overlay off): re-level too, so the only change is the overlay itself
    base_pre, base_post = _cov(base, Era.PRE, n), _cov(base, Era.POST, n)
    base_out = {
        "pre_rate": _expected_rate(base, base_pre),
        "post_rate": _expected_rate(base, base_post),
        "pre_paf": _paf_smoking(base, base_pre),
        "post_paf": _paf_smoking(base, base_post),
    }

    shift = solve_smoke_post_shift(base, n=n)
    p = make_era_params(base, smoke_post_shift=shift, n=n)
    pre, post = _cov(p, Era.PRE, n), _cov(p, Era.POST, n)
    enriched = {
        "smoke_post_shift": shift,
        "post_smoke_prev": float(p_post_smoke := _sigmoid(
            p.smoke_intercept + p.smoke_ses_slope * post.ses.to_numpy() + p.smoke_post_shift).mean()),
        "pre_rate": _expected_rate(p, pre),
        "post_rate": _expected_rate(p, post),
        "pre_paf": _paf_smoking(p, pre),
        "post_paf": _paf_smoking(p, post),
    }
    return {"base": base_out, "enriched": enriched,
            "targets": {"pre_rate": 1.2, "post_rate": 0.4, "pre_paf": 0.50, "post_paf": 0.80}}
