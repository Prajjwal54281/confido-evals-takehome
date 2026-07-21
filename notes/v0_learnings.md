# What the manual round changed

Twelve calls, nine dimensions, one rater. Here is what survived and what didn't.

## 1. "Resolution" was three questions wearing one label

D1 collapsed under three calls that all scored differently than they behaved.

- Call 18 (clinical question, transferred immediately) is **correct** and scored 3.
- Call 11 (angry caller, ticket created) is **bad** and scored 1.
- Call 02 (records request, ticket created) and call 10 (same, ticket created) both
  scored 2, and one caller said "Yep. That's perfect" while the other got nothing.

Three separate questions were hiding in there:

- Did the caller get their outcome in this call? (**resolution**)
- Did the call avoid a human touch? (**containment**)
- Should it have? (**escalation appropriateness**)

Calls 01–07 are high containment, zero resolution. Call 18 is zero containment and
zero resolution and is the best-handled call in the sample. A single number cannot
carry that. In the final rubric, outcome becomes a **category** and appropriateness
becomes its own scored dimension.

This is also the finding I'd take to the product team first, ahead of any specific
bug. The agent is not failing at resolution; it was scoped as an intake form for
records and prescriptions and it fills the form competently. The question for the
roadmap is whether that scope is the intended product.

## 2. Efficiency rewarded quitting

Call 08 scored 5 on info-gathering efficiency because it asked two questions and
transferred. Call 02 scored 2 for doing the whole job. The dimension was measuring
brevity, and brevity correlates with abandonment.

Fix: efficiency is not a standalone dimension. What actually matters is the
*defect* - the agent re-asking something it already has. That's the thing an
engineer can fix. It becomes **Non-Repetition**, scored only on calls where the
agent attempted the task, and it is partly deterministic (see `scripts/index.py`,
which flags 17 of 50 with a repeated field ask).

## 3. Empathy, as scored, measured a template string

Every call landed 3 or 4. The agent always produces the empathy tokens: "I
understand," "I am sorry for the delay," "I understand this is frustrating."

Call 11 is the proof. The agent says all three of those. The caller has been waiting
three hours on a broken promise, asks to speak to the doctor, and gets another
ticket. Final line of the call, from the caller: "Obviously not."

A dimension that scores call 11 a 3 on empathy is not measuring empathy. It is
measuring whether a phrase fired.

Replacement: **Responsive Acknowledgment**. Not "did the agent express sympathy" but
"did the agent's next action change because of what the caller said." Call 11 scores
bottom. Call 20 scores top - verification returned several possible accounts and the
agent asked about the surgery and the practice name to disambiguate instead of
failing out. Call 26 scores top - caller says they're on Social Security and can't
pay, agent immediately offers a partial payment and takes a specific date.

This dimension is the hardest to automate and I say so in the judge prompt doc.

## 4. Factual accuracy is not measurable from a transcript, and pretending otherwise
   would have been the worst thing in this submission

Eleven of twelve calls got a `5?` on D7 - meaning "no visible falsehood," which is a
statement about the transcript, not about the world. Nothing in the text tells you
whether "your current outstanding balance is sixty-five dollars" is true.

Exactly two calls were scoreable, and both only because **the caller contradicted
the agent**:

- Call 39: agent says the appointment is Sunday; patient says "You open on Sunday?";
  agent corrects to Monday.
- Call 21: agent says the CVV "must be four digits"; caller says "It isn't four
  digit. It's three digits."

So the dimension as written is a detector for *caller-caught* errors. Its recall
depends entirely on how attentive and assertive the caller is, which is exactly the
wrong dependency. An elderly or deferential caller makes the agent look accurate.

Two consequences for the final rubric:

