# SIDS Causal Simulation — Design Protocol

**Question (plain):** Is sleeping prone (on the stomach) a risk *by itself* — i.e.
for a baby with none of the other dangers present (no maternal smoking, adequate
SES, firm bedding, own crib, breastfed) — or does prone only *look* dangerous
because it travels in the company of those other factors?

**Status:** Design locked. Discrete-three-worlds approach first; blended/fitted
mixing weights deferred to a later phase.

---

## 1. Why a simulation can and cannot answer this

A simulation is a world we author. If we program prone to be causal, the sim
"finds" causation; if we program it as a pure marker, the sim "finds" that. So a
simulation **cannot prove** the real-world cause on its own.

What it *can* do is **falsification**. We ask:

> Can we build a world where prone has **zero independent effect** and still
> reproduce *every* real historical number (the calibration targets in §5)?

- If **no** harmless-prone world can match reality → "prone is just a marker" is
  ruled out → strong evidence prone is causal on its own.
- If **yes** → the historical data alone cannot separate cause from correlation,
  and we must report how much of the signal is genuinely causal vs. confounded.

The deliverable is therefore a **bounded** statement, not a yes/no:
"to match history, prone must carry ≥ X% of its risk directly; an unmeasured
confounder would need strength E to nullify it."

---

## 2. Competing hypotheses (the three worlds)

| World | Name | Mechanism |
|-------|------|-----------|
| **H1** | Prone is a strong direct cause | Position acts on the causal path to death (rebreathing/CO₂, thermal load, arousal failure), independent of *who* sleeps prone. |
| **H2** | Prone is largely a marker | Most of the observed OR is carried by the bundle prone travels in (smoking, SES, soft bedding, bed-sharing, no breastfeeding). Position is mostly a correlate of social adversity. |
| **H3** | Triple-risk interaction (primary outcome model) | Prone is an exogenous stressor that only matters given a latent vulnerable infant in the critical developmental window. Death = f(vulnerability × window × stressor). Prone is removable but not "principal" in a variance sense. |

These are not mutually exclusive in reality; the discrete phase runs them as
separate scenarios and asks which reproduce the calibration targets. A later
phase fits a continuous mixing weight.

---

## 3. The two estimands

| | Estimand | Method | Answers |
|---|----------|--------|---------|
| **A. Causal effect** | Conditional ATE: risk(prone) − risk(supine) for a *fixed* infant | do-operator on the SCM; back-door adjustment; IPW; **E-value** sensitivity bounds | "Does the position itself kill, or is it the company it keeps?" |
| **B. Variance share** | Share of outcome-liability variance attributable to each factor | Shapley/LMG R² decomposition on the latent liability **+** PCA on the *risk-factor matrix* | "Is position the largest axis of risk, or does it co-load with the adversity bundle?" |

**Note on "PCA":** PCA decomposes variance *among predictors*, not variance *in
the outcome*. Prediction to test: prone will **not** be its own axis — it loads
onto a "social-adversity" component with smoking, SES, bedding. That eigenvector
*is* the correlation-vs-causation story. For "largest share of outcome variance"
we use a Shapley/LMG decomposition of the latent liability. Report both; they are
different questions. The variance share is **era-dependent**: removing prone from
the population mechanically raises smoking's share (50%→80% historically), so
"principal component" is a property of the population, not of the factor.

---

## 4. Structural causal model (the DAG)

```
        SES ──────────┬───────────┐
         │            │           │
         ▼            ▼           ▼
     Smoking      Bedding     Prone choice ◄── Era/Advice (time-varying)
         │         (soft)         │                    │
         │            │           │            (healthy-adherer gate)
         ▼            ▼           ▼
   ┌─────────────────────────────────────┐
   │   Exogenous stressor load (S)        │
   └─────────────────────────────────────┘
                     │
   Latent vulnerability (V) ──┐         Developmental window (W)
   (brainstem 5-HT phenotype) │              │
                              ▼              ▼
                    ┌────────────────────────────┐
                    │  Death hazard = g(V, W, S)  │  ← H3 multiplicative interaction
                    └────────────────────────────┘
                                 │
                                 ▼
                    Observed cause-of-death label
                    (SIDS / suffocation / unexplained)  ← optional misclassification layer
```

Load-bearing structural choices:

- **`Era → Prone choice`** is time-varying. The **healthy-adherer gate** makes
  post-campaign prone-choice conditional on high adversity. This is the mechanism
  that must reproduce the OR *rising* after the campaign — the single sharpest
  discriminating test (only H2/H3 + adherer-gating can do it; pure H1 cannot).
- **`V` (vulnerability)** is latent, population prevalence ~35–40% (calibrated to
  33–42% control binding-deficit rate), enriched to ~80% in deaths by `g`.
- **Outcome misclassification** is an optional switch (default OFF). Used to stress
  how much of the population "decline" is diagnostic transfer vs. lives saved.

---

## 5. Calibration targets (the "hybrid" — the DGP is rejected unless it matches these)

| # | Target | Value | Source |
|---|--------|-------|--------|
| 1 | Prone in cases | 84% (1991–93) → 48.5% (1996–2008) | Risk-factor-changes (PMC3356149) |
| 2 | Prone in controls | ~50%+ pre → ~25% (King County 24.6%) | King County 1996 |
| 3 | US SIDS rate | 1.2 → 0.4 / 1000 | CDC / Back-to-Sleep reviews |
| 4 | Adjusted prone OR | ~3–5, **and the RISE** 2.86 → 3.93 across the campaign | Gilbert 2005 (2.95→6.91); pooled RR review |
| 5 | Smoking OR | ~2, dose-response to ~12.7 (>20/day); **attributable risk 50%→80%** across era | PMC545061 |
| 6 | Vulnerability phenotype | ~33–42% controls / ~79–88% cases low 5-HT binding | Kinney serotonin hypothesis (PMC6934437) |

