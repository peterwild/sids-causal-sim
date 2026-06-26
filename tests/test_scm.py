"""Phase 1 sanity checks: the simulator runs and the engineered structural
behaviours show up. These are NOT calibration gates (that's Phase 2) -- they only
assert the qualitative shape we built into the DAG.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sids_sim.scm import Era, SimConfig, World, simulate_cohort
from sids_sim.summarize import crude_prone_or, summarize


def _cohort(world, era, n=200_000, seed=7):
    return simulate_cohort(SimConfig(n=n, era=era, world=world, seed=seed))


def test_runs_and_shapes():
    df = _cohort(World.TRIPLE, Era.PRE)
    assert len(df) == 200_000
    assert set(["prone", "death", "vulnerable", "smoke"]).issubset(df.columns)
    assert 0 < df.death.mean() < 0.1


def test_adherer_gate_makes_OR_rise_post_campaign():
    # healthy-adherer gate: prone OR should be higher post-campaign than pre,
    # in any world where prone is associated with the hazard.
    for world in (World.CAUSAL, World.TRIPLE):
        or_pre = crude_prone_or(_cohort(world, Era.PRE))
        or_post = crude_prone_or(_cohort(world, Era.POST))
        assert or_post > or_pre, world


def test_marker_world_has_weak_direct_signal():
    # H2 has no direct prone effect, so its OR should be far below the causal world
    or_marker = crude_prone_or(_cohort(World.MARKER, Era.PRE))
    or_causal = crude_prone_or(_cohort(World.CAUSAL, Era.PRE))
    assert or_marker < or_causal


def test_triple_world_concentrates_deaths_in_vulnerable():
    s = summarize(_cohort(World.TRIPLE, Era.PRE))
    assert s["vuln_prev_in_cases"] > 0.8  # deaths heavily enriched for vulnerability
