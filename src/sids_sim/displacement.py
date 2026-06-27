"""Phase 7 -- parental-exhaustion / bed-sharing displacement (DESIGN.md sections 12, 14).

The supine recommendation has a DIRECT protective effect (no prone risk in the
crib) and an INDIRECT harmful effect: supine sleep is lighter -> more parental
exhaustion -> more unplanned bed/sofa sharing, whose risk dwarfs prone-in-a-crib.
This module models the competition and finds the exhaustion threshold above which
the recommendation goes net-harmful -- and shows that (a) abstinence framing
("never bed-share") makes it worse by pushing displacement into the sofa tail,
while harm-reduction framing helps, and (b) an enforced-supine soother (SNOO-like)
defuses the loop by cutting fragmentation.

    NetEffect(supine advice) = DirectProtection - DisplacementHarm

Magnitudes here are ILLUSTRATIVE, anchored to the section-14 table (location ORs)
and to qualitative bed-sharing epidemiology; they are not yet fit to a specific
dataset. The deliverable is the SHAPE: that a threshold exists and where the
framing/soother levers move it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .mediation import (Apportionment, Environment, FORM_SHARES, Profile,
                        abs_death_prob, prone_logodds, solve_unhab_factor)
from .scm import Params


# --------------------------------------------------------------------------- #
# parameters
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Family:
    """Drivers of exhaustion (separate from the infant's intrinsic SIDS profile)."""

    ses: float = 0.0           # higher = more advantaged (relief help, less shift work)
    no_support: int = 0        # 1 = solo / no second caregiver
    multiparity: int = 0       # 1 = twins or other young children competing for sleep


@dataclass(frozen=True)
class ExhaustionParams:
    intercept: float = 0.0
    b_frag: float = 0.9        # sleep fragmentation -> exhaustion (the key coupling)
    b_ses: float = 0.35        # advantage reduces exhaustion
    b_no_support: float = 0.6
    b_multiparity: float = 0.3
    # fragmentation by sleep arrangement (standardized units)
    frag_supine: float = 0.6   # back-sleep is lighter -> more night-waking
    frag_prone: float = -0.2   # prone sleeps deeper (the very thing that is dangerous)
    frag_soother: float = -0.9 # active soothing (rocking/white noise) cuts waking hard


@dataclass(frozen=True)
class DisplacementParams:
    alpha0: float = -4.0       # baseline log-odds of unsafe surface-sharing (rare for advantaged).
    # Anchored so the back-sleep campaign is net-beneficial at the POPULATION level
    # (bare-crib supine << historical prone), while still letting the most exhausted
    # families flip net-harmful (Phase 7). A higher alpha0 makes displacement dominate
    # the population average and wrongly implies the campaign cost lives.
    alpha_E: float = 1.1       # exhaustion -> displacement (the engine)
    alpha_abstinence: float = 0.4  # abstinence framing raises total sharing a bit too
    # excess-risk multipliers vs a safe supine crib (section 14.3 table)
    or_prepared_bed: float = 2.0
    or_unplanned_bed: float = 7.0
    or_sofa: float = 50.0
    # location mix GIVEN a displacement event, by framing
    loc_harm_reduction: tuple = (0.60, 0.30, 0.10)  # (prepared, unplanned, sofa)
    loc_abstinence: tuple = (0.15, 0.45, 0.40)      # abstinence pushes into the tail


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


# --------------------------------------------------------------------------- #
# the model
# --------------------------------------------------------------------------- #
def fragmentation(ep: ExhaustionParams, position: str, soother: bool) -> float:
    base = ep.frag_supine if position == "supine" else ep.frag_prone
    return base + (ep.frag_soother if soother else 0.0)


def exhaustion(fam: Family, ep: ExhaustionParams, position: str, soother: bool) -> float:
    return (
        ep.intercept
        + ep.b_frag * fragmentation(ep, position, soother)
        - ep.b_ses * fam.ses
        + ep.b_no_support * fam.no_support
        + ep.b_multiparity * fam.multiparity
    )


def p_displace(E: float, dp: DisplacementParams, abstinence: bool) -> float:
    return float(_sigmoid(dp.alpha0 + dp.alpha_E * E
                          + dp.alpha_abstinence * (1 if abstinence else 0)))


def displaced_risk(base_supine_risk: float, dp: DisplacementParams,
                   abstinence: bool) -> float:
    """Expected death risk of a displaced infant = safe-crib risk scaled by the
    framing-weighted location OR (the shared surface dominates the hazard)."""
    mix = dp.loc_abstinence if abstinence else dp.loc_harm_reduction
    ors = (dp.or_prepared_bed, dp.or_unplanned_bed, dp.or_sofa)
    weighted_or = sum(w * o for w, o in zip(mix, ors))
    return base_supine_risk * weighted_or


@dataclass
class PolicyOutcome:
    risk_supine_advice: float       # back-sleep recommended (the policy)
    risk_prone_historical: float    # uncontrolled prone permitted (pre-campaign counterfactual)
    risk_supine_plus_soother: float # back-sleep + enforced-supine soother (SNOO-like)
    risk_prone_engineered: float    # for reference: engineered prone-in-crib (section 16)
    net_advice_minus_prone: float   # >0 => supine advice net HARMFUL vs permitting prone
    p_displace_supine: float
    p_displace_prone: float
    p_displace_soother: float


def evaluate_family(p: Params, prof: Profile, fam: Family, *,
                    ep: ExhaustionParams | None = None,
                    dp: DisplacementParams | None = None,
                    abstinence: bool = True,
                    form: str = "G_gated") -> PolicyOutcome:
    """Compare the back-sleep recommendation against the realistic counterfactual it
    replaced -- permitting (uncontrolled) prone -- for one family, accounting for
    the exhaustion->displacement loop. Net > 0 means the recommendation backfired.
    """
    ep = ep or ExhaustionParams()
    dp = dp or DisplacementParams()

    appor = Apportionment.from_shares(p.w_prone, FORM_SHARES[form])
    unhab = solve_unhab_factor(appor)
    hist = Environment(breathable=False, cool=False, habituated=True)
    eng = Environment(breathable=True, cool=True, habituated=True)

    base_supine = abs_death_prob(p, prof, 0.0)
    base_prone_hist = abs_death_prob(p, prof, prone_logodds(appor, hist, unhab))
    base_prone_eng = abs_death_prob(p, prof, prone_logodds(appor, eng, unhab))
    d_risk = displaced_risk(base_supine, dp, abstinence)

    def policy_risk(position, soother, crib_risk):
        E = exhaustion(fam, ep, position, soother)
        pD = p_displace(E, dp, abstinence)
        return (1 - pD) * crib_risk + pD * d_risk, pD

    r_supine, pD_s = policy_risk("supine", False, base_supine)
    r_prone, pD_p = policy_risk("prone", False, base_prone_hist)
    r_soother, pD_so = policy_risk("supine", True, base_supine)
    r_prone_eng, _ = policy_risk("prone", False, base_prone_eng)

    return PolicyOutcome(
        risk_supine_advice=r_supine,
        risk_prone_historical=r_prone,
        risk_supine_plus_soother=r_soother,
        risk_prone_engineered=r_prone_eng,
        net_advice_minus_prone=r_supine - r_prone,
        p_displace_supine=pD_s,
        p_displace_prone=pD_p,
        p_displace_soother=pD_so,
    )


def solve_exhaustion_threshold(p: Params, prof: Profile, *,
                               driver: str = "no_support_scan",
                               abstinence: bool = True,
                               ep: ExhaustionParams | None = None,
                               dp: DisplacementParams | None = None,
                               form: str = "G_gated") -> dict:
    """Sweep an exhaustion driver and find where supine advice flips to net-harmful.

    We scan a continuous exhaustion shift (extra log-odds added via a synthetic
    'no_support'-like axis using ses as the dial: lower ses = more exhausted) and
    report the ses level at which net crosses zero, under the given framing.
    """
    ep = ep or ExhaustionParams()
    dp = dp or DisplacementParams()
    ses_grid = np.linspace(2.0, -2.5, 120)   # advantaged -> deprived
    nets = []
    crossing = None
    for s in ses_grid:
        # scan a SOLO parent (no_support=1) so the SES axis spans the flip region;
        # a fully-supported family rarely reaches the exhaustion needed to flip.
        fam = Family(ses=float(s), no_support=1)
        out = evaluate_family(p, prof, fam, ep=ep, dp=dp, abstinence=abstinence, form=form)
        nets.append(out.net_advice_minus_prone)
        if crossing is None and out.net_advice_minus_prone > 0:
            crossing = float(s)
    return {
        "abstinence": abstinence,
        "ses_at_flip": crossing,   # None => supine advice net-protective across the range
        "net_at_most_advantaged_per_1000": nets[0] * 1000.0,
        "net_at_most_deprived_per_1000": nets[-1] * 1000.0,
    }