**Falsification gates:** Targets #4 (the OR *rise*) and #5 (smoking's rising
share) are the discriminators. A pure-H1 world cannot make the OR rise as
exposure becomes rarer; it requires adherer-gating + confounding (H2/H3).

---

## 6. Experimental procedure

1. **Forward-simulate** each world (H1/H2/H3) → synthetic 1987–2008 cohorts.
2. **Re-run the historical study design on top** — simulate a retrospective
   case-control study *with* recall bias and control-selection bias baked in —
   and compare the OR the flawed design *would have reported* vs. the *true*
   planted do-effect. Quantifies how much the original designs mislead.
3. **Recover the effect** with modern tools: back-door adjustment, IPW, then the
   **E-value** (how strong must unmeasured confounding be to nullify prone?).
4. **Decompose** (Shapley R² + PCA) under each world, per era.
5. **Discriminate:** which world(s) reproduce all six calibration targets at once.

---

## 7. Success criteria

- A bounded causal statement: "to match history, ≥ X% of the prone OR must be
  direct-causal; a pure-confounding world is rejected because it cannot reproduce
  [target]."
- A causal effect estimate **with sensitivity bounds** (E-value), not a point claim.
- A variance decomposition showing whether prone is its own axis or part of the
  adversity bundle, and how that share **shifts across eras**.

---

## 8. The "unaccustomed prone" external check

Babies usually placed supine but placed/found prone *once* show OR ~18–20, far
above habitual prone sleepers. These are often low-risk infants, so a
pure-marker (H2) world cannot explain the spike — it is a physiological
fingerprint (a baby with no practice turning its head cannot clear rebreathed
air). The simulation should reproduce this stylized fact as an additional gate.

---

## 9. Limitations (state up front, always)

- No RCT can ever exist; everything rests on the credibility of the planted DGP.
  Garbage parameters → garbage conclusions. Calibration discipline (§5) is the
  whole ballgame.
- "SIDS" is a heterogeneous wastebasket diagnosis. `V` is a modeling convenience,
  not a measured variable.
- A favourable falsification result bounds the *innocent* explanation; it does not
  upgrade observational evidence to experimental certainty.

---

## 10. Roadmap

- [x] Phase 0 — Research + design protocol (this document)
- [ ] Phase 1 — SCM forward simulator (`src/sids_sim/`), 3 discrete worlds
- [ ] Phase 2 — Calibration harness against §5 targets
- [ ] Phase 3 — Biased case-control replication + modern estimators + E-value
- [ ] Phase 4 — Variance decomposition (Shapley + PCA), per era
- [x] **Phase 4.5 — Mediation decomposition (§11) + linchpin challenge-toggle experiment (§17–§18): conditional absolute-risk surface, removable vs irreducible**
- [x] Phase 5 — Discrimination report (`scripts/phase5_discrimination.py`); write-up in FINDINGS §6
- [x] Phase 6 — Continuous mixing-weight fit (`scripts/phase6_mixing.py`); write-up in FINDINGS §7.5
- [x] **Phase 7 — Exhaustion/displacement sub-model (§12, §14): `scripts/phase7_displacement.py`; write-up in FINDINGS §7**
- [x] **Phase 8 — Home-protocol comparison (§15–§16): `scripts/phase8_protocols.py`; capstone write-up in FINDINGS §8 + bottom line**
- [x] **Phase 3.5 — Biased case-control replication (§6 step 2): `scripts/phase35_bias.py`; FINDINGS §3.5**
- [x] **Phase 9 — Era-model closure (smoking decline + breastfeeding; additive SCM knobs): `scripts/phase9_era.py`; FINDINGS §9 (death-rate gap closes; PAF-rise remains open)**

---

## 11. Mediation decomposition — "is prone a misnomer for rebreathing?"

**The question (distinct from §1–2).** §1–2 ask *cause vs. marker* (confounding).
This asks, *granting prone is causal*, **through what does it act, and is that
mediator removable?** If prone's effect were *fully mediated* by a rebreathing
microenvironment, then engineering that environment away (breathable mattress,
breathable sheets, no soft objects) would zero the prone risk — and "stomach
sleeping" would be a misnomer for "rebreathing." This is **mediation, not
confounding.**

**SCM extension.** Split the `Prone → S` arrow into competing mediators:

```
Prone ──► Rebreathing(surface) ──► S        ← controllable (surface/objects)
      └─► DirectProne ───────────► S        ← NOT surface-controllable
            (arousal suppression, positional airway obstruction, autonomic/thermal)
```

- `Rebreathing` is gated by a new `Surface` node (firm/soft historically; add a
  `breathable` level for counterfactual queries the historical data never sampled).
