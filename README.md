# sids-causal-sim

A rigorous causal simulation testing whether prone (stomach) infant sleeping is a
risk **by itself** — or whether it only looks dangerous because of the factors it
co-occurs with (maternal smoking, low SES, soft bedding, bed-sharing) — and, if it
is causal, **how much of that risk is engineerable at home**.

This is **not** an attempt to prove causation from a simulation (you can't — see
`DESIGN.md` §1). It is a falsification engine: we try our hardest to build a world
where prone is harmless and still matches the real historical record. If we can't,
the innocent explanation is ruled out. The work is shared openly **so it can be
critiqued** — the parameters, the structural assumptions, and the conclusions are
all on the table.

> Not medical advice. This is an independent modeling exercise. Current public-health
> guidance is to place infants on their back for every sleep; talk to a pediatrician.

## Read first

- [`DESIGN.md`](./DESIGN.md) — the locked protocol (the science we build against).
- [`FINDINGS.md`](./FINDINGS.md) — every result and the honest limitations.

## What it concludes (short version)

1. **Prone is a genuine cause, not just a correlate** — the marker-only world is
   falsified; an unmeasured confounder would need implausible strength; the
   continuous fit demands essentially all of prone's effect be direct-causal.
2. **But most of the risk for a low-risk infant is engineerable** — ~78% removable
   (rebreathing + thermal), leaving a small residual (positional obstruction +
   endogenous autonomic) that is robustly below ~0.5/1000.
3. **The recommendation's net effect is heterogeneous** — back-sleep can backfire
   for exhausted, unsupported families via bed-sharing displacement, especially
   under abstinence framing.
4. **The dominant home protocol** is back-sleep + an enforced-supine soother under
   harm-reduction framing — it keeps supine's safety and defuses the displacement
   loop.

See `FINDINGS.md` for the numbers, the supervised-prone carve-out, and the caveats.

## Layout

```
DESIGN.md            the protocol (start here)
FINDINGS.md          results + limitations
src/sids_sim/        structural causal model, estimators, mediation, displacement
scripts/             one runnable script per phase (phase1..phase9 + phase35/45)
data/calibration/    real published targets the sim must match
tests/               unit tests + calibration-gate checks
```

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest                          # full test suite
python scripts/phase5_discrimination.py   # the falsification verdict
python scripts/phase45_linchpin.py        # conditional absolute-risk decomposition
```

## Provenance

Built as a personal-curiosity research project, with substantial AI pair-programming
(Claude). Calibration targets and parameter anchors are cited in `DESIGN.md`.
Corrections and critiques welcome — open an issue or PR.