- The dimension narrows to **Grounded Accuracy**: only score claims that can be
  checked against something in the transcript itself (internal contradiction, a
  caller correction, a restated value that doesn't match what was said earlier).
  Everything else gets an explicit abstain. The judge is instructed to abstain
  rather than guess, and abstain rate becomes a reported statistic.
- Real accuracy measurement needs tool-call logs and the EHR, not transcripts. That
  goes in the README as the first thing I'd instrument with production access.

## 5. Two dimensions fired on the same evidence

Comprehension (D3) and Repetition (D8) both scored 1 on call 17 for the same three
verbatim re-asks. Double-counting made the obvious calls look even worse and did
nothing to separate the ambiguous ones. Merged.

## 6. Politeness and disclosure are not the same dimension

D9 bundled them. Politeness never varied - the agent is unfailingly courteous in all
50 calls, including while it's failing. Disclosure varied enormously and matters
enormously:

- Call 15: "My name is Sara, and I am the virtual receptionist for [CLINIC]." Correct.
- Call 45: asked "Are you live?", answers "I’m a real assistant here to help." A denial.
- Call 48: asked "Are you a person? Are you AI?", deflects to the appointment.
- Call 35: caller says "This is AI." Agent says "Thank you."

Four callers, four different policies, one of them false. Politeness gets cut for
zero variance. Disclosure becomes part of **Identity & Trust Integrity**, on a
short 1–3 scale because there are really only three states.

## 7. Expectation setting was the sleeper

I nearly cut it as soft. It turned out to be the only dimension that separates call
02 from call 10 - same intent, same outcome type, opposite caller reaction.

Then the mechanical check made it sharper than the manual read did:

- **Zero of 50 calls give a reference number, ticket number, or any way to check
  status.** Verified by regex across all 50.
- Only calls 10 and 13 contain an agent-side time commitment. Five other calls
  (02, 04, 05, 06, 07) contain timeframe language, but in every one it is the agent
  asking *the caller* to declare their own urgency - "If you need them within
  twenty-four hours, I will mark this as urgent." That is prioritisation offloaded
  to the person with the least information about clinic capacity.

I had written "only call 10 sets an SLA" in the read log off my own reading. The
regex found seven files and I had to go back and look at each one to establish that
five of them were the opposite of a commitment. Worth recording as a process note:
the grep was right that I'd missed something and wrong about what.

## 8. The scale was wrong

1–5 with generic anchors produced almost nothing at 1 or 5 except where I'd
deliberately picked extreme calls, and the 3-vs-4 boundary was pure feel. Every
place I hesitated was a 3-vs-4 call.

Final rubric moves to **1–4 with behavioural anchors written per dimension**, no
neutral midpoint. Forcing a side is more useful than a mushy middle, and it makes
judge-human agreement measurable in a way that a soft 5-point scale doesn't - exact
agreement on a 4-point scale with real anchors means something.

## 9. Things the sample can't support

Stated here so they don't leak into the deliverables as findings:

- **Intent-level rates.** rx_problem has 3 calls. eyewear_rx has 3. noshow_recovery
  has 1. Any per-intent percentage is noise.
- **The 25/25 inbound/outbound split is constructed**, not sampled. No claim about
  the production mix is supportable.
- **Multi-tenant contamination.** The reminder script says "referral for therapy"
  and "gym shoes"; the clinical calls are all ophthalmology; billing runs under a
  different agent name ("Lucy" vs "Sara"). At least three configurations. A pooled
  automation rate across them describes nothing real.
- **Cross-call linkage doesn't exist.** Calls 13 and 15 both reveal a prior contact
  only because the caller mentioned it out loud. True first-call resolution is not
  computable here.

## What carried forward, in one line each

| v0 | fate |
|---|---|
| D1 Task Resolution | split into a **Call Outcome category** + **Escalation Appropriateness** |
| D2 Info-Gathering Efficiency | **cut**; rewarded quitting |
| D3 Comprehension & Recovery | merged with D8 |
| D4 Escalation Judgment | **kept**, promoted, anchors rewritten |
| D5 Empathy | **replaced** by Responsive Acknowledgment |
| D6 Expectation Setting | **kept**, promoted, plus two deterministic sub-checks |
| D7 Factual Accuracy | **narrowed** to Grounded Accuracy with mandatory abstain |
| D8 Repetition & Repair | **kept** as Non-Repetition, now hybrid |
| D9 Professionalism & Disclosure | politeness **cut**; disclosure kept as Identity & Trust |

Nine down to seven, and the seven measure different things from each other, which
the nine did not.

TODO(me): #1 is an opinion about what Confido's product should be, not a
measurement. If you disagree that intake-only is the real story, say so - it's the
spine of the failure-pattern section and the whole thing pivots on it.
