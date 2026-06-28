# The couch is the real enemy (draft essay)

> **This is an opinion / policy essay draft, not the analysis.** The numbers behind
> it live in [`FINDINGS.md`](./FINDINGS.md) and [`DESIGN.md`](./DESIGN.md). It is a
> work in progress and it is not medical advice.

We tell new parents two things: always put the baby on its back, and never share a
bed. Both pieces of advice are right on their own. Put together, for an exhausted
parent at 3am, they can produce the single most dangerous thing a baby can do --
and almost nobody says so out loud.

Here is the part that took me a while to see. The honest comparison isn't "back
sleeping versus stomach sleeping." It's "what a wrecked parent actually does at 3am
versus the alternatives." And what they actually do, when the baby won't go down on
its back and the rule is *never bed-share*, is improvise. They feed lying down and
fall asleep. They give up and sink into the couch with the baby on their chest.

I think about this the way I used to think about trading strategies. There is always
a gap between the simulation and the real world. A backtest can tell you one thing is
optimal -- and it can be, on paper, under perfect execution. But deploy it into a
live market full of real humans and slippage and behavior eat the edge; the strategy
that actually makes money is rarely the one that looked best in the sim. "Always
back, never bed-share" is the backtest-optimal policy. It assumes perfect compliance.
The real world is the live market, and the exhausted parent at 3am is the part of the
system that doesn't comply. A good quant doesn't fall in love with the paper-optimal
strategy -- they optimize the realized outcome, net of how the thing actually gets
executed by imperfect agents. Public-health advice should be built the same way:
optimize for what sleep-deprived parents will really do, not for what a perfectly
compliant robot would do. Our own simulation says back, always. We also know, with
certainty, that a chunk of parents will end up on the couch instead. A policy that
ignores that second fact is optimizing the backtest, not the world.

That couch is not a small mistake. Sofa and armchair co-sleeping carries roughly
**18 to 50 times** the risk of a baby sleeping safely on its back. By contrast, a
low-risk baby placed on its stomach in a properly set-up crib -- firm breathable
mattress, nothing else in there, cool room -- carries something like **1.4 times**
the baseline risk, and close to baseline if a parent is awake and watching. I am not
telling you to put your baby on its stomach. I'm telling you that the math of the 3am
decision is not the math the advice assumes. The parent flipping the baby prone in a
good crib is on the order of ten to thirty times safer than the same parent
collapsing on the couch -- and our messaging nudges them toward the couch, because it
gives them nothing safe to reach for when the rules fail.

That's a public-health design problem. You don't hand a sleep-deprived population a
list of *don'ts* with no sanctioned *do* and expect good outcomes. Harm reduction
beats abstinence here for the same reason it does everywhere: people in distress will
act, and your job is to make the thing they reach for the least dangerous version,
not to pretend they won't reach.

So what's the safe thing to reach for? The most effective one is boring: cut the
exhaustion that drives the whole spiral. The lighter sleep of back-sleeping is real,
it wears parents down, and worn-down parents are the ones who end up on the couch. A
responsive bassinet that keeps the baby on its back and soothes it back to sleep --
the SNOO is the one everyone knows -- attacks the problem at the root. It keeps the
baby supine *and* it keeps the parent rested enough not to make the 3am mistake. In
our modeling it beats every other home setup, not by making any single night safer
in the crib, but by quietly removing the desperation that leads to bed-sharing in the
first place.

There's one ugly catch. A SNOO is about $1,700. Which means the tool that defuses the
most dangerous failure mode is paywalled away from exactly the families most likely
to hit it -- the exhausted, unsupported, lower-income parents where bed-sharing risk
already runs highest. We've built a safety device and priced it so the people who
need it most can't have it.

So here's the policy take: governments should give every new family a responsive
bassinet, the way some already give safe-sleep kits. This is not a fringe idea.
Finland has handed every expecting mother a "baby box" since 1938 -- a box of
supplies that doubles as a safe place to sleep -- and it was introduced for exactly
two reasons: falling birth rates and high infant mortality. Scotland copied it in
2017 and has shipped over 350,000. Nobody calls this socialism. It's the same genre
as fluoride, vaccines, and prenatal vitamins -- cheap public infrastructure that
pays for itself many times over the first time it prevents one catastrophe.

And then the part I find most interesting. The newborn phase is, for a lot of people,
genuinely traumatic -- not "tiring," but a months-long sleep-deprivation grind that
is one of the most cited reasons couples stop at one kid, or at none. Birth rates
across the developed world are sliding below replacement and every government is
nervously throwing money at it. A device that makes the newborn phase survivable --
even enjoyable -- is, plausibly, pro-natal policy. Make the worst part of having a
baby less brutal and, at the margin, more people have another. Finland's box was
born from a fertility panic in the first place. The wheel comes back around.

Two honest caveats, because the whole point of this project is not to oversell. No
home device -- not the SNOO, not the Finnish box -- has been *proven* to reduce SIDS
deaths in a trial; the box's historical win came largely from pulling mothers into
prenatal care, not from the cardboard. And the fertility link is a plausible
mechanism, not a measured effect. So the case for buying every family a bassinet
doesn't rest on a guaranteed body count. It rests on this: it is cheap, it is
progressive in who it reaches, it plausibly helps on two of the things we say we care
about most -- keeping babies alive and helping families grow -- and it has decades of
precedent doing exactly this in countries with the lowest infant mortality on earth.

The current message to exhausted parents is "don't." A better one is "here's how,"
plus the tool that means they rarely have to choose under fire. Give them the
bassinet.
