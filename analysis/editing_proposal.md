# Editing proposal — `video_01_brut_nugz.MOV`

**Status: proposal only. No edit has been made, and none will be until you approve.**

## Recommended structure — vertical short of about 50 s (9:16, Reels/TikTok/Shorts)

| Part | Source in / out | Length | Content | Treatment |
|---|---|---|---|---|
| 1. Hook | 1:20.3 → 1:24.7 (alt. 1:13.3 → 1:18.3) | ~4.5 s | « Et si je te disais qu'en Europe tu peux préparer un trade avec même pas 10 € de risque… et ne même pas pouvoir l'ouvrir. » | Punch-in crop on the subject (Setup A framing is weak). Big on-screen text: **« 10 € de risque… et impossible d'entrer ? »** |
| 2. The rule | 2:44.4 → 2:51.9 | ~7.5 s | x30 in the EU vs x400 elsewhere | Same crop. Overlays **x30 🇪🇺** / **x400**, with a small note: *« paires de devises majeures, clients particuliers »* |
| 3. The pivot | 2:52.8 → 3:00.3 | ~7.5 s | « La différence : la marge… » | Keyword on screen: **MARGE** |
| 4. Example + payoff | 7:30.2 → 7:58.5 | ~28 s | 500 € account, 0.20 lot = 20 000 €, margin 667 € (x30) vs 50 € (x400), closing question | Setup B (better framing). Animated numbers: **500 €** → **20 000 €** → **667 € > 500 € ❌** vs **50 € ✅**. Ends on the question as the CTA |
| **Total** | | **≈ 48–50 s** | | |

Cut points are taken from the transcript's word timestamps (±0.5 s). Before rendering,
each in/out will be tightened to the actual waveform, with 3–6 frames of handle so
breaths don't get clipped.

## Within-take tightening (optional, after you listen)

- Take #19 is 28 s and has small hesitations. Jump cuts could bring it to about 22–24 s.
  The usual short-form style is about one cut per sentence.
- Remove the « alors là » fillers if they read as hesitations.

## Technical plan (for the edit phase — not executed)

1. **Never touch** `original/video_01_brut_nugz.MOV`. Every render reads from it and writes
   to `exports/`.
2. **Cut list** in `scripts/` (JSON: in/out per part). Render with ffmpeg, frame-accurate
   by re-encoding (keyframes are every ~0.93 s, so stream-copy cuts would be inaccurate).
3. **Colour**: the source is HDR HLG BT.2020 10-bit with Dolby Vision 8.4. Decision needed:
   - **SDR BT.709 (recommended)**: tone-map HLG→SDR (zscale + tonemap). Looks the same
     everywhere; Instagram/TikTok handle HDR inconsistently.
   - Keep **HDR HLG** 10-bit HEVC: brighter on iPhones, but risks a washed-out look on
     other screens.
4. **Video export**: 1080×1920, 30 fps CFR, H.264 High (or HEVC), CRF ~18, yuv420p.
   Setup A shots get a crop and scale, matched in size to Setup B.
5. **Audio**: loudness-normalise to **-14 LUFS integrated, -1 dBTP** (two-pass `loudnorm`),
   light high-pass (~80 Hz). Optional gentle de-noise after listening. Audio stays mono,
   duplicated to both channels.
6. **Captions**: burned-in French subtitles with exact wording (taken from the transcript,
   then corrected by you), plus the keyword overlays above. I will **not** generate any
   text with an AI video model.
7. **Optional additions** (each needs your OK and may cost money):
   - Music bed: you supply a track, or we use a royalty-free one.
   - B-roll/graphic inserts generated with HeliosGen/kie.ai. **Not needed by default**,
     so 0 credits. Per your standing rule, never `seedance-2-mini`.

## Content and fact check (please read before publishing)

The numbers in the video check out:

| Claim | Check | Verdict |
|---|---|---|
| 0.20 lot EUR/USD = 20 000 € | 0.20 × 100 000 units of the base currency (EUR) | ✅ |
| Margin at x30 = 667 € | 20 000 / 30 = 666.67 € | ✅ |
| Margin at x400 = 50 € | 20 000 / 400 = 50 € | ✅ |
| A 500 € account can't open the trade at x30 | 667 € margin needed > 500 € balance | ✅ |
| "10 € de risque" | 0.20 lot EUR/USD ≈ $2/pip ≈ €1.7–1.9/pip, so 10 € ≈ a 5–6 pip stop | ✅ plausible (tight stop) |
| "Les brokers CFD régulés en Europe sont limités à x30" | ESMA's 2018 retail measures: **30:1 is the cap for major currency pairs only**; 20:1 for non-major pairs, gold and major indices, down to 2:1 for crypto. Professional clients are exempt | ⚠️ true for major FX pairs; add the on-screen precision |
| « perte maximale de 167 € » (take at 5:46) | Not used in the final take, and unclear | dropped |

**Regulatory caution (France):** the 2023 "influencer law" (loi n° 2023-451 du 9 juin 2023)
bans influencers from promoting certain high-risk financial contracts (some CFDs, Forex,
binary options). Saying x400 exists *outside* the regulated framework is education. Pointing
viewers to a specific x400 broker, or putting an affiliate link to one, could expose you to
serious legal risk. Keep it educational, add a risk mention, and consider the AMF/ARPP
"certificat de l'influence responsable dans la finance". This is not legal advice; get it
checked if you monetise.

Sources:
- [ESMA — final product intervention measures on CFDs and binary options](https://www.esma.europa.eu/node/85445)
- [ESMA — agrees to restrict CFDs to protect retail investors](https://www.esma.europa.eu/node/84933)
- [ESMA — renewal of CFD measures from 1 May 2019 (PDF)](https://www.esma.europa.eu/sites/default/files/library/esma71-99-1130_esma_renews_cfd_measures_from_1_may_2019.pdf)
- [Irish Times — Europe restricts leverage on CFDs](https://www.irishtimes.com/business/personal-finance/europe-restricts-leverage-on-cfds-to-protect-retail-investors-1.3441764)
- [ESMA — France finfluencers factsheet (PDF)](https://esma.europa.eu/sites/default/files/2026-01/FR_France_fr_-_Finfluencers_factsheet.pdf)
- [AMF — ESMA/AMF advice to finfluencers](https://www.amf-france.org/fr/actualites-publications/actualites/lesma-et-lamf-publient-lattention-des-finfluenceurs-des-conseils-pour-une-promotion-responsable-sur)
- [Vie publique — loi influenceurs](https://www.vie-publique.fr/node/288793)

## Decisions I need from you before editing

1. Hook take: #6 (1:20) or #5 (1:13)? Listen to both.
2. Colour: SDR (recommended) or HDR?
3. Captions: full word-by-word subtitles plus keywords, or keywords only?
4. Music: yes or no? If yes, add the track to `inputs/` or name a style.
5. Target platform(s) and maximum length.
