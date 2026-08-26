#!/usr/bin/env python3
"""AI-slop tells for outward-facing writing — THE single source of truth.

Edit the pattern tables HERE and nowhere else. Four callers use this module so
there is one list to maintain:
  - .claude/hooks/check-slop.py     (PostToolUse hook — flags Claude's writes)
  - .githooks/pre-commit            (git hook — advisory warning on human commits)
  - the slop-check skill            (the gate — runs the CLI, then judges)
  - a human, from the terminal

Run directly:
    python3 ai_slop.py path/to/file.md [more.md ...]
    python3 ai_slop.py --all marketing/content/execution   # every .md beneath
    python3 ai_slop.py --json file.md                      # machine-readable

Exit 1 if any file is flagged, else 0. No third-party deps.

WHAT THIS IS NOT: a verdict. The scanner matches literal strings, and paraphrase
walks straight past it — the same failure `.claude/rules/partner-agreements.md`
records for its own tell list. A hit is a place to look, not a thing to delete.
The false-positive rules live in the README. Read them before cutting.

Pattern numbering (§n) tracks the `humanizer` skill's sections, so a hit here
points at the explanation and the before/after there.

ATTRIBUTION: sections §1-§35 derive from Wikipedia's "Signs of AI writing"
(CC BY-SA 4.0, WikiProject AI Cleanup) by way of github.com/blader/humanizer
(MIT, (c) 2025 Siqi Chen). Sections GB, OUT and CL are original, as is this
implementation. Released under CC BY-SA 4.0 -- see ATTRIBUTION.md.
"""
import argparse
import glob
import json
import os
import re
import sys

# ─── Scope: what counts as "sent or published" ─────────────────────────────
# Configure per repo with a .slopcheck.json at the repo root:
#
#   {
#     "outward":  ["marketing/", "partnerships/"],
#     "never":    ["notes/"],
#     "suffixes": [".md", ".txt"]
#   }
#
# With no config file, everything not in NEVER_PREFIXES is scanned. That is
# deliberate: a fresh install should do something on day one. Narrow it once
# you know which directories are actually outward-facing, because a scanner
# that shouts about internal notes gets muted.
OUTWARD_PREFIXES = ("",)
# Never scanned, whatever the config says. Build output, dependencies, and
# the places a repo keeps its own scaffolding.
NEVER_PREFIXES = (
    ".git/",
    ".github/",
    ".claude/",
    "node_modules/",
    "vendor/",
    "dist/",
    "build/",
)
NEVER_BASENAMES = {"CLAUDE.md", "README.md", "INDEX.md", "AGENTS.md", "CHANGELOG.md"}
SCANNED_SUFFIXES = (".md", ".txt")
# Named in the report footer, so a repo can point at its own gate skill.
FIX_COMMAND = "/slop-check"
# Where the false-positive rules live, named in the report footer.
RULES_DOC = "the README"

TOP_LEVEL_DIRS = set()


def _load_config(start_dir=None):
    """Read .slopcheck.json from the nearest ancestor that has one."""
    global OUTWARD_PREFIXES, NEVER_PREFIXES, SCANNED_SUFFIXES, TOP_LEVEL_DIRS, FIX_COMMAND, RULES_DOC
    d = os.path.abspath(start_dir or os.getcwd())
    while True:
        candidate = os.path.join(d, ".slopcheck.json")
        if os.path.isfile(candidate):
            try:
                with open(candidate, encoding="utf-8") as fh:
                    cfg = json.load(fh)
            except Exception:
                return  # a broken config must not take the scanner down
            if cfg.get("outward"):
                OUTWARD_PREFIXES = tuple(cfg["outward"])
            if cfg.get("never"):
                NEVER_PREFIXES = NEVER_PREFIXES + tuple(cfg["never"])
            if cfg.get("suffixes"):
                SCANNED_SUFFIXES = tuple(cfg["suffixes"])
            if cfg.get("fix_command"):
                FIX_COMMAND = cfg["fix_command"]
            if cfg.get("rules_doc"):
                RULES_DOC = cfg["rules_doc"]
            TOP_LEVEL_DIRS = {p.strip("/").split("/")[0]
                              for p in OUTWARD_PREFIXES + NEVER_PREFIXES if p}
            return
        parent = os.path.dirname(d)
        if parent == d:
            return
        d = parent


# ─── EDIT HERE — the tells ─────────────────────────────────────────────────
# HARD  = an unambiguous chatbot artifact, or an objective error such as a
#         British spelling in American copy.
#         Always reported, whatever else the file scores.
# 3/2/1 = signal weight. Reported once the file's total clears THRESHOLD,
#         because one tell proves nothing and several together do.
#
# Keep the HARD list short. Everything that a real writer might do on purpose
# belongs in the weighted set: em dashes, curly quotes, and emoji were all HARD
# in the first cut and flagged every file in the repo, which is the same as
# flagging none of them.
HARD, HIGH, MED, LOW = "hard", 3, 2, 1
THRESHOLD = 8
# No single pattern can carry a file over the threshold on repetition alone.
SECTION_SCORE_CAP = 6
# Findings shown per section per file, before collapsing to "... n more".
SECTION_REPORT_CAP = 3

_load_config()

