"""End-to-end verification for the submission. Run before zipping.

Checks, in order: pipeline scripts re-run cleanly; data files complete; every
JSON schema in 02_judge_prompts.md parses; every quoted piece of evidence in the
deliverables string-matches its cited source (transcript or ASR); every numeric
claim re-derives from the data; no em dashes outside verbatim source quotes; all
call-ID references in range; slop scan. Exit code 1 on any failure.
"""
import pathlib, json, re, csv, subprocess, sys

P = pathlib.Path(__file__).resolve().parents[1]
fails = []
def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail and not ok else ""))
    if not ok: fails.append(name)

for script in ['scripts/extract.py', 'scripts/index.py', 'scripts/audio_silence.py']:
    r = subprocess.run([sys.executable, str(P/script)], capture_output=True, text=True)
    check(f"script runs: {script}", r.returncode == 0, r.stderr[-200:])

tfiles = sorted(P.glob('data/transcripts/call_*.txt'))
check("50 transcript files", len(tfiles) == 50)
check("no blank transcripts", all(f.read_text(encoding='utf-8').strip() for f in tfiles))
idx = list(csv.DictReader(open(P/'data/index.csv')))
check("index.csv 50 rows", len(idx) == 50)
ints = list(csv.DictReader(open(P/'data/intents.csv')))
check("intents.csv 50 rows and ids 01..50", len(ints) == 50 and
      [r['call_id'] for r in ints] == [f"{i:02d}" for i in range(1,51)])
ajs = sorted(P.glob('data/audio_transcripts/*.json'))
check("10 ASR jsons", len(ajs) == 10)

s = (P/'deliverables/02_judge_prompts.md').read_text(encoding='utf-8')
blocks = re.findall(r'```json\n(.*?)```', s, re.S)
check("6 JSON schemas present", len(blocks) == 6, f"found {len(blocks)}")
for i, b in enumerate(blocks, 1):
    try:
        obj = json.loads(b)
        check(f"schema {i} parses with object/required/properties",
              obj.get('type') == 'object' and 'required' in obj and 'properties' in obj)
    except Exception as e:
        check(f"schema {i} parses", False, str(e)[:80])

tx = {f"{i:02d}": (P/f"data/transcripts/call_{i:02d}.txt").read_text(encoding='utf-8').lower()
      for i in range(1,51)}
tq = [("11","obviously not."),("11","i would like to talk to the doctor"),
      ("45","i’m a real assistant"),("45","is this a recording"),("48","are you a person"),
      ("40","i’m having trouble transferring your call"),("10","two to three business days"),
      ("10","yep. that's perfect"),("21","it isn't four digit"),("39","you open on sunday"),
      ("17","i wish i could understand you"),("28","you don't call someone and ask for their information"),
      ("47","i need to speak to a real person"),("13","do i have to repeat everything"),
      ("15","i had called earlier"),("09","i do not see any active prescriptions"),
      ("27","we will call you back tomorrow"),("15","virtual receptionist"),
      ("12","i need to order my contacts"),("26","i'm living on social security"),
      ("16","just checking in"),
      ("04","please wait while i create a request for our teami have created a task")]
for cid, q in tq:
    check(f"transcript quote call_{cid}: {q[:38]!r}", q in tx[cid])

ax = {}
for a in ajs:
    d = json.loads(a.read_text())
    ax[d['short_id']] = " ".join(seg['text'] for seg in d['segments']).lower()
aq = [("90cd69877396","i need to speak to a live person"),
      ("90cd69877396","i can often help right away"),
      ("90cd69877396","not able to connect you to a staff member just"),
      ("c8bbec5bd602","hablar con representante, por favor"),
      ("c8bbec5bd602","comunicar con un operador"),
      ("25a7b90c6d66","your appointment is scheduled"),
      ("68384b5d9127","i found the patient's chart"),
      ("209bf832bf90","virtual assistant on a recorded line"),
      ("209bf832bf90","spell your last name one more time slowly"),
      ("381df7d8fd17","just some burning when i urinate"),
      ("381df7d8fd17","since you are not experiencing severe symptoms"),
      ("5efc2f655ab6","robin a virtual assistant")]
for sid, q in aq:
    check(f"audio quote {sid}: {q[:38]!r}", q in ax[sid])

def calls_matching(pat, flags=0):
    return [f.stem[-2:] for f in tfiles if re.search(pat, f.read_text(encoding='utf-8'), flags)]
check("concat bug = 19 calls",
      len(calls_matching(r"our team[A-Z]|our team\.[A-Z]|payment\.[A-Z]|request\.[A-Z]|at\[PHONE\]")) == 19)
check("repeat-request flag = 17 calls",
      sum(r['contains_repeat_request'] == '1' for r in idx) == 17)
check("'I am verifying' = 18 calls", len(calls_matching(r"i am verifying", re.I)) == 18)
check("stall filler = 11 calls",
      len(calls_matching(r"are you still there|i am still here|i'm still here|still here (to|and)", re.I)) == 11)
