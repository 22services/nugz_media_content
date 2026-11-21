#!/usr/bin/env python3
"""Edit v2 of video_01_brut_nugz — reworked from the team's script doc (SCRIPT REEL — LEVIER
ESMA x30 VS LEVIER x400, comments by Elyfe), using the ORIGINAL footage only (the new shoot is
not filmed yet, so Part 3 and the conclusion are absent).

Applied notes
- Hook: no b-roll; progressive zoom, zoom stops on the last phrase; MetaTrader-style error
  sound with a resonant / tunnel tail.
- ESMA: recreated image as a rounded card on the DA background (#f4c430 dots), newspaper
  filter, progressive zoom onto the ESMA logo.
- x400: recreated brand-free leverage visual (no Vantage), panned from the title to the image.
- « LA MARGE »: DA background, very large type inside the safe area, impact sound.
- Part 2 ("animation IA"): replaced by coded motion graphics in the Silence Capital style
  (white glowing line icons on black + #f4c430 dots), sound on every movement; the old top
  panels are removed.
- Captions: @planfomo style — one word at a time, centred, Montserrat Bold + Playfair Display
  italic on key words.

Usage: python3 -I scripts/edit_v2.py <tmpdir> <esma.jpg> <lev.jpg>
Reads original/ read-only, writes exports/v2/.
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "original/video_01_brut_nugz.MOV")
WORDS = os.path.join(ROOT, "analysis/transcript_words.json")
OUTDIR = os.path.join(ROOT, "exports/v2"); os.makedirs(OUTDIR, exist_ok=True)
OUT = os.path.join(OUTDIR, "nugz_levier_x30_x400_v2.mp4")
TMP, ESMA_IMG, LEV_IMG = sys.argv[1], sys.argv[2], sys.argv[3]
FONTS = os.environ.get("NUGZ_FONTS", os.path.join(ROOT, "assets/fonts"))
os.makedirs(TMP, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 30, 48000
DA = (0xF4, 0xC4, 0x30)              # brand accent #f4c430
WHITE, RED, GREEN = (255, 255, 255), (255, 84, 84), (92, 224, 128)

_fc = {}
def font(name, size):
    size = max(1, int(size)); k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(os.path.join(FONTS, name), size)
    return _fc[k]
F_SANS, F_SERIF, F_LIGHT = "Montserrat-Bold.ttf", "PlayfairDisplay-SemiBoldItalic.ttf", "Montserrat-Light.ttf"

TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
           "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.05:saturation=1.12")
CROPS = {"A_wide": "crop=676:1202:404:718", "A_close": "crop=492:874:532:850",
         "C_wide": None, "C_close": "crop=832:1478:{cx}:190"}

# ------------------------------------------------------------------ timeline
# (src_in, src_out, kind, spoken words (corrected), opts)
P = [
 (80.27, 84.87, "hook", "Et si je te disais qu'en Europe tu peux préparer un trade avec même pas 10 € de risque, et même pas pouvoir l'ouvrir.", {"em": ["risque,", "l'ouvrir."]}),
 (164.70, 165.60, "A_close", "brokers CFD", {"em": ["CFD"]}),
 (165.60, 168.53, "esma", "régulés en Europe sont limités à x30 d'effet de levier.", {"em": ["régulés", "x30"]}),
 (168.93, 172.13, "lev", "Hors de ce cadre, certains brokers sont limités à x400.", {"em": ["x400."]}),
 (173.07, 175.20, "A_close", "La différence entre ces deux choses-là,", {"em": ["différence"]}),
 (175.20, 175.87, "marge", "la marge,", {"nocap": True}),
 (175.87, 180.40, "A_wide", "et cette marge-là qui peut empêcher un trader particulier de rentrer sur une position.", {"em": ["empêcher"]}),
 (450.13, 451.13, "anim:0", "Exemple concret,", {"em": ["concret,"]}),
 (451.77, 453.40, "anim:1", "tu as 500 € sur ton compte,", {"em": ["500 €"]}),
 (453.40, 456.37, "anim:2", "tu veux ouvrir une position avec un lot 0,20,", {"em": ["0,20,"]}),
 (456.93, 458.07, "anim:3", "ce qui fait 20 000 €.", {"em": ["20 000 €."]}),
 (458.80, 460.03, "anim:4", "Tu en risques dix,", {"em": ["dix,"]}),
 (460.60, 463.27, "anim:5", "si tu as seulement un effet de levier de x30,", {"em": ["x30,"]}),
 (463.50, 466.17, "anim:6", "alors là la marge nécessaire sera de 667 €.", {"em": ["667 €."]}),
 (467.10, 470.30, "anim:7", "Si là par contre tu as un effet de levier de x400,", {"em": ["x400,"]}),
 (470.30, 473.47, "anim:8", "alors là d'un coup la marge nécessaire n'est seulement que de 50 €.", {"em": ["50 €."]}),
 (474.17, 475.20, "C_close", "Est-ce que tu comprends", {"cx": 0.45}),
 (475.73, 478.40, "C_wide", "le problème avec la marge sur les brokers CFD ?", {"em": ["problème", "marge"]}),
]
q = lambda t: round(t * FPS) / FPS
pieces, t = [], 0
for i, (a, b, kind, text, o) in enumerate(P):
    a, b = q(a), q(b); n = round((b - a) * FPS)
    pieces.append(dict(i=i, a=a, b=b, n=n, t0=t, dur=n / FPS, kind=kind, text=text, o=o)); t += n / FPS
TOTAL = t; NFR = sum(p["n"] for p in pieces)
anim_t0 = next(p["t0"] for p in pieces if p["kind"] == "anim:0")
anim_marks = {int(p["kind"].split(":")[1]): p["t0"] - anim_t0 for p in pieces if p["kind"].startswith("anim:")}

# ------------------------------------------------------------------ helpers
ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(max(x, 0), 1))
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back_out(x, s=1.7):
    x = min(max(x, 0), 1) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

_bg_cache = {}
def da_background(t=0.0):
    """Black + #f4c430 dot grid (the DA), soft vignette, slow drift."""
    key = int((t * 6) % 54)
    if key in _bg_cache: return _bg_cache[key].copy()
    img = Image.new("RGB", (W, H), (6, 6, 8)); d = ImageDraw.Draw(img)
    sp = 54
    yy, xx = np.mgrid[0:H, 0:W]
    for y in range(-sp + key, H + sp, sp):
        for x in range(sp // 2, W, sp):
            r = math.hypot((x - W / 2) / (W * 0.62), (y - H / 2) / (H * 0.62))
            a = max(0.0, 1 - r) ** 1.3
            if a < 0.04: continue
            c = tuple(int(6 + (v - 6) * 0.3 * a) for v in DA)
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=c)
    _bg_cache[key] = img
    return img.copy()

