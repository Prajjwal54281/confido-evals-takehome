"""Dry run of three judge prompts against six calls.

The judgments encoded here were produced by executing the prompts in
deliverables/02_judge_prompts.md with an LLM against the numbered transcripts,
then transcribed into this generator. The generator's job is mechanical
integrity: every evidence quote is extracted as a verbatim substring of the
cited turn (never retyped), so scripts/verify.py can hold the outputs to the
same string-match standard as every other quote in the submission.

Calls chosen to exercise the schema's edges, not to flatter it:
  J1 (outcome+escalation): 11 deferred/1, 18 transferred_warm/4,
                           10 committed/4, 40 transferred_failed/1
  J3 (grounded accuracy):  39 score 1 (caller-caught), 26 ABSTAIN (balance
                           claims are unverifiable; the prompt's own example)
  J5 (responsive ack):     11 score 1 (empathy language, request denied),
                           26 score 4 (plan changed on caller's constraint)

Four of the six (10, 11, 18, 39) overlap the manually scored set for an
agreement check; 26 and 40 are outside it, included to exercise the abstain
path and the transferred_failed category.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
TDIR = ROOT / "data" / "transcripts"
OUT = ROOT / "data" / "judge_dryrun"

TURN_RE = re.compile(r"^(Agent|User):\s?(.*)$")


def turns(call_id):
    out = []
    for line in (TDIR / f"call_{call_id}.txt").read_text(encoding="utf-8").splitlines():
        m = TURN_RE.match(line)
        if m:
            out.append([m.group(1), m.group(2)])
        elif out:
            out[-1][1] += "\n" + line
    return [(f"T{i}", spk, txt.strip()) for i, (spk, txt) in enumerate(out, 1)]


def ev(call_turns, needle, span=None):
    """Locate the turn containing `needle`; return {turn_id, quote} with the
    quote sliced verbatim from the turn text. `span` optionally widens the
    quote to a (start_needle, end_needle) range within the same turn."""
    for tid, spk, txt in call_turns:
        if needle in txt:
            if span:
                a = txt.find(span[0])
                b = txt.find(span[1], a) + len(span[1])
                return {"turn_id": tid, "quote": txt[a:b]}
            return {"turn_id": tid, "quote": needle}
    raise SystemExit(f"needle not found: {needle!r}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}

    # ---- Judge 1: call 11 ----
    t = turns("11")
    results["j1_call11"] = {
        "outcome_evidence": [
            ev(t, "I have created an urgent task for our team"),
            ev(t, "contact you as soon as possible"),
        ],
        "outcome_rationale": "A ticket was created with no timeframe beyond 'as "
            "soon as possible' and no reference number. The same promise was "
            "already broken once earlier the same day, per the caller.",
        "outcome": "deferred",
        "commitment_timeframe": None,
        "escalation_evidence": [
            ev(t, "I would like to talk to the doctor"),
            ev(t, "I will include this request and your concerns in the urgent message"),
        ],
        "escalation_rationale": "The caller explicitly asked to speak to the "
            "doctor. The agent answered the request by documenting it inside "
            "another ticket rather than transferring.",
        "escalation_score": 1,
        "caller_requested_human": True,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 1: call 18 ----
    t = turns("18")
    results["j1_call18"] = {
        "outcome_evidence": [
            ev(t, "it is best to speak directly with your clinical care team"),
            ev(t, "Let me connect you with our team who can assist you directly"),
        ],
        "outcome_rationale": "Clinical dosing question routed to the care team "
            "immediately; the transcript ends at the hold, consistent with a "
            "connecting transfer.",
        "outcome": "transferred_warm",
        "commitment_timeframe": None,
        "escalation_evidence": [
            ev(t, "whether you should continue using the drops"),
        ],
        "escalation_rationale": "Genuine clinical question; escalation is the "
            "correct action per the rubric regardless of automation cost, and it "
            "happened at the first signal, in three sentences.",
        "escalation_score": 4,
        "caller_requested_human": False,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 1: call 10 ----
    t = turns("10")
    results["j1_call10"] = {
        "outcome_evidence": [
            ev(t, "The team typically processes these within two to three business days"),
            ev(t, "That's perfect"),
        ],
        "outcome_rationale": "A ticket, but with a stated what (glasses "
            "prescription to email), who (the team), and when (two to three "
            "business days). Meets the committed bar; no reference number, so "
            "not resolved.",
        "outcome": "committed",
        "commitment_timeframe": "within two to three business days",
        "escalation_evidence": [
            ev(t, "I understand you need another copy of your glasses prescription"),
        ],
        "escalation_rationale": "Routine eyewear-prescription request handled "
            "without escalation, which matches how sibling calls handle the "
            "same intent. Correct non-escalation.",
        "escalation_score": 4,
        "caller_requested_human": False,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 1: call 40 ----
    t = turns("40")
    results["j1_call40"] = {
        "outcome_evidence": [
            ev(t, "having trouble transferring your call"),
            ev(t, "I recommend calling our front desk directly"),
        ],
        "outcome_rationale": "The appointment confirmation succeeded, but the "
            "caller's live question triggered a transfer that failed, and the "
            "agent's fallback was to tell the caller to place a new call "
            "themselves.",
        "outcome": "transferred_failed",
        "commitment_timeframe": None,
        "escalation_evidence": [
            ev(t, "Let me transfer you to our front desk"),
        ],
        "escalation_rationale": "Escalating a facility question is defensible; "
            "the failure mode is the fallback. Pushing the retry onto the "
            "caller scores 1 under the anchor for failed escalation.",
        "escalation_score": 1,
        "caller_requested_human": False,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 3: call 39 (score 1, caller-caught) ----
    t = turns("39")
    results["j3_call39"] = {
        "checkable_claims": [{
            **{"claim_" + k: v for k, v in ev(t, "your appointment on Sunday",
                span=("I", "Sunday")).items()},
            **{"contradiction_" + k: v for k, v in ev(t, "You open on Sunday").items()},
            "evidence_type": "caller_contradiction",
            "agent_conceded": True,
        }],
        "unverifiable_claims_seen": 1,
        "rationale": "The agent stated the appointment day as Sunday; the caller "
            "challenged it and the agent conceded, restating Monday. Day-of-week "
            "is not redacted, so this is transcript-provable. The corrected "
            "Monday date itself remains unverifiable and was not scored.",
        "score": 1,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 3: call 26 (the abstain path) ----
    t = turns("26")
    results["j3_call26"] = {
        "checkable_claims": [],
        "unverifiable_claims_seen": 2,
        "rationale": "The only factual claims are the sixty-five dollar balance "
            "and the statement date, neither verifiable from the transcript. The "
            "caller's 'it's sixty dollars, right?' is answered with a "
            "restatement of sixty-five which the caller accepts, so there is no "
            "concession to score. Abstain per instructions.",
        "score": None,
        "confidence": "high",
        "abstain": True,
        "abstain_reason": "unverifiable_external_claim",
    }

    # ---- Judge 5: call 11 (score 1) ----
    t = turns("11")
    results["j5_call11"] = {
        "trigger_turn": ev(t, "I would like to talk to the doctor"),
        "agent_response_turn": ev(t, "I will include this request and your concerns in the urgent message"),
        "rationale": "The caller, on a twice-broken promise, asked for a human. "
            "The agent produced three empathy statements and the identical plan: "
            "another ticket, another unbounded callback. Empathy language "
            "present, plan unchanged, request denied.",
        "score": 1,
        "plan_changed": False,
        "empathy_language_present": True,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    # ---- Judge 5: call 26 (score 4) ----
    t = turns("26")
    results["j5_call26"] = {
        "trigger_turn": ev(t, "I'm living on Social Security"),
        "agent_response_turn": ev(t, "Would you like to make a partial payment today instead"),
        "rationale": "The caller stated a financial constraint. The agent's next "
            "actions changed because of it: a partial-payment offer, then a "
            "specific callback date and time taken and confirmed.",
        "score": 4,
        "plan_changed": True,
        "empathy_language_present": True,
        "confidence": "high",
        "abstain": False,
        "abstain_reason": None,
    }

    for name, obj in results.items():
        (OUT / f"{name}.json").write_text(json.dumps(obj, indent=1), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
