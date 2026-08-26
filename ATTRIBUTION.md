# Attribution

Most of the patterns in this scanner are not original to it. This file records what came from where, because a pattern list is the whole value of a tool like this and the people who assembled it should be named.

## The upstreams

| Source | What it gave | License |
|---|---|---|
| [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup | The editorial selection of tells behind sections §1–§35: inflated importance, vague sourcing, formulaic outlook sections, the overused-word list, the "not just X, it's Y" construction, and the rest | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| [blader/humanizer](https://github.com/blader/humanizer) by Siqi Chen | The organisation of those tells into numbered sections with before/after guidance, and the false-positive rules this README reproduces in shortened form | MIT, © 2025 Siqi Chen — see [`LICENSE-humanizer-MIT`](./LICENSE-humanizer-MIT) |

The `§n` numbers in every scan report point at humanizer's section numbering. If upstream renumbers, the references here go stale — which is worth checking on any re-sync.

Humanizer was vendored into a private repo on 2026-08-20 at commit `e2e92e7b4b8229253ed5c8e81dc65463fdeddda5`, version 2.11.2, and this scanner was written against it.

## What is original here

**The implementation.** Humanizer is a prose skill: you hand it text and it rewrites. This is a scanner — path scoping, per-pattern weights, a reporting threshold, per-section score and report caps, quoted-span masking, the JSON and CLI interfaces, the `.slopcheck.json` config. None of that exists upstream.

**Three pattern sections:**

- **`GB`** — British spellings in American copy. From a house styleguide, not from Wikipedia.
- **`OUT`** — B2B outreach openers: "just curious", "circling back", "I wanted to reach out", "hope you're doing well". Same source.
- **`CL`** — phrases Claude reaches for constantly: the hidden-knowledge construction, the aphoristic restatement, "shape" standing in for a specific noun, "X is doing real work". Assembled in August 2026 by Jared Waxman, mostly from spotting them in other people's published newsletters and recognising where they came from.

**Two deliberate departures from upstream:**

- **Em dashes.** Humanizer treats them as close to banned. Here they are reported as a rate rather than a per-instance violation, because editors use dashes and a rule that fires on every one of them gets ignored.
- **Scope.** Humanizer rewrites whatever you give it. This decides what counts as outward-facing and leaves internal writing alone, because internal writing is supposed to be blunt and running a slop check over it sands it down.

## Share-alike

Sections §1–§35 derive from CC BY-SA material, so this repo is released under **CC BY-SA 4.0** rather than a permissive licence. Reuse it, change it, ship it — attribute the same upstreams and keep derivatives under the same terms.

The MIT text for humanizer is included separately at [`LICENSE-humanizer-MIT`](./LICENSE-humanizer-MIT) and applies to that work.