- `DirectProne` carries the surface-independent routes. **Positional airway
  obstruction is the decisive one**: a chin-tucked / face-straight-down airway is
  occluded regardless of mattress porosity, so it cannot route through the
  rebreathing arm by construction. **It is positional + developmentally transient,
  NOT a fixed anatomical defect** — it arises from the *infant-specific* combination
  of a large occiput, proportionally large tongue, high/compliant (floppy) larynx,
  and immature head/neck motor control: a young infant whose neck flexes
  chin-to-chest cannot lift/reposition to clear it. As neck strength, head control,
  and airway rigidity mature, the same position stops occluding — which is *why
  adults and older children sleep prone safely and why this is not a permanent
  trait*. Cleanest real-world evidence the pathway is real and surface-independent:
  the **inclined-sleeper deaths (Fisher-Price Rock 'n Play, recalled 2019 after
  dozens of deaths)** — chin-to-chest positional asphyxia on a breathable,
  non-suffocating surface [cite: CPSC Rock 'n Play recall 2019]. The implication
  *cuts toward the §16 thesis, not against it*: the transient window of anatomical
  vulnerability **coincides with** the SIDS risk window (~0–6mo), so "protect during
  the window, relax after" is the anatomically-correct policy, not an arbitrary one.

**Estimand.** Natural direct effect (NDE) vs. natural indirect effect (NIE) of
prone, i.e. the **proportion mediated** by rebreathing. Report as a bound:
*"to match history, ≥ Y% of the prone effect must act outside the rebreathing
path; a fully-controllable-rebreathing world is rejected because it cannot
reproduce [gate]."* Direct analog of the §3 E-value, one level down.

**Falsification gates (the discriminators).**
1. **Firm-surface residual.** Prone OR stays elevated on firm/non-soft surfaces. A
   100%-rebreathing-mediated DGP cannot hold this while zeroing prone on a
   breathable surface.
2. **Unaccustomed-prone spike (§8, OR ~18–20).** If *all* of this is forced
   through the rebreathing arm, the implied CO₂ parameters overshoot the bench
   bounds (Kemp & Thach surrogate studies). The spike is partly motor/arousal
   immaturity — a baby that never learned the head-turn — which is `DirectProne`.

**The honest limitation that motivates this.** The cell *prone + engineered-
breathable environment* is **essentially unobserved**: breathable mattresses
(~2010s) postdate the §5 case-control era (1987–2008), and there is **no death-
outcome evidence** for them — only surrogate CO₂-dispersal bench data. The
historical studies measured soft-vs-firm, soft objects, face/head-covering
(rebreathing proxies), never engineered breathability. So the counterfactual is
recoverable *only* in the sim, under an explicit DGP — never from the data alone.

---

## 12. Holistic competing-risks decision ledger (deferred)

The causal/mediation work answers "does/how-does prone kill." The **decision**
("supine vs. prone for a given infant") is a competing-risks, expected-utility
question that the SCM alone does not answer. Build a separate ledger.

**The other side of the ledger — costs of supine.**

| Cost | Severity / reversibility | Notes |
|------|--------------------------|-------|
| Lighter, more fragmented sleep | low / reversible | **This is the protective mechanism, not a side effect** — easier arousal is *why* supine is safer. Modest effect size. |
| Plagiocephaly / brachycephaly | low / mostly reversible | Rose post-Back-to-Sleep; cosmetic, tummy time mitigates, helmet in a minority. |
| Transient gross-motor delay | low / self-resolving | Rolling/sitting/crawling slightly later; caught up by ~18mo. |
| Torticollis | low / treatable | Positional-preference neck tightness. |
| Aspiration on spit-up | **negligible** | Original *pro-prone* rationale; **disproven** — supine airway anatomy protects. |
| **Bed-sharing displacement** | **high / catastrophic** | The underrated one: lighter supine sleep → exhausted parents → couch/armchair/bed-sharing, a *larger* SIDS risk. Behavioral feedback loop, belongs in the SCM as a policy-induced arrow. |

**Bed-sharing displacement — promote to a structural arrow, not a footnote.**
This is the one mechanism where the recommendation can *net increase* deaths, and
it is observed repeatedly in practice (anecdotally common among new parents). Model
it as a **policy-induced behavioral feedback loop in the SCM (§4)**, not just a
ledger cost:

```
Advice(supine) ─► lighter/fragmented infant sleep ─► parental exhaustion ─►
      ─► unplanned bed-sharing / couch / armchair sleep ─► S (large ↑)
```

- **Why it can dominate.** Sofa/armchair co-sleeping carries some of the highest
  ORs in the entire literature (often >50), and *unplanned/unsafe* bed-sharing by
  an exhausted parent is far more dangerous than the prone-in-crib risk it was
  meant to avoid. So the arrow can flip the sign of the intervention's net effect
  for the exhausted-parent subpopulation.
- **It is a confounding *and* a mediation story for policy.** The supine
  recommendation has a *direct* protective effect and an *indirect* harmful effect
  through this loop; the net is a competition between them. Decompose exactly like
  §11 (NDE vs NIE), but for the **advice**, not the position:
  *"the supine recommendation's net effect = direct protection − displacement harm;
  for parents with exhaustion propensity ≥ θ the net can go positive (harmful)."*
- **Calibration hook.** Needs a parental-exhaustion latent and a displacement
  hazard tied to it; calibrate displacement ORs to the sofa/bed-sharing literature.
  Predicted gate: a world without the displacement arrow will *understate*
  real-world SUID in the post-campaign era among low-SES/high-exhaustion strata —
  i.e. it helps explain residual deaths that pure prone-reduction cannot.
- **Real-policy implication this surfaces.** "Never bed-share" framed as
  abstinence may *raise* risk vs. harm-reduction framing (how to bed-share least
  dangerously when it will happen anyway) — a genuinely contested public-health
  debate the model can illuminate without resolving.

**On "infants are underslept."** Calibrate down: the supine→lighter-sleep effect
is real but small, and the leap from it to clinically meaningful chronic infant
sleep deprivation (and downstream obesity/cognition/behavior associations) is
**weakly evidenced and heavily confounded** for the supine-vs-prone contrast
specifically. Do not import the general "short sleep → bad outcomes" literature
as if it applied cleanly here.

**The spine of the decision — ruin asymmetry.** Work in **absolute** risk, not
OR. Baseline SIDS ≈ 0.4/1000; even a 4× prone effect ≈ ~1.6/1000 (0.16%). The
supine costs are common-but-minor-and-reversible; the averted outcome is
**rare-but-catastrophic-and-irreversible** (an absorbing state). Under any
sane utility function the irreversible tail dominates — you do not optimize
expected sleep quality against a ruin risk. This is why population advice is
unambiguous *despite* the small absolute risk.

**Why the mediation result (§11) is the only thing that can move this.** The
ledger tips toward "prone is defensible for this infant" *only if* §11 finds the
controllable (rebreathing) arm carries most of the effect — i.e. you can shrink
the catastrophic-tail probability while keeping the sleep/development benefit.
Absent a large controllable arm, ruin asymmetry settles it. The two questions are
linked: **§11 is the precondition for §12 being a live trade-off at all.**

**What else to model holistically.**
- **Competing risks / NNT vs NNH.** Number-needed-to-back-sleep to prevent one
  death vs. number-needed-to-harm for a helmet, etc. Model all-cause infant
  mortality + morbidity, not SIDS in isolation.
- **Severity × reversibility weighting**, not probability alone — death and a
  helmet are not commensurable on a probability axis.
- **Time-varying calculus.** SIDS risk peaks 2–4mo, ~90% before 6mo, and drops
  once the infant rolls independently (AAP: no repositioning needed once it rolls
  both ways unaided). The *cost* of supine (sleep, motor) bites later — when the
  *risk* has already fallen. The time structure largely dissolves the trade-off.
- **Heterogeneity in `V`.** Risk is wildly unequal across the latent vulnerability
  phenotype; if low-`V` infants were identifiable the individual calculus would
  differ — but no test exists, so the precautionary default wins under uncertainty
  about *your* infant's `V`. Population-optimal ≠ individual-optimal, and we can't
  locate the individual.

---

## 13. NICU prone as a boundary-condition check (external validity)

The NICU looks like it contradicts the guidance — sick/preterm infants are
deliberately placed **prone** — and resolving it is the real-world existence
proof of the §11/§12 logic. Use it as an external check, like §8.

**Two facts that look contradictory:**
1. Prone in the NICU has a *genuine medical benefit*: a Cochrane review finds
   prone slightly improves oxygenation / pO₂ / SpO₂ in mechanically ventilated
   neonates (small magnitude, short-term). Preterm lungs gain V/Q matching,
   lung mechanics, thoracoabdominal synchrony, fewer apnea/brady events.
2. Yet the AAP *also* says: keep NICU infants **supine from 32 weeks PMA**,
   model safe home sleep before discharge, and any prone period requires
   **continuous cardiorespiratory + SpO₂ monitoring**, with benefit explicitly
   required to outweigh SUID risk.

**The resolution (and why it is not a contradiction).** The lethal SIDS pathway
is *unwitnessed, unrescued* asphyxia/bradycardia — the vulnerable infant fails to
arouse and no one intervenes. In the NICU that pathway is **neutralized by
substitution**: external monitoring + staff replace the infant's own protective
arousal (the §11 `DirectProne` arousal arm), and a firm flat surface removes the
rebreathing arm. The NICU does not "accept the SIDS risk because the benefit is
bigger" — **it removes the risk, then collects the benefit.**

**Why this matters for the model.** This is the §12 ruin-asymmetry frame
instantiated: monitoring converts the **absorbing/irreversible** death state into
a **rescuable** one. Once the catastrophic tail is no longer absorbing, prone
becomes a normal cost-benefit optimization — which is exactly the condition §12
says must hold for the trade-off to be live. The mandated **transition to supine
before discharge** is the system itself acknowledging the calculus flips back the
moment monitoring is withdrawn. The naturalistic-fallacy trap to avoid: "babies
sleep better prone / may prefer it" (true — prone measurably lowers arousability
and lengthens sleep) does **not** imply prone is safe; ancestral infant sleep was
*on a monitoring caregiver's body*, not alone on a soft mattress — the preference
may be ancestral while the safe context for expressing it is gone.

