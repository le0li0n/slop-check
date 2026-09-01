#!/usr/bin/env python3
"""Measure the shape of prose, not its vocabulary.

Phrase lists only catch tells someone already thought of. These features
describe how a piece of writing is *built* — how much its sentence lengths
vary, how often it starts a sentence the same way, whether it uses
contractions — and machine prose tends to sit in a narrower band than human
prose on nearly all of them.

Run it on the corpus to get the human envelope, then on a draft to see which
axes fall outside it.

  python3 tools/profile.py                  # the human envelope, per feature
  python3 tools/profile.py --compare FILE   # where a draft sits in it
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SENT = re.compile(r"(?<=[.!?])[\"'”’)]?\s+")
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
CONTRACTION = re.compile(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b", re.I)
TRICOLON = re.compile(r"\b[\w'’]+(?:\s+[\w'’]+){0,3},\s+[^,.;:!?]{2,30},\s+and\s+[^,.;:!?]{2,30}[.;]")
NOT_JUST = re.compile(r"\bnot (?:just|only|merely|simply)\b[^.!?]{0,60}\bbut\b", re.I)
PARTICIPIAL = re.compile(r",\s+(?:ensuring|highlighting|underscoring|emphasizing|reflecting|"
                         r"allowing|enabling|making it|creating|driving|helping|providing|"
                         r"offering|showcasing|demonstrating)\b", re.I)
LATINATE = re.compile(r"\b(?:moreover|furthermore|additionally|consequently|thus|hence|"
                      r"nevertheless|nonetheless|therefore|in conclusion|overall)\b", re.I)
HEDGE = re.compile(r"\b(?:arguably|notably|importantly|significantly|crucially|essentially|"
                   r"fundamentally|ultimately|indeed|particularly)\b", re.I)
FIRST = re.compile(r"\b(?:i|i'm|i've|i'd|i'll|me|my|mine)\b", re.I)
SECOND = re.compile(r"\b(?:you|your|you're|you've|yours)\b", re.I)
OPENER_CONJ = re.compile(r"^(?:but|and|so|yet|or|because)\b", re.I)


def features(text):
    text = text.strip()
    words = WORD.findall(text)
    n = len(words)
    if n < 60:
        return None
    per1k = lambda c: 1000.0 * c / n

    paras = [p for p in text.split("\n\n") if p.strip()]
    sents = [s.strip() for s in SENT.split(text) if len(s.strip()) > 1]
    slens = [len(WORD.findall(s)) for s in sents]
    slens = [x for x in slens if x]
    if len(slens) < 5:
        return None
    mean = sum(slens) / float(len(slens))
    sd = (sum((x - mean) ** 2 for x in slens) / len(slens)) ** 0.5

    openers = [WORD.findall(s)[0].lower() for s in sents if WORD.findall(s)]
    ocount = Counter(openers)

    f = {}
    f["sentence length (mean)"] = mean
    # the single most reported difference: humans vary sentence length a lot
    f["sentence length variation"] = sd / mean if mean else 0
    f["short sentences <9w %"] = 100.0 * sum(1 for x in slens if x < 9) / len(slens)
    f["long sentences >34w %"] = 100.0 * sum(1 for x in slens if x > 34) / len(slens)
    f["sentences per paragraph"] = len(sents) / float(len(paras))
    f["distinct openers %"] = 100.0 * len(ocount) / len(openers)
    f["commonest opener %"] = 100.0 * ocount.most_common(1)[0][1] / len(openers)
    f["opens with 'the' %"] = 100.0 * ocount.get("the", 0) / len(openers)
    f["opens with conjunction %"] = 100.0 * sum(1 for s in sents if OPENER_CONJ.match(s.strip())) / len(sents)
    f["contractions /1k"] = per1k(len(CONTRACTION.findall(text)))
    f["first person /1k"] = per1k(len(FIRST.findall(text)))
    f["second person /1k"] = per1k(len(SECOND.findall(text)))
    f["em/en dash /1k"] = per1k(len(re.findall(r"[—–]|(?<=\s)--(?=\s)", text)))
    f["semicolon /1k"] = per1k(text.count(";"))
    f["question mark /1k"] = per1k(text.count("?"))
    f["exclamation /1k"] = per1k(text.count("!"))
    f["tricolon /1k"] = per1k(len(TRICOLON.findall(text)))
    f["'not just X but Y' /1k"] = per1k(len(NOT_JUST.findall(text)))
    f["participial closer /1k"] = per1k(len(PARTICIPIAL.findall(text)))
    f["latinate connective /1k"] = per1k(len(LATINATE.findall(text)))
    f["hedge adverb /1k"] = per1k(len(HEDGE.findall(text)))
    f["-ly adverbs /1k"] = per1k(sum(1 for w in words if w.lower().endswith("ly") and len(w) > 5))
    f["long words 12+ /1k"] = per1k(sum(1 for w in words if len(w) >= 12))
    f["mean word length"] = sum(len(w) for w in words) / float(n)
    f["vocabulary variety"] = len({w.lower() for w in words[:600]}) / float(min(n, 600))
    return f


def strip_front_matter(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            return t[e + 4:].lstrip()
    return t


def corpus_features():
    with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as fh:
        docs = json.load(fh)["documents"]
    rows = []
    for d in docs:
        p = os.path.join(ROOT, d["path"])
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            f = features(strip_front_matter(fh.read()))
        if f:
            rows.append(f)
    return rows


def pct(vals, q):
    vals = sorted(vals)
    return vals[min(len(vals) - 1, int(q * len(vals)))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare")
    args = ap.parse_args()

    rows = corpus_features()
    keys = list(rows[0].keys())
    env = {k: [r[k] for r in rows] for k in keys}

    if not args.compare:
        print("Human B2B prose, %d documents. The middle 90%% of each feature —\n"
              "a draft outside p5..p95 is shaped unlike anything here.\n" % len(rows))
        print("%-28s %8s %8s %8s" % ("feature", "p5", "median", "p95"))
        print("-" * 56)
        for k in keys:
            print("%-28s %8.2f %8.2f %8.2f"
                  % (k, pct(env[k], .05), pct(env[k], .50), pct(env[k], .95)))
        return

    with open(args.compare, encoding="utf-8") as fh:
        f = features(strip_front_matter(fh.read()))
    if not f:
        sys.exit("draft too short to profile")

    print("%-28s %8s %8s %8s %8s  %s"
          % ("feature", "draft", "p5", "median", "p95", ""))
    print("-" * 78)
    out = []
    for k in keys:
        lo, mid, hi = pct(env[k], .05), pct(env[k], .50), pct(env[k], .95)
        v = f[k]
        if v < lo:
            flag, dist = "LOW", (lo - v) / (abs(lo) + 1e-9)
        elif v > hi:
            flag, dist = "HIGH", (v - hi) / (abs(hi) + 1e-9)
        else:
            flag, dist = "", 0.0
        out.append((dist, k, v, lo, mid, hi, flag))
    for dist, k, v, lo, mid, hi, flag in sorted(out, reverse=True):
        print("%-28s %8.2f %8.2f %8.2f %8.2f  %s" % (k, v, lo, mid, hi, flag))
    outliers = [o for o in out if o[6]]
    print("\n%d of %d features outside the human range." % (len(outliers), len(keys)))


if __name__ == "__main__":
    main()
