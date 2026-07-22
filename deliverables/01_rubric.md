# Evaluation rubric

Seven dimensions. Four on agent performance, three on patient experience. Each one
earned its place by changing a decision someone would make; anything that didn't is
in the Ruled Out section at the bottom, which is the more informative half of this
document.

Derived from hand-scoring 12 calls against a rougher 9-dimension v0 and watching it
break. That process is in `notes/manual_scoring_v0.md` and `notes/v0_learnings.md`.

## Two things that constrain everything below

**The two business metrics are my framing, not the brief's.** The brief asks for
agent performance and patient experience. I'm treating those as proxies for
automation rate and patient experience because those are the two numbers a voice-AI
company reports. If Confido's actual north star is different, the dimensions stay
but the weighting changes.

**"Automation rate" as a single number is the wrong instrument here.** Calls 01–07
are fully contained - no human touched them - and not one produced an outcome for
the caller. Call 18 escalated immediately and is the best-handled call in the set.
A rate that scores those the same way is measuring cost, not performance. The rubric
therefore splits containment from resolution and scores appropriateness separately.

## Redaction rule (applies to every dimension, and is restated in every judge prompt)

`[NAME]`, `[NAME_SPELLED]`, `[DOB]`, `[DIGITS]`, `[PHONE]`, `[EMAIL]`,
`[LOCATION]`, `[CLINIC]`, `[STATE]` are anonymization placeholders. Transcripts that
stop mid-sentence, and audio with audible cuts, are anonymization artifacts.

None of these is ever evidence of an agent defect. Specifically:
- An agent asking a caller to repeat or spell a name is **not** a repetition defect
  when the surrounding text is `[NAME]` / `[NAME_SPELLED]` - the redaction removed
  the information needed to judge it (see call 16).
