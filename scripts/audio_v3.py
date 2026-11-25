#!/usr/bin/env python3
"""v3 = v2 picture + new sound design (team feedback: synthesized SFX sounded cheap).

- SFX: real recorded sounds from Mixkit (Mixkit Sound Effects Free License: free for
  commercial use, no attribution), each placed so its PEAK lands on the cut.
- Music: "C.B.P.D" (Mixkit, dark trap, 96 BPM) — chosen because it is the closest match,
  by measurement, to the music under the @planfomo and Silence Capital references
  (spectral centre ~310-330 Hz, ~44 % bass energy, 92-96 BPM). It enters after the hook,
  ducks under the voice and dips under « LA MARGE ».

Usage: python3 -I scripts/audio_v3.py <tmpdir> <sfx_dir> <music.mp3>
Reads original/ (speech) and exports/v2/ (picture + cutlist); writes exports/v3/.
"""
import json, os, subprocess, sys, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "original/video_01_brut_nugz.MOV")
V2 = os.environ.get("PICTURE", os.path.join(ROOT, "exports/v2/nugz_levier_x30_x400_v2.mp4"))   # any style's picture
CUT = json.load(open(os.path.join(ROOT, "exports/v2/cutlist_v2.json")))
OUTDIR = os.path.join(ROOT, "exports/v3"); os.makedirs(OUTDIR, exist_ok=True)
OUT = os.environ.get("OUT", os.path.join(OUTDIR, "nugz_levier_x30_x400_v3.mp4"))
TMP, SFXDIR, MUSIC = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(TMP, exist_ok=True)
SR = 48000

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"FAILED {cmd[:6]}\n{r.stderr[-2000:]}")
    return r
def readwav(f):
    w = wave.open(f); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def decode(src, out, extra=()):
    run(["ffmpeg", "-v", "error", "-y", *extra, "-i", src, "-ac", "1", "-ar", str(SR), out]); return readwav(out)

pieces = CUT["pieces"]; TOTAL = CUT["total_s"]; N = int(TOTAL * SR)
P = {p["kind"]: p for p in pieces}
A0 = P["anim:0"]["t0"]; M = {int(p["kind"].split(":")[1]): p["t0"] for p in pieces if p["kind"].startswith("anim:")}

# ---------- speech (same cut list as v2, 10 ms de-click fades, HPF, gentle compression)
fc, lab = [], []
for p in pieces:
    d = p["dur"]
    fc.append(f"[0:a]atrim=start={p['a']:.4f}:end={p['b']:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
              f"afade=t=out:st={d-0.012:.4f}:d=0.012[a{p['i']}]"); lab.append(f"[a{p['i']}]")
fc.append("".join(lab) + f"concat=n={len(pieces)}:v=0:a=1,highpass=f=80,"
          "acompressor=threshold=-24dB:ratio=2.5:attack=5:release=120:makeup=2[sp]")
sp_f = os.path.join(TMP, "speech.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[sp]", "-ac", "1", "-ar", str(SR), sp_f])
speech = np.zeros(N, np.float32); s = readwav(sp_f)[:N]; speech[:len(s)] = s

# ---------- SFX (peak-aligned)
S = {k: decode(os.path.join(SFXDIR, k + ".mp3"), os.path.join(TMP, f"sfx_{k}.wav"))
     for k in ("whoosh", "slide", "pop", "click", "tick", "impact", "heartbeat", "reject", "confirm",
               "clickerr", "tunnel", "rumble", "swoosh")}
S["tunnel"] = S["tunnel"][int(0.95 * SR):]        # skip the build-up: resonance starts on the hit
PEAK = {k: int(np.argmax(np.abs(v))) / SR for k, v in S.items()}
sfx = np.zeros(N + 10 * SR, np.float32)
def put(k, t, g, at_peak=True, dur=None, fade=0.3):
    x = S[k].copy()
    if dur:
        x = x[: int(dur * SR)]; nf = int(fade * SR); x[-nf:] *= np.linspace(1, 0, nf)
    st = t - (PEAK[k] if at_peak else 0)
    if st < 0: x = x[int(-st * SR):]; st = 0
    i = int(st * SR); sfx[i:i + len(x)] += g * x

