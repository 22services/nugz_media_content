# nugz_media_content — reel editing workspace

Raw footage lives in GitHub Releases (never in git). `scripts/fetch_original.sh` restores it
read-only with a SHA-256 check. Never modify, rename or transcode files in `original/`;
everything derived goes to `exports/`.

## DA (direction artistique) — applies to EVERY nugz reel

Set by the team on 2026-11-20 (script "Levier ESMA ×30 vs ×400"):

- **Accent colour: `#f4c430`** (saffron yellow). Used for the **dots in the background** of
  every motion-graphics / "animation IA" scene and of the big word cards (e.g. « LA MARGE »).
- **Background: black**, matching the shoot (yellow desk lighting, monitors on, no background
  light).
- **Explainer animations ("animation IA")** use one of the named styles below. They must
  be crisp and unambiguous ("pas de place au doute"). Numbers and text are drawn in the edit,
  never left to an AI video model.
- **Big word cards**: DA background (black + `#f4c430` dots), very large type inside the real
  9:16 safe area, with an impact sound on the word.
- **Captions**: highly readable, in the @planfomo reel style
  (https://www.instagram.com/reel/DfCo1fKslwY/): one word or short group at a time,
  centred, white, with an italic serif accent on key words. Readable fonts list:
  https://www.tiktok.com/@ben_films/video/7322520525169872161 (Montserrat, Avenir Next,
  Barlow, The Bold Font, Fava Black, Made Soulmaze, Rubik, Minion Pro).
- **Sound** (team feedback 2026-11-21: synthesized sounds "look cheap"): only real
  recorded SFX (Mixkit, see `analysis/audio_credits.md`), peak-aligned on the cuts; no
  game-show buzzers. Music: dark trap / dark tech beat around 90–100 BPM, the trading-reel
  sound of the references, entering after the hook, ducked ~15 dB under the voice.

## Animation styles — ALWAYS ask which one when the user adds a new video

When a new raw video arrives, ask the user which animation style to use (list the names
below with one line each) before building the animation scenes. Everything else in the DA
(captions, word cards, sound, `#f4c430`) stays the same whatever the style.

| Style | Look | Reference | How to render |
|---|---|---|---|
| **Grid** | Black background with a `#f4c430` dot grid; minimalist white glowing line icons, charts and outlined containers; one idea per shot. | Silence Capital — https://vm.tiktok.com/ZN8arWp6T/ | `scripts/edit_v2.py` (default, `ANIM_STYLE=grid`). Example: `exports/v3/` |
| **Hologram** | Navy 3D stage with blue perspective laser lines and haze; neon **glass containers** (blue, red = danger, green = OK) with glossy streaks and luminous fills; terminal-style monospace readouts (`› ./commande`, big numbers + cyan units, yellow highlight boxes); faint scanlines. | iv2fi — https://www.instagram.com/reel/DgLK1eZhEkS/ | `ANIM_STYLE=hologram scripts/edit_v2.py` — stage plate `assets/styles/hologram_stage.jpg` (HeliosGen, nano-banana-pro); font IBM Plex Mono. Example: `exports/v4_hologram/` |

To add a style: give it a short name, add a row here, and add a `scene_anim_<name>` renderer
selected by `ANIM_STYLE` in the edit script.

## Video generation

HeliosGen (repo `22services/22creations`, `bin/helios`) and its rules apply: budget rule
(ask before more than 4 paid generations, or any 4K / ≥ 15 s shot), resume rather than
re-run failed jobs, never use `seedance-2-mini`.

## Compliance (finance content, France)

Educational framing only: no broker names, logos or affiliate links. The 2023 influencer law
(loi n° 2023-451) restricts the promotion of high-risk products (some CFDs, Forex).
