# Video talking points - one take, ~5 minutes

Bullets to riff from. Do not read these aloud. If you read them it will sound
read, and the brief is explicit that they're screening for unedited LLM output.

Have open on screen: `notes/read_log.md`, `data/index.csv`, and call_11.txt.

---

## 0:00–0:40 - Open with the thing that reframes the whole task

- Don't open with methodology. Open with: half this dataset isn't what the prompt
  said it was.
- 25 inbound, 25 outbound. Exactly. That's constructed, not sampled.
- 9 of 50 never reach a human at all - voicemail drops. Automation rate is undefined
  for those.
- At least three different products in one file: outbound physical-therapy reminders
  ("gym shoes," "referral for therapy"), inbound ophthalmology, and a billing agent
  running under a different name - Lucy, not Sara.
- So the first real deliverable was a denominator. Effective scoreable n = 36.
- Land it: *any single automation-rate number over these 50 calls describes nothing.*

## 0:40–1:30 - The approach, fast

- Read all 50 by hand before writing one rubric dimension. Say why: if I'd written
  the rubric first I'd have written the generic voice-AI rubric - resolution,
  empathy, accuracy, tone - and four of those measure nothing on this data.
- Then a mechanical index over all 50, so no prevalence claim rests on memory.
- Then 12 calls scored by hand against a rough 9-dimension v0, picked as contrast
  pairs inside the same intent.
- v0 broke in five places. Those breaks are the judge prompts.
- (Unscripted beat: one concrete sentence about a time you ran this kind of
  manual-scoring loop in your own work. Name the system and what broke. This is the
  spot where your experience makes it yours and not a method description.)

## 1:30–2:30 - Why these evals: the split that carries everything

- The headline finding: **not one inbound clinical or records call resolves in-call.**
  15 of 18 end in a ticket. The other three transfer.
- But those 15 are 100% contained. No human touched the call.
- So containment says the agent is perfect and resolution says it does nothing.
  Same 15 calls.
- That's why outcome is a **category** in my rubric, not a score.
- Then the counter-argument, out loud, because it's the strongest objection:
  maybe it's *supposed* to be an intake bot. You can't fax medical records on an
  AI's authority.
- Resolve it with the contrast pair - this is the moment of the video:
  - Call 02: fourteen questions, ticket, caller never learns when the fax arrives.
  - Call 10: same outcome type, one extra sentence - "the team typically processes
    these within two to three business days" - and the caller says *"Yep. That's
    perfect."*
  - Only 2 of 50 calls contain an agent-side time commitment. **Zero of 50 give a
    reference number.**
- So the finding isn't "it fails to resolve." It's "it never closes the loop." That
  reframe is the whole submission.

## 2:30–3:00 - Two rubric decisions worth defending

- **Empathy is cut.** Zero variance. The agent says "I understand," "I'm sorry," "I
  understand this is frustrating" in nearly every call - including call 11, where
  it says all three and refuses the caller's explicit request to speak to a doctor.
  A dimension scoring that call a 3 on empathy is measuring whether a template fired.
- Replaced with **Responsive Acknowledgment**: did the agent's *next action* change
  because of what the caller said. Empathy language is now evidence of *failure* at
  the bottom of the scale.
- **Accuracy abstains by default.** A transcript can't tell you whether "your balance
  is sixty-five dollars" is true. Only 2 of 50 were checkable, and both only because
  the caller contradicted the agent. So the judge is built to decline, and abstain
  rate is a reported number, not a hidden one.
- If you only have time for one here, do the empathy one.

## 3:00–4:15 - The six patterns, and why I ranked them the way I did

Don't list all six. Pick three and be specific.

- **Play call 11.** Caller's wife's prescription stuck since noon, a callback was
  promised and never came, he's missing a meeting. He says *"I would like to talk to
  the doctor."* The agent's response is to create another ticket promising another
  callback. His last words: *"Obviously not."*
  - That's escalation-refused-under-distress. And note the automation cost of
    transferring him was **zero** - the call ended in a ticket anyway.
- **Call 45**, one line, high impact: caller asks "Is this a recording? Are you
  live?" Agent: *"I’m a real assistant here to help."* Three callers asked whether
  they were talking to an AI. Three different answers, one of them false. 3 out of
  50 is a low base rate - I keep it because the fix is one paragraph of prompt and
  the downside is regulatory.
- **Call 40** for the automation side: transfer attempted, transfer **failed**,
  agent says "I recommend calling our front desk directly." That's the worst outcome
  in the taxonomy - the caller's work is pushed back onto the caller as a new inbound
  call, and it scores as contained.
- The ranking, and the tradeoff you're making: unbounded-commitment is #1 despite
  intake-only-terminus having higher prevalence, because #1 is a prompt change and a
  config table and the other is a quarter of integration work. Say the risk out loud:
  shipping the cheap conversational fixes first makes the agent *feel* better while
  it still resolves nothing, and that can buy cover for never doing the integration.

## 4:15–5:00 - Close on limits, not on strengths

- Say the sample sizes plainly. rx_problem is 3 calls. noshow_recovery is 1. No
  per-intent rate in this submission means anything and I've said so everywhere it
  comes up.
- One thing I got wrong: I counted a template bug in 8 calls by eye. Regex found 19.
  Then the reverse - regex missed call 35's "This is AI" because a barge-in split it
  across two turn lines, and only reading caught it. Both directions are designed
  into which judges get pre-filtered and which read the full transcript.
- The audio: transcribed it locally with whisper, and it flipped three of my own
  conclusions. Tell this as the self-correction story, it's the strongest 30 seconds
  available: (1) my silence measurement looked like a latency finding until gap
  classification showed the longest gaps follow PII requests - anonymization cuts,
  exactly what the brief said not to penalise. Retracted. (2) My weakest pattern - 
  escalation refused - replicated twice in the audio, different configs, including a
  Spanish-language caller refused three times. Promoted to #1. (3) My biggest
  pattern - nothing resolves in-call - turned out to be config-scoped: the
  scheduling agent in the audio books an appointment end to end. The finding
  narrowed from "build integration" to "why don't the records configs have what the
  scheduling config has."
- If there is time before recording, play 381df7d8fd17 (50–75s) and c8bbec5bd602
  once through - every audio quote is machine transcription and worth one ear-check.
- First thing with production volume: tool-call logs. Everything weak in my accuracy
  judge is a workaround for not having them. With them, call 39's wrong appointment
  date is a deterministic check instead of a lucky catch by an alert patient.

---

## Delivery notes

- Five minutes is short. The reframe (0:00–0:40) and call 11 (3:00) are the two
  things that must land. Everything else is cuttable live.
- One take, no edits, per the brief. Stumbling is fine. Sounding scripted is not.
- Don't apologise for sample size - state it as a constraint you handled, which you
  did, by scoping every denominator.
- Screen-share `read_log.md` while you talk. It is evidence the 50 transcripts were
  actually read - the claim hardest to fake and the one most worth making visible.
