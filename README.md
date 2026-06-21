# TakeMeter

A classifier that distinguishes how a Hacker News post argues its case — by **evidence** (`analysis`), **mechanism** (`explanation`), **personal experience** (`anecdote`), or **unsupported assertion** (`hot_take`). The labels turn on rhetorical structure, not topic or vocabulary, so a single-topic corpus (database posts) sharpens the learning signal for *how* people argue rather than *what* they argue about.

🔗 **Live demo:** [huggingface.co/spaces/zuccamia/takemeter](https://huggingface.co/spaces/zuccamia/takemeter) — paste any HN-style post and see the fine-tuned model's predicted label and confidence distribution across all four classes. First load takes ~30 seconds (Space wakes from sleep); subsequent calls are ~150 ms.

This README is the evaluation report. The planning document (`planning.md`) records label definitions, edge-case rules, and the design decisions made before any data was collected.

---

## 1. Community

**Hacker News** ([news.ycombinator.com](https://news.ycombinator.com/news)).

**Why this community:**
- High-volume, self-contained plain text — no images, embeds, or engagement-bait formatting. The signal lives entirely in the language.
- A vibrant technology community that produces both careful technical analysis and reflexive contrarianism, so each of the four labels is reasonably populated.
- HN's dry register makes faint praise, sarcasm, and dismissal lexically similar — a useful target for a reader-side filter that surfaces real discussion.
- A keyword or sentiment-lexicon baseline will struggle because the labels turn on rhetorical structure (basis of the claim), not vocabulary — justifying the use of a learned classifier.

---

## 2. Label Taxonomy

| Label | One-line gloss |
|---|---|
| `analysis` | Structured argument backed by specific, verifiable evidence (statistics, benchmarks, historical comparison, code). |
| `explanation` | Neutral, didactic account of how or why something works, aiming to clarify a concept or mechanism rather than argue a position. |
| `anecdote` | Claim grounded in the author's own first-hand experience, offering personal observation rather than generalizable evidence. |
| `hot_take` | Bold, confident opinion asserted without supporting evidence — states rather than argues its case. |

### `analysis`

A post is labeled `analysis` when its claim is backed by specific, verifiable evidence and reasons from that evidence toward a conclusion.

**Example 1.** *"It took 5 years from construction start to grid connection for Oskarshamn R3, at the time the reactor with the world's highest rated output. Since it began operating it has produced 350TWh. That nuclear power must take forever is a myth and is only due to dysfunctional politics."* — backs the myth-busting thesis with a specific reactor's timeline and lifetime output. [Source](https://news.ycombinator.com/item?id=48595449)

**Example 2.** *"Benchmarks vs SQLite WITHOUT ROWID (1M records, identical settings): Sequential writes +57%, Random reads +68%, Sequential scan +90%, Random updates +72%, Random deletes +104%..."* — full benchmark table with reproducible methodology; honest tradeoffs (LMDB beats on raw reads, RocksDB on writes) are called out alongside the wins. [Source](https://news.ycombinator.com/item?id=47136553)

### `explanation`

A post is labeled `explanation` when it neutrally describes how or why something works — clarifying a concept or mechanism without staking a position.

**Example 1.** *"They seem similar at a glance but they're quite different. You can think of SQLite as a transactional database while DuckDB is better used as an analytical database... SQLite is your metadata record, DuckDB is your ingestion/scanning/aggregating/joining engine."* — clarifies the distinction didactically, framing them as complementary. [Source](https://news.ycombinator.com/item?id=48595297)

**Example 2.** *"There are actually two types of stored query: regular and 'trusted'. Any query you save is a regular query. It operates under the permissions of the viewer... So there's a second category: 'trusted' queries..."* — walks the reader through the mechanism of two permission modes with no rhetorical stance. [Source](https://news.ycombinator.com/item?id=48600234)

### `anecdote`

A post is labeled `anecdote` when its claim rests on the author's own first-hand, single-instance experience rather than on aggregate or independently verifiable evidence.

**Example 1.** *"This morning, our database flagged a duplicate UUID (v4)... today the system inserted a new document with a fresh UUIDv4 and it came up with the exact same one... the database only has about 15,000 records, and now one collision. Statistically impossible. Has that ever happened to anyone?!"* — n=1 personal incident, not reproducible by readers. [Source](https://news.ycombinator.com/item?id=48060054)

**Example 2.** *"I discovered ClickHouse around 2017-18 and built a PoC to replace Elasticsearch: 5x better storage and qps, in a couple of weeks. Managers rejected it because it wasn't well known..."* — first-hand career story; numbers are real but unreproducible, and the basis of the claim is "what happened to me." [Source](https://news.ycombinator.com/item?id=48597041)

### `hot_take`

A post is labeled `hot_take` when it asserts a confident opinion without supporting evidence — stating rather than arguing its case.

**Example 1.** *"Writing to disk for every write is required, otherwise you're not durable. Sure it's faster to never write to disk, then you reboot and you've lost data. /dev/null is a webscale database that is even faster!"* — sarcastic, confident dismissal with no supporting evidence beyond the punchline. [Source](https://news.ycombinator.com/item?id=48590390)

**Example 2.** *"'AI' is a buzzword now thanks to the Vulture Capitalists. The feature should speak for itself. If your feature is good you don't need to market the underlying technology... Saying something uses AI is pointless."* — strongly stated opinion with no evidence beyond the assertions themselves. [Source](https://news.ycombinator.com/item?id=48571046)

**Coverage & exclusivity.** The four labels are mutually exclusive — one per example. Anything fitting none of the four is skipped at labeling and excluded at export, then topped up with more in-scope data via the `--add` flow.

---

## 3. Data Collection & Labeling

### Source

Hacker News via the public Algolia HN Search API (`https://hn.algolia.com/api/v1`, no auth), collected with `hn_collect.py`. Three passes, all against `/search_by_date` (newest-first):

| Pass | Tag | Quality filter |
|---|---|---|
| Comments | `tags=comment` | length only (no per-comment score on HN) |
| Ask HN | `tags=ask_hn` | `points > 19` |
| Show HN | `tags=show_hn` | `points > 19` |

**Topic scope is narrowed via `--query database`** — a deliberately single-topic corpus, not a general HN sample. Holding the topic constant forces the model to key on rhetorical signal (how a claim is made) rather than topic vocabulary (what the post is about).

### Sampling and filtering

- **Dedup by HN `objectID`** within a run.
- **Length filter:** keep 200–2000 chars of cleaned text. Drops one-liners and walls.
- **Normalization:** HN's HTML (`<p>`, entities, links) stripped to plain text before filtering.
- **Type mixing:** deliberately samples across comments + Ask + Show so post type can't be a shortcut.
- **Anti-anchoring:** final set is shuffled (seed 42) so post types are interleaved during labeling.

### Labeling process

Two-stage process:

1. **Pre-labeling.** Claude Opus 4.7 (via Claude Code) pre-labeled all 200 rows against the planning-doc rules. The pre-labeled file was snapshotted as `hn_dataset.pre-ai.jsonl` before review so AI-vs-final disagreements are recoverable.
2. **Hand-review.** Every row reviewed against §3 tie-break rules; disagreements with AI pre-labels were resolved by the §3 dominant-basis rule.

### Label distribution

| Label | Count | % of 200 |
|---|---|---|
| `anecdote` | 63 | 31.5% |
| `explanation` | 63 | 31.5% |
| `analysis` | 46 | 23.0% |
| `hot_take` | 28 | 14.0% |

`hot_take` came in at **14%, just under the 15% trigger** for the §4 contingency plan. Given project timeline constraints, the dataset was held rather than delayed for targeted re-collection — the trade-off (small support → noisy per-class F1 on test) is documented in §5 and reflected in §6 of `planning.md`.

### Three difficult-to-label examples and decisions

**Example A — "I built X and discovered Y" (Show HN posts).** Examples introducing a product but really offering insight into the problem the product solves. The narrative frame ("I built…") suggests `anecdote`, but the claim often rests on aggregate evidence.

> *"I built a trend visualizer / data-query tool on top of a Product Hunt dataset and discovered that while the amount of launches nearly doubled in the first half of 2026, the engagement (upvotes, comments, etc) with those launches almost halved. Product Hunt's effectiveness was highly contested already, but with the platform being flooded by thin AI launches its value to builders seems fleeting."* — [Source](https://news.ycombinator.com/item?id=48594671)

**Decision:** `analysis`. The §3 rule says strip the narrative frame ("I built…" describes how evidence was gathered, not what the claim rests on); the underlying claim is an aggregate finding over a public dataset that a reader could verify.

**Example B — Structured opinion without verifiable evidence.** Posts that read like reasoned argument but where the supporting claims are themselves assertions, not evidence.

> *"Native software is incredibly difficult to build well. There are at least 4 platforms they would need to support: Win, Mac, iPhone, and Android. That's 4 different software engineers at least, just to keep up with the basic API churn..."* — [Source](https://news.ycombinator.com/item?id=48588372)

**Decision:** `analysis`. Although none of the supporting points cite a measurement, they reason from observable, verifiable facts about platform engineering (number of OS targets, API churn). The §3 rule "checkable aggregate evidence → analysis" applies even when the evidence is implicit rather than tabular.

**Example C — Sarcasm/dismissal with rhetorical confidence.** The hardest boundary: confident statements where the support *is* the rhetorical move, with no further argument.

> *"Writing to disk for every write is required, otherwise you're not durable. Sure it's faster to never write to disk, then you reboot and you've lost data. /dev/null is a webscale database that is even faster!"* — [Source](https://news.ycombinator.com/item?id=48590390)

**Decision:** `hot_take`. The §3 rule "label the dominant basis, not the strongest single sentence" applies — the post sounds argumentative but the entire support is sarcasm and a punchline, not evidence. This is the canonical `hot_take` shape and one the model finds hardest (see §6 below).

---

## 4. Fine-tuning Approach

**Base model:** `distilbert-base-uncased` (66M params), with a fresh 4-way classification head.

**Why DistilBERT:** small enough to train on a T4 GPU in ~2 minutes per run, well-studied baseline for text classification, and the assignment-provided notebook ships with it as the default. The point of the exercise is not architecture exploration but to compare a small fine-tuned model against a frontier prompt-baseline on a small labeled set.

### Training setup

| Hyperparameter | Value |
|---|---|
| Optimizer | AdamW (HF default) |
| Learning rate | 2e-5 |
| Warmup steps | 7 (≈10% of total) |
| Batch size | 16 |
| Epochs | 8 |
| Weight decay | 0.01 |
| Splits | 70/15/15 stratified (140 train / 30 val / 30 test) |
| Seed | 42 |

Loss is class-weighted cross-entropy and best checkpoint is picked by val macro-F1; both decisions are explained below.

### Hyperparameter decision: class-weighted loss

The original notebook's plain cross-entropy collapsed to two classes on test (acc 0.40, macro-F1 0.25, `analysis` and `hot_take` both at F1 0.00) despite val accuracy reaching 0.533. Investigation traced this to untreated class imbalance — `hot_take` at 14% of train (~20 examples) provided too weak a gradient signal, and accuracy-only val monitoring hid the collapse.

**Fix applied:**

```python
from sklearn.utils.class_weight import compute_class_weight
weights = compute_class_weight("balanced",
                               classes=np.arange(NUM_LABELS),
                               y=train_df["label_id"].values)
# Produces: {analysis: 1.09, anecdote: 0.80, explanation: 0.80, hot_take: 1.75}
```

A subclassed `WeightedTrainer` overrides `compute_loss` to pass these weights to `cross_entropy`. Misclassifying a `hot_take` example now costs the model ~2.2× more than misclassifying an `anecdote`. Per-class F1 was also added to `compute_metrics` so collapse is visible during training, not after.

This is the single most consequential decision in the project: it recovered three of four classes on test and raised macro-F1 from 0.25 to 0.44.

### Other deviations from the starter notebook

- **`warmup_steps` reduced from 50 → 7.** The default 50 exceeded the total training step count (27 with 3 epochs), so the LR never reached its nominal peak. Reduced to 10% of total steps.
- **Epochs increased from 3 → 8.** With warmup fixed, more updates were needed to reach a stable val plateau.
- **`metric_for_best_model` changed from `accuracy` → `macro_f1`.** Accuracy let the 2-class collapse hide during training.

---

## 5. Baseline (Zero-shot Llama-3.3-70B via Groq)

Each test post is sent to `llama-3.3-70b-versatile` with `temperature=0` and `max_tokens=20`. The system prompt provides label definitions and one example post per label, copied from §2.

### Prompt

```
You are classifying posts and comments from Hacker News (a technology discussion community).
Assign each post to exactly one of the following categories based on the BASIS of its
claim, not its surface framing.

analysis: A post backs its claim with specific, verifiable evidence (statistics,
benchmarks, historical comparison, code) and reasons from that evidence toward a conclusion.
Example: "It took 5 years from construction start to grid connection for Oskarshamn R3...
That nuclear power must take forever is a myth and is only due to dysfunctional politics."

explanation: A post neutrally describes how or why something works — clarifying a
concept or mechanism without staking a position.
Example: "They seem similar at a glance but they're quite different. You can think of
SQLite as a transactional database while DuckDB is better used as an analytical database..."

anecdote: A post's claim rests on the author's own first-hand, single-instance
experience rather than on aggregate or independently verifiable evidence.
Example: "This morning, our database flagged a duplicate UUID (v4)... the database
only has about 15,000 records, and now one collision. Statistically impossible."

hot_take: A post asserts a confident opinion without supporting evidence — stating
rather than arguing its case.
Example: "Writing to disk for every write is required, otherwise you're not durable...
/dev/null is a webscale database that is even faster!"

Tie-break when a post could fit more than one: analysis > explanation > anecdote > hot_take.
A narrative frame ("I built / we ran / we tried") describes how evidence was gathered —
strip it and label by what the claim actually rests on.

Respond with ONLY the label name. Do not explain your reasoning.

Valid labels:
analysis
explanation
anecdote
hot_take
```

### How results were collected

A simple loop iterates the 30 test rows, sends each one to Groq, and parses the response. Parsing is case-insensitive and tolerates the model wrapping the label in quotes or whitespace. Any response that doesn't match a known label is recorded as unparseable. **All 30 responses parsed successfully** (no unparseable responses).

---

## 6. Evaluation Report

### Headline numbers

| Metric | Baseline (Llama-70B prompt) | Fine-tuned (DistilBERT + weighted loss) | Δ |
|---|---|---|---|
| Accuracy | 0.467 | **0.533** | +0.067 (2 examples) |
| Macro F1 | **0.45** | 0.44 | -0.01 (tied within noise) |
| Weighted F1 | 0.47 | **0.51** | +0.04 |

The fine-tuned model **beats the baseline on accuracy by 2 examples** (well above the one-example noise floor) and **ties on macro-F1**. The story is in the per-class numbers.

### Per-class F1

| Class | Support | Baseline F1 | Fine-tuned F1 | Δ |
|---|---|---|---|---|
| `analysis` | 7 | 0.60 | 0.57 | -0.03 (tied) |
| `anecdote` | 10 | 0.61 | 0.50 | -0.11 |
| `explanation` | 9 | 0.31 | **0.71** | **+0.40** |
| `hot_take` | 4 | 0.29 | **0.00** | **-0.29** |

The fine-tuned model is a **trade**: a large gain on `explanation` (the baseline's weakest class) and a complete loss on `hot_take` (already weak in baseline, now zero). `analysis` and `anecdote` are roughly held.

### Confusion matrix (fine-tuned, test set)

Rows are true labels, columns are model predictions.

| True ↓ \ Pred → | `analysis` | `anecdote` | `explanation` | `hot_take` | Total |
|---|---|---|---|---|---|
| `analysis` | **4** | 2 | 1 | 0 | 7 |
| `anecdote` | 3 | **6** | 0 | 1 | 10 |
| `explanation` | 0 | 3 | **6** | 0 | 9 |
| `hot_take` | 0 | 3 | 1 | **0** | 4 |
| **Total predicted** | 7 | 14 | 8 | 1 | 30 |

(Diagonal sums to 16 = accuracy 16/30 = 0.533. Image version saved at `confusion_matrix.png`.)

### Which labels are being confused?

Read the matrix row-wise (where each true class's errors land):

- **`hot_take`:** all 4 missed — 3 went to `anecdote`, 1 to `explanation`.
- **`anecdote`:** 4 missed — 3 went to `analysis` (the §3-hypothesized boundary), 1 to `hot_take`.
- **`explanation`:** 3 missed — all 3 went to `anecdote` (also §3-hypothesized).
- **`analysis`:** 3 missed — 2 to `anecdote`, 1 to `explanation`, none to `hot_take`.

The named patterns behind these errors — `anecdote`-as-sink, sarcasm blindness, small-class instability — are analyzed in §8.

### Why is the hot_take boundary hard?

Three reasons, in order of importance: **(1) training-set starvation** — ~20 examples is too few for a stable decision boundary; **(2) lexical overlap with `anecdote`** — first-person framing pulls predictions toward anecdote regardless of whether the claim rests on personal experience; **(3) sarcasm** — confident mock-arguments like the `/dev/null` example require world knowledge the classifier head doesn't have. Each of these is examined as its own named pattern in §8.

### Is this a labeling problem or a prompt/data problem?

**A data problem, not a labeling problem.** Hand-spot-checks of the hot_take examples in train confirm the labeling is internally consistent (all clear opinion-without-evidence cases). The model fails not because the labels are wrong but because:
- There aren't enough hot_take examples for the model to learn the boundary.
- The §3 hardest case (sarcasm) requires world-knowledge the model doesn't have.

The `anecdote ↔ analysis` confusion is a different story — both classes are well-represented, and the confusion mirrors the §3-predicted boundary exactly. That suggests the label boundary itself is the bottleneck, not data quantity. Tightening the label definition (e.g., requiring a quantitative claim for `analysis`) would reduce this confusion but lose nuance.

### What would need to change?

- **For `hot_take`:** more data (the §4 contingency, deferred for time) and/or a model that can detect sarcasm (a much larger model, or one fine-tuned on sarcasm-specific data). Tightening the definition wouldn't help; the issue is bandwidth.
- **For `anecdote ↔ analysis`:** clearer training examples that explicitly draw the boundary (e.g., side-by-side posts about the same incident, one with aggregate evidence and one without). Could also try a contrastive learning setup.
- **For `explanation` over-predictions:** none needed — `explanation` is the model's strongest class (F1 0.71). The bigger story is that `explanation` is also the baseline's weakest (F1 0.31), so the fine-tuning is doing real work specifically on this boundary.

### Three specific wrong predictions with analysis

**#1 — `hot_take` predicted as `anecdote` (the dominant failure mode)**

> *"AI agents can perfectly do a lot of the data entry tasks and build dashboards. You practically need to build none of that when you can ask an AI agent to pull the data and build a chart or provide a few summary statistics..."* — [Source](https://news.ycombinator.com/item?id=48592240)
>
> **True:** `hot_take` · **Predicted:** `anecdote` (confidence 0.33)

The post is confidently asserting that AI agents can replace data-entry workflows with no supporting evidence — a textbook hot_take. But the surface vocabulary ("you practically need", "you can ask") reads as personal advice/experience, which the model has learned correlates with anecdote. The confidence is very low (0.33), reflecting the model's uncertainty. This is the §3 hot_take ↔ anecdote boundary that requires reading rhetorical *intent*, not just first-person markers.

**#2 — `hot_take` predicted as `explanation` (sarcasm failure)**

> *"Writing to disk for every write is required, otherwise you're not durable. Sure it's faster to never write to disk, then you reboot and you've lost data. /dev/null is a webscale database that is even faster!"* — [Source](https://news.ycombinator.com/item?id=48590390)
>
> **True:** `hot_take` · **Predicted:** `explanation` (confidence 0.30)

The model reads the structure ("X is required, otherwise Y. /dev/null is Z") as didactic and routes to `explanation`. It can't detect that the post is a sarcastic dismissal of a previous claim. Note the lowest confidence in the wrong-prediction set (0.30) — the model is essentially uncertain across all four classes.

**#3 — `anecdote` predicted as `analysis` (the §3 boundary)**

> *"I am currently getting my Facebook feed flooded with 'ads' that claim to be coming from OpenAI and/or Midjourney. These 'ads' claim to be containing a 'private release' of their new AI technology..."* — [Source](https://news.ycombinator.com/item?id=39545116)
>
> **True:** `anecdote` · **Predicted:** `analysis` (confidence 0.37)

A first-hand observation about a personal social-feed pattern, presented with enough structure (specific brands, mechanism of the scam) to read as analysis. The §3 rule that distinguishes the two — *"checkable aggregate evidence → analysis; single first-hand instance → anecdote"* — would catch this, but only if the model could tell that a single user's feed observations are not aggregate evidence.

### Sample classifications

Four wrong predictions and one correct prediction are sampled below. The full calibration analysis — including whether confidence is a reliable signal — is in §7.

| # | True | Predicted | Conf | Correct? | Text (truncated) |
|---|---|---|---|---|---|
| 1 | `hot_take` | `anecdote` | 0.33 | ✗ | "AI agents can perfectly do a lot of the data entry tasks…" |
| 2 | `hot_take` | `explanation` | 0.30 | ✗ | "/dev/null is a webscale database that is even faster!" |
| 3 | `anecdote` | `analysis` | 0.37 | ✗ | "I am currently getting my Facebook feed flooded with 'ads'…" |
| 4 | `analysis` | `explanation` | 0.40 | ✗ | "Native software is incredibly difficult to build well…" |
| 5 | `explanation` | `explanation` | 0.34 | ✓ | "Here is the thing, it's a write only single file format. If you need to run analytical queries it's optimized for reading, you just open a file and query..." |

**Explanation of the correct case (row 5):** The model correctly identifies this as `explanation` based on structural cues — didactic opener ("Here is the thing"), mechanism description, no personal-experience marker, no rhetorical opinion. This is the cleanest `explanation` shape, and `explanation` is the model's strongest class (F1 0.71).

---

## 7. Confidence Calibration

**The question:** does a 90%-confident prediction actually get it right more often than a 60%-confident one?

**Direct answer: untestable.** The fine-tuned model never produces a 60% confidence, much less 90%. Its **maximum confidence across all 30 test posts is 0.50**, and most predictions cluster between 0.30 and 0.45. The model offers no high-confidence regime to evaluate.

**What the data shows on the range that exists:**

| | n | Mean confidence | Range |
|---|---|---|---|
| Correct predictions (sampled) | 4 | 0.42 | 0.34 – 0.50 |
| Wrong predictions (all) | 14 | 0.36 | 0.30 – 0.45 |

There's a **weak signal** — correct predictions average ~5 percentage points higher in confidence than wrong ones — but the distributions overlap almost entirely. A 0.40 prediction has roughly equal odds of being right or wrong. Confidence is not a useful filter at this granularity.

**Why calibration fails at this dataset size.** With 140 training examples across 4 classes (averaging 35 per class, fewer for `analysis` and `hot_take`), the softmax distribution never sharpens. The classifier head was randomly initialized and only updated 72 times — not enough to learn what "high confidence" should look like for any one class. The model converges to a decision surface that's correct ~53% of the time but offers no per-prediction trust signal.

**Implication for the planning.md §6 human-assist deployment mode.** A reviewer cannot filter to "high-confidence machine calls" because there are none. Confidence cannot be used to spot-check uncertain predictions because every prediction looks uncertain. Effectively the model delivers a single 0.53 accuracy number with no per-row trust gradient. The human-assist deployment plan in planning.md §6 implicitly assumed calibrated confidence; that assumption did not hold.

**Comparison to baseline.** The Llama-70B baseline uses `temperature=0` and emits a label string only — no probability is exposed via the text response. We cannot directly compare calibration between the two models, but **neither offers a usable confidence signal** in their current form.

**What would fix it (in increasing effort):**
1. **Temperature scaling** — a single-parameter post-hoc calibration step using val-set probabilities. Trains a temperature `T` such that `softmax(logits / T)` aligns better with empirical accuracy. Cheap and often effective.
2. **More training data on the thin classes** — the root cause is per-class sample starvation; more `analysis` and `hot_take` examples would let the softmax sharpen naturally.
3. **Distillation** — train against soft-label probabilities from a larger, better-calibrated model rather than hard human labels.

None of these are in scope for this submission, but they would matter more than further hyperparameter tuning if the goal is making the model actually deployable.

---

## 8. Error Pattern Analysis

Three additional error patterns emerged across the final test run and earlier failed runs documented during the investigation loop. They are independent of the calibration issue above — fixing calibration would not fix any of these.

### `anecdote` is the default sink

The model emitted `anecdote` 14 times for 10 actual cases. Eight of those predictions were wrong — drawn from `analysis` (2), `explanation` (3), and `hot_take` (3). When uncertain, the model defaults to `anecdote`.

**Why:** first-person framing ("I think", "we ran", "let me explain") is everywhere on HN, across every label. The model learned to associate first-person markers with `anecdote` regardless of whether the claim rests on personal experience. The §3 tie-break rule (*strip the narrative frame and label by the basis of the claim*) is exactly what the model fails to apply.

**Implication:** the errors are **directional, not symmetric**. The §3 hypothesis predicted balanced `anecdote ↔ analysis` and `anecdote ↔ explanation` confusion; in practice the flow is one-way *into* `anecdote`.

### Sarcasm flips the predicted label

The canonical `hot_take` example ("/dev/null is a webscale database that is even faster!") was predicted as `explanation`. The model reads the structural framing ("X is required, otherwise Y. Z is even faster!") as didactic mechanism description.

**Why:** without world knowledge to recognize "/dev/null as a webscale database" as absurd, the classifier head treats confident sarcasm and confident explanation identically. Token-level fine-tuning of a 66M-parameter model cannot bridge this gap.

### Small classes are unstable even after the class-weight fix

`hot_take` caught 2 of 4 on val (F1 0.50) but 0 of 4 on test (F1 0.00) — same model, same support size, completely different per-class outcome. Earlier in training, run 4's per-class F1 logs showed `hot_take` and `analysis` flickering between dead and alive across consecutive epochs (epoch 1: both at zero; epoch 4: `hot_take` jumps to 0.57; epoch 5: `analysis` revives at 0.44).

**Why:** with ~20 train examples for `hot_take`, the model is one bad split or one weight-init away from "trained" vs "broken." Class weights stopped the model from ignoring the class entirely; they didn't give it enough signal to learn a stable boundary.

**Implication:** any small-class win on val should be treated as provisional, not confirmed, until test agrees. This is the planning.md §5 noise caveat showing up as model behavior, not just as a measurement issue.

---

## 9. Reflection: What the Model Learned vs. What I Intended

**Intended:** a four-way classifier that distinguishes posts by the *basis of their claim* — evidence (`analysis`), mechanism (`explanation`), personal experience (`anecdote`), or unsupported assertion (`hot_take`).

**Learned:**

- **`explanation`: cleanly learned.** Neutral didactic structure is the most consistent signal in the training set, and it's the biggest win — validating the project premise that rhetorical structure is learnable from 140 examples.
- **`analysis`: partially learned.** The model finds quantitative or strongly-structured evidence but conflates structured `anecdote` with `analysis` at the §3-hypothesized boundary.
- **`anecdote`: barely held.** Regresses from baseline, and the model treats it as the default sink for uncertain posts — class-imbalance shadow surviving the weighted loss.
- **`hot_take`: not learned.** Val showed some signal (F1 0.50) but it didn't transfer to test. Dataset-size-bound at ~20 train examples.

**The clearest gap is `hot_take`** — intended as one of four equally-treated classes, learned as a residual category predicted only when nothing else fits.

---

## 10. Spec Reflection

**How the spec helped:** the requirement to write `planning.md` *before* collecting data forced me to define edge-case tie-break rules (§3) upfront. These rules were directly used during hand-labeling and prevented mid-annotation drift. Specifically, the rule *"label the dominant basis, not the strongest single sentence"* came up repeatedly with Show-HN-style posts and would have been impossible to apply consistently if I'd tried to figure it out per-example.

**Where implementation diverged from spec:** the spec's "investigate before writeup" requirement triggered a remediation loop the planning document didn't anticipate. The initial fine-tuned model collapsed to 2 classes on test (acc 0.40, macro-F1 0.25); per the spec, I investigated and identified **untreated class imbalance + accuracy-only val monitoring** as the root cause. The remediation — weighted cross-entropy + per-class F1 in `compute_metrics` + `metric_for_best_model="macro_f1"` — was not in the original `planning.md`. The plan assumed the starter notebook's defaults would produce a working model; in reality, plain cross-entropy with 14% support on the rare class produced a model that scored "competitively" on val accuracy while predicting only 2 of 4 classes. The divergence is documented across `planning.md` §4 (the §4 trigger fired) and §5 (per-class noise caveat added explicitly because `hot_take` n=4 makes its F1 swing ±0.25 per misclass).

---

## 11. AI Usage

This project used Claude (Opus 4.7) extensively. Two specific instances of directed use and revision:

**1. Diagnosing the warmup-vs-total-steps bug.**

After an initial fine-tuning run with the starter notebook's defaults produced flat train loss (~1.38 ≈ ln(4), the uniform-prediction baseline), I asked Claude to inspect the notebook and identify the cause. Claude correctly identified that `warmup_steps=50` exceeded the total training step count of 27 (140 train / 16 batch × 3 epochs), so the linear LR warmup never finished. The fix Claude proposed was `warmup_steps=5` and `num_train_epochs=8`.

**What I revised:** Claude initially proposed `warmup_ratio=0.1` as a cleaner alternative. I tried this first, then noticed the HuggingFace deprecation warning and reverted to the explicit `warmup_steps=7` for the final runs. I also chose to keep `num_train_epochs=8` rather than experimenting with 6 or 10 — the val-loss plateau at epoch 5-6 made further epochs unlikely to help.

**2. Designing the class-weighted loss remediation.**

When the test set revealed a 2-class collapse despite val accuracy looking competitive (0.533), I asked Claude to walk me through the three failure modes the spec asks about (label leakage, class imbalance, training bug). Claude ran a duplicate-detection script on the dataset (ruled out leakage), reviewed the notebook code (ruled out a training bug), and identified class imbalance as the cause. It proposed a `WeightedTrainer` subclass using `sklearn.utils.class_weight.compute_class_weight("balanced", ...)` and an expanded `compute_metrics` function that logs per-class F1 each epoch.

**What I revised:** I accepted the code as proposed. The remediation was applied verbatim — class weights of `{analysis: 1.09, anecdote: 0.80, explanation: 0.80, hot_take: 1.75}` — and produced the final model evaluated above. The expanded `compute_metrics` was decisive: without per-class F1 visible during training, I would not have been able to confirm at training time that all four classes were alive on val (and would not have understood why test still collapsed `hot_take` despite val recovering it).

**Annotation disclosure.** All 200 labeled rows were **first pre-labeled by Claude Opus 4.7** against the §2/§3 rules and then hand-reviewed. The pre-AI file is snapshotted as `data/hn_dataset.pre-ai.jsonl` so AI-vs-final disagreements are recoverable. Borderline calls surfaced during pre-labeling (Show-HN anecdote-vs-explanation, Ask-HN analysis-vs-hot-take) are what motivated the §3 tie-break rules — i.e., the AI's mistakes shaped the schema.

---

## Repository structure

```
.
├── data/labeled.csv          # 200 hand-reviewed examples
├── hn_collect.py             # Algolia HN scraper
├── hn_label.py               # Claude-assisted pre-labeling
├── export_csv.py             # JSONL → CSV exporter
├── planning.md               # Pre-flight design doc (label definitions, edge cases, success criteria)
├── confusion_matrix.png      # Fine-tuned test-set confusion matrix
├── evaluation_results.json   # Headline metrics from the final run
└── README.md                 # This document
```
