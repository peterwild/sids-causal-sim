# sids-causal-sim

A rigorous causal simulation testing whether prone (stomach) infant sleeping is a
risk **by itself** — or whether it only looks dangerous because of the factors it
co-occurs with (maternal smoking, low SES, soft bedding, bed-sharing).

This is **not** an attempt to prove causation from a simulation (you can't — see
`DESIGN.md` §1). It is a falsification engine: we try our hardest to build a world
where prone is harmless and still matches the real historical record. If we can't,
the innocent explanation is ruled out.

## Read first

[`DESIGN.md`](./DESIGN.md) — the locked protocol. We build against it; we don't
improvise the science.

## Approach in one line

Encode three competing worlds (prone-causal / prone-as-marker / triple-risk),
calibrate each to six real historical numbers, then see which can reproduce
history — and quantify, with sensitivity bounds, how much of prone's risk has to
be genuinely causal.

## Layout

```
DESIGN.md            the protocol (start here)
src/sids_sim/        structural causal model + simulators
data/calibration/    real published targets the sim must match
tests/               unit tests + calibration-gate checks
```

## Status

Phase 0 (research + design) complete. Phase 1 (forward simulator) is next.
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
