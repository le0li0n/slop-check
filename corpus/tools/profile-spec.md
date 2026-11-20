# Author profile spec

A profile describes one author well enough that a writer could produce a new piece in their voice, arguing the way they argue, on a topic they never covered. It has two halves: **voice** (how they write) and **worldview** (what they believe and how they reason). It is written to `texts/profiles/<slug>/profile.json` beside the measured profile, and checked with `python3 tools/check_profile.py <slug>`.

Every profile uses the same fields, because profiles are later blended trait by trait. A trait that only makes sense in one author's vocabulary of categories cannot be blended with anyone else's.

## Rules

1. **Evidence from the corpus only.** Read the documents listed in `measured.json` under `documents`. Never open the file under `held_out`: it is reserved for testing whether the profile predicts a piece it has not seen. If you know something about the author from outside these files, leave it out. A profile that is right about the author but not supported by these texts cannot be tested.
2. **Every trait quotes the author.** Quotes are verbatim, copied exactly from the file, 5 to 40 words. The checker matches them against the source text and rejects any that do not appear.
3. **Count the pieces.** `docs_showing` is how many of the author's measured pieces show the trait, written `"4/6"`. A voice trait needs at least 2 pieces. A worldview item seen in only 1 piece is allowed but must say so, and should be `kind: "stated"`.
4. **Agree with the measurements.** Read `measured.json` first. Any `shape` entry marked `"trait": true` must be accounted for, either in a voice trait (list the feature name in `measured`) or in `unexplained_measured` with a sentence on why it does not amount to a trait. Nothing in the profile may contradict a measurement: do not call an author terse whose sentences rank long.
5. **Specific, not generic.** Before keeping a trait, ask whether it would be false of at least half of 50 well-regarded business and technology writers. "Uses concrete examples" and "writes clearly" are true of all of them and are cut. "Opens by conceding the reader's likely objection, then spends the piece taking it apart" is a trait.
6. **Portable.** Write `how_to_apply` as an instruction a writer could follow on an unrelated topic. Topic words from `phrases` ("lisp", "analytics") are subject matter, not voice, unless the author's *way* of using them is the point.
7. **Stated vs inferred.** A `stated` belief is something the author says outright; quote it. An `inferred` disposition is a pattern in how they reason across pieces; quote the passages that show the pattern. Keep them apart — the difference decides whether a new piece may assert the view or only reason in that manner.
8. **Snapshot, not biography.** These texts cover a limited span of years. Describe what the pieces show. For each belief, `generalizes_as` says how that reasoning would bear on a topic the author never wrote about, phrased as a way of thinking and never as an opinion attributed to the person.

## Shape

```json
{
  "author": "Name as in the manifest",
  "slug": "author-slug",
  "built_from": ["texts/<slug>/<file>.txt", "..."],
  "span": "2001–2004",
  "evidence_note": "one sentence on how much there is to go on and where it is thin",

  "summary": "2–4 sentences: what makes this author effective at persuading a business or technical reader. The mechanism, not praise.",

  "voice": [
    {
      "id": "v1",
      "category": "opening | structure | argument | evidence | sentence | lexicon | reader | humor | closing",
      "trait": "one specific sentence describing what they do",
      "how_to_apply": "an instruction a writer could follow on any topic",
      "evidence": [{"quote": "verbatim", "doc": "texts/<slug>/<file>.txt"}],
      "docs_showing": "4/6",
      "measured": ["feature or phrase names from measured.json that support this, or empty"]
    }
  ],

  "worldview": [
    {
      "id": "w1",
      "category": "belief | opponent | value | reasoning | temperament | reader | authority",
      "kind": "stated | inferred",
      "claim": "the belief, target, value or habit of mind, in one sentence",
      "generalizes_as": "how this way of thinking would bear on an unfamiliar topic",
      "evidence": [{"quote": "verbatim", "doc": "texts/<slug>/<file>.txt"}],
      "docs_showing": "3/6"
    }
  ],

  "never": [
    {
      "id": "n1",
      "trait": "something this author conspicuously does not do, where other writers commonly do",
      "basis": "measurement name from measured.json, or a sentence on how the texts show the absence",
      "docs_showing": "6/6"
    }
  ],

  "unexplained_measured": [
    {"feature": "name from measured.json", "why": "why this measured trait is not a voice trait"}
  ]
}
```

### Categories

**Voice.** `opening`: how a piece starts. `structure`: how it is organised and moves. `argument`: the moves used to persuade — concessions, reframes, reductio, analogy. `evidence`: what counts as support — anecdote, data, history, authority, logic. `sentence`: rhythm, length, punctuation habits. `lexicon`: characteristic words, registers, coinages. `reader`: how the reader is addressed and positioned. `humor`: kind and placement, if any. `closing`: how a piece ends.

**Worldview.** `belief`: a recurring thesis. `opponent`: what they argue against — a practice, a kind of company, conventional wisdom, a type of person. `value`: what they treat as good work and what as waste. `reasoning`: how they get to conclusions — first principles, pattern-matching from experience, data first, historical analogy. `temperament`: optimist or skeptic, certain or exploratory, how much they concede. `reader`: who they take the reader to be — peer, student, someone to warn or recruit. `authority`: where their standing to say this comes from.

### Size

Aim for 8–15 voice traits, 8–20 worldview items and 3–8 `never` items. Fewer well-evidenced traits beat many thin ones. Every worldview category should appear at least once; if the texts truly show nothing for one, say so in `evidence_note`.