# (section, weight, pattern, what to do instead)
LINE_PATTERNS = [
    # §1 Inflated claims about importance and legacy
    ("1", MED,  r"\b(?:stands|serves) as (?:a|an|the)\b", "say what it is"),
    ("1", HIGH, r"\b(?:is|as) a testament to\b", "state the fact, not its meaning"),
    ("1", MED,  r"\b(?:vital|crucial|pivotal|key) (?:role|moment|turning point)\b", "cut, or say what changed"),
    ("1", HIGH, r"\bunderscor(?:es|ing) (?:its|the) (?:importance|significance)\b", "cut"),
    ("1", MED,  r"\breflects? (?:a )?broader\b", "cut the trend claim"),
    ("1", MED,  r"\bsymboliz(?:es|ing) its\b", "cut"),
    ("1", MED,  r"\bsetting the stage for\b", "say what happened next"),
    ("1", MED,  r"\bmark(?:s|ing|ed) a (?:shift|turning point|new era)\b", "say what changed"),
    ("1", HIGH, r"\bevolving landscape\b", "name the thing that is changing"),
    ("1", HIGH, r"\bindelible mark\b", "cut"),
    ("1", LOW,  r"\bdeeply rooted\b", "cut or be specific"),
    ("1", LOW,  r"\bfocal point\b", "cut"),

    # §2 Name-dropping to prove importance
    ("2", HIGH, r"\bactive social media presence\b", "cut, or give the number that matters"),
    ("2", MED,  r"\b(?:local|regional|national) media outlets\b", "name the outlet"),
    ("2", LOW,  r"\bindependent coverage\b", "name the coverage"),

    # §3 Shallow analysis with -ing phrases
    ("3", MED,  r",\s+(?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|cultivating|fostering|encompassing|showcasing|contributing to)\b",
                "end the sentence at the fact"),

    # §4 Sales language
    ("4", HIGH, r"\bboasts? (?:a|an|over|more than)\b", "use has"),
    ("4", HIGH, r"\bnestled\b", "say where it is"),
    ("4", MED,  r"\bin the heart of\b", "say where it is"),
    ("4", MED,  r"\b(?:breathtaking|must-visit|stunning|renowned|groundbreaking)\b", "cut the adjective"),
    ("4", HIGH, r"\bcommitment to (?:excellence|quality|innovation|our (?:students|partners))\b", "show it or cut it"),
    ("4", MED,  r"\brich (?:history|heritage|tradition|tapestry)\b", "give the detail"),
    ("4", MED,  r"\bexemplifies\b", "use is or shows"),
    ("4", MED,  r"\bworld-class\b", "cut or substantiate"),
    ("4", MED,  r"\bgame[- ]chang(?:er|ing)\b", "say what it changes"),

    # §5 Vague sources
    ("5", HIGH, r"\b(?:industry reports?|experts?|analysts?) (?:say|says|argue|believe|suggest|note)\b", "name the source or cut the claim"),
    ("5", HIGH, r"\b(?:observers|critics|analysts) have (?:cited|noted|argued)\b", "name them"),
    ("5", HIGH, r"\bsome (?:critics|experts|observers|would) (?:argue|say)\b", "name them or cut"),
    ("5", MED,  r"\bit is (?:widely )?believed that\b", "attribute it or cut it"),
    ("5", MED,  r"\bstudies (?:have )?(?:show|shown|suggest)\b", "cite the study"),

    # §6 Formulaic challenges and outlook sections
    ("6", HIGH, r"\bdespite (?:its|these|the) (?:challenges|success|setbacks)\b", "cut the framing"),
    ("6", HIGH, r"\bfaces (?:several|a number of|its share of) challenges\b", "name the problem"),
    ("6", MED,  r"\bcontinues to (?:thrive|grow|evolve|shape)\b", "give the number"),

    # §7 Overused AI words
    ("7", HIGH, r"\bdelv(?:e|es|ing)\b", "use look at"),
    ("7", HIGH, r"\btapestry\b", "cut"),
    ("7", HIGH, r"\btestament\b", "cut"),
    ("7", MED,  r"\bunderscor(?:e|es|ed)\b", "use shows"),
    ("7", MED,  r"\bshowcas(?:e|es|ing|ed)\b", "use show"),
    ("7", MED,  r"\bintricat(?:e|ely|ies|acy)\b", "use complicated, or be specific"),
    ("7", MED,  r"\binterplay\b", "say how they interact"),
    ("7", MED,  r"\bpivotal\b", "cut"),
    ("7", MED,  r"\bfoster(?:s|ing|ed)?\b", "use build or encourage"),
    ("7", MED,  r"\bgarner(?:s|ed|ing)?\b", "use get or win"),
    ("7", MED,  r"\bleverag(?:e|es|ing|ed)\b", "use use"),
    ("7", MED,  r"\bseamless(?:ly)?\b", "cut"),
    ("7", MED,  r"\brobust\b", "say what it withstands"),
    ("7", LOW,  r"\benhanc(?:e|es|ing|ed|ement)\b", "use improve"),
    ("7", LOW,  r"\bcrucial\b", "cut"),
    ("7", LOW,  r"\balign(?:s|ed|ing)? with\b", "use matches or fits"),
    ("7", LOW,  r"\b(?:Additionally|Moreover|Furthermore),", "cut the connector"),
    ("7", LOW,  r"\blandscape\b", "name the market or field"),
    ("7", LOW,  r"\bquietly\b", "cut"),
    ("7", LOW,  r"\bvibrant\b", "cut"),
    ("7", LOW,  r"\bunlock(?:s|ing)? (?:the |your )?(?:potential|value|growth)\b", "say what it does"),

    # §8 Avoiding is and are
    ("8", MED,  r"\b(?:features|offers) (?:a|an|over|more than)\b", "use has"),
    ("8", MED,  r"\brepresents? (?:a|an|the) (?:shift|opportunity|step)\b", "use is"),

    # §9 Not X but Y, and clipped negative endings
    ("9", HIGH, r"\bit'?s not (?:just|only|merely|about)\b", "state the point directly"),
    ("9", HIGH, r"\bnot (?:just|only|merely) .{2,60}?,\s*(?:but|it'?s|it is)\b", "state the point directly"),
    ("9", MED,  r",\s*no (?:guessing|hassle|fuss|surprises|exceptions|extra steps)\b", "write the clause out"),

    # §12 False from X to Y ranges
    ("12", HIGH, r"\bfrom .{3,40} to .{3,40},\s*from .{3,40} to\b", "list the items"),
    ("12", MED,  r"\beverything from .{3,40} to\b", "list the items"),

    # §13 Passive voice and missing subjects
    ("13", MED,  r"^\s*No .{2,40} (?:needed|required)\.\s*$", "name who does not need it"),

    # §21 Knowledge-limit disclaimers and guesses
    ("21", HARD, r"\bas of my (?:last )?(?:knowledge|training)\b", "cut — chatbot artifact"),
    ("21", HIGH, r"\bwhile (?:specific )?details .{0,50}?(?:limited|scarce|not (?:extensively )?documented)\b", "say the source does not show it, or cut"),
    ("21", HIGH, r"\bbased on (?:the )?available information\b", "cut"),
    ("21", HIGH, r"\bmaintains a low profile\b", "cut the guess"),
    ("21", MED,  r"\bit is believed that\b", "attribute it or cut it"),

    # §20/§22 Chatbot text and overly agreeable tone
    ("20", HARD, r"\b(?:I hope this helps|Let me know if|Would you like me to|Want me to|Should I continue|Certainly!|Of course!|Great question|You'?re absolutely right)\b",
                 "cut — chatbot artifact"),
    ("20", HARD, r"^\s*Here'?s (?:a |an |the )?(?:breakdown|overview|summary) (?:of|for)\b", "cut — chatbot artifact"),

    # §23 Filler phrases
    ("23", MED,  r"\bin order to\b", "use to"),
    ("23", MED,  r"\bdue to the fact that\b", "use because"),
    ("23", MED,  r"\bat this point in time\b", "use now"),
    ("23", MED,  r"\bin the event that\b", "use if"),
    ("23", MED,  r"\bhas the ability to\b", "use can"),
    ("23", MED,  r"\bit is important to note that\b", "cut"),
    ("23", MED,  r"\bit'?s worth noting\b", "cut"),
    ("23", MED,  r"\bneedless to say\b", "cut"),
    ("23", LOW,  r"\bwhen it comes to\b", "cut"),

    # §24 Too many qualifiers
    ("24", MED,  r"\bcould potentially\b", "use could"),
    ("24", MED,  r"\bmight arguably\b", "use may"),
    ("24", MED,  r"\bin some cases it may\b", "say when"),
    ("24", MED,  r"\bit'?s also possible\b", "cut or commit"),
    ("24", LOW,  r"^\s*To be fair,", "cut"),

    # §25 Generic positive endings
    ("25", HIGH, r"\bthe future looks bright\b", "end on the last real fact"),
    ("25", HIGH, r"\bexciting times (?:lie )?ahead\b", "end on the last real fact"),
    ("25", HIGH, r"\bstep in the right direction\b", "end on the last real fact"),
    ("25", HIGH, r"\b(?:journey|path) (?:toward|towards) (?:excellence|success|greatness)\b", "cut"),
    ("25", MED,  r"\bonly time will tell\b", "cut"),

    # §27 Pretending to reveal a deeper truth
    ("27", HIGH, r"\bthe real question is\b", "ask the question"),
    ("27", HIGH, r"^\s*At its core,", "make the claim"),
    ("27", HIGH, r"\bwhat really matters\b", "say what matters"),
    ("27", HIGH, r"\bthe (?:deeper issue|heart of the matter)\b", "state the issue"),
    ("27", MED,  r"^\s*In reality,", "cut"),

    # §28 Announcing the next point
    ("28", HIGH, r"\blet'?s (?:dive|explore|break this down|take a look|unpack|get into)\b", "make the point"),
    ("28", HIGH, r"\bhere'?s what you need to know\b", "tell them"),
    ("28", HIGH, r"\bwithout further ado\b", "cut"),
    ("28", MED,  r"\bnow let'?s look at\b", "cut"),
    ("28", MED,  r"^\s*(?:Quick note|Heads up)[:,]", "cut the announcement"),
    ("28", MED,  r"\bbefore I forget\b", "cut"),

    # §32 Formulaic sayings
    ("32", HIGH, r"\bis the (?:language|currency|architecture|backbone|new) of\b", "make the specific claim"),
    ("32", HIGH, r"\bbecomes? a trap\b", "say what goes wrong"),
    ("32", MED,  r"\bnot a .{2,25} but a (?:mirror|map|mindset)\b", "make the claim"),

    # §33 Fake-candid openings
    ("33", HIGH, r"(?:^|(?<=[.!?]\s))(?:Honestly\?|Look,|Here'?s the thing[.,:]|The thing is,|Let'?s be honest[.,:]|Real talk[.,:])",
                 "state the point"),

    # §34 Answering objections no one raised
    ("34", HIGH, r"\bthis isn'?t (?:mainly |really )?about\b", "say what it is about"),
    ("34", HIGH, r"\bI'?m not (?:saying|arguing|trying to)\b", "make the claim"),
    ("34", HIGH, r"\bdon'?t get me wrong\b", "cut"),
    ("34", HIGH, r"\bthis is not to say\b", "cut"),
    ("34", MED,  r"^\s*To be clear,", "cut"),
    ("34", MED,  r"\bsome might say\b", "name who, or cut"),

    # §35 Rejecting fake alternatives
    ("35", HIGH, r"\ba tempting (?:option|approach) would be\b", "state the real constraint"),
    ("35", HIGH, r"\bone might be tempted to\b", "state the real constraint"),
    ("35", HIGH, r"\ban obvious approach would be\b", "state the real constraint"),
    ("35", MED,  r"\byou might think .{0,40}?, but\b", "state the real constraint"),
    ("35", MED,  r"\bit would be easy to just\b", "state the real constraint"),

    # OUT — outreach openers. Generic B2B email cliches, not house style.
    # They were tagged GES until 2026-08-26 because they came from
    # marketing/styleguide/writing-style.md, which made them look like rules
    # about Jared's voice. They are not: anyone writing a partner email
    # anywhere should avoid all four, and mislabelling them meant they nearly
    # got left behind when the scanner was extracted for reuse.
    #
    # "just curious" is the hard one and the only manipulative one -- it
    # frames a real request as idle interest so the recipient does not brace.
    ("OUT", HARD, r"\bjust curious\b", "reads as lowering their guard"),
    ("OUT", MED,  r"\bI wanted to reach out\b", "open with the ask"),
    ("OUT", MED,  r"\bcircling back\b", "say what you need"),
    ("OUT", MED,  r"\bhope you'?re doing well\b", "open with the ask"),

    # GB — British spellings, for houses that write American throughout
    # (marketing/authors/jared-waxman.md §7). HARD because it is an objective
    # error rather than a judgment call: nobody picks "programme" on
    # purpose, and one of these alone needs to fire. "standardised" was the
    # only tell in a mail to 6,000 people and would never clear a threshold.
    #
    # Moved here 2026-08-26 from the ges-pulse skill, where it only ever ran
    # against the newsletter. Partner and student-facing copy never saw it,
    # and in two days that gap shipped "standardised" to the list plus
    # "programme" and "enrols" into a reusable sponsor template.
    #
    # Two entries were dropped in the move: the original list contained
    # "favorite" and "behavior", which are the AMERICAN spellings. As written
    # it flagged correct copy.
    # The verb ending is required. Bare stems over-match badly: "organis"
    # also hits organism, "optimis" hits optimism, "criticis" hits criticism,
    # "specialis" hits specialist and "analys" hits analysis -- all correct
    # American words. The first cut of this pattern flagged every one of them.
    ("GB", HARD, r"\b\w*(?:customis|organis|recognis|categoris|analys|optimis"
                 r"|personalis|specialis|prioritis|realis|summaris|utilis"
                 r"|minimis|maximis|apologis|standardis|normalis|monetis"
                 r"|digitis|characteris|criticis|modernis)"
                 r"(?:e|es|ed|ing|ation|ations)\b",
     "US spelling: -ize / -yze"),
    ("GB", HARD, r"\b(?:colour|labour|honour|favourite|behaviour|flavour)\w*\b",
     "US spelling: drop the u"),
    ("GB", HARD, r"\b(?:centre|theatre|litre|metre|fibre)\w*\b",
     "US spelling: -er"),
    ("GB", HARD, r"\b(?:licence|defence|offence|pretence|practis\w*)\b",
     "US spelling: -se / practice"),
    ("GB", HARD, r"\b(?:modelling|labelling|travelling|cancelled|counsellor|enrolment|fulfil|fulfilled|instalment)\b",
     "US spelling: single l, or -ment"),
    ("GB", HARD, r"\b(?:whilst|amongst|towards|learnt|spelt|grey|cheque|storey|sceptic\w*|judgement|programme|manoeuvre)\b",
     "US spelling"),

    # CL — reads as written with Claude. Not slop exactly: these are phrases a
    # model reaches for constantly, so anyone who works with one every day
    # clocks them instantly in published writing. `[Jared, 2026-08-26]`
    #
    # "nobody tells you" is HARD because it is a clickbait construction that
    # promises a secret and never has one. "failure mode" is weighted, not
    # hard, because it is real engineering vocabulary and people write about
    # systems -- it is the reach for it that is the tell, not the term.
    # The hidden-knowledge construction, in all its shapes: "the pattern
    # nobody names", "the part nobody talks about", "what they don't tell
    # you". It promises a secret and the secret is never a secret. Matched by
    # shape rather than by string, but narrowed to verbs of disclosure --
    # "the man nobody knew" is a sentence, not a tell.
    ("CL", HARD, r"\b(?:the|a|one) \w+ (?:that )?(?:nobody|no one|everyone|everybody) "
                 r"(?:ever )?(?:names?|mentions?|tells?|talks? about|says?|admits?"
                 r"|discusses|acknowledges?|asks?|notices?|misses|sees)\b",
     "say the thing instead of promising a secret"),
    ("CL", HARD, r"\b(?:what|the thing) (?:that )?(?:nobody|no one|they) "
                 r"(?:don'?t|doesn'?t|won'?t|never)? ?(?:tells?|tell|say|says|mention)s? you\b",
     "say the thing instead of promising a secret"),
    ("CL", HARD, r"\b(?:nobody|no one) (?:ever )?(?:tells|tell) you\b",
     "say the thing instead of promising a secret"),
    ("CL", HIGH, r"\bthe (?:uncomfortable|inconvenient|hard) truth\b",
     "just state it"),
    ("CL", HIGH, r"\bhiding in plain sight\b", "say where it is"),
    ("CL", HIGH, r"\bthe (?:dirty|open) (?:little )?secret\b", "say the thing"),

    # "Shape" as a substitute for a specific noun. `[Jared, 2026-08-26]`
    # Spotted in someone else's newsletter -- "Same shape all three times" --
    # and instantly recognisable to anyone who writes with Claude daily.
    # Not the bare word: "the shape of the curve" is fine and "AGI-shaped
    # hammer" is good writing. The tell is reaching for "shape" where
    # pattern, structure, argument or failure would be specific.
    ("CL", HARD, r"\bsame shape\b", "name the pattern the two things share"),
    ("CL", HIGH, r"\b(?:a|the) (?:similar|familiar|different|recognisable|recognizable) shape\b",
     "say what the thing actually is"),
    ("CL", MED,  r"\bthe shape of (?:the|this|that|it)\b", "name it"),

    # "X is doing real work" -- praising a sentence or a clause for pulling
    # its weight, instead of saying what it does. `[Jared, 2026-08-26]`
    ("CL", HARD, r"\b(?:is|are|was|were|isn'?t|aren'?t|wasn'?t|weren'?t)(?: not)? "
                 r"doing (?:real|genuine|actual|the real|heavy|serious) work\b",
     "say what it does"),
    ("CL", MED,  r"\b(?:earns?|pulls?) (?:its|their) (?:keep|weight)\b", "say what it does"),

    # The aphoristic restatement: "A gate that can't run in a bare python3 is
    # a gate that gets skipped." `[Jared, 2026-08-26]` The marker is the
    # repeated noun on both sides of "is", which is why this uses a
    # backreference rather than a word list -- the construction has no fixed
    # vocabulary, only a fixed skeleton.
    #
    # The noun must be followed by a clause, not a prepositional phrase, or
    # ordinary sentences get caught: "the date on the card is the date on the
    # page" is a statement of fact, not an epigram.
    ("CL", HARD, r"\b(?:a|an|the) (?:\w+ )?(\w{3,}) "
                 r"(?!(?:on|in|at|of|for|from|with|by|to|about|and|or) )"
                 r"(?:that |which |who )?[^.\n]{3,70}? is (?:a|an|the) (?:\w+ )?\1\b",
     "say the second half plainly; the restatement adds nothing"),
    ("CL", HIGH, r"\bfailure mode\b", "name the specific way it breaks"),
    ("CL", MED,  r"\bthe (?:real|actual) question is\b", "just ask it"),
    ("CL", MED,  r"\bhere'?s the thing\b", "cut and say it"),
]