**As a sim check:** an NICU-style scenario (prone + firm surface + an external
"rescue" node that interrupts the death hazard on alarm) should drive prone's net
effect toward null — reproducing why prone is permissible there. If the DGP can't
produce that, the monitoring/arousal mechanism is mis-specified.

---

## 14. Parameterization — parental exhaustion latent + displacement hazard

Formal spec for the §12 bed-sharing arrow. Goal: a structural sub-model where the
supine recommendation has a **direct protective** effect and an **indirect harmful**
effect through exhaustion → unsafe surface-sharing, and a soothing intervention
(§16) can attack both.

**14.1 Latent: parental exhaustion `E`.** Continuous, standardized to liability.

```
E_i = β0
    + β_frag · Fragmentation_i        # infant night-waking load (main driver)
    + β_ses  · LowSES_i               # less support / more shift work
    + β_sup  · NoPartnerSupport_i      # solo / no relief caregiver
    + β_mult · Multiparity_or_Twins_i
    + ε_E ,   ε_E ~ N(0, σ_E²)
```

- `Fragmentation_i` is **endogenous to position and soothing**:
  `Fragmentation = f(supine↑, prone↓, SNOO/white-noise/rocking↓, colic↑)`.
  This is the load-bearing coupling — it's *why* supine feeds the loop and *why*
  a soother breaks it. Anchor the supine→prone fragmentation gap to the arousal
  data (prone: ~3.5 vs supine ~9.7 awakenings; treat as ~2–3× more arousals
  supine) and the SNOO effect as a large reduction in awakenings (calibrate to
  vendor + independent sleep data, held skeptically — see §15).
- Suggested starting magnitudes (to be calibrated, not asserted): standardize all
  predictors; `β_frag ≈ 0.6`, `β_ses ≈ 0.3`, `β_sup ≈ 0.3`, `β_mult ≈ 0.2`.

**14.2 Displacement hazard (per sleep-period).** Probability the infant ends up on
an unsafe shared surface that night:

```
logit P(share_i) = α0
    + α_E      · E_i                       # exhaustion is the engine
    + α_advice · StrictAbstinenceFraming    # "never bed-share" → unplanned, unprepared
    + α_ses    · LowSES_i
    + α_norm   · CulturalCosleepNorm_i
```

Conditional on sharing, draw the **location**, because location dominates the OR:

```
Location | share ~ Categorical(
    prepared_adult_bed ,   # lowest excess risk
    unplanned_adult_bed ,  # higher (drowsy, soft bedding, no prep)
    sofa_or_armchair )     # catastrophic
```

