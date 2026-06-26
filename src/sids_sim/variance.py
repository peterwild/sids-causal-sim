"""Phase 4 -- variance decomposition and PCA.

Two different questions the word 'principal component' can mean:

1. PCA on the risk-factor matrix: do the factors bundle into axes, and does prone
   sit on its OWN axis or co-load with the social-adversity bundle (smoking, SES,
   bedding)? If prone loads with adversity, that eigenvector IS the
   correlation-vs-causation story drawn as a picture.

2. Shapley / LMG decomposition of OUTCOME variance: of all factors, which explains
   the largest share of variation in death? Run twice --
     * observable-only (what an epidemiologist measures), and
     * full, including the latent vulnerability --
   to show that the single biggest axis of variance is the hidden vulnerability,
   while prone is a strong but era-dependent slice among the modifiable factors.

LMG handles correlated predictors by averaging each predictor's incremental R^2
over every ordering (this equals the Shapley value of R^2).
"""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd


# --------------------------------------------------------------------------- #
# OLS R^2 and the Shapley / LMG relative-importance decomposition
# --------------------------------------------------------------------------- #
def _r2(df: pd.DataFrame, outcome: str, predictors: tuple) -> float:
    y = df[outcome].to_numpy(float)
    if not predictors:
        return 0.0
    X = np.column_stack([np.ones(len(df))] + [df[p].to_numpy(float) for p in predictors])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    sse = float(resid @ resid)
    sst = float(((y - y.mean()) ** 2).sum())
    return 1.0 - sse / sst if sst > 0 else 0.0


def lmg_decomposition(df: pd.DataFrame, outcome: str, predictors: list) -> dict:
    """Shapley/LMG share of explained R^2 for each predictor.

    Returns {predictor: absolute_R2_share}, summing to the full-model R^2.
    """
    p = len(predictors)
    idx = list(range(p))
    # memoize R^2 over subsets (by frozenset of indices)
    cache: dict[frozenset, float] = {}

    def r2(subset_idx) -> float:
        key = frozenset(subset_idx)
        if key not in cache:
            cache[key] = _r2(df, outcome, tuple(predictors[i] for i in subset_idx))
        return cache[key]

    # Shapley weights: |S|! (p-|S|-1)! / p!
    from math import factorial
    shares = {predictors[j]: 0.0 for j in idx}
    for j in idx:
        others = [i for i in idx if i != j]
        for k in range(len(others) + 1):
            w = factorial(k) * factorial(p - k - 1) / factorial(p)
            for S in combinations(others, k):
                shares[predictors[j]] += w * (r2(tuple(S) + (j,)) - r2(S))
    return shares


def lmg_table(df: pd.DataFrame, outcome: str, predictors: list) -> pd.DataFrame:
    shares = lmg_decomposition(df, outcome, predictors)
    total = sum(shares.values())
    rows = [{"factor": k, "r2_share": v, "pct_of_explained": (v / total if total else 0.0)}
            for k, v in sorted(shares.items(), key=lambda kv: -kv[1])]
    out = pd.DataFrame(rows).set_index("factor")
    out.attrs["total_r2"] = total
    return out


# --------------------------------------------------------------------------- #
# PCA on the standardized risk-factor matrix
# --------------------------------------------------------------------------- #
def pca_loadings(df: pd.DataFrame, predictors: list, n_components: int = 3):
    """Return (explained_variance_ratio, loadings_df). Loadings are the
    eigenvectors of the correlation matrix (variables standardized).
    """
    X = np.column_stack([df[p].to_numpy(float) for p in predictors])
    X = (X - X.mean(0)) / X.std(0)
    # correlation-matrix eigendecomposition
    C = np.corrcoef(X, rowvar=False)
    vals, vecs = np.linalg.eigh(C)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    evr = vals / vals.sum()
    k = min(n_components, len(predictors))
    loadings = pd.DataFrame(
        vecs[:, :k],
        index=predictors,
        columns=[f"PC{i+1}" for i in range(k)],
    )
    return evr[:k], loadings
