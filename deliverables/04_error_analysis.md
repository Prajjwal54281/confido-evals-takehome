# Error analysis - how the judges actually got built

## The order I did things in

Ground truth first, rubric second. I read all 50 transcripts end to end before
writing a single dimension. That ordering matters: had I written the rubric first I
would have written the standard voice-AI rubric - resolution, empathy, accuracy,
tone - and four of those six dimensions would have measured nothing on this data.

Then: mechanical index over all 50 → 12-call manual round against a deliberately
rough v0 → watched v0 break → final rubric → judge prompts whose few-shot examples
are the exact calls where v0 broke.

## What the manual round broke, and what each break changed

Five breaks. Each one is a specific edit to a specific prompt.

### Break 1 - "resolution" was three questions in a trenchcoat

Scoring call 18 (clinical question, transferred in three sentences) against call 11
(furious caller, ticket created) made this unavoidable. Call 18 scored 3 on Task
Resolution and is the best-handled call in the set. Call 11 scored 1 and is the
worst. They are not measuring the same thing, and neither is measuring what the
business cares about.

Hiding inside one dimension: *did the caller get their outcome*, *did we avoid a
human*, and *should we have*.

**Prompt consequence.** Outcome became a six-value **category** with an explicit
`committed` vs `deferred` split, and appropriateness became its own 1–4 score in the
same judge. The critical line in the final prompt exists because of this break:

> Creating a ticket is NEVER "resolved". The caller sounding satisfied is NEVER
> evidence of "resolved" on its own.

That second sentence is there because of call 12, where the caller ends happy and an
order was never placed.

### Break 2 - the efficiency dimension rewarded quitting

Call 08 scored **5** on Info-Gathering Efficiency for asking two questions and
transferring a records request that four sibling calls complete end to end. Call 02
scored 2 for doing the job.

I invented a tiebreak mid-scoring ("score N/A when resolution ≤1 via transfer"),
which is the tell that a dimension is broken rather than underspecified.

**Prompt consequence.** The dimension was **deleted**, not patched. What replaced it
is Non-Repetition, which measures the actual fixable defect and cannot be gamed by
doing less.

### Break 3 - empathy measured whether a template fired

Every one of the twelve landed on 3 or 4. The agent emits "I understand," "I am
sorry," and "I understand this is frustrating" unconditionally.

Call 11 emits all three and refuses the caller's explicit request to speak to a
doctor. A dimension that scores that call a 3 on empathy is broken in a way that
would have quietly validated the worst call in the dataset.

**Prompt consequence, shown as a diff.** This is the change I'd point to if I could
only show one.

**v0 (what I scored by hand):**

```
Dimension: Empathy & Acknowledgment
Definition: Did the agent acknowledge the caller's situation and emotional state?
Score 1-5:
  5  Warm, specific acknowledgment of the caller's circumstances.
  4  Clear acknowledgment.
  3  Generic acknowledgment.
  2  Minimal acknowledgment.
  1  None; the agent ignored the caller's emotional state.
```

**v1 (the shipped judge, Judge 5):**

```
You are scoring one AI voice agent call on RESPONSIVE ACKNOWLEDGMENT.

READ THIS TWICE. You are NOT scoring whether the agent produced sympathetic
language. This agent says "I understand", "I am sorry", and "I understand this is
frustrating" in nearly every call, INCLUDING the calls where it fails the caller
most badly. Counting those phrases measures whether a template fired. It is not
what this dimension measures.

You are scoring ONE thing: did the agent's NEXT ACTION change because of what the
caller said?

Score 1-4:
  4  The agent CHANGED its plan in response to the caller's situation.
  3  Acknowledged accurately and continued appropriately; nothing needed to change.
  2  Produced empathy language and continued its script unchanged when a change
     WAS warranted.
  1  Produced empathy language while DENYING or IGNORING the caller's explicit
     request.
```

Four changes and each is traceable to a specific call:

1. The name changed from Empathy to **Responsive Acknowledgment**, because the old
   name kept pulling the judge toward sentiment.
2. Two-thirds of the prompt is now a **negative instruction**. The failure mode was
   specific enough that telling the model what not to do was more effective than
   telling it what to do.
3. The scale inverted its axis: empathy language is now **evidence of failure** at
   levels 1 and 2, not evidence of success. Call 11 sets the bottom anchor.
4. The schema returns `plan_changed` and `empathy_language_present` as separate
   booleans, so the pathological quadrant - empathy present, plan unchanged - is
   queryable directly rather than inferred from a score.

### Break 4 - factual accuracy was unmeasurable and I nearly shipped it anyway

Eleven of twelve calls got `5?` - my own notation for "no visible falsehood," which
is a claim about the transcript, not about the world. Nothing in a transcript
establishes that "your current outstanding balance is sixty-five dollars" is true.

Exactly two calls were scoreable, both only because **the caller contradicted the
agent**: call 39 (wrong appointment day, patient catches it) and call 21 (agent
asserts a false CVV length, caller corrects it).

So the dimension as drafted was a detector for *caller-caught* errors. Its recall
depends on how assertive the caller is - a deferential caller makes the agent look
accurate. That's the wrong dependency and it would have produced a confidently
wrong accuracy number on a dashboard.

**Prompt consequence.** Judge 3 is now built around a mandatory abstain path with an
enumerated list of what it may not score, and it opens by telling the model what it
does not have access to. The load-bearing lines:

> You do NOT have access to the clinic's records, schedule, or billing system. You
> therefore CANNOT verify whether any of these are true [...] DO NOT SCORE THESE.
> [...] Abstaining is the CORRECT answer for most calls. You will not be penalised
> for abstaining. You WILL be producing a wrong answer if you guess.