check("reference numbers = 0 calls",
      len(calls_matching(r"reference number|confirmation number|ticket number|case number|request number", re.I)) == 0)
check("agent-side SLA = calls 10,13 only",
      sorted(calls_matching(r"typically processes|two to three business days|within two business days", re.I)) == ['10','13'])

em = []
for f in list(P.glob('deliverables/*.md')) + list(P.glob('notes/*.md')):
    for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if '—' in line: em.append((f.name, i))
check("em dashes: zero anywhere", len(em) == 0, str(em[:3]))

bad = []
for f in list(P.glob('deliverables/*.md')) + list(P.glob('notes/*.md')):
    for m in re.finditer(r'call[ _](\d{1,2})\b', f.read_text(encoding='utf-8'), re.I):
        if not (1 <= int(m.group(1)) <= 50): bad.append((f.name, m.group(0)))
check("all call refs in 1..50", not bad, str(bad[:5]))

slop = re.compile(r"delve|it'?s worth noting|moreover|furthermore|in today'?s|tapestry|leverage|robust|seamless|holistic|crucial|pivotal|underscore|testament|navigat(e|ing) the|game.chang|at the end of the day", re.I)
hits = []
for f in list(P.glob('deliverables/*.md')) + list(P.glob('notes/*.md')):
    for i, line in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
        if slop.search(line): hits.append((f.name, i))
check("slop scan clean", not hits, str(hits[:3]))

# ---- judge dry-run outputs: schema conformance + verbatim evidence ----
DRY = P / 'data' / 'judge_dryrun'
J1_REQ = {"outcome_evidence","outcome_rationale","outcome","escalation_evidence",
          "escalation_rationale","escalation_score","confidence","abstain"}
J3_REQ = {"checkable_claims","rationale","score","confidence","abstain","abstain_reason"}
J5_REQ = {"trigger_turn","agent_response_turn","rationale","score","plan_changed",
          "empathy_language_present","confidence","abstain"}
OUTCOMES = {"resolved","committed","deferred","transferred_warm","transferred_failed","unresolved"}
raw_tx = {f"{i:02d}": (P/f"data/transcripts/call_{i:02d}.txt").read_text(encoding='utf-8')
          for i in range(1,51)}

def quotes_of(obj):
    if isinstance(obj, dict):
        if 'quote' in obj: yield obj['quote']
        for k, v in obj.items():
            if k.endswith('_quote') and isinstance(v, str): yield v
            else: yield from quotes_of(v)
    elif isinstance(obj, list):
        for v in obj: yield from quotes_of(v)

dry_files = sorted(DRY.glob('*.json'))
check("8 dry-run outputs", len(dry_files) == 8, str(len(dry_files)))
for df in dry_files:
    d = json.loads(df.read_text())
    judge, cid = df.stem.split('_call')
    req = {'j1': J1_REQ, 'j3': J3_REQ, 'j5': J5_REQ}[judge]
    check(f"dryrun {df.stem}: required fields", req <= set(d))
    if judge == 'j1':
        check(f"dryrun {df.stem}: outcome enum", d['outcome'] in OUTCOMES)
        check(f"dryrun {df.stem}: escalation in 1..4",
              d['escalation_score'] is None or 1 <= d['escalation_score'] <= 4)
    if judge == 'j3':
        for c in d['checkable_claims']:
            check(f"dryrun {df.stem}: evidence_type enum",
                  c['evidence_type'] in {"caller_contradiction","self_contradiction","restatement_mismatch"})
        if d['abstain']:
            check(f"dryrun {df.stem}: abstain has null score and a reason",
                  d['score'] is None and bool(d['abstain_reason']))
    bad_q = [q for q in quotes_of(d) if q not in raw_tx[cid]]
    check(f"dryrun {df.stem}: all quotes verbatim in call_{cid}", not bad_q, str(bad_q)[:80])

# ---- audio claims: greeting/statement replay in 4 of 10 recordings ----
replay = [("65ce44e043897a7872d74537982","on a recorded line",2),
          ("5efc2f655ab6f8c59ed98858e32","this call is being recorded for quality assurance",2),
          ("68384b5d912730be8c93fa0f8dc","speaking with sarah on a recorded line",2),
          ("209bf832bf900ff32ece9661d93","cassidy abrahamson",2)]
for sid, phrase, n in replay:
    short = sid[:12]
    d = json.loads((P/f"data/audio_transcripts/{short}.json").read_text())
    joined = " ".join(seg['text'] for seg in d['segments']).lower()
    check(f"audio replay {short}: {phrase[:30]!r} x{n}", joined.count(phrase) >= n,
          f"count={joined.count(phrase)}")

todos = sum(f.read_text(encoding='utf-8').count('TODO(me)')
            for f in list(P.glob('deliverables/*.md'))+list(P.glob('notes/*.md')))
print(f"\nopen TODO(me): {todos}")
print("RESULT:", "ALL PASS" if not fails else f"{len(fails)} FAILURES: {fails}")
sys.exit(1 if fails else 0)
