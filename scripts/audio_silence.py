"""Measure silence gaps in the 10 sample wavs.

This does NOT transcribe. No ASR is available locally, so nothing here makes any
claim about what was said. It measures one thing: how long the line was quiet.

Method: 20 ms RMS frames. A frame is "silent" if its RMS is below
max(floor_rms * 3, 0.5% of full scale), where floor_rms is the 5th percentile of
all frame RMS in that file (an estimate of that call's noise floor). Runs of
silent frames >= 1.5 s are reported as gaps.

Limits worth stating before anyone quotes these numbers:
- The audio is single-channel mixed. A gap cannot be attributed to the agent or
  to the caller. "Agent latency" is an interpretation, not a measurement.
- Recordings were cut for anonymization. A cut can read as silence. Gaps near a
  redaction are not agent failures. Only sustained gaps in mid-conversation are
  interesting, and even then only after listening.
- Hold music or comfort noise would read as speech, not silence.
"""
import pathlib
import wave

import numpy as np

AUDIO = pathlib.Path(__file__).resolve().parents[2] / "Transcripts + Calls" / "Sample Calls"
FRAME_MS = 20
MIN_GAP_S = 1.5


def frames_rms(path):
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    n = int(sr * FRAME_MS / 1000)
    usable = len(x) - len(x) % n
    fr = x[:usable].reshape(-1, n)
    return np.sqrt((fr ** 2).mean(axis=1)), sr, len(x) / sr


def main():
    print(f"{'file':16s} {'dur':>7s} {'silent%':>8s} {'gaps>=1.5s':>11s} {'longest':>8s} {'total_gap':>10s}")
    for p in sorted(AUDIO.glob("*.wav")):
        rms, sr, dur = frames_rms(p)
        floor = np.percentile(rms, 5)
        thr = max(floor * 3, 0.005)
        silent = rms < thr
        # run-length encode the silent mask
        gaps, run = [], 0
        for s in silent:
            if s:
                run += 1
            else:
                if run:
                    gaps.append(run * FRAME_MS / 1000)
                run = 0
        if run:
            gaps.append(run * FRAME_MS / 1000)
        long = [g for g in gaps if g >= MIN_GAP_S]
        short = p.name.replace("call_", "")[:12]
        print(f"{short:16s} {dur:6.0f}s {silent.mean()*100:7.1f}% "
              f"{len(long):11d} {max(long, default=0):7.1f}s {sum(long):9.1f}s")


if __name__ == "__main__":
    main()
