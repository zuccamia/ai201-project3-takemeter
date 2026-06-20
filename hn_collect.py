#!/usr/bin/env python3
"""
hn_collect.py — Build a Hacker News dataset for rhetorical-style labeling.

Pulls posts/comments from the public Algolia HN Search API (no API key
required) and writes a JSONL file with a blank `label` field to fill in.

Target taxonomy (will be labeled by hand after collecting):
  analysis     — claim backed by specific, checkable evidence (data, mechanism,
                 sources, historical comparison). Test: a skeptic could verify it.
  anecdote     — point backed by the author's own firsthand experience.
                 Test: evidence is personal/unverifiable ("when I was at...").
  explanation  — neutral how/why exposition; teaching, not arguing a position.
                 Test: it informs without taking a contestable stance.
  hot_take     — confident claim asserted with no support. Test: you couldn't
                 fact-check it from the post alone.

Why HN works for this: comments carry the analysis/hot_take signal, while
Ask/Show HN posts give you self-text with real argumentation. The script
mixes both so label classes aren't correlated with post type.

Usage:
  python hn_collect.py                         # fresh: COUNT rows, recent/general
  python hn_collect.py --query "database"      # fresh, topic-filtered
  python hn_collect.py --query "database" --add 80   # append 80 NEW rows, keep labels

All other settings (count, mix ratio, length bounds, etc.) are constants
near the top of this file.

Zero dependencies — standard library only. Python 3.8+.
"""

import argparse
import html
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ALGOLIA = "https://hn.algolia.com/api/v1"
USER_AGENT = "hn-collect/1.0 (research dataset; rate-limited; contact: you@example.com)"

# Collection settings
COUNT = 200             # total rows to collect
COMMENT_RATIO = 0.6     # fraction that are comments; rest split Ask/Show
MIN_CHARS = 200         # drop text shorter than this
MAX_CHARS = 2000        # drop text longer than this
MIN_STORY_POINTS = 20   # min points for Ask/Show HN posts
DELAY = 0.5             # seconds between paged requests
SEED = 42               # shuffle seed (interleaves types for unbiased labeling)
OUT = "data/hn_dataset.jsonl"

_TAG = re.compile(r"<[^>]+>")
_MULTINL = re.compile(r"\n{3,}")
_SPACES = re.compile(r"[ \t]+")


def clean_text(raw):
    """HN text comes as HTML-ish markup; turn it into plain text."""
    if not raw:
        return ""
    t = raw.replace("</p>", "\n\n").replace("<p>", "\n\n")
    t = _TAG.sub("", t)
    t = html.unescape(t)
    t = _MULTINL.sub("\n\n", t)
    t = _SPACES.sub(" ", t)
    return t.strip()


def fetch(path, params, retries=3):
    url = ALGOLIA + path + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            if 400 <= e.code < 500:  # client error won't fix on retry
                raise RuntimeError(f"HTTP {e.code} for {url}\n{body}") from None
            last = f"HTTP {e.code}: {body}"
        except Exception as e:  # transient (network/timeout) — retry with backoff
            last = e
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {retries} tries: {url}\n{last}")


def hits(tags, query, numeric_filters, by_date, delay, page_size=100, max_pages=20):
    """Yield raw hits across pages for a given tag set."""
    path = "/search_by_date" if by_date else "/search"
    page = 0
    while page < max_pages:
        params = {"tags": tags, "hitsPerPage": page_size, "page": page}
        if query:
            params["query"] = query
        if numeric_filters:
            params["numericFilters"] = numeric_filters
        data = fetch(path, params)
        page_hits = data.get("hits", [])
        if not page_hits:
            return
        for h in page_hits:
            yield h
        nb_pages = data.get("nbPages", page + 1)
        page += 1
        if page >= nb_pages:
            return
        time.sleep(delay)


def to_record(hit, type_label):
    text = clean_text(hit.get("comment_text") or hit.get("story_text") or "")
    return {
        "id": hit.get("objectID"),
        "type": type_label,
        "author": hit.get("author"),
        "text": text,
        "label": "",   # <- fill with the taxonomy
        "notes": "",   # <- optional note for difficult cases
    }


