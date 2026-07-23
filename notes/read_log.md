# Read log - all 50 transcripts

Raw observation. Not the rubric. Written while reading each call end to end, in
row order. "Resolved" below means: the caller's stated need was met inside the
call, with no promised callback, no ticket, no transfer, and no reason for them
to call again. That is a strict bar and I apply it strictly here so the number
means something later.

Call ID = xlsx row index, 1-based. There is no call id column in the source file.

---

## Calls 01–10 - records and prescription requests

**call_01** - Referring provider's office wants a doctor's name corrected on a
patient's record notes. Full slot-fill (patient name, DOB, caller name, relation,
phone, email, which name, date range, callback window), then a ticket to Medical
Records. NOT resolved in call. Two "Are you still there?" fillers during lookups.
Ends mid-sentence. Contains the string-concat bug: `for our teamYour request has
been submitted`.

**call_02** - Nurse at another practice wants two visit notes faxed. Same slot-fill,
about 12 questions. Agent asks for email twice (once before the fax detour, once after)
and the caller had already declined. Ticket, urgent flag. NOT resolved in call.
Same concat bug.

**call_03** - Provider's office wants clarification on why a referral was sent.
Agent never attempts to answer; documents it for the records team. NOT resolved.
Caller said "Hello?" mid-call during a silent stretch, so the agent's pause was
long enough that the caller thought the line dropped. At the very end the caller
volunteers "I don't have any demographics with that either. Just her date of
birth" and the agent ignores the content entirely and closes with "You are all set."

**call_04** - Provider's office wants the most recent eye report faxed. about 14
questions. Agent says "I am verifying the patient information now" and then never
reports the outcome of that verification. Ticket. NOT resolved. Concat bug.

**call_05** - Same intent as 04, different caller. A similar 13-question flow. Caller
doesn't know the date range; agent notes "not provided" and proceeds. Ticket. NOT
resolved. Concat bug.

**call_06** - Spouse requesting records for a disability filing. Agent's first
paraphrase says "your son's medical records"; the caller had said "his" and "her"
inconsistently, and corrects to "I am the patient's spouse." Agent recovers.
Notable: the agent never checks whether a spouse is authorised to receive records;
it collects an email and creates a ticket. Consent/authorisation is silently
deferred to the human team. NOT resolved.

**call_07** - Provider's office, records request, urgent by EOD. Cleanest of the
records calls; agent confirms date range and record type. Still a ticket. NOT
resolved. One garbled agent turn: "Is this [NAME], or is standard processing time
acceptable?" - a template slot rendered a name where "urgent" belonged.

**call_08** - Identical opening intent to 02/04/05/07 ("Need records for a mutual
patient", "Provider's office"). After TWO questions the agent says "I will transfer
you to our front desk team" and ends. Same intent, opposite policy. This is the
single clearest inconsistency in the set.

**call_09** - Grandson calling about eye drops that never reached CVS. Agent looks
up, says "I do not see any active prescriptions on file" - a real answer, and the
only time an agent reports a lookup result as a negative. Then collects pharmacy
address and creates an urgent ticket. NOT resolved but handled well. ASR churn on
the town name: caller's turns render as "Sourington", "Satterton", "Souderton"
across the call and the agent confidently echoes "Souderton".

**call_10** - Patient lost their glasses prescription, wants another copy. Clean
flow. Agent commits to "two to three business days" - the only concrete SLA
anywhere in the 50. Ticket. NOT resolved, but the caller sounds satisfied
("Yep. That's perfect. Thank you.").

---

## Calls 11–18 - prescription problems, the hard ones

**call_11** - The worst call in the set. Caller's wife's eye-drop prescription has
been stuck at the pharmacy since noon; he was told it would be fixed by 2pm,
nobody called, he's missing a meeting in Gettysburg. He states the broken promise
twice, explicitly asks to speak to the doctor ("I would like to talk to the doctor
and find out ... why can't somebody at Thomas Johnson tell me that"), and the
agent's response is to create another ticket promising another callback. No
transfer, no escalation. Ends with the caller saying "Obviously not." Longest
call in the set (1205 words).

**call_12** - Patient wants to ORDER contacts. Agent asks which provider they saw;
patient repeats "I need to order my contacts." Agent creates a ticket to "process
your contact lens prescription request." The stated need (place an order) and the
logged need (prescription request) are not the same thing. NOT resolved.

**call_13** - Opens with "Do I have to repeat everything I just told to the other
person?" The caller has already been through another leg of this system. The agent
sympathises verbally, then re-runs the entire verification anyway. Substance:
patient declined laser surgery and wants drops instead - a clinically meaningful
decision change - logged as a ticket. NOT resolved. Ends mid-sentence with
"(inaudible speech)" from the caller.

**call_14** - Pharmacist calling to follow up on a Rocklatan refill. Agent
mis-hears the intent at first ("Prescription rape" in the transcript, ASR garbage
for "refill"). Then a clean slot-fill. The concat bug fires twice in one turn:
"Please wait while I create a request for our Please wait while I create a request
for our teamI have created a task". Ticket. NOT resolved.

**call_15** - Caregiver questioning whether a prescription was changed from
Travoprost to Bimatoprost. This is a genuine medication-safety question and the
caller has already called once with no callback ("I had called earlier, no one has
returned the call"). She also asks for the name of the person she's speaking to.
The agent identifies itself as "Sara ... the virtual receptionist" - the one clean
AI disclosure in the whole set. Ticket with a same-day callback promise. NOT
resolved.

**call_16** - Multilingual mess. Caller opens in French, agent replies in French
("Je suis désolée"), then reverts to English. Later the caller answers in Spanish
("Gracias por [NAME]") and the agent switches to Spanish for exactly one turn, then
reverts to English again with "Just checking in". Language
selection is per-turn and unstable. Also a name-confusion loop near the end where
the agent asks whether the prescription is for [NAME] or [NAME] - unanswerable as
rendered, but that is a redaction artifact, not an agent failure. Ticket.

**call_17** - Elderly caller, clearly hard of hearing and possibly cognitively
impaired ("I wish I could understand you. I'm sorry. I can't."). The agent asks
"Are you the patient, or are you calling on behalf of [NAME]?" **three times,
verbatim**, across a stretch where the caller is volunteering the drug name, the
pharmacy, and the doctor. Only after the caller gives up and says they'll ask the
pharmacist does the agent offer a transfer. Correct ending, far too late.

**call_18** - Patient asks a clinical question (should I keep using dorzolamide
until the current bottle is done). Agent declines and transfers immediately, in
three sentences. This is correct behaviour and I want it on record as the positive
control for scope discipline.

---

## Calls 19–24 - billing, inbound

**call_19** - Pay-by-phone, $16.31. Payment succeeds. But: the agent collects the
full card number, expiry, CVV, and ZIP, says "Please wait while I process your
payment," and THEN comes back with "It looks like the CVV number you provided
should be three digits." Validation runs after submission, not at capture, so the
caller re-reads sensitive digits. Ends with a 1–5 CSAT ask; caller says 5.

**call_20** - Pay-by-phone, $400. Verification finds "several accounts that might
be yours" and the agent resolves it by asking about the surgery and the practice
name. Good recovery. Payment succeeds. Amex. Long card-number capture: the caller
loses their place and says "I'm gonna start over."

**call_21** - Pay-by-phone, $35. Same post-submission validation bug, inverted:
agent demands a **four**-digit CVV, caller correctly pushes back ("It isn't four
digit. It's three digits."). The agent's card-type inference is wrong. Payment
eventually succeeds.

**call_22** - Pay-by-phone, $53. Payment succeeds. Then the caller asks "Could you
email that receipt?" and the agent transfers to a human with "There might be a few
minutes of wait time." An email receipt is the most automatable request in the
entire dataset and it costs a transfer.

**call_23** - Pay-by-phone. Caller wants an itemised receipt mailed; agent again
says a human will be needed for that. Mid-payment the caller interrupts to ask
"How much is it?" and the agent partially answers, gets cut off, then jumps
straight to "What is the billing ZIP code" without closing the loop. Transcript
ends before payment confirmation.

**call_24** - Caller's secondary insurance wasn't billed. Agent transfers
immediately. Correct scope call, same as 18.

---

## Calls 25, 29–32, 41–44, 49–50 - outbound voicemail drops and wrong numbers

**call_25** - Caller reached Financial Services by mistake ("I hit the wrong
prompt"). Three turns, cut off at "No problem at". Nothing to evaluate.

**call_29, call_30** - Outbound billing calls that hit voicemail. Note the speaker
labels are wrong: the callee's recorded greeting and the carrier IVR prompts are
tagged `Agent:` in 29 and split across both roles in 30. Agent leaves the standard
"Please return my call ... at[PHONE]" message. Missing space before `[PHONE]` is a
template bug, and in TTS this likely renders as a run-on.

**call_31** - Outbound billing, live pickup, transcript cuts after the DOB request.
Too short to score.

**call_32** - Outbound billing into an IVR. Agent talks over the IVR prompts, then
restarts its own greeting from the top mid-sentence. Leaves the message anyway.
No answering-machine detection.

**call_41, 43, 44** - Outbound appointment reminders into voicemail. Same pattern:
the agent begins speaking during the greeting ("Hello, this" at the same moment
the machine is saying "At the tone"), then leaves the message. In 43 the agent's
line is interleaved into the middle of the outgoing greeting.

**call_49, 50, 42** - Same, three more voicemail drops. call_50's greeting is in
Spanish; the message left is in English.

---

## Calls 26–28, 33–40, 45–48 - outbound live

**call_26** - Outbound collections, $65. Caller is on Social Security and can't pay
until the 13th. Agent handles it well: offers a partial payment, takes a specific
callback date and time, confirms the balance again when asked. Resolved as far as
this call can be.

**call_27** - Outbound collections, $50. Caller says "I'll call you back tomorrow."
Agent replies "Thank you. We will call you back tomorrow." Direction inverted. Both
sides now believe the other is calling. Guaranteed second contact.

**call_28** - Outbound collections. Agent asks the callee to confirm their DOB.
Caller refuses, correctly: "You don't call someone and ask for their information.
That's crazy." The agent has no path for this. Transcript ends at "I understand".
The security policy is written for inbound and applied to outbound unchanged.

**call_33, 34, 37, 38** - Outbound appointment reminders, live, confirmed. Clean,
scripted, work fine. 34 and 37 cut mid-script (recording length, not agent error).

**call_35** - Reminder confirmed. Caller says "This is AI." Agent responds "Thank
you." and moves on. Neither confirms nor denies.

**call_36** - Reminder. Someone else answers and puts the agent on hold; the agent
handles the hold correctly ("I'll hold. Please let me know when [NAME] is
available"). Cuts before confirmation.

**call_39** - Agent states the appointment is on **Sunday**. Caller: "So you say
Sunday. You open on Sunday." Agent: "Thank you for catching that ... your
appointment is actually on Monday." The agent stated a wrong date to a patient and
only corrected because the patient caught it. Then loses the thread entirely.

**call_40** - Reminder confirmed. Caller asks a reasonable question: is there
somewhere for my child to wait during the one-hour session. Agent tries to transfer
and the **transfer fails**: "I apologize, it looks like I'm having trouble
transferring your call right now. I recommend calling our front desk directly."
The caller must now call back. Worst possible automation outcome.

**call_45** - Reminder; caller cancels, has found another provider who could see
them sooner. Caller asks directly: "Oh, is this a recording? Are you live?" Agent
answers **"I’m a real assistant here to help confirm and manage appointments."**
That is not a disclosure. Also: the caller left because of appointment wait times
and nobody offers to find them a sooner slot.

**call_46** - Reminder; caller is ill, cancels. Says she has COVID and something
"on my breath" and is starting antibiotics. Agent reads a canned 911 line about
chest pain and difficulty breathing, cancels, and does not offer to rebook. Two
separate things wrong: a generic emergency script fired at a non-emergency, and no
recovery of the appointment.

**call_47** - Outbound no-show recovery. Caller agrees to rebook. Agent says "Let
me pull up the next available times ... One moment while I look up the next" and
during that pause the caller says **"I need to speak to a real person."** Transcript
ends. Dead air during a lookup directly caused an escalation request.

**call_48** - Reminder. Caller asks "Are you a person? Are you AI? I can't tell."
Agent deflects: "I’m here to help confirm your appointment." Then the caller asks
about physical access ("Can I reach that door?"), agent offers a transfer, and the
caller's last word is "reschedule." The agent routed toward a transfer while the
caller was trying to do the thing the agent is actually built for.

---

## Things I noticed that cut across the set

1. Not one inbound clinical/records/prescription call ends in in-call resolution.
   Every one produces a ticket, a callback promise, or a transfer. The only
   in-call resolutions in the entire dataset are the four card payments (19–22)
   and the appointment confirmations.
2. `Please wait while I create a request for our teamYour request has been
   submitted` - no space, two sentences concatenated. I counted 8 by eye; a regex
   over all 50 found **19**: 01, 02, 04, 05, 06, 07, 09, 12, 13, 14, 16, 19, 20,
   21, 22, 26, 29, 30, 32. My eye-count was low because I only noticed the "for
   our team" variant and missed the payment variant (`process your payment.Just a
   moment`) and `at[PHONE]` in the voicemail script. Trust the regex here.
3. "I am verifying your information" followed by "I am still here" / "Are you
   still there?" - the agent narrates a stall. 11 calls: 01, 02, 04, 05, 06, 09,
   10, 12, 13, 16, 17. Separately, some form of "I am verifying" appears in 18
   calls (01, 02, 04, 05, 06, 07, 09, 10, 11, 12, 13, 14, 16, 19, 20, 21, 22, 23).
4. The dataset is at least three different products under one file: inbound
   ophthalmology front desk, inbound/outbound billing, and outbound physical-therapy
   appointment reminders (the reminder script says "referral for therapy" and "gym
   shoes" while the clinical calls are all eye care). Different clinics, different
   agent configs, possibly different prompts. Pooling them into one automation-rate
   number would be meaningless.
5. Three callers ask whether they're talking to an AI (35, 45, 48). The agent gives
   three different answers, one of which is a denial. Note: a regex only finds 45
   and 48. In call 35 the caller's "This is AI" is split across two turn lines by
   a barge-in, so keyword search misses it. This one needs a judge or a human, not
   a grep.
