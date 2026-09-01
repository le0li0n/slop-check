#!/usr/bin/env python3
"""Show raw CDX URLs for an author, before the permalink filter, from cache."""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
import build as B
from sources import AUTHORS

for slug in sys.argv[1:]:
    a = [x for x in AUTHORS if x["slug"] == slug][0]
    print("\n### %s" % slug)
    for seed in a["seeds"]:
        url = B.CDX % (urllib.parse.quote(seed, safe=""), 3000)
        hit = C.cache_get(url)
        if not hit or hit.get("status") != 200:
            print("  %s -> no cached response (%s)" % (seed, hit and hit.get("status")))
            continue
        try:
            rows = json.loads(hit["body"])[1:]
        except Exception:
            print("  %s -> unparseable" % seed)
            continue
        print("  %s -> %d rows" % (seed, len(rows)))
        seen = set()
        for r in rows:
            o = r[0]
            path = urllib.parse.urlsplit(o).path
            shape = "/".join(p[:14] for p in path.split("/")[:4])
            if shape in seen:
                continue
            seen.add(shape)
            print("     %s" % o[:110])
            if len(seen) >= 12:
                break