def collect(source_iter, type_label, need, seen, min_chars, max_chars):
    out = []
    for h in source_iter:
        oid = h.get("objectID")
        if not oid or oid in seen:
            continue
        rec = to_record(h, type_label)
        if not (min_chars <= len(rec["text"]) <= max_chars):
            continue
        seen.add(oid)
        out.append(rec)
        if len(out) >= need:
            break
    return out


def collect_batch(query, target, seen):
    """Collect up to `target` NEW unique records (ids not already in `seen`),
    applying the comment/Ask/Show type mix. Mutates `seen`."""
    n_comments = round(target * COMMENT_RATIO)
    n_stories = target - n_comments
    n_ask = n_stories // 2
    n_show = n_stories - n_ask

    pts = f"points>{MIN_STORY_POINTS - 1}"  # HN API rejects '>='; '>N-1' == '>=N'
    records = []

    print(f"Collecting comments (target {n_comments})...", file=sys.stderr)
    # No comment score on HN, so use recency + length to control quality.
    records += collect(
        hits("comment", query, None, by_date=True, delay=DELAY),
        "comment", n_comments, seen, MIN_CHARS, MAX_CHARS,
    )

    print(f"Collecting Ask HN posts (target {n_ask})...", file=sys.stderr)
    # search_by_date (not /search): /search rejects numericFilters without a query.
    records += collect(
        hits("ask_hn", query, pts, by_date=True, delay=DELAY),
        "ask_hn", n_ask, seen, MIN_CHARS, MAX_CHARS,
    )

    print(f"Collecting Show HN posts (target {n_show})...", file=sys.stderr)
    records += collect(
        hits("show_hn", query, pts, by_date=True, delay=DELAY),
        "show_hn", n_show, seen, MIN_CHARS, MAX_CHARS,
    )

    # Backfill from comments if Ask/Show ran short (e.g. narrow query).
    if len(records) < target:
        need = target - len(records)
        print(f"Backfilling {need} from comments...", file=sys.stderr)
        records += collect(
            hits("comment", query, None, by_date=True, delay=DELAY),
            "comment", need, seen, MIN_CHARS, MAX_CHARS,
        )

    # Interleave types to avoid labeling long runs of one kind (reduces anchoring).
    random.Random(SEED).shuffle(records)
    return records[:target]


def main():
    ap = argparse.ArgumentParser(description="Collect a Hacker News dataset for labeling.")
    ap.add_argument("--query", default="", help="optional topic filter (e.g. 'database'); empty = recent/general")
    ap.add_argument("--add", type=int, default=0, metavar="N",
                    help="append N NEW unique rows to the existing file, preserving "
                         "already-labeled rows (default 0 = fresh collection of COUNT rows)")
    args = ap.parse_args()

    existing = []
    seen = set()
    if args.add > 0:
        if not os.path.exists(OUT):
            sys.exit(f"--add needs an existing file at {OUT}; run a fresh collection first.")
        with open(OUT, encoding="utf-8") as f:
            existing = [json.loads(line) for line in f if line.strip()]
        seen = {r.get("id") for r in existing}
        print(f"Append mode: {len(existing)} existing rows; fetching up to {args.add} new "
              f"(dedup against existing)...", file=sys.stderr)
        target = args.add
    else:
        target = COUNT

    batch = collect_batch(args.query, target, seen)
    records = existing + batch  # existing rows + their labels are written back unchanged

    # Atomic write: never leave a half-written file if this is appending to labeled data.
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, OUT)

    by_type = {}
    for r in batch:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    print(f"\nWrote {len(batch)} new rows ({len(records)} total) -> {OUT}", file=sys.stderr)
    print(f"New batch by type: {by_type}", file=sys.stderr)
    if len(batch) < target:
        print(f"NOTE: short of target ({len(batch)}/{target} new). "
              f"Query pool may be thin — broaden --query or loosen the constants at the top.",
              file=sys.stderr)


if __name__ == "__main__":
    main()

