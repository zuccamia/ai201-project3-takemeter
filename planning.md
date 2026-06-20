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
- Its dry, understated register means faint praise, sarcasm, and dismissal share much of the same vocabulary (e.g. "interesting, but I don't think this scales"), so a classifier that separates substantive comments from shallow dismissals could power a reader-side filter or moderation aid that surfaces the discussion actually worth reading on a given topic.

**Why it's a good fit for a classification task:**
<!-- A community is a good fit when the same surface topic gets discussed in genuinely different WAYS or for different PURPOSES — that variation is what your labels capture. Address all three:
     - What varies? Name the axis your labels sit on (intent / tone / fact-vs-opinion / help-seeking-vs-giving). Show it's real in the data, not invented.
     - Why varied ENOUGH to be interesting? A community where 95% of posts fall in one bucket makes a boring, hard-to-evaluate classifier. Argue your labels will each be reasonably populated and that the boundaries require actual reading.
     - Why not trivial? Give one or two reasons a naive baseline (keyword lookup, post length) would FAIL here. That difficulty is what justifies the project. -->
- Posts are self-contained plain text with no images, embeds, or engagement-bait formatting, so the signal lives entirely in the language and gives clean input with minimal preprocessing.
- HN reliably produces both deep technical analysis and reflexive contrarianism, offering several natural label axes (substantive critique vs. shallow dismissal, additive insight vs. "well-actually" correction/explanation, or stance toward the submission).
- The task is genuinely non-trivial because HN's understated register makes faint praise, sarcasm, and dismissal lexically similar, so a keyword or sentiment-lexicon baseline will struggle and correct classification requires actually reading the comment.

---

## 2. Labels

**Label count:** [2–4]

<!-- Quick-reference table — one short gloss per label. Fill the full definitions and examples below. -->
| Label | One-line gloss |
|---|---|
| `analysis` | A structured argument backed by specific, verifiable evidence such as statistics, historical comparison, or tactical observation | 
| `explanation` | A neutral, didactic account of how or why something works, aiming to clarify a concept or mechanism rather than argue a position. |
| `anecdote` | A claim grounded in the author's own first-hand experience ("when we ran this in production..."), offering personal observation rather than generalizable evidence. |
| `hot-take` | A bold, confident opinion asserted without supporting evidence, which may be true but states rather than argues its case. |

<!-- For each label below: a complete-sentence definition stated POSITIVELY (what makes a post belong here), plus exactly two REAL example posts. Use actual posts (quote or close paraphrase + link) — invented examples hide the ambiguity you'll hit later. -->

### Label A — `analysis`

**Definition:**
<!-- One complete sentence: "A post is labeled X when it ___." -->
A post is labeled analysis when it makes a structured argument whose claims are backed by specific, verifiable evidence (such as statistics, benchmarks, historical comparison, code, or concrete tactical observation), reasoning from that evidence toward a conclusion rather than simply asserting one.

