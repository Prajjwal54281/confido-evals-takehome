# Audio findings - 10 recordings, ASR-transcribed

## Provenance and what this is worth

Transcribed locally with faster-whisper (`small`, int8, VAD-filtered, beam 5) via
`scripts/transcribe.py`. No ffmpeg on this machine, so the wavs are read straight
with the stdlib `wave` module and resampled 24k→16k in numpy. Raw output is in
`data/audio_transcripts/*.json` with per-segment timestamps.

**Three caveats before any of this is quoted.**

1. **This is machine transcription, not the human-corrected transcripts in the
   xlsx.** The two artifacts must never be pooled. Visible ASR errors in this batch:
   "Eduling" for "Scheduling", "Big Nuh" for an insurance carrier name, "Walgreens
   Kidney Name" for a pharmacy, "Dr. Maddie" and "Dr. Masi" for the same name,
   "Amberle" for a drug. Anything resting on an exact word is unsafe. Everything
   below rests on structure - who asked what, how many times, what happened next.
2. **Single-channel mixed audio. No diarization.** Speaker attribution below is mine,
   read off content and the agents' heavily scripted phrasing. It is reliable for
   the agent's lines and less so for short caller turns.
3. **n=10.** Nothing here is a rate.

## The headline: this is a different agent population

The audio sample is not the transcript sample with sound attached. It is a
different, larger set of products.

| file | agent | clinic signature | what it does |
|---|---|---|---|
| 209bf832bf90 | "Sarah, a virtual assistant" | after-hours line, PCP | prescription refill intake |
| 25a7b90c6d66 | "Robin, a virtual assistant" | Bridgewater, optometry | **books an appointment end to end** |
| 381df7d8fd17 | "Sarah, a virtual assistant" | after-hours, primary care | urinary symptom triage |
| 5efc2f655ab6 | "Robin, a virtual assistant" | ophthalmology | urgent-visit callback request |
| 6009c3b5fb87 | "Sarah" | endocrinology, Gilbert office | scheduling, record lookup |
| 6abddfe4c012 | "Sarah" | endocrinology, Mesa office | scheduling → lab callback |
| 65ce44e04389 | "Sara" | IVR front-end | doctor-to-doctor peer-to-peer routing |
| 68384b5d9127 | "Sarah" | Oakland, workers' comp | **reads back appointment history** |
| 90cd69877396 | unnamed | unknown | medication refill → failed transfer |
| c8bbec5bd602 | Spanish-language IVR + agent | GI (endoscopy/colonoscopy) | scheduling |

Specialties visible: optometry, ophthalmology, endocrinology (diabetes, thyroid
biopsy), primary care, gastroenterology, workers' compensation. Two files
(6009c3b5fb87 and 6abddfe4c012) are clearly the same configuration - identical
script down to "regular follow-up, a diabetes check-in, or something specific like a
thyroid biopsy."

Combined with the three configurations visible in the transcripts, Confido is
running **at least eight distinct agent configurations** across this data. Any
single company-wide quality number is an average over eight different products.

---

## Correction 1 - my silence measurement was mostly measuring the anonymizer

In `audio_protocol.md` I reported 46–66% silence and gaps up to 19.5s, and flagged
that I could not attribute them. Now that the content is transcribed, I can.

Classifying every gap ≥2.0s by what the agent said immediately before it:

| cause | count |
|---|---|
| follows a request for PII (name, DOB, member ID, subscriber ID, phone, address) - **redaction cut** | 18 |
| follows "one moment" / "please wait" / "let me check" - **genuine tool stall** | 8 |
| other | 51 |

The longest gaps are almost all redaction: 19.7s after "And what is your member ID?"
(6abddfe4c012), 12.6s after "confirm your full name and the best callback number"
(same file), 11.1s after "provide your first and last name, spelling both out for me"
(25a7b90c6d66), 6.1s after "Subscriber ID."

**The brief said not to penalise anonymization cuts, and a naive latency metric built
on this audio would do exactly that.** Retract the implied latency finding. Genuine
agent stalls in this sample are modest: 7.9s (5efc2f655ab6, after the caller finishes
describing a corneal scratch, before "Please wait while I create a callback request")
and ~5s on record lookups.

The one long gap that is *not* redaction and *not* a normal stall is in
209bf832bf90 and it's a real defect - see P-3 below.

---

## Correction 2 - in-call resolution exists, in a config the transcripts don't contain

My A-1 pattern says no inbound clinical or records call resolves in-call, across
15 of 18. That holds for the transcript sample. **It does not generalise**, and the
audio proves it.

**25a7b90c6d66** books a real appointment, end to end, in one call:

> **Agent:** Please wait while I book your appointment. Your appointment is scheduled
> with Dr. Caroline Bertler on Wednesday May 20th at 12:30pm. [...] We will send you
> a text confirming your appointment details.

