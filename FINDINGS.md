# Findings (through Phase 8)

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

## 3.5 How much of the historical OR is a study artifact? (Phase 3.5)

`scripts/phase35_bias.py` plants the calibrated causal effect, then runs the flawed
retrospective design on top -- recall bias (cases over-report prone among the
truly-supine) + control-selection bias (controls oversampled toward advantaged/
supine families) -- and compares to the TRUE do-effect.

| | PRE era | POST era |
|---|---:|---:|
| **true do-effect OR (planted)** | 3.03 | 3.02 |
| clean crude design (no bias) | 2.93 | 5.04 |
| + recall bias only | 3.91 | 5.94 |
| + control-selection bias only | 3.53 | 7.40 |
| + both biases (what a study sees) | 4.30 | 8.73 |

Two honest takeaways, both vindicating Pete's skepticism *in degree, not in kind*:

1. **The reported OR is materially inflated by design** -- 1.4x (pre) to 2.9x (post)
   above the true do-effect once recall + selection bias are layered on. The famous
   numbers are partly artifact.
2. **But the effect does not vanish when bias is removed.** The clean do-effect
   stays ~3. Note the POST clean-*crude* OR (5.04) already overshoots the do-effect
   (3.02) *before any bias* -- that gap is the healthy-adherer **confounding** (post
   prone concentrates in adversity), exactly the Phase-4 PCA story, and it's what the
   *adjusted* OR is meant to remove. So the historical OR = a real causal core (~3)
   + confounding + design bias stacked on top.

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

## 5. How much of prone's risk can you engineer away at home? (Phase 4.5)

Phases 1-4 establish *that* prone is causal. Phase 4.5 (DESIGN.md sections 11,17,18)
asks the decision-relevant question: decompose the calibrated prone effect into
mechanism channels (rebreathing, thermal, obstruction, free-standing arousal,
endogenous autonomic), then toggle a fully engineered home environment (breathable
surface + cool room) and read off the **residual excess absolute risk** for a
**low-risk infant** (non-smoking household, firm/bare crib, advantaged), marginal
over the unknown vulnerability phenotype.

The decomposition is pinned so that in a historical crib it reproduces the
calibrated prone effect exactly (OR ~3.1), and the habituation amplifier is solved
to reproduce the unaccustomed-prone spike (OR ~19) -- which only the *gated*
(challenge x response-failure) structure can produce, not a free-standing arousal
term.

**Excess absolute risk, prone vs supine, low-risk infant (per 1000 births):**

| form (anchor) | historical crib | engineered (breathable+cool) | removable |
|---------------|----------------:|-----------------------------:|----------:|
| **G gated** (Horne: lambda~0) | 0.191 | **0.041** | **78%** |
| H endo (prone raises autonomic events) | 0.191 | 0.069 | 64% |
| A additive (adversarial; lambda large) | 0.191 | 0.093 | 51% |

**Form E-value (robustness):** to push the engineered-prone excess above
**0.5/1000** is *unreachable* even if the entire prone effect were free-standing
arousal hazard; to exceed even **0.1/1000** would require **~33%** of the prone
effect to be free-standing arousal -- but the no-baseline-derangement data (Horne
2001) anchors that term near 0%. So the engineered residual sits robustly in the
**~0.04-0.09 / 1000** band (roughly 1 in 11,000-25,000).

**What survives all engineering:** positional airway obstruction (prone-intrinsic)
plus endogenous autonomic events in vulnerable infants -- and `V` cannot be
identified in advance. So the residual is small but non-zero against an absorbing
outcome. The contribution of this phase is to convert the scary multiplicative
OR (~3-5) into a *conditional absolute* number a parent can actually reason about,
and to bound how much of it is removable (most) vs irreducible (little, but real).

**Caveats specific to Phase 4.5:** the engineered-prone cell is *unobserved* in the
real data, so these are model extrapolations whose credibility is the functional
form -- which is exactly why the result is reported as a form-band plus E-value, not
a point estimate. The mechanism shares within each form are still illustrative
(anchored to the spike + the no-derangement datum, not yet individually fit).

## 6. Discrimination report -- the formal verdict (Phase 5)

