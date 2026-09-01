# A corpus of human B2B writing, published before 2012

Business and technology writing from well-regarded authors, every piece published before 2012-01-01 — before large language models had any hand in prose. It exists to answer one question honestly: **what does human writing actually look like?** Without that, "this reads like AI" is a hunch, and a slop scanner is a list of someone's pet peeves.

Use it to calibrate. Run [`ai_slop.py`](../slop-check/hooks/ai_slop.py) over the corpus and any pattern that fires constantly is not an AI tell — it is English, and flagging it costs you a good sentence. Patterns that stay silent across hundreds of thousands of words of human prose are the ones worth acting on. [`BASELINE.md`](./BASELINE.md) is that measurement.

## Layout

```
texts/<author-slug>/<YYYY-MM-DD>--<title-slug>.txt
manifest.json      every document with its metadata
BASELINE.md        how each pattern behaves on human prose
tools/             the harvester, the analyser, the checks
```

Each `.txt` opens with a metadata header, then a blank line, then the prose:

```
---
author: Paul Graham
title: Why Startups Condense in America
date: 2006-05-01
date_basis: dateline
type: essay
area: Startups & venture
source_url: http://paulgraham.com/america.html
archived_url: https://web.archive.org/web/20060601205746id_/http://...
retrieved_from: live site
words: 4740
retrieved: 2026-08-27
---
```

Anything reading these files should drop everything up to and including the second `---`. `tools/baseline.py` has a `strip_front_matter` that does it in four lines.

## How the pre-2012 cutoff is enforced

A date on a live page proves nothing — the page may have been edited last week. So the cutoff is enforced three times, at three different points.

**1. Discovery admits nothing newer.** Every candidate is found through the Wayback Machine's CDX index restricted to captures taken before 2012-01-01. A URL with a 2011 capture is proof that page existed in 2011, whatever the live site says today.

**2. Every document must date itself.** Text is fetched from the live site, because modern markup extracts far more cleanly than a 2004 capture. But it is kept only if the page carries its own pre-2012 date — in the permalink (`/2009/05/`), in its metadata, or in a dateline the author wrote. `date_basis` records which. Undated pages are dropped, and that rule matters more than it looks: a dead permalink quietly serving today's author-bio page still returns 200 with plausible prose on it, and dropping undated pages is what keeps those out.

**3. The prose is checked for things it could not have known.** A 2003 post mentioning 2025 is either a page that changed under us or a footer that survived extraction. Either way it goes. `tools/prune.py` re-applies this to the whole corpus, so a document collected before a rule tightened does not outlive the rule.

The cutoff lives in one constant, `CUTOFF` in `tools/corpuslib.py`.

## Rebuilding

```
python3 tools/build.py --discover-only    # warm the permalink cache
python3 tools/build.py --live-only        # fetch, extract, gate, write
python3 tools/prune.py --apply            # re-check the corpus, rewrite the manifest
python3 tools/verify.py                   # confirm it keeps its promises
python3 tools/baseline.py                 # regenerate BASELINE.md
```

Run discovery and fetching apart. Heavy CDX use makes the archive throttle for a while afterwards, and running the two together drops the yield sharply — that is what the flag is for.

`--live-only` skips the archive fallback. The archive's replay endpoint rate-limits to roughly one request at a time and answers 503 to the rest, so a bulk run through it takes hours; the live web does the same work in minutes. The fallback is still there for a small top-up, with `--budget` to bound how long any one author may take.

Both phases are resumable and cache every response under `cache/`, so a re-run costs almost nothing and fetches only the shortfall. Adding authors to `tools/sources.py` and re-running touches only the new ones.

### When an author yields nothing

`tools/sample_urls.py <slug>` prints the raw URLs the archive holds, and `tools/why_zero.py <slug>` walks the first few candidates through every gate and says where each one died. Most failures are one of three things: the permalinks carry no date and need a pattern in `PERMALINK_SHAPES`, the site has moved and its old URLs 404, or the domain is gone. The first is worth fixing; the last two are not.

## What is in it

**382 documents, 330,288 words, 62 authors**, spanning 1995 to 2011 — startups and venture, software engineering, marketing and content, management and strategy, design and product, technology and media, and sales. 53 authors have five pieces or more; the rest are kept because they are still genuine pre-2012 human prose, and the baseline is measured per word, not per author.

Paul Graham, Joel Spolsky, Martin Fowler, Jakob Nielsen, Fred Wilson, Steve Blank, Eric Ries, Dave Winer, danah boyd, Nicholas Carr, Rand Fishkin, Avinash Kaushik, Doc Searls, Tim Bray, John Gruber, Aaron Swartz, and around forty-five others.

## What it already tells us

From the first run of `BASELINE.md`, on writing that predates the models entirely:

- **24% of it trips the scanner.** That is the false-positive rate on human prose, and the number to drive down.
- **Curly quotes fire in 293 of 382 documents.** Every publishing platform of the era converted quotes automatically. As an AI tell this is close to noise.
- **"In order to", "when it comes to", "towards", "landscape", "robust", "leveraging"** all appear in ordinary pre-2012 business writing. A draft containing them has not thereby been caught.
- The median human document scores **3** against a threshold of 8 — so the threshold is roughly in the right place, and the damage is concentrated in a few patterns rather than spread across all 139.

These are working documents, not literature: blog posts, essays, articles and a manifesto, mostly written fast by people with something to say. They contain typos, ragged transitions, jokes that did not land, and sentences that run on. That is the point. A corpus of polished prose would teach the scanner to flag anything with a rough edge, which is the failure mode worth avoiding — the one where every draft gets sanded until it reads like everything else.

## Provenance and use

Every document records its `source_url` and `archived_url`, so any passage can be traced to the page it came from. The texts are here for measurement — counting how often a phrase occurs in human writing — not for redistribution. Copyright rests with the authors.