COMPILED = [
    (sec, w, re.compile(p, re.IGNORECASE), fix)
    for sec, w, p, fix in LINE_PATTERNS
]

# §26 Too many hyphenated word pairs — density, not any single use.
HYPHEN_PAIRS = re.compile(
    r"\b(?:third-party|cross-functional|client-facing|data-driven|decision-making|"
    r"well-known|high-quality|real-time|long-term|end-to-end|best-in-class|"
    r"purpose-built|battle-tested|first-class)\b",
    re.IGNORECASE,
)
HYPHEN_PAIR_LIMIT = 4

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F900-\U0001F9FF☀-➿⬀-⯿]")
CURLY = re.compile("[“”‘’]")
DASHES = re.compile("—|–|(?<=\\s)--(?=\\s)")
# A bold label + colon opening a line, with or without a list marker or an
# emoji in front of it. The tell is the label, not the bullet.
BOLD_LEDE = re.compile(
    r"^\s*(?:[-*+]\s+|\d+\.\s+)?[^\w\s*]{0,3}\s*"
    r"(?:\*\*[^*]{1,45}:\*\*|\*\*[^*]{1,45}\*\*\s*:)"  # colon inside or outside the bold
)
BOLD_SPAN = re.compile(r"\*\*[^*\n]{1,80}\*\*")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
TRIPLE = re.compile(r"\b[\w'’]+(?:\s+[\w'’]+){0,3},\s+[^,.;:!?]{2,30},\s+and\s+[^,.;:!?]{2,30}[.;]")
TRIPLE_LIMIT = 3
MINOR_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into",
    "nor", "of", "on", "or", "the", "to", "with", "via", "over",
}
STOPWORDS = MINOR_WORDS | {"is", "are", "it", "its", "this", "that", "you", "we", "our", "your"}
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


