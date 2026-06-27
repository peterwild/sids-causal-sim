"""Phase 3.5 -- biased case-control replication (DESIGN.md section 6, step 2).

The historical prone OR came from retrospective case-control studies, which carry
two classic biases Pete is right to be skeptical of:

  * RECALL bias -- parents of a dead infant are interviewed intensely and
    scrutinize the sleep position; some truly-supine cases get reported prone
    (differential misclassification that inflates the OR).
  * CONTROL-SELECTION bias -- volunteer/hospital controls skew advantaged, who are
    less likely to put a baby prone, making controls look artificially supine
    (also inflates the OR).

This module plants a KNOWN causal effect (the calibrated world), then runs the
flawed study design ON TOP and compares the OR the design WOULD HAVE REPORTED to
the TRUE do-effect. It quantifies how much of the famous OR could be a study
artifact vs real -- the honest answer to "can you even trust those studies?"
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .scm import Era, Params, SimConfig, World, pdeath, simulate_covariates


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def _odds(p):
    return p / (1.0 - p)


def true_do_or(world: World, params: Params, *, era: Era = Era.POST,
               n: int = 150_000, seed: int = 11) -> float:
    """The PLANTED truth: marginal causal OR from the do-operator (set prone=1 for
    everyone vs prone=0 for everyone), no study, no bias.
    """
    cov = simulate_covariates(SimConfig(n=n, era=era, world=world, seed=seed, params=params))
    common = dict(
        vulnerable=cov.vulnerable.to_numpy(), smoke=cov.smoke.to_numpy(),
        heavy_smoke=cov.heavy_smoke.to_numpy(), soft_bedding=cov.soft_bedding.to_numpy(),
        ses=cov.ses.to_numpy(),
    )
    p1 = pdeath(world, params, prone=np.ones(n), **common).mean()
    p0 = pdeath(world, params, prone=np.zeros(n), **common).mean()
    return float(_odds(p1) / _odds(p0))


def _crude_or(prone, death) -> float:
    cases_p = ((death == 1) & (prone == 1)).sum() + 0.5
    cases_np = ((death == 1) & (prone == 0)).sum() + 0.5
    ctrl_p = ((death == 0) & (prone == 1)).sum() + 0.5
    ctrl_np = ((death == 0) & (prone == 0)).sum() + 0.5
    return float((cases_p / cases_np) / (ctrl_p / ctrl_np))


def biased_case_control_or(df: pd.DataFrame, *, case_overreport: float = 0.15,
                           control_advantage_k: float = 0.7,
                           controls_per_case: int = 5, seed: int = 0) -> float:
    """OR a flawed retrospective study WOULD report: recall bias (cases over-report
    prone among the truly-supine) + control-selection bias (controls oversampled
    toward advantaged/supine families).
    """
    rng = np.random.default_rng(seed)
    cases = df[df.death == 1].copy()
    controls = df[df.death == 0].copy()

    # control-selection bias: sample controls with weight rising in advantage (ses)
    w = _sigmoid(control_advantage_k * controls.ses.to_numpy())
    w = w / w.sum()
    n_ctrl = min(len(controls), controls_per_case * len(cases))
    idx = rng.choice(len(controls), size=n_ctrl, replace=False, p=w)
    controls = controls.iloc[idx].copy()

    # recall bias: among cases truly supine, a fraction are mis-reported prone
    cp = cases.prone.to_numpy().copy()
    supine_cases = cp == 0
    flip = supine_cases & (rng.random(len(cp)) < case_overreport)
    cp[flip] = 1
    cases["obs_prone"] = cp
    controls["obs_prone"] = controls.prone.to_numpy()  # controls report accurately

    sample = pd.concat([cases, controls], ignore_index=True)
    return _crude_or(sample["obs_prone"].to_numpy(), sample["death"].to_numpy())


def bias_decomposition(world: World, params: Params, *, era: Era = Era.POST,
                       n: int = 150_000, seed: int = 11,
                       case_overreport: float = 0.15,
                       control_advantage_k: float = 0.7) -> dict:
    """Compare the true do-OR to the OR under: clean design, recall-only,
    selection-only, and both biases together.
    """
    from .scm import attach_hazard
    cov = simulate_covariates(SimConfig(n=n, era=era, world=world, seed=seed, params=params))
    rng = np.random.default_rng(seed + 999)
    df = attach_hazard(cov, world, params, rng)

    truth = true_do_or(world, params, era=era, n=n, seed=seed)
    clean = biased_case_control_or(df, case_overreport=0.0, control_advantage_k=0.0, seed=seed)
    recall = biased_case_control_or(df, case_overreport=case_overreport,
                                    control_advantage_k=0.0, seed=seed)
    select = biased_case_control_or(df, case_overreport=0.0,
                                    control_advantage_k=control_advantage_k, seed=seed)
    both = biased_case_control_or(df, case_overreport=case_overreport,
                                  control_advantage_k=control_advantage_k, seed=seed)
    return {
        "true_do_or": truth,
        "clean_design_or": clean,
        "recall_only_or": recall,
        "selection_only_or": select,
        "both_biases_or": both,
        "inflation_factor": both / truth if truth else float("nan"),
    }
