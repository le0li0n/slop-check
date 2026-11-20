#!/usr/bin/env python3
"""Check an author profile keeps the promises in profile-spec.md, then render it.

A profile written by reading the texts is only as good as its evidence, so
this checks the evidence mechanically: every quote must appear in the file it
cites, no quote may come from the held-out document, the piece counts must be
possible, and every measured trait must be accounted for. It then writes
profile.md, the version meant for a person to read.

  python3 tools/check_profile.py paul-graham
  python3 tools/check_profile.py --all
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
import mine

PROFILES = os.path.join(C.ROOT, "texts", "profiles")
VOICE = {"opening", "structure", "argument", "evidence", "sentence", "lexicon", "reader", "humor", "closing"}
WORLD = {"belief", "opponent", "value", "reasoning", "temperament", "reader", "authority"}


def squash(text):
    """Compare quotes on words alone: extraction and copying disagree about quotes, dashes and spacing."""
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return " ".join(re.findall(r"[a-z0-9']+", text.lower()))


def check(slug):
    d = os.path.join(PROFILES, slug)
    with open(os.path.join(d, "measured.json"), encoding="utf-8") as fh:
        measured = json.load(fh)
    try:
        with open(os.path.join(d, "profile.json"), encoding="utf-8") as fh:
            pr = json.load(fh)
    except (OSError, ValueError) as e:
        return None, ["cannot read profile.json: %s" % e]

    problems = []
    allowed = {x["path"] for x in measured["documents"]}
    held = measured["held_out"]["path"]
    n_docs = len(allowed)
    source = {}
    for p in allowed:
        with open(os.path.join(C.ROOT, p), encoding="utf-8") as fh:
            source[p] = squash(mine.strip_front_matter(fh.read()))
    names = {s["feature"] for s in measured["shape"]}
    names |= {r["term"] for key in ("phrases", "function_habits", "avoids") for r in measured[key]}

    def evidence(item, where, min_docs):
        ev = item.get("evidence") or []
        if not ev:
            problems.append("%s: no evidence" % where)
        cited = set()
        for e in ev:
            doc, quote = e.get("doc", ""), e.get("quote", "")
            if doc == held:
                problems.append("%s: quotes the HELD-OUT document" % where)
                continue
            if doc not in allowed:
                problems.append("%s: cites a document outside the measured set: %s" % (where, doc))
                continue
            n = len(quote.split())
            if n < 5 or n > 40:
                problems.append("%s: quote is %d words (5–40): %.60s" % (where, n, quote))
            if squash(quote) not in source[doc]:
                problems.append("%s: quote not found in %s: %.80s" % (where, os.path.basename(doc), quote))
            cited.add(doc)
        m = re.match(r"^(\d+)/(\d+)$", str(item.get("docs_showing", "")))
        if not m or int(m.group(2)) != n_docs or int(m.group(1)) > n_docs:
            problems.append("%s: docs_showing should be k/%d, got %r" % (where, n_docs, item.get("docs_showing")))
        elif int(m.group(1)) < min_docs:
            problems.append("%s: shown in %s pieces, needs %d" % (where, m.group(0), min_docs))
        elif int(m.group(1)) < len(cited):
            problems.append("%s: cites %d pieces but claims %s" % (where, len(cited), m.group(0)))

    for i, v in enumerate(pr.get("voice", [])):
        where = "voice %s" % v.get("id", i)
        if v.get("category") not in VOICE:
            problems.append("%s: unknown category %r" % (where, v.get("category")))
        for f in ("trait", "how_to_apply"):
            if not v.get(f):
                problems.append("%s: missing %s" % (where, f))
        for name in v.get("measured") or []:
            if name not in names:
                problems.append("%s: measured name not in measured.json: %r" % (where, name))
        evidence(v, where, 2)

    for i, w in enumerate(pr.get("worldview", [])):
        where = "worldview %s" % w.get("id", i)
        if w.get("category") not in WORLD:
            problems.append("%s: unknown category %r" % (where, w.get("category")))
        if w.get("kind") not in ("stated", "inferred"):
            problems.append("%s: kind must be stated or inferred" % where)
        for f in ("claim", "generalizes_as"):
            if not w.get(f):
                problems.append("%s: missing %s" % (where, f))
        evidence(w, where, 1)
    missing = WORLD - {w.get("category") for w in pr.get("worldview", [])}
    if missing and not pr.get("evidence_note"):
        problems.append("worldview categories absent with no evidence_note: %s" % ", ".join(sorted(missing)))

    covered = {n for v in pr.get("voice", []) for n in (v.get("measured") or [])}
    covered |= {u.get("feature") for u in pr.get("unexplained_measured", [])}
    covered |= {n.get("basis") for n in pr.get("never", [])}
    for s in measured["shape"]:
        if s["trait"] and s["feature"] not in covered:
            problems.append("measured trait not accounted for: %s (pct %d)" % (s["feature"], s["percentile"]))

    counts = (len(pr.get("voice", [])), len(pr.get("worldview", [])), len(pr.get("never", [])))
    for label, n, lo, hi in (("voice", counts[0], 8, 15), ("worldview", counts[1], 8, 20), ("never", counts[2], 3, 8)):
        if not lo <= n <= hi:
            problems.append("%d %s items; spec asks for %d–%d" % (n, label, lo, hi))
    return pr, problems


def render(pr, measured):
    lines = ["# %s" % pr["author"], "",
             "*%s. Built from %d pieces; held out: %s.*" % (
                 pr.get("span", ""), len(pr.get("built_from", [])), measured["held_out"]["title"]), "",
             pr.get("summary", ""), ""]
    if pr.get("evidence_note"):
        lines += ["> %s" % pr["evidence_note"], ""]

    def quotes(item):
        return ["   > %s *(%s)*" % (e["quote"], os.path.basename(e["doc"])[:10]) for e in item.get("evidence", [])]

    lines += ["## Voice", ""]
    for v in pr.get("voice", []):
        lines.append("- **%s** · %s · %s  " % (v["category"], v["docs_showing"], v["trait"]))
        lines.append("  *Apply:* %s" % v["how_to_apply"])
        if v.get("measured"):
            lines.append("  *Measured:* %s" % ", ".join("`%s`" % m for m in v["measured"]))
        lines += quotes(v) + [""]
    lines += ["## Worldview", ""]
    for w in pr.get("worldview", []):
        lines.append("- **%s** · %s · %s · %s  " % (w["category"], w["kind"], w["docs_showing"], w["claim"]))
        lines.append("  *Generalizes as:* %s" % w["generalizes_as"])
        lines += quotes(w) + [""]
    lines += ["## Never", ""]
    for n in pr.get("never", []):
        lines.append("- %s · %s *(%s)*" % (n["docs_showing"], n["trait"], n["basis"]))
    if pr.get("unexplained_measured"):
        lines += ["", "## Measured but not a trait", ""]
        for u in pr["unexplained_measured"]:
            lines.append("- `%s`: %s" % (u["feature"], u["why"]))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dir", help="profiles directory to check instead of texts/profiles/, "
                                  "for a draft kept outside the corpus")
    args = ap.parse_args()
    global PROFILES
    if args.dir:
        PROFILES = os.path.abspath(args.dir)
    if args.all:
        slugs = sorted(s for s in os.listdir(PROFILES) if os.path.exists(os.path.join(PROFILES, s, "profile.json")))
    elif args.slug:
        slugs = [args.slug]
    else:
        sys.exit("name an author slug, or --all")

    failed = 0
    for slug in slugs:
        pr, problems = check(slug)
        if problems:
            failed += 1
            print("%s: %d problems" % (slug, len(problems)))
            for p in problems:
                print("   " + p)
        else:
            print("%s: ok — %d voice, %d worldview, %d never" % (
                slug, len(pr["voice"]), len(pr["worldview"]), len(pr["never"])))
        if pr:
            with open(os.path.join(PROFILES, slug, "measured.json"), encoding="utf-8") as fh:
                measured = json.load(fh)
            with open(os.path.join(PROFILES, slug, "profile.md"), "w", encoding="utf-8") as fh:
                fh.write(render(pr, measured))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
