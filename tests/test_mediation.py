"""Tests for Phase 4.5 mechanism decomposition (mediation.py).

Uses hand-set Params so the suite stays fast (no calibration in the loop).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.mediation import (Apportionment, Environment, Profile,
                                FORM_SHARES, delta_abs_risk, form_evalue_lambda,
                                prone_logodds, run_linchpin, solve_unhab_factor)
from sids_sim.scm import Params

# representative calibrated-ish triple world
P = Params(w_prone=1.15, hazard_intercept=-7.4, triple_vuln_bonus=2.0,
           triple_nonvuln_floor=-10.0, p_vulnerable=0.37, w_ses=0.3)


def test_apportionment_sums_to_w_prone():
    for shares in FORM_SHARES.values():
        a = Apportionment.from_shares(P.w_prone, shares)
        assert a.total() == pytest.approx(P.w_prone, abs=1e-9)


def test_shares_must_sum_to_one():
    with pytest.raises(ValueError):
        Apportionment.from_shares(1.0, {"rebr": 0.5, "obstr": 0.2})


def test_historical_contribution_reproduces_w_prone():
    # historical crib + habituated => decomposed contribution == calibrated w_prone
    a = Apportionment.from_shares(P.w_prone, FORM_SHARES["G_gated"])
    hist = Environment(breathable=False, cool=False, habituated=True)
    assert prone_logodds(a, hist, unhab_factor=1.0) == pytest.approx(P.w_prone)


def test_engineering_reduces_or_preserves_risk():
    # a breathable + cool environment can only lower (never raise) the prone effect
    a = Apportionment.from_shares(P.w_prone, FORM_SHARES["G_gated"])
    unhab = solve_unhab_factor(a)
    hist = Environment(breathable=False, cool=False, habituated=True)
    eng = Environment(breathable=True, cool=True, habituated=True)
    d_hist = delta_abs_risk(P, Profile.low_risk(), a, hist, unhab)
    d_eng = delta_abs_risk(P, Profile.low_risk(), a, eng, unhab)
    assert 0 < d_eng < d_hist


def test_gated_form_more_engineerable_than_additive():
    # Form G (lambda~0) leaves a smaller engineered residual than Form A (big lambda)
    prof = Profile.low_risk()
    eng = Environment(breathable=True, cool=True, habituated=True)
    g = Apportionment.from_shares(P.w_prone, FORM_SHARES["G_gated"])
    a = Apportionment.from_shares(P.w_prone, FORM_SHARES["A_additive"])
    d_g = delta_abs_risk(P, prof, g, eng, solve_unhab_factor(g))
    d_a = delta_abs_risk(P, prof, a, eng, solve_unhab_factor(a))
    assert d_g < d_a


def test_unaccustomed_amplifier_hits_target_or():
    # the solved amplifier should reproduce ~19 for the unaccustomed sleeper
    a = Apportionment.from_shares(P.w_prone, FORM_SHARES["G_gated"])
    unhab = solve_unhab_factor(a, target_or=19.0)
    unaccustomed = Environment(breathable=False, cool=False, habituated=False)
    or_check = math.exp(prone_logodds(a, unaccustomed, unhab))
    assert or_check == pytest.approx(19.0, rel=0.05)


def test_low_risk_profile_lowers_absolute_risk():
    # advantaged, non-smoking profile must carry lower absolute risk than a
    # high-risk one at the same position
    a = Apportionment.from_shares(P.w_prone, FORM_SHARES["G_gated"])
    eng = Environment(breathable=False, cool=False, habituated=True)
    low = delta_abs_risk(P, Profile.low_risk(), a, eng, 1.0)
    high = delta_abs_risk(P, Profile(smoke=1, heavy_smoke=1, soft_bedding=1, ses=-1.0),
                          a, eng, 1.0)
    assert low < high


def test_form_evalue_monotone_and_bounded():
    ev = form_evalue_lambda(P, Profile.low_risk(), P.w_prone,
                            Environment(breathable=True, cool=True), 0.5)
    # residual rises with the free-standing arousal share
    assert ev["residual_at_max_lambda_per_1000"] >= ev["residual_at_zero_lambda_per_1000"]


def test_run_linchpin_smoke():
    res = run_linchpin(P)
    assert set(res["forms"]) == set(FORM_SHARES)
    for f in res["forms"].values():
        # engineering never makes things worse
        assert f["excess_engineered_per_1000"] <= f["excess_historical_per_1000"]