`scripts/phase5_discrimination.py` calibrates all three worlds and scores them
against `data/calibration/targets.json`, separating **discriminating** targets from
**shared** ones (reproduced by no world -- the documented era-model gap, so they
cannot discriminate). The operative discriminator is the prone adjusted OR at both
eras plus its rise across the campaign.

| world | calib loss | discriminator (prone-OR + rise) | verdict |
|-------|-----------:|:-------------------------------:|:-------:|
| H1 causal | 1.11 | PASS (3.34 -> 3.81) | **SURVIVES** |
| H3 triple | 1.20 | PASS (3.28 -> 3.48) | **SURVIVES** |
| H2 marker | 6.06 | **FAIL (1.16 -> 1.40)** | **REJECTED** |

The marker world is rejected because it cannot lift the OR off ~1 or make it rise.
H1 and H3 both reproduce the discriminator (minor out-of-sample level misfits
remain, e.g. the noisy pre-era death rate and the smoking dose-response OR; these
do not bear on the causal verdict). Shared, non-discriminating gaps (post-era death
decline, smoking's rising attributable share) are the same era-model limitation
noted below -- they reject no world differentially.

## 7. When does the back-sleep recommendation backfire? (Phase 7)

`scripts/phase7_displacement.py` adds the parental-exhaustion -> bed-sharing
displacement loop (DESIGN sections 12,14): supine sleep is lighter -> more
exhaustion -> more unplanned bed/sofa sharing, whose risk dwarfs prone-in-a-crib.
We compare the recommendation (back-sleep) against the counterfactual it replaced
(uncontrolled prone), net of displacement. **Net > 0 = the recommendation increases
expected death for that family.** Parameters are illustrative (anchored to the
section-14 location ORs), so the result is the SHAPE, not the magnitudes.

| family (low-risk infant), abstinence framing | P(displace) | supine advice | prone (hist) | +soother | net /1000 |
|---|---:|---:|---:|---:|---:|
| advantaged, supported | 0.03 | 0.160 | 0.316 | 0.125 | **-0.156** (protective) |
| average | 0.05 | 0.205 | 0.335 | 0.144 | **-0.131** (protective) |
| deprived, solo, twins | 0.19 | 0.527 | 0.488 | 0.297 | **+0.039 (HARMFUL)** |

Three findings:

1. **The sign is heterogeneous.** For advantaged/supported families the
   recommendation is clearly net-protective. For exhausted, unsupported families it
   can flip net-harmful -- the displacement loop outweighs the in-crib protection.
2. **Framing is a lever.** Under abstinence framing ("never bed-share") the flip
   occurs at ses ~ -1.74 for a solo parent (and below); under **harm-reduction
   framing it never flips** across the scanned range. Telling exhausted parents how
   to bed-share least dangerously beats telling them not to, because abstinence
   pushes displacement into the sofa/armchair tail (the >50x-risk location).
3. **An enforced-supine soother removes the trap.** The `+soother` column (SNOO-like)
   is the safest arm for every family, because cutting fragmentation cuts the
   exhaustion that drives displacement. This is the section-16 punchline arriving by
   a second, independent route: the device helps not only by enforcing supine but by
   defusing the bed-sharing loop.

This is also the predicted calibration signal of DESIGN section 14: a model WITHOUT
the displacement arm understates real post-campaign SUID precisely in the
high-exhaustion / low-SES strata -- the families where the arm fires hardest.

## 7.5 Continuous direct-causal fraction (Phase 6)

`scripts/phase6_mixing.py` replaces the discrete three-worlds with a continuous
**direct-causal fraction** `lambda = w_prone / w_prone_full` (0 = pure marker,
1 = full causal) and profiles the calibration loss over it -- re-optimizing every
other parameter (confounding slopes, smoking/bedding/SES, vulnerability) at each
lambda to give the marker side every chance.

| lambda (direct share) | 0% | 25% | 50% | 75% | 100% | 125% | 150% | 175% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| calib loss | 8.11 | 5.37 | 4.80 | 4.18 | 2.66 | 1.44 | 1.45 | 1.36 |

The loss **explodes ~6x toward the marker end** (lambda=0) and plateaus low once the
direct share is large; the acceptable region (within 2x of the best fit) is
**lambda >= ~1.0**. So the data demand that essentially all of prone's apparent
effect be direct-causal -- they never prefer a diluted or marker world no matter how
the confounders are retuned. This is the continuous analog of the Phase-3 E-value
verdict. (The flat minimum wandering to lambda=1.75 is optimizer noise on the
plateau, not a claim that prone "over-explains"; it also hints the discrete
calibration mildly under-shot w_prone.)

## 8. Which home protocol minimizes NET infant mortality? (Phase 8, capstone)

`scripts/phase8_protocols.py` integrates Phase 4.5 (position/environment -> in-crib
risk) and Phase 7 (exhaustion -> displacement) into ONE model and ranks realistic
home protocols by net population mortality, split into in-crib vs displacement
components. Calibrated so the campaign is net-beneficial at the population level
(bare supine << historical prone); displacement magnitudes inherit the illustrative
Phase-7 params, so trust the RANKING, not the absolute levels.

**Abstinence framing ("never bed-share"):**

| rank | protocol | net/1000 | in-crib | displace |
|---|---|---:|---:|---:|
| 1 | **supine + soother (SNOO)** | **0.938** | 0.498 | 0.440 |
| 2 | engineered prone permitted | 1.198 | 0.714 | 0.483 |
| 3 | supine, bare firm crib | 1.478 | 0.474 | 1.005 |
| 4 | supine + breathable mattress | 1.478 | 0.474 | 1.005 |
| 5 | historical prone (reference) | 1.982 | 1.499 | 0.483 |

**Harm-reduction framing:**

| rank | protocol | net/1000 | in-crib | displace |
|---|---|---:|---:|---:|
| 1 | **supine + soother (SNOO)** | **0.610** | 0.504 | 0.106 |
| 2 | supine, bare firm crib | 0.734 | 0.487 | 0.247 |
| 3 | supine + breathable mattress | 0.734 | 0.487 | 0.247 |
| 4 | engineered prone permitted | 0.841 | 0.724 | 0.117 |
| 5 | historical prone (reference) | 1.635 | 1.519 | 0.117 |

Five findings:

1. **The enforced-supine soother wins under BOTH framings** -- and wins via the
   *displacement* column, not the in-crib column (its in-crib risk equals bare
   supine; it just cuts the exhaustion that drives bed/sofa sharing). This is the
   section-16 punchline confirmed on the full DGP.
2. **A breathable mattress is ~useless for a SUPINE baby** (identical to the bare
   crib): rebreathing is a *prone* channel, so a breathable surface has almost
   nothing to act on once the baby is on its back. It matters only if you are
   contemplating prone.
3. **The case for permitting engineered prone exists ONLY under abstinence framing.**
   Under abstinence it ranks #2 (its deeper sleep cuts displacement enough to beat
   bare supine); switch to harm-reduction framing and bare supine reclaims the edge
   (#2 vs #4). So the right lever is not "permit prone" -- it is "fix the framing and
   add a soother," which dominates prone either way.
4. **Harm-reduction framing lowers every protocol's net risk** vs abstinence, by
   moving displacement off the >50x sofa tail.
5. **Historical (uncontrolled) prone is worst under both framings**, reproducing why
   Back-to-Sleep saved lives -- the empirical anchor the model is tuned to respect.

## Bottom line (all phases)

1. Prone IS an independent cause (Phases 1-5): the marker-only world is falsified;
   H1/H3 survive.
2. But most of prone's risk for a low-risk infant is *engineerable* (Phase 4.5):
   ~78% removable, leaving ~0.04-0.09/1000 (obstruction + endogenous autonomic),
   robustly below 0.5/1000. Engineered prone is close to -- not equal to -- that
   infant's own supine risk, and well below the population supine average.
3. The back-sleep recommendation's net effect is *heterogeneous* (Phase 7): clearly
   protective for supported families, able to backfire for exhausted/unsupported ones
   via bed-sharing displacement, especially under abstinence framing.
4. The dominant home protocol (Phase 8) is **back-sleep + an enforced-supine soother**,
   under **harm-reduction framing** -- it captures supine's in-crib safety AND defuses
   the displacement loop, beating every alternative including engineered prone. The
   data-supported version of Pete's thesis is not "prone is fine if engineered"; it is
   "supine + soother through the high-risk window, framed as harm-reduction."

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
