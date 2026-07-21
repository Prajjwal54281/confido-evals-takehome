"""Transcribe the 10 sample wavs with faster-whisper.

No ffmpeg on this machine, so audio is loaded directly with the stdlib `wave`
module (the files are plain 16-bit PCM) and resampled 24k -> 16k in numpy before
being handed to the model as a float32 array.

IMPORTANT LIMITS on what comes out of this:
- This is ASR output. It is NOT the same artifact as the 50 human-corrected
  transcripts in the xlsx and the two must never be pooled or compared as if they
  were. Whisper will mishear things the humans got right, and vice versa.
- The audio is single-channel mixed, so there is NO speaker diarization. Speaker
  attribution below is done afterwards, by matching against the agent's known
  scripted phrasings, and it is a heuristic with an error rate.
- Segment gaps are real measurements of silence on the line. Attributing a gap to
  the agent requires knowing who spoke next, which depends on the heuristic above.
"""
import json
import pathlib
import wave

import numpy as np
from faster_whisper import WhisperModel

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIO = ROOT.parent / "Transcripts + Calls" / "Sample Calls"
OUT = ROOT / "data" / "audio_transcripts"
MODEL = "small"


def load_16k(path):
    with wave.open(str(path)) as w:
        sr, n, ch, sw = (w.getframerate(), w.getnframes(),
                         w.getnchannels(), w.getsampwidth())
        raw = w.readframes(n)
    assert sw == 2 and ch == 1, f"unexpected format in {path.name}"
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if sr != 16000:
        # linear resample; adequate for ASR on 8k-band telephony content
        tgt = int(round(len(x) * 16000 / sr))
        x = np.interp(np.linspace(0, len(x) - 1, tgt),
                      np.arange(len(x)), x).astype(np.float32)
    return x, len(x) / 16000


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    for p in sorted(AUDIO.glob("*.wav")):
        short = p.name.replace("call_", "").replace("_redacted.wav", "")[:12]
        audio, dur = load_16k(p)
        segs, info = model.transcribe(
            audio,
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 700},
            word_timestamps=True,
            condition_on_previous_text=False,  # avoids runaway repetition loops
        )
        rows = []
        for s in segs:
            rows.append({
                "start": round(s.start, 2),
                "end": round(s.end, 2),
                "text": s.text.strip(),
            })
        rec = {
            "file": p.name,
            "short_id": short,
            "duration_s": round(dur, 1),
            "detected_language": info.language,
            "language_probability": round(info.language_probability, 3),
            "model": MODEL,
            "segments": rows,
        }
        (OUT / f"{short}.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
        print(f"{short}  {dur:6.1f}s  lang={info.language}({info.language_probability:.2f})  "
              f"{len(rows):3d} segments", flush=True)


if __name__ == "__main__":
    main()
