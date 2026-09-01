"""Shared plumbing for the pre-2012 corpus: caching fetcher, HTML-to-text, date extraction.

Standard library only, matching the rest of this repo.
"""

import gzip
import hashlib
import io
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")

CUTOFF = "2012-01-01"          # nothing published on or after this date
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


# --------------------------------------------------------------------------- fetch


def _cache_path(key):
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    d = os.path.join(CACHE, h[:2])
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, h + ".gz")


def cache_get(key):
    p = _cache_path(key)
    if not os.path.exists(p):
        return None
    try:
        with gzip.open(p, "rb") as fh:
            return json.loads(fh.read().decode("utf-8"))
    except Exception:
        return None


def cache_put(key, obj):
    p = _cache_path(key)
    tmp = p + ".tmp"
    with gzip.open(tmp, "wb") as fh:
        fh.write(json.dumps(obj).encode("utf-8"))
    os.replace(tmp, p)


def _decode(raw, ctype):
    enc = None
    m = re.search(r"charset=([\w-]+)", ctype or "", re.I)
    if m:
        enc = m.group(1)
    if not enc:
        m = re.search(rb'charset=["\']?([\w-]+)', raw[:4096], re.I)
        if m:
            enc = m.group(1).decode("ascii", "ignore")
    for cand in [enc, "utf-8", "cp1252", "latin-1"]:
        if not cand:
            continue
        try:
            return raw.decode(cand)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "replace")


_throttle_lock = threading.Lock()
_last_hit = [0.0]
_interval = [1.5]      # adapts to how hard Wayback is pushing back
MIN_INTERVAL, MAX_INTERVAL = 1.2, 8.0


def _wait_turn(url):
    """Wayback answers 503 when annoyed, and stays annoyed. Go at its pace."""
    if "archive.org" not in url:
        return
    with _throttle_lock:
        gap = time.time() - _last_hit[0]
        if gap < _interval[0]:
            time.sleep(_interval[0] - gap)
        _last_hit[0] = time.time()


def _back_off():
    with _throttle_lock:
        _interval[0] = min(MAX_INTERVAL, _interval[0] + 0.6)


def _ease_up():
    with _throttle_lock:
        _interval[0] = max(MIN_INTERVAL, _interval[0] - 0.03)


def fetch(url, timeout=60, retries=5, use_cache=True, pause=0.0):
    """Return {'status': int, 'url': str, 'body': str} and cache it (failures included, briefly)."""
    if use_cache:
        hit = cache_get(url)
        if hit is not None:
            return hit
    last = {"status": 0, "url": url, "body": "", "error": "unattempted"}
    for attempt in range(retries):
        try:
            _wait_turn(url)
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip",
                "Accept-Language": "en-US,en;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    try:
                        raw = gzip.decompress(raw)
                    except Exception:
                        pass
                out = {
                    "status": resp.status,
                    "url": resp.geturl(),
                    "body": _decode(raw, resp.headers.get("Content-Type", "")),
                }
                if use_cache:
                    cache_put(url, out)
                _ease_up()
                if pause:
                    time.sleep(pause)
                return out
        except urllib.error.HTTPError as e:
            last = {"status": e.code, "url": url, "body": "", "error": "http %s" % e.code}
            if e.code in (404, 403, 410):
                break
            retry_after = 0
            try:
                retry_after = int(e.headers.get("Retry-After", 0))
            except (TypeError, ValueError):
                pass
            if e.code in (429, 503, 502, 504):
                _back_off()
                time.sleep(max(retry_after, 12 * (attempt + 1)))
            else:
                time.sleep(max(retry_after, 4 * (attempt + 1)))
        except Exception as e:  # timeouts, resets, DNS
            last = {"status": 0, "url": url, "body": "", "error": type(e).__name__}
            time.sleep(3 * (attempt + 1))
    if use_cache and last["status"] in (404, 403, 410):
        cache_put(url, last)
    return last


def wayback_url(timestamp, original):
    """Raw archived bytes, without the Wayback navigation chrome."""
    return "https://web.archive.org/web/%sid_/%s" % (timestamp, original)


# --------------------------------------------------------------------------- DOM


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}
DROP = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form",
        "iframe", "svg", "select", "button", "textarea", "object", "applet", "map"}
BLOCK = {"p", "div", "section", "article", "ul", "ol", "li", "blockquote", "pre",
         "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "td", "dl", "dt", "dd",
         "figure", "figcaption", "hr", "br", "address", "center"}
TEXT_BLOCKS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre",
               "dd", "dt", "figcaption", "td", "address"}

# Matched against whole class/id tokens, never as substrings. WordPress stamps
# posts with "category-foo" and "tag-bar", and a substring match on "categor"
# throws the article away with the furniture.
JUNK_TOKEN = re.compile(
    r"^(?:comments?|commentlist|comment-\w+|respond|sidebar|secondary|footer|"
    r"header|masthead|nav|navigation|menu|share|sharing|sharedaddy|social|"
    r"related|related-\w+|widget|widget-\w+|promo|subscribe|newsletter|disqus|"
    r"trackbacks?|breadcrumbs?|pagination|pager|author-bio|byline|postmeta|"
    r"entry-meta|post-meta|tagcloud|banner|advert(?:isement)?|ads?|sponsor|"
    r"popular|recent|recent-\w+|blogroll|search|searchform|skip|toolbar|"
    r"wm-ipp\w*|donato\w*|jetpack-\w+|sd-content|sharedaddy\w*|jp-\w+)$",
    re.I)

