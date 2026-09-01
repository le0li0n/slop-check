#!/usr/bin/env python3
"""Re-apply every rule to the files already on disk, then rebuild the manifest.

Builds are incremental, so a document collected before a rule tightened can
outlive the rule. This re-checks the corpus as a whole — cutoff, anachronisms,
duplicates across all authors — and rewrites manifest.json from what survives,
so the manifest always describes the files that are actually there.

  python3 tools/prune.py            # report only
  python3 tools/prune.py --apply    # delete offenders and rewrite the manifest
"""

import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
from build import looks_later_than

ROOT = C.ROOT
TEXTS = os.path.join(ROOT, "texts")

FIELDS = ("author", "title", "date", "date_basis", "type", "area",
          "source_url", "archived_url", "retrieved_from", "words", "retrieved")


def read_doc(path):
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if not raw.startswith("---"):
        return None, raw
    end = raw.find("\n---", 3)
    if end == -1:
        return None, raw
    meta = {}
    for line in raw[3:end].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, raw[end + 4:].lstrip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    docs, drop = [], []
    seen = {}
    for slug in sorted(os.listdir(TEXTS)):
        d = os.path.join(TEXTS, slug)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".txt"):
                continue
            path = os.path.join(d, fn)
            rel = os.path.relpath(path, ROOT)
            meta, body = read_doc(path)
            if not meta or not meta.get("date"):
                drop.append((rel, "no metadata"))
                continue
            if meta["date"] >= C.CUTOFF:
                drop.append((rel, "past the cutoff: %s" % meta["date"]))
                continue
            late = looks_later_than(body, meta["date"])
            if late:
                drop.append((rel, "mentions %d" % late))
                continue
            if len(body.split()) < 100:
                drop.append((rel, "too short"))
                continue
            h = hashlib.sha1(re.sub(r"\W+", "", body[:600]).lower().encode()).hexdigest()
            if h in seen:
                drop.append((rel, "same text as %s" % seen[h]))
                continue
            seen[h] = rel
            rec = {k: meta.get(k, "") for k in FIELDS}
            rec["slug"] = slug
            rec["path"] = rel
            rec["words"] = len(body.split())
            docs.append(rec)

    print("keep %d, drop %d" % (len(docs), len(drop)))
    for rel, why in drop:
        print("   drop %s — %s" % (rel, why))

    if not args.apply:
        print("\n(report only; pass --apply to act)")
        return

    for rel, _ in drop:
        os.remove(os.path.join(ROOT, rel))
    for slug in os.listdir(TEXTS):
        d = os.path.join(TEXTS, slug)
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)

    docs.sort(key=lambda d: (d["slug"], d["date"]))
    with open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"generated": docs[0]["retrieved"] if docs else "",
                   "cutoff": C.CUTOFF, "documents": docs}, fh, indent=1)
    authors = {d["slug"] for d in docs}
    ge5 = len([s for s in authors
               if len([d for d in docs if d["slug"] == s]) >= 5])
    print("\nmanifest rewritten: %d documents, %d authors, %d with five or more"
          % (len(docs), len(authors), ge5))


if __name__ == "__main__":
    main()
