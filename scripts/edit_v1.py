#!/usr/bin/env python3
"""Edit v1 of video_01_brut_nugz — reel-style cut (talking head + AI b-roll + word captions).

Reads only original/video_01_brut_nugz.MOV (never modified) and the b-roll images in
exports/broll/. Writes exports/v1/nugz_marge_cfd_v1.mp4.

Cuts requested by the user (source time, mm:ss.cc):
  delete 0:00 -> 1:19.99 | 1:24.94 -> 2:41.58 | 3:00.60 -> 7:29.97 | 7:59.45 -> end
Inside the three kept ranges, dead air > ~0.6 s is tightened (cut points measured on
the waveform, -45 dBFS) and every piece is snapped to the 30 fps frame grid so audio
and video stay in sync.
"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "original/video_01_brut_nugz.MOV")
BROLL = os.path.join(ROOT, "exports/broll")
OUTDIR = os.path.join(ROOT, "exports/v1")
OUT = os.path.join(OUTDIR, "nugz_marge_cfd_v1.mp4")
WORDS = os.path.join(ROOT, "analysis/transcript_words.json")
FPS = 30
W, H = 1080, 1920
TMP = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp()
os.makedirs(TMP, exist_ok=True); os.makedirs(OUTDIR, exist_ok=True)

TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.05:saturation=1.12")

def crop_for(kind, fx=0.5):
    """Framing presets. Setup A = seated (subject ~72% right), setup C = standing."""
    if kind == "A_wide":  return "crop=676:1202:404:718"
    if kind == "A_close": return "crop=492:874:532:850"
    if kind == "C_wide":  return None
    if kind == "C_close":
        cw, ch = 832, 1478
        cx = int(min(max(fx * 1080 - cw / 2, 0), 1080 - cw)); cy = 190
        return f"crop={cw}:{ch}:{cx}:{cy}"
    raise ValueError(kind)

# Mono speech is duplicated to stereo (+3 LU), hence -17 LUFS mono -> -14 LUFS delivered.
# (src_in, src_out, visual, spoken text — corrected wording, extras)
P = [
 (80.28, 82.40, "A_wide",  "Et si je te disais qu'en Europe tu peux préparer un trade", {}),
 (82.40, 83.45, "A_close", "avec même pas 10 € de risque,", {"hl": ["10", "€", "risque,"]}),
 (83.78, 84.85, "broll:lock", "et même pas pouvoir l'ouvrir.", {"title": "IMPOSSIBLE\\ND'ENTRER ?", "whoosh": 1, "flash_out": 1}),
 (164.70, 165.60, "A_close", "brokers CFD", {"flash_in": 1, "hl": ["CFD"]}),
 (165.60, 168.55, "broll:eu", "régulés en Europe sont limités à x30 d'effet de levier.", {"title": "x30", "sub": "EUROPE · CLIENTS PARTICULIERS\\NPAIRES DE DEVISES MAJEURES", "whoosh": 1, "hl": ["x30"]}),
 (168.95, 170.15, "A_wide",  "Hors de ce cadre,", {}),
 (170.15, 172.15, "broll:lever", "certains brokers sont limités à x400.", {"title": "x400", "titlefx": "\\3c&H1020E0&\\bord9\\blur2", "whoosh": 1, "hl": ["x400."]}),
 (173.05, 175.20, "A_close", "La différence entre ces deux choses-là,", {"hl": ["différence"]}),
 (175.20, 175.85, "card",    "la marge,", {"title": "LA MARGE", "whoosh": 1, "hl": ["marge,"]}),
 (175.85, 180.40, "A_wide",  "et cette marge-là qui peut empêcher un trader particulier de rentrer sur une position.", {"hl": ["empêcher"], "flash_out": 1}),
 (450.15, 451.13, "C_close", "Exemple concret,", {"fx": 0.62, "flash_in": 1, "whoosh": 1, "hl": ["concret,"]}),
 (451.78, 453.40, "C_wide",  "tu as 500 € sur ton compte,", {"panel": "COMPTE : 500 €", "hl": ["500", "€"]}),
 (453.40, 456.36, "C_close", "tu veux ouvrir une position avec un lot 0,20,", {"fx": 0.46, "panel": "POSITION : LOT 0,20", "hl": ["0,20,"]}),
 (456.94, 458.07, "broll:cash", "ce qui fait 20 000 €.", {"title": "20 000 €", "sub": "D'EXPOSITION", "whoosh": 1, "hl": ["20", "000", "€."]}),
 (458.80, 460.03, "C_wide",  "Tu en risques dix,", {"panel": "RISQUE : 10 €", "hl": ["dix,"]}),
 (460.60, 463.25, "C_close", "si tu as seulement un effet de levier de x30,", {"fx": 0.58, "panel": "LEVIER x30", "hl": ["x30,"]}),
 (463.50, 466.17, "C_wide",  "alors là la marge nécessaire sera de 667 €.", {"panel": "MARGE : 667 €", "panel2": ("> 500 € → TRADE IMPOSSIBLE", "&H3A3AFF&"), "hl": ["667", "€."]}),
 (467.09, 470.30, "C_close", "Si là par contre tu as un effet de levier de x400,", {"fx": 0.50, "panel": "LEVIER x400", "hl": ["x400,"]}),
 (470.30, 473.48, "C_wide",  "alors là d'un coup la marge nécessaire n'est seulement que de 50 €.", {"panel": "MARGE : 50 €", "panel2": ("< 500 € → TRADE OUVERT", "&H5AE05A&"), "hl": ["50", "€."]}),
 (474.17, 475.19, "C_close", "Est-ce que tu comprends", {"fx": 0.45}),
 (475.75, 478.40, "C_wide",  "le problème avec la marge sur les brokers CFD ?", {"hl": ["problème", "marge"]}),
]

q = lambda t: round(t * FPS) / FPS
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stderr[-3000:]}")
    return r

# ---------- 1. video pieces ----------
pieces, t_out = [], 0.0
for i, (a, b, vis, text, ex) in enumerate(P):
    a, b = q(a), q(b); n = round((b - a) * FPS); dur = n / FPS
    f = os.path.join(TMP, f"v{i:02d}.mp4")
    fades = []
    if ex.get("flash_in"):  fades.append("fade=t=in:st=0:d=0.17:color=white")
    if ex.get("flash_out"): fades.append(f"fade=t=out:st={dur-0.1:.3f}:d=0.1:color=white")
    if vis.startswith("broll:"):
        img = os.path.join(BROLL, vis.split(":")[1] + ".jpg")
        vf = (f"scale=2160:-2:flags=lanczos,crop=2160:3840,"
              f"zoompan=z='1.18-0.18*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
              f"eq=brightness=-0.05:saturation=1.1,vignette=PI/4,format=yuv420p")
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", img, "-vf", ",".join([vf] + fades), "-frames:v", str(n)]
    elif vis == "card":
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x0b0b0f:s={W}x{H}:r={FPS}",
               "-vf", ",".join(["vignette=PI/3,format=yuv420p"] + fades), "-frames:v", str(n)]
    else:
        c = crop_for(vis, ex.get("fx", 0.5))
        chain = [TONEMAP] + ([c] if c else []) + [f"scale={W}:{H}:flags=lanczos"] + \
                (["unsharp=5:5:0.5"] if c else []) + fades
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", SRC, "-map", "0:v:0", "-an",
               "-vf", ",".join(chain), "-frames:v", str(n)]
    run(cmd + ["-r", str(FPS), "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", f])
    pieces.append(dict(i=i, a=a, b=b, dur=dur, t0=t_out, vis=vis, text=text, ex=ex)); t_out += dur
    print(f"piece {i:02d} {vis:12s} {a:7.2f}-{b:7.2f} -> out {pieces[-1]['t0']:6.2f} ({dur:.2f}s)", flush=True)
TOTAL = t_out

lst = os.path.join(TMP, "list.txt")
open(lst, "w").write("".join(f"file '{os.path.join(TMP, f'v{p['i']:02d}.mp4')}'\n" for p in pieces))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", os.path.join(TMP, "video.mp4")])

# ---------- 2. audio: speech pieces, 10 ms de-click fades, HPF, two-pass loudnorm, whooshes ----------
fc, labels = [], []
for p in pieces:
    d = p["dur"]
    fc.append(f"[0:a]atrim=start={p['a']:.4f}:end={p['b']:.4f},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.01,afade=t=out:st={d-0.012:.4f}:d=0.012[a{p['i']}]")
    labels.append(f"[a{p['i']}]")
fc.append("".join(labels) + f"concat=n={len(pieces)}:v=0:a=1,highpass=f=80,"
          "acompressor=threshold=-24dB:ratio=2.5:attack=5:release=120:makeup=2[sp]")
speech = os.path.join(TMP, "speech.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[sp]",
     "-ac", "1", "-ar", "48000", speech])
m = run(["ffmpeg", "-hide_banner", "-i", speech, "-af", "loudnorm=I=-17:TP=-4:LRA=9:print_format=json",
         "-f", "null", "-"]).stderr
js = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
ln = (f"loudnorm=I=-17:TP=-4:LRA=9:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
      f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
whoosh_t = [p["t0"] for p in pieces if p["ex"].get("whoosh")]
inputs = ["-i", speech]; mix = [f"[0:a]{ln},aresample=48000[s]"]; wl = ["[s]"]
for k, t in enumerate(whoosh_t):
    st = max(t - 0.22, 0)
    inputs += ["-f", "lavfi", "-t", "0.42", "-i", "anoisesrc=c=pink:r=48000:a=0.9"]
    mix.append(f"[{k+1}:a]highpass=f=500,lowpass=f=5200,afade=t=in:d=0.26:curve=exp,"
               f"afade=t=out:st=0.26:d=0.16,volume=0.16,adelay={int(st*1000)}[w{k}]")
    wl.append(f"[w{k}]")
mix.append("".join(wl) + f"amix=inputs={len(wl)}:normalize=0:duration=first,alimiter=limit=0.63,"
           f"atrim=0:{TOTAL:.4f},pan=stereo|c0=c0|c1=c0[out]")
mixf = os.path.join(TMP, "mix.wav")
run(["ffmpeg", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(mix), "-map", "[out]", mixf])
# Deterministic loudness: measure the stereo mix, apply the exact gain to reach -14 LUFS, true-peak limit.
def lufs(f):
    e = run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128", "-f", "null", "-"]).stderr
    return float(e[e.rfind("I:"):].split()[1])
gain = -14.0 - lufs(mixf)
audio = os.path.join(TMP, "audio.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", mixf, "-af",
     f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.79:level=false,aresample=48000", audio])
print(f"audio gain {gain:+.2f} dB -> {lufs(audio):.1f} LUFS", flush=True)

# ---------- 3. captions + titles + panels (ASS, libass) ----------
words = [w for s in json.load(open(WORDS)) for w in s["words"]]
def ts(t):
    t = max(t, 0); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
def esc(s): return s.replace("{", "(").replace("}", ")")
YEL = "&H42E6F5&"
ev = []
for p in pieces:
    toks = p["text"].split()
    ww = [w for w in words if w["s"] >= p["a"] - 0.15 and w["e"] <= p["b"] + 0.15]
    if len(ww) == len(toks):
        st = [max(w["s"], p["a"]) for w in ww]
    else:  # wording corrected vs ASR -> spread evenly over the spoken span
        s0 = max(ww[0]["s"], p["a"]) if ww else p["a"]; s1 = min(ww[-1]["e"], p["b"]) if ww else p["b"]
        st = [s0 + (s1 - s0) * k / len(toks) for k in range(len(toks))]
    groups, cur = [], []
    for k, tok in enumerate(toks):
        cur.append(k)
        if len(cur) == 3 or sum(len(toks[j]) for j in cur) > 13 or tok[-1] in ",.?" or k == len(toks) - 1:
            groups.append(cur); cur = []
    for g_i, g in enumerate(groups):
        s = p["t0"] + st[g[0]] - p["a"]
        e = p["t0"] + (st[groups[g_i+1][0]] - p["a"] if g_i + 1 < len(groups) else p["dur"])
        txt = " ".join((f"{{\\c{YEL}}}{toks[j].upper()}{{\\c&HFFFFFF&}}" if toks[j] in p["ex"].get("hl", [])
                        else toks[j].upper()) for j in g)
        ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\fscx88\\fscy88\\t(0,90,\\fscx100\\fscy100)}}{txt}")
    t0, t1 = p["t0"], p["t0"] + p["dur"]; ex = p["ex"]
    if ex.get("title"):
        col = ex.get("titlecol", "&HFFFFFF&")
        ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Title,,0,0,0,,{{\\c{col}{ex.get('titlefx','')}\\fscx70\\fscy70\\t(0,160,\\fscx100\\fscy100)"
                  f"\\t(160,{int(p['dur']*1000)},\\fscx106\\fscy106)}}{ex['title']}")
    if ex.get("sub"):
        ev.append(f"Dialogue: 1,{ts(t0+0.12)},{ts(t1)},Sub,,0,0,0,,{{\\fad(120,0)}}{ex['sub']}")
    if ex.get("panel"):
        ev.append(f"Dialogue: 1,{ts(t0)},{ts(t1)},Panel,,0,0,0,,{{\\fscx80\\fscy80\\t(0,120,\\fscx100\\fscy100)}}{esc(ex['panel'])}")
    if ex.get("panel2"):
        txt2, c2 = ex["panel2"]
        ev.append(f"Dialogue: 1,{ts(t0+0.5)},{ts(t1)},Panel2,,0,0,0,,{{\\c{c2}\\fad(100,0)}}{esc(txt2)}")

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,6,2,2,70,70,520,1
Style: Title,Anton,250,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,3,6,5,60,60,0,1
Style: Sub,Inter Black,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,3,2,8,60,60,1120,1
Style: Panel,Inter Black,70,&H00FFFFFF,&H00FFFFFF,&H40101010,&H00000000,0,0,0,0,100,100,1,0,3,22,0,8,60,60,150,1
Style: Panel2,Inter Black,62,&H00FFFFFF,&H00FFFFFF,&H40101010,&H00000000,0,0,0,0,100,100,1,0,3,16,0,8,60,60,290,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n"
assf = os.path.join(TMP, "subs.ass"); open(assf, "w").write(ass)
fonts = "/usr/share/fonts/opentype/inter"
anton = os.path.join(TMP, "fonts"); os.makedirs(anton, exist_ok=True)
for fn in ("Anton-Regular.ttf",):
    srcf = "/home/user/22creations/assets/fonts/" + fn
    if os.path.exists(srcf): subprocess.run(["cp", srcf, anton])
for fn in ("Inter-Black.otf",):
    subprocess.run(["cp", os.path.join(fonts, fn), anton])

# ---------- 4. final encode ----------
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(TMP, "video.mp4"), "-i", audio,
     "-vf", f"ass={assf}:fontsdir={anton}", "-map", "0:v", "-map", "1:a",
     "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-r", str(FPS),
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT])
json.dump(dict(total_s=round(TOTAL, 3), pieces=[{k: v for k, v in p.items() if k != "ex"} for p in pieces]),
          open(os.path.join(OUTDIR, "cutlist_v1.json"), "w"), indent=1, ensure_ascii=False)
print(f"done: {OUT} ({TOTAL:.2f}s)")