# ─── Masking: never scan what isn't prose ──────────────────────────────────
def mask(text):
    """Blank out non-prose, preserving line and column positions.

    Dropped: YAML frontmatter, fenced code, inline code, link targets, bare
    URLs, HTML comments, and blockquotes. Blockquotes go because that is where
    this repo puts quoted counterparty text and the internal headers that
    `ges-partner-note` strips before sending. It matches the humanizer's
    "secondhand text" rule: do not rewrite a phrase that is being discussed
    rather than used.
    """
    lines = text.split("\n")
    out = []
    in_fence = False
    fence = ""
    in_front = bool(lines) and lines[0].strip() == "---"
    for i, line in enumerate(lines):
        stripped = line.strip()
        if in_front:
            out.append(" " * len(line))
            if i > 0 and stripped == "---":
                in_front = False
            continue
        m = re.match(r"^\s*(```+|~~~+)", line)
        if m:
            token = m.group(1)[:3]
            if not in_fence:
                in_fence, fence = True, token
            elif token == fence:
                in_fence = False
            out.append(" " * len(line))
            continue
        if in_fence or stripped.startswith(">"):
            out.append(" " * len(line))
            continue
        line = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), line)
        # Short quoted spans are a phrase being cited, not used — a DON'T list
        # naming "just curious" must not trip the "just curious" rule. Longer
        # quotes are passages of real copy and stay in scope.
        line = re.sub(r"[\"“][^\"”\n]{1,40}[\"”]", lambda m: " " * len(m.group(0)), line)
        line = re.sub(r"\]\([^)\n]*\)", lambda m: " " * len(m.group(0)), line)
        line = re.sub(r"https?://\S+", lambda m: " " * len(m.group(0)), line)
        line = re.sub(r"<!--.*?-->", lambda m: " " * len(m.group(0)), line)
        out.append(line)
    return out