def glow(layer, radius=14, strength=1.6):
    """Add a soft glow under an RGBA layer (lines/text) — the Silence Capital look."""
    small = layer.resize((W // 2, H // 2), Image.BILINEAR).filter(ImageFilter.GaussianBlur(radius / 2))
    g = small.resize((W, H), Image.BILINEAR)
    a = np.asarray(g, dtype=np.float32); a[..., 3] = np.clip(a[..., 3] * strength, 0, 255)
    out = Image.fromarray(a.astype(np.uint8), "RGBA")
    out.alpha_composite(layer); return out

def rounded(img, r):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, *img.size], r, fill=255)
    out = img.convert("RGBA"); out.putalpha(m); return out

def text_center(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def newspaper(img):
    """Subtle newsprint look: partial desaturation, warm paper tint, fine grain."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    gray = a.mean(axis=2, keepdims=True)
    a = gray * 0.45 + a * 0.55
    a = a * np.array([1.04, 1.0, 0.9]) + 6
    rng = np.random.default_rng(7); a += rng.normal(0, 7, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ------------------------------------------------------------------ scenes
ESMA = newspaper(Image.open(ESMA_IMG).convert("RGB"))
LEV = Image.open(LEV_IMG).convert("RGB")
ESMA_LOGO = tuple(float(v) for v in os.environ.get("ESMA_LOGO", "0.5,0.55").split(","))  # logo centre (fraction)

def scene_esma(t, dur):
    img = da_background(t).convert("RGBA")
    cw, ch = 900, 1200
    s_in = back_out(t / 0.35)
    z = 1 + 0.9 * ease((t - 0.45) / (dur - 0.6))          # progressive zoom onto the logo
    iw, ih = ESMA.size
    vw, vh = iw / z, ih / z
    cx, cy = ESMA_LOGO[0] * iw, ESMA_LOGO[1] * ih
    fx = ease((t - 0.45) / (dur - 0.6))
    x0 = (iw - vw) / 2 * (1 - fx) + (cx - vw / 2) * fx; y0 = (ih - vh) / 2 * (1 - fx) + (cy - vh / 2) * fx
    x0 = min(max(x0, 0), iw - vw); y0 = min(max(y0, 0), ih - vh)
    card = ESMA.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((cw, ch), Image.LANCZOS)
    sc = 0.86 + 0.14 * s_in
    card = rounded(card, 46).resize((int(cw * sc), int(ch * sc)), Image.LANCZOS)
    border = Image.new("RGBA", (card.width + 10, card.height + 10), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle([0, 0, border.width - 1, border.height - 1], 50, outline=DA + (230,), width=5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(border, ((W - border.width) // 2, 860 - border.height // 2))
    lay.alpha_composite(card, ((W - card.width) // 2, 860 - card.height // 2))
    img.alpha_composite(glow(lay, 26, 0.7))
    d = ImageDraw.Draw(img)
    a = int(255 * ease_out((t - 0.2) / 0.3))
    text_center(d, (W // 2, 170), "LIMITE ESMA", font(F_LIGHT, 44), WHITE + (a,))
    text_center(d, (W // 2, 1560), "x30", font(F_SANS, 190), DA + (a,))
    text_center(d, (W // 2, 1680), "CLIENTS PARTICULIERS · PAIRES MAJEURES", font(F_LIGHT, 34), WHITE + (a,))
    return img.convert("RGB")

def scene_lev(t, dur):
    img = da_background(t).convert("RGBA")
    ch = 1250; iw, ih = LEV.size; s = ch / ih; full = LEV.resize((int(iw * s), ch), Image.LANCZOS)
    vw = 960
    # title overlay on the empty left half of the visual
    tl = full.convert("RGBA"); d = ImageDraw.Draw(tl)
    d.text((70, ch // 2 - 140), "LEVIER", font=font(F_SANS, 120), fill=WHITE)
    d.text((70, ch // 2 - 10), "x400", font=font(F_SANS, 250), fill=DA)
    d.text((76, ch // 2 + 260), "HORS CADRE ESMA", font=font(F_LIGHT, 46), fill=WHITE)
    fx = ease((t - 1.2) / (dur - 1.45))                     # hold the title, then pan: title -> image
    x0 = int((full.width - vw) * fx)
    win = rounded(tl.crop((x0, 0, x0 + vw, ch)), 46)
    sc = 0.9 + 0.1 * back_out(t / 0.35)
    win = win.resize((int(vw * sc), int(ch * sc)), Image.LANCZOS)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lay.alpha_composite(win, ((W - win.width) // 2, 880 - win.height // 2))
    img.alpha_composite(glow(lay, 26, 0.6))
    return img.convert("RGB")

def scene_marge(t, dur):
    img = da_background(t).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = 1.0 + 0.5 * (1 - ease_out(t / 0.13))                 # slam
    shake = (8 * math.sin(t * 90) * max(0, 1 - t / 0.25), 0)
    f1, f2 = font(F_SANS, int(120 * s)), font(F_SANS, int(250 * s))
    d.text((W / 2 + shake[0], 800), "LA", font=f1, fill=WHITE, anchor="mm")
    d.text((W / 2 + shake[0], 990), "MARGE", font=f2, fill=DA, anchor="mm")
    img.alpha_composite(glow(lay, 30, 1.2))
    return img.convert("RGB")

# --- Part 2 motion graphics (Silence Capital style) ---
JAR = (150, 760, 470, 1240)       # account container (x0, y0, x1, y1): height 480 px = 600 € scale
EUR_PER_PX = 600 / 480
def scene_anim(T):
    """T = seconds since the start of Part 2. Marks: anim_marks[k] = start of sub-beat k."""
    M = anim_marks
    img = da_background(T).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lw = 5
    # header pill
    a = ease_out(T / 0.35)
    if a > 0:
        f = font(F_SANS, 38); txt = "EXEMPLE CONCRET"; tw = d.textlength(txt, font=f)
        x0, y0 = W / 2 - tw / 2 - 34, 300
        d.rounded_rectangle([x0, y0, W - x0, y0 + 76], 38, outline=WHITE + (int(255 * a),), width=4)
        d.text((W / 2, y0 + 39), txt, font=f, fill=WHITE + (int(255 * a),), anchor="mm")
    # account jar
    if T >= M[1]:
        u = ease_out((T - M[1]) / 0.5)
        x0, y0, x1, y1 = JAR; h = (y1 - y0) * u
        d.rounded_rectangle([x0, y1 - h, x1, y1], 34, outline=WHITE, width=lw)
        bal = 500 * ease((T - M[1] - 0.2) / 0.9)
        used = 0
        lvl = (bal - used) / EUR_PER_PX
        if lvl > 1:
            d.rounded_rectangle([x0 + 12, y1 - 12 - lvl, x1 - 12, y1 - 12], 24, fill=DA + (210,))
        d.text(((x0 + x1) / 2, y1 + 60), "COMPTE", font=font(F_LIGHT, 40), fill=WHITE, anchor="mm")
        d.text(((x0 + x1) / 2, y0 - 70), f"{int(round(bal - used))} €", font=font(F_SANS, 78), fill=WHITE, anchor="mm")
    # right column: chart (beats 2-4) then leverage + margin (5-8)
    RX0, RX1, RY0, RY1 = 560, 1000, 780, 1180
    if M[2] <= T < M[5]:
        fade = 1 - ease((T - (M[5] - 0.3)) / 0.3)
        al = int(255 * fade)
        u = ease_out((T - M[2]) / 1.4)
        pts = [(0, .55), (.12, .5), (.22, .62), (.34, .44), (.46, .52), (.58, .36), (.7, .42), (.82, .28), (1, .32)]
        xy = [(RX0 + px * (RX1 - RX0), RY0 + py * (RY1 - RY0)) for px, py in pts]
        k = u * (len(xy) - 1); n = int(k); seg = xy[:n + 1]
        if n < len(xy) - 1:
            fr = k - n; seg.append((xy[n][0] + (xy[n + 1][0] - xy[n][0]) * fr, xy[n][1] + (xy[n + 1][1] - xy[n][1]) * fr))
        if len(seg) > 1: d.line(seg, fill=WHITE + (al,), width=lw, joint="curve")
        d.text((RX0, RY0 - 70), "EUR/USD", font=font(F_LIGHT, 40), fill=WHITE + (al,), anchor="lm")
        if T >= M[2] + 0.9:
            b = back_out((T - M[2] - 0.9) / 0.35)
            d.text((RX1, RY0 - 70), "LOT 0,20", font=font(F_SANS, int(48 * max(b, .01))), fill=DA + (al,), anchor="rm")
        if T >= M[3]:
            b = back_out((T - M[3]) / 0.35)
            d.text(((RX0 + RX1) / 2, RY1 + 110), "20 000 €", font=font(F_SANS, max(1, int(96 * b))), fill=WHITE + (al,), anchor="mm")
            d.text(((RX0 + RX1) / 2, RY1 + 190), "D'EXPOSITION", font=font(F_LIGHT, 36), fill=WHITE + (al,), anchor="mm")
        if T >= M[4]:
            u2 = ease_out((T - M[4]) / 0.4); ys = RY0 + 0.75 * (RY1 - RY0)
            x = RX0 + (RX1 - RX0) * u2
            for xx in range(RX0, int(x), 34): d.line([(xx, ys), (min(xx + 18, x), ys)], fill=RED + (al,), width=4)
            if u2 > 0.6: d.text((RX1, ys + 44), "STOP : −10 €", font=font(F_SANS, 40), fill=RED + (al,), anchor="rm")
    in_margin = (M[6] <= T < M[7]) or T >= M[8]
    if T >= M[5] and in_margin:
        lev = 400 if T >= M[7] else 30
        d.text((780, 520), f"LEVIER x{lev}", font=font(F_SANS, 52), fill=DA, anchor="mm")
    if T >= M[5] and not in_margin:
        lev = 400 if T >= M[7] else 30
        k0 = M[7] if lev == 400 else M[5]
        b = back_out((T - k0) / 0.4)
        ang = (-8 if lev == 30 else -26) * ease_out((T - k0) / 0.6)
        cx, cy, L = 780, 900, 220
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d.polygon([(cx, cy + 8), (cx - 36, cy + 70), (cx + 36, cy + 70)], outline=WHITE, width=lw)
        d.line([(cx - L * ca, cy - L * sa), (cx + L * ca, cy + L * sa)], fill=WHITE, width=lw + 1)
        d.text((cx, 760), "LEVIER", font=font(F_LIGHT, 40), fill=WHITE, anchor="mm")
        d.text((cx, 1060), f"x{lev}", font=font(F_SANS, max(1, int(120 * b))), fill=DA, anchor="mm")
    def margin_bar(T0, amount, ok):
        """Margin column next to the account jar, same baseline and scale."""
        u = ease_out((T - T0) / 0.7)
        jx0, jy0, jx1, jy1 = JAR
        base = jy1 - 12
        hpx = amount / EUR_PER_PX * u
        bx0, bx1 = 640, 920
        col = (GREEN if ok else RED) if T > T0 + 0.9 else WHITE
        if hpx > 2: d.rounded_rectangle([bx0, base - hpx, bx1, base], 20, outline=col, width=lw)
        d.text(((bx0 + bx1) / 2, jy1 + 60), "MARGE", font=font(F_LIGHT, 40), fill=WHITE, anchor="mm")
        d.text(((bx0 + bx1) / 2, base - hpx - 50), f"{int(round(amount * u))} €", font=font(F_SANS, 64), fill=col, anchor="mm")
        ref = base - 500 / EUR_PER_PX                          # account level (500 €)
        for xx in range(jx0 - 10, bx1 + 40, 30): d.line([(xx, ref), (xx + 15, ref)], fill=DA, width=3)
        if T > T0 + 0.9:
            sc = back_out((T - T0 - 0.9) / 0.3)
            d.text((W / 2, 1500), "667 € > 500 €" if not ok else "50 € < 500 €", font=font(F_SANS, 54 * sc), fill=WHITE, anchor="mm")
            d.text((W / 2, 1590), "TRADE IMPOSSIBLE" if not ok else "TRADE OUVERT",
                   font=font(F_SANS, 76 * sc), fill=(GREEN if ok else RED), anchor="mm")
    if M[6] <= T < M[7]: margin_bar(M[6], 667, False)
    if T >= M[8]: margin_bar(M[8], 50, True)
    img.alpha_composite(glow(lay, 16, 1.5))
    return img.convert("RGB")

# ------------------------------------------------------------------ captions (@planfomo style)
words = [w for s in json.load(open(WORDS)) for w in s["words"]]
CAPS = []   # (t_start, t_end, token, is_emphasis)
for p in pieces:
    if p["o"].get("nocap"): continue
    toks = p["text"].split(" ")
    ww = [w for w in words if w["s"] >= p["a"] - 0.15 and w["e"] <= p["b"] + 0.15]
    if len(ww) == len(toks): st = [max(w["s"], p["a"]) for w in ww]
    else:
        s0 = max(ww[0]["s"], p["a"]) if ww else p["a"]; s1 = min(ww[-1]["e"], p["b"]) if ww else p["b"]
        st = [s0 + (s1 - s0) * k / len(toks) for k in range(len(toks))]
    for k, tok in enumerate(toks):
        s = p["t0"] + st[k] - p["a"]
        e = p["t0"] + (st[k + 1] - p["a"] if k + 1 < len(toks) else p["dur"])
        CAPS.append((s, e, tok, tok in p["o"].get("em", [])))
CAP_Y = {"default": 1470, "anim": 1830}
def draw_caption(img, tnow, kind):
    for s, e, tok, em in CAPS:
        if s <= tnow < e:
            word = tok.strip(",.?")
            pop = back_out((tnow - s) / 0.12, 2.2)
            size = int((104 if em else 86) * (0.85 + 0.15 * pop))
            f = font(F_SERIF if em else F_SANS, size)
            y = CAP_Y["anim"] if kind.startswith("anim") else CAP_Y["default"]
            if kind in ("esma",): y = 1800
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            d.text((W / 2, y), word, font=f, fill=(0, 0, 0, 170), anchor="mm")
            sh = lay.filter(ImageFilter.GaussianBlur(10))
            d2 = ImageDraw.Draw(sh)
            d2.text((W / 2, y), word, font=f, fill=(DA if em else WHITE) + (255,), anchor="mm")
            base = img.convert("RGBA"); base.alpha_composite(sh); return base.convert("RGB")
    return img

# ------------------------------------------------------------------ video
REUSE = os.environ.get("REUSE_VIDEO") == "1" and os.path.exists(os.path.join(TMP, "video.mp4"))
enc = None if REUSE else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                        "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", os.path.join(TMP, "video.mp4")], stdin=subprocess.PIPE)

def face_frames(p):
    kind = p["kind"]
    if kind == "hook":
        vf = TONEMAP + "," + CROPS["A_wide"]; fw, fh = 676, 1202
    else:
        c = CROPS[kind]; c = c.format(cx=int(min(max(p["o"].get("cx", .5) * 1080 - 416, 0), 248))) if c else None
        vf = ",".join([TONEMAP] + ([c] if c else []) + [f"scale={W}:{H}:flags=lanczos"] + (["unsharp=5:5:0.5"] if c else []))
        fw, fh = W, H
    pr = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{p['a']:.4f}", "-i", SRC, "-map", "0:v:0", "-an",
                           "-vf", vf, "-frames:v", str(p["n"]), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE)
    for k in range(p["n"]):
        buf = pr.stdout.read(fw * fh * 3)
        if len(buf) < fw * fh * 3: break
        fr = Image.frombuffer("RGB", (fw, fh), buf)
        if kind == "hook":
            tt = k / FPS; stop = 83.87 - p["a"]                # zoom stops on the last phrase
            z = 1 + 0.42 * ease_out(min(tt / stop, 1)) if tt < stop else 1.42
            vw, vh = fw / z, fh / z; cx, cy = 0.55 * fw, 0.41 * fh
            x0 = min(max(cx - vw * 0.55, 0), fw - vw); y0 = min(max(cy - vh * 0.41, 0), fh - vh)
            fr = fr.crop((int(x0), int(y0), int(x0 + vw), int(y0 + vh))).resize((W, H), Image.LANCZOS)
        yield fr
    pr.wait()

fi = 0
pieces_to_render = [] if REUSE else pieces
for p in pieces_to_render:
    kind = p["kind"]
    if kind in ("hook", "A_wide", "A_close", "C_wide", "C_close"): gen = face_frames(p)
    elif kind == "esma":  gen = (scene_esma(k / FPS, p["dur"]) for k in range(p["n"]))
    elif kind == "lev":   gen = (scene_lev(k / FPS, p["dur"]) for k in range(p["n"]))
    elif kind == "marge": gen = (scene_marge(k / FPS, p["dur"]) for k in range(p["n"]))
    else:                 gen = (scene_anim(p["t0"] - anim_t0 + k / FPS) for k in range(p["n"]))
    for k, fr in enumerate(gen):
        tnow = p["t0"] + k / FPS
        fr = draw_caption(fr, tnow, kind)
        # short flash from the face section into Part 2 (and back), DA-coloured
        if kind == "anim:0" and k < 5 or kind == "C_close" and k < 5:
            a = 1 - k / 5
            fr = Image.blend(fr, Image.new("RGB", (W, H), DA), 0.3 * a)
        enc.stdin.write(fr.tobytes()); fi += 1
    print(f"piece {p['i']:02d} {kind:8s} out {p['t0']:6.2f}s  ({p['n']} frames)", flush=True)
if not REUSE: enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio: speech + SFX
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit(f"FAILED {cmd[:6]}\n{r.stderr[-2000:]}")
    return r
fc, lab = [], []
for p in pieces:
    fc.append(f"[0:a]atrim=start={p['a']:.4f}:end={p['b']:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,"
              f"afade=t=out:st={p['dur']-0.012:.4f}:d=0.012[a{p['i']}]"); lab.append(f"[a{p['i']}]")
fc.append("".join(lab) + f"concat=n={len(pieces)}:v=0:a=1,highpass=f=80,"
          "acompressor=threshold=-24dB:ratio=2.5:attack=5:release=120:makeup=2[sp]")
speech = os.path.join(TMP, "speech.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[sp]", "-ac", "1", "-ar", str(SR), speech])
wv = wave.open(speech); sp = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(np.float32) / 32768

N = int(TOTAL * SR) + SR; sfx = np.zeros(N, np.float32); rng = np.random.default_rng(1)
def put(t0, x, g):
    i = int(t0 * SR); j = min(N, i + len(x)); sfx[i:j] += g * x[: j - i]
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
def tone(f0, d, f1=None, r=0.2, a=0.003):
    n = int(d * SR); f = np.linspace(f0, f1 or f0, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(n, a, r)
def noise_band(d, lo, hi):
    x = rng.normal(0, 1, int(d * SR)); X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR)
    X[(fr < lo) | (fr > hi)] = 0; y = np.fft.irfft(X, len(x)); return y / (np.abs(y).max() + 1e-9)
def whoosh(d=0.45):
    y = noise_band(d, 400, 6000); n = len(y); e = np.sin(np.linspace(0, np.pi, n)) ** 2; return y * e
def pop(): return tone(950, 0.09, 380, r=0.035)
def tick(): return tone(2400, 0.03, 1800, r=0.008)
def impact():
    y = 0.9 * tone(70, 0.9, 38, r=0.28); n = int(0.15 * SR)
    y[:n] += 0.5 * noise_band(0.15, 60, 2500)[:n] * env(n, 0.001, 0.04); return y
def reverb(x, wet=0.6, tail=2.0):
    y = np.concatenate([x, np.zeros(int(tail * SR), np.float32)]); out = y.copy()
    for dl, g in ((0.0297, .78), (0.0371, .76), (0.0411, .74), (0.0437, .72)):
        dn = int(dl * SR); c = y.copy()
        for k in range(dn, len(c), dn): c[k:k + dn] += g * c[k - dn:k][: len(c[k:k + dn])]
        out += wet * 0.25 * c
    return out
def lowpass(x, fc_):
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + (fr / fc_) ** 4); return np.fft.irfft(X, len(x))
def mt_error_tunnel():
    """MetaTrader-like 'order refused' tone (two low bell strikes) with a resonant tunnel tail."""
    def bell(f):
        return sum(g * tone(f * m, 1.6, r=0.45 / m ** 0.5) for m, g in ((1, 1), (2.01, .5), (3.02, .25), (4.2, .12)))
    x = np.concatenate([bell(233), np.zeros(int(0.02 * SR))]); x2 = bell(174.6)
    y = np.zeros(int(2.0 * SR)); y[: len(x)] += x; y[int(0.16 * SR): int(0.16 * SR) + len(x2)] += x2
    y = reverb(y.astype(np.float32), 0.9, 1.5); y = lowpass(y, 1800); return y / np.abs(y).max()
def buzz():
    t = np.arange(int(0.32 * SR)) / SR; sq = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.5
    g = ((t % 0.16) < 0.12).astype(np.float32); return lowpass(sq * g * env(len(t), 0.002, 0.3), 1200)
def success(): return np.concatenate([tone(880, 0.12, r=0.08), tone(1320, 0.35, r=0.18)])
def riser(d):
    n = int(d * SR); y = noise_band(d, 300, 4000) * np.linspace(0, 1, n) ** 2 * 0.6
    return y + 0.25 * tone(200, d, 520, r=10, a=d * 0.8)[:n]

pt = {p["kind"]: p for p in pieces}
hook = pt["hook"]
put(hook["t0"], riser(83.87 - hook["a"]), 0.10)                       # tension under the zoom
put(hook["t0"] + 84.62 - hook["a"], mt_error_tunnel(), 0.55)          # the refused order
put(pt["esma"]["t0"] - 0.2, whoosh(), 0.35); put(pt["esma"]["t0"] + 0.22, pop(), 0.4)
put(pt["lev"]["t0"] - 0.2, whoosh(), 0.35); put(pt["lev"]["t0"] + 0.6, whoosh(0.9) * 0.6, 0.25)
put(pt["marge"]["t0"], impact(), 0.75)
A = anim_t0; M = anim_marks
put(A - 0.25, whoosh(), 0.4); put(A + 0.05, pop(), 0.4)
put(A + M[1], pop(), 0.4)
for k in range(9): put(A + M[1] + 0.2 + k * 0.1, tick(), 0.18)        # balance counting up
put(A + M[2], whoosh(1.2) * 0.5, 0.22); put(A + M[2] + 0.9, pop(), 0.4)
put(A + M[3], pop(), 0.45); put(A + M[4], tick(), 0.35)
put(A + M[5], whoosh(), 0.3); put(A + M[5] + 0.1, pop(), 0.4)
put(A + M[6], riser(0.8), 0.12); put(A + M[6] + 0.9, buzz(), 0.35)
put(A + M[7], whoosh(), 0.3); put(A + M[7] + 0.1, pop(), 0.4)
put(A + M[8], riser(0.8), 0.12); put(A + M[8] + 0.9, success(), 0.3)
put(pt["C_close"]["t0"] - 0.2, whoosh(), 0.35)

mix = np.zeros(N, np.float32); mix[: len(sp)] += sp; mix += sfx
mix = mix[: int(TOTAL * SR)]
mixf = os.path.join(TMP, "mix.wav")
with wave.open(mixf, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767).astype(np.int16).tobytes())
def lufs(f):
    e = run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128", "-f", "null", "-"]).stderr
    return float(e[e.rfind("I:"):].split()[1])
st = os.path.join(TMP, "stereo.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", mixf, "-af", "pan=stereo|c0=c0|c1=c0", st])
gain = -14.0 - lufs(st)
audio = os.path.join(TMP, "audio.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", st, "-af",
     f"volume={gain:.2f}dB,aresample=192000,alimiter=limit=0.79:level=false,aresample=48000", audio])
run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(TMP, "video.mp4"), "-i", audio, "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT])
json.dump(dict(total_s=round(TOTAL, 3), pieces=[{k: v for k, v in p.items() if k != "o"} for p in pieces]),
          open(os.path.join(OUTDIR, "cutlist_v2.json"), "w"), indent=1, ensure_ascii=False)
print(f"done {OUT} {TOTAL:.2f}s, audio {lufs(audio):.1f} LUFS")
