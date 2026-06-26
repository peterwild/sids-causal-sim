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
- [ ] Phase 5 — Discrimination report + write-up
- [ ] Phase 6 (deferred) — Continuous mixing-weight fit

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
