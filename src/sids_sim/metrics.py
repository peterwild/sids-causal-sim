"""Metrics that turn a simulated cohort into the quantities the historical
literature reported -- so we can compare like-for-like against the calibration
targets in data/calibration/targets.json.

Two that matter most:

* adjusted_prone_or -- the odds ratio for prone AFTER adjusting for the
  confounders an epidemiologist could actually measure (smoking, bedding, SES).
  Crucially it does NOT adjust for the latent vulnerability, exactly like the
  real studies, so any residual confounding through vulnerability stays baked in.

* smoking_paf -- the population attributable fraction for smoking, computed by
  the cleanest possible counterfactual: re-evaluate every infant's death hazard
  with smoking switched off and ask what share of deaths disappears.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .scm import Params, World, pdeath


# --------------------------------------------------------------------------- #
# transparent logistic regression (IRLS / Newton-Raphson) -- no black box
# --------------------------------------------------------------------------- #
def logistic_irls(X: np.ndarray, y: np.ndarray, max_iter: int = 50,
                  tol: float = 1e-8, ridge: float = 1e-6):
    """Maximum-likelihood logistic regression coefficients via IRLS.

    X already includes an intercept column. Tiny ridge keeps it stable under
    near-separation. Returns the coefficient vector.
    """
    n, k = X.shape
    beta = np.zeros(k)
    R = ridge * np.eye(k)
    for _ in range(max_iter):
        eta = X @ beta
        mu = 1.0 / (1.0 + np.exp(-eta))
        w = np.clip(mu * (1.0 - mu), 1e-9, None)
        # Newton step: beta += (X'WX + R)^-1 X'(y - mu)
        XtW = X.T * w
        H = XtW @ X + R
        grad = X.T @ (y - mu) - R @ beta
        step = np.linalg.solve(H, grad)
        beta = beta + step
        if np.max(np.abs(step)) < tol:
            break
    return beta


def _case_control_sample(df: pd.DataFrame, controls_per_case: int, rng):
    cases = df[df.death == 1]
    controls = df[df.death == 0]
    n_ctrl = min(len(controls), controls_per_case * len(cases))
    ctrl = controls.sample(n=n_ctrl, random_state=int(rng.integers(1 << 31)))
    return pd.concat([cases, ctrl], ignore_index=True)


def adjusted_prone_or(df: pd.DataFrame, controls_per_case: int = 5,
                      seed: int = 0) -> float:
    """Adjusted OR for prone from a case-control sample, controlling for the
    OBSERVED confounders (smoke, heavy_smoke, soft_bedding, ses). Vulnerability
    is deliberately excluded -- it is latent in the real world.
    """
    rng = np.random.default_rng(seed)
    sample = _case_control_sample(df, controls_per_case, rng)
    cols = ["prone", "smoke", "heavy_smoke", "soft_bedding", "ses"]
    X = np.column_stack([np.ones(len(sample))] + [sample[c].to_numpy(float) for c in cols])
    y = sample["death"].to_numpy(float)
    beta = logistic_irls(X, y)
    # index 1 is prone (0 is intercept)
    return float(np.exp(beta[1]))


def smoking_adjusted_ors(df: pd.DataFrame, controls_per_case: int = 5,
                         seed: int = 0) -> dict:
    """Adjusted ORs for smoking from the same case-control logistic used for prone.

    Returns the light-smoker OR (any smoking vs none) and the heavy-smoker OR
    (>20/day, which carries the extra heavy term on top of the base). Lets the
    discrimination report check the dose-response target (~2 -> ~12.7).
    """
    rng = np.random.default_rng(seed)
    sample = _case_control_sample(df, controls_per_case, rng)
    cols = ["prone", "smoke", "heavy_smoke", "soft_bedding", "ses"]
    X = np.column_stack([np.ones(len(sample))] + [sample[c].to_numpy(float) for c in cols])
    y = sample["death"].to_numpy(float)
    beta = logistic_irls(X, y)
    # column order: [intercept, prone, smoke, heavy_smoke, soft_bedding, ses]
    return {"base": float(np.exp(beta[2])), "heavy": float(np.exp(beta[2] + beta[3]))}


def crude_prone_or(df: pd.DataFrame) -> float:
    cases, controls = df[df.death == 1], df[df.death == 0]
    a = (cases.prone == 1).sum() + 0.5
    b = (cases.prone == 0).sum() + 0.5
    c = (controls.prone == 1).sum() + 0.5
    d = (controls.prone == 0).sum() + 0.5
    return float((a / b) / (c / d))


def smoking_paf(df: pd.DataFrame, world: World, params: Params) -> float:
    """Population attributable fraction for smoking via counterfactual hazard.

    PAF = 1 - E[hazard | nobody smokes] / E[hazard | actual]. Uses expected
    probabilities (not Bernoulli draws) for low variance.
    """
    common = dict(
        vulnerable=df.vulnerable.to_numpy(),
        soft_bedding=df.soft_bedding.to_numpy(),
        prone=df.prone.to_numpy(),
        ses=df.ses.to_numpy(),
    )
    actual = pdeath(world, params, smoke=df.smoke.to_numpy(),
                    heavy_smoke=df.heavy_smoke.to_numpy(), **common)
    no_smoke = pdeath(world, params, smoke=np.zeros(len(df)),
                      heavy_smoke=np.zeros(len(df)), **common)
    return float(1.0 - no_smoke.sum() / actual.sum())


def cohort_metrics(df: pd.DataFrame, world: World, params: Params,
                   seed: int = 0) -> dict:
    """Full vector of metrics for one cohort (one world, one era)."""
    n = len(df)
    deaths = int(df.death.sum())
    return {
        "death_rate_per_1000": 1000 * deaths / n,
        "prone_prev_cases": float(df.loc[df.death == 1, "prone"].mean()) if deaths else np.nan,
        "prone_prev_controls": float(df.loc[df.death == 0, "prone"].mean()),
        "adjusted_prone_or": adjusted_prone_or(df, seed=seed),
        "smoking_paf": smoking_paf(df, world, params),
        "vuln_prev_cases": float(df.loc[df.death == 1, "vulnerable"].mean()) if deaths else np.nan,
        "vuln_prev_controls": float(df.loc[df.death == 0, "vulnerable"].mean()),
        "n_deaths": deaths,
    }
