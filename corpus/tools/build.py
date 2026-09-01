#!/usr/bin/env python3
"""Build the pre-2012 human writing corpus.

Discovery and retrieval both run through the Wayback Machine, restricted to
captures taken before 2012-01-01. A capture from 2011 is proof the text existed
in 2011; a live page carrying a 2009 date is not, because it may have been
edited since. Every document therefore has a date ceiling it cannot escape.

  python3 tools/build.py --target 6
  python3 tools/build.py --only seth-godin --target 8
"""

import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.parse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import corpuslib as C
from sources import AUTHORS, GENERIC_ACCEPT, GENERIC_REJECT

TEXTS = os.path.join(C.ROOT, "texts")
CDX = ("https://web.archive.org/cdx/search/cdx?url=%s&matchType=prefix"  # no "*": the API rejects both together
       "&from=1994&to=20111231&output=json&fl=original,timestamp,statuscode,mimetype"
       "&filter=statuscode:200&filter=mimetype:text/html&collapse=urlkey&limit=%d")

RETRIEVED = date.today().isoformat()

# Furniture that survives extraction on 2000s blog templates.
LINE_JUNK = re.compile(
    r"^(?:permalink|comments?(?:\s*\(\d+\))?|email this|digg this|digg|del\.icio\.us|"
    r"reddit|stumbleupon|share(?: this)?|tweet|retweet|print(?:er friendly)?|"
    r"posted (?:by|at|on)\b.*|filed under\b.*|tags?:.*|categor(?:y|ies):.*|"
    r"continue reading.*|read (?:more|the rest).*|trackbacks?(?:\s*\(\d+\))?|"
    r"reply|leave a (?:comment|reply)|subscribe.*|rss|home|about|contact|archives?|"
    r"next(?: post| entry|:)?.*|previous(?: post| entry|:)?.*|\d+ comments?|"
    r"bookmark.*|sponsored.*|advertisement|follow me.*|by \w+ \w+|"
    r"get new posts.*|sign up.*|cite this post|get the book.*|buy the book.*|"
    r"add to:.*|share on.*|email this post.*|labels:.*|posted in.*|"
    r"related:.*|see also:?|more like this|about the author.*)$",
    re.I)

# A run of short, unpunctuated lines at the end of a page is a blogroll, a
# related-posts list, or a row of social bookmark links — never the argument.
def trim_tail(parts):
    while parts:
        p = parts[-1].strip()
        lines = [l for l in p.split("\n") if l.strip()]
        # Three or more stacked short lines is a list of links. A single short
        # closing line ("Go to it!") is the author, so leave it be.
        listish = len(lines) >= 3 and all(len(l) < 45 for l in lines)
        stub = len(p) < 60 and not re.search(r"[.!?]['\"”’)]?$", p)
        if listish or stub:
            parts.pop()
            continue
        break
    return parts

# Typepad and Movable Type put "« Previous | Main | Next »" inline with the post.
NAV_LINE = re.compile(r"^\s*(?:«|»|\||\bmain\b\s*\|)|(?:«|»)\s*$|^\s*\|\s*main\s*\|", re.I)

# Where the article stops and the page's machinery starts.
CUT_AT = re.compile(
    r"^(?:comments?\s*\(\d+\)|\d+\s+comments?|post a comment|leave a (?:comment|reply)|"
    r"add a comment|trackback|trackbacks?\s*\(\d+\)|related posts?|you might also like|"
    r"related articles?|about the author|share this (?:post|entry)|"
    r"previous(?: post| entry)|recent posts|recent comments|categories|blog archive|"
    r"subscribe to|sign up for|posted by .{0,60}(?:comments|permalink))\b",
    re.I)


JUNK_QS = re.compile(r"^(?:no_prefetch|utm_\w+|ref|src|fbclid|from|cid|mc_cid|mc_eid)$", re.I)


def norm_url(u):
    u = u.strip()
    if not u.startswith("http"):
        u = "http://" + u
    p = urllib.parse.urlsplit(u)
    host = re.sub(r":(?:80|443)$", "", p.netloc.lower())
    if host.startswith("www."):
        host = host[4:]
    path = re.sub(r"/+$", "", p.path) or "/"
    qs = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not JUNK_QS.match(k)]
    return urllib.parse.urlunsplit(("http", host, path, urllib.parse.urlencode(qs), ""))


def looks_like_permalink(url, author):
    url = re.sub(r"(://[^/]+?):(?:80|443)(?=/|$)", r"\1", url)   # archived URLs keep the port
    if re.search(author.get("reject", "") or r"(?!x)x", url, re.I):
        return False
    if re.search(GENERIC_REJECT, url, re.I):
        return False
    acc = author.get("accept")
    if acc:
        return bool(re.search(acc, url, re.I))
    return any(re.search(p, url, re.I) for p in GENERIC_ACCEPT)