Key asymmetry to preserve: the *abstinence* arrow (`α_advice`) **raises the share
of the sofa/unplanned tail** rather than total sharing — a parent who "would never"
bed-share but collapses on a couch at 4am is the worst cell. Harm-reduction framing
moves mass from sofa → prepared bed.

**14.3 Feed into the death hazard `g` (§4).** Multiply the exogenous stressor load
on share-nights by a location-specific factor calibrated to literature:

| Location | Excess-risk multiplier (calibration target) |
|----------|---------------------------------------------|
| Prepared adult bed, no modifiers | ~1–2× (contested; near-null for breastfed, non-smoking, sober) |
| Unplanned bed-share + modifiers (smoking/alcohol/soft bedding) | ~5–10× |
| **Sofa / armchair** | **>50×** (among the highest ORs in the literature) |

**14.4 The estimand this produces (advice-level mediation).**

```
NetEffect(advice = supine) = DirectProtection  −  DisplacementHarm
   DirectProtection ∝ removal of prone arms (§11)
   DisplacementHarm ∝ E[α_E · E] · location-weighted OR
```

Falsifiable prediction: there exists an exhaustion threshold `θ` such that for the
subpopulation with `E ≥ θ` (high fragmentation, low support, low SES), the **net
sign flips to harmful** under strict-abstinence framing. Reporting target:
*"the supine recommendation is net-protective overall but net-harmful for the top
q% most-exhausted, unsupported parents under abstinence framing; harm-reduction
framing shrinks that q to ~0."* This is the policy payload of the whole project.

---

## 15. Engineering the risk away at home — which arms, and with what

The NICU (§13) neutralizes the death tail with **firm surface + continuous
monitoring + trained rescue**. The home question is: *which of those substitutions
are actually available outside the NICU, and how good are the substitutes?* Map
each §11 arm to its best home control and its honest evidence grade.

| §11 arm | Home control | Evidence grade |
|---------|--------------|----------------|
| **Rebreathing** | Firm/breathable mattress, no soft objects/bedding, no bumpers, no loose swaddle | **Strong for firm + bare crib** (well-established epi). **Unproven for engineered-breathable** (surrogate CO₂-dispersal only; no mortality data — see §11). |
| **Positional airway obstruction** | Enforce supine; prevent roll-to-prone (swaddle-to-bassinet, §16) | Strong mechanistically; supine is the only proven lever. |
| **Arousal failure (self-rescue)** | *No good home substitute.* This is what the NICU monitor replaces. | See devices below — weak. |
| **Displacement (§14)** | Improve infant sleep to cut exhaustion; harm-reduction framing | Mechanistic; see §16. |

**Devices — the honest read.**

- **Home pulse-ox / cardiorespiratory monitors (Owlet Dream Sock / BabySat).**
  These are the *attempted* substitute for the NICU monitor on the arousal arm.
  Regulatory reality: Owlet's original Smart Sock was **pulled after a 2021 FDA
  warning letter** for marketing a medical device without clearance; the line
  returned as the OTC **Dream Sock** and the prescription **BabySat** (FDA-cleared
  2023). **Crucial caveat: no home monitor has ever been shown to reduce SIDS, and
  the AAP explicitly does *not* recommend home monitors to prevent SIDS.** Why the
  NICU monitor works and the sock is weaker: the NICU pairs the alarm with a
  *trained human who rescues within seconds*; the home sock pairs it with a
  sleeping, exhausted parent who must wake, orient, and act — a slower, less
  reliable rescue loop, plus false-alarm fatigue. It is a partial, unproven
  substitute for the arousal arm, **not** equivalent to NICU monitoring. Model it
  as a *probabilistic, latency-delayed rescue node* with rescue-success < 1 and
  parental-response latency drawn from a distribution — not as the NICU's
  near-deterministic rescue.
- **Breathable mattress (Newton-class).** Targets the rebreathing arm only;
  see §11 — reduces a surrogate, no mortality evidence, does nothing for the
  obstruction/arousal arms. Useful, not sufficient, not a license to prone.

**The synthesis:** at home you can largely neutralize **rebreathing** (firm/bare
crib) and **obstruction** (enforced supine), partially address **displacement**
(better sleep), but you **cannot** truly replace the NICU's rescue of the
**arousal** arm. So the home-optimal strategy is not "monitor prone like a NICU" —
it's "remove the arms you can and keep the baby supine so the arousal arm never has
to fire," which is exactly §16.

---

## 16. Working hypothesis (the punchline) — supine + active soothing through the high-risk window

**Claim to be tested and written up:** the home-optimal protocol is **back-sleep in
a sleep environment that (a) mechanically enforces supine and (b) actively improves
sleep quality, used through the high-SIDS-risk window (~0–6 months), then relaxed
once the infant rolls independently.** SNOO is the current instantiation of (a)+(b);
the claim is about the *mechanism*, not the brand.

**Why this resolves the whole thread — it attacks every arm at once:**

1. **Removes prone arms (§11).** The SNOO sleep-sack wings clip to the bassinet, so
   roll-to-prone is *physically impossible*. A 1,012-infant study reported a
   **91.5% reduction in unsafe stomach sleeping**. This directly kills the
   highest-risk cell — *secondary/unaccustomed prone* (§8, OR ~18–20), the baby who
   rolls over and can't get back.
2. **Breaks the displacement loop (§14).** Active soothing (rocking + white noise)
   *reduces* `Fragmentation`, which lowers exhaustion `E`, which lowers the
   unsafe-sharing hazard. This is the key move: it lets you keep the supine
   *safety* benefit **without** paying its sleep-quality cost in exhaustion — the
   one thing that otherwise feeds bed-sharing. It converts supine's chief downside
   into a non-issue.
