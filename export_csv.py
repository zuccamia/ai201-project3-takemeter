#!/usr/bin/env python3
"""
export_csv.py — Export the labeled JSONL into the single CSV the notebook expects.

Columns: text, label, notes
- Keeps ONLY rows whose label is one of the real classes (LABELS below).
- Drops blank/skipped rows and anything outside the taxonomy, so the notebook
  never sees a phantom extra class.
- Writes one complete file; does NOT pre-split. The notebook owns the
  70/15/15 train/val/test split.

Uses the csv module (not manual joining): HN text is full of commas, quotes,
and newlines, which csv quotes correctly and a hand-rolled join would mangle.

Usage:
  python export_csv.py                         # data/hn_dataset.jsonl -> data/labeled.csv
  python export_csv.py data/hn_dataset.jsonl data/labeled.csv
"""

import csv
import json
import os
import sys
from collections import Counter

# Must match the taxonomy in hn_label.py. Anything not in here is dropped.
LABELS = ["analysis", "anecdote", "explanation", "hot_take"]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/hn_dataset.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/labeled.csv"

    if not os.path.exists(src):
        sys.exit(f"file not found: {src}")

    valid = set(LABELS)
    kept, dropped = [], 0
    seen_labels = Counter()

    with open(src, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            label = (r.get("label") or "").strip()
            text = (r.get("text") or "").strip()
            seen_labels[label or "<blank>"] += 1
            if label in valid and text:
                kept.append({"text": text, "label": label, "notes": (r.get("notes") or "").strip()})
            else:
                dropped += 1

    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["text", "label", "notes"], quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(kept)

    print(f"Wrote {len(kept)} rows -> {dst}", file=sys.stderr)
    print(f"  kept by label: {dict(Counter(r['label'] for r in kept))}", file=sys.stderr)
    print(f"  dropped (blank/skipped/out-of-taxonomy): {dropped}", file=sys.stderr)
    if seen_labels:
        print(f"  all labels seen in source: {dict(seen_labels)}", file=sys.stderr)

    # 70/15/15 needs enough per class to populate val+test (15% each).
    counts = Counter(r["label"] for r in kept)
    thin = [lab for lab in LABELS if counts.get(lab, 0) < 7]
    if thin:
        print(f"  WARNING: thin classes (<7 rows) may vanish from val/test "
              f"after the split: {thin}", file=sys.stderr)


if __name__ == "__main__":
    main()

