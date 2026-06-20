# TakeMeter — planning.md

> Complete this document before collecting data or training anything.
> Your label definitions and edge-case rules are what keep annotation consistent — the more precise they are, the less you'll second-guess yourself mid-labeling.
> This planning.md will be reviewed as part of your submission.
> Update it before you change your label schema or success thresholds.

| | |
|---|---|
| **Author** | Nguyen Bich Ngoc Hoang (Norah Hoang) |
| **Course / Assignment** | AI201 Summer 2026 |
| **Date** | 6/19/2026 |
| **Repo** | [link] |

---

## 1. Community

**Community chosen:**
<!-- Name the subreddit / forum / Discord / etc. with a link. -->
[HackerNews](https://news.ycombinator.com/news)

**Why this community:**
<!-- What drew you to it? Useful angles: you already understand its norms, it has a clear observable behavior worth classifying, or it produces a high volume of self-contained posts. -->
- Hacker News is a vibrant technology community that produces a high, diverse volume of both detailed analytic posts and bold hot-takes.
- It offers a completely free, open API for fetching comments and posts.
- HN's dry register makes faint praise, sarcasm, and dismissal lexically similar — a useful target for a reader-side filter that surfaces real discussion.

**Why it's a good fit for a classification task:**
<!-- A community is a good fit when the same surface topic gets discussed in genuinely different WAYS or for different PURPOSES — that variation is what your labels capture. Address all three:
     - What varies? Name the axis your labels sit on (intent / tone / fact-vs-opinion / help-seeking-vs-giving). Show it's real in the data, not invented.
     - Why varied ENOUGH to be interesting? A community where 95% of posts fall in one bucket makes a boring, hard-to-evaluate classifier. Argue your labels will each be reasonably populated and that the boundaries require actual reading.
     - Why not trivial? Give one or two reasons a naive baseline (keyword lookup, post length) would FAIL here. That difficulty is what justifies the project. -->
- Posts are self-contained plain text with no images, embeds, or engagement-bait formatting, so the signal lives entirely in the language and gives clean input with minimal preprocessing.
- HN reliably produces both deep technical analysis and reflexive contrarianism, so each label will be populated and the boundaries require actual reading.
- A keyword or sentiment-lexicon baseline will struggle because the labels turn on rhetorical structure (basis of the claim), not vocabulary.

---

## 2. Labels

**Label count:** [2–4]

<!-- Quick-reference table — one short gloss per label. Fill the full definitions and examples below. -->
| Label | One-line gloss |
|---|---|
| `analysis` | A structured argument backed by specific, verifiable evidence such as statistics, historical comparison, or tactical observation | 
| `explanation` | A neutral, didactic account of how or why something works, aiming to clarify a concept or mechanism rather than argue a position. |
| `anecdote` | A claim grounded in the author's own first-hand experience ("when we ran this in production..."), offering personal observation rather than generalizable evidence. |
| `hot_take` | A bold, confident opinion asserted without supporting evidence, which may be true but states rather than argues its case. |

<!-- For each label below: a complete-sentence definition stated POSITIVELY (what makes a post belong here), plus exactly two REAL example posts. Use actual posts (quote or close paraphrase + link) — invented examples hide the ambiguity you'll hit later. -->

### Label A — `analysis`

**Definition:**
<!-- One complete sentence: "A post is labeled X when it ___." -->
A post is labeled `analysis` when its claim is backed by specific, verifiable evidence (statistics, benchmarks, historical comparison, code) and reasons from that evidence toward a conclusion.

**Example posts:**
1. > "It took 5 years from construction start to grid connection for Oskarshamn R3, at the time the reactor with the world's highest rated output. Since it began operating it has produced 350TWh. That nuclear power must take forever is a myth and is only due to dysfunctional politics." — backs the myth-busting thesis with a specific reactor's construction-to-grid timeline and lifetime output, linked to a verifiable nuclear-reactor database entry. [Source](https://news.ycombinator.com/item?id=48595449)
2. > "Benchmarks vs SQLite WITHOUT ROWID (1M records, identical settings): Sequential writes +57%, Random reads +68%, Sequential scan +90%, Random updates +72%, Random deletes +104%..." — full benchmark table with reproducible methodology grounds the performance claims; honest tradeoffs (LMDB beats on raw reads, RocksDB on writes) are called out alongside the wins. [Source](https://news.ycombinator.com/item?id=47136553)

### Label B — `explanation`

**Definition:**
A post is labeled `explanation` when it neutrally describes how or why something works — clarifying a concept or mechanism without staking a position.

**Example posts:**
1. > "They seem similar at a glance but they're quite different. You can think of SQLite as a transactional database while DuckDB is better used as an analytical database... SQLite is your metadata record, DuckDB is your ingestion/scanning/aggregating/joining engine." — clarifies the SQLite-vs-DuckDB distinction didactically, framing them as complementary rather than arguing one is better. [Source](https://news.ycombinator.com/item?id=48595297)
2. > "There are actually two types of stored query: regular and 'trusted'. Any query you save is a regular query. It operates under the permissions of the viewer... The problem with that is that it means you can't build an app which other, signed out or unprivileged users, can use. So there's a second category: 'trusted' queries..." — walks the reader through the mechanism of two permission modes to clarify how the system works, with no rhetorical stance. [Source](https://news.ycombinator.com/item?id=48600234)

### Label C — `anecdote`

**Definition:**
A post is labeled `anecdote` when its claim rests on the author's own first-hand, single-instance experience rather than on aggregate or independently verifiable evidence.

**Example posts:**
1. > "This morning, our database flagged a duplicate UUID (v4)... today the system inserted a new document with a fresh UUIDv4 and it came up with the exact same one: b6133fd6-70fe-4fe3-bed6-8ca8fc9386cd... the database only has about 15.000 records, and now one collision. Statistically... impossible. Has that ever happened to anyone?!" — n=1 personal incident; the claim ("this happened to us") rests entirely on the author's single observation and is not reproducible by readers. [Source](https://news.ycombinator.com/item?id=48060054)
2. > "I discovered ClickHouse around 2017-18 and built a PoC to replace Elasticsearch: 5x better storage and qps, in a couple of weeks. Managers rejected it because it wasn't well known and was seen as 'some database made by Russians.' On a personal level, it's quite sad to have seen that train coming so early and not been able to get on board." — first-hand career story; the numbers are real but unreproducible, and the basis of the claim is "what happened to me." [Source](https://news.ycombinator.com/item?id=48597041)

### Label D — `hot_take`

**Definition:**
A post is labeled `hot_take` when it asserts a confident opinion without supporting evidence — stating rather than arguing its case.

**Example posts:**
1. > "Writing to disk for every write is required, otherwise you're not durable. Sure it's faster to never write to disk, then you reboot and you've lost data. /dev/null is a webscale database that is even faster!" — sarcastic, confident dismissal with no supporting evidence beyond the punchline; the rhetorical move is the whole argument. [Source](https://news.ycombinator.com/item?id=48590390)
2. > "'AI' is a buzzword now thanks to the Vulture Capitalists. The feature should speak for itself. If your feature is good you don't need to market the underlying technology... Saying something uses AI is pointless." — strongly stated opinion across multiple sentences with no evidence beyond the assertions themselves. [Source](https://news.ycombinator.com/item?id=48571046)

**Coverage & exclusivity:**
<!-- Are the labels mutually exclusive? Do they cover ~everything in the community, or do you need an "Other / out-of-scope" bucket? State the decision and why. -->
The four labels (`analysis`, `anecdote`, `explanation`, `hot_take`) are mutually exclusive — one per example, with a documented tie-break for the analysis/explanation edge. I dropped an explicit `other` bucket because the misfits were mostly Show HN project announcements (a source artifact, not a real category), so I cleaned the source and over-collected instead of adding a fifth class. Anything fitting none of the four is skipped at labeling and excluded at export, then topped up with more in-scope data — keeping coverage clean without a catch-all that would dilute training.

---

## 3. Hard Edge Cases

**The genuinely ambiguous case:**
<!-- Name the two specific labels it sits between, then characterize the PATTERN — don't just say "some posts are unclear."
     Example shape: "Posts that ask a question but are really venting sit between `help-seeking` and `discussion`." -->
Posts that introduce a new product but are really offering insights into a problem that the product is trying to solve could sit between `anecdote` and `analysis`, depending on what type of insights they elaborate on.

**Why it's ambiguous:**
<!-- What signal pulls it toward each label? -->
A `Show HN` post that showcases a product or an idea could be either be:
- an `anecdote` if the post is about how the product was born out of a personal experience, or 
- a `hot_take` if the post just offers a novel prototype with little to no constructive context, or
- an `analysis` if the post tries to articulate WHY a product is a good idea and backs that up with structured arguments, verifiable statistics and observations, or
- an `explanation` if the post is only describing in details how the product works without stating any stance or concluding in any position.

**Concrete instances:**
<!-- A real post you found hard to call, + link. -->
Example 1:
```
I built a trend visualizer / data-query tool on top of a Product Hunt dataset (https://www.kaggle.com/datasets/mathisco01/product-hunt-laun...) and discovered that while the amount of launches nearly doubled in the first half of 2026, the engagement (upvotes, comments, etc) with those launches almost halved.

Product Hunts effectiveness was highly contested already, but with the platform being flooded by thin AI launches it's value to builders seems fleeting.

And before you ask, yes the webapp was built with LLMs.
```
[Source](https://news.ycombinator.com/item?id=48594671)

"I built a tool" frames it as anecdote, but the claim rests on an aggregate finding over a public Kaggle dataset (launches doubled, engagement halved) — checkable, generalizable evidence that reasons to a conclusion ("value to builders seems fleeting"). Routes to `analysis`.

Example 2:
```
I added the Feed feature to the site to make it more usable from mobile. You can scroll and discover important connections. I used Wikidata as source, ArangoDB as database, Redis for caching, Vue+ Cytoscape.js for frontend. If you are from desktop try Explore mode.
```
[Source](https://news.ycombinator.com/item?id=48572698)

Sits between `anecdote` and `explanation`. The "I added X" frame looks anecdotal, but strip it and the descriptive content (what the feature does, the stack, a usage tip) survives intact — no story arc, no claim, no contested position. The dominant basis is description, not personal experience. Pre-labeled `anecdote`; corrected to `explanation`.

Example 3:
```
This is such a basic thing nowadays, and ElasticSearch is massive overkill for it. Something like SQLite or LanceDB or basically any vector database is much more appropriate.

This seems to be coming from the "we must make ElasticSearch AI-compatible" department more than anything.
```
[Source](https://news.ycombinator.com/item?id=48584737)

Sits between `analysis` and `hot_take` because naming concrete alternatives (SQLite, LanceDB) looks like evidence. But the alternatives are listed, not justified: no mechanism, no characterization of what the task needs, no tradeoff. The post stakes a contested position ("massive overkill") and asserts rather than argues it. Pre-labeled `analysis`; corrected to `hot_take`.

**Annotation rule:**
<!-- The decision procedure you'll apply EVERY time you hit this case, so labeling stays consistent. Good rules are deterministic and reference observable features. Forms that work:
     - "If both intents are present, label by the PRIMARY one — judged by the title / first sentence."
     - "If the post contains a direct question addressed to readers -> `help-seeking`, else -> `discussion`."
     Optional: note a second edge case if you have more than one fuzzy boundary, and say how you'll record hard calls (e.g. a `notes` column flagging low-confidence labels). -->
- **Judge by the basis of the claim, not the narrative frame**: "I built/ran/tried" describes how evidence was gathered, not what the claim rests on, so strip the framing before labeling.
- **Checkable aggregate evidence → analysis; single first-hand instance → anecdote**: reproducible data or measurements stay analysis even if self-gathered, while one unreproducible experience is anecdote even when it carries numbers.
- **A link or figure only counts if the claim reasons from it**: verify that the cited source actually supports the conclusion and that a reader could check it, because decorative links, borrowed-authority citations, and cherry-picked stats mimic evidence without being it.
- **Label the dominant basis, not the strongest single sentence**: one assertive unsupported line does not flip an otherwise evidence-based post.
- **Tie-break order when labels genuinely co-occur**: analysis > explanation > anecdote > hot_take, taking the first the post substantially does, not merely gestures at, after the dominant-basis check above.
- **Flag, don't agonize**: if it is within a coin-flip of two labels, assign the tie-break winner and mark it low_confidence for review.

---

## 4. Data Collection Plan

**Where examples come from:**
<!-- API / scraper / export tool (e.g. Reddit PRAW, Pushshift archive, manual). Note time range and sort (top/new/hot) so it's reproducible. -->
Hacker News, via the public Algolia HN Search API (https://hn.algolia.com/api/v1, no key/auth), collected with hn_collect.py. Three passes, all against the /search_by_date endpoint (newest-first):

comments — tags=comment, no score filter (HN doesn't expose per-comment points)
Ask HN — tags=ask_hn, numericFilters=points>19 (i.e. ≥20 points)
Show HN — tags=show_hn, numericFilters=points>19

Sort is by date (newest-first), paging backward in time until each target fills.

**Topic scope is narrowed via `--query database`** — a deliberately single-topic corpus, not a general HN sample. Collected on `06/19/2026`.

Single-topic rationale: holding the topic constant is intentional. Because every example is about databases, the model can't use topic vocabulary as a shortcut to guess the label — it's forced to key on the *rhetorical* signal (how a claim is made) rather than *what* the post is about, which is exactly the axis this taxonomy measures. So a fixed topic sharpens the learning signal for style. The tradeoff: narrower generalization — a classifier trained only on database posts is expected to transfer less well to unrelated topics. Accepted as a scope limitation for this project, not a defect.

Reproducibility caveat: the default pulls the newest qualifying posts, so re-running returns a different sample — SEED=42 only fixes the shuffle, not the fetch. Because the target is reached by over-collecting and topping up with `--add`, the final corpus is assembled from several runs across different days, fragmenting the effective date range. For an exact reproducible build, pin and record the API's `created_at_i` window for *each* batch.

**Sampling approach:**
<!-- How do you avoid a skewed or duplicate-heavy sample? Dedup, removing deleted/bot posts, min-length filter, etc. -->
- Dedup: every item is keyed by HN objectID; a shared seen set blocks duplicates within and across the three passes. (Note: this only dedups within a single run — when merging multiple runs, dedup by id first.)
- Length filter: keep 200–2000 chars of cleaned text. Drops one-liners ("+1", "this"), over-long walls, and empty/deleted items (their text is blank and falls below the floor).
- Normalization: HN's HTML (<p>, entities, links) is stripped to plain text before filtering, so length reflects real content.
- Type mixing: deliberately samples across comments + Ask/Show so the rhetorical label can't be trivially predicted from post type.
- Quality floor: Ask/Show require ≥20 points; comments rely on recency + length instead (no score available).
- Anti-anchoring: final set is shuffled (seed 42) so post types are interleaved during labeling.

**Not handled**: bot/automated accounts aren't explicitly excluded (rare on HN — spot-check recurring authors), and near-duplicate text under different IDs isn't caught by ID dedup.

**Target counts:**
<!-- State per-label targets and the rationale. Roughly balanced classes make training and evaluation cleaner. If you allow imbalance because it reflects the real distribution, say so AND note the consequence for your metrics (see Section 5). -->

The collector targets a *post-type* mix, not label balance — and with `--query database` that mix skews comment-heavy (Ask/Show database posts are scarce; see Sampling). The four labels are assigned by hand after collection, so the per-label targets below are aspirational (an even split). The **target is 200 _usable_ examples** (after skipped/excluded rows are dropped), reached by over-collecting and topping up via `--add`; the real per-label distribution is recorded post-labeling from `export_csv.py`'s by-label count.

| Label | Target # examples |
|---|---|
| `analysis` | 50 |
| `anecdote` | 50 |
| `explanation` | 50 |
| `hot_take` | 50 |
| **Total** | 200 |

**Contingency — a label is underrepresented after 200 examples:**
<!-- Commit to a concrete plan and the threshold that triggers it (e.g. "if a label is < 15% of 200"). State which you'd try FIRST:
     - Targeted collection: search keywords/threads likely to surface the rare label rather than sampling blindly.
     - Widen the window: longer date range or a related sub-community.
     - Reconsider the schema: if the label stays rare because the behavior IS rare, decide whether to merge it, redefine it, or keep it and report per-class metrics honestly. -->
If a label falls below ~15% of the usable total, I'll first try targeted collection — re-running with `--query` terms likely to surface the rare label, or lowering `MIN_STORY_POINTS` and `--add`-ing more. If it stays rare, I'll reconsider the schema: merge with its nearest neighbor, broaden the definition, or keep it and report per-class metrics with a note on small support. No up-sampling by duplication — leakage across the split inflates scores and hides the problem.

**Outcome (post-labeling):** the trigger fired — `hot_take` came in at 14% (28/200). On a project timeline, I chose to **hold the dataset** rather than delay for targeted re-collection. The trade-off is documented in §5 (per-class noise caveat — `hot_take` test support is n=4, so its F1 swings ±0.25 per misclass) and reflected in §6 (the per-class floor for `hot_take` is loosened from a precise threshold to a directional "≥3 of 4 correct" check). The label boundary itself remains meaningful in the data, so I kept the four-way schema rather than merging.

---

## 5. Evaluation Metrics

<!-- Accuracy alone is not enough — say what else you need and why, grounded in THIS task and YOUR class balance from Section 4. -->

**Primary metric(s):**
<!-- e.g. macro-averaged F1 -->
Macro-F1. Also report per-class precision, recall, F1, and a 4×4 confusion matrix.

**Why these are right here:**
<!-- Cover:
     - Why not accuracy alone? If classes are imbalanced, a model that always predicts the majority label scores high accuracy while being useless. Tie this to YOUR expected distribution.
     - Precision vs. recall trade-off: which error is costlier FOR the community tool you imagine? (e.g. for a moderation-flag classifier, a false positive annoys good-faith users; a false negative lets harmful content through — which matters more, and why?) Pick your operating point accordingly.
     - Per-class vs. averaged: will you report per-label P/R/F1 to catch a label the model quietly fails on? Macro- or micro-average, given your balance? -->
- Classes are uneven (anecdote 31.5%, explanation 31.5%, analysis 23%, hot_take 14%), so accuracy can hide failure on the smaller two. Macro-F1 weights each class equally. Note: `hot_take` came in at 14%, tripping the 15% contingency in §4. Given the project timeline, I held the dataset rather than delaying for targeted re-collection — the per-class noise caveat below documents the resulting trade-off (n=4 on test → ±0.25 F1 swing per misclass), and §6's per-class floor is correspondingly loosened for `hot_take`.
- Precision and recall matter the same here — this is a reader-side filter, not a moderation tool, so no error is more costly than the other.
- Per-class F1 is the check that no label gets quietly ignored.

**Supporting analysis:**
<!-- A confusion matrix to see WHICH labels get confused — this should line up with your edge cases from Section 3. Optionally a few qualitative error examples. -->
The confusion matrix is the diagnostic for Section 3 edges (`analysis` ↔ `explanation`, `anecdote` ↔ `analysis`, `anecdote` ↔ `explanation`). The Groq baseline surfaced an unhypothesized confusion worth watching: `hot_take` as a sink — the baseline emitted `hot_take` ~2.5× its true frequency on test (10 predictions, 4 actual), with most of those false positives drawn from real `analysis` and `explanation` posts. If those cells are heavy in the fine-tuned model too, the boundary is the bottleneck, not the model. I'll also pull 5–10 error examples for the writeup.

**Validation setup:**
<!-- Train/test split or k-fold? A held-out test set you don't touch until the end? Note it so results are trustworthy. -->
Stratified 70/15/15 split: 140 train, 30 val, 30 test. Test is held out until final scoring; val is used during development for prompt and hyperparameter iteration. The zero-shot Llama-3.3-70B baseline scores on the same held-out 30-row test set. Caveat: 30 rows is small — test supports are 7 / 10 / 9 / 4 for analysis / anecdote / explanation / hot_take, so a single misclassification shifts overall accuracy by ~3 percentage points, per-class F1 by ~10 points on the larger classes and **~25 points on `hot_take` (n=4)**. Narrow macro-F1 gaps are noise; per-class numbers must be reported alongside any headline, and `hot_take`-specific claims should be made cautiously.

---

## 6. Definition of Success

**"Genuinely useful" bar:**
<!-- What performance makes this classifier worth using? Frame it against a BASELINE, not zero:
     e.g. "beats a majority-class baseline of X% and a keyword baseline of Y% by a meaningful margin," plus a per-class floor ("no label below Z F1, so the tool isn't blind to any category"). -->
Beats the zero-shot Llama-3.3-70B baseline (macro-F1 **0.45**; per-class F1: analysis **0.60**, anecdote **0.61**, explanation **0.31**, hot_take **0.29**) on macro-F1, OR beats it on the two smallest classes (`analysis`, `hot_take`) where labeled data should help most. Per-class floor: no F1 below 0.45, with one caveat — `hot_take` has only 4 test examples, so its F1 jumps in ±0.25 increments; treat the floor for `hot_take` as a directional check (≥3 of 4 correct) rather than a precise threshold. (Caveat: gold is hand-reviewed Opus pre-labels, so part of any Llama gap is style drift, not real error.)

**"Good enough to deploy" bar:**
<!-- What would you accept to run this in a real community tool? It depends on what the tool DOES with predictions:
     - Auto-acts (auto-removes / publicly tags): high, precision-driven bar — errors are visible and costly.
     - Assists a human (surfaces a suggestion a mod confirms): lower bar — a person catches mistakes.
     State which deployment mode you're targeting + the numeric threshold, then name the failure mode that would make you NOT ship even if aggregate numbers look fine (e.g. "systematically mislabels the rare-but-important class"). -->
Mode: human-assist (suggests a label, person confirms). Bar: macro-F1 ≥ 0.65, no class below 0.50. Block ship if the model systematically mixes `analysis` with `hot_take` — separating those is the whole point of the tool.

---

## 7. AI Tool Plan
 
<!-- This is a labeling project, not an implementation one — there's no code to generate. AI tools help in three places. -->
 
**Label stress-testing:**
<!-- Give the AI your label definitions + edge-case description; ask for 5-10 posts that sit on the boundary between two labels. Posts you can't classify cleanly mean your definitions need tightening now, before annotating 200 examples. -->
Done implicitly via pre-labeling — Claude's borderline calls (Show HN anecdote-vs-explanation, Ask HN analysis-vs-hot-take) surfaced the gaps now codified in the Section 3 tie-break rules.
 
**Annotation assistance:**
<!-- Will you use an LLM to pre-label a batch before reviewing it yourself? If yes, name the tool and how you'll track which examples were pre-labeled (for the AI-usage disclosure). -->
**Claude Opus 4.7 (via Claude Code)** pre-labeled all 200 rows on 2026-06-19 against the Section 2/3 rules; I'll snapshot the file as `hn_dataset.pre-ai.jsonl` before the hand-review pass so AI-vs-final disagreements are recoverable.
 
**Failure analysis:**
<!-- Plan to hand your wrong predictions to an AI tool to spot patterns before writing up evaluation. Note what patterns you'll look for (e.g. one label confused for another, length effects) and how you'll verify them yourself. -->
[your answer]

---

_End of planning document._
