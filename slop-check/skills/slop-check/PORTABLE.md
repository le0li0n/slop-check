---
name: slop-check
description: Check writing for AI tells before it is sent or published, then fix what is real. Use when asked whether something "sounds like AI" or "reads as AI-written", and before any draft goes to a customer, partner, or the public.
---

# Slop check

A gate in front of sending. Two passes: first find candidate tells using the lists below, then judge each one. The lists match literal strings and shapes, so they cannot tell a habit from a choice. A hit is a place to look, not a thing to delete.

## How to score

Hard: an unambiguous chatbot artifact. Always fix.
High, Med, Low: signal weights (roughly 3, 2, 1). One tell proves nothing. Several different tells in the same passage are the evidence. A text reads as AI-written when hard tells appear, or when the weighted total across at least three or four different patterns is clearly high. The same pattern repeated eight times is one habit, not eight problems, so cap each pattern's contribution.

Current model output rarely uses the classic words (delve, tapestry). It argues by negation, withholds payloads, and stages its reveals. Weight the structural families (negation, withheld reveal, announced points) above the vocabulary list.

## Hard tells (fix every one)

- Chatbot artifacts: "I hope this helps", "Would you like me to", "Want me to", "Should I continue", "Certainly!", "Of course!", "You're absolutely right", "As of my last knowledge/training", an opening line like "Here's a breakdown/overview/summary of".
- Outreach manipulation: "just curious" (frames a real request as idle interest so the reader does not brace).
- The hidden-knowledge promise: "the pattern nobody names", "the thing nobody talks about", "what they don't tell you", "nobody tells you". It promises a secret and never has one. Applies to "nobody / no one / everyone" plus a verb of disclosure (names, mentions, tells, admits, discusses, acknowledges, notices, misses, sees).
- "Same shape" as a stand-in for naming the pattern two things share.
- "X is doing real work" / "doing genuine work" / "doing heavy work": say what it does.

## Negation and contrast (strongest family)

- Two-beat negation: state what a thing is not, then restate what it is. "It isn't X, it's Y." "That's not a feature. It's a platform." Lead with what it is. High.
- "It's not just / only / merely / about X, but Y." Low to Med.
- The antithesis epigram: "I don't think that's a ceiling. I think it's an order." The second half is asserted, not argued. High.
- "None of this is / means / changes..." The pivot to a conclusion after clearing the table. High.
- "This isn't about", "I'm not saying", "I'm not arguing", "Don't get me wrong", "This is not to say", "To be clear,", "Some might say". Answering objections nobody raised. High to Med.
- "A tempting option would be", "One might be tempted to", "An obvious approach would be", "You might think X, but", "It would be easy to just". Rejecting alternatives nobody proposed. High to Med.
- Aphoristic restatement: "A gate that can't run in a bare script is a gate that gets skipped." The same noun on both sides of "is". High. Plain statements of fact with the same noun ("the date on the card is the date on the page") are fine.
- "X, not Y" as a default sentence shape (density rule, below).
- "rather than" as the default way to draw every contrast (density rule, below).

## Withheld reveals and staged payloads