3. **The time-window coincidence does the rest.** SIDS risk peaks 2–4 months and is
   ~90% over by 6 months; SNOO is used to ~6 months / until consistent rolling; and
   AAP says once an infant rolls *both ways unaided* you needn't reposition. So the
   period when you most need enforced supine is exactly the period the infant
   *can't* self-rescue and the device is in use. The cost of enforced supine
   (motor/sleep) bites *later* — after the device is retired and the risk has
   already collapsed (the §12 time-structure argument). **The trade-off largely
   dissolves on the calendar.**

**Honest limits (state these in the write-up, do not soft-pedal):**
- SNOO has FDA **Breakthrough Device designation** (2020) for keeping babies supine
  — a designation to *expedite review*, **not** proof of mortality benefit. It has
  **not** demonstrated a reduction in SIDS incidence; the 91.5% figure is a
  *behavioral surrogate* (less stomach sleeping), not deaths averted.
- **June 2026 FDA warning letter (resolved):** it does *not* retract the core
  supine-enforcement clearance or the 91.5% surrogate. It cites (a) an
  **unauthorized X-Small sleep sack (4–8 lb)** outside the cleared sizes —
  notable because that's the *smallest, youngest, highest-risk* infants and the
  cited risk is "respiratory compromise and suffocation," i.e. it touches the very
  mechanism we're relying on; (b) an unauthorized **Hospital Bundle**; (c) **quality
  failures** including **mold on mattresses/covers** and soiled refurbished units —
  which bears on the rebreathing/respiratory arm. Takeaway for the write-up: the
  *mechanism* stands; the *specific product execution* has real QC issues, so any
  claim should be about enforced-supine-plus-soothing as a principle, not an
  endorsement of one vendor's current units.
- The mechanism chain is strong and each link is individually evidenced; the
  *end-to-end mortality claim* is inferential, exactly the gap this whole project
  exists to bound rather than assert.
- Equity caveat: SNOO is expensive (~$1,700). A protocol that depends on it is
  unavailable to the highest-`E`, lowest-SES families — precisely the §14
  subpopulation where displacement harm is largest. The *mechanism* (enforced
  supine + soothing) should be separable from the *price point* in any policy claim.