# Tokens that mark the real article, and outrank anything above.
CONTENT_TOKEN = re.compile(
    r"^(?:post|posts|entry|hentry|article|content|main|maincontent|story|"
    r"storycontent|body|blogpost|post-body|entry-content|entry-body|"
    r"post-content|postcontent|articlebody|text)(?:-\w+)?$", re.I)


def _tokens(ident):
    return [t for t in re.split(r"[\s_]+", ident.strip()) if t]


def is_junk(node):
    toks = _tokens(node.attrs.get("class", "") + " " + node.attrs.get("id", ""))
    if not toks:
        return False
    if any(CONTENT_TOKEN.match(t) for t in toks):
        return False
    return any(JUNK_TOKEN.match(t) for t in toks)


class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = parent
        self.text = ""

    def ident(self):
        return "%s %s" % (self.attrs.get("class", ""), self.attrs.get("id", ""))


class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.cur = self.root
        self.metas = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            self.metas.append(a)
            return
        if tag == "title":
            self._in_title = True
            return
        if tag in VOID:
            if tag == "br":
                self.cur.children.append(Node("br", a, self.cur))
            return
        # implicit closes for the sloppy markup of 2004-2011 blogs
        if tag in BLOCK:
            while self.cur.tag == "p":
                self.cur = self.cur.parent or self.root
        if tag == "li":
            while self.cur.tag == "li":
                self.cur = self.cur.parent or self.root
        if tag in ("td", "tr", "dd", "dt"):
            while self.cur.tag in ("td", "dd", "dt") or (tag == "tr" and self.cur.tag == "tr"):
                self.cur = self.cur.parent or self.root
        node = Node(tag, a, self.cur)
        self.cur.children.append(node)
        self.cur = node

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
            return
        if tag in VOID or tag == "meta":
            return
        n = self.cur
        depth = 0
        while n is not None and n.tag != tag and depth < 60:
            n = n.parent
            depth += 1
        if n is not None and n.tag == tag:
            self.cur = n.parent or self.root

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if not data.strip():
            # Always keep one space. Dropping whitespace that follows a text
            # node fuses words across inline tags — "been</a>writing" becomes
            # "beenwriting" — and runs of spaces are collapsed later anyway.
            data = " "
        t = Node("#text", parent=self.cur)
        t.text = data
        self.cur.children.append(t)


def parse(html):
    d = DOM()
    try:
        d.feed(html)
    except Exception:
        pass
    return d


# --------------------------------------------------------------------------- extraction


def node_text(node, keep_drop=False):
    out = []

    def walk(n):
        if n.tag == "#text":
            out.append(n.text)
            return
        if not keep_drop and n.tag in DROP:
            return
        if n.tag == "br":
            out.append("\n")
            return
        for c in n.children:
            walk(c)
        if n.tag in BLOCK:
            out.append("\n")

    walk(node)
    return re.sub(r"[ \t\xa0]+", " ", "".join(out))


def link_density(node):
    total = len(node_text(node))
    if total == 0:
        return 1.0
    links = 0
    stack = [node]
    while stack:
        n = stack.pop()
        if n.tag == "a":
            links += len(node_text(n))
            continue
        stack.extend(n.children)
    return links / total


def _score(node):
    """Weight of real prose beneath a node: long paragraphs count, link lists do not."""
    s = 0
    stack = [node]
    while stack:
        n = stack.pop()
        if n.tag in DROP:
            continue
        if n.tag in ("p", "blockquote", "pre"):
            t = node_text(n).strip()
            if len(t) >= 40 and link_density(n) < 0.5:
                s += len(t)
            continue
        stack.extend(n.children)
    return s


def _blocks(node):
    out = []

    def walk(n):
        if n.tag in DROP:
            return
        if n.tag != "#root" and n is not node and is_junk(n):
            return
        if n.tag in TEXT_BLOCKS:
            t = node_text(n).strip()
            # keep blank-line breaks: on table-and-<br> layouts they are the
            # only paragraph structure the page has
            t = re.sub(r"\n{3,}", "\n\n", t).strip()
            if t:
                prefix = "- " if n.tag == "li" else ""
                out.append(prefix + t)
            return
        for c in n.children:
            walk(c)

    walk(node)
    return out


CONTENT_HINT = re.compile(
    r"entry-?content|entry-?body|post-?body|post-?content|articlebody|article-?body|"
    r"blog-?post|entry-?text|storycontent|post-?text|maincontent|entrybody", re.I)


