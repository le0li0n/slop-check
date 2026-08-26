# slop-check

A scanner for writing that reads as AI-written, plus the discipline for using it without sanding good prose flat.

139 patterns, no third-party dependencies, one file. Built on [humanizer](https://github.com/blader/humanizer) and Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — see [`ATTRIBUTION.md`](./ATTRIBUTION.md). It **warns and never blocks**, because slop is a judgment call and a gate that fires on judgment calls gets bypassed until nobody reads it.

## Install

Add the marketplace, then the plugin:

```
/plugin marketplace add <this-repo-url>
/plugin install slop-check@slop-check
```

That wires up three things: a `PostToolUse` hook that flags Claude's writes to outward-facing files, the `/slop-check` skill as the gate before sending, and the scanner itself as a CLI.

Run it by hand any time:

```
python3 hooks/ai_slop.py path/to/file.md
python3 hooks/ai_slop.py --all docs/
```

## Configure per repo

Drop a `.slopcheck.json` at the repo root:

```json
{
  "outward":     ["marketing/", "partnerships/"],
  "never":       ["notes/"],
  "suffixes":    [".md", ".txt"],
  "fix_command": "/slop-check"
}
```

With no config file **everything is scanned** except build output, dependencies and `.claude/`. That is deliberate — a fresh install should do something on day one. Narrow it once you know which directories are genuinely outward-facing, because a scanner that shouts about internal notes gets muted, and a muted scanner is not a check.

`fix_command` is what the report footer tells the reader to run. Set it if your repo wraps this in a skill of its own name.

## Vendoring instead of installing

A shared repo is often better off with a copy of `hooks/ai_slop.py` committed to it than with a plugin dependency. Two reasons, both learned the hard way:

**Git hooks cannot reach a plugin.** `pre-commit` runs in a bare shell with no Claude Code context, so `${CLAUDE_PLUGIN_ROOT}` is undefined. A repo that checks prose on commit needs the file at a path it controls.

**Teammates would each have to install it.** Anyone who clones and does not gets no checks, silently, which is worse than no checks at all.

So copy the file in, and record where it came from — upstream URL, commit, and a one-line re-sync command. Keep it unmodified so the re-sync is an overwrite rather than a merge, and put everything repo-specific in `.slopcheck.json`. That is the whole reason the config file exists.

Internal writing should stay out of scope on purpose. "Not a team. A person." is good writing for colleagues, and running a slop check over it would sand it down.

## Call it from a build script

Anywhere prose is compiled from source — an ebook built from per-chapter markdown, a newsletter assembled into a sendable, a static site — check the **source**, not the output. That is where the writing and the editing happen. Compiled HTML flags the same prose a second time and adds markup noise.

Add it to whatever does the compiling:

```python
subprocess.run([sys.executable, "path/to/ai_slop.py", *chapter_files])
```

Then the book cannot be built through a path where nobody looked. **Warn, don't fail** — a build that breaks on a judgment call gets bypassed, and then nothing is checked at all.

This matters most for long-form. In an email the risk is one bad sentence, and you would probably catch it. Across forty thousand words the risk is a house style drifting while nobody reads the whole thing at once, which is exactly the failure a per-file scanner is good at and a human proofreader is not.

## What it looks for

| Section | Tells |
|---|---|
| §1–§35 | Wikipedia's "Signs of AI writing" — inflated importance, vague sourcing, formulaic outlook sections, the overused-word list, the "it's not just X, it's Y" construction |
| `GB` | British spellings in American copy. Hard, because it is an objective error and one alone has to fire |
| `OUT` | B2B outreach openers: "just curious", "circling back", "I wanted to reach out", "hope you're doing well" |
| `CL` | Phrases Claude reaches for constantly |

`CL` is the section worth explaining. These are not slop exactly — a model reaches for them so often that anyone working with one every day clocks them instantly in published writing:

- **The hidden-knowledge construction.** "The pattern nobody names", "what they don't tell you", "the part everyone misses". It promises a secret and the secret is never a secret. Matched by skeleton rather than by string, because the surface forms are unlimited.
- **The aphoristic restatement.** "A gate that can't run in a bare python3 is a gate that gets skipped." The repeated noun either side of "is" is the marker. The second half rarely adds information; it restates the first with a consequence attached, and the symmetry makes it sound earned.
- **"Shape"** standing in for a specific noun. "Same shape all three times" rather than naming the pattern the three share. Only the abstract forms match: "the shape of the curve" is fine, and "AGI-shaped hammer" is good writing.
- **"X is doing real work"**, praising a sentence for pulling its weight instead of saying what it does.

## A hit is a place to look, not a thing to delete

The scanner matches literal strings and paraphrase walks straight past it. Grep first, then read for the pattern.

It cuts the other way too, and this is the part to read before deleting anything:

- A repeated sentence opening can be rhythm the writer chose. "She came. She saw. She conquered."
- Em dashes and curly quotes prove nothing on their own. Editors use dashes; macOS, Word and Google Docs curl quotes automatically.
- One short sentence for emphasis is fine. A row of them is the tell.
- Formal words are not AI words.
- Real limits, disclaimers and named objections stay. So do real alternatives in a design doc or a tutorial.
- A watched phrase inside a quotation, a title, or a "don't write this" list is being discussed rather than used. The scanner masks short quoted spans for exactly this, and still misses cases.

Specific unusual details, mixed feelings, dated references and uneven sentence length are what make writing sound like a person. Keep them.

**Rewriting prose until a regex goes quiet produces text that passes the check and still sounds like a chatbot.** Rewrite the paragraph around its point instead of patching phrase by phrase.

## Adding a tell

Edit `LINE_PATTERNS` in `hooks/ai_slop.py`. Keep `HARD` for objective errors and unambiguous artifacts only — everything a real writer might do on purpose belongs in the weighted set. Em dashes, curly quotes and emoji were all hard in the first cut and flagged every file, which is the same as flagging none of them.

**Test both directions before committing a pattern**: the phrases that should flag, and the ordinary sentences that should not. Every over-matching pattern in this file was caught that way rather than by reading it. `organis` also matches "organism"; `analys` also matches "analysis"; a repeated-noun rule with no guard eats "the date on the card is the date on the page".

## Provenance and licence

**Most of the patterns here are not original.** Sections §1–§35 come from [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), by way of [blader/humanizer](https://github.com/blader/humanizer) by Siqi Chen, which organised them into the numbered sections every scan report still references.

What is original: the scanner itself — scoping, weighting, thresholds, quote masking, config — and three pattern sections (`GB`, `OUT`, `CL`).

Because §1–§35 derive from CC BY-SA material, this repo is **CC BY-SA 4.0**. Full detail, including what changed from upstream and why, in [`ATTRIBUTION.md`](./ATTRIBUTION.md).