- "The part that / which / where...", "the bit that...": a slot where the noun should be. Name the thing. High. "The part of the process that fails" is fine; naming what the part belongs to is the fix.
- Crowd-miss constructions: "the step most people skip", "the thing most founders overlook", "that's what most people miss", "the detail so many teams forget". An unnamed crowd stands in for evidence that the reader is about to be smarter than them. Say what it is and why it matters. Med. "The mistake many organizations make" is ordinary prose and is left alone.
- "The part no tool supplies", "the thing no model can replace", "the one piece no AI gives you": the human contribution is called special and never named. Say what it is. Med, because the literal version is a plain fact: "email is the one thing no enrichment tool returned" stays.
- "But here's the thing", "Here's the thing", "The thing is,", "The thing is / that matters / worth...", "Here's the kicker / catch / twist", "The real question is", "What really matters", "At its core,", "The deeper issue", "The heart of the matter", "In reality,". Say it.
- "The one that didn't:" followed by a name. "The ones who win / lose / survive..." sorting the world into two kinds of people.
- "The uncomfortable / inconvenient / hard truth", "hiding in plain sight", "the dirty / open secret". High.
- "That's the whole point", "That's exactly the point". Med.
- "The honest take / version / answer / truth / read / assessment / counterweight": claiming candor instead of demonstrating it. Also with intensifiers ("the most honest public read"). Med. Ordinary uses ("an honest mistake", "be honest with yourself") are fine.
- Fake-candid openers: "Honestly?", "Look,", "Let's be honest", "Real talk". High.
- "Which is why" as a sentence connector. Low.
- "Failure mode" as a label. Med. It is real engineering vocabulary; the tell is the reach for it, not the term.
- "On day one" / "from day one" as an idiom for "immediately". Med. "Day one of the cohort" is literal and fine.
- "Shape" in place of a specific noun: "a familiar shape", "the shape of this". Not the bare word ("the shape of the curve").
- "Earns its keep" / "earned its keep" / "earning their keep", with a tool, a feature or a sentence as the subject: say what it does. High. Only with "its" or "their"; "he earned his keep" is usually a person and often literal. "Pulls its weight" is the same move at Med.
- "What ... actually": "what customers actually want", "what's actually happening", "what the data actually shows". It sets the sentence against a wrong version nobody put forward. Med. Drop "actually", or name what it is being contrasted with.

## Announcing the next point

- "Let's dive in / explore / break this down / unpack / get into", "Here's what you need to know", "Without further ado", "Now let's look at". High to Med.
- Counted preambles: "Two things to sit with", "Three things to consider / note / keep in mind", "Here are three key takeaways", "sit with that". Just say the things.
- "Some surprising / exciting / interesting news", "You might find this fascinating". Lead with the news; let them decide.
- "What's worth noting here is", "What's interesting here is", "It's worth noting", "It is important to note that". Cut.
- "[Subject] keeps coming back to / returning to [X]": stages a thought as hard-won. Say X.
- "Is top of mind". Say the thing itself.
- "Quick note:", "Heads up:", "Before I forget".
- "Great question", "Let me know if": Med. Chatbot-flavored, but real people write them to a reader.

## Inflation, sales language, vague authority

- Importance claims: "stands/serves as", "is a testament to", "vital / crucial / pivotal / key role", "underscores its importance", "reflects a broader...", "setting the stage for", "marks a shift / turning point", "evolving landscape", "indelible mark", "deeply rooted", "focal point".
- Name-dropping to prove importance: "active social media presence", "local/regional/national media outlets", "independent coverage". Name the outlet or give the number.
- Sales words: "boasts", "nestled", "in the heart of", "breathtaking", "must-visit", "stunning", "renowned", "groundbreaking", "world-class", "game-changer", "rich history / heritage / tapestry", "commitment to excellence / quality / innovation", "exemplifies".
- Vague sources: "experts say", "industry reports suggest", "observers have noted", "some critics argue", "it is widely believed that", "studies show". Name the source or cut the claim.
- Formulaic challenge or outlook paragraphs: "Despite its challenges", "faces several challenges", "continues to thrive / grow / evolve", "the future looks bright", "exciting times ahead", "a step in the right direction", "only time will tell", "a journey toward excellence". End on the last real fact.
- Formulaic sayings: "X is the language / currency / backbone / new [thing] of Y", "becomes a trap", "not a ___ but a mirror / map / mindset".
- False ranges: "from X to Y, from A to B", "everything from X to Y". List the items.
- Knowledge-limit hedging: "while details are limited", "based on available information", "maintains a low profile", "it is believed that".

## Vocabulary

High: delve, tapestry, testament.
Med: underscore, showcase, intricate/intricacies, interplay, pivotal, foster, garner, seamless, robust (say what it withstands). "Leverage" as a verb (leverage the platform); the noun is ordinary business vocabulary ("the highest-leverage hire") and should not be flagged.
Low: enhance, crucial, align with, landscape, quietly, vibrant, "unlock potential/value/growth", sentence-opening "Additionally, / Moreover, / Furthermore,".
A capitalized watched word mid-sentence may be a product or company name (the vendor Seamless.AI). Not a tell.

## Filler and hedging

