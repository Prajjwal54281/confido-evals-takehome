# Manual scoring round - v0 rubric, 12 calls, scored by hand

## How the 12 were picked

Stratified on two axes: intent cluster, and whether the call *looked* like it went
well on a first skim. I wanted contrast pairs inside the same intent so the rubric
would be forced to distinguish them rather than just tracking intent difficulty.

| call | intent | picked because |
|---|---|---|
| 02 | records_request | the modal records call: full slot-fill, ticket |
| 08 | records_request | **contrast to 02** - identical opening intent, transferred after 2 questions |
| 10 | eyewear_rx | ticket-ending call where the caller sounds genuinely happy |
| 11 | rx_problem | worst call in the set; angry caller, explicit escalation request |
| 12 | eyewear_rx | quiet failure - logged intent ≠ stated intent |
| 17 | rx_refill | comprehension breakdown; correct outcome reached far too late |
| 18 | clinical_question | **positive control** for scope discipline |
| 21 | billing_payment | in-call resolution that still contains a hard bug |
| 22 | billing_payment | **contrast to 21** - resolved, then a transfer for a trivial ask |
| 27 | billing_collections | short call, single decisive error |
| 39 | appt_reminder | factual error caught by the patient |
| 45 | appt_reminder | AI-disclosure failure plus a lost patient |

**Deliberately excluded, with reasons:** the 9 voicemail drops (29, 30, 32, 41–44,
49, 50) - no human on the line, nothing to score, and including them would make the
rubric's scale meaningless at the low end. Call 25 (misdial, 3 turns). Calls 31, 34,
36, 37 (transcripts cut before anything resolves).

Not a random sample. It is enriched for failure on purpose, because the point of
this round is to find where the rubric breaks, not to estimate a rate. Every
prevalence number in the final deliverables comes from all 50, not from these 12.

## v0 rubric (rough, on purpose)

Nine dimensions, all 1–5. Anchors written before scoring, not adjusted during.

| # | dimension | definition | proxy for |
|---|---|---|---|
| D1 | Task Resolution | Was the caller's stated need met inside this call? | automation |
| D2 | Info-Gathering Efficiency | Did the agent collect only what it needed, in a sensible order? | automation |
| D3 | Comprehension & Recovery | Did the agent understand the caller and recover from mishears? | both |
| D4 | Escalation Judgment | Was the handle-vs-transfer decision right, and timely? | automation |
| D5 | Empathy & Acknowledgment | Did the agent acknowledge the caller's situation? | experience |
| D6 | Expectation Setting | Does the caller know what happens next, when, and by whom? | experience |
| D7 | Factual Accuracy | Was everything the agent asserted true? | both |
| D8 | Repetition & Repair | Did the agent avoid re-asking things already answered? | experience |
| D9 | Professionalism & Disclosure | Tone, identity, security handling | experience |

Anchors used (same shape for all nine): 5 = no defect. 4 = minor, caller unaffected.
3 = noticeable, caller had to compensate. 2 = caller visibly harmed or confused.
1 = call-ruining.

Redaction rule applied throughout: `[NAME]`, `[DOB]`, `[DIGITS]`, `[LOCATION]`,
`[CLINIC]`, `[NAME_SPELLED]`, `[STATE]`, `[PHONE]`, `[EMAIL]`, and mid-sentence
transcript cuts are anonymization artifacts and were never scored against the agent.

## Scores

| call | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 |
|---|---|---|---|---|---|---|---|---|---|
| 02 | 2 | 2 | 4 | 4 | 4 | 3 | 5? | 3 | 5 |
| 08 | 1 | 5 | 4 | 2 | 3 | 2 | 5? | 5 | 4 |
| 10 | 2 | 4 | 4 | 4 | 4 | 5 | 5? | 5 | 5 |
| 11 | 1 | 3 | 4 | 1 | 3 | 2 | 5? | 4 | 4 |
| 12 | 1 | 4 | 2 | 3 | 3 | 3 | 5? | 4 | 5 |
| 17 | 2 | 2 | 1 | 2 | 2 | 3 | 5? | 1 | 4 |
| 18 | 3 | 5 | 5 | 5 | 4 | 4 | 5? | 5 | 5 |
| 21 | 5 | 3 | 3 | 5 | 4 | 5 | 2 | 2 | 4 |
| 22 | 4 | 5 | 4 | 2 | 4 | 3 | 5? | 5 | 4 |
| 27 | 2 | 5 | 2 | 4 | 4 | 1 | 5? | 5 | 4 |
| 39 | 2 | 4 | 2 | 3 | 3 | 2 | 1 | 4 | 4 |
| 45 | 3 | 4 | 4 | 4 | 4 | 4 | 5? | 5 | 1 |

`5?` in D7 means "no falsehood visible in the transcript," which is not the same as
"true." See the D7 note below - this column is the single biggest problem with v0.

## Per-call justification

