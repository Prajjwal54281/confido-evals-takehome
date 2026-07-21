"""Extract the 50 transcripts from the xlsx into data/transcripts/call_XX.txt.

Call ID = spreadsheet row order, 1-indexed, zero-padded to 2 digits.
Row order is the only stable identifier we have; the xlsx carries no call id column.
"""
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
XLSX = ROOT.parent / "Transcripts + Calls" / "Call_Transcripts_redacted.xlsx"
OUT = ROOT / "data" / "transcripts"


def main():
    df = pd.read_excel(XLSX, engine="openpyxl")
    print("columns:", list(df.columns))
    print("rows:", len(df))
    col = "transcript_redacted"
    assert col in df.columns, f"expected column {col!r}, got {list(df.columns)}"
    OUT.mkdir(parents=True, exist_ok=True)
    n_blank = 0
    for i, val in enumerate(df[col], start=1):
        text = "" if pd.isna(val) else str(val)
        if not text.strip():
            n_blank += 1
            print(f"  WARNING: row {i} is blank")
        (OUT / f"call_{i:02d}.txt").write_text(text, encoding="utf-8")
    print(f"wrote {len(df)} files, {n_blank} blank")
    # sanity: are there other non-null columns we're throwing away?
    for c in df.columns:
        if c != col:
            print(f"  extra column {c!r}: {df[c].notna().sum()} non-null")


if __name__ == "__main__":
    main()
