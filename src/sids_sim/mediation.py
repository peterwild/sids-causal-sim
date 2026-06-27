"""Phase 4.5 -- the linchpin challenge-toggle experiment (DESIGN.md sections 11, 17, 18).

The earlier phases established THAT prone is causal. This phase asks the question
Pete actually cares about: *through what* does it act, and how much of it can you
engineer away at home?

We take the single calibrated prone term `w_prone` (the whole direct effect, on the
death log-odds scale) and **decompose** it into mechanism channels:

    w_prone  =  b_rebr      # rebreathing CO2 microenvironment   -- removable (breathable surface)
              + b_therm     # thermal load                       -- removable (cool room)
              + b_obstr     # positional airway obstruction       -- NOT removable while prone
              + lambda_ar   # free-standing arousal hazard        -- "Form A"; Horne anchor says ~0
              + b_endo      # prone-raised endogenous autonomic events -- "Form H"; NOT removable

Key invariant: in a HISTORICAL crib (not breathable, not cool, habituated sleeper)
all channels are present at face value, so the decomposed contribution reproduces
`w_prone` exactly -- the Phase-2 calibration (prone OR ~3.2) is preserved untouched.

The experiment then toggles the environment:
  * breathable surface -> zeroes b_rebr
  * cool room          -> zeroes b_therm
and reports the residual excess ABSOLUTE risk that survives, decomposed into
removable vs irreducible. Because the engineered-prone cell is unobserved in the
real data (breathable mattresses postdate the studies), we never report a point
estimate -- we report a BAND across competing functional forms (G / A / H) plus a
"form E-value": how large the free-standing arousal term `lambda_ar` would have to
be to push the engineered residual above a decision threshold. If that required
value contradicts the no-baseline-derangement data (Horne 2001: prone impairs
arousal "with no clinically significant cardiorespiratory change"), the
engineered-prone-is-low-risk conclusion is robust.

The unaccustomed-prone spike (OR ~19) calibrates the habituation amplifier and is
the discriminator that the effect is GATED (challenge x response-failure), not
additive: a usually-supine baby rolled prone has no head-turn practice, so the
*escapable* challenges (rebreathing, obstruction) explode -- the additive arousal
term cannot produce that spike.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .scm import Params, World, _sigmoid


# --------------------------------------------------------------------------- #
# Mechanism apportionment of the calibrated w_prone
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Apportionment:
    """Split of the calibrated prone log-odds effect into mechanism channels.

    Values are absolute log-odds contributions (they sum to w_prone in a
    historical crib). Build via `from_shares` to keep the sum pinned to w_prone.
    """

    b_rebr: float       # rebreathing      (removable: breathable surface)
    b_therm: float      # thermal load     (removable: cool room)
    b_obstr: float      # airway obstruction (irreducible while prone)
    lambda_ar: float    # free-standing arousal hazard (Form A; ~0 per Horne)
    b_endo: float       # prone-raised endogenous autonomic events (Form H; irreducible)

    def total(self) -> float:
        return self.b_rebr + self.b_therm + self.b_obstr + self.lambda_ar + self.b_endo

    @classmethod
    def from_shares(cls, w_prone: float, shares: dict[str, float]) -> "Apportionment":
        s = sum(shares.values())
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"shares must sum to 1.0, got {s}")
        return cls(
            b_rebr=w_prone * shares.get("rebr", 0.0),
            b_therm=w_prone * shares.get("therm", 0.0),
            b_obstr=w_prone * shares.get("obstr", 0.0),
            lambda_ar=w_prone * shares.get("arousal", 0.0),
            b_endo=w_prone * shares.get("endo", 0.0),
        )


# Three competing functional forms, each resting on a stated calibration anchor.
# Shares are of the total calibrated prone effect. See DESIGN.md section 18.5.
FORM_SHARES = {
    # Pete's hypothesis: prone acts almost entirely through engineerable challenges;
    # the free-standing arousal term is ~0 (Horne: no baseline derangement).
    "G_gated": {"rebr": 0.55, "therm": 0.12, "obstr": 0.18, "arousal": 0.00, "endo": 0.15},
    # "prone is intrinsically dangerous": a large free-standing arousal hazard that
    # survives any environment. Contradicted by the no-derangement data, included
    # as the adversarial bound.
    "A_additive": {"rebr": 0.30, "therm": 0.08, "obstr": 0.15, "arousal": 0.40, "endo": 0.07},
    # gated, but prone meaningfully raises endogenous autonomic events (HRV/BP
    # shifts) -> a non-engineerable residual without a free-standing arousal term.
    "H_endo": {"rebr": 0.40, "therm": 0.10, "obstr": 0.18, "arousal": 0.00, "endo": 0.32},
}


@dataclass(frozen=True)
class Environment:
    """Home sleep environment toggles."""

    breathable: bool = False   # breathable mattress -> kills rebreathing channel
    cool: bool = False         # cool room           -> kills thermal channel
    habituated: bool = True    # False = unaccustomed (rolled prone, no head-turn practice)


@dataclass(frozen=True)
class Profile:
    """Infant/family covariate profile (a point on the risk manifold)."""

    smoke: int = 0
    heavy_smoke: int = 0
    soft_bedding: int = 0
    ses: float = 0.0           # higher = more advantaged

    @classmethod
    def low_risk(cls) -> "Profile":
        # term, non-smoking household, firm/bare crib, advantaged
        return cls(smoke=0, heavy_smoke=0, soft_bedding=0, ses=1.0)


# --------------------------------------------------------------------------- #
# Core mechanism -> hazard plumbing
# --------------------------------------------------------------------------- #
def base_stressors(p: Params, prof: Profile) -> float:
    """Non-prone stressor log-odds for a profile (mirrors scm._death_logodds)."""
    return (
        p.w_smoke * prof.smoke
        + p.w_heavy_extra * prof.heavy_smoke
        + p.w_bedding * prof.soft_bedding
        - p.w_ses * prof.ses
    )


def prone_logodds(appor: Apportionment, env: Environment, unhab_factor: float) -> float:
    """Effective prone contribution to the death log-odds under an environment.

    Habituation amplifies only the *escapable* challenges (rebreathing,
    obstruction) -- the ones a baby clears by turning/lifting its head. A baby with
    no practice cannot, so these explode for the unaccustomed sleeper. The thermal,
    free-standing arousal, and endogenous terms are not head-turn-escapable, so the
    amplifier does not touch them.
    """
    mult = 1.0 if env.habituated else unhab_factor
    rebr = 0.0 if env.breathable else appor.b_rebr
    therm = 0.0 if env.cool else appor.b_therm
    escapable = mult * (rebr + appor.b_obstr)
    non_escapable = therm + appor.lambda_ar + appor.b_endo
    return escapable + non_escapable


def abs_death_prob(p: Params, prof: Profile, prone_contrib: float,
                   p_vuln: float | None = None) -> float:
    """Population absolute death probability for a profile, integrating over the
    unknown vulnerability phenotype (triple-risk world).

    Non-vulnerable infants sit at the near-immune floor; vulnerable infants carry
    the full predictor. We integrate because V is unmeasurable in advance -- the
    decision-relevant risk is the marginal over V.
    """
    pv = p.p_vulnerable if p_vuln is None else p_vuln
    eta_vuln = (
        p.hazard_intercept
        + p.triple_vuln_bonus
        + base_stressors(p, prof)
        + prone_contrib
    )
    risk_vuln = _sigmoid(eta_vuln)
    risk_nonvuln = _sigmoid(p.triple_nonvuln_floor)
    return pv * risk_vuln + (1.0 - pv) * risk_nonvuln


def delta_abs_risk(p: Params, prof: Profile, appor: Apportionment,
                   env: Environment, unhab_factor: float,
                   p_vuln: float | None = None) -> float:
    """Excess absolute death probability of prone over supine for this profile and
    environment. Supine is the reference: no prone contribution at all.
    """
    prone = abs_death_prob(p, prof, prone_logodds(appor, env, unhab_factor), p_vuln)
    supine = abs_death_prob(p, prof, 0.0, p_vuln)
    return prone - supine


# --------------------------------------------------------------------------- #
# Calibration of the habituation amplifier to the unaccustomed-prone spike
# --------------------------------------------------------------------------- #
def solve_unhab_factor(appor: Apportionment, target_or: float = 19.0) -> float:
    """Find the habituation amplifier so an unaccustomed prone sleeper reproduces
    the OR ~19 spike in a historical crib.

    For a rare outcome OR ~= exp(prone log-odds contribution). The amplifier scales
    only the escapable challenges; solve so the unaccustomed contribution hits
    ln(target_or). If the spike is unreachable by amplifying challenges alone (i.e.
    the escapable share is ~0), returns inf -- a signal the form cannot produce the
    spike, which itself argues against that apportionment.
    """
    escapable = appor.b_rebr + appor.b_obstr
    non_escapable = appor.b_therm + appor.lambda_ar + appor.b_endo
    target = np.log(target_or)
    if escapable <= 1e-9:
        return float("inf")
    return max(1.0, (target - non_escapable) / escapable)


# --------------------------------------------------------------------------- #
# The "form E-value": how much free-standing arousal hazard would it take?
# --------------------------------------------------------------------------- #
def form_evalue_lambda(p: Params, prof: Profile, w_prone: float,
                       env: Environment, threshold_per_1000: float,
                       p_vuln: float | None = None) -> dict:
    """Minimum free-standing arousal share that would push the ENGINEERED-prone
    excess absolute risk above a decision threshold.

    We hold the total calibrated effect fixed at w_prone and shift mass out of the
    removable rebreathing channel into the free-standing arousal term, keeping a
    fixed obstruction/endo floor. As lambda rises, the engineered residual rises.
    Report the share at which it crosses the threshold; compare to the Horne anchor
    (~0). A large required share => conclusion robust.
    """
    obstr_share, endo_share = 0.18, 0.15  # fixed irreducible floor (Form-G-like)
    floor = obstr_share + endo_share
    thr = threshold_per_1000 / 1000.0

    def residual(arousal_share: float) -> float:
        rebr_share = max(0.0, 1.0 - floor - arousal_share)
        appor = Apportionment.from_shares(
            w_prone,
            {"rebr": rebr_share, "obstr": obstr_share, "arousal": arousal_share,
             "endo": endo_share, "therm": 0.0},
        )
        unhab = solve_unhab_factor(appor)
        return delta_abs_risk(p, prof, appor, env, unhab, p_vuln)

    shares = np.linspace(0.0, 1.0 - floor, 400)
    crossed = None
    for s in shares:
        if residual(s) >= thr:
            crossed = s
            break
    return {
        "threshold_per_1000": threshold_per_1000,
        "required_arousal_share": crossed,   # None => never crosses even at max
        "residual_at_zero_lambda_per_1000": residual(0.0) * 1000.0,
        "residual_at_max_lambda_per_1000": residual(1.0 - floor) * 1000.0,
    }


# --------------------------------------------------------------------------- #
# Top-level driver: the conditional absolute-risk band
# --------------------------------------------------------------------------- #
def run_linchpin(p: Params, prof: Profile | None = None,
                 thresholds=(0.1, 0.5), p_vuln: float | None = None) -> dict:
    """Produce the section-18 deliverable for a calibrated triple-world Params.

    Returns, per functional form, the prone excess absolute risk in a historical
    vs fully-engineered environment, the removable vs irreducible split, and the
    form E-value band.
    """
    prof = prof or Profile.low_risk()
    w_prone = p.w_prone
    historical = Environment(breathable=False, cool=False, habituated=True)
    engineered = Environment(breathable=True, cool=True, habituated=True)

    out = {"w_prone": w_prone, "profile": prof, "forms": {}}
    for name, shares in FORM_SHARES.items():
        appor = Apportionment.from_shares(w_prone, shares)
        unhab = solve_unhab_factor(appor)
        d_hist = delta_abs_risk(p, prof, appor, historical, unhab, p_vuln)
        d_eng = delta_abs_risk(p, prof, appor, engineered, unhab, p_vuln)
        out["forms"][name] = {
            "apportionment": appor,
            "unhab_factor": unhab,
            "unaccustomed_or_check": float(np.exp(prone_logodds(
                appor, Environment(habituated=False), unhab))),
            "excess_historical_per_1000": d_hist * 1000.0,
            "excess_engineered_per_1000": d_eng * 1000.0,
            "removable_fraction": 1.0 - (d_eng / d_hist) if d_hist > 0 else float("nan"),
        }

    out["form_evalues"] = {
        f"thr_{t}_per_1000": form_evalue_lambda(p, prof, w_prone, engineered, t, p_vuln)
        for t in thresholds
    }
    return out