Plus a counted field, `unverifiable_claims_seen`, which reports per call how many
factual claims the metric deliberately could not check. Tracked over time that
number is the business case for funding tool-call logging.

### Break 5 - two dimensions double-counting the same evidence

Comprehension and Repetition both scored 1 on call 17 for the same three verbatim
re-asks. Merging them cost nothing and stopped the already-obvious calls from
looking artificially worse than the ambiguous ones.

### The one the manual round missed and the machine caught

I claimed in my read log that the sentence-concatenation bug (`for our teamYour
request has been submitted`) appeared in 8 calls. A regex over all 50 found **19**.
I had only been noticing the "our team" variant and missed the payment variant
(`process your payment.Just a moment`) and `at[PHONE]` in the voicemail script.

The reverse also happened. A regex for callers challenging the agent's identity
found calls 45 and 48 and **missed call 35**, where the caller's "This is AI" is
split across two turn lines by a barge-in. My reading caught it; the grep could not.

Both directions of that are in the final design: Judge 2 runs only on
regex-flagged calls and adjudicates them, while Judge 6 reads the full transcript
because pre-filtering would have lost a third of its cases.

## A dry run of the judges

Before shipping the prompts as designs, three of them were executed with an LLM
against six calls chosen to hit the schema's edges - not a production pipeline,
one pass, outputs committed in `data/judge_dryrun/` and held to the same standard
as every other claim here: `scripts/verify.py` checks each output for required
fields, legal enum values, and that every evidence quote is a verbatim substring
of the cited call.

| output | call | result | matches manual score? |
|---|---|---|---|
| Judge 1 | 11 | `deferred`, escalation 1, `caller_requested_human=true` | yes (v0 D1=1, D4=1) |
| Judge 1 | 18 | `transferred_warm`, escalation 4 | yes (v0 D4 top) |
| Judge 1 | 10 | `committed`, timeframe quoted | yes (v0 D6 top) |
| Judge 1 | 40 | `transferred_failed`, escalation 1 | not in manual set |
| Judge 3 | 39 | score 1, `caller_contradiction`, agent conceded | yes (v0 D7=1) |
| Judge 3 | 26 | **abstain**, `unverifiable_external_claim`, 2 claims left unscored | not in manual set |
| Judge 5 | 11 | score 1, `empathy_language_present=true, plan_changed=false` | yes |
| Judge 5 | 26 | score 4, `plan_changed=true` | not in manual set |

What the dry run does establish: the schemas fill correctly, the evidence-before-
score ordering holds, and the abstain path fires where it should - Judge 3
declined to score call 26's balance claim exactly as instructed, and reported the
two claims it could not check in `unverifiable_claims_seen`.

What it does not establish, stated before anyone over-reads the table: **judge
accuracy.** Most of the overlap calls (10, 11, 18, 39) also appear as few-shot
examples inside the very prompts being tested, so agreement on them is partially
circular - the judge was shown the answer. The two clean data points are calls 26
and 40, which appear in no prompt. Real agreement numbers require the held-out
gold set described below, scored by a judge that has never seen those calls in
its examples. The dry run is a mechanics check, not a validation.

## How I'd keep refining this

### Disagreement sampling
Every metric returns `confidence` and every judge can abstain. The weekly human
audit is not a random sample - it's stratified toward:
- all `abstain=true` (is the judge dodging or is the data genuinely thin?)
- all `confidence: "low"`
- all instances of the specific alert combinations: `caller_requested_human=true AND
  escalation_score=1`, `next_action_owner="ambiguous"`, `empathy_language_present=true
  AND plan_changed=false`, `disclosure_outcome="denied"`
- a random 10% floor, so the audit can still discover failure modes the stratification
  wasn't designed to catch

Every human-judge disagreement goes into a disagreement log with the call ID and both
rationales. When one dimension accumulates 10+ disagreements clustering on the same
boundary, that boundary's anchor gets rewritten and the gold set is re-scored.

### Regression set
60 gold-labelled calls, double-scored, disagreements adjudicated, stratified by
intent and outcome. Re-run on every judge prompt change and every judge model change.
A prompt edit that improves the metric you were targeting while moving three others
is the normal outcome, and without a regression set you will not see it.

The 12 calls in `notes/manual_scoring_v0.md` are a **seed, not the gold set** - 
single-rater and deliberately enriched for failure. Any rate computed on them is
meaningless.

### Drift checks when the agent's prompt changes
The non-negotiable one. A judge calibrated against one agent version silently
mis-scores the next. Before and after every agent release: re-run the full gold set,
diff the score distributions per dimension, and require a human to sign off on any
distribution shift over ~1 standard deviation. The failure mode this prevents is a
dashboard that has quietly stopped meaning anything while continuing to render.

### Re-calibration cadence
- Weekly: audit sample per the table in `02_judge_prompts.md`.
- Monthly: recompute weighted κ against the gold set. Below 0.6 on any dimension
  (0.7 on A1 and A3) triggers a prompt rewrite.
- Quarterly: refresh 20% of the gold set. Call mix drifts as clinics onboard, and a
  gold set from launch stops representing production within about two quarters.
- On every agent release: full regression, no exceptions.

### The thing I'd fix first with real volume
Everything in Judge 3 is a workaround for not having tool-call logs. With production
access, accuracy stops being a transcript-inference problem: log every tool call,
its arguments, and its return, and check what the agent *said* against what the tool
*returned*. Call 39's wrong appointment day becomes a deterministic assertion rather
than a lucky catch by an alert patient. That single change moves the lowest-confidence
metric in this rubric to the highest.

