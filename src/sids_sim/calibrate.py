"""Phase 2 calibration (staged).

The blind 10-D optimizer of the first attempt failed to converge (death rates
landed 15-20x too high). The fix is to pin the targets that map cleanly onto a
single knob, leaving the optimizer only the genuinely-coupled handful:

  * Prone prevalence  -> solved analytically from the prone-choice equation
                         (survivors ~= whole population, since deaths are rare).
  * Pre-era death rate -> the hazard intercept is a pure level dial; solved by
                         bisection on fixed covariates so it ALWAYS hits 1.2/1000.
                         Whether the POST rate then falls to 0.4 is left as a real
                         test (does removing prone+bedding produce the 3x drop?).
  * Everything else (effect sizes, prone<->SES coupling, vulnerability
                     enrichment) -> optimized on the now well-behaved surface.

The marker world (H2) keeps w_prone == 0 but is free to crank w_ses and the
prone<->SES slopes -- its fair shot at faking the odds ratio through confounding.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
from scipy.optimize import minimize

from .metrics import cohort_metrics
from .scm import (Era, Params, SimConfig, World, attach_hazard, pdeath,
                  simulate_covariates)

# fixed standard-normal sample for deterministic prevalence/intercept solves
_Z = np.random.default_rng(0).standard_normal(40_000)


TARGETS = {
    "death_rate_per_1000": {"pre": 1.2, "post": 0.4, "scale": "log", "w": 1.5},
    "prone_prev_controls": {"pre": 0.50, "post": 0.246, "scale": "lin", "w": 1.0},
    "prone_prev_cases": {"pre": 0.84, "post": 0.485, "scale": "lin", "w": 1.0},
    "adjusted_prone_or": {"pre": 2.86, "post": 3.93, "scale": "log", "w": 1.5},
    "smoking_paf": {"pre": 0.50, "post": 0.80, "scale": "lin", "w": 1.0},
    "vuln_prev_cases": {"both": 0.83, "scale": "lin", "w": 1.0},
    "vuln_prev_controls": {"both": 0.37, "scale": "lin", "w": 0.5},
}


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _prevalence(a, b):
    return float(np.mean(_sigmoid(a + b * _Z)))


def solve_prone_intercept(target_prev: float, slope: float) -> float:
    """1-D bisection for the prone-choice intercept hitting target prevalence."""
    lo, hi = -10.0, 10.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _prevalence(mid, slope) < target_prev:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def solve_hazard_intercept(world: World, params: Params, cov_pre,
                           target_rate_per_1000: float = 1.2) -> float:
    """Bisection on the hazard intercept so the PRE-era expected death rate hits
    the target. Uses expected probabilities on fixed covariates (no resampling).
    """
    kw = dict(
        vulnerable=cov_pre.vulnerable.to_numpy(), smoke=cov_pre.smoke.to_numpy(),
        heavy_smoke=cov_pre.heavy_smoke.to_numpy(),
        soft_bedding=cov_pre.soft_bedding.to_numpy(),
        prone=cov_pre.prone.to_numpy(), ses=cov_pre.ses.to_numpy(),
    )
    lo, hi = -22.0, 2.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        rate = 1000.0 * pdeath(world, replace(params, hazard_intercept=mid), **kw).mean()
        if rate < target_rate_per_1000:
            lo = mid       # higher intercept -> higher rate
        else:
            hi = mid
    return 0.5 * (lo + hi)


def free_spec(world: World):
    """(names, x0, bounds) for the optimized params. Prone INTERCEPTS and the
    hazard intercept are NOT here -- they are solved analytically each eval.
    """
    common = [
        ("w_smoke", 1.0, (0.0, 2.5)),
        ("w_bedding", 0.7, (0.0, 2.5)),
        ("w_ses", 0.3, (0.0, 2.5)),
        ("prone_pre_ses_slope", -0.2, (-3.0, 0.4)),
        ("prone_post_ses_slope", -1.2, (-3.0, 0.2)),
    ]
    if world is World.CAUSAL:
        extra = [("w_prone", 1.1, (0.0, 3.0)), ("w_vuln", 1.4, (0.0, 4.0))]
    elif world is World.MARKER:
        extra = [("w_vuln", 1.4, (0.0, 4.0))]   # no w_prone -> stays 0
    else:  # TRIPLE
        extra = [
            ("w_prone", 1.1, (0.0, 3.0)),
            ("triple_vuln_bonus", 2.5, (0.0, 6.0)),
            ("triple_nonvuln_floor", -11.0, (-16.0, -6.0)),
        ]
    names = [c[0] for c in common + extra]
    x0 = np.array([c[1] for c in common + extra], float)
    bounds = [c[2] for c in common + extra]
    return names, x0, bounds


def build_params(world: World, names, x) -> Params:
    """Assemble Params: set free values, then solve the prone intercepts so the
    prevalence targets are hit exactly for the given slopes.
    """
    p = Params(p_vulnerable=0.37, w_prone=0.0)
    p = replace(p, **{n: float(v) for n, v in zip(names, x)})
    p = replace(
        p,
        prone_pre_intercept=solve_prone_intercept(0.50, p.prone_pre_ses_slope),
        prone_post_intercept=solve_prone_intercept(0.246, p.prone_post_ses_slope),
    )
    return p


def _finalize(world: World, names, x, n: int, seed: int) -> Params:
    """Params with prone intercepts AND hazard intercept solved."""
    p = build_params(world, names, x)
    cov_pre = simulate_covariates(SimConfig(n=n, era=Era.PRE, world=world,
                                            seed=seed, params=p))
    return replace(p, hazard_intercept=solve_hazard_intercept(world, p, cov_pre))


def loss_terms(world: World, names, x, n: int, seed: int):
    p = _finalize(world, names, x, n, seed)
    terms = {}
    for era in (Era.PRE, Era.POST):
        cov = simulate_covariates(SimConfig(n=n, era=era, world=world, seed=seed, params=p))
        rng = np.random.default_rng(seed + 999)
        df = attach_hazard(cov, world, p, rng)
        m = cohort_metrics(df, world, p, seed=seed)
        for metric, spec in TARGETS.items():
            tgt = spec.get(era.value, spec.get("both"))
            ach = m[metric]
            err = (np.log(max(ach, 1e-6)) - np.log(tgt)) if spec["scale"] == "log" else (ach - tgt)
            terms[(metric, era.value)] = (ach, tgt, spec["w"] * err**2)
    return terms, p


def loss(world, names, x, n, seed) -> float:
    terms, _ = loss_terms(world, names, x, n, seed)
    return float(sum(v[2] for v in terms.values()))


def calibrate(world: World, n_opt: int = 70_000, seed: int = 11, maxiter: int = 600):
    names, x0, bounds = free_spec(world)
    res = minimize(
        lambda x: loss(world, names, x, n_opt, seed),
        x0, method="Nelder-Mead", bounds=bounds,
        options={"maxiter": maxiter, "fatol": 1e-4, "xatol": 1e-3},
    )
    return res, names
