"""Tests for the Phase 8 home-protocol comparison (fast; hand-set Params)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.protocols import (PROTOCOLS, HomeProtocol, compare_protocols,
                               evaluate_protocol, sample_population)
from sids_sim.scm import Params

P = Params(w_prone=1.15, hazard_intercept=-7.4, triple_vuln_bonus=2.0,
           triple_nonvuln_floor=-10.0, p_vulnerable=0.37, w_ses=0.3)


def _pop(n=4000):
    return sample_population(P, n=n, seed=1)


def test_breathable_equals_bare_for_supine():
    # a breathable mattress does nothing for a SUPINE baby (rebreathing is a
    # prone channel) -> same net as the bare firm crib
    pop = _pop()
    bare = HomeProtocol("bare", "supine", False, False, False)
    breath = HomeProtocol("breath", "supine", True, False, False)
    a = evaluate_protocol(P, pop, bare, abstinence=True)
    b = evaluate_protocol(P, pop, breath, abstinence=True)
    assert abs(a["net_per_1000"] - b["net_per_1000"]) < 1e-9


def test_soother_cuts_displacement_component():
    pop = _pop()
    bare = HomeProtocol("bare", "supine", False, False, False)
    sooth = HomeProtocol("sooth", "supine", True, True, True)
    a = evaluate_protocol(P, pop, bare, abstinence=True)
    s = evaluate_protocol(P, pop, sooth, abstinence=True)
    # same in-crib risk (both supine) but the soother lowers displacement
    assert s["displacement_component_per_1000"] < a["displacement_component_per_1000"]
    assert s["net_per_1000"] < a["net_per_1000"]


def test_prone_has_higher_incrib_but_less_displacement():
    pop = _pop()
    supine = HomeProtocol("supine", "supine", False, False, False)
    prone = HomeProtocol("eng prone", "prone", True, True, False)
    s = evaluate_protocol(P, pop, supine, abstinence=True)
    pr = evaluate_protocol(P, pop, prone, abstinence=True)
    assert pr["incrib_component_per_1000"] > s["incrib_component_per_1000"]
    assert pr["displacement_component_per_1000"] < s["displacement_component_per_1000"]


def test_harm_reduction_beats_abstinence_everywhere():
    pop = _pop()
    for proto in PROTOCOLS:
        a = evaluate_protocol(P, pop, proto, abstinence=True)
        h = evaluate_protocol(P, pop, proto, abstinence=False)
        assert h["net_per_1000"] <= a["net_per_1000"] + 1e-9


def test_soother_is_top_ranked():
    rows = compare_protocols(P, abstinence=True, n=6000)
    assert "soother" in rows[0]["protocol"]


def test_historical_prone_is_worst():
    rows = compare_protocols(P, abstinence=True, n=6000)
    assert "historical prone" in rows[-1]["protocol"]
