"""Phase 6 -- continuous mixing-weight fit (DESIGN.md section 2, deferred phase).

The discrete three-worlds setup answers "marker or causal?" as a yes/no. This
phase makes it continuous: define the direct-causal FRACTION

    lambda = w_prone / w_prone_full        (0 = pure marker, 1 = full causal)

and profile the calibration loss over lambda -- at each fixed lambda we re-optimize
ALL the other free parameters (confounding slopes, smoking/bedding/SES weights,
vulnerability) to give the marker side every chance. The loss curve then bounds how
much of prone's effect MUST be direct-causal to reproduce history: where the curve
turns sharply up toward lambda=0 is the data refusing the marker explanation.

This is the continuous analog of the Phase-3 E-value: instead of "a hidden
confounder would need strength E," it answers "the direct-causal share must be at
least ~X% or the fit falls apart."
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from .calibrate import build_params, calibrate, free_spec, loss
from .scm import World


def w_prone_full(seed: int = 11) -> float:
    """The unconstrained calibrated causal w_prone (lambda = 1 reference)."""
    res, names = calibrate(World.CAUSAL, seed=seed)
    return float(build_params(World.CAUSAL, names, res.x).w_prone)


def loss_at_fixed_wprone(V: float, *, n: int = 45_000, seed: int = 11,
                         maxiter: int = 250) -> float:
    """Best achievable calibration loss with w_prone pinned at V, re-optimizing all
    other free CAUSAL parameters.
    """
    names, x0, bounds = free_spec(World.CAUSAL)
    k = names.index("w_prone")
    free = [i for i in range(len(names)) if i != k]
    x0 = np.asarray(x0, float)

    def obj(xr):
        x = x0.copy()
        x[free] = xr
        x[k] = V
        return loss(World.CAUSAL, names, x, n, seed)

    res = minimize(obj, x0[free], method="Nelder-Mead",
                   bounds=[bounds[i] for i in free],
                   options={"maxiter": maxiter, "fatol": 1e-3, "xatol": 1e-2})
    return float(res.fun)


def profile_lambda(lambdas=(0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75), *,
                   w_full: float | None = None, n: int = 45_000,
                   seed: int = 11, maxiter: int = 250) -> dict:
    """Profile the loss over the direct-causal fraction lambda."""
    w_full = w_full if w_full is not None else w_prone_full(seed)
    curve = {float(lam): loss_at_fixed_wprone(lam * w_full, n=n, seed=seed, maxiter=maxiter)
             for lam in lambdas}
    best_lambda = min(curve, key=curve.get)
    best_loss = curve[best_lambda]
    # the smallest lambda whose loss stays within 2x of the best fit -> a crude
    # "fit falls apart below here" bound (loss is weighted SSE, not a likelihood).
    acceptable = [lam for lam, L in curve.items() if L <= 2.0 * best_loss]
    return {
        "w_full": w_full,
        "curve": curve,
        "best_lambda": best_lambda,
        "best_loss": best_loss,
        "min_acceptable_lambda": min(acceptable) if acceptable else None,
    }
