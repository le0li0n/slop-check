---
name: slop-check
description: Check writing for AI tells before it is sent or published, then fix what is real. Runs the scanner, judges the hits against the false-positive rules, and rewrites. Use when the user says "/slop-check", asks whether something "sounds like AI" / "reads as AI-written" / "smells of AI", or before any draft goes to a customer, partner, or the public.
---

# Slop check

The gate in front of sending. Two passes: the scanner finds candidates, then you judge them — because the scanner matches literal strings and cannot tell a habit from a choice.

## 1. Run it

```
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/ai_slop.py" <file> [more files...]
```

Or `--all <dir>` for every `.md` beneath a directory, `--json` for machine-readable output.

**Check what the file list actually contains before reading the scores.** `--all` walks
everything, including files no reader will ever see: build artifacts that concatenate the
real sources (these score highest, because every finding in them is a duplicate), superseded
drafts, raw interview transcripts, and internal briefs. Score a generated file and you will
"fix" the same sentence twice, in the wrong place, and the next build will overwrite you.
Work out which files are sources and which are output first.

## 2. Read the two kinds of finding differently

**`x` — hard.** A chatbot artifact ("I hope this helps"), a British spelling in American copy, or one of the constructions that only ever promises and never delivers. Fix these.

**`.` — signal.** Weighted, and only reported once a file clears the threshold. One tell proves nothing. Several different ones in the same passage are the evidence. A single pattern cannot carry a file over the threshold by repetition, because a word used eight times is one habit rather than eight problems.

## 3. Judge before cutting

**This is the part that matters, and the part that gets skipped.** A scanner run to zero produces text that passes the check and still reads like a chatbot. Before deleting anything:

- **A repeated sentence opening can be rhythm the writer chose.** "She came. She saw. She conquered."
- **Em dashes and curly quotes prove nothing.** Editors use dashes; macOS, Word and Google Docs curl quotes automatically.
- **One short sentence for emphasis is fine.** A row of them is the tell.
- **Formal words are not AI words.**
- **Real limits, disclaimers and named objections stay.** So do real alternatives in a design doc or a tutorial.
- **A watched phrase inside a quotation, a title, or a "don't write this" list is being discussed, not used.** The scanner masks short quoted spans for this reason and still misses cases.

Specific unusual details, mixed feelings, dated references and uneven sentence length are what make writing sound like a person. Keep them.

## 4. Fix by rewriting, not patching

Rewrite the paragraph around its point. Patching one flagged phrase at a time produces sentences that dodge the pattern and keep the rhythm, which is the thing being detected.

**Varying a tic means varying it.** Swapping every "failure mode" for "the trap"
moves the tic rather than removing it, and swapping every "honestly" for
"candidly" is the same mistake with a thesaurus. If a phrase appears eight
times, it needs eight decisions — and check afterwards that your replacement
has not itself become the new repeat, or that it does not collide with a word
another chapter is using deliberately.

**Never invent a fact to make text sound human.** If a sentence needs a detail that is not in the source, ask for it or write a simpler sentence.

## 5. Report

Say what was changed and what was left, with the reason for anything left. A finding you decided against is information; silence about it is not.

## Adding a tell

Edit `LINE_PATTERNS` in `hooks/ai_slop.py`. Weight it `HARD` only for objective errors and unambiguous artifacts — everything a real writer might do on purpose belongs in the weighted set. Em dashes, curly quotes and emoji were all hard in the first cut and flagged every file, which is the same as flagging none of them.

**Test both directions before committing a pattern.** The phrases that should flag, and the ordinary sentences that should not. Every pattern in the file that over-matched was caught this way and not by reading it.
