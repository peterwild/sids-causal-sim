"""Phase 3 sensitivity analysis: how strong must the HIDDEN vulnerability->prone
channel be for a marker world (no real prone effect) to fake the historical
adjusted odds ratio?

We take the calibrated MARKER world (w_prone == 0), then crank a single hidden
knob -- gamma_vuln_prone, the degree to which vulnerable infants are
preferentially placed prone -- holding prone prevalence and the pre-era death
rate fixed. We read off the adjusted prone OR as gamma grows, and solve for the
gamma* that reproduces the historical OR. Then we translate gamma* into a plain
statement ('vulnerable babies placed prone X-fold more often') and compare it to
the analytic VanderWeele-Ding E-value and to the strength of known risk factors.

If gamma* implies an implausibly strong hidden association, the 'it's only
correlation' explanation is rejected.
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from .calibrate import _Z, calibrate, build_params, solve_hazard_intercept
from .metrics import adjusted_prone_or
from .scm import (Era, Params, SimConfig, World, attach_hazard,
                  simulate_covariates)


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def solve_prone_intercept_vuln(target_prev: float, slope: float, gamma: float,
                               p_vuln: float) -> float:
    """Prone-choice intercept hitting target population prevalence when a hidden
    vulnerability bump (gamma) is present. Prevalence is the vuln mixture.
    """
    def prev(a):
        non = np.mean(_sigmoid(a + slope * _Z))
        vul = np.mean(_sigmoid(a + slope * _Z + gamma))
        return (1 - p_vuln) * non + p_vuln * vul

    lo, hi = -12.0, 12.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if prev(mid) < target_prev:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def analytic_evalue(rr: float) -> float:
    """VanderWeele-Ding E-value: the minimum strength (as a risk ratio on BOTH
    legs) an unmeasured confounder must have to explain away an observed RR.
    """
    return rr + np.sqrt(rr * (rr - 1.0))


def marker_with_gamma(base: Params, gamma: float) -> Params:
    """Marker-world params with the hidden channel set to gamma, prone intercepts
    re-solved to hold prevalence (pre 0.50, post 0.246).
    """
    p = replace(base, w_prone=0.0, gamma_vuln_prone=gamma)
    p = replace(
        p,
        prone_pre_intercept=solve_prone_intercept_vuln(0.50, p.prone_pre_ses_slope, gamma, p.p_vulnerable),
        prone_post_intercept=solve_prone_intercept_vuln(0.246, p.prone_post_ses_slope, gamma, p.p_vulnerable),
    )
    return p


def marker_metrics_at_gamma(base: Params, gamma: float, era: Era,
                            n: int = 300_000, seed: int = 101) -> dict:
    """Adjusted prone OR (and the two confounding 'legs') for the marker world at
    a given hidden-channel strength, holding pre death rate at 1.2/1000.
    """
    p = marker_with_gamma(base, gamma)
    cov_pre = simulate_covariates(SimConfig(n=n, era=Era.PRE, world=World.MARKER, seed=seed, params=p))
    p = replace(p, hazard_intercept=solve_hazard_intercept(World.MARKER, p, cov_pre))

    cov = simulate_covariates(SimConfig(n=n, era=era, world=World.MARKER, seed=seed, params=p))
    df = attach_hazard(cov, World.MARKER, p, np.random.default_rng(seed + 7))

    # the two legs of the hidden confounding triangle, as crude ORs
    leg_v_prone = _crude_or(df, "vulnerable", "prone")     # V <-> prone
    leg_v_death = _crude_or(df, "vulnerable", "death")     # V <-> death
    return {
        "gamma": gamma,
        "prone_in_vuln": float(df.loc[df.vulnerable == 1, "prone"].mean()),
        "prone_in_nonvuln": float(df.loc[df.vulnerable == 0, "prone"].mean()),
        "adjusted_prone_or": adjusted_prone_or(df, seed=seed),
        "leg_V_to_prone_or": leg_v_prone,
        "leg_V_to_death_or": leg_v_death,
    }


def _crude_or(df, a, b) -> float:
    x, y = df[a].to_numpy(), df[b].to_numpy()
    n11 = ((x == 1) & (y == 1)).sum() + 0.5
    n10 = ((x == 1) & (y == 0)).sum() + 0.5
    n01 = ((x == 0) & (y == 1)).sum() + 0.5
    n00 = ((x == 0) & (y == 0)).sum() + 0.5
    return float((n11 * n00) / (n10 * n01))


def solve_gamma_for_or(base: Params, target_or: float, era: Era,
                       n: int = 300_000, seed: int = 101) -> float | None:
    """Bisection for the hidden-channel strength gamma that makes the marker
    world's adjusted prone OR reach target_or. Returns None if unreachable in
    the searched range (gamma up to 6).
    """
    lo, hi = 0.0, 6.0
    or_hi = marker_metrics_at_gamma(base, hi, era, n, seed)["adjusted_prone_or"]
    if or_hi < target_or:
        return None
    for _ in range(28):
        mid = 0.5 * (lo + hi)
        cur = marker_metrics_at_gamma(base, mid, era, n, seed)["adjusted_prone_or"]
        if cur < target_or:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def calibrated_marker_base(seed: int = 11) -> Params:
    """Return the Phase-2 calibrated marker-world params (gamma still 0)."""
    res, names = calibrate(World.MARKER, seed=seed)
    return build_params(World.MARKER, names, res.x)
