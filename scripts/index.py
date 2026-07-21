"""Build data/index.csv: mechanical, judgment-free facts per call.

Every column here is computed by a regex or a count. Nothing in this file is a
quality judgment. Heuristics are deliberately conservative and are all visible
below so a reader can audit or disagree with each one.

Turn parsing
------------
A turn starts at a line matching ^(Agent|User):\\s and continues until the next
such line. Blank lines inside a turn are kept (call_01 has a turn with a
paragraph break inside it).

CAVEAT on speaker labels, discovered by reading the data: the labels are not
reliable. In outbound calls that reach voicemail, the callee's recorded greeting
and the carrier IVR prompts are sometimes tagged `Agent:` and sometimes `User:`
(see call_29, call_30, call_50). Diarization, not ground truth. Any metric built
on n_agent_turns / n_user_turns inherits that error.
"""
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
TDIR = ROOT / "data" / "transcripts"
OUT = ROOT / "data" / "index.csv"

TURN_RE = re.compile(r"^(Agent|User):\s?(.*)$")
REDACTION_RE = re.compile(r"\[[A-Z_]+\]")
WORD_RE = re.compile(r"[A-Za-z']+")

# --- keyword heuristics -----------------------------------------------------
# Transfer: agent hands the live call to, or promises routing to, a human.
TRANSFER_RE = re.compile(
    r"\b("
    r"transfer(ring|red)?\b|"
    r"connect(ing)? you\b|"
    r"put(ting)? you (through|on hold for)\b|"
    r"speak (with|to) (a|an|one of our|our) (representative|agent|team member|staff|nurse|person|human)|"
    r"let me get (someone|somebody)|"
    r"hand(ing)? (you|this) (over|off)"
    r")",
    re.I,
)

# Callback: resolution deferred to a later outbound contact from the clinic.
CALLBACK_RE = re.compile(
    r"\b("
    r"call you back|calling you back|call(s)? back|callback|"
    r"(will|they'?ll|our team will|someone will) (reach out|contact you|get back to you|be in touch)|"
    r"return (your|my) call|"
    r"good time (for|to) (our team|us|someone) to (call|reach)"
    r")",
    re.I,
)

# Escalation to a queue/ticket rather than in-call resolution.
TICKET_RE = re.compile(
    r"\b(creat(e|ing) a (request|ticket)|submit(ting|ted)? (this|your) request|"
    r"forward(ing)? (this|your) (request|to)|send (this|a note) to (our|the) team)\b",
    re.I,
)

# Voicemail / answering-machine / IVR markers, wherever they are speaker-tagged.
VOICEMAIL_RE = re.compile(
    r"\b(leave (your|a) message|record your message|at the tone|after the (tone|beep)|"
    r"is not available|voicemail|press (any )?(key|one|1) |deje su mensaje|"
    r"please leave a message)\b",
    re.I,
)

# Agent opening that identifies an OUTBOUND call (agent dials the patient).
OUTBOUND_OPEN_RE = re.compile(
    r"\bthis is \w+ calling from\b|\bthis is a (message|reminder|call regarding) for\b|"
    r"\bthis is a message for\b|\bam i speaking with\b",
    re.I,
)
# Agent opening that identifies an INBOUND call (patient dialed the clinic).
INBOUND_OPEN_RE = re.compile(r"\bhow (can|may) i help you\b|\bhow can i assist\b", re.I)

# --- repeat-request heuristic ----------------------------------------------
# Agent asks for a field it has already been given. We only fire when the agent
# asks for the SAME field twice AND the user supplied something in between.
# Deliberately narrow: it will miss paraphrased re-asks and it will miss re-asks
# of free-text fields. Under-counting is the intended failure mode.
FIELD_ASKS = {
    "dob": re.compile(r"date of birth|\bdob\b", re.I),
    "first_name": re.compile(r"(patient'?s )?first name", re.I),
    "last_name": re.compile(r"(patient'?s )?last name", re.I),
    "phone": re.compile(r"(phone|contact) number|number (we|our team) can reach", re.I),
    "reason": re.compile(r"reason for (your|the) (visit|call)", re.I),
    "email": re.compile(r"email address", re.I),
}
ASK_MARK_RE = re.compile(r"\?|may i have|can you (please )?(tell|provide|confirm)|what is your", re.I)


