#!/usr/bin/env python3
"""Measure how slop-check behaves on genuine pre-2012 human prose.

A pattern that fires constantly in this corpus is not an AI tell — it is
English, and flagging it costs you a good sentence. A pattern that never fires
across a few hundred thousand words of human B2B writing is a real signal.

This drives the scanner through its own scan_text(), so masking and
proper-noun suppression apply exactly as they do in normal use.

  python3 tools/baseline.py                 # write BASELINE.md
  python3 tools/baseline.py --compare FILE  # score a draft against the corpus
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)


def load_scanner():
    for cand in (os.path.join(REPO, "slop-check", "hooks", "ai_slop.py"),
                 os.path.join(REPO, "hooks", "ai_slop.py")):
        if os.path.exists(cand):
            spec = importlib.util.spec_from_file_location("ai_slop", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, cand
    sys.exit("could not find ai_slop.py next to this corpus")


def strip_front_matter(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip()
    return text


def corpus_docs():
    with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as fh:
        docs = json.load(fh)["documents"]
    for d in docs:
        p = os.path.join(ROOT, d["path"])
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                yield d, strip_front_matter(fh.read())


def normalise(snippet):
    """Collapse structural findings that differ only by line numbers or counts.

    "9 lines with curly quotes (l1, l3, +5 more)" and "1 lines with curly
    quotes (l15)" are one tell, not two, and splitting them buries the rate.
    """
    s = snippet.strip().lower()
    s = re.sub(r"\s*\((?:l\d+[^)]*)\)", "", s)
    s = re.sub(r"^\d+\s+", "", s)
    s = re.sub(r"^(lines?|sentences?|paragraphs?)\b", r"\1", s)
    return s.strip()


def tally(mod, text):
    """Per-tell counts for one document, keyed by the snippet the scanner matched."""
    res = mod.scan_text(text)
    c = Counter()
    for h in res["hard"] + res["signals"]:
        c[(h["section"], normalise(h["text"]), h.get("fix", ""))] += 1
    return res, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compare", help="a draft to score against the corpus baseline")
    ap.add_argument("--top", type=int, default=60)
    args = ap.parse_args()

    mod, path = load_scanner()

    words = 0
    docs = 0
    hits = Counter()
    docs_with = Counter()
    flagged = 0
    scores = []
    by_area = {}

    for meta, text in corpus_docs():
        docs += 1
        w = len(text.split())
        words += w
        res, c = tally(mod, text)
        scores.append(res["score"])
        if res["flagged"]:
            flagged += 1
            by_area.setdefault(meta["area"], []).append(meta["path"])
        hits.update(c)
        for k in c:
            docs_with[k] += 1

    if not docs:
        sys.exit("no documents in the corpus yet — run tools/build.py first")

    if args.compare:
        with open(args.compare, encoding="utf-8") as fh:
            draft = strip_front_matter(fh.read())
        dw = max(1, len(draft.split()))
        res, dc = tally(mod, draft)
        print("draft: %d words, score %d, threshold %d, flagged=%s\n"
              % (dw, res["score"], res["threshold"], res["flagged"]))
        print("%-44s %9s %9s" % ("tell", "draft/10k", "human/10k"))
        print("-" * 66)
        rows = []
        for key, n in dc.items():
            d_rate = n * 10000.0 / dw
            h_rate = hits.get(key, 0) * 10000.0 / words
            rows.append((d_rate - h_rate, key, d_rate, h_rate))
        for _, key, d_rate, h_rate in sorted(rows, reverse=True):
            note = "  <-- unseen in the human corpus" if h_rate == 0 else ""
            print("%-44s %9.1f %9.1f%s" % (("§%s %s" % (key[0], key[1]))[:44],
                                           d_rate, h_rate, note))
        return

    scores.sort()
    median = scores[len(scores) // 2]
    p90 = scores[int(len(scores) * 0.9)]

    L = [
        "# What these patterns do to human writing",
        "",
        "`ai_slop.py` run over the whole corpus: **%d documents, %s words**, all "
        "published before 2012 and all written by people." % (docs, f"{words:,}"),
        "",
        "| | |",
        "| --- | --- |",
        "| Documents flagged | %d of %d (%.0f%%) |" % (flagged, docs, 100.0 * flagged / docs),
        "| Median score | %d (threshold %d) |" % (median, mod.THRESHOLD),
        "| 90th percentile score | %d |" % p90,
        "",
        "The flagged share is the false-positive rate on human prose. Every one "
        "of these documents predates the models, so each flag is the scanner "
        "objecting to writing that a person actually published.",
        "",
        "## Tells ranked by how ordinary they are",
        "",
        "Rates are per 10,000 words. High in this table means the phrase is "
        "normal English and a hit proves nothing on its own; near-zero means a "
        "hit is worth acting on.",
        "",
        "| § | Match | Hits | Per 10k | Docs |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for (sec, txt, _fix), n in hits.most_common(args.top):
        L.append("| %s | `%s` | %d | %.2f | %d/%d |"
                 % (sec, txt.replace("|", "\\|")[:60], n, n * 10000.0 / words,
                    docs_with[(sec, txt, _fix)], docs))

    sec_hits = Counter()
    for (sec, _t, _f), n in hits.items():
        sec_hits[sec] += n
    L += ["", "## By section", "",
          "Which parts of the pattern list generate the most noise on human prose.",
          "", "| § | Hits | Per 10k |", "| --- | ---: | ---: |"]
    for sec, n in sec_hits.most_common():
        L.append("| %s | %d | %.2f |" % (sec, n, n * 10000.0 / words))

    if flagged:
        L += ["", "## Where the scanner objects most", ""]
        for area, paths in sorted(by_area.items(), key=lambda kv: -len(kv[1])):
            L.append("- **%s** — %d flagged" % (area, len(paths)))

    L += ["", "---", "",
          "Regenerate with `python3 tools/baseline.py`. Score a draft against it "
          "with `python3 tools/baseline.py --compare path/to/draft.md`.", ""]

    out = os.path.join(ROOT, "BASELINE.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("wrote %s (%d docs, %s words, %d flagged)" % (out, docs, f"{words:,}", flagged))


if __name__ == "__main__":
    main()
