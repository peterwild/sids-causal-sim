"""Tests for the Phase 3.5 biased case-control replication."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from sids_sim.bias import (_crude_or, biased_case_control_or, true_do_or)
from sids_sim.scm import Era, Params, SimConfig, World, simulate_cohort

# a clearly-causal world for testing
P = Params(w_prone=1.5, w_vuln=1.2, hazard_intercept=-7.0, p_vulnerable=0.37)


def _cohort(world=World.CAUSAL, era=Era.POST, n=120_000, seed=3):
    return simulate_cohort(SimConfig(n=n, era=era, world=world, seed=seed, params=P))


def test_crude_or_recovers_known_ratio():
    # 2x2 OR = (90.5/10.5)/(30.5/70.5) = 19.92 with the 0.5 continuity correction
    prone = np.array([1] * 90 + [0] * 10 + [1] * 30 + [0] * 70)
    death = np.array([1] * 100 + [0] * 100)
    assert _crude_or(prone, death) == __import__("pytest").approx(19.92, rel=0.02)


def test_true_do_or_above_one_for_causal():
    assert true_do_or(World.CAUSAL, P, era=Era.POST, n=80_000) > 1.5


def test_marker_world_true_do_or_near_one():
    # marker world has zero direct effect -> do-OR ~ 1
    do = true_do_or(World.MARKER, P, era=Era.POST, n=80_000)
    assert 0.8 < do < 1.25


def test_biases_inflate_the_or():
    df = _cohort()
    clean = biased_case_control_or(df, case_overreport=0.0, control_advantage_k=0.0, seed=1)
    both = biased_case_control_or(df, case_overreport=0.15, control_advantage_k=0.7, seed=1)
    assert both > clean


def test_each_bias_inflates_individually():
    df = _cohort()
    clean = biased_case_control_or(df, case_overreport=0.0, control_advantage_k=0.0, seed=2)
    recall = biased_case_control_or(df, case_overreport=0.2, control_advantage_k=0.0, seed=2)
    select = biased_case_control_or(df, case_overreport=0.0, control_advantage_k=0.9, seed=2)
    assert recall > clean
    assert select > clean
