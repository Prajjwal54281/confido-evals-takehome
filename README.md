# Confido Health - Evals/Data Lead take-home

Evaluation design for an AI voice agent handling patient calls: a scoring rubric,
LLM-as-judge prompts with schemas and an audit plan, the error-analysis loop that
produced them, and six evidenced failure patterns.

**Start here: [deliverables/00_README.md](deliverables/00_README.md)** - it states
the sample-size caveats and the two framing assumptions everything else depends on.

| | |
|---|---|
| [deliverables/](deliverables/) | the submission: rubric, judge prompts, error analysis, failure patterns, video notes |
| [notes/](notes/) | working evidence: full read log of all 50 transcripts, manual scoring round, audio findings |
| [data/](data/) | per-call transcripts, mechanical index, intent labels, ASR output, judge dry-run results |
| [scripts/](scripts/) | the pipeline, plus `verify.py` - 100+ checks that every quoted claim string-matches its source |

Reproduce:

```bash
python3 -m venv .venv && .venv/bin/pip install pandas openpyxl numpy faster-whisper
.venv/bin/python scripts/extract.py && .venv/bin/python scripts/index.py
.venv/bin/python scripts/verify.py   # exits 0 only if every claim traces
```

Method note: LLMs were used as labor throughout - transcription, indexing,
cross-checking, drafting - per the brief's encouragement. Every factual claim is
traceable to a call ID and machine-verified; the judgment calls and their
tradeoffs are argued in place, most explicitly in the rubric's "Ruled out"
section and the failure patterns' devil's-advocate pass.
