#!/usr/bin/env python3
"""
hn_label.py — Single-keypress terminal labeler for the HN dataset.

Reads a JSONL file (default: data/hn_dataset.jsonl), shows one post at a time,
and writes your label back into the `label` field. Resumable: it skips rows
that already have a label, so you can quit and continue any time.

Keys:
  1..N   apply a label (mapped to LABELS below)
  n      add/edit a note on the current row (for difficult cases)
  s      first pass: skip/discard (left blank, dropped on export).
         review mode: keep current label, move on.
  u      undo — restores the previous label (blank in first pass)
  h / ?  show this help
  q      save and quit  (also Ctrl-C saves)

Progress is saved to disk after every decision via an atomic write, so a
crash never loses work.

Usage:
  python hn_label.py                      # label unlabeled rows in data/hn_dataset.jsonl
  python hn_label.py posts.jsonl          # label a different file
  python hn_label.py --review             # revisit ALL labeled rows to re-annotate
  python hn_label.py --review explanation # revisit only rows labeled 'explanation'
"""

import argparse
import json
import os
import sys
import textwrap

# Edit this list if your taxonomy changes — keys 1..N are assigned in order.
LABELS = ["analysis", "anecdote", "explanation", "hot_take"]

WRAP = 88


# ---- single-keypress input (portable, with non-tty fallback) ---------------
def make_getch():
    if not sys.stdin.isatty():
        return lambda: (sys.stdin.readline().strip()[:1] or "\n")
    try:
        import termios
        import tty

        def getch():
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch

        return getch
    except ImportError:
        import msvcrt

        return lambda: msvcrt.getwch()


getch = make_getch()


# ---- io --------------------------------------------------------------------
def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)  # atomic on the same filesystem


# ---- display ---------------------------------------------------------------
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def fmt_counts(rows):
    counts = {lab: 0 for lab in LABELS}
    unlabeled = 0
    for r in rows:
        lab = r.get("label", "")
        if lab in counts:
            counts[lab] += 1
        elif lab == "":
            unlabeled += 1
    parts = [f"{lab}:{counts[lab]}" for lab in LABELS]
    return "  ".join(parts), unlabeled


def help_text(review=False):
    keymap = "   ".join(f"[{i+1}] {lab}" for i, lab in enumerate(LABELS))
    action = ("[s] keep current, next" if review
              else "[s] skip (discard — left blank, dropped on export)")
    return (f"{keymap}\n"
            f"[n] add note   {action}   [u] undo   [h] help   [q] save & quit")


def show(rows, idx, progress, review=False):
    clear()
    dist, _ = fmt_counts(rows)
    r = rows[idx]
    print(f"  {progress}        {dist}")
    print("  " + "-" * (WRAP - 2))
    text = r.get("text") or ""
    meta = f"  type={r.get('type')}  author={r.get('author')}  len={len(text)}"
    if review:
        meta += f"  CURRENT LABEL: {r.get('label') or '(blank)'}"
    print(meta)
    print(f"  https://news.ycombinator.com/item?id={r.get('id')}")
    note = r.get("notes") or ""
    if note:
        print(f"  note: {note}")
    print("  " + "-" * (WRAP - 2))
    print()
    for para in text.split("\n"):
        for line in textwrap.wrap(para, width=WRAP) or [""]:
            print("  " + line)
    print()
    print("  " + "-" * (WRAP - 2))
    print("  " + help_text(review).replace("\n", "\n  "))


# ---- main loop -------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Label / review the HN dataset.")
    ap.add_argument("path", nargs="?", default="data/hn_dataset.jsonl",
                    help="JSONL file to label (default: data/hn_dataset.jsonl)")
    ap.add_argument("--review", nargs="?", const="__ALL__", default=None, metavar="LABEL",
                    help="review already-labeled rows and re-annotate. "
                         "Bare --review reviews all labeled rows; --review LABEL reviews only that class.")
    args = ap.parse_args()

    path = args.path
    if not os.path.exists(path):
        sys.exit(f"file not found: {path}")

    rows = load(path)
    total = len(rows)
    keymap = {str(i + 1): lab for i, lab in enumerate(LABELS)}
    review = args.review is not None

    if review:
        if args.review == "__ALL__":
            queue = [i for i, r in enumerate(rows) if r.get("label")]
            scope = "all labeled"
        else:
            if args.review not in keymap.values():
                sys.exit(f"--review label must be one of {LABELS}, got {args.review!r}")
            queue = [i for i, r in enumerate(rows) if r.get("label") == args.review]
            scope = args.review
        if not queue:
            print(f"No rows to review (scope: {scope}).")
            return
    else:
        queue = [i for i, r in enumerate(rows) if not r.get("label")]
        if not queue:
            dist, _ = fmt_counts(rows)
            print(f"All {total} rows already labeled.\n  {dist}\n"
                  f"Use --review (or --review LABEL) to revisit and re-annotate.")
            return

    history = []  # stack of (idx, previous_label) for undo
    qpos = 0

    try:
        while qpos < len(queue):
            idx = queue[qpos]
            if review:
                progress = f"review {qpos + 1}/{len(queue)} [{scope}]"
            else:
                done = total - sum(1 for r in rows if not r.get("label"))
                progress = f"labeled {done}/{total}"
            show(rows, idx, progress, review)

            ch = getch().lower()

            if ch in ("q", "\x03"):  # q or Ctrl-C
                break
            elif ch in ("h", "?"):
                input("\n  " + help_text(review).replace("\n", "\n  ") + "\n  [enter] back ")
                continue
            elif ch == "n":
                # terminal is in cooked mode between getch() calls, so input() works
                note = input("\n  note> ").strip()
                rows[idx]["notes"] = note
                save(path, rows)
                continue  # don't advance — apply a label next
            elif ch == "s":
                qpos += 1  # first-pass: leave blank; review: keep current label
                continue
            elif ch == "u":
                if history:
                    prev_idx, prev_label = history.pop()
                    rows[prev_idx]["label"] = prev_label  # restore prior value, not blank
                    save(path, rows)
                    if prev_idx in queue:
                        qpos = queue.index(prev_idx)
                    else:
                        queue.insert(qpos, prev_idx)
                continue
            elif ch in keymap:
                history.append((idx, rows[idx].get("label", "")))  # remember prior label
                rows[idx]["label"] = keymap[ch]
                save(path, rows)
                qpos += 1
            else:
                continue  # ignore unknown keys
    except KeyboardInterrupt:
        pass
    finally:
        save(path, rows)

    clear()
    dist, unlabeled = fmt_counts(rows)
    print(f"Saved {path}")
    print(f"  {dist}")
    if not review:
        print(f"  unlabeled remaining: {unlabeled}")
        if unlabeled:
            print("  (run again to continue where you left off)")


if __name__ == "__main__":
    main()

