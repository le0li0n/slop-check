#!/usr/bin/env python3
"""Measure what sets each author's prose apart from everyone else's.

The corpus baseline asks what human writing looks like in general. This asks
the narrower question: what does *this* writer do that the other sixty do not?
It is the measured half of an author profile — numbers and phrases a reading
of the texts has to agree with, so that a description like "short, punchy
sentences" is checked against the sentences.

Two kinds of evidence, both measured against the rest of the corpus:

  shape    the features in profile.py plus a few that bear on stance
           (hedging, absolutes, prescriptive verbs, numbers, "we").
           Each author's median is ranked among all authors' medians, and
           a feature only counts as a trait if most of that author's pieces
           sit on the same side of the corpus median. One odd essay is not
           a habit.
  phrases  n-grams ranked by the same z-scored log-odds as mine.py, author
           against everyone else, kept only if they appear in at least half
           the author's pieces. Split into content phrases, function-word
           habits ("and so", "i think"), and common words the author avoids.

One document per author is held out and never measured, so a later test can
ask whether a profile predicts a piece it has not seen. The choice is a hash
of the path: stable across runs and untouched when authors are added.

  python3 tools/styles.py                   # every author, written to texts/profiles/
  python3 tools/styles.py --author paul-graham

Output goes to the private corpus clone, beside the texts it describes.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C
import mine

# tools/profile.py shares a name with the standard library's profiler, so load it by path
_spec = importlib.util.spec_from_file_location(
    "corpus_profile", os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

TEXTS = os.path.join(C.ROOT, "texts")
PROFILES = os.path.join(TEXTS, "profiles")
HOLDOUT = os.path.join(C.ROOT, "holdout.json")

MIN_DOCS = 5          # below this an author has too little to profile
N_FUNCTION = 100      # the commonest words by document frequency count as function words

WE = re.compile(r"\b(?:we|we're|we've|we'd|we'll|us|our|ours)\b", re.I)
HEDGED = re.compile(r"\b(?:i think|i suspect|i guess|i believe|maybe|perhaps|probably|"
                    r"possibly|seems?|might)\b", re.I)
ABSOLUTE = re.compile(r"\b(?:always|never|everyone|everybody|nobody|nothing|"
                      r"certainly|clearly|obviously|undoubtedly)\b", re.I)
PRESCRIPTIVE = re.compile(r"\b(?:should|shouldn't|must|need to|needs to|have to|has to)\b", re.I)
NUMBER = re.compile(r"\$\d|\b\d[\d,.]*%?")


def features(body):
    f = P.features(body)
    if not f:
        return None
    ws = [w.lower() for w in P.WORD.findall(body)]
    n = len(ws)
    per1k = lambda c: 1000.0 * c / n

    # profile.py measures these over a whole document, so a 3,000-word essay
    # scores low on both simply for being long. Comparing authors whose pieces
    # run 300 words against authors whose pieces run 3,000 needs a fixed window.
    win = min(100, n)
    f["vocabulary variety"] = sum(len(set(ws[i:i + win])) for i in range(n - win + 1)) / float(win * (n - win + 1))
    openers = [P.WORD.findall(s)[0].lower() for s in P.SENT.split(body) if P.WORD.findall(s)]
    win = min(20, len(openers))
    f["distinct openers %"] = 100.0 * sum(len(set(openers[i:i + win])) for i in range(len(openers) - win + 1)) \
        / float(win * (len(openers) - win + 1))

    paras = [p for p in body.split("\n\n") if p.strip()]
    single = sum(1 for p in paras if len([s for s in P.SENT.split(p.strip()) if s.strip()]) == 1)
    f["paragraph length (words)"] = float(n) / len(paras)
    f["one-sentence paragraphs %"] = 100.0 * single / len(paras)
    f["we / us / our /1k"] = per1k(len(WE.findall(body)))
    f["hedged (I think, maybe) /1k"] = per1k(len(HEDGED.findall(body)))
    f["absolutes (always, nobody) /1k"] = per1k(len(ABSOLUTE.findall(body)))
    f["prescriptive (should, must) /1k"] = per1k(len(PRESCRIPTIVE.findall(body)))
    f["numbers /1k"] = per1k(len(NUMBER.findall(body)))
    f["quotations /1k"] = per1k((body.count('"') + body.count("“") + body.count("”")) / 2.0)
    f["parentheses /1k"] = per1k(body.count("("))
    f["colon /1k"] = per1k(body.count(":"))
    return f


def median(xs):
    xs = sorted(xs)
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2.0


def split(docs):
    """One held-out document per profiled author, chosen by a hash of its path."""
    by = defaultdict(list)
    for d in docs:
        by[d["slug"]].append(d)
    train, held = {}, {}
    for slug, ds in sorted(by.items()):
        if len(ds) < MIN_DOCS:
            continue
        ds = sorted(ds, key=lambda d: hashlib.sha1(d["path"].encode("utf-8")).hexdigest())
        held[slug], train[slug] = ds[0], ds[1:]
    return train, held


def log_odds(term_counts, target, rest, n_target, n_rest, prior_weight=0.01):
    """mine.log_odds, restricted to the terms asked about.

    Scoring every n-gram in the corpus for every author is sixty passes over a
    million terms; only the ones an author uses often enough to matter need it.
    """
    n_pooled = n_target + n_rest
    a0 = prior_weight * n_pooled
    out = {}
    for w in term_counts:
        a_w = prior_weight * (target.get(w, 0) + rest.get(w, 0))
        num_t = target.get(w, 0) + a_w
        num_r = rest.get(w, 0) + a_w
        den_t = n_target + a0 - num_t
        den_r = n_rest + a0 - num_r
        if den_t <= 0 or den_r <= 0:
            continue
        delta = math.log(num_t / den_t) - math.log(num_r / den_r)
        out[w] = delta / math.sqrt(1.0 / num_t + 1.0 / num_r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--author", help="one author slug, printed instead of written")
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    if not os.path.isdir(TEXTS):
        sys.exit("no texts/ — clone the private corpus first (see README.md)")
    with open(os.path.join(C.ROOT, "manifest.json"), encoding="utf-8") as fh:
        docs = json.load(fh)["documents"]
    train, held = split(docs)
    held_paths = {d["path"] for d in held.values()}

    # Load every document once. Held-out pieces stay out of every count,
    # including the background other authors are compared against.
    body, feats, grams, words = {}, {}, {}, {}
    for d in docs:
        if d["path"] in held_paths:
            continue
        p = os.path.join(C.ROOT, d["path"])
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            raw = mine.strip_front_matter(fh.read())
        body[d["path"]] = raw
        feats[d["path"]] = features(raw)
        norm = mine.normalise(raw)
        words[d["path"]] = len(mine.WORD.findall(norm))
        grams[d["path"]] = {n: Counter(mine.ngrams(norm, n)) for n in (1, 2, 3)}

    docfreq = Counter()
    for g in grams.values():
        docfreq.update(g[1].keys())
    function_words = {w for w, _ in docfreq.most_common(N_FUNCTION)}

    total = {n: Counter() for n in (1, 2, 3)}
    for g in grams.values():
        for n in (1, 2, 3):
            total[n].update(g[n])
    total_words = sum(words.values())

    # ---- shape: each author's median, ranked among all authors' medians
    keys = None
    author_median = {}
    for slug, ds in train.items():
        rows = [feats[d["path"]] for d in ds if feats.get(d["path"])]
        if not rows:
            continue
        keys = keys or list(rows[0].keys())
        author_median[slug] = {k: median([r[k] for r in rows]) for k in keys}
    all_rows = [f for path, f in feats.items() if f and any(path == d["path"] for ds in train.values() for d in ds)]
    corpus_median = {k: median([r[k] for r in all_rows]) for k in keys}

    targets = [args.author] if args.author else sorted(author_median)
    if args.author and args.author not in author_median:
        sys.exit("no profile for %s: unknown slug, or fewer than %d documents" % (args.author, MIN_DOCS))

    profiles = {}
    for slug in targets:
        ds = train[slug]
        paths = [d["path"] for d in ds if d["path"] in grams]
        rows = [feats[p] for p in paths if feats.get(p)]
        others = [m for s, m in author_median.items() if s != slug]

        shape = []
        for k in keys:
            v = author_median[slug][k]
            below = sum(1 for m in others if m[k] < v)
            equal = sum(1 for m in others if m[k] == v)
            pct = 100.0 * (below + 0.5 * equal) / len(others)
            side = (v > corpus_median[k]) - (v < corpus_median[k])
            agree = (sum(1 for r in rows if ((r[k] > corpus_median[k]) - (r[k] < corpus_median[k])) == side)
                     / float(len(rows))) if side else 0.0
            shape.append({"feature": k, "author": round(v, 2), "corpus": round(corpus_median[k], 2),
                          "percentile": round(pct), "direction": "high" if side > 0 else "low" if side < 0 else "",
                          "docs_agree": round(agree, 2),
                          "trait": (pct <= 10 or pct >= 90) and agree >= 0.8})
        shape.sort(key=lambda s: -abs(s["percentile"] - 50))

        # ---- phrases: this author against everyone else
        n_author = sum(words[p] for p in paths)
        min_docs = max(3, int(math.ceil(len(paths) / 2.0)))
        content, habits, avoids = [], [], []
        for n in (1, 2, 3):
            mine_c = Counter()
            dfreq = Counter()
            for p in paths:
                mine_c.update(grams[p][n])
                dfreq.update(grams[p][n].keys())
            rest = total[n] - mine_c
            n_rest = total_words - n_author
            spread = [t for t in mine_c if dfreq[t] >= min_docs]
            z = log_odds(spread, mine_c, rest, n_author, n_rest)
            for t, score in z.items():
                if score < 2.0:
                    continue
                row = {"term": t, "z": round(score, 1), "docs": "%d/%d" % (dfreq[t], len(paths)),
                       "author_per10k": round(10000.0 * mine_c[t] / n_author, 1),
                       "rest_per10k": round(10000.0 * rest[t] / n_rest, 2)}
                if all(w in function_words for w in t.split()):
                    habits.append(row)
                else:
                    content.append(row)
            if n == 1:
                # common words this author leaves out; spread is judged on everyone else
                common = [w for w in function_words if mine_c[w] <= rest[w]]
                for w, score in log_odds(common, mine_c, rest, n_author, n_rest).items():
                    if score <= -2.0:
                        avoids.append({"term": w, "z": round(score, 1),
                                       "docs": "%d/%d" % (dfreq[w], len(paths)),
                                       "author_per10k": round(10000.0 * mine_c[w] / n_author, 1),
                                       "rest_per10k": round(10000.0 * rest[w] / n_rest, 2)})
        for lst in (content, habits):
            lst.sort(key=lambda r: -r["z"])
        avoids.sort(key=lambda r: r["z"])

        meta = ds[0]
        profiles[slug] = {
            "author": meta["author"], "slug": slug,
            "words_measured": n_author,
            "documents": [{"title": d["title"], "date": d["date"], "words": d["words"], "path": d["path"]}
                          for d in sorted(ds, key=lambda d: d["date"])],
            "held_out": {"title": held[slug]["title"], "date": held[slug]["date"], "path": held[slug]["path"]},
            "shape": shape,
            "phrases": content[:args.top],
            "function_habits": habits[:args.top],
            "avoids": avoids[:15],
        }

    if args.author:
        pr = profiles[args.author]
        print("%s — %d documents, %s words (held out: %s)\n"
              % (pr["author"], len(pr["documents"]), f"{pr['words_measured']:,}", pr["held_out"]["title"]))
        print("%-34s %8s %8s %5s %6s" % ("feature", "author", "corpus", "pct", "agree"))
        for s in pr["shape"][:15]:
            print("%-34s %8.2f %8.2f %5d %6.2f %s" % (s["feature"], s["author"], s["corpus"],
                                                    s["percentile"], s["docs_agree"], "TRAIT" if s["trait"] else ""))
        for name in ("phrases", "function_habits", "avoids"):
            print("\n-- %s --" % name)
            for r in pr[name][:15]:
                print("  %-28s z=%5.1f  %s docs  %6.1f vs %6.2f /10k"
                      % (r["term"], r["z"], r["docs"], r["author_per10k"], r["rest_per10k"]))
        return

    os.makedirs(PROFILES, exist_ok=True)
    for slug, pr in profiles.items():
        d = os.path.join(PROFILES, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "measured.json"), "w", encoding="utf-8") as fh:
            json.dump(pr, fh, indent=1)

    with open(HOLDOUT, "w", encoding="utf-8") as fh:
        json.dump({"note": "one document per author, never measured; see tools/styles.py",
                   "held_out": {s: {"title": h["title"], "date": h["date"], "path": h["path"]}
                                for s, h in sorted(held.items())}}, fh, indent=1)

    write_report(profiles, len(docs) - len(held), total_words)
    thin = sorted({d["author"] for d in docs if d["slug"] not in train})
    print("profiled %d authors; %d too thin to profile: %s" % (len(profiles), len(thin), ", ".join(thin)))
    print("wrote %s/<slug>/measured.json, %s, %s"
          % (os.path.relpath(PROFILES, C.ROOT), os.path.relpath(os.path.join(PROFILES, "MEASURED.md"), C.ROOT),
             os.path.relpath(HOLDOUT, C.ROOT)))


def write_report(profiles, n_docs, n_words):
    lines = ["# Measured author profiles", "",
             "What each author does that the rest of the corpus does not, measured over %d documents and %s words with one piece per author held out. Generated by `tools/styles.py`; the reasoning is in its docstring." % (n_docs, f"{n_words:,}"), "",
             "**Shape.** Each author's median is ranked among every author's median. **pct** is that rank: 95 means higher than 95% of authors. **agree** is the share of the author's pieces on the same side of the corpus median. A feature is marked a trait when it ranks in the top or bottom tenth and at least four in five pieces agree. Features ranked in the outer 15% with two-thirds agreement are listed as leanings.", "",
             "**Phrases** appear in at least half the author's pieces and score z ≥ 2 against everyone else. Topic words rank high here and describe subject matter more than voice. **Habits** are the same test restricted to the corpus's hundred commonest words, which is where voice tends to show. **Avoids** are common words the author uses markedly less.", ""]
    for slug in sorted(profiles, key=lambda s: profiles[s]["author"].lower()):
        pr = profiles[slug]
        lines += ["## %s" % pr["author"], "",
                  "%d pieces, %s words, %s to %s. Held out: *%s* (%s)." % (
                      len(pr["documents"]), f"{pr['words_measured']:,}", pr["documents"][0]["date"][:4],
                      pr["documents"][-1]["date"][:4], pr["held_out"]["title"], pr["held_out"]["date"][:4]), ""]
        shown = [s for s in pr["shape"] if s["trait"] or ((s["percentile"] <= 15 or s["percentile"] >= 85) and s["docs_agree"] >= 0.67)]
        if shown:
            lines += ["| feature | author | corpus | pct | agree | |", "| --- | ---: | ---: | ---: | ---: | --- |"]
            for s in shown:
                lines.append("| %s | %.2f | %.2f | %d | %.0f%% | %s |" % (
                    s["feature"], s["author"], s["corpus"], s["percentile"], 100 * s["docs_agree"],
                    "trait" if s["trait"] else "leaning"))
            lines.append("")
        else:
            lines += ["No shape feature stands out consistently.", ""]
        for label, key, k in (("Phrases", "phrases", 12), ("Habits", "function_habits", 10), ("Avoids", "avoids", 8)):
            items = pr[key][:k]
            if items:
                lines.append("**%s:** %s" % (label, ", ".join(
                    "`%s` (%s, %s)" % (r["term"], ("%+.1f" % r["z"]).replace("+", ""), r["docs"]) for r in items)))
                lines.append("")
    with open(os.path.join(PROFILES, "MEASURED.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()
