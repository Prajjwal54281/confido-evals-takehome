# Confido Health - Evals/Data Lead take-home

## Read these three things first

**1. The sample is smaller than 50.** Nine of the 50 transcripts are outbound
voicemail drops where no human is ever reached (29, 30, 32, 41–44, 49, 50). Four cut
before any outcome (31, 34, 36, 37). One is a misdial (25). **Effective scoreable
n = 36.** Every rate in this submission states its denominator. Where a bucket has
three calls, I say three calls rather than a percentage.

**2. It isn't one product.** The outbound reminder script says "referral for
therapy," "wear comfortable clothing and gym shoes," one-hour sessions - physical
therapy. The inbound clinical calls are all ophthalmology: eye drops, glasses
prescriptions, retina specialists. Billing runs under a different agent name, Lucy
rather than Sara. That is at least three configurations, probably three clinics. A
pooled automation rate across them would describe nothing real, so every prevalence
figure here is scoped to its segment.

**3. Half of it is outbound.** Exactly 25 inbound and 25 outbound. That precision
means the sample was constructed, not drawn from production. Nothing here supports a
claim about Confido's real call mix.

## Two assumptions I made that the brief did not state

The brief asks for dimensions split into agent performance and patient experience.
It does not name "automation rate" as a business metric. I have treated agent
performance as a proxy for automation rate because that is the number a voice-AI
company reports, but that is my inference. If Confido's north star is different, the
dimensions survive and the weighting changes.

Second: I treat **containment and resolution as different things** and score them
separately. Calls 01–07 are fully contained - no human touched them - and produced
zero outcomes for the caller. Call 18 escalated immediately and is the best-handled
call in the set. Any single automation number that scores those the same way is
measuring cost, not performance. This split is the spine of the whole submission; if
you disagree with it, most of what follows reads differently.

## What's here

**Deliverables** (`deliverables/`)

| file | contents |
|---|---|
| `01_rubric.md` | 7 dimensions, 4 agent / 3 experience, plus 8 ruled-out metrics with reasons |
| `02_judge_prompts.md` | 6 copy-pasteable judge prompts, JSON schemas, confidence and audit-cadence table |
| `03_failure_patterns.md` | 6 patterns with call IDs, quoted evidence, mechanisms, fixes, ranking, devil's-advocate pass |
| `04_error_analysis.md` | the manual-scoring loop, including a before/after diff of the empathy judge |
| `05_video_script.md` | talking points for the optional video |

**Working notes** (`notes/`) - the evidence the deliverables rest on.

| file | contents |
|---|---|
| `read_log.md` | all 50 transcripts, read end to end, 2–4 lines each |
| `manual_scoring_v0.md` | 12 calls hand-scored against a rough v0, with a "rubric broke here" section |
| `v0_learnings.md` | what the manual round changed and why |
| `audio_protocol.md` | listening protocol and tally sheet for the 10 recordings |

**Data and scripts** (`data/`, `scripts/`)

| file | contents |
|---|---|
| `data/transcripts/call_01..50.txt` | one file per xlsx row |
| `data/index.csv` | mechanical per-call facts, no judgment |
| `data/intents.csv` | my hand-assigned intent labels, one row per call |
| `scripts/extract.py` | xlsx → text files |
| `scripts/index.py` | every regex used for a mechanical claim, commented |
| `scripts/audio_silence.py` | silence measurement on the wavs; no ASR |
| `scripts/transcribe.py` | faster-whisper ASR over the 10 wavs → `data/audio_transcripts/` |
| `scripts/verify.py` | end-to-end checks: scripts re-run, schemas parse, every quoted piece of evidence string-matches its cited source, numeric claims re-derive from data |

Reproduce with `python3 -m venv .venv && .venv/bin/pip install pandas openpyxl numpy`
then run the three scripts.

## Call IDs

**Call ID = the xlsx row index, 1-based, zero-padded.** The source file has one
column, `transcript_redacted`, and no identifier. These IDs are mine and exist only
inside this submission; they do not correspond to anything in Confido's systems.

## Audio

The 10 recordings were ASR-transcribed locally with faster-whisper
(`scripts/transcribe.py` → `data/audio_transcripts/*.json`, per-segment
timestamps). Findings are in `notes/audio_findings.md`. Three things to know:

1. **The ASR transcripts are a different artifact from the human-corrected xlsx
   transcripts** and are never pooled with them. Known mishears include drug,
   provider, and pharmacy names. Audio claims in the deliverables rest on
   conversational structure, not exact wording, and are cited by wav file id.
2. **The audio is a different agent population** - optometry, endocrinology,
   primary-care after-hours, GI, workers' comp, at least five more configurations
   beyond the three in the transcripts. It functions as an independent replication
   sample, and two failure patterns (P-1 escalation refusal, A-2 transfer failure)
   replicated in it.
3. **An earlier silence measurement was retracted.** Classifying every ≥2s gap by
   the preceding content showed the longest gaps follow PII requests - they are
   anonymization cuts, which the brief says not to penalise. Genuine agent stalls
   exist but are shorter. The retraction is documented in `notes/audio_findings.md`
   because catching it is exactly what the redaction-exclusion rule is for.

## What I'd do first with real production volume

1. **Log tool calls.** Every argument and every return value. Almost everything weak
   in the accuracy judge is a workaround for not having these. With them, call 39's
   wrong appointment date becomes a deterministic check instead of a lucky catch by
   an alert patient, and the lowest-confidence metric in the rubric becomes the
   highest.
2. **Instrument transfer success and failure.** Call 40's transfer failed outright.
   From one transcript I cannot tell whether that's a rare SIP fault or a 5%
   baseline, and nobody can prioritise it until it's counted.
3. **Add a caller identifier.** True first-call resolution is not computable here.
   Calls 13 and 15 both reveal a prior contact only because the caller mentioned it
   out loud. Repeat contacts are the automation metric that matters most and the one
   this dataset cannot see.
4. **Split the dashboards by agent configuration** before anyone reports a company
   number. Reminders, billing, and clinical intake have different ceilings and
   averaging them hides all three.
5. **Build the 60-call gold set.** Double-scored, adjudicated, stratified by intent
   and outcome. Everything in `02_judge_prompts.md` about κ and drift depends on it,
   and the 12 calls I scored here are a seed, not a gold set.

## Honest limitations

- One rater. Every manual score in `manual_scoring_v0.md` is mine and unadjudicated.
- The 12 manually scored calls were **deliberately enriched for failure** to stress
  the rubric. No rate should be computed from them.
- The judge prompts in `02_judge_prompts.md` have not been run against the data.
  They are designed from the manual round; their κ against human labels is unmeasured
  and I have not claimed otherwise anywhere in this submission.
- Intent labels in `data/intents.csv` are my judgment. Several are contestable - 
  call 03 in particular reads as either a records request or a clinical question
  depending on where you put the boundary.
- Six of my prevalence figures sit at or near the n=3 systemic threshold. The
  devil's-advocate section in `03_failure_patterns.md` argues against each of them.