def parse_turns(text):
    turns = []
    for line in text.splitlines():
        m = TURN_RE.match(line)
        if m:
            turns.append([m.group(1), m.group(2)])
        elif turns:
            turns[-1][1] += "\n" + line
    return [(s, t.strip()) for s, t in turns]


def count_repeat_requests(turns):
    """Return (count, list of field names re-asked)."""
    hits = []
    for field, pat in FIELD_ASKS.items():
        ask_idxs = [
            i for i, (spk, txt) in enumerate(turns)
            if spk == "Agent" and pat.search(txt) and ASK_MARK_RE.search(txt)
        ]
        if len(ask_idxs) < 2:
            continue
        for a, b in zip(ask_idxs, ask_idxs[1:]):
            user_spoke = any(
                spk == "User" and WORD_RE.search(txt) for spk, txt in turns[a + 1:b]
            )
            if user_spoke:
                hits.append(field)
                break
    return len(hits), hits


def ends_abruptly(turns):
    """Last turn does not end in terminal punctuation. Catches cut recordings
    and mid-sentence hangups alike; cannot distinguish the two."""
    if not turns:
        return True
    last = turns[-1][1].rstrip().rstrip('"”')
    return not last.endswith((".", "!", "?"))


def direction(turns):
    """inbound | outbound | unknown, from the FIRST agent turn only."""
    for spk, txt in turns:
        if spk == "Agent":
            if INBOUND_OPEN_RE.search(txt):
                return "inbound"
            if OUTBOUND_OPEN_RE.search(txt):
                return "outbound"
            return "unknown"
    return "unknown"


def main():
    rows = []
    for path in sorted(TDIR.glob("call_*.txt")):
        text = path.read_text(encoding="utf-8")
        cid = path.stem.replace("call_", "")
        turns = parse_turns(text)
        agent = [t for s, t in turns if s == "Agent"]
        user = [t for s, t in turns if s == "User"]
        n_rep, rep_fields = count_repeat_requests(turns)
        rows.append({
            "call_id": cid,
            "n_turns": len(turns),
            "n_agent_turns": len(agent),
            "n_user_turns": len(user),
            "agent_words": sum(len(WORD_RE.findall(t)) for t in agent),
            "user_words": sum(len(WORD_RE.findall(t)) for t in user),
            "transcript_ends_abruptly": int(ends_abruptly(turns)),
            "contains_transfer_language": int(any(TRANSFER_RE.search(t) for t in agent)),
            "contains_callback_language": int(any(CALLBACK_RE.search(t) for t in agent)),
            "contains_ticket_language": int(any(TICKET_RE.search(t) for t in agent)),
            "contains_repeat_request": int(n_rep > 0),
            "repeat_request_fields": "|".join(rep_fields),
            "voicemail_markers": int(bool(VOICEMAIL_RE.search(text))),
            "direction": direction(turns),
            "redaction_token_count": len(REDACTION_RE.findall(text)),
        })

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")

    def tally(key):
        d = {}
        for r in rows:
            d[r[key]] = d.get(r[key], 0) + 1
        return dict(sorted(d.items(), key=lambda kv: -kv[1]))

    for k in ["direction", "voicemail_markers", "transcript_ends_abruptly",
              "contains_transfer_language", "contains_callback_language",
              "contains_ticket_language", "contains_repeat_request"]:
        print(f"{k:32s} {tally(k)}")
    print("repeat fields:", tally("repeat_request_fields"))


if __name__ == "__main__":
    main()