def extract_text(html):
    """Best-effort article text. Returns (title, text)."""
    d = parse(html)
    title = re.sub(r"\s+", " ", d.title).strip()

    # 1. an explicit content container, where the platform gave us one
    best, best_score = None, 0
    stack = [d.root]
    hinted = []
    while stack:
        n = stack.pop()
        if n.tag in DROP:
            continue
        if n.tag not in ("#text", "br") and CONTENT_HINT.search(n.ident()):
            hinted.append(n)
        stack.extend(n.children)
    for n in hinted:
        s = _score(n)
        if s > best_score:
            best, best_score = n, s

    # 2. otherwise the densest block of prose on the page. The bar is low on
    #    purpose: a hinted container beats a guess even for a 200-word post.
    if best_score < 120:
        stack = [d.root]
        while stack:
            n = stack.pop()
            if n.tag in DROP or n.tag in ("#text", "br"):
                continue
            if is_junk(n):
                continue
            s = _score(n)
            if s > best_score:
                best, best_score = n, s
            stack.extend(n.children)

    if best is None:
        best = d.root

    text = "\n\n".join(_blocks(best))
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return title, text.strip()


# --------------------------------------------------------------------------- dates


MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}
MONTHS.update({m[:3]: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])})
MONTH_RE = "|".join(sorted(MONTHS, key=len, reverse=True))


def _mk(y, m, d):
    try:
        y, m, d = int(y), int(m), int(d)
    except (TypeError, ValueError):
        return None
    if not (1994 <= y <= 2013 and 1 <= m <= 12 and 1 <= d <= 31):
        return None
    return "%04d-%02d-%02d" % (y, m, d)


def date_from_url(url):
    m = re.search(r"/((?:19|20)\d\d)/(\d\d)/(\d\d)(?:/|-|_)", url)
    if m:
        return _mk(*m.groups())
    # /2002/Aug/14/ — Simon Willison and other early hand-rolled blogs
    m = re.search(r"/((?:19|20)\d\d)/(%s)\w*/(\d{1,2})(?:/|$)" % MONTH_RE, url, re.I)
    if m:
        return _mk(m.group(1), MONTHS[m.group(2).lower()[:3]], m.group(3))
    # /alertbox/20000109.html — Nielsen dated his files
    m = re.search(r"/((?:19|20)\d\d)(\d\d)(\d\d)\.(?:html?|php|asp)$", url)
    if m:
        return _mk(*m.groups())
    m = re.search(r"/((?:19|20)\d\d)/(\d\d)/", url)
    if m:
        return _mk(m.group(1), m.group(2), 1)
    m = re.search(r"[?&](?:year|y)=((?:19|20)\d\d).*?[?&](?:month|m)=(\d{1,2})", url)
    if m:
        return _mk(m.group(1), m.group(2), 1)
    return None


META_DATE_KEYS = ("article:published_time", "datepublished", "date", "dc.date",
                  "dc.date.issued", "pubdate", "publish-date", "og:published_time",
                  "sailthru.date", "parsely-pub-date")


def date_from_html(html):
    d = parse(html)
    for meta in d.metas:
        key = (meta.get("property") or meta.get("name") or meta.get("itemprop") or "").lower()
        if key in META_DATE_KEYS:
            got = parse_datestring(meta.get("content", ""))
            if got:
                return got
    m = re.search(r'<time[^>]+datetime=["\']([^"\']+)', html, re.I)
    if m:
        got = parse_datestring(m.group(1))
        if got:
            return got
    # a visible date inside an element that announces itself as one
    for m in re.finditer(
            r'<[^>]+(?:class|id)=["\'][^"\']*(?:date|posted|published|timestamp|dateline)'
            r'[^"\']*["\'][^>]*>(.{0,200}?)<', html, re.I | re.S):
        got = parse_datestring(re.sub(r"<[^>]+>", " ", m.group(1)))
        if got:
            return got
    return None


def parse_datestring(s):
    if not s:
        return None
    s = s.strip()
    m = re.search(r"((?:19|20)\d\d)-(\d{1,2})-(\d{1,2})", s)
    if m:
        return _mk(*m.groups())
    m = re.search(r"(%s)\w*\.?,?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+((?:19|20)\d\d)" % MONTH_RE, s, re.I)
    if m:
        return _mk(m.group(3), MONTHS[m.group(1).lower()[:3]], m.group(2))
    m = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+(%s)\w*\.?,?\s+((?:19|20)\d\d)" % MONTH_RE, s, re.I)
    if m:
        return _mk(m.group(3), MONTHS[m.group(2).lower()[:3]], m.group(1))
    m = re.search(r"(%s)\w*\.?\s+((?:19|20)\d\d)" % MONTH_RE, s, re.I)
    if m:
        return _mk(m.group(2), MONTHS[m.group(1).lower()[:3]], 1)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/((?:19|20)\d\d)\b", s)
    if m:  # assume US ordering, which these sources overwhelmingly use
        return _mk(m.group(3), m.group(1), m.group(2))
    return None


def date_from_text(text):
    """A dateline in the opening lines, as Paul Graham and others write it."""
    head = text[:400]
    return parse_datestring(head)


def ts_to_date(ts):
    return "%s-%s-%s" % (ts[0:4], ts[4:6], ts[6:8])


def slugify(s, maxlen=60):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:maxlen].strip("-") or "untitled"
