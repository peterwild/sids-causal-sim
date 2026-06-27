"""Tests for the Phase 6 continuous mixing fit (small/fast calibration settings)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.mixing import loss_at_fixed_wprone, profile_lambda


def test_marker_end_fits_worse_than_causal_end():
    # lambda=0 (no direct effect) must fit worse than a healthy direct effect
    loss0 = loss_at_fixed_wprone(0.0, n=9000, seed=11, maxiter=40)
    loss1 = loss_at_fixed_wprone(1.1, n=9000, seed=11, maxiter=40)
    assert loss0 > loss1


def test_profile_returns_curve_and_best():
    out = profile_lambda(lambdas=(0.0, 1.0), w_full=1.1, n=9000, seed=11, maxiter=40)
    assert set(out["curve"]) == {0.0, 1.0}
    assert out["best_lambda"] in (0.0, 1.0)
    # the causal end should win
    assert out["curve"][1.0] < out["curve"][0.0]
