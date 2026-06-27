"""Phase 8 -- home-protocol comparison, the capstone (DESIGN.md section 16).

Integrates Phase 4.5 (position/environment -> in-crib risk) and Phase 7
(exhaustion -> bed-sharing displacement) into ONE model, and ranks realistic home
protocols by NET population infant mortality:

    net death risk = (1 - P(displace)) * in-crib risk  +  P(displace) * displaced risk

evaluated over a synthetic population (infant SIDS profiles x family exhaustion
drivers). The point (DESIGN section 16): the enforced-supine soother wins NOT by
lowering the per-night in-crib risk (it is already supine) but by suppressing the
displacement arm the other supine protocols leave active. A breathable mattress
barely helps a SUPINE baby (rebreathing is a prone channel), and permitting
engineered prone trades a small in-crib penalty for less displacement -- a real,
controversial wash that the model makes explicit.

Magnitudes inherit the illustrative displacement params (Phase 7); the deliverable
is the RANKING and the in-crib-vs-displacement decomposition, not the absolute
levels.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .displacement import DisplacementParams, ExhaustionParams, fragmentation
from .mediation import (Apportionment, Environment, FORM_SHARES, prone_logodds,
                        solve_unhab_factor)
from .scm import Era, SimConfig, World, simulate_covariates
from .scm import Params, _sigmoid


@dataclass(frozen=True)
class HomeProtocol:
    name: str
    position: str        # 'supine' | 'prone'
    breathable: bool
    cool: bool
    soother: bool        # enforced-supine soothing device (SNOO-like)


PROTOCOLS = [
    HomeProtocol("supine, bare firm crib", "supine", False, False, False),
    HomeProtocol("supine + breathable mattress", "supine", True, False, False),
    HomeProtocol("supine + soother (SNOO)", "supine", True, True, True),
    HomeProtocol("engineered prone permitted", "prone", True, True, False),
    HomeProtocol("historical prone (reference)", "prone", False, False, False),
]


@dataclass
class Population:
    ses: np.ndarray
    smoke: np.ndarray
    heavy: np.ndarray
    bedding: np.ndarray
    no_support: np.ndarray
    multiparity: np.ndarray


def sample_population(p: Params, n: int = 80_000, seed: int = 5) -> Population:
    """Infant SIDS profiles (from the SCM, POST era) + family exhaustion drivers."""
    cov = simulate_covariates(SimConfig(n=n, era=Era.POST, world=World.TRIPLE,
                                        seed=seed, params=p))
    rng = np.random.default_rng(seed + 17)
    # exhaustion drivers correlate weakly with disadvantage (lower ses)
    ses = cov.ses.to_numpy()
    no_support = (rng.random(n) < _sigmoid(-1.4 - 0.4 * ses)).astype(int)
    multiparity = (rng.random(n) < 0.20).astype(int)
    return Population(ses=ses, smoke=cov.smoke.to_numpy(), heavy=cov.heavy_smoke.to_numpy(),
                     bedding=cov.soft_bedding.to_numpy(), no_support=no_support,
                     multiparity=multiparity)


def _base_supine_vec(p: Params, pop: Population) -> np.ndarray:
    """Absolute supine death prob per infant, marginal over vulnerability."""
    base_stressors = (p.w_smoke * pop.smoke + p.w_heavy_extra * pop.heavy
                      + p.w_bedding * pop.bedding - p.w_ses * pop.ses)
    eta_vuln = p.hazard_intercept + p.triple_vuln_bonus + base_stressors
    risk_vuln = _sigmoid(eta_vuln)
    risk_nonvuln = _sigmoid(p.triple_nonvuln_floor)
    return p.p_vulnerable * risk_vuln + (1 - p.p_vulnerable) * risk_nonvuln


def evaluate_protocol(p: Params, pop: Population, proto: HomeProtocol, *,
                      abstinence: bool, form: str = "G_gated",
                      ep: ExhaustionParams | None = None,
                      dp: DisplacementParams | None = None) -> dict:
    """Population net mortality (per 1000) for one protocol + framing, split into
    the in-crib and displacement components.
    """
    ep = ep or ExhaustionParams()
    dp = dp or DisplacementParams()
    appor = Apportionment.from_shares(p.w_prone, FORM_SHARES[form])
    unhab = solve_unhab_factor(appor)

    base_supine = _base_supine_vec(p, pop)

    # in-crib risk: supine = base; prone = base scaled by the prone log-odds bump
    if proto.position == "prone":
        env = Environment(breathable=proto.breathable, cool=proto.cool, habituated=True)
        bump = prone_logodds(appor, env, unhab)
        base_stressors = (p.w_smoke * pop.smoke + p.w_heavy_extra * pop.heavy
                          + p.w_bedding * pop.bedding - p.w_ses * pop.ses)
        eta_vuln = p.hazard_intercept + p.triple_vuln_bonus + base_stressors + bump
        crib = (p.p_vulnerable * _sigmoid(eta_vuln)
                + (1 - p.p_vulnerable) * _sigmoid(p.triple_nonvuln_floor))
    else:
        crib = base_supine

    # displacement: exhaustion from this protocol's sleep arrangement
    frag = fragmentation(ep, proto.position, proto.soother)
    E = (ep.intercept + ep.b_frag * frag - ep.b_ses * pop.ses
         + ep.b_no_support * pop.no_support + ep.b_multiparity * pop.multiparity)
    pD = _sigmoid(dp.alpha0 + dp.alpha_E * E + dp.alpha_abstinence * (1 if abstinence else 0))

    mix = dp.loc_abstinence if abstinence else dp.loc_harm_reduction
    weighted_or = sum(w * o for w, o in zip(mix, (dp.or_prepared_bed, dp.or_unplanned_bed, dp.or_sofa)))
    displaced = base_supine * weighted_or

    net = (1 - pD) * crib + pD * displaced
    return {
        "net_per_1000": float(net.mean() * 1000),
        "incrib_component_per_1000": float(((1 - pD) * crib).mean() * 1000),
        "displacement_component_per_1000": float((pD * displaced).mean() * 1000),
        "mean_p_displace": float(pD.mean()),
    }


def compare_protocols(p: Params, *, abstinence: bool = True, n: int = 80_000,
                      seed: int = 5, form: str = "G_gated") -> list[dict]:
    """Rank all protocols by net population mortality under a framing."""
    pop = sample_population(p, n=n, seed=seed)
    rows = []
    for proto in PROTOCOLS:
        r = evaluate_protocol(p, pop, proto, abstinence=abstinence, form=form)
        r["protocol"] = proto.name
        rows.append(r)
    rows.sort(key=lambda r: r["net_per_1000"])
    return rows
