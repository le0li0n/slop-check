#!/usr/bin/env python3
"""Check the corpus keeps its promises.

The one that matters: nothing published on or after the cutoff. This checks the
recorded dates, that they agree with the files, and — because a live page can
be edited after the fact — looks in the prose itself for signs of a later
rewrite. A pre-2012 post mentioning 2016 is either a quotation about the future
or a page that changed under us, and either way it deserves a human glance.
"""

import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C

ROOT = C.ROOT
CUTOFF_YEAR = int(C.CUTOFF[:4])


def front_matter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[end + 4:].lstrip()


def main():
    with open(os.path.join(ROOT, "manifest.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    docs = man["documents"]

    problems = []
    late_mentions = []
    counts = Counter()
    words = 0
    seen_hash = {}

    for d in docs:
        p = os.path.join(ROOT, d["path"])
        if not os.path.exists(p):
            problems.append("missing file: %s" % d["path"])
            continue
        with open(p, encoding="utf-8") as fh:
            raw = fh.read()
        meta, body = front_matter(raw)

        if d["date"] >= C.CUTOFF:
            problems.append("PAST CUTOFF: %s dated %s" % (d["path"], d["date"]))
        if meta.get("date") != d["date"]:
            problems.append("date mismatch: %s file=%s manifest=%s"
                            % (d["path"], meta.get("date"), d["date"]))
        for field in ("author", "title", "type", "area", "source_url"):
            if not meta.get(field):
                problems.append("missing %s: %s" % (field, d["path"]))
        if len(body.split()) < 100:
            problems.append("suspiciously short: %s (%d words)" % (d["path"], len(body.split())))

        key = body[:400]
        if key in seen_hash:
            problems.append("duplicate text: %s == %s" % (d["path"], seen_hash[key]))
        seen_hash[key] = d["path"]

        counts[d["slug"]] += 1
        words += len(body.split())

        # years later than the cutoff, mentioned in prose that predates it
        later = sorted({int(y) for y in re.findall(r"\b(20[12]\d)\b", body)
                        if int(y) > CUTOFF_YEAR})
        if later:
            late_mentions.append((d["path"], d["date"], later[:6]))

    authors_ok = [s for s, n in counts.items() if n >= 5]

    print("documents            %d" % len(docs))
    print("words                %s" % f"{words:,}")
    print("authors              %d" % len(counts))
    print("authors with >=5     %d" % len(authors_ok))
    print("date range           %s .. %s" % (min(d["date"] for d in docs),
                                             max(d["date"] for d in docs)))
    print("date basis           %s" % dict(Counter(d["date_basis"] for d in docs)))
    print("retrieved from       %s" % dict(Counter(d["retrieved_from"] for d in docs)))
    print("types                %s" % dict(Counter(d["type"] for d in docs)))
    print("areas                %s" % dict(Counter(d["area"] for d in docs)))

    print("\nintegrity problems:  %d" % len(problems))
    for p in problems[:40]:
        print("   " + p)

    print("\ndocuments mentioning a post-2011 year: %d" % len(late_mentions))
    for path, dt, years in late_mentions[:25]:
        print("   %s (%s) mentions %s" % (path, dt, years))

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
