"""Structural causal model (SCM) for the SIDS prone-sleeping question.

This is the DAG in DESIGN.md section 4 turned into code. We generate one row per
infant. Every variable is produced by an explicit structural equation from its
parents plus noise, so the *generative* correlations (prone travels with smoking,
soft bedding, low SES) are real and built in. The three worlds differ ONLY in how
prone enters the death hazard:

    H1 (causal) : prone has a large direct effect on the hazard for everyone.
    H2 (marker) : prone has ~zero direct effect; its apparent risk is borrowed
                  entirely from the adverse factors it co-occurs with.
    H3 (triple) : prone is a trigger that only bites if the infant is vulnerable
                  (latent brainstem phenotype) -- a multiplicative interaction.

Phase 1 goal: produce plausibly-shaped cohorts with hand-set defaults so we can
eyeball marginals. Tuning the constants to hit the calibration targets is Phase 2.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import numpy as np
import pandas as pd


class World(str, Enum):
    CAUSAL = "H1_causal"
    MARKER = "H2_marker"
    TRIPLE = "H3_triple"


class Era(str, Enum):
    PRE = "pre"    # before the Back-to-Sleep campaign (prone advised / common)
    POST = "post"  # after the campaign (prone advised against)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class Params:
    """All structural-equation coefficients in one place.

    Defaults are hand-set to land in the right ballpark, NOT yet calibrated.
    Higher SES = more advantaged. Sign conventions noted per field.
    """

    # --- exogenous prevalences ---
    p_vulnerable: float = 0.37          # latent brainstem phenotype, population base rate

    # --- smoking | SES  (lower SES -> more smoking) ---
    smoke_intercept: float = -0.40      # sigmoid(-0.4) ~= 0.40 at SES=0
    smoke_ses_slope: float = -1.00
    p_heavy_given_smoke: float = 0.25   # >20 cig/day among smokers
    # Phase 9 (era-model closure): smoking declined across the campaign era. A
    # log-odds shift applied to the smoking intercept in the POST era. Default 0
    # keeps the base model byte-identical (era switch changes only prone+bedding).
    smoke_post_shift: float = 0.0

    # --- breastfeeding (Phase 9): protective, rose across the era ---
    # Defaults make it inert: w_bf=0 means no hazard effect even though the column
    # is generated. The bf draw is taken AFTER prone so existing draw sequences
    # (and thus all earlier-phase cohorts) are unchanged.
    bf_intercept: float = 0.0           # sigmoid(0)=0.5 prevalence at SES=0
    bf_ses_slope: float = 0.0           # advantaged breastfeed more when >0
    bf_post_shift: float = 0.0          # POST-era rise in breastfeeding
    w_bf: float = 0.0                   # protective hazard weight (subtracted)

    # --- soft bedding | SES, era  (lower SES & pre-era -> more soft bedding) ---
    bedding_intercept: float = -0.20
    bedding_ses_slope: float = -0.60
    bedding_post_shift: float = -0.70   # awareness reduces soft bedding post-campaign

    # --- prone choice | era, SES  (the healthy-adherer gate lives here) ---
    # PRE: prone near-universal, weak SES gradient (everyone followed Spock).
    prone_pre_intercept: float = 1.50   # sigmoid(1.5) ~= 0.82
    prone_pre_ses_slope: float = -0.20
    # POST: prone rare overall, and what remains is concentrated in low SES
    # (advice followed by the advantaged) -> strong negative SES slope.
    prone_post_intercept: float = -1.55  # sigmoid(-1.55) ~= 0.17 at SES=0
    prone_post_ses_slope: float = -1.20
    # Phase 3: HIDDEN confounding channel. Log-odds bump to prone choice for
    # vulnerable infants (e.g. fragile/preterm babies placed prone more often).
    # This is UNMEASURED -- the adjusted OR cannot subtract it -- so it is the
    # marker world's last refuge for faking a prone effect with no real effect.
    gamma_vuln_prone: float = 0.0

    # --- death hazard ---
    # baseline log-odds of death with no stressors; very negative (rare outcome).
    hazard_intercept: float = -7.4
    # stressor weights feeding the linear predictor (shared shape across worlds)
    w_smoke: float = 0.9
    w_heavy_extra: float = 1.3          # additional for heavy smokers
    w_bedding: float = 0.8
    w_ses: float = 0.0                  # direct low-SES->hazard path (>=0; main engine of H2)
    w_prone: float = 1.7                # prone's DIRECT contribution (worlds re-scale this)
    # vulnerability main effect (used by H1/H2 as an additive bump)
    w_vuln: float = 1.2
    # H3: non-vulnerable infants sit at this floor log-odds regardless of stressors
    triple_nonvuln_floor: float = -10.0
    # H3: vulnerable infants get the full stressor predictor plus this bump
    triple_vuln_bonus: float = 2.0


@dataclass
class SimConfig:
    n: int = 200_000
    era: Era = Era.PRE
    world: World = World.TRIPLE
    seed: int = 7
    params: Params = field(default_factory=Params)


def _death_logodds(world: World, p: Params, *, vuln, smoke, heavy, bedding, prone,
                   ses, bf=0.0):
    """Return per-infant log-odds of death under the chosen world.

    The stressor predictor is identical across worlds; what changes is how prone
    and vulnerability combine into the final hazard.
    """
    # shared stressor terms (everything EXCEPT prone's direct effect).
    # w_ses is the direct low-SES->hazard path: lower (more negative) ses raises
    # the hazard. This is the marker world's strongest fair engine -- poverty
    # killing through many routes, with prone as its correlate. w_bf is the
    # protective breastfeeding term (Phase 9; default 0 -> inert).
    base_stressors = (
        p.w_smoke * smoke
        + p.w_heavy_extra * heavy
        + p.w_bedding * bedding
        - p.w_ses * ses
        - p.w_bf * bf
    )

    if world is World.CAUSAL:
        # prone acts directly and strongly, for everyone
        eta = (
            p.hazard_intercept
            + p.w_vuln * vuln
            + base_stressors
            + p.w_prone * prone
        )

    elif world is World.MARKER:
        # prone contributes ~nothing directly; risk comes only from the company
        # it keeps (smoke/bedding/SES, already correlated with prone upstream)
        eta = (
            p.hazard_intercept
            + p.w_vuln * vuln
            + base_stressors
            + 0.0 * prone
        )

    elif world is World.TRIPLE:
        # non-vulnerable infants are nearly immune; vulnerable infants feel the
        # full stressor load INCLUDING prone (multiplicative-style interaction)
        eta_vuln = (
            p.hazard_intercept
            + p.triple_vuln_bonus
            + base_stressors
            + p.w_prone * prone
        )
        eta = np.where(vuln == 1, eta_vuln, p.triple_nonvuln_floor)

    else:  # pragma: no cover
        raise ValueError(world)

    return eta


def pdeath(world: World, params: Params, *, vulnerable, smoke, heavy_smoke,
           soft_bedding, prone, ses, breastfeeding=None):
    """Public hazard: probability of death given covariate arrays.

    Used for counterfactual / attributable-fraction calculations (e.g. set
    smoke=0 to ask 'how many deaths would remain with no smoking?'). breastfeeding
    is optional (Phase 9); defaults to none so all earlier-phase calls are unchanged.
    """
    bf = 0.0 if breastfeeding is None else breastfeeding
    eta = _death_logodds(
        world, params, vuln=vulnerable, smoke=smoke, heavy=heavy_smoke,
        bedding=soft_bedding, prone=prone, ses=ses, bf=bf,
    )
    return _sigmoid(eta)


def simulate_covariates(cfg: SimConfig) -> pd.DataFrame:
    """Generate the covariate block (everything EXCEPT death) for one cohort.

    Split out from death generation so the calibrator can solve the hazard
    intercept against fixed covariates (see calibrate.py) without resampling.
    """
    rng = np.random.default_rng(cfg.seed)
    p = cfg.params
    n = cfg.n
    post = cfg.era is Era.POST

    # SES: standard normal latent (higher = more advantaged)
    ses = rng.standard_normal(n)

    # latent vulnerability (independent of SES in Phase 1)
    vuln = (rng.random(n) < p.p_vulnerable).astype(int)

    # smoking | SES, era  (smoke_post_shift declines smoking in POST; default 0)
    p_smoke = _sigmoid(
        p.smoke_intercept + p.smoke_ses_slope * ses
        + (p.smoke_post_shift if post else 0.0)
    )
    smoke = (rng.random(n) < p_smoke).astype(int)
    heavy = ((smoke == 1) & (rng.random(n) < p.p_heavy_given_smoke)).astype(int)

    # soft bedding | SES, era
    p_bed = _sigmoid(
        p.bedding_intercept
        + p.bedding_ses_slope * ses
        + (p.bedding_post_shift if post else 0.0)
    )
    bedding = (rng.random(n) < p_bed).astype(int)

    # prone | era, SES, (hidden) vulnerability
    # gamma_vuln_prone is the unmeasured V->prone channel (Phase 3).
    if post:
        eta_prone = p.prone_post_intercept + p.prone_post_ses_slope * ses
    else:
        eta_prone = p.prone_pre_intercept + p.prone_pre_ses_slope * ses
    eta_prone = eta_prone + p.gamma_vuln_prone * vuln
    prone = (rng.random(n) < _sigmoid(eta_prone)).astype(int)

    # breastfeeding | SES, era -- drawn LAST so adding it does not perturb any
    # prior draw (prone/death sequences stay identical to earlier phases).
    p_bf = _sigmoid(
        p.bf_intercept + p.bf_ses_slope * ses + (p.bf_post_shift if post else 0.0)
    )
    breastfeeding = (rng.random(n) < p_bf).astype(int)

    return pd.DataFrame(
        {
            "ses": ses,
            "vulnerable": vuln,
            "smoke": smoke,
            "heavy_smoke": heavy,
            "soft_bedding": bedding,
            "prone": prone,
            "breastfeeding": breastfeeding,
            "era": cfg.era.value,
            "world": cfg.world.value,
        }
    )


def attach_hazard(df: pd.DataFrame, world: World, params: Params,
                  rng: np.random.Generator) -> pd.DataFrame:
    """Add p_death and a Bernoulli death draw to a covariate frame (in place)."""
    bf = df["breastfeeding"].to_numpy() if "breastfeeding" in df else None
    p_death = pdeath(
        world, params,
        vulnerable=df.vulnerable.to_numpy(), smoke=df.smoke.to_numpy(),
        heavy_smoke=df.heavy_smoke.to_numpy(), soft_bedding=df.soft_bedding.to_numpy(),
        prone=df.prone.to_numpy(), ses=df.ses.to_numpy(), breastfeeding=bf,
    )
    df = df.copy()
    df["p_death"] = p_death
    df["death"] = (rng.random(len(df)) < p_death).astype(int)
    return df


def simulate_cohort(cfg: SimConfig) -> pd.DataFrame:
    """Generate one synthetic birth cohort as a DataFrame (one row per infant)."""
    cov = simulate_covariates(cfg)
    rng = np.random.default_rng(cfg.seed + 1)  # distinct stream for death draw
    return attach_hazard(cov, cfg.world, cfg.params, rng)