It also does the thing A-3 says nobody does - it summarises the whole booking back
to the caller for confirmation before committing, and it discloses a cost up front
("This costs $45 and insurance may not cover it but we will verify your coverage
before your visit").

**68384b5d9127** retrieves and reads back real appointment history:

> **Agent:** I found the patient's chart. [...] does not have any upcoming
> appointments scheduled at the Oakland location. For past visits, here are the three
> most recent. March 19th 2026 with Edith Maraz, February 19th 2026 [...]

**Why this matters more than the original finding.** The correct framing is not "the
agent can't resolve." It's that **resolution capability is shipped in some
configurations and absent in the ones handling records and prescriptions.** That
turns A-1 from a hard integration project into a question about why the scheduling
config has EHR write access and the records config doesn't. Much cheaper question,
much better week-one conversation.

---

## Correction 3 - proactive AI disclosure is already shipped somewhere

P-2 (Identity Evasion) rests on transcript calls 35, 45, 48, where the agent
deflects or denies being an AI. Call 45 denies outright.

**Every after-hours and Robin-config call in the audio discloses proactively, in the
greeting, unprompted:**

> **209bf832bf90:** "You are speaking with Sarah, a virtual assistant on a recorded
> line."
> **381df7d8fd17:** "You are speaking with Sarah, a virtual assistant on a recorded
> line."
> **25a7b90c6d66:** "This call is being recorded for quality assurance. Thank you for
> calling Bridgewater. I'm Robin, a virtual assistant."
> **5efc2f655ab6:** "I am Robin, a virtual assistant."

The fix I proposed for P-2 was "add a disclosure line to the prompt." The audio shows
**the line already exists in Confido's own prompt library and is simply not deployed
to the configs that denied it.** That is a stronger and cheaper recommendation:
this is a config-consistency problem, not a writing problem.

---

## Corroborations - patterns that now hold across two independent samples

### P-1 (Escalation Refused Under Distress) - confirmed twice, independently

This was my thinnest pattern at n=3, all from transcripts. The audio adds two more
from a completely separate sample, and one of them is worse than anything in the
transcripts.

**90cd69877396** - the caller's *opening statement* is a request for a human:

> **Caller:** I need to speak to a live person.
> **Agent:** I can often help right away. Is this about an appointment, medications,
> or something else?

The agent deflects, runs the caller through medication intake, fails to catch the
drug name three times, and then the transfer fails anyway (below). The caller asked
for a human at second 13.7 and never got one.

**c8bbec5bd602** - Spanish-language call. The caller asks for a human **three times**
and is deflected every time:

> **Caller:** Hablar con representante, por favor. *(Speak to a representative, please.)*
> **Agent:** Con gusto le ayudo. Puedo programar una cita de paciente nuevo o de
> seguimiento, cancelar o reprogramar una cita existente o ayudar con un resurtido de
> receta. ¿En qué le puedo ayudar?
> **Caller:** No, para hablar con un representante, por favor.
> **Agent:** Entiendo. Puedo ayudarle con citas, resurtidos, o conectarle con el
> departamento correcto. ¿En qué le puedo ayudar?
> **Caller:** Por favor, si me puede comunicar con un operador.

The recording ends there. Three explicit escalation requests, three menu re-reads.
The agent's second reply even says it can connect the caller to the right department
and then asks the menu question again instead of doing it.

**P-1 now stands at 5 unambiguous instances across two independent samples.** It was
my weakest pattern and it is now my best-evidenced one. I would promote it to #1 in
the ranking.

### A-2 (Transfer Failure) - second independent instance

Transcript call 40 was n=1 on hard transfer failure and I flagged that I couldn't
tell a one-off SIP fault from a baseline. **90cd69877396 is a second occurrence in a
different agent config:**

> **Agent:** I will connect you with our staff so they can assist you directly with
> your medication request. It looks like I was not able to connect you to a staff
> member just... *(recording ends there)*

Two failures in two small samples from different configurations. The recommendation
to instrument transfer success/failure as first-class telemetry moves from
"reasonable" to "urgent."

### P-3 (Comprehension Breakdown Without Adaptation) - confirmed three ways

**209bf832bf90** - last-name spelling fails twice and never recovers cleanly:

> **Agent:** Just to confirm your last name is spelled - is that correct?
> **Caller:** No.
> **Agent:** Can you please spell your last name for me? [...] So your last name is - 
> is that correct?
> **Caller:** No.
> **Agent:** I apologize for the confusion. Could you please spell your last name one
> more time slowly?

Same file, the non-redaction 12.2-second gap: the agent reads out a seven-name
provider list, gets cut off mid-name ("...Cassidy Abrahamson, or Thea"), goes silent
for 12.2 seconds, then **re-reads the entire list from the top** with slightly
different ASR renderings of the same names. That is a barge-in or timeout failure
followed by a full restart, and it is exactly the class of defect that is invisible
in a text transcript.

**90cd69877396** - drug name asked three times, then abandons:

> **Agent:** What is the name and dosage of the medication you need a refill for?
> **Caller:** Amberle.
> **Agent:** Could you please tell me the name and dosage of the medication you would
> like to refill?
> [...]
> **Agent:** I did not catch that. Could you please repeat the name and dosage of the
> medication you need a refill.

**381df7d8fd17** - the triage question is asked twice with the caller's answer
already given, which in a symptom-screening context is worse than annoying:

> **Agent:** Are you experiencing any severe pain, fever, difficulty urinating or any
> other concerning symptoms right now?
> **Caller:** Just some burning when I urinate.
> **Agent:** Thank you for letting me know. Just to be sure, are you experiencing any
> severe pain, fever, nausea, vomiting, or difficulty passing urine at this time?

The caller reported dysuria. The agent's re-ask lists "difficulty passing urine" as
if it hadn't been answered, then concludes "since you are not experiencing severe
symptoms." **The agent classified a reported symptom as no-symptom.** This is the
most clinically consequential thing in either sample and it deserves its own line in
the writeup.

---

## New - only visible in audio

### Greeting and IVR loops

**65ce44e04389** plays its greeting **three times** before proceeding - at 0.1s, 7.7s,
and 24.6s - cycling "for English press one / para español presione dos" twice before
finally reaching "Can you please tell me who you are calling as?" at 43 seconds. The
caller waited 43 seconds to say anything.

Same file, the agent asks "Are you still there?" **twice** during its own processing,
and then repeats its entire peer-to-peer routing statement verbatim:

> **Agent:** ...I will connect you with our peer-to-peer team now. Are you still there?
> **Caller:** Yes, I'm here.
> **Agent:** You are calling to set up a doctor-to-doctor call with Dr. Maddie. I will
> connect you with our peer-to-peer team now.

**5efc2f655ab6** opens with "This call is being recorded for quality assurance" twice
in a row. **68384b5d9127** re-plays its greeting at 17.1s after the IVR prompts.

Four of ten recordings contain a greeting or statement replay. In text this is
invisible or looks like a transcription artifact; in audio it is 20–40 seconds of
the caller's life.

### One genuinely good call worth studying

**25a7b90c6d66** does something no call in either sample does. The caller says they
need "immediate attention," the agent starts an urgent-callback flow, and then the
caller explains they actually want contact lens replacements. The agent
**reclassifies mid-call**:

> **Agent:** Thanks for explaining. Contact lens prescription renewals or replacements
> - you will need a routine eye exam rather than a medical emergency appointment.
> Would you like to schedule a routine eye exam for contact lenses as a new patient?

It caught a caller's mis-triage, corrected it, and completed the booking. That is the
top anchor for Responsive Acknowledgment (B2) and a better few-shot example than the
transcript call 20 I used in the judge prompt.

---

## What changes in the deliverables

| item | change |
|---|---|
| P-1 Escalation Refused | n=3 → **n=5 across two independent samples**; promote to rank #1 |
| A-2 Transfer Failure | hard failure n=1 → **n=2, different configs**; instrumentation is now urgent |
| P-3 Comprehension | add the triage mis-classification in 381df7d8fd17 as the severity case |
| A-1 Intake-Only | **narrowed** - resolution is shipped in the scheduling config; reframe as config inconsistency |
| P-2 Identity Evasion | **fix simplified** - the disclosure line already exists in other configs |
| latency / silence | **retracted** as a finding; mostly redaction cuts |
| new candidate | greeting/statement replay, 4 of 10 recordings |
| B2 few-shot | swap transcript call 20 for 25a7b90c6d66's mid-call reclassification |

Verification note on the triage claim: the quote is whisper output, checkable
against `data/audio_transcripts/381df7d8fd17.json` segments at 50.1s ("Are you
experiencing any severe pain, fever, difficulty urinating or any other concerning
symptoms right now?"), 56.9s ("Just some burning when I urinate."), 63.0s (the
re-ask), and 74.4s ("Since you are not experiencing severe symptoms"). The segment
sequence supports the reading; a human listen is the remaining check, and the
claim is presented with its ASR provenance stated wherever it appears.

Decision: greeting-replay stays folded into P-3 as audio-only corroborating
evidence rather than becoming a seventh pattern. It is well-attested (4 of 10
recordings) but audio-only, spread across different configs, and the transcript
sample cannot corroborate it - promoting it would break the rule that a pattern
needs evidence in the sample where it is claimed.