**How the sim earns the punchline:** run three home protocols —
(i) supine, bare firm crib; (ii) supine + breathable mattress; (iii) supine +
enforced-supine soothing device (SNOO-like, with the §14 fragmentation/exhaustion
reduction switched on) — against the full DGP including the §14 displacement loop.
Prediction: protocol (iii) dominates on *net* infant mortality not because it
lowers the per-night prone risk further (it's already supine) but because it
**suppresses the displacement arm** that (i) and (ii) leave active. If the model
*can't* reproduce that ordering, the displacement mechanism is mis-calibrated.

---

## 17. SES is a confounder, not a cause — and the genuinely novel deliverable

This section exists to keep the project *honest in both directions*: not blown off
the line by the guideline literature, and not blown off the line by the analyst's
own prior against back-sleep. Follow the mechanism.

**17.1 SES does not cause SIDS — it has no direct arrow to the death hazard.**
The critique is correct as causal structure: in the SCM (§4), `SES` is a
*back-door* node acting **only** through mediators. There is no biological pathway
"poverty → infant dies in sleep." So "low SES causes SIDS" is exactly the
H2-marker error (§2), one level up. Right.

**17.2 But the mediator mix is mostly NOT drugs — that part of the critique is wrong.**
Decomposing the SES→risk gradient by population-attributable weight:

| Mediator | Rough weight | Note |
|----------|-------------|------|
| **Maternal smoking** (pregnancy + postnatal) | **largest** | Dose-response OR up to ~12; the single biggest modifiable factor. This, not drugs, dominates the gradient. |
| **Prematurity / low birth weight** | large | Poorer prenatal care; the 2–3× baseline risk multiplier. |
| **Not breastfeeding** | moderate | Breastfeeding is protective (~OR 0.4–0.6). |
| **Bed-sharing / unsafe surfaces** | moderate→large | Couples to §14 exhaustion + cultural norms + housing. |
| **Illicit drugs / alcohol** | **smaller (real, not dominant)** | Matters most as a bed-sharing *modifier* (sober vs. impaired co-sleeping), not as a large standalone population term. |

So "we force back-sleep because parents are on drugs" is **false on the numbers**:
the gradient is smoking + prematurity + no breastfeeding + unsafe surfaces, which
*cluster* with low SES. Drugs are a real but minor term, mostly as a co-sleeping
modifier. The emotional version of the claim overshoots the evidence.

**17.3 The part of the critique that is RIGHT and under-served: back-sleep's benefit
is heterogeneous, and the guideline reports the population OR, not the conditional
absolute risk.** Two facts coexist:
- Back-sleep's protective effect is **physiological, not social**: prone impairs
  arousal in *healthy term infants* with no SES/drug confound (§11 sources;
  Horne 2001), and Back-to-Sleep halved SIDS across *all* SES strata including
  affluent non-smokers. So the benefit is **not** contingent on being high-risk.
  (This is where the "it's just for drug users, makes no sense for my kid" inference
  fails — the mechanism is real for every infant.)
- **AND** the *absolute* incremental risk of prone for a precisely-characterized
  low-risk infant (term, non-smoking household, breastfed, firm/bare crib, sober
  non-bed-sharing caregivers) is **far smaller than the population OR of 3–5
  implies**, because OR is multiplicative on a baseline that is itself tiny and
  unequal. Nobody publishes *that* number, because case-control studies report
  population ORs, not conditional absolute risks on the low-risk manifold.

**17.4 The novel deliverable (this is the contribution).** Stop arguing *position*;
compute the **conditional absolute-risk surface** the literature never reports:

```
ΔAbsRisk(profile) = P(death | prone, profile, environment)
                  − P(death | supine, profile, environment)
```

evaluated on the **low-risk manifold** and **decomposed into**:
- **Removable-by-engineering** component (rebreathing via firm/breathable surface;
  obstruction via enforced supine — but note that "supine" is the very thing under
  question, so for a *prone* counterfactual obstruction stays in the irreducible
  bucket), and
- **Irreducible** component, which after a perfectly engineered environment is just
  two things: **(i) positional airway obstruction** (surface-independent, §11) and
  **(ii) primary autonomic failure** — a fatal brady/arrhythmia in a vulnerable-`V`
  infant that is *not* challenge-triggered and so has nothing to "engineer away."

Output: *"for a low-risk infant in a fully engineered environment, the irreducible
excess absolute risk of prone over the 0–6mo window is on the order of 1 in N,
versus 1 in M for supine; the difference is X, of which Y% is removable and Z% is
irreducible."* A number Pete can actually run ruin-asymmetry on — instead of a
scary, population-averaged, multiplicative OR.

**17.5 The crux open question (where novelty and skepticism are both legitimate):
does impaired arousal kill in the *absence* of a challenge?** The arousal arm
(§11) may be **necessary but not sufficient** — an arousal you never needed to mount
(because rebreathing/thermal/obstruction were engineered out) may be harmless. If
arousal-impairment requires a co-occurring challenge to be lethal, then removing
challenges *neuters* the largest prone pathway, and the irreducible residual
collapses toward only (i)+(ii) above. The literature does **not** cleanly separate
"arousal deficit" from "arousal deficit *given* a challenge," because in real cribs
the two travel together. The sim *can* separate them (toggle challenge nodes
independently of the arousal node). **This is the single most decision-relevant
unknown in the whole project**, and it is genuinely open — not settled by existing
papers. Treat it as the primary scientific target, with the honest caveat that if
(ii) primary autonomic failure is real and unidentifiable in advance (no test for
`V`), the residual stays non-zero against an absorbing outcome — which is *why* the
precautionary default survives even a favorable result, for now.

---

## 18. The linchpin experiment — does the arousal deficit kill without a challenge?

Concrete design for §17.5. The whole personal-decision question reduces to the
**functional form of the death hazard**: is prone's arousal penalty *additive*
(contributes hazard on its own) or *gated* (only bites when a physiological
challenge is present)? Real-world data can't answer it because in any normal crib
prone→challenge and prone→arousal-deficit are perfectly collinear. The sim breaks
the collinearity with `do()` and then lets **calibration** decide which form is
admissible.

**18.1 The two-layer defense, made explicit.** Decompose the protective response `R`
into its real physiology — they trigger differently, which is the crux:

- `R_arousal` — cortical arousal (wake, cry, squirm, turn head). **Requires a
  detectable challenge to fire.** Prone raises its threshold (Horne 2001).
- `R_autoresusc` — subcortical gasping / autoresuscitation, the last-ditch reflex
  that restores oxygenation after severe hypoxia. Fires on hypoxia **regardless of
  the source** (exogenous or endogenous). Vulnerable-`V` infants fail it (brainstem
  5-HT). Prone may also blunt it.

The distinction matters: removing exogenous challenges removes the *need* for
`R_arousal`, but **cannot** remove the need for `R_autoresusc` if an endogenous
event ever occurs. So "engineer the challenges away" defangs the first layer, not
necessarily the second.

**18.2 Challenge taxonomy (toggle each independently).**
- `C_exo` — engineerable: rebreathing (`Surface`), thermal load, positional
  obstruction. Set to 0 by a perfectly engineered environment.
- `C_endo` — **not** engineerable: spontaneous central apnea / brady / arrhythmia,
  a function of `V`, window `W`, and possibly prone (does position worsen baseline
  autonomic tone?). This is the irreducible challenge generator.

**18.3 Competing hazard forms to fit (the actual object of the experiment).**
Per sleep-epoch, with `C_total = C_exo + C_endo`:

```
Form G (gated/multiplicative):  h = κ · g(V,W) · C_total · (1 − R(C_total))
Form A (additive arousal):      h = κ · g(V,W) · C_total · (1 − R) + λ · pronePenalty
Form H (gated + prone-endo):    h = κ · g(V,W) · [C_exo + C_endo(prone)] · (1 − R)
```

- Under **G**: at `C_exo = 0` and `C_endo = 0`, hazard = 0 — *arousal deficit is
  harmless without a challenge*. This is Pete's hypothesis in equation form.
- Under **A**: the `λ · pronePenalty` term contributes hazard even at `C_total = 0`.
  This is the "prone is intrinsically dangerous" claim. `λ` is the thing to bound.
- Under **H**: prone has no free-standing hazard but *raises the endogenous
  challenge rate* — so engineering exogenous challenges away still leaves a
  prone-sensitive residual through `C_endo(prone)`.

**18.4 The factorial `do()` sweep.** Cross these planted interventions (the cells
the real world cannot produce):

| Toggle | Levels |
|--------|--------|
| Position | supine / prone |
| Arousal penalty (sever prone→`R`) | ON / **OFF** ← counterfactual: prone *without* the arousal deficit |
| `C_exo` (rebreathing/thermal/obstruction) | ON / **OFF** ← engineered environment |
| `C_endo` | ON / OFF (scaled by `V`) |
| `V` | vulnerable / not |

**Decisive cells:**
- `[prone, arousal-penalty ON, C_exo OFF, C_endo OFF]` → if `h ≈ 0`, arousal deficit
  is harmless absent a challenge → **Form G**, Pete's case holds; prone risk is
  fully engineerable.
- `[prone, arousal-penalty ON, C_exo OFF, C_endo ON]` → the **irreducible residual**:
  the part that survives a perfect environment. Its size = the real decision number.
- `[supine, arousal-penalty ON (imposed), C_exo ON]` vs `[prone, …]` → isolates how
  much of prone's risk is the *position's challenges* vs the *position's arousal
  penalty*. (Supine-with-imposed-deficit is impossible in vivo; here it's one line.)

**18.5 What forces the answer — calibration anchors (the experiment is only as good
as these).**

1. **Unaccustomed-prone spike (§8, OR ~18–20) discriminates the form.** Under G the
   spike *requires both* a present challenge and a near-total response failure (a
   baby with no head-turn practice). Reproducing it via challenge alone overshoots
   the CO₂ bench bounds; via arousal alone with `C_exo=0`, Form G yields zero. So
   the spike is the empirical fingerprint of the **interaction** — it calibrates the
   gated term and argues *against* pure-additive A.
2. **The no-baseline-derangement anchor argues λ ≈ 0 (supports G).** Horne 2001:
   prone impairs arousability *"with no clinically significant changes in
   cardiorespiratory variables or body temperature."* An arousal deficit that does
   not, by itself, derange physiology is direct evidence the free-standing additive
   term `λ` is near zero. **This is the strongest honest point for Pete's hypothesis.**
3. **Counter-anchor bounds `C_endo(prone)` (keeps a residual under H).** Prone shifts
   HRV, blood-pressure control, and cerebral oxygenation at baseline in several
   studies — so position may raise the *endogenous* event rate even with `C_exo=0`.
   Calibrate `C_endo(prone)` to those autonomic deltas; this is what stops the
   residual from going cleanly to zero.

**18.6 Reporting — form-conditional bounds + a form E-value.** Because the
`C_exo = 0` prone cell is *unobserved* (§11), its value is an extrapolation whose
credibility is the functional form. So never report a point estimate; report:

- The residual excess absolute risk at `C_exo = 0`, **as a band across forms G/A/H**,
  with `λ` and `C_endo(prone)` swept over their anchored plausible ranges.
- A **"form E-value":** how large would the additive arousal term `λ` (or the
  prone-endo multiplier) have to be to push the engineered-prone residual above a
  stated decision threshold (e.g. 1/10,000 excess over 0–6mo)? If that required `λ`
  contradicts the no-derangement anchor (§18.5.2), the engineered-prone-low-risk
  conclusion is *robust*; if a small `λ` suffices, it's *fragile*. Either way the
  claim is bounded, not asserted.

**18.7 The honest headline this produces.** Not "prone is safe" and not "prone is
dangerous," but:
> *"For a low-risk infant in a fully engineered environment, prone's excess absolute
> risk over supine is [band]. To argue it exceeds [threshold] you must commit to
> either (a) an additive arousal hazard `λ ≥ X` — contradicted by the
> no-baseline-derangement data — or (b) prone-driven endogenous autonomic events of
> magnitude `Y`, bounded by the HRV/BP literature. The residual that survives all
> engineering is `C_endo` in vulnerable-`V` infants, who cannot be identified in
> advance — which is why, against an absorbing outcome, the supine default holds
> until [band] is shown to sit below [threshold]."*

That is the novel, defensible, *bounded* statement the whole project exists to make.

---

## Sources

- Gilbert et al. 2005, *Int. J. Epidemiology* — systematic + historical review.
  https://academic.oup.com/ije/article/34/4/874/692905
- Mitchell et al. 1991 — New Zealand Cot Death Study.
  https://onlinelibrary.wiley.com/doi/10.1111/j.1440-1754.1991.tb00409.x
- King County, WA case-control 1996.
  https://www.sciencedirect.com/science/article/abs/pii/S0022347696801260
- Risk-factor changes after Back-to-Sleep (PMC3356149).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3356149/
- Smoking attributable risk in the BTS era (PMC545061).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC545061/
- Serotonin brainstem / triple-risk hypothesis (PMC6934437).
  https://pmc.ncbi.nlm.nih.gov/articles/PMC6934437/

**Mediation / arousal / NICU (§11–§13):**
- Prone impairs arousability in term infants (Horne et al.), J Pediatr 2001.
  https://pubmed.ncbi.nlm.nih.gov/11391321/
- Higher awakening threshold of preterm infants in prone (Ikels 2024), Acta Paediatr.
  https://onlinelibrary.wiley.com/doi/10.1111/apa.17194
- Cochrane: prone slightly improves oxygenation in ventilated neonates (small, short-term).
  https://www.evidentlycochrane.net/ventilated-oxygenated-comfy-positioning-preterm-babies/
- AAP: Transition to a Safe Home Sleep Environment for the NICU Patient, Pediatrics 2021;148(1):e2021052045
  (supine by 32wk PMA; prone requires continuous cardiorespiratory + SpO₂ monitoring).
  https://publications.aap.org/pediatrics/article/148/1/e2021052045/179976/

**Home devices / intervention (§15–§16):**
- FDA warning letter to Owlet Baby Care (Smart Sock marketed without clearance), 2021.
  https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/owlet-baby-care-inc-616354-10052021
- Owlet Dream Sock De Novo (DEN220091), FDA 2023 — OTC infant pulse-ox; BabySat (Rx) cleared 2023.
  https://www.accessdata.fda.gov/cdrh_docs/reviews/DEN220091.pdf
- SNOO FDA Breakthrough Device designation (2020) for keeping infants supine; De Novo coverage 2023.
  https://aasm.org/snoo-smart-sleeper-granted-fda-de-novo-approval/
- SNOO research (1,012-infant study; 91.5% reduction in unsafe stomach sleeping; no SIDS-incidence claim).
  https://happiestbabyscience.com/all-products/
- AAP 2022 safe-sleep recommendations (no home monitors to prevent SIDS; rolling/repositioning guidance).
  https://publications.aap.org/pediatrics/article/150/1/e2022057990/188304/
- FDA warning letter to Happiest Baby, Inc. (2026-06-15) — content not yet reviewed; verify before publishing.
  https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/happiest-baby-inc-718306-06152026
