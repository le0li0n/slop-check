#!/usr/bin/env python3
"""What an edit lost, and where it says more than the original did.

The scanner asks whether prose reads as machine-written. This asks a
different question about the same file: after an edit — yours, an editor's,
or a model's — does it still say what it said?

Two failures, both quiet. The first is dropping something: a figure, a
source, a link, a claim that resisted the rewrite. The second is subtler and
is the reason this exists. A draft's "can spike" comes back as "churns
customers significantly faster", and the piece now asserts more than its
author was willing to. An adverb habit borrowed from a confident writer does
that on its own, and neither a tell scanner nor a prose-shape measurement
notices: both files pass, and the claim has still changed.

Neither check understands the text. They are string comparisons, so they
report candidates for a reading, not verdicts. Read the passage before
accepting any line of the output.

  python3 hooks/edit_check.py original.md edited.md
"""

import argparse
import re
import sys

# words that raise a claim, and words that keep it hedged
STRONGER = ["always", "never", "every", "all", "must", "will", "cannot", "inherently",
            "systematically", "significantly", "dramatically", "obviously", "clearly",
            "certainly", "undoubtedly", "guaranteed", "proves", "eliminates", "ensures"]
HEDGES = ["can", "could", "may", "might", "often", "usually", "sometimes", "tends",
          "likely", "generally", "typically", "some", "most", "perhaps", "seems"]

STOP = {"the", "this", "that", "your", "if", "a", "it", "what", "here", "then", "and", "for",
        "add", "write", "know", "design", "moving", "even", "get", "whatever", "does", "still",
        "pure", "one", "net", "three", "choose", "charge", "when", "where", "why", "how", "but",
        "or", "so", "you", "we", "they", "there", "their", "its", "not", "no", "yes", "do", "don"}


def norm(t):
    t = t.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(t.lower().split())


def count(word, text):
    return len(re.findall(r"\b%s\b" % re.escape(word), text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("original")
    ap.add_argument("edited")
    args = ap.parse_args()

    before = open(args.original, encoding="utf-8").read()
    after = open(args.edited, encoding="utf-8").read()
    nb, na = norm(before), norm(after)
    problems = 0

    checks = {
        "links": re.findall(r"https?://[^\s)]+", before),
        "numbers": re.findall(r"\\?\$[\d,]+|\b\d+(?:[.,]\d+)?%?\b", before),
        "names": sorted({m for m in re.findall(r"\b[A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)?\b", before)
                         if m.lower() not in STOP and len(m) > 2}),
        "quotations": re.findall(r'"([^"]{15,140})"', before),
    }
    print("== in the original, missing from the edit ==")
    for label, items in checks.items():
        missing = [i for i in items if norm(i.strip("*_")) not in na]
        problems += len(missing)
        print("%-12s %d of %d missing" % (label, len(missing), len(items)))
        for m in sorted(set(missing)):
            print("     %s" % m[:100])

    heads = re.findall(r"^#{1,6}\s+(.*)$", before, re.M)
    gone = [h for h in heads if norm(h) not in na]
    print("%-12s %d of %d changed or gone" % ("headings", len(gone), len(heads)))
    for h in gone:
        print("     %s" % h)

    print("\n== where the edit claims more than the original ==")
    rows = []
    for w in STRONGER:
        a, b = count(w, nb), count(w, na)
        if b > a:
            rows.append((b - a, w, a, b))
    for w in HEDGES:
        a, b = count(w, nb), count(w, na)
        if b < a:
            rows.append((a - b, w + " (hedge lost)", a, b))
    for delta, w, a, b in sorted(rows, reverse=True):
        problems += delta
        print("  %-28s original %2d  edit %2d" % (w, a, b))
    if not rows:
        print("  nothing: no strengthening word gained ground and no hedge lost any")

    bw, aw = len(re.findall(r"[A-Za-z']+", before)), len(re.findall(r"[A-Za-z']+", after))
    print("\nwords: original %d, edit %d (%+.0f%%)" % (bw, aw, 100.0 * (aw - bw) / bw))
    print("\nEvery line above is a candidate, not a verdict: read the passage before accepting it.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
