#!/usr/bin/env python3
"""For authors yielding nothing, report what happens to their first few candidates."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
import build as B
from sources import AUTHORS

for slug in sys.argv[1:]:
    a = [x for x in AUTHORS if x["slug"] == slug][0]
    perms = B.discover(a)
    print("\n=== %s (%d candidates)" % (slug, len(perms)))
    if not perms:
        continue
    step = max(1, len(perms) // 4)
    for original, ts in [perms[i * step] for i in range(min(4, len(perms)))]:
        live = B.live_url(original)
        r = C.fetch(live, timeout=12, retries=1)
        line = "  %-3s %s" % (r["status"], live[:76])
        if r["status"] == 200:
            title, text = C.extract_text(r["body"])
            text, _ = B.tidy(text)
            pub, basis = B.resolve_date(original, r["body"], text, ts)
            claimed = C.date_from_url(original) or C.date_from_html(r["body"])
            line += "\n      chars=%d date=%s (%s) claimed=%s title=%r" % (
                len(text), pub, basis, claimed, title[:40])
        print(line)
