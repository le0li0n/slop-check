#!/usr/bin/env python3
"""Score the scanner on both corpora at once.

A false-positive rate on its own is a misleading number: deleting every pattern
drives it to zero. This reports the two together — how much human writing gets
flagged, and how much machine writing gets caught — so a change has to justify
itself on both.

  python3 tools/evaluate.py                 # summary
  python3 tools/evaluate.py --sections      # per-section damage on human prose
  python3 tools/evaluate.py --save before   # keep a snapshot to diff against
"""

import argparse
import importlib.util
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
from mine import strip_front_matter

REPO = os.path.dirname(C.ROOT)
AI = os.path.join(C.ROOT, "ai_texts")


def load_scanner():
    path = os.path.join(REPO, "slop-check", "hooks", "ai_slop.py")
    spec = importlib.util.spec_from_file_location("ai_slop", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def human_docs():
    with open(os.path.join(C.ROOT, "manifest.json"), encoding="utf-8") as fh:
        for d in json.load(fh)["documents"]:
            p = os.path.join(C.ROOT, d["path"])
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f2:
                    yield d["path"], strip_front_matter(f2.read())


def ai_docs():
    for dirpath, _dirs, files in os.walk(AI):
        for fn in sorted(files):
            if fn.endswith(".txt"):
                p = os.path.join(dirpath, fn)
                with open(p, encoding="utf-8") as fh:
                    yield os.path.relpath(p, C.ROOT), strip_front_matter(fh.read())


def run(mod, docs):
    flagged, scores, sections, hard = 0, [], Counter(), Counter()
    names = []
    n = 0
    for path, text in docs:
        n += 1
        r = mod.scan_text(text)
        scores.append(r["score"])
        if r["flagged"]:
            flagged += 1
            names.append(path)
        for h in r["hard"]:
            hard[h["section"]] += 1
        for h in r["hard"] + r["signals"]:
            sections[h["section"]] += 1
    scores.sort()
    return {"n": n, "flagged": flagged, "rate": 100.0 * flagged / max(n, 1),
            "median": scores[len(scores) // 2] if scores else 0,
            "p90": scores[int(len(scores) * 0.9)] if scores else 0,
            "sections": sections, "hard": hard, "names": names}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sections", action="store_true")
    ap.add_argument("--save")
    ap.add_argument("--against")
    args = ap.parse_args()

    mod = load_scanner()
    hu = run(mod, human_docs())
    ai = run(mod, ai_docs())

    print("                     human (should be low)   AI (should be high)")
    print("flagged              %5.1f%%  (%3d/%3d)        %5.1f%%  (%3d/%3d)"
          % (hu["rate"], hu["flagged"], hu["n"], ai["rate"], ai["flagged"], ai["n"]))
    print("median score         %5d                   %5d" % (hu["median"], ai["median"]))
    print("90th pct score       %5d                   %5d" % (hu["p90"], ai["p90"]))
    sep = ai["rate"] - hu["rate"]
    print("separation           %5.1f points" % sep)

    if args.sections:
        print("\nper-section hits (human corpus is the false-positive bill):")
        print("  %-6s %8s %8s %8s" % ("§", "human", "AI", "ratio"))
        for sec, n in hu["sections"].most_common(18):
            a = ai["sections"].get(sec, 0)
            # rates per document, so the two corpora compare despite size
            hr, ar = n / hu["n"], a / ai["n"]
            print("  %-6s %8.2f %8.2f %8s"
                  % (sec, hr, ar, ("%.1fx" % (ar / hr)) if hr else "-"))
        if hu["hard"]:
            print("\n  HARD hits on human prose (each one flags a file outright):")
            for sec, n in hu["hard"].most_common(10):
                print("    §%-4s %d" % (sec, n))

    snap = {"human_rate": hu["rate"], "ai_rate": ai["rate"],
            "human_flagged": hu["flagged"], "ai_flagged": ai["flagged"],
            "human_n": hu["n"], "ai_n": ai["n"],
            "human_median": hu["median"], "ai_median": ai["median"]}
    if args.save:
        p = os.path.join(C.ROOT, "eval-%s.json" % args.save)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(snap, fh, indent=1)
        print("\nsaved %s" % p)
    if args.against:
        p = os.path.join(C.ROOT, "eval-%s.json" % args.against)
        with open(p, encoding="utf-8") as fh:
            old = json.load(fh)
        print("\nversus %s:" % args.against)
        print("  human flagged  %5.1f%% -> %5.1f%%  (%+.1f)"
              % (old["human_rate"], snap["human_rate"],
                 snap["human_rate"] - old["human_rate"]))
        print("  AI flagged     %5.1f%% -> %5.1f%%  (%+.1f)"
              % (old["ai_rate"], snap["ai_rate"], snap["ai_rate"] - old["ai_rate"]))
        print("  separation     %5.1f  -> %5.1f  (%+.1f)"
              % (old["ai_rate"] - old["human_rate"], sep,
                 sep - (old["ai_rate"] - old["human_rate"])))


if __name__ == "__main__":
    main()
