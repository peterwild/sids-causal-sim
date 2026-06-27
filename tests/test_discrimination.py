"""Tests for the Phase 5 discrimination scoring logic.

Calibration is slow, so these exercise build_checks / gate logic on synthetic
metric dicts rather than running the full optimizer.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.discrimination import (Check, build_checks, gate_rise_ok,
                                     load_targets)


def _fake_ev(adj_or_pre, adj_or_post, paf_pre=0.50, paf_post=0.80):
    """A metrics dict shaped like evaluate_world() output, with knobs for the gates."""
    def era(prone_cases, prone_ctrl, rate, adj_or, paf):
        return {
            "prone_prev_cases": prone_cases,
            "prone_prev_controls": prone_ctrl,
            "death_rate_per_1000": rate,
            "adjusted_prone_or": adj_or,
            "smoking_paf": paf,
            "vuln_prev_controls": 0.37,
            "vuln_prev_cases": 0.83,
            "smoking_ors": {"base": 2.0, "heavy": 12.7},
        }
    return {
        "pre": era(0.84, 0.50, 1.2, adj_or_pre, paf_pre),
        "post": era(0.485, 0.246, 0.4, adj_or_post, paf_post),
    }


def test_check_passed_tolerance():
    c = Check("x", "pre", achieved=2.9, expected=2.86, tol=0.5, is_gate=True)
    assert c.passed
    c2 = Check("x", "pre", achieved=1.0, expected=2.86, tol=0.5, is_gate=True)
    assert not c2.passed


def test_causal_like_world_passes_all():
    targets = load_targets()
    checks = build_checks(_fake_ev(3.21, 3.96), targets)
    assert all(c.passed for c in checks)
    assert gate_rise_ok(checks, "prone_adjusted_or")
    assert gate_rise_ok(checks, "smoking_attributable_risk")


def test_marker_like_world_fails_or_gate():
    targets = load_targets()
    checks = build_checks(_fake_ev(1.10, 1.00), targets)
    or_checks = [c for c in checks if c.target_id == "prone_adjusted_or"]
    assert all(not c.passed for c in or_checks)          # OR ~1 misses 2.86/3.93
    assert not gate_rise_ok(checks, "prone_adjusted_or")  # and no rise (post<pre)


def test_gate_rise_requires_increase():
    targets = load_targets()
    # OR levels fine but FALLING across the era -> rise gate must fail
    checks = build_checks(_fake_ev(3.93, 2.86), targets)
    assert not gate_rise_ok(checks, "prone_adjusted_or")