- A call that ends mid-turn is **not** an abandonment (see calls 28, 34, 47).
- Two different people both rendering as `[NAME]` is **not** an agent confusion
  (see call 16's name-disambiguation loop).

## Scope: what is scoreable

Three of the 50 call types are not scoreable on most dimensions and must be handled
before any rate is computed.

| segment | n | calls | treatment |
|---|---|---|---|
| voicemail drops, no human reached | 9 | 29,30,32,41,42,43,44,49,50 | **excluded from all rates**; scored only on Voicemail/IVR Handling, a deterministic check |
| transcripts cut before any outcome | 4 | 31,34,36,37 | excluded from outcome rates, scoreable on conversational dimensions |
| misdial | 1 | 25 | excluded |

Effective scoreable n = 36. Every percentage in this submission uses that
denominator or a stated subset. Say the denominator or don't say the number.

---

# Section A - Agent performance

## A1. Call Outcome

**Definition.** A category, not a score: what actually happened to the caller's need
by the end of the call.

| value | means |
|---|---|
| `resolved` | The caller's stated need was completed in-call. Nothing further required of them. |
| `committed` | Not completed, but the agent made a specific, bounded commitment: what will happen, by when, by whom. |
| `deferred` | A ticket or callback with no time bound and no reference. The caller must wait and hope. |
| `transferred_warm` | Handed to a human, transfer confirmed as connecting. |
| `transferred_failed` | Transfer attempted and failed, or the caller was told to call back themselves. |
| `unresolved` | Call ended with the need neither met nor routed. |

**What does not count.** Creating a ticket is not resolution. Saying "our team will
contact you" is not a commitment unless a timeframe is attached. The caller
sounding satisfied is not resolution - call 12's caller says nothing is wrong and
an order was never placed.

**Why it's in.** Automation rate and containment rate are both derivable from this
one field, and they come out different. `resolved + committed` is the honest
automation numerator. `everything except transferred_*` is containment. In this
sample the gap between those two is the entire finding.

**Computed:** judge, with a deterministic pre-pass that flags transfer and callback
language (`scripts/index.py`) as evidence the judge must reconcile against.

**Metric:** automation rate.

## A2. Escalation Appropriateness

**Definition.** Whether the handle-vs-escalate decision was right, and whether it
was made at the right moment.

| 4 | Escalated exactly when it should have, or correctly handled without escalating. Call 18: clinical dosing question, transferred in three sentences. |
| 3 | Right decision, late. The caller had to signal more than once. Call 17: correct transfer after asking the same question three times to a caller who said "I wish I could understand you." |
| 2 | Wrong decision, recoverable. Escalated something the agent handles elsewhere, or handled something it should have escalated, without harm. Call 22: transfers to a human to email a receipt. Call 08: transfers a records request that four other calls complete end-to-end. |
| 1 | Refused an explicit escalation request, or the escalation failed. Call 11: caller asks to speak to the doctor, gets another ticket. Call 40: "I’m having trouble transferring your call right now. I recommend calling our front desk directly." |

**What does not count.** Escalating a genuine clinical question is never a defect
regardless of automation cost. A1 already records the containment loss; scoring it
twice would push the agent toward answering medical questions it must not answer.

**Why it's in.** It is the only dimension that separates a good transfer from a bad
one, and transfers are the largest controllable lever on automation rate.

**Computed:** judge.
**Metric:** automation rate, with a patient-experience tail at level 1.

## A3. Non-Repetition

**Definition.** Whether the agent re-asked for information the caller had already
supplied in this call.

| 4 | No re-asks. |
| 3 | One re-ask, framed as a confirmation ("just to confirm, that was..."). Legitimate for numbers. |
| 2 | One or more re-asks of already-given information, not framed as confirmation. Call 02: asks for an email address twice after the caller declined and redirected to fax. |
| 1 | Verbatim repetition of the same question three or more times, or re-asking sensitive data after telling the caller the transaction was submitted. Call 17. Call 21: "Please wait while I process your payment" then "the CVV number for your card must be four digits." |

**What does not count.** Asking a caller to spell or repeat a name adjacent to
`[NAME]` / `[NAME_SPELLED]` tokens. Confirming a card number or DOB once by
read-back. Asking for something the caller gave in a *previous* call - not visible.

**Why it's in.** It is the most common defect that is both automatable to detect and
directly fixable in the dialogue policy. Scored 1–2 on 17 of 50 by the deterministic
pass alone.

**Computed:** hybrid. `scripts/index.py` detects repeated field asks with a
deliberately narrow regex (under-counts by design); the judge adjudicates whether
each flagged instance was a legitimate confirmation.

**Metric:** patient experience primarily, automation secondarily (re-asks lengthen
calls and cause abandonment).

## A4. Grounded Accuracy

**Definition.** Whether any factual claim the agent made is contradicted by evidence
**inside the transcript**. Not whether the claim was true in the world.

| 4 | No internal contradiction found. |
| 3 | Ambiguous restatement the caller let pass. |
| 2 | The agent restated a caller-supplied value incorrectly and corrected itself. |
| 1 | The agent asserted something the caller then corrected, or contradicted itself. Call 39: states Sunday, patient says "You open on Sunday?", agent corrects to Monday. Call 21: asserts a 4-digit CVV requirement, caller corrects it. |
| `abstain` | No claim in this transcript is checkable. **This is the expected output for most calls and is not a failure of the judge.** |

**What does not count - and this is the whole design of this dimension.** A
transcript cannot verify that "your balance is sixty-five dollars" is true. Any
judge that scores such a claim is hallucinating a ground truth it does not have.
The judge must abstain, and **abstain rate is reported as a first-class statistic,
not hidden.**

**Why it's in, given it abstains most of the time.** Because the two calls it does
catch are the two most serious errors in the sample: a wrong appointment date given
to a patient, and a payment system asserting a false fact about a caller's own card.
A dimension that fires twice in 50 and catches those two is worth running. Its base
rate is low, which is exactly why it needs the audit cadence in
`02_judge_prompts.md`.

**Honest limitation.** As specified, this measures *caller-caught* errors. Recall
depends on how assertive the caller is. A deferential caller makes the agent look
accurate. Real accuracy measurement needs tool-call logs against the EHR, which is
the first thing I would instrument with production access.

**Computed:** judge, with a mandatory abstain path.
**Metric:** both. A wrong appointment date is a no-show (automation) and a trust
breach (experience).

---

# Section B - Patient experience

## B1. Expectation Clarity

**Definition.** At the end of the call, does the caller know what happens next, when,
and how to check on it?

| 4 | Specific commitment: what, by when, and who. Call 10: "The team typically processes these within two to three business days." Caller: "Yep. That's perfect." |
| 3 | What and who, no when. |
| 2 | "Our team will contact you" with no timeframe, no reference, no way to check. The modal records call. |
| 1 | The caller leaves with a false or contradictory belief about what happens next. Call 27: caller says "I'll call you back tomorrow," agent says "We will call you back tomorrow." Both now expect the other to call. |

**What does not count.** The agent asking the caller to declare their own urgency
("if you need them within twenty-four hours, I will mark this as urgent") is not a
commitment. It appears in calls 02, 04, 05, 06, 07 and is the opposite of expectation
setting - it moves prioritisation onto the person with the least information.

**Why it's in.** It is the single dimension that separates call 02 from call 10 - 
identical intent, identical outcome type, opposite caller reaction. And it is
cheaply fixable: two sentences of prompt change, versus rebuilding a tool integration.

**Deterministic support.** Across all 50 calls, **zero** contain a reference number,
ticket number, confirmation number, or case number. Verified by regex. Only calls
10 and 13 contain an agent-side time commitment.

**Computed:** hybrid - regex for reference-number and timeframe presence, judge for
whether the commitment was actually specific and correctly directed.
**Metric:** patient experience, with a real automation tail - a caller with no
expectation calls back.

## B2. Responsive Acknowledgment

**Definition.** Whether the agent's **next action** changed because of what the
caller said. Not whether it produced sympathetic language.

| 4 | The agent altered its plan in response to the caller's situation. Call 20: lookup returns several possible accounts, agent asks about the recent surgery and the practice name to disambiguate instead of failing out. Call 26: caller says they're on Social Security and can't pay, agent immediately offers a partial payment and takes a specific date and time. |
| 3 | Acknowledged accurately and continued appropriately; nothing needed to change. |
| 2 | Produced empathy language and continued the script unchanged when a change was warranted. |
| 1 | Produced empathy language while denying the caller's explicit request. Call 11: says "I understand how important this is," "I am sorry for the delay," "I understand your frustration," and answers a request to speak to the doctor by creating another ticket. Caller's last words: "Obviously not." |

**What does not count - and this is the point.** The presence of "I understand," "I
am sorry," or "I understand this is frustrating." The agent produces these in
essentially every call including the ones where it fails hardest. A dimension that
counts those strings measures whether a template fired.

**Why it's in.** The v0 empathy dimension had zero variance and scored call 11 a 3.
This is the rewrite. It is the hardest dimension to automate and I flag it as the
widest-CI metric in the judge document.

**Computed:** judge. Lowest confidence of the seven.
**Metric:** patient experience.

## B3. Identity & Trust Integrity

**Definition.** Whether the agent handled its own identity honestly and whether its
security demands were appropriate to the call's direction.

| 3 | Disclosed AI status when asked, or proactively. Call 15: "My name is Sara, and I am the virtual receptionist for [CLINIC]." Security asks proportionate. |
| 2 | Deflected an identity question without answering, or made a security demand that the caller reasonably resisted. Call 48: asked "Are you a person? Are you AI?", redirects to the appointment. Call 28: outbound collections call demands the callee's DOB; caller refuses - "You don't call someone and ask for their information. That's crazy." - and the agent has no recovery path. |
| 1 | Denied being an AI. Call 45: caller asks "Is this a recording? Are you live?"; agent answers "I’m a real assistant here to help confirm and manage appointments." |

**Why a 1–3 scale.** There are only three states and a fourth level would be
invented precision.

**Why it's in.** Four callers raised it (15, 35, 45, 48) and got four different
answers, one of them false. This is the only dimension in the rubric with regulatory
exposure attached - several US states now require AI disclosure on consumer calls - 
and it is a one-line prompt fix. Low prevalence, high severity, trivial remediation.
That combination is exactly what belongs in a week-one rubric.

**What does not count.** Not volunteering AI status when nobody asked. That's a
policy question for Confido and its clinics, not an agent defect.

**Computed:** judge, with a deterministic pre-filter for identity-question
phrasings. Note that in call 35 the caller's "This is AI" is split across two turn
lines by a barge-in and **regex misses it**, which is why the judge sees the full
transcript rather than only pre-filtered candidates.

**Metric:** patient experience, plus compliance risk.

---

# Ruled out

Eight metrics I considered and did not include. Each with the actual reason, not a
polite one.

**1. Empathy / sentiment tone.** *Zero variance.* Scored 3 or 4 on all twelve
manually scored calls. The agent emits empathy tokens unconditionally, including in
call 11 while refusing the caller's request. The dimension detects a template
string. Replaced by B2, which scores behaviour change instead of language.

**2. Professionalism / politeness.** *Zero variance.* The agent is courteous in all
50 calls, including while failing. A metric that never moves cannot inform a
decision. It would also crowd out B3, which is where the actual trust risk lives.

**3. Caller sentiment trajectory (start vs end).** *Confounded by intent.* Call 11's
caller arrives angry about something that happened three hours earlier. Scoring the
agent on his arrival state punishes it for a prior failure and rewards it on calls
where nothing was at stake. Any signal here is dominated by intent difficulty, and
with 3 calls in the rx_problem bucket it cannot be controlled for.

**4. Call duration / turn count as a quality proxy.** *Inversely correlated with
quality in this sample.* Call 08 is among the shortest inbound calls and is the
worst records outcome - two questions and a transfer. Call 07 is long and is the
cleanest records handling. Shipping duration as a quality metric would optimise the
agent toward abandoning callers faster. It stays in `index.csv` as a descriptive
field and never as a score.

**5. HIPAA / PHI-handling compliance.** *Unmeasurable from this data by
construction.* Every identifier is redacted. That is the entire point of the
redaction, and the brief instructs that redactions not be penalised. A judge scoring
PHI handling on redacted transcripts would be scoring the anonymizer. Genuinely
important, genuinely needs unredacted audio and a compliance reviewer, genuinely not
this artifact. **Partial exception worth flagging separately:** in calls 19–23 the
agent collects full card numbers and CVVs by voice, and in call 28 it demands a DOB
on an outbound call. Those are policy questions visible even through redaction, and
B3 catches the second one.

**6. First-call resolution.** *Not computable.* Requires linking calls to a caller
across time, and there is no caller identifier - call IDs are row indices I assigned.
Calls 13 and 15 both reveal a prior contact ("Do I have to repeat everything I just
told to the other person?", "I had called earlier, no one has returned the call"),
and both are only visible because the caller said so out loud. Any FCR number
computed here would be a floor of unknown distance from the truth. Belongs in the
production instrumentation plan, not the rubric.

**7. Response latency, barge-in handling, talk-over.** *Not measurable honestly from
this data - and the audio proved the naive version would be wrong.* My first pass
measured 46–66% silence in the ten recordings and looked like a latency finding.
After transcribing them (`notes/audio_findings.md`), classifying every ≥2s gap by
the preceding content showed the longest gaps sit immediately after PII requests - 
name, DOB, member ID - meaning they are anonymization cuts, which the brief
explicitly says not to penalise. A latency metric built on this audio would mostly
score the anonymizer. Genuine stalls exist (a 12s freeze mid-provider-list in
209bf832bf90, ~5–8s on lookups) and the transcripts corroborate a stall problem
independently (11 calls contain "Are you still there?" / "I am still here"; call
03's caller says "Hello?" thinking the line dropped; call 47's caller asks for a
human during a lookup pause). **In production, with uncut dual-channel audio and
turn timestamps, this becomes a deterministic metric and probably a top-three one.
On this sample it cannot be scored without penalising redaction, so it stays out.**

**8. Medical / clinical correctness of anything the agent says.** *Out of scope by
design, and dangerous to measure.* The correct behaviour is refusal - call 18 is the
positive control. Adding a dimension that scores clinical answers creates pressure
to produce them. The escalation dimension (A2) already rewards the refusal. This is
a case where *not* measuring something is the safety property.

Also considered and dropped without a full entry: intent-classification accuracy
(no ground-truth labels), containment as a standalone score (derivable from A1),
and a composite quality score (would have hidden call 27 entirely, which fails on
exactly one dimension and is otherwise a clean call).

---

Decision on B3's placement: it stays in the week-one rubric, with the constraint
already stated - it is reported as a count with call IDs, never as a rate, because
a 3-in-50 base rate makes any percentage sampling noise. Revisit after a quarter of
production volume; if the count stays near zero once the disclosure line ships, it
graduates to a compliance checklist and frees a rubric slot.

