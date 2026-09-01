# What these patterns do to human writing

`ai_slop.py` run over the whole corpus: **382 documents, 330,288 words**, all published before 2012 and all written by people.

| | |
| --- | --- |
| Documents flagged | 9 of 382 (2%) |
| Median score | 1 (threshold 8) |
| 90th percentile score | 5 |

The flagged share is the false-positive rate on human prose. Every one of these documents predates the models, so each flag is the scanner objecting to writing that a person actually published.

## Tells ranked by how ordinary they are

Rates are per 10,000 words. High in this table means the phrase is normal English and a hit proves nothing on its own; near-zero means a hit is worth acting on.

| § | Match | Hits | Per 10k | Docs |
| --- | --- | ---: | ---: | ---: |
| 11 | `sentences in one paragraph open with "i"` | 15 | 0.45 | 15/382 |
| 7 | `landscape` | 14 | 0.42 | 14/382 |
| 37 | `words with no first person` | 10 | 0.30 | 10/382 |
| 7 | `leveraging` | 8 | 0.24 | 6/382 |
| 7 | `robust` | 7 | 0.21 | 6/382 |
| 11 | `sentences in one paragraph open with "the"` | 7 | 0.21 | 7/382 |
| 7 | `enhanced` | 7 | 0.21 | 4/382 |
| CL | `which is why` | 6 | 0.18 | 4/382 |
| 23 | `needless to say` | 5 | 0.15 | 4/382 |
| 28 | `let's take a look` | 4 | 0.12 | 1/382 |
| 7 | `moreover,` | 4 | 0.12 | 4/382 |
| 8 | `offers a` | 4 | 0.12 | 1/382 |
| 7 | `seamlessly` | 4 | 0.12 | 4/382 |
| 7 | `foster` | 4 | 0.12 | 3/382 |
| 11 | `sentences in one paragraph open with "you"` | 4 | 0.12 | 4/382 |
| 7 | `furthermore,` | 4 | 0.12 | 4/382 |
| 14 | `em/en dashes, one per 155 words` | 4 | 0.12 | 4/382 |
| CL | `nobody is` | 3 | 0.09 | 3/382 |
| 14 | `em/en dashes, one per 118 words` | 3 | 0.09 | 3/382 |
| 7 | `enhance` | 3 | 0.09 | 3/382 |
| 10 | `three-item lists in 17 lines` | 3 | 0.09 | 3/382 |
| 7 | `crucial` | 3 | 0.09 | 3/382 |
| 7 | `leverage the` | 3 | 0.09 | 3/382 |
| 14 | `em/en dashes, one per 119 words` | 3 | 0.09 | 3/382 |
| 7 | `enhancing` | 3 | 0.09 | 3/382 |
| 7 | `aligned with` | 3 | 0.09 | 2/382 |
| 28 | `lets take a look` | 3 | 0.09 | 3/382 |
| 14 | `em/en dashes, one per 195 words` | 3 | 0.09 | 3/382 |
| 9 | `it's not just` | 2 | 0.06 | 2/382 |
| 20 | `let me know if` | 2 | 0.06 | 2/382 |
| 7 | `align with` | 2 | 0.06 | 1/382 |
| 7 | `leveraged` | 2 | 0.06 | 2/382 |
| 4 | `renowned` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "he"` | 2 | 0.06 | 2/382 |
| 34 | `to be clear,` | 2 | 0.06 | 2/382 |
| 7 | `additionally,` | 2 | 0.06 | 2/382 |
| 24 | `could potentially` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 84 words` | 2 | 0.06 | 2/382 |
| 20 | `great question` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 110 words` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 113 words` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 57 words` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "and"` | 2 | 0.06 | 2/382 |
| CL | `nobody has` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 66 words` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 69 words` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "it"` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "if"` | 2 | 0.06 | 2/382 |
| CL | `nobody wants` | 2 | 0.06 | 2/382 |
| 7 | `pivotal` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 159 words` | 2 | 0.06 | 2/382 |
| 7 | `showcase` | 2 | 0.06 | 2/382 |
| 8 | `offers an` | 2 | 0.06 | 2/382 |
| 7 | `leverage this` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "we"` | 2 | 0.06 | 2/382 |
| 7 | `quietly` | 2 | 0.06 | 2/382 |
| 14 | `em/en dashes, one per 140 words` | 2 | 0.06 | 2/382 |
| 11 | `sentences in one paragraph open with "will"` | 2 | 0.06 | 2/382 |
| 5 | `studies have shown` | 2 | 0.06 | 2/382 |
| 9 | `not just fair use, but` | 1 | 0.03 | 1/382 |

## By section

Which parts of the pattern list generate the most noise on human prose.

| § | Hits | Per 10k |
| --- | ---: | ---: |
| 7 | 92 | 2.79 |
| 14 | 79 | 2.39 |
| 11 | 51 | 1.54 |
| 9 | 44 | 1.33 |
| CL | 33 | 1.00 |
| 10 | 17 | 0.51 |
| 31 | 16 | 0.48 |
| 37 | 10 | 0.30 |
| 28 | 8 | 0.24 |
| 23 | 8 | 0.24 |
| 4 | 7 | 0.21 |
| 8 | 6 | 0.18 |
| 34 | 5 | 0.15 |
| 20 | 4 | 0.12 |
| 5 | 3 | 0.09 |
| 24 | 3 | 0.09 |
| 1 | 3 | 0.09 |
| 3 | 2 | 0.06 |
| 26 | 1 | 0.03 |
| 12 | 1 | 0.03 |
| 6 | 1 | 0.03 |
| 33 | 1 | 0.03 |
| 27 | 1 | 0.03 |

## Where the scanner objects most

- **Marketing & content** — 4 flagged
- **Management & strategy** — 2 flagged
- **Software engineering** — 2 flagged
- **Startups & venture** — 1 flagged

---

Regenerate with `python3 tools/baseline.py`. Score a draft against it with `python3 tools/baseline.py --compare path/to/draft.md`.