"Due to the fact that" (because), "at this point in time" (now), "in the event that" (if), "has the ability to" (can), "needless to say", "could potentially", "might arguably", "in some cases it may", "it's also possible", "no guessing / hassle / fuss / surprises / extra steps" as a clipped trailing clause. "Features / offers / represents a shift" instead of "has / is". Participial tails that add commentary instead of fact: ", highlighting...", ", underscoring...", ", ensuring...", ", reflecting...", ", fostering...", ", showcasing...", ", contributing to...". End the sentence at the fact.

## Outreach openers (email and DMs)

"I wanted to reach out", "circling back", "hope you're doing well". Open with the ask.

## Density rules (one is normal; the rate is the tell)

- Em and en dashes (including a "--" attached to a word): in a text of 120+ words with three or more, flag when there is one per 200 words or more often. High at one per 100. Aim for about one per 500 words. Fix with a period first, then a colon, then a comma. Editors use dashes; a single one proves nothing.
- "X, not Y" closings: about 2 per 10,000 words is typical human prose; machine-heavy text runs 15 or more. Flag at 8+ per 10k (400+ words, four or more instances).
- "Rather than": human 1.8 per 10k words, machine 14.5. Flag at 8+ per 10k (400+ words, four or more instances).
- "Actually" and "real" as default emphasis ("the real constraint", "a real replica", "what it actually means"): human 8.8 per 10k words combined, machine 45.6, and the typical human document uses neither. Flag at 40+ per 10k (200+ words, three or more instances). High at 60. Do not count "real-time", "real estate" or "real world". Cut most of them; the sentence usually stands without the word. Keep one where the thing it contrasts with is named. Do not swap in "really", "very" or "in fact": that moves the tell.
- Lists of three: a habit when three or more triples appear in a short piece. Some ideas come in twos and fours.
- Repeated sentence openers: four or more sentences in one paragraph starting with the same word.
- Runs of dramatic fragments: four or more sentences of four words or fewer in a row. One short sentence landing is fine; a row is staging.
- Bold-label lists: three or more items that are "**Label** — sentence" or "**Label:** full sentence". Write it as prose or drop the labels. Reference docs that bold field names on purpose are fine.
- Bold as decoration: only when most lines are saturated with it.
- Stock hyphenated pairs (cross-functional, data-driven, end-to-end, best-in-class, battle-tested, first-class, long-term, real-time, and similar): four or more in a piece.
- Emoji leading headings or list items (not mid-sentence).
- Title Case headings below H1: capitalized "And / Of / The" plus mostly capitalized words. Use sentence case.
- A heading whose first sentence underneath only repeats the heading.
- No first person in a piece of 400+ words: a model has no war stories and writes from nowhere. Low, and only a prompt to check; plenty of good writing is deliberately third-person. The fix is the thing only the writer saw: what they tried, what it cost, who said what.

## Judge before cutting

This is the part that matters, and the part that gets skipped. A text scrubbed to zero hits can still read like a chatbot. Before deleting anything:

- A repeated sentence opening can be rhythm the writer chose. "She came. She saw. She conquered."
- Em dashes and curly quotes prove nothing. Curly quotes are applied automatically by word processors; do not flag them at all.
- Never flag dialect. British spellings, "towards", "whilst" are author voice, not slop.
- One short sentence for emphasis is fine. A row of them is the tell.
- Formal words are not AI words.
- Real limits, disclaimers, and named objections stay. So do real alternatives in a design doc or tutorial.
- A watched phrase inside a quotation, a title, a code block, or a "don't write this" list is being discussed, not used. Skip it.
- Specific unusual details, mixed feelings, dated references, and uneven sentence length are what make writing sound like a person. Keep them.

## Fix by rewriting, not patching

Rewrite the paragraph around its point. Patching one flagged phrase at a time produces sentences that dodge the pattern and keep the rhythm, which is the thing being detected. Say the thing plainly, once, in the order a person would say it.

Never invent a fact to make text sound human. If a sentence needs a detail that is not in the source, ask for it or write a simpler sentence.

## Report

List what you changed and what you left, with the reason for anything left. A finding you decided against is information; silence about it is not.

## Adding a tell

Make it HARD only for objective errors and unambiguous artifacts. Anything a real writer might do on purpose goes in the weighted set. Test both directions before adopting a pattern: phrases that should flag, and ordinary sentences that should not. Every pattern that over-matched was caught this way, not by reading it.
