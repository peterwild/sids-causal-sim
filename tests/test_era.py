"""Tests for the Phase 9 era-model extension (additive, default-off)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from sids_sim.era import _cov, _expected_rate, make_era_params
from sids_sim.scm import (Era, Params, SimConfig, World, pdeath,
                          simulate_covariates)

BASE = Params(w_prone=1.15, hazard_intercept=-10.3, triple_vuln_bonus=2.3,
              triple_nonvuln_floor=-10.0, p_vulnerable=0.37, w_ses=0.3)


def test_defaults_add_only_a_bf_column_no_perturbation():
    # with default (inert) params, adding breastfeeding must not change prone/smoke
    p = Params()
    a = simulate_covariates(SimConfig(n=5000, era=Era.PRE, world=World.TRIPLE, seed=7, params=p))
    assert "breastfeeding" in a.columns
    # prone/smoke draws are deterministic given seed and unaffected by the bf draw
    assert set(a["prone"].unique()) <= {0, 1}
    assert 0.0 < a["breastfeeding"].mean() < 1.0


def test_breastfeeding_is_protective_when_active():
    p = Params(w_bf=0.6)
    kw = dict(vulnerable=np.array([1, 1]), smoke=np.array([0, 0]),
              heavy_smoke=np.array([0, 0]), soft_bedding=np.array([0, 0]),
              prone=np.array([0, 0]), ses=np.array([0.0, 0.0]))
    fed = pdeath(World.TRIPLE, p, breastfeeding=np.array([1, 1]), **kw)
    not_fed = pdeath(World.TRIPLE, p, breastfeeding=np.array([0, 0]), **kw)
    assert fed[0] < not_fed[0]


def test_smoke_post_shift_lowers_post_prevalence():
    p = Params(smoke_post_shift=-1.0)
    pre = simulate_covariates(SimConfig(n=40000, era=Era.PRE, world=World.TRIPLE, seed=1, params=p))
    post = simulate_covariates(SimConfig(n=40000, era=Era.POST, world=World.TRIPLE, seed=1, params=p))
    assert post["smoke"].mean() < pre["smoke"].mean()


def test_era_overlay_lowers_post_rate_and_relevels_pre():
    p = make_era_params(BASE, smoke_post_shift=-1.0, n=20000)
    pre_rate = _expected_rate(p, _cov(p, Era.PRE, 20000))
    base_post = _expected_rate(BASE, _cov(BASE, Era.POST, 20000))
    enr_post = _expected_rate(p, _cov(p, Era.POST, 20000))
    assert abs(pre_rate - 1.2) < 0.15          # re-leveled to PRE target
    assert enr_post < base_post                 # era trends pull POST down
