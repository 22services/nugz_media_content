"""Word-timestamped French transcript of the original (local, no API).
Usage: ffmpeg -i original/video_01_brut_nugz.MOV -map 0:a:0 -ac 1 -ar 16000 /tmp/a.wav
       pip install faster-whisper && python3 -I scripts/transcribe.py /tmp/a.wav analysis/transcript_words.json
Reads WAV via numpy (avoids a PyAV incompatibility in some faster-whisper installs)."""
import sys, wave, json, numpy as np
from faster_whisper import WhisperModel
w = wave.open(sys.argv[1]); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(
    a, language="fr", vad_filter=True, beam_size=5, word_timestamps=True, condition_on_previous_text=False)
out = [dict(text=s.text.strip(), words=[dict(w=x.word, s=round(x.start, 2), e=round(x.end, 2), p=round(x.probability, 2)) for x in s.words]) for s in segs]
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False)
