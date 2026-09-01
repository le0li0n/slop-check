#!/usr/bin/env python3
"""Generate the AI half of the contrast pair.

The human corpus tells you what is normal. It cannot tell you what a model
overuses — absence from human writing is not the same as presence in machine
writing. For that you need a matched set: same titles, same topics, same
lengths, written by a model instead of a person. Then the difference between
the two is the signal, and everything they share is genre rather than tell.

Prompts are deliberately naive — a title, an audience, a length. Asking for
"human-sounding" prose would hide the very thing we are trying to measure.

  python3 tools/generate_ai.py --n 200
  python3 tools/generate_ai.py --n 20 --model claude-sonnet-5
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C

AI = os.path.join(C.ROOT, "ai_texts")
# somewhere neutral, so the corpus repo's own instructions do not steer the prose
NEUTRAL = os.environ.get("TMPDIR", "/tmp")

PROMPT = ("Write a blog post titled \"{title}\". "
          "It is for an audience of {area} professionals. "
          "Aim for about {words} words. "
          "Output only the post itself, with no preamble or commentary.")


def pick(docs, n, per_author=4):
    """A spread across authors and areas, so topics match the human side."""
    by = defaultdict(list)
    for d in sorted(docs, key=lambda x: (x["slug"], x["date"])):
        by[d["slug"]].append(d)
    out, rnd = [], 0
    while len(out) < n and rnd < per_author:
        for slug in sorted(by):
            if rnd < len(by[slug]) and len(out) < n:
                out.append(by[slug][rnd])
        rnd += 1
    return out


def generate(doc, model, timeout=300):
    slug = doc["slug"]
    outdir = os.path.join(AI, slug)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, os.path.basename(doc["path"]))
    if os.path.exists(path):
        return "have", path

    words = max(350, min(1400, doc["words"]))
    prompt = PROMPT.format(title=doc["title"], area=doc["area"].lower(), words=words)
    try:
        r = subprocess.run(["claude", "-p", "--model", model, prompt],
                           capture_output=True, text=True, timeout=timeout,
                           cwd=NEUTRAL)
    except subprocess.TimeoutExpired:
        return "timeout", doc["title"]
    body = (r.stdout or "").strip()
    if r.returncode != 0 or len(body.split()) < 120:
        return "failed", doc["title"]

    head = ["---",
            "source: generated",
            "model: %s" % model,
            "prompt_style: naive title + audience + length",
            "title: %s" % doc["title"],
            "type: %s" % doc["type"],
            "area: %s" % doc["area"],
            "matched_human_doc: %s" % doc["path"],
            "words: %d" % len(body.split()),
            "generated: %s" % date.today().isoformat(),
            "---"]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(head) + "\n\n" + body + "\n")
    return "wrote", path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--model", default=None,
                    help="one model; default alternates Opus 5 and Sonnet 5 so "
                         "a tell can be checked for holding across both")
    args = ap.parse_args()

    with open(os.path.join(C.ROOT, "manifest.json"), encoding="utf-8") as fh:
        docs = json.load(fh)["documents"]
    chosen = pick(docs, args.n)
    models = ([args.model] * len(chosen) if args.model else
              [("claude-opus-5", "claude-sonnet-5")[i % 2] for i in range(len(chosen))])

    os.makedirs(AI, exist_ok=True)
    tally = defaultdict(int)
    log = open(os.path.join(C.ROOT, "generate.log"), "a", encoding="utf-8")
    print("generating %d posts (%d workers)" % (len(chosen), args.workers), flush=True)

    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(generate, d, m): d for d, m in zip(chosen, models)}
        done = 0
        for fut in cf.as_completed(futs):
            status, what = fut.result()
            tally[status] += 1
            done += 1
            if done % 10 == 0 or status in ("failed", "timeout"):
                msg = "%3d/%d  %s" % (done, len(chosen), dict(tally))
                print(msg, flush=True)
                log.write(msg + "\n")
                log.flush()

    print("done:", dict(tally))


if __name__ == "__main__":
    main()