def _paragraphs(masked):
    """Yield (start_line_no, [lines]) for each blank-line-delimited block."""
    buf, start = [], 0
    for i, line in enumerate(masked, 1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            yield start, buf
            buf = []
    if buf:
        yield start, buf


def _is_proper_noun(line, m):
    """True when a watched word is really part of a name.

    "Seamless moved into enrichment-by-prompt" is the vendor Seamless.AI, not
    §7's "seamless". A capital in mid-sentence, or a domain suffix, marks a
    name. Single-word matches only — a multi-word phrase that happens to start
    a clause is not a proper noun.
    """
    text = m.group(0)
    if " " in text or not text[:1].isupper():
        return False
    if re.match(r"\.[A-Za-z0-9]", line[m.end():]):  # Seamless.AI, Clay.com
        return True
    before = line[:m.start()].rstrip()
    # Start of a line or a sentence: ordinary capitalization, not a name.
    return bool(before) and not before.endswith(tuple(".!?:;-*#>|(\"'"))


def _add(hits, line_no, section, weight, snippet, fix):
    hits.append({
        "line": line_no,
        "section": section,
        "weight": weight,
        "text": " ".join(snippet.split())[:90],
        "fix": fix,
    })


# ─── Structural checks ─────────────────────────────────────────────────────
def _where(line_nos, limit=4):
    shown = ", ".join(f"L{n}" for n in line_nos[:limit])
    return shown + (f", +{len(line_nos) - limit} more" if len(line_nos) > limit else "")


def structural(masked, hits):
    body = "\n".join(masked)
    dash_lines, curly_lines, emoji_lines = [], [], []

    for i, line in enumerate(masked, 1):
        if DASHES.search(line):
            dash_lines.append(i)
        if CURLY.search(line):
            curly_lines.append(i)
        h = HEADING.match(line)
        # Decoration = an emoji opening a line, a heading, or a list item.
        # An emoji mid-sentence is ordinary writing and is left alone.
        if EMOJI.search(line) and (
            h or re.match(r"^\s*(?:[-*+]\s|\d+\.\s)", line) or EMOJI.match(line.lstrip())
        ):
            emoji_lines.append(i)
        # §17 title case. The unambiguous tell is a capitalized minor word
        # ("And", "Of", "The"). Counting capitals instead just flags headings
        # full of proper nouns, which many headings are. H1 is exempt:
        # a document title is allowed to look like a title.
        if h and len(h.group(1)) > 1:
            words = re.findall(r"[A-Za-z][\w'’-]*", h.group(2))
            rest = words[1:]
            if len(words) >= 4:
                minor_capped = any(w.lower() in MINOR_WORDS and w[0].isupper() for w in rest)
                capped_ratio = sum(1 for w in rest if w[0].isupper()) / len(rest)
                # Both conditions, not either: "Tier A and B" capitalizes a
                # minor word without being title case, and a heading full of
                # proper nouns capitalizes a lot without being title case.
                if minor_capped and capped_ratio >= 0.7:
                    _add(hits, i, "17", MED, line, "sentence case the heading")

    # §14/§19/§18 — density, not any single use. The humanizer's false-positive
    # rules are explicit that one em dash, a curly quote, or an emoji proves
    # nothing; a rate does. The styleguide's line is "avoid in most
    # circumstances", not a ban.
    if len(dash_lines) >= 3:
        _add(hits, dash_lines[0], "14", HIGH if len(dash_lines) >= 8 else MED,
             f"{len(dash_lines)} lines with em/en dashes ({_where(dash_lines)})",
             "styleguide: avoid outward. Comma, period, colon, or parentheses")
    if curly_lines:
        _add(hits, curly_lines[0], "19", LOW,
             f"{len(curly_lines)} lines with curly quotes ({_where(curly_lines)})",
             "straight quotes, unless the destination curls them itself")
    if emoji_lines:
        _add(hits, emoji_lines[0], "18", MED if len(emoji_lines) >= 3 else LOW,
             f"{len(emoji_lines)} headings or list items led by an emoji ({_where(emoji_lines)})",
             "cut the decoration; keep an emoji only where it carries meaning")

    # §16 lists where every item is a bold label followed by a sentence that
    # restates it. A spec's field list ("**Deadline:** T-14") is legitimate
    # structure, so the item has to carry a full clause after the colon to count.
    lede = []
    for i, line in enumerate(masked, 1):
        m = BOLD_LEDE.match(line)
        if m and len(line[m.end():].split()) >= 6:
            lede.append(i)
    if len(lede) >= 3:
        _add(hits, lede[0], "16", MED,
             f"{len(lede)} list items are a bold label plus a sentence ({_where(lede)})",
             "write it as prose, or drop the labels")

    # §15 bold used as decoration. Reference docs in this repo bold their field
    # names on purpose, so this only fires on real saturation and stays LOW.
    bold = BOLD_SPAN.findall(body)
    prose_lines = max(1, sum(1 for line in masked if line.strip()))
    if len(bold) >= 15 and len(bold) / prose_lines > 0.45:
        _add(hits, 1, "15", LOW, f"{len(bold)} bold spans across {prose_lines} lines",
             "bold the one thing that matters, not every term")

    # §26 hyphenated-pair density
    pairs = HYPHEN_PAIRS.findall(body)
    if len(pairs) >= HYPHEN_PAIR_LIMIT:
        sample = ", ".join(sorted({p.lower() for p in pairs})[:5])
        _add(hits, 1, "26", LOW, f"{len(pairs)} stock hyphenated pairs ({sample})",
             "vary them, and drop the hyphen after the noun")

    # §10 forced groups of three. Density, not a raw count: three triples in a
    # 250-line playbook is ordinary writing, three in a 20-line email is a habit.
    triples = TRIPLE.findall(body)
    if len(triples) >= TRIPLE_LIMIT and len(triples) / prose_lines > 0.03:
        _add(hits, 1, "10", MED, f"{len(triples)} three-item lists in {prose_lines} lines",
             "some ideas come in twos and fours")

    for start, para in _paragraphs(masked):
        if any(re.match(r"^\s*(?:[-*+]|\d+\.|\||#)", line) for line in para):
            continue
        text = " ".join(line.strip() for line in para)
        sentences = [s for s in SENTENCE_SPLIT.split(text) if s.strip()]
        if len(sentences) < 3:
            continue

        # §11 repeated sentence openings
        openers = {}
        for s in sentences:
            w = re.match(r"[A-Za-z][\w'’]*", s.strip())
            if w:
                openers.setdefault(w.group(0).lower(), []).append(s)
        for word, group in openers.items():
            if len(group) >= 3:
                _add(hits, start, "11", MED,
                     f'{len(group)} sentences in one paragraph open with "{word}"',
                     "merge them, or start with the action")

        # §31 runs of dramatic fragments
        run = 0
        for s in sentences:
            if len(s.split()) <= 4:
                run += 1
                if run >= 3:
                    _add(hits, start, "31", MED, text,
                         "one short sentence lands; a row of them reads as staging")
                    break
            else:
                run = 0

    # §29 a heading repeated in the first sentence beneath it
    for i, line in enumerate(masked):
        h = HEADING.match(line)
        if not h:
            continue
        head = {w.lower() for w in re.findall(r"[A-Za-z][\w'’-]*", h.group(2))} - STOPWORDS
        if not head:
            continue
        for offset, nxt in enumerate(masked[i + 1:i + 4], start=2):
            if not nxt.strip():
                continue
            if HEADING.match(nxt) or re.match(r"^\s*(?:[-*+]|\d+\.|\|)", nxt):
                break
            words = {w.lower() for w in re.findall(r"[A-Za-z][\w'’-]*", nxt)} - STOPWORDS
            if len(nxt.split()) <= 10 and words and len(head & words) / len(head) >= 0.5:
                # LOW: a short line under a heading is often a cross-reference
                # ("Same as Track A Touch 3."), not an echo.
                _add(hits, i + offset - 1, "29", LOW, nxt,
                     "cut the sentence if it only repeats the heading")
            break


def scan_text(text):
    masked = mask(text)
    hits = []
    for i, line in enumerate(masked, 1):
        for section, weight, rx, fix in COMPILED:
            for m in rx.finditer(line):
                if _is_proper_noun(line, m):
                    continue
                _add(hits, i, section, weight, m.group(0), fix)
    structural(masked, hits)

    seen = set()
    unique = []
    for h in hits:
        key = (h["line"], h["section"], h["text"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(h)
    unique.sort(key=lambda h: (h["line"], h["section"]))

    hard = [h for h in unique if h["weight"] == HARD]
    signals = [h for h in unique if h["weight"] != HARD]

    # Cap each section's contribution so one repeated word can't carry a file
    # over the threshold on its own. Several *different* tells are the evidence.
    per_section = {}
    for h in signals:
        per_section[h["section"]] = per_section.get(h["section"], 0) + h["weight"]
    score = sum(min(v, SECTION_SCORE_CAP) for v in per_section.values())

    return {
        "hard": hard,
        "signals": signals,
        "sections": len(per_section),
        "score": score,
        "threshold": THRESHOLD,
        "flagged": bool(hard) or score >= THRESHOLD,
    }


# ─── Paths ─────────────────────────────────────────────────────────────────
def repo_relative(path, root=None):
    root = root or os.environ.get("CLAUDE_PROJECT_DIR") or ""
    ap = os.path.abspath(path)
    if root:
        rel = os.path.relpath(ap, os.path.abspath(root))
        if not rel.startswith(".."):
            return rel.replace(os.sep, "/")
    parts = ap.replace(os.sep, "/").split("/")
    for i in range(len(parts) - 1, -1, -1):
        if parts[i] in TOP_LEVEL_DIRS:
            return "/".join(parts[i:])
    return os.path.basename(ap)


def is_outward_path(path, root=None):
    """True when the file is something a counterparty reads.

    Internal docs are excluded on purpose. The styleguide keeps them punchy;
    running a slop check over them would sand them down.
    """
    rel = repo_relative(path, root)
    if os.path.basename(rel) in NEVER_BASENAMES:
        return False
    if not rel.endswith(SCANNED_SUFFIXES):
        return False
    if any(rel.startswith(p) for p in NEVER_PREFIXES):
        return False
    return any(rel.startswith(p) for p in OUTWARD_PREFIXES)


def scan_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return scan_text(fh.read())


# ─── Reporting ─────────────────────────────────────────────────────────────
def _render(findings, marker):
    """One line per finding, collapsed to SECTION_REPORT_CAP per section."""
    shown, counts = [], {}
    for h in findings:
        counts[h["section"]] = counts.get(h["section"], 0) + 1
        if counts[h["section"]] <= SECTION_REPORT_CAP:
            shown.append(f"    {marker} L{h['line']} §{h['section']}  {h['text']}  -> {h['fix']}")
    hidden = {s: n - SECTION_REPORT_CAP for s, n in counts.items() if n > SECTION_REPORT_CAP}
    if hidden:
        tail = ", ".join(f"§{s} +{n}" for s, n in sorted(hidden.items()))
        shown.append(f"    {marker} ... also {tail}")
    return shown


def format_report(rel, result):
    lines = [
        f"  {rel}  (score {result['score']}/{result['threshold']}"
        f" across {result['sections']} pattern{'s' if result['sections'] != 1 else ''})"
    ]
    lines += _render(result["hard"], "x")
    if result["score"] >= result["threshold"]:
        lines += _render(result["signals"], ".")
    elif result["hard"]:
        lines.append(f"    . ({len(result['signals'])} weighted signals, under threshold)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Scan outward-facing files for AI writing tells.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--all", action="store_true", help="recurse into directories")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--any-path", action="store_true",
                    help="scan even files outside the outward-facing set")
    args = ap.parse_args()

    targets = []
    for p in args.paths:
        if os.path.isdir(p):
            if not args.all:
                print(f"skipping directory {p} (pass --all to recurse)", file=sys.stderr)
                continue
            targets.extend(sorted(glob.glob(os.path.join(p, "**", "*.md"), recursive=True)))
        else:
            targets.append(p)

    results = {}
    for path in targets:
        if not os.path.exists(path):
            continue
        if not args.any_path and not is_outward_path(path):
            continue
        results[repo_relative(path)] = scan_file(path)

    if args.json:
        print(json.dumps(results, indent=2))
        return 1 if any(r["flagged"] for r in results.values()) else 0

    flagged = {rel: r for rel, r in results.items() if r["flagged"]}
    if not flagged:
        n = len(results)
        print(f"OK - no AI tells over threshold in {n} file{'s' if n != 1 else ''}.")
        return 0

    print("Reads as AI-written. Check these before it goes out:\n", file=sys.stderr)
    for rel, r in flagged.items():
        print(format_report(rel, r), file=sys.stderr)
    print(
        "\nx = an objective error or a chatbot artifact.  . = a signal; several together are"
        "\nevidence, one is not. False-positive rules: " + RULES_DOC + "."
        "\nTo judge and rewrite: " + FIX_COMMAND + ".",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
