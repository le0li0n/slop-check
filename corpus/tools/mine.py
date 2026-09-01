#!/usr/bin/env python3
"""Find what the machine writes that people do not.

Two corpora, matched on title, topic and length: one human and pre-2012, one
generated. For every n-gram, the question is not "which side uses it more" —
raw ratios put a hapax legomenon at the top of every list — but "how confident
are we that the rate differs at all". That is the log-odds ratio with an
informative Dirichlet prior (Monroe, Colaresi & Quinn, 2008), which shrinks
terms toward zero in proportion to how little evidence supports them.

A tell worth adding to the scanner needs three things, and this reports all
three: it must be frequent in machine prose, near-absent in human prose, and
spread across many documents rather than concentrated in one.

  python3 tools/mine.py                # write TELLS.md
  python3 tools/mine.py --n 2 --top 40 # just bigrams, to the terminal
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import corpuslib as C

AI = os.path.join(C.ROOT, "ai_texts")
WORD = re.compile(r"[a-z][a-z'’-]*")

# Formatting cannot be compared: the human side was extracted from HTML and
# lost its markup, so "##" and "**" would look like tells when they are
# artefacts of how each corpus was captured.
MARKDOWN = re.compile(r"^#{1,6}\s+|\*\*|__|^\s*[-*+]\s+|^\s*>\s?|`{1,3}|^\s*\d+\.\s+",
                      re.M)


def strip_front_matter(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e != -1:
            return t[e + 4:].lstrip()
    return t


def normalise(text):
    text = MARKDOWN.sub(" ", text)
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[“”]", '"', text)
    return text.lower()


def load(root, manifest=None):
    docs = []
    if manifest:
        with open(manifest, encoding="utf-8") as fh:
            for d in json.load(fh)["documents"]:
                p = os.path.join(C.ROOT, d["path"])
                if os.path.exists(p):
                    with open(p, encoding="utf-8") as f2:
                        docs.append(normalise(strip_front_matter(f2.read())))
        return docs
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if fn.endswith(".txt"):
                with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                    docs.append(normalise(strip_front_matter(fh.read())))
    return docs


# Candidate tells worth stating as rules rather than as n-grams: rhetorical
# frames the ranking above surfaced, plus the inverse tells — things people do
# and the model does not.
FRAMES = [
    ("em dash", r"[—–]", "the single widest gap; not wrong, but a habit"),
    ("first person (I, my, me)", r"\b(?:i|i'm|i've|i'd|my|me)\b", "INVERSE: people write from experience"),
    ("nobody / no one", r"\b(?:nobody|no one)\b", "rhetorical straw man"),
    ("actually", r"\bactually\b", "the corrective register"),
    ("worth (…ing/it/doing)", r"\bworth\b", "'worth noting', 'worth the'"),
    ("isn't / aren't / wasn't", r"\b(?:isn't|aren't|wasn't|weren't)\b", "negation-led contrast"),
    ("rather than", r"\brather than\b", "contrastive framing"),
    ("it's not X (it's Y)", r"\b(?:it|that|this)'s not\b|\bis not (?:a|the|about)\b|\bisn't (?:a|the|about)\b",
     "the defining frame of current machine prose"),
    ("none of this / that", r"\bnone of (?:this|that)\b", "the pivot-to-conclusion move"),
    ("the ones who / that", r"\bthe ones (?:who|that)\b", "sorting the world into two groups"),
    ("the thing is / that", r"\bthe thing (?:is|that)\b", "false intimacy"),
    ("what people get wrong", r"\b(?:get|gets|got) (?:it )?wrong\b", "contrarian opener"),
]


def frame_stats(docs, rx):
    words = sum(len(WORD.findall(d)) for d in docs)
    hits = sum(len(re.findall(rx, d)) for d in docs)
    ndocs = sum(1 for d in docs if re.search(rx, d))
    return (100.0 * ndocs / len(docs)) if docs else 0, (10000.0 * hits / words) if words else 0


def by_model(root):
    groups = {}
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith(".txt"):
                continue
            raw = open(os.path.join(dirpath, fn), encoding="utf-8").read()
            m = re.search(r"^model: (\S+)", raw, re.M)
            groups.setdefault(m.group(1) if m else "unknown", []).append(
                normalise(strip_front_matter(raw)))
    return groups


def ngrams(doc, n):
    w = WORD.findall(doc)
    if n == 1:
        return w
    return [" ".join(w[i:i + n]) for i in range(len(w) - n + 1)]


def counts(docs, n):
    total = Counter()
    docfreq = Counter()
    for d in docs:
        g = ngrams(d, n)
        total.update(g)
        docfreq.update(set(g))
    return total, docfreq


def log_odds(ai, hu, prior_weight=0.01):
    """Monroe et al: z-scored log-odds ratio, informative Dirichlet prior.

    The prior is the pooled corpus itself, scaled down; rare terms are pulled
    toward no-difference so that a word appearing twice cannot outrank a word
    appearing four hundred times.
    """
    pooled = Counter(ai)
    pooled.update(hu)
    n_pooled = sum(pooled.values())
    a0 = prior_weight * n_pooled
    n_ai, n_hu = sum(ai.values()), sum(hu.values())
    out = {}
    for w, cnt in pooled.items():
        a_w = prior_weight * cnt
        ai_w, hu_w = ai.get(w, 0), hu.get(w, 0)
        num_ai = ai_w + a_w
        num_hu = hu_w + a_w
        den_ai = n_ai + a0 - num_ai
        den_hu = n_hu + a0 - num_hu
        if den_ai <= 0 or den_hu <= 0:
            continue
        delta = math.log(num_ai / den_ai) - math.log(num_hu / den_hu)
        var = 1.0 / num_ai + 1.0 / num_hu
        out[w] = delta / math.sqrt(var)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=0, help="0 = 1,2,3 and 4-grams")
    ap.add_argument("--top", type=int, default=45)
    ap.add_argument("--min-ai-docs", type=int, default=None,
                    help="how many documents a term must appear in to be ranked; "
                         "defaults to 4%% of the set, floor 3")
    ap.add_argument("--dir", dest="ai_dir", default=AI,
                    help="the side to compare against the human corpus "
                         "(default: the generated set in ai_texts/). Point this "
                         "at your own drafts to see which tells you actually ship")
    ap.add_argument("--label", default=None,
                    help="what to call that side in the report (default: AI for "
                         "the generated set, otherwise the directory name)")
    ap.add_argument("--out", default=None,
                    help="output file (default: TELLS.md, or TELLS-<label>.md "
                         "when --dir is given, so a comparison never silently "
                         "overwrites the reference one)")
    args = ap.parse_args()

    generated = os.path.abspath(args.ai_dir) == os.path.abspath(AI)
    label = args.label or ("AI" if generated else os.path.basename(
        os.path.normpath(args.ai_dir)))

    human = load(None, manifest=os.path.join(C.ROOT, "manifest.json"))
    ai = load(args.ai_dir)
    if not ai:
        sys.exit("no .txt files in %s%s" % (
            args.ai_dir,
            " — run tools/generate_ai.py first" if generated else ""))
    hw = sum(len(WORD.findall(d)) for d in human)
    aw = sum(len(WORD.findall(d)) for d in ai)
    print("human: %d docs, %s words | %s: %d docs, %s words"
          % (len(human), f"{hw:,}", label, len(ai), f"{aw:,}"))

    min_docs = args.min_ai_docs
    if min_docs is None:
        min_docs = max(3, len(ai) // 25)
    if len(ai) < 60:
        print("note: %d documents is thin for phrase mining — the frame table "
              "holds up on small samples because it counts documents, but treat "
              "the n-gram rankings as suggestive only." % len(ai))

    sizes = [args.n] if args.n else [1, 2, 3, 4]
    report = {}
    for n in sizes:
        a_tot, a_df = counts(ai, n)
        h_tot, h_df = counts(human, n)
        z = log_odds(a_tot, h_tot)
        rows = []
        for term, score in z.items():
            if a_df[term] < min_docs:
                continue
            if score <= 0:
                continue
            ai_rate = 10000.0 * a_tot[term] / aw
            hu_rate = 10000.0 * h_tot[term] / hw
            rows.append((score, term, a_tot[term], h_tot[term], ai_rate, hu_rate,
                         100.0 * a_df[term] / len(ai), 100.0 * h_df[term] / len(human)))
        rows.sort(reverse=True)
        report[n] = rows[:args.top]

    title = ("Tells: what the model writes that these people did not" if generated
             else "Tells: %s against pre-2012 human writing" % label)
    provenance = ("generated from the same titles at the same lengths" if generated
                  else "from %s" % args.ai_dir)
    lines = ["# %s" % title, "",
             "Human side: %d documents, %s words, all published before 2012. "
             "%s side: %d documents, %s words, %s."
             % (len(human), f"{hw:,}", label[0].upper() + label[1:],
                len(ai), f"{aw:,}", provenance),
             "",
             "Ranked by z-scored log-odds with an informative Dirichlet prior, so "
             "a phrase has to be both lopsided *and* well evidenced to place. "
             "Rates are per 10,000 words. **Docs** is the share of documents on "
             "each side containing the term at least once — a tell that is common "
             "across many documents is worth more than one a single document "
             "repeats. A term must appear in %d documents to be ranked." % min_docs,
             "",]
    if len(ai) < 60:
        lines += ["> %d documents is thin for phrase mining. The frame table below "
                  "counts documents and holds up at this size; treat the n-gram "
                  "rankings as suggestive." % len(ai), ""]
    lines += [
             "Markdown syntax is stripped before counting: the human corpus was "
             "extracted from HTML and lost its formatting, so headings, bold and "
             "bullets cannot be compared fairly here.", ""]

    models = by_model(args.ai_dir)
    mnames = sorted(m for m in models if m != "unknown")
    lines += ["## The tells worth acting on", "",
              "Frames rather than words, because a frame survives paraphrase. "
              "**Docs** is the share of documents containing it at least once — "
              "the number that matters, since a tell you can only see by "
              "counting repetitions inside one piece is not much of a tell.", "",
              ("Checked separately against each generating model, so a habit of one "
               "model does not get mistaken for a property of machine prose."
               if mnames else
               "No model recorded in these files, so there is no per-model split."), ""]
    hdr = "| frame | %s docs | human docs | %s /10k | human /10k |" % (label, label)
    sep = "| --- | ---: | ---: | ---: | ---: |"
    for m in mnames:
        hdr += " %s |" % m.replace("claude-", "")
        sep += " ---: |"
    lines += [hdr + " note |", sep + " --- |"]
    for name, rx, note in FRAMES:
        ad, ar = frame_stats(ai, rx)
        hd, hr = frame_stats(human, rx)
        row = "| %s | %.0f%% | %.0f%% | %.1f | %.1f |" % (name, ad, hd, ar, hr)
        for m in mnames:
            row += " %.0f%% |" % frame_stats(models[m], rx)[0]
        lines.append(row + " %s |" % note)
    lines.append("")

    names = {1: "Words", 2: "Two-word phrases", 3: "Three-word phrases", 4: "Four-word phrases"}
    for n in sizes:
        lines += ["## %s" % names.get(n, "%d-grams" % n), "",
                  "| term | %s /10k | human /10k | %s docs | human docs | z |" % (label, label),
                  "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for score, term, _a, _h, ar, hr, adf, hdf in report[n]:
            lines.append("| `%s` | %.1f | %.2f | %.0f%% | %.0f%% | %.1f |"
                         % (term, ar, hr, adf, hdf, score))
        lines.append("")

    absent = []
    for n in sizes:
        for score, term, a, h, ar, hr, adf, hdf in report[n]:
            if h == 0 and adf >= 20:
                absent.append((adf, term, ar, n))
    absent.sort(reverse=True)
    if absent:
        lines += ["## Never once in 330,000 words of human prose", "",
                  "These appear in at least a fifth of %s documents and " % label +
                  "**zero** human ones. They are the safest patterns to add: a "
                  "hit cannot be a false positive against this corpus.", "",
                  "| term | in %% of %s docs | %s /10k |" % (label, label), "| --- | ---: | ---: |"]
        for adf, term, ar, _n in absent[:40]:
            lines.append("| `%s` | %.0f%% | %.1f |" % (term, adf, ar))
        lines.append("")

    out = args.out or os.path.join(
        C.ROOT, "TELLS.md" if generated else "TELLS-%s.md" % C.slugify(label))
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print("wrote %s" % out)
    for n in sizes:
        print("\n-- top %d-grams --" % n)
        for score, term, _a, _h, ar, hr, adf, _hdf in report[n][:12]:
            print("  %-34s ai %6.1f  human %5.2f  in %3.0f%% of ai docs  z=%.1f"
                  % (term, ar, hr, adf, score))


if __name__ == "__main__":
    main()