hook = P["hook"]; zoom_stop = 83.87 - hook["a"]; hit = 84.62 - hook["a"]
put("rumble", 0.0, 0.07, at_peak=False, dur=zoom_stop + 0.3, fade=0.6)       # tension under the zoom
put("clickerr", hit, 0.45)                                                   # the refused order…
put("tunnel", hit + 0.05, 0.30, at_peak=False, dur=1.0, fade=0.75)                                  # …with a resonant tunnel tail
put("swoosh", P["esma"]["t0"], 0.32); put("pop", P["esma"]["t0"] + 0.2, 0.35, at_peak=False)
put("whoosh", P["lev"]["t0"], 0.30); put("slide", P["lev"]["t0"] + 1.2, 0.55, at_peak=False)
put("impact", P["marge"]["t0"], 0.55); put("heartbeat", P["marge"]["t0"], 0.6)
put("whoosh", A0, 0.32); put("pop", A0 + 0.03, 0.3, at_peak=False)
put("pop", M[1], 0.32, at_peak=False)
for k in range(8): put("tick", M[1] + 0.2 + k * 0.11, 0.07, at_peak=False)  # balance counting up
put("slide", M[2], 0.45, at_peak=False); put("pop", M[2] + 0.9, 0.3, at_peak=False)
put("pop", M[3], 0.35, at_peak=False); put("click", M[4], 0.3, at_peak=False)
put("swoosh", M[5], 0.28, at_peak=False); put("pop", M[5] + 0.1, 0.3, at_peak=False)
put("tick", M[6], 0.12, at_peak=False); put("reject", M[6] + 0.9, 0.32, at_peak=False, dur=1.0, fade=0.4)
put("swoosh", M[7], 0.28, at_peak=False); put("pop", M[7] + 0.1, 0.3, at_peak=False)
put("tick", M[8], 0.12, at_peak=False); put("confirm", M[8] + 0.9 - PEAK["confirm"] + 0.12, 0.3, at_peak=False)
put("whoosh", P["C_close"]["t0"], 0.30)
sfx = sfx[:N]

# ---------- music: enters after the hook, ducks under the voice, dips under « LA MARGE »
mus_raw = decode(MUSIC, os.path.join(TMP, "music.wav"))
m0 = hook["dur"] - 0.02                                                      # beat drops after the hit
music = np.zeros(N, np.float32); seg = mus_raw[: N - int(m0 * SR)]
music[int(m0 * SR): int(m0 * SR) + len(seg)] = seg
fi = int(0.04 * SR); i0 = int(m0 * SR); music[i0:i0 + fi] *= np.linspace(0, 1, fi)
fo = int(1.6 * SR); music[-fo:] *= np.linspace(1, 0, fo) ** 2
# speech envelope -> ducking gain (fast attack, slow release)
hop = 480; e = np.sqrt((speech[: N // hop * hop].reshape(-1, hop) ** 2).mean(1))
act = (20 * np.log10(e + 1e-9) > -38).astype(np.float32)
g = np.zeros_like(act); a_up, a_dn = 1 - np.exp(-1 / 3), 1 - np.exp(-1 / 30)
for k in range(1, len(act)): g[k] = g[k - 1] + (a_up if act[k] > g[k - 1] else a_dn) * (act[k] - g[k - 1])
g = np.concatenate([g[15:], np.repeat(g[-1:], 15)])   # 150 ms look-ahead: duck before the first syllable
duck = np.repeat(1 - 0.45 * g, hop); duck = np.pad(duck, (0, N - len(duck)), constant_values=duck[-1])
dip = np.ones(N, np.float32); t1, t2 = P["marge"]["t0"] - 0.08, P["marge"]["t0"] + P["marge"]["dur"]
k1, k2 = int(t1 * SR), int(t2 * SR); dip[k1:k2] = 0.15
r = int(0.05 * SR); dip[k1 - r:k1] = np.linspace(1, 0.15, r); dip[k2:k2 + r] = np.linspace(0.15, 1, r)
# music level: ~16 dB under the voice (more in speech, via ducking)
mask = np.repeat(act, hop) > 0; v_rms = np.sqrt(np.mean(speech[: len(mask)][mask] ** 2)) if act.any() else 0.1
m_rms = np.sqrt(np.mean(music[i0:] ** 2)) + 1e-9
music *= (v_rms / m_rms) * 10 ** (-16 / 20) * duck * dip

mix = speech + sfx + music
mixf = os.path.join(TMP, "mix.wav")
with wave.open(mixf, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767).astype(np.int16).tobytes())
def lufs(f):
    e_ = run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128", "-f", "null", "-"]).stderr
    return float(e_[e_.rfind("I:"):].split()[1])
st = os.path.join(TMP, "stereo.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", mixf, "-af", "pan=stereo|c0=c0|c1=c0", st])
gain = -14.0 - lufs(st)
audio = os.path.join(TMP, "audio.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", st, "-af",
     f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.79:level=false,aresample=48000", audio])
run(["ffmpeg", "-v", "error", "-y", "-i", V2, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
     "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT])
print(f"done {OUT}  {lufs(audio):.1f} LUFS")
