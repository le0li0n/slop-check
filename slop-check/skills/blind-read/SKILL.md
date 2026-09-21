---
name: blind-read
description: Judge two or three versions of the same piece with a reader who cannot see which is which. Use when the user asks "is this version better", after rewriting or editing a draft, or whenever someone needs to know whether an edit actually improved the writing rather than just changing it.
---

# Blind read

The person who made an edit is the worst judge of it. So is the model that made it. Both know which version is the new one, and both will find reasons the new one is better.

This is the cheapest fix: hand the versions to a reader who has none of that context, and see which one it picks.

In the session this came from, the blind reader overturned the verdict three times. Each rewrite scored better on the scanner, sat inside the human range on every prose-shape measure, and kept every fact. A reader seeing them unlabeled called the first one "the draft put through a de-voicing pass", the second "a list run through a converter", and ranked the third last of three, behind the untouched original. Without the blind read, all three would have shipped as improvements.

## 1. Stage the files

Copy each version to a scratch directory under neutral names: `version-A.md`, `version-B.md`, `version-C.md`. Randomize which letter gets which version, and vary it between runs so a habit cannot form.

Strip nothing else. Both versions keep their formatting, so the reader sees what a reader would see.

## 2. Spawn a reader with no context

Use a subagent, which starts with none of this conversation. Give it the paths and the questions. Tell it to use no tool except Read.

Never say which version is the original, that any version was rewritten, what was changed, or why. Do not name the author, the style, or the goal. A single hint about which is new and the answer is worthless.

## 3. Ask the same questions every time

Consistent questions make runs comparable:

1. Which version reads as though a person wrote it, rather than being generated? Quote two or three passages from each that drove the judgment.
2. Which has the more distinctive point of view, meaning an argument with a position and an opponent rather than balanced coverage?
3. Does either read as an imitation of a particular writer, or as a style exercise rather than a piece of writing? If so, what gave it away?
4. Which would you rather read, and why?
5. Name the differences that matter most to a reader, and say which version handles each better.
6. Anything that struck you as off: a claim that does not follow, a sentence that trips, a tic that repeats, an analogy that breaks under inspection.

Require quoted evidence throughout. An unquoted verdict cannot be checked.

Add a line about length where the versions differ in size, for example that brevity is a feature of this piece, so words that add nothing make a version worse.

## 4. Report what it said, including the parts you dislike

Give the user the verdict, which version the reader picked, and its reasoning in its own words. Never soften a result because the edit was yours.

Three results are all worth having:

- **The edit wins.** Report the reasons, since they tell you what to do more of.
- **The original wins.** The edit failed. Say so plainly and offer to revert.
- **The reader cannot tell them apart.** The edit changed the writing without improving it, which is its own answer.

## Watch for

- **Near-identical versions.** When the texts overlap heavily, the reader judges a small number of words. Ask it to say what fraction differs, so the verdict is read in proportion.
- **Length bias.** A longer version looks more substantial. Tell the reader what the piece is for, so it can weigh added words honestly.
- **One reader is one opinion.** Two readers disagreed about the same pair in the session this came from, and that disagreement was the finding: the improvement was real but marginal. Run a second reader when a verdict decides something expensive.
- **Editorial gold.** Blind readers keep finding defects that predate the edit: contradictions between sections, load-bearing claims with no evidence, figures with no denominator. Pass those to the user even though nobody asked.
