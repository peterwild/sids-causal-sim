"""Tests for the Phase 7 exhaustion/displacement model (fast; hand-set Params)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.displacement import (DisplacementParams, ExhaustionParams, Family,
                                   displaced_risk, evaluate_family, exhaustion,
                                   fragmentation, p_displace,
                                   solve_exhaustion_threshold)
from sids_sim.mediation import Profile
from sids_sim.scm import Params

P = Params(w_prone=1.15, hazard_intercept=-7.4, triple_vuln_bonus=2.0,
           triple_nonvuln_floor=-10.0, p_vulnerable=0.37, w_ses=0.3)


def test_supine_more_fragmented_than_prone():
    ep = ExhaustionParams()
    assert fragmentation(ep, "supine", False) > fragmentation(ep, "prone", False)


def test_soother_cuts_fragmentation():
    ep = ExhaustionParams()
    assert fragmentation(ep, "supine", True) < fragmentation(ep, "supine", False)


def test_exhaustion_rises_with_adversity():
    ep = ExhaustionParams()
    easy = Family(ses=2.0, no_support=0, multiparity=0)
    hard = Family(ses=-2.0, no_support=1, multiparity=1)
    assert exhaustion(hard, ep, "supine", False) > exhaustion(easy, ep, "supine", False)


def test_abstinence_framing_raises_displaced_risk():
    dp = DisplacementParams()
    base = 0.0001
    assert displaced_risk(base, dp, abstinence=True) > displaced_risk(base, dp, abstinence=False)


def test_displacement_prob_monotone_in_exhaustion():
    dp = DisplacementParams()
    assert p_displace(2.0, dp, abstinence=True) > p_displace(-2.0, dp, abstinence=True)


def test_soother_lowers_risk_vs_plain_supine():
    out = evaluate_family(P, Profile.low_risk(), Family(ses=-1.5, no_support=1, multiparity=1))
    # the SNOO-like arm should be the safest of the three (least displacement)
    assert out.risk_supine_plus_soother <= out.risk_supine_advice
    assert out.p_displace_soother < out.p_displace_supine


def test_net_harmful_only_for_exhausted():
    # advantaged family: supine advice net-protective vs prone (net <= 0);
    # deprived/solo/twins under abstinence: can flip net-harmful (net > 0)
    easy = evaluate_family(P, Profile.low_risk(), Family(ses=2.0), abstinence=True)
    hard = evaluate_family(P, Profile.low_risk(),
                           Family(ses=-2.0, no_support=1, multiparity=1), abstinence=True)
    assert easy.net_advice_minus_prone <= 0
    assert hard.net_advice_minus_prone > easy.net_advice_minus_prone


def test_harm_reduction_pushes_flip_further_than_abstinence():
    abst = solve_exhaustion_threshold(P, Profile.low_risk(), abstinence=True)
    harm = solve_exhaustion_threshold(P, Profile.low_risk(), abstinence=False)
    # if abstinence flips at some ses, harm-reduction should flip at a lower ses
    # (more deprived) or not at all -> harm-reduction is safer framing
    if abst["ses_at_flip"] is not None and harm["ses_at_flip"] is not None:
        assert harm["ses_at_flip"] <= abst["ses_at_flip"]
    else:
        assert harm["ses_at_flip"] is None or abst["ses_at_flip"] is not None