def discover(author, per_seed=3000):
    """Pre-2012 permalinks for one author, earliest capture first."""
    found = {}
    for seed in author["seeds"]:
        url = CDX % (urllib.parse.quote(seed, safe=""), per_seed)
        r = C.fetch(url, timeout=120, retries=4)
        if r["status"] != 200 or not r["body"].strip():
            continue
        try:
            rows = json.loads(r["body"])
        except Exception:
            continue
        if not rows or len(rows) < 2:
            continue
        for original, ts, _status, _mime in (row[:4] for row in rows[1:]):
            if not looks_like_permalink(original, author):
                continue
            if ts >= "20120101":          # belt and braces; the API already filtered
                continue
            key = norm_url(original)
            if key not in found or ts < found[key][1]:
                found[key] = (original, ts)
    out = sorted(found.values(), key=lambda x: x[1])
    return out


def dewrap(text):
    """Rejoin paragraphs that were hard-wrapped in the source.

    Only where the shape says so: three or more lines of roughly typewriter
    width that mostly do not end in sentence punctuation. Short lines are left
    alone, so verse, addresses and lists survive intact.
    """
    out = []
    for para in text.split("\n\n"):
        lines = [l for l in para.split("\n") if l.strip()]
        if len(lines) < 3 or any(re.match(r"^[-•*\d]", l.strip()) for l in lines):
            out.append(para)
            continue
        body = lines[:-1]
        widths = sorted(len(l) for l in body)
        wrapped = sum(1 for l in body if not re.search(r'[.!?:;"”\')]$', l.strip()))
        # median, not mean: a one-line dateline above the paragraph should not
        # drag the average below the threshold and leave the wrapping in place
        width = widths[len(widths) // 2]
        if 36 <= width <= 100 and wrapped >= 0.6 * len(body):
            out.append(" ".join(l.strip() for l in lines))
        else:
            out.append(para)
    return "\n\n".join(out)


def tidy(text):
    lines = [l.rstrip() for l in text.split("\n")]
    kept, cut = [], False
    for line in lines:
        s = line.strip().strip("|").strip()
        bare = re.sub(r"^[-•*]\s*", "", s)
        if CUT_AT.match(bare):
            cut = True
            break
        if not s:
            kept.append("")
            continue
        if LINE_JUNK.match(bare):
            continue
        if NAV_LINE.search(bare) and len(bare) < 120:
            continue
        if len(bare) <= 2:
            continue
        kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # drop nav-ish opening fragments: short, unpunctuated leading lines
    parts = text.split("\n\n")
    while parts and len(parts[0]) < 30 and not re.search(r"[.!?:\"']$", parts[0].strip()):
        parts.pop(0)
    parts = trim_tail(parts)
    return dewrap("\n\n".join(parts).strip()), cut


def clean_title(title, author_name):
    """Strip the site furniture publishers append, and the odd doubled title."""
    t = re.sub(r"\s+", " ", title or "").strip()
    # "Post Title - Brian SolisPost Title - Brian Solis" from stacked <title>s
    if len(t) > 24:
        head = t[:20]
        again = t.find(head, 1)
        if again > 0:
            t = t[:again]
    for sep in ("|", " - ", " – ", " — ", " :: ", " » "):
        if sep in t:
            head, tail = t.rsplit(sep, 1)
            if head.strip() and (author_name.lower() in tail.lower() or len(tail) < 32):
                t = head
    # "CodeCon Wrapup (Aaron Swartz: The Weblog)" — the blog's name, not the post's
    m = re.match(r"^(.{6,}?)\s*\(([^()]{3,60})\)\s*$", t)
    if m and (author_name.lower() in m.group(2).lower()
              or re.search(r"\b(blog|weblog|journal|com|net|org)\b", m.group(2), re.I)):
        t = m.group(1)
    return t.strip(" -|–—:»").strip()


def resolve_date(url, html, text, capture_ts):
    cap = C.ts_to_date(capture_ts)
    for cand, basis in ((C.date_from_url(url), "permalink"),
                        (C.date_from_html(html), "page metadata"),
                        (C.date_from_text(text), "dateline")):
        if cand and cand <= cap:            # publication cannot postdate its own capture
            return cand, basis
    return cap, "capture ceiling"


def live_url(original):
    """The present-day address of an archived URL."""
    p = urllib.parse.urlsplit(original)
    host = re.sub(r":(?:80|443)$", "", p.netloc)
    return urllib.parse.urlunsplit(("http", host, p.path, p.query, ""))


# Hosts that have refused to connect repeatedly. One timeout is a hiccup and
# must not condemn a whole domain; several in a row means the site is gone.
DEAD_HOSTS = {}
DEAD_AFTER = 4
_dead_lock = threading.Lock()

# Text hashes across every author, so one platform's "blog not found" page
# cannot be filed nine times under nine different names.
_seen_globally = {}
_seen_lock = threading.Lock()


def looks_later_than(text, pub):
    """True if the prose mentions a year it could not have known about.

    Modern page furniture — a 2025 copyright line, a sidebar of recent posts —
    is the giveaway that a permalink now serves something other than the post
    we went looking for. A year or so beyond publication is ordinary
    speculation and allowed; a decade is not.
    """
    year = int(pub[:4])
    for y in re.findall(r"\b(20[0-3]\d)\b", text):
        if int(y) > max(year + 1, 2012):
            return int(y)
    return None


def get_document(original, ts, min_chars, live_only=False):
    """Prefer today's clean HTML, but only when it carries its own pre-2012 date.

    The Wayback capture is the fallback and the backstop: it is throttled and
    its markup is messier, but a pre-2012 capture cannot contain post-2012 text.
    """
    live = live_url(original)
    host = urllib.parse.urlsplit(live).netloc.lower()
    # A live site answers quickly or not at all. Half these domains lapsed years
    # ago, and waiting out their DNS timeouts once per URL costs hours.
    with _dead_lock:
        skip_live = DEAD_HOSTS.get(host, 0) >= DEAD_AFTER
    r = {"status": 0, "body": ""} if skip_live else C.fetch(live, timeout=10, retries=1)
    if not skip_live:
        with _dead_lock:
            if r["status"] == 0:
                DEAD_HOSTS[host] = DEAD_HOSTS.get(host, 0) + 1
            else:
                DEAD_HOSTS[host] = 0        # it answered; the domain is fine
    if r["status"] == 200 and len(r["body"]) > 500:
        # Redirects to a new domain are fine and common — seomoz.org became
        # moz.com, and the post came along. The date test below is what guards
        # against landing on a parked domain or a soft 404.
        title, text = C.extract_text(r["body"])
        text, _ = tidy(text)
        if len(text) >= min_chars:
            pub, basis = resolve_date(original, r["body"], text, ts)
            claimed = C.date_from_url(original) or C.date_from_html(r["body"])
            if claimed and claimed >= C.CUTOFF:
                # the page says it is newer than the cutoff: not the post we
                # discovered, or it has been republished. Leave it.
                return None if live_only else _from_archive(original, ts)
            # A live page must carry its own pre-2012 date. Undated ones are
            # how modern replacements get in: a dead permalink quietly serving
            # today's author-bio page still looks like a 200 with prose on it.
            if basis != "capture ceiling" and pub < C.CUTOFF:
                return title, text, pub, basis, "live site"

    return None if live_only else _from_archive(original, ts)


def _from_archive(original, ts):
    r = C.fetch(C.wayback_url(ts, original), timeout=45, retries=2)
    if r["status"] != 200 or len(r["body"]) < 500:
        return None
    title, text = C.extract_text(r["body"])
    text, _ = tidy(text)
    pub, basis = resolve_date(original, r["body"], text, ts)
    return title, text, pub, basis, "wayback capture"


def harvest(author, target, candidates, log, live_only=False, per_author_budget=420):
    slug = author["slug"]
    outdir = os.path.join(TEXTS, slug)
    os.makedirs(outdir, exist_ok=True)
    existing = [f for f in os.listdir(outdir) if f.endswith(".txt")]
    if len(existing) >= target:
        log("%-24s already has %d" % (slug, len(existing)))
        return []
    target = target - len(existing)      # runs are resumable; only fetch the shortfall

    perms = discover(author)
    log("%-24s %d candidate permalinks" % (slug, len(perms)))
    if not perms:
        return []

    # spread the picks across the years rather than taking the oldest block
    if len(perms) > candidates:
        step = len(perms) / float(candidates)
        perms = [perms[int(i * step)] for i in range(candidates)]

    min_chars = author.get("min_chars", 1200)
    docs, seen = [], set()
    why = {"fetch": 0, "short": 0, "date": 0, "dupe": 0, "have": 0}
    t_start = time.time()
    for original, ts in perms:
        if len(docs) >= target:
            break
        if time.time() - t_start > per_author_budget:
            log("%-24s out of time, moving on" % slug)
            break
        got = get_document(original, ts, min_chars, live_only)
        if got is None:
            why["fetch"] += 1
            continue
        title, text, pub, how, via = got
        words = len(text.split())
        if len(text) < min_chars or words < max(120, min_chars // 9):
            why["short"] += 1
            continue
        if pub >= C.CUTOFF:
            why["date"] += 1
            continue
        if looks_later_than(text, pub):
            why["anachronism"] = why.get("anachronism", 0) + 1
            continue
        h = hashlib.sha1(re.sub(r"\W+", "", text[:600]).lower().encode()).hexdigest()
        if h in seen:
            why["dupe"] += 1
            continue
        with _seen_lock:                  # the same page under another author
            if h in _seen_globally:
                why["dupe"] += 1
                continue
            _seen_globally[h] = slug
        seen.add(h)
        title = clean_title(title, author["name"]) or C.slugify(original)
        fname = "%s--%s.txt" % (pub, C.slugify(title or "untitled", 55))
        if os.path.exists(os.path.join(outdir, fname)):
            why["have"] += 1              # already collected on an earlier pass
            continue
        docs.append(dict(
            fname=fname,
            author=author["name"], slug=slug, area=author["area"],
            type=author.get("type", "blog post"), title=title[:120],
            date=pub, date_basis=how, retrieved_from=via,
            # the archived URL keeps its :80 so the capture stays addressable;
            # the citation should not
            source_url=re.sub(r"(://[^/]+?):(?:80|443)(?=/|$)", r"\1", original),
            archived_url=C.wayback_url(ts, original), capture=C.ts_to_date(ts),
            words=words, text=text))

    for d in docs:
        path = os.path.join(outdir, d.pop("fname"))
        head = ["---"]
        for k in ("author", "title", "date", "date_basis", "type", "area",
                  "source_url", "archived_url", "retrieved_from", "words"):
            head.append("%s: %s" % (k, d[k]))
        head.append("retrieved: %s" % RETRIEVED)
        head.append("---")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(head) + "\n\n" + d["text"] + "\n")
        d["path"] = os.path.relpath(path, C.ROOT)
        del d["text"]
    log("%-24s kept %d  (rejected: %s)" % (
        slug, len(docs), ", ".join("%s=%d" % kv for kv in why.items() if kv[1])) or "none")
    return docs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=6)
    ap.add_argument("--candidates", type=int, default=16)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default=None, help="comma-separated slugs")
    ap.add_argument("--budget", type=int, default=420,
                    help="seconds to spend on one author before moving on")
    ap.add_argument("--live-only", action="store_true",
                    help="skip the archive fallback; the replay endpoint rate-limits "
                         "to roughly one request at a time, so a bulk run is better "
                         "served by the live web")
    ap.add_argument("--discover-only", action="store_true",
                    help="warm the permalink cache and stop; heavy CDX use makes "
                         "the archive throttle replay requests, so the two phases "
                         "are better run apart")
    args = ap.parse_args()

    authors = AUTHORS
    if args.only:
        want = set(args.only.split(","))
        authors = [a for a in AUTHORS if a["slug"] in want]

    os.makedirs(TEXTS, exist_ok=True)
    logfile = open(os.path.join(C.ROOT, "build.log"), "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logfile.write(msg + "\n")
        logfile.flush()

    log("=== run %s: %d authors, target %d ===" % (RETRIEVED, len(authors), args.target))

    if args.discover_only:
        for a in authors:
            try:
                log("%-24s %d permalinks" % (a["slug"], len(discover(a))))
            except Exception as e:
                log("%-24s discovery FAILED %s" % (a["slug"], type(e).__name__))
        return

    all_docs = []
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(harvest, a, args.target, args.candidates, log, args.live_only, args.budget): a for a in authors}
        for fut in cf.as_completed(futs):
            a = futs[fut]
            try:
                all_docs.extend(fut.result())
            except Exception as e:
                log("%-24s FAILED %s: %s" % (a["slug"], type(e).__name__, e))

    mpath = os.path.join(C.ROOT, "manifest.json")
    old = []
    if os.path.exists(mpath):
        with open(mpath, encoding="utf-8") as fh:
            old = json.load(fh).get("documents", [])
    by_path = {d["path"]: d for d in old}
    for d in all_docs:
        by_path[d["path"]] = d
    docs = sorted(by_path.values(), key=lambda d: (d["slug"], d["date"]))
    with open(mpath, "w", encoding="utf-8") as fh:
        json.dump({"generated": RETRIEVED, "cutoff": C.CUTOFF,
                   "documents": docs}, fh, indent=1)
    log("manifest: %d documents, %d authors" %
        (len(docs), len({d["slug"] for d in docs})))


if __name__ == "__main__":
    main()