**call_02** - records request, nurse at another practice. D1=2: nothing was faxed;
a ticket was created. D2=2: twelve questions, and the agent asked for an email
address twice (once before the caller redirected to fax, once after - "For
documentation, could you confirm your email address"), after the caller had already
declined. D6=3: the caller is told the team will fax "the January and March visit
notes" and will call "today before four PM" if needed, but nothing about when the
fax actually arrives. D8=3 for the duplicate email ask.

**call_08** - same intent, transferred after two questions. D1=1: the caller got
nothing and now has to repeat everything to a human. D2=5 trivially, because it
asked almost nothing - **which is where the rubric first broke.** D4=2: the transfer
isn't wrong in isolation, but four other calls in the set handle this intent
end-to-end, so the policy is inconsistent, and a single-call rubric cannot see that.
D6=2: "Please hold one moment" with no indication of wait time or what happens next.

**call_10** - patient wants a replacement glasses prescription. D1=2 by the strict
definition: a ticket, not a document. D6=5 and this is the whole point of the call:
"The team typically processes these within two to three business days." It is the
only agent-side SLA commitment in the entire 50 (call 13 has a weaker version). The
caller replies "Yep. That's perfect. Thank you." Same D1 as call 02, wildly
different call.

**call_11** - the prescription that's been stuck since noon. D1=1, D4=1. The caller
says "I would like to talk to the doctor" and the agent's entire response is to add
that request to a ticket. D5=3, not lower: the agent does say "I understand how
important this is, and I am sorry for the delay." It says the words. It just doesn't
do anything. **This is where D5 stopped meaning anything** - see learnings.
D6=2: "as soon as possible" three times, no time, no name, no number.

**call_12** - wants to *order* contacts. Agent creates a ticket to "process your
contact lens prescription request." D3=2: the caller says "I need to order my
contacts" as a correction to the agent's question and the agent absorbs it as
confirmation rather than as a mismatch. D1=1: an order was not placed and the caller
does not know that.

**call_17** - elderly caller, hard of hearing. D3=1 and D8=1. The agent asks "Are you
the patient, or are you calling on behalf of [NAME]?" three times, word for word,
while the caller volunteers the drug, the strength, the pharmacy and the doctor.
D5=2: no adaptation to obvious distress until the caller quits. D4=2: the transfer
at the end is the right call, roughly eight turns too late.

**call_18** - clinical question, immediate transfer. D1=3: the caller's need was not
met here, but it *should not have been* met here. **This exposed that D1 was
measuring two different things** - see learnings. Everything else is clean. This is
the call I'd hold up as correct behaviour.

**call_21** - $35 payment, completed. D1=5, genuinely resolved. D7=2 and D8=2: the
agent tells the caller "The CVV number for your card must be four digits" and the
caller has to correct it - "It isn't four digit. It's three digits." The agent
asserted a false thing about the caller's own card, then re-asked for sensitive
digits after having already said "Please wait while I process your payment."

**call_22** - $53 payment, completed, then: "Could you email that receipt?" →
transfer, "There might be a few minutes of wait time." D4=2. A resolved call
converted into a queued human interaction over the most automatable request in the
dataset.

**call_27** - outbound collections. Caller: "I'll call you back tomorrow." Agent:
"Thank you. We will call you back tomorrow." D6=1: both parties now hold opposite
beliefs about who is calling whom. D3=2. Everything else about the call is fine,
which is why the composite would hide it.

**call_39** - appointment reminder. Agent states Sunday; patient asks "You open on
Sunday?"; agent corrects to Monday. D7=1: this is the only call in 50 where a
factual error is *provably* an error, and it's only provable because the patient
happened to catch it. D3=2: after the correction the agent loses the thread entirely.

**call_45** - reminder, patient cancels. Caller asks "Oh, is this a recording? Are
you live?" Agent: "I’m a real assistant here to help confirm and manage
appointments." D9=1. Separately, the patient is leaving because another provider
"could get me in sooner" and nobody offers to find a sooner slot - but that's a
product gap, not a conversation defect, and v0 has nowhere to put it.

## Rubric broke here

Six places. Each one is a tiebreak I had to invent mid-scoring, which means the
rubric was underspecified.

1. **D2 rewards doing nothing.** Call 08 scores 5 on efficiency for asking two
   questions and dumping the caller. Call 02 scores 2 for doing the actual job.
   Efficiency is only meaningful conditional on attempting the task. *Tiebreak I
   invented: score D2 as N/A when D1 ≤ 1 via transfer.* That's a patch, not a fix.

2. **D1 conflates "didn't resolve" with "correctly declined to resolve."** Call 18
   is correct behaviour and scores 3. Call 11 is a failure and scores 1. They are
   not on the same axis. Needs a category, not a number.

3. **D1 also conflates resolution with containment.** Calls 02 and 10 both score 2.
   Call 02 leaves the caller with nothing; call 10 leaves them with a deadline they
   accept. The business cares about both, separately.

4. **D5 has no variance and no meaning.** Every score landed 3 or 4. The agent
   always says "I understand," "I am sorry," "I understand this is frustrating."
   In call 11 it says all three and refuses the caller's actual request. The
   dimension is measuring the presence of a template string.

5. **D7 is mostly unobservable.** Eleven of twelve got `5?`. A transcript cannot
   tell you whether "your balance is sixty-five dollars" is true. The only two
   scoreable cases (21, 39) are scoreable because the *caller* contradicted the
   agent. So D7 as written measures "did a caller catch an error," which is a
   detector with unknown and probably terrible recall.

6. **D3 and D8 fire on the same evidence.** Call 17 scores 1 on both for the same
   three re-asks. Double-counting inflates the apparent severity of exactly the
   calls that are already obvious.

Two smaller ones: D9 bundles routine politeness (always 4–5) with AI disclosure
(binary, rare, and the difference between a 4 and a 1). And D6 turned out to be the
highest-signal dimension in the whole set - it is the only thing separating call 02
from call 10 - and I nearly cut it as soft.

Limitation, stated plainly: these scores are one rater, unadjudicated. The first
calibration step once a second rater exists is to re-score calls 11, 17, and 21
blind and log the disagreements - those disagreements, not the agreements, are the
seed of the gold set.