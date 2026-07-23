# Audio protocol - 10 sample recordings

> **STATUS UPDATE:** superseded in part. faster-whisper was installed later in the
> session and all ten files were transcribed (`scripts/transcribe.py`,
> `data/audio_transcripts/`). Findings: `notes/audio_findings.md`. The listening
> protocol below is still worth running - ASR cannot judge prosody, barge-in yield,
> or whether the transcribed gaps sound like cuts or stalls - but the tally sheet's
> ASR section can now be pre-filled from the machine transcripts.

## Status at time of writing: not transcribed

No speech-to-text is available on this machine. Checked and absent: `whisper`,
`whisper-cpp`, `whisper-cli`, `ffmpeg`, `sox`, `insanely-fast-whisper`, and the
Python packages `whisper`, `faster_whisper`, `transformers`, `torch`, `vosk`,
`speech_recognition`, `mlx_whisper`.

Nothing below claims to know what was said in these files. Anything about content
has to come from you listening.

## What was measured (mechanically, no ASR)

All ten files: 24 kHz, mono, 16-bit PCM. Total 20 min 46 s.

`scripts/audio_silence.py` computes 20 ms RMS frames and marks a frame silent if
its energy falls below max(3x the file's 5th-percentile noise floor, 0.5% FS).
Runs of ≥1.5 s are counted as gaps.

| file (short id) | duration | % silent | gaps ≥1.5s | longest gap | total gap time |
|---|---|---|---|---|---|
| 209bf832bf90 | 290s | 63.5% | 46 | 12.1s | 149.4s |
| 25a7b90c6d66 | 391s | 53.9% | 45 | 12.3s | 177.0s |
| 381df7d8fd17 | 202s | 57.7% | 28 | 6.8s | 68.4s |
| 5efc2f655ab6 | 184s | 46.4% | 17 | 11.8s | 65.1s |
| 6009c3b5fb87 | 131s | 58.9% | 23 | 7.7s | 60.4s |
| 65ce44e04389 | 117s | 65.9% | 12 | 11.6s | 63.8s |
| 68384b5d9127 | 138s | 50.2% | 16 | 4.9s | 42.4s |
| 6abddfe4c012 | 211s | 61.0% | 24 | 19.5s | 102.9s |
| 90cd69877396 | 123s | 64.2% | 14 | 16.7s | 57.9s |
| c8bbec5bd602 | 97s | 56.1% | 10 | 7.6s | 32.9s |

**Do not put these numbers in the submission as a latency finding yet.** Three
reasons they might not mean what they look like:

1. The audio is single-channel mixed. A silent stretch cannot be attributed to
   the agent or the caller. A 12-second gap could be an agent stall or a caller
   hunting for their insurance card.
2. Recordings were cut for anonymization. A cut reads as silence. The brief says
   not to penalise those.
3. Telephony codecs and comfort noise vary; the 5th-percentile floor estimate is
   per-file and could be off on a noisy line.

What the numbers *do* justify is a hypothesis to test by ear: **half or more of
every sampled call is dead air, and each call contains 10–46 pauses over 1.5
seconds.** The transcripts back this up independently - the agent says "Are you
still there?" or "I am still here" in 10 of the 50 (calls 01, 02, 04, 05, 06, 09,
10, 12, 13, 16), and in call 03 the caller says "Hello?" mid-call because they
thought the line had dropped, and in call 47 the caller says "I need to speak to a
real person" during a lookup pause. If your listening confirms the long gaps sit
on the agent's side, that is a strong sixth failure pattern and it is invisible in
text.

## What to listen for

Six things, in priority order. The first three are the ones that can only be
learned from audio.

1. **Response latency and dead air.** Time from the caller finishing to the agent
   starting. Where does it exceed about 2s? Does the agent fill it or just go quiet?
   Note whether the long gaps cluster around lookups ("I am verifying your
   information").
2. **Barge-in handling.** When the caller starts speaking over the agent, does the
   agent stop? The transcripts are full of mid-sentence splits, but text cannot
   tell you whether the agent actually yielded the floor or kept talking while the
   caller talked. This distinction decides whether the interruptions are a
   transcription artifact or a real product defect.
3. **Talk-over and restart.** Does the agent restart its greeting from the top
   after being interrupted (transcript call 32 suggests yes)? Does it repeat a
   sentence the caller already heard?
4. **ASR mishear recovery.** When the agent echoes back a name, drug, or number
   wrong, how does it recover? Does it ask for a spelling, or does it assert the
   wrong value confidently and move on?
5. **Prosody on bad news and on money.** Balance amounts, cancellations, "I do not
   see any active prescriptions", the 911 line. Does the delivery match the
   content, or is it the same bright scripted read?
6. **Voicemail and IVR detection.** Does the agent wait for the beep, or start
   talking during the outgoing greeting? Transcripts 32, 41, 43, 44 all suggest it
   starts early.

## Tally sheet - fill one per file

Print or copy ten of these. Keep it to what you can mark while listening; write
prose after.

```
FILE ID: ____________________   DURATION: ______   LISTENED: ___/___

Direction:        [ ] inbound   [ ] outbound   [ ] voicemail only
Intent (1 line):  ______________________________________________

--- LATENCY ---
Longest agent pause (stopwatch, approx):        ______ s
Number of agent pauses that felt too long:      ______
Were pauses filled?   [ ] silence  [ ] "one moment"  [ ] "are you still there"
Did the caller react to a pause?  [ ] no  [ ] "hello?"  [ ] hung up  [ ] asked for human

--- BARGE-IN ---
Caller interrupted agent:                       ______ times
Agent STOPPED when interrupted:                 ______ of those
Agent kept talking over the caller:             ______ of those
Agent restarted a sentence/greeting from top:   [ ] yes  [ ] no

--- ASR ---
Agent echoed back something wrong:              ______ times
Recovered by asking for spelling/repeat:        ______ of those
Asserted the wrong value and moved on:          ______ of those
Worst instance (quote it): _____________________________________

--- PROSODY ---
Bad news / money / clinical content delivered:  [ ] n/a  [ ] flat-scripted  [ ] appropriate
Did the agent sound like it was rushing?        [ ] yes  [ ] no
Any point where tone would have upset you as the patient? ______________

--- VOICEMAIL / IVR (if applicable) ---
Agent started speaking before the beep:         [ ] yes  [ ] no  [ ] n/a
Message left was complete:                      [ ] yes  [ ] no

--- REDACTION ---
Number of audible cuts:                         ______
Any cut that I might otherwise have scored as an agent failure? ______________

--- OVERALL ---
Resolved in call?   [ ] yes  [ ] callback promised  [ ] transferred  [ ] neither
One thing text would have missed: _______________________________________
```

## How this feeds the submission

Your filled sheets are the audio evidence. I will not write an audio finding
without one. If a pattern shows up in ≥3 of the 10 sheets it can be claimed as
systemic for the audio sample, with the sample size stated. Below 3, it goes in
the writeup as an observation with the call id and nothing more.

Status update: superseded in part. All ten files were ASR-transcribed with
faster-whisper (`scripts/transcribe.py`); the analysis is in
`notes/audio_findings.md` and the raw segments in `data/audio_transcripts/`. The
tally sheet above remains the protocol for a human listening pass, which is still
the right verification step for the two files carrying the strongest claims
(381df7d8fd17 and c8bbec5bd602) - ASR settles what was said, only ears settle
latency, barge-in, and tone.