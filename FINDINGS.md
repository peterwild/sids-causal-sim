# Findings (through Phase 3)

**Question:** Is sleeping prone (stomach) a SIDS risk *by itself* -- holding the
other dangers (smoking, low SES, soft bedding) constant -- or does it only look
dangerous because of the company it keeps?

**Answer so far: prone is dangerous by itself.** The "it's only correlation"
explanation is rejected by two independent arguments.

---

## 1. Measured confounding cannot fake it (Phase 2)

Three worlds were calibrated to six historical targets across both eras:

| World | Fit (loss) | adjusted prone OR pre -> post (target 2.86 -> 3.93) |
|-------|-----------:|------------------------------------------------------|
| H1 prone causal | **1.23** | 3.21 -> 3.96 (fits) |
| H3 triple-risk  | **1.36** | 3.44 -> 3.25 (fits; rise weak) |
| H2 marker (confounding only) | **5.87** | **1.10 -> 1.00 (fails)** |

The marker world was given every fair advantage (free poverty->death path, free
prone<->SES coupling) but kept prone's direct effect at zero. It cannot lift the
odds ratio off 1.0 -- because all the confounders it leans on (smoking, bedding,
SES) are exactly what the historical "adjusted OR" already subtracts out.

So the marker theory's only refuge is **unmeasured** confounding.

## 2. Unmeasured confounding would have to be implausibly strong (Phase 3)

We added the one hidden channel that survives adjustment: vulnerable (fragile)
infants being preferentially placed prone (`gamma_vuln_prone`). Sweeping it:

| hidden V->prone OR | prone in vulnerable | prone in others | resulting adjusted prone OR |
|-------------------:|--------------------:|----------------:|----------------------------:|
| 1.0 (none) | 50% | 50% | 1.08 |
| 2.7 | 65% | 41% | 1.43 |
| 7.2 | 79% | 34% | 1.94 |
| 11.9 | 84% | 30% | 2.10 |
| 19.6 | 88% | 28% | 2.69 |

To fake the **pre-era OR of 2.86**, fragile babies would have to be placed prone
with an odds ratio of **~22.6** (89% of vulnerable infants vs 27% of others).
The **post-era OR of 3.93 is unreachable at any plausible strength.**

The assumption-light VanderWeele-Ding **E-values** agree: an unmeasured
confounder would need associations of at least **5.17** (pre) and **7.32** (post)
with BOTH prone and death to explain the effect away.

**Plausibility:** the strongest known SIDS risk factor is heavy maternal smoking
(OR ~12.7); most are 2-4. A hidden factor with an OR of ~22 on prone placement,
that nobody ever measured, is not credible. The structural argument is even
harder: pre-campaign, ~80% of *all* babies were placed prone, leaving almost no
room for vulnerable babies to be placed prone *differentially*.

## 3. External fingerprint (independent of the model)

Babies usually placed supine but placed prone once show OR ~18-20 -- often
low-risk infants. A pure-marker world cannot produce that spike. It is a
physiological signature of a real causal mechanism (an infant with no practice
turning its head cannot clear rebreathed CO2).

---

## 4. Is prone the "principal component"? Causally yes, by variance no (Phase 4)

The word means two different things, and the answer differs:

**Outcome-variance decomposition (Shapley / LMG share of death R^2, H3 calibrated):**

| factor | pre, observable | pre, incl. vulnerability | post, observable |
|--------|----------------:|-------------------------:|-----------------:|
| latent vulnerability | -- | **49.8%** | -- |
| heavy smoking | 44.8% | 22.5% | 39.3% |
| smoking (any) | 19.0% | 9.5% | 15.3% |
| **prone** | **14.9%** | **7.5%** | **21.7%** |
| SES | 11.4% | 5.7% | 13.2% |
| soft bedding | 9.9% | 5.0% | 10.6% |

By share of variance prone is a **mid-pack** contributor. The single largest axis
is the **latent vulnerability (~42-50%)**; among measured factors, **smoking
dominates**. So prone is a real, removable *cause* (sections 1-3) yet NOT the
biggest slice of variance. Those are different questions: variance share also
depends on prevalence and on how much the other factors vary. Prone was the
headline public-health win because it is the biggest *modifiable causal lever* --
you cannot change a baby's brainstem, but you can change its position -- not
because it explains the most variance.

**PCA on the risk-factor matrix -- the correlation-vs-causation story as a picture:**

* PRE-campaign, prone loads on its OWN axis (PC3 = -0.88), nearly orthogonal to
  the social-adversity bundle (PC1: smoking/SES/bedding). When ~everyone sleeps
  prone, prone is statistically independent of adversity -- so the prone<->death
  link of that era *cannot* be confounding. It has to be causal.
* POST-campaign, prone migrates ONTO the adversity axis (PC1 loading -0.13 ->
  -0.43), because the healthy-adherer gate ties remaining prone use to low SES /
  smoking. This is exactly why the post-era OR is partly inflated by selection
  rather than extra causal potency -- and why naive pre/post OR comparisons are
  treacherous.

## Honest limitations

- Everything rests on the calibrated data-generating process. The result is
  robust because it agrees with the assumption-light E-value, but it is not an
  experiment (none can exist).
- **No world yet reproduces the full post-campaign death decline** (1.2 -> 0.4)
  or the rise in smoking's attributable share (50% -> 80%). Our model of "what
  changed across the era" is currently just prone + bedding; the real decline
  also rode on smoking and breastfeeding campaigns. This does not affect the
  odds-ratio / E-value logic, but it is an open calibration gap (Phase 4+).
- The triple-risk world slightly under-reproduces the OR *rise* and over-
  concentrates deaths in the vulnerable; minor tuning outstanding.
- The Phase-4 variance decomposition does NOT reproduce the real-world rise in
  smoking's attributable share (50% -> 80%): in our model prone's variance share
  rises post-era and smoking's falls, the opposite of history. This traces to the
  same incomplete era-model gap (we change only prone + bedding across the era)
  plus the healthy-adherer gate making post-era prone a stronger risk marker.
  Note PAF and LMG R^2-share are different metrics; neither is yet matched.

## Bottom line for the original question

Holding smoking, SES, and bedding constant, **stomach sleeping carries real,
independent risk.** The correlation-only story would require a hidden cause far
stronger than any known SIDS risk factor -- and cannot reproduce the post-era
evidence at all. The triple-risk reading remains the best mechanism: prone is a
removable *trigger* that bites hardest in an already-vulnerable infant, which is
why eliminating it saved so many lives without being the whole story.