**Example posts:**
1. > "It took 5 years from construction start to grid connection for Oskarshamn R3, at the time the reactor with the world's highest rated output. Since it began operating it has produced 350TWh. That nuclear power must take forever is a myth and is only due to dysfunctional politics." — backs the myth-busting thesis with a specific reactor's construction-to-grid timeline and lifetime output, linked to a verifiable nuclear-reactor database entry. [Source](https://news.ycombinator.com/item?id=48595449)
2. > "Benchmarks vs SQLite WITHOUT ROWID (1M records, identical settings): Sequential writes +57%, Random reads +68%, Sequential scan +90%, Random updates +72%, Random deletes +104%..." — full benchmark table with reproducible methodology grounds the performance claims; honest tradeoffs (LMDB beats on raw reads, RocksDB on writes) are called out alongside the wins. [Source](https://news.ycombinator.com/item?id=47136553)

### Label B — `explanation`

**Definition:**
A post is labeled `explanation` when it gives a neutral, didactic account of how or why something works — clarifying a concept, mechanism, or distinction for the reader — without staking a position for or against it.

**Example posts:**
1. > "They seem similar at a glance but they're quite different. You can think of SQLite as a transactional database while DuckDB is better used as an analytical database... SQLite is your metadata record, DuckDB is your ingestion/scanning/aggregating/joining engine." — clarifies the SQLite-vs-DuckDB distinction didactically, framing them as complementary rather than arguing one is better. [Source](https://news.ycombinator.com/item?id=48595297)
2. > "There are actually two types of stored query: regular and 'trusted'. Any query you save is a regular query. It operates under the permissions of the viewer... The problem with that is that it means you can't build an app which other, signed out or unprivileged users, can use. So there's a second category: 'trusted' queries..." — walks the reader through the mechanism of two permission modes to clarify how the system works, with no rhetorical stance. [Source](https://news.ycombinator.com/item?id=48600234)

### Label C — `anecdote`

**Definition:**
A post is labeled `anecdote` when its claim rests primarily on the author's own first-hand, single-instance experience — a personal story, a thing that happened once to them, or a project born from a specific personal need — rather than on aggregate or independently verifiable evidence.

**Example posts:**
1. > "This morning, our database flagged a duplicate UUID (v4)... today the system inserted a new document with a fresh UUIDv4 and it came up with the exact same one: b6133fd6-70fe-4fe3-bed6-8ca8fc9386cd... the database only has about 15.000 records, and now one collision. Statistically... impossible. Has that ever happened to anyone?!" — n=1 personal incident; the claim ("this happened to us") rests entirely on the author's single observation and is not reproducible by readers. [Source](https://news.ycombinator.com/item?id=48060054)
2. > "I discovered ClickHouse around 2017-18 and built a PoC to replace Elasticsearch: 5x better storage and qps, in a couple of weeks. Managers rejected it because it wasn't well known and was seen as 'some database made by Russians.' On a personal level, it's quite sad to have seen that train coming so early and not been able to get on board." — first-hand career story; the numbers are real but unreproducible, and the basis of the claim is "what happened to me." [Source](https://news.ycombinator.com/item?id=48597041)

### Label D — `hot-take`

**Definition:**
A post is labeled `hot-take` when it asserts a bold or confident opinion without supporting evidence, stating rather than arguing its case — the claim may well be true, but the post does not show its work.

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
- a `hot-take` if the post just offers a novel prototype with little to no constructive context, or
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

The first-person "I built a tool" framing makes it look anecdotal, but that framing only describes how the author obtained the evidence, not what the claim rests on. The actual basis is an aggregate finding over a public dataset (launches nearly doubled while engagement almost halved), with a linked Kaggle source anyone can check. That is generalizable, verifiable evidence, not n=1 personal experience, so the characteristic "checkable/generalizable evidence to analysis; first-hand single instance to anecdote" of `analysis` routes cleanly to `analysis`. It also reasons from the evidence toward a conclusion ("value to builders seems fleeting") rather than just asserting one.

Example 2:


**Annotation rule:**
<!-- The decision procedure you'll apply EVERY time you hit this case, so labeling stays consistent. Good rules are deterministic and reference observable features. Forms that work:
     - "If both intents are present, label by the PRIMARY one — judged by the title / first sentence."
     - "If the post contains a direct question addressed to readers -> `help-seeking`, else -> `discussion`."
     Optional: note a second edge case if you have more than one fuzzy boundary, and say how you'll record hard calls (e.g. a `notes` column flagging low-confidence labels). -->
- **Judge by the basis of the claim, not the narrative frame**: "I built/ran/tried" describes how evidence was gathered, not what the claim rests on, so strip the framing before labeling.
- **Checkable aggregate evidence → analysis; single first-hand instance → anecdote**: reproducible data or measurements stay analysis even if self-gathered, while one unreproducible experience is anecdote even when it carries numbers.
- **A link or figure only counts if the claim reasons from it**: verify that the cited source actually supports the conclusion and that a reader could check it, because decorative links, borrowed-authority citations, and cherry-picked stats mimic evidence without being it.
- **Label the dominant basis, not the strongest single sentence**: one assertive unsupported line does not flip an otherwise evidence-based post.
- **Tie-break order when labels genuinely co-occur**: analysis > explanation > anecdote > hot-take, taking the first the post substantially does, not merely gestures at, after the dominant-basis check above.
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

Reproducibility caveat: the default pulls the most recent qualifying posts, so re-running on another day returns a different sample — SEED=42 only fixes the post-collection shuffle, not which posts are fetched. For an exactly reproducible pull, pin a window with the API's created_at_i numeric filter (created_at_i>START,created_at_i<END).

Note on multi-batch collection: because the target is reached by over-collecting and topping up with `--add` (see Sampling), the final corpus is assembled from several runs, each fetching the newest posts not already in the file and paging backward from there. Spreading those runs across different days therefore widens — and fragments — the effective date range of the sample. For an exactly reproducible build, pin and record the `created_at_i` window for *each* batch, not just one; otherwise the date span is whatever the run dates happened to cover.

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
| `hot-take` | 50 |
| **Total** | 200 |

**Contingency — a label is underrepresented after 200 examples:**
<!-- Commit to a concrete plan and the threshold that triggers it (e.g. "if a label is < 15% of 200"). State which you'd try FIRST:
     - Targeted collection: search keywords/threads likely to surface the rare label rather than sampling blindly.
     - Widen the window: longer date range or a related sub-community.
     - Reconsider the schema: if the label stays rare because the behavior IS rare, decide whether to merge it, redefine it, or keep it and report per-class metrics honestly. -->
If any label falls below ~15% of the usable total (and especially below 7, where it can vanish from the 15% val/test slices), I'll first try targeted collection — re-running with `--query` terms likely to surface the rare label, though within the narrow `database` topic lowering `MIN_STORY_POINTS` and `--add`-ing more is often the more reliable lever.
If it stays rare because the behavior genuinely is rare on HN, I'll reconsider the schema: merge the label into its nearest neighbor, broaden its definition, or keep it and report per-class metrics honestly with a note on the small support. I won't up-sample by duplicating the rare class, since near-identical rows leaking across the split inflate the scores and hide the problem.

---

## 5. Evaluation Metrics

<!-- Accuracy alone is not enough — say what else you need and why, grounded in THIS task and YOUR class balance from Section 4. -->

**Primary metric(s):**
<!-- e.g. macro-averaged F1 -->
[your answer]

**Why these are right here:**
<!-- Cover:
     - Why not accuracy alone? If classes are imbalanced, a model that always predicts the majority label scores high accuracy while being useless. Tie this to YOUR expected distribution.
     - Precision vs. recall trade-off: which error is costlier FOR the community tool you imagine? (e.g. for a moderation-flag classifier, a false positive annoys good-faith users; a false negative lets harmful content through — which matters more, and why?) Pick your operating point accordingly.
     - Per-class vs. averaged: will you report per-label P/R/F1 to catch a label the model quietly fails on? Macro- or micro-average, given your balance? -->
[your answer]

**Supporting analysis:**
<!-- A confusion matrix to see WHICH labels get confused — this should line up with your edge cases from Section 3. Optionally a few qualitative error examples. -->
[your answer]

**Validation setup:**
<!-- Train/test split or k-fold? A held-out test set you don't touch until the end? Note it so results are trustworthy. -->
[your answer]

---

## 6. Definition of Success

**"Genuinely useful" bar:**
<!-- What performance makes this classifier worth using? Frame it against a BASELINE, not zero:
     e.g. "beats a majority-class baseline of X% and a keyword baseline of Y% by a meaningful margin," plus a per-class floor ("no label below Z F1, so the tool isn't blind to any category"). -->
[your answer]

**"Good enough to deploy" bar:**
<!-- What would you accept to run this in a real community tool? It depends on what the tool DOES with predictions:
     - Auto-acts (auto-removes / publicly tags): high, precision-driven bar — errors are visible and costly.
     - Assists a human (surfaces a suggestion a mod confirms): lower bar — a person catches mistakes.
     State which deployment mode you're targeting + the numeric threshold, then name the failure mode that would make you NOT ship even if aggregate numbers look fine (e.g. "systematically mislabels the rare-but-important class"). -->
[your answer]

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
