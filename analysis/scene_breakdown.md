# Scene breakdown — `video_01_brut_nugz.MOV`

Source: 8 min 20.9 s, one continuous iPhone recording (no camera cuts: scene detection
at threshold 0.25 found none). Language: French. Topic: **CFD leverage in Europe (x30)
vs x400 and how margin can stop a small account from opening a trade.**

## How this was analysed (and its limits)

| Method | Coverage | Confidence |
|---|---|---|
| 100 frames, one every 5 s, HDR→SDR tone-mapped (`contact_sheet_5s.jpg`) | whole video, sampled | High for framing and blocking; anything shorter than about 5 s between samples can be missed |
| Whisper `small` speech-to-text with word timestamps (`transcript_takes.txt`, `transcript_words.json`) | whole audio | Good. Some words are misheard (e.g. "trésor" = *trader*, "l'horreur USD" = *l'EUR/USD*). Timestamps can drift ±0.5 s, more inside long pauses |
| `silencedetect` (-40 dB, ≥1.5 s) and EBU R128 loudness | whole audio | High (measured) |
| Average brightness every second | whole video | High (measured) |

I have **not listened** to the audio as a human would. I can't judge delivery energy,
diction, room echo or noise by ear; those notes are inferred from the measurements.
Lines marked **(verify by ear)** need a listen before the cut is final.

## Two visual setups

| | Setup A — seated at desk | Setup B — standing, holding a football |
|---|---|---|
| Time | 0:00 → about 3:15 | about 5:15 → 8:21 (close-up interlude from 3:45 to 5:15) |
| Framing | Wide, static. The subject sits on the **far right edge**, often cut by the frame; about 60 % of the frame is empty wall and ceiling; the curved monitor is cut on the left edge | Medium shot, centred, chest-up. Much better framing for 9:16 |
| Light | Dim warm room light plus the monitor's pink/purple glow; face small and fairly dark | Same room, purple/pink light on the wall behind (strong coloured shadow). Face readable |
| Usable? | Hook and the "leverage" section are spoken here | The whole "concrete example" section, including the **complete 28 s take** |

Visible in every speaking shot: a small black handheld object held at the chin. It looks
like a wireless mic transmitter used as a handheld mic (clearest at 4:50). The audio
track is mono, which fits an external mic, but this is inferred, not proven.

## Chronological breakdown

| # | Time | What we see | What is said (auto-transcript, cleaned) | Status |
|---|---|---|---|---|
| 1 | 0:00 – 0:15 | Empty room, desk chair, monitor glow. Nobody in frame | (silence) | ❌ dead time |
| 2 | 0:15 – 0:25 | He walks in and sits at the desk, right edge | (silence) | ❌ |
| 3 | 0:25 – 0:43 | Seated, mic at chin | **Hook take 1** ("vous" form): « Si je vous disais qu'en Europe vous pouvez préparer un trade avec même pas dix euros de risque… et ne pas pouvoir rentrer dedans. » Long pause in the middle (27 → 36 s) | ❌ broken, superseded |
| 4 | 0:52 – 1:11 | Seated | **Hook take 2** ("vous"), broken into three pieces | ❌ superseded |
| 5 | 1:13.3 – 1:18.3 | Seated | **Hook take 3** ("tu"): « Et si je te disais qu'en Europe tu peux préparer un trade avec même pas 10 € de risque, et ne même pas pouvoir l'ouvrir. » | ✅ candidate |
| 6 | 1:20.3 – 1:24.7 | Seated | **Hook take 4** ("tu"), same sentence, ends « …pas pouvoir l'ouvrir. » | ✅ **best candidate** (verify by ear) |
| 7 | 1:25 – 1:44 | He gets up and leaves; hair passes in front of the lens around 1:30 | (silence) | ❌ |
| 8 | 1:44 – 2:17 | Seated again; around 2:00 he stands right next to the lens | « Les brokers CFD en Europe… sont… limités à x30 de levier » — spoken in fragments, long gaps | ❌ unusable as one piece |
| 9 | 2:17 – 2:19 | Seated | « Certains brokers peuvent même monter à x400. » | ⚠️ alternative line |
| 10 | 2:31 – 2:37 | Seated | « Les brokers CFD régulés en Europe sont limités à x30 de levier… » (trails off) | ⚠️ partial |
| 11 | 2:44.4 – 2:51.9 | Seated | **Leverage take**: « Les brokers CFD régulés en Europe sont limités à x30 d'effet de levier. Hors de ce cadre, certains brokers montent à x400. » (the ASR heard "sont limités à 400"; verify by ear) | ✅ **best** |
| 12 | 2:52.8 – 3:00.3 | Seated | **Margin take**: « La différence entre ces deux choses-là : la marge. Et c'est cette marge-là qui peut empêcher un trader particulier de rentrer sur une position. » | ✅ **only take; keep** |
| 13 | 3:00 – 3:15 | He moves to the camera | (silence) | ❌ |
| 14 | 3:15 – 3:45 | **The phone is picked up and moved**: shaky pan over the room (monitor, laptop, door) | (silence) | ❌ unusable, shaky |
| 15 | 3:45 – 4:45 | New framing. He walks up to the phone; extreme close-up, looking down (adjusting the phone or reading?). Darkest stretch of the video | (silence; 42.7 s with no speech, 4:08 → 4:51) | ❌ |
| 16 | 4:50.6 – 4:55.8 | Handheld-style close-up, face fills the frame | « Imagine, tu as 500 € sur ton compte broker, tu veux ouvrir une position. » | ⚠️ different look from setup B; superseded |
| 17 | 4:55 – 5:20 | Phone re-framed again; empty room; he walks back with the ball | (silence; 32 s, 5:00 → 5:32) | ❌ |
| 18 | 5:20 – 7:50 | **Setup B**, standing with the ball | Repeated takes of the "concrete example": 5:33, 5:46 (contains « perte maximale de 167 € », dropped in later takes), 6:06, 6:14, 6:37, 6:55, 7:16, 7:36 | ❌ superseded by #19 |
| 19 | **7:30.2 – 7:58.5** | Setup B, centred, ball in hand, mic at chin | **Complete take (28 s)**: « Exemple concret : tu as 500 € sur ton compte, tu veux ouvrir une position avec un lot de 0,20, ce qui fait 20 000 €. Tu en risques dix. Si tu as seulement un effet de levier de x30, alors la marge nécessaire sera de 667 €. Si par contre tu as un effet de levier de x400, alors d'un coup la marge nécessaire n'est que de 50 €. Est-ce que tu comprends le problème avec la marge sur les brokers CFD ? » | ✅ **core of the video**. Note: in this take he leaves out "sur l'EUR/USD" |
| 20 | 7:58 – 8:21 | He walks to the phone, blurred face close-up, recording stops | (silence) | ❌ |

## Useful material vs total

- Usable speech after choosing the best takes: about **5 + 7.5 + 7.5 + 28 ≈ 48 s**.
- Total silence ≥ 1.5 s: about **6 min 10 s of the 8 min 21 s** (74 %). So roughly 90 %
  of the file is retakes, set-up or dead time. That is normal for raw talking-head
  footage.

## Repeated or unnecessary sections

1. **Hook**: four attempts (0:25–1:25). Keep one (#6, or #5).
2. **Leverage line**: about six attempts (1:44–2:52). Keep #11 (+ #12).
3. **Concrete example**: about eleven attempts (4:50–7:58). Keep #19 (complete and fluent).
4. **Dead time**: 0:00–0:25, 1:25–1:44, 3:00–5:20 (camera moves, close-up fiddling), 7:58–end.

## Image quality, lighting, framing, audio

- **Image**: 10-bit HEVC HDR (HLG, Dolby Vision 8.4), sharp, no visible noise problems in
  the sampled frames. The HDR source must be tone-mapped to SDR (or kept HLG on purpose)
  at export, or colours and contrast will look wrong on many platforms.
- **Lighting**: low-key room plus coloured practical light. Setup B is clearly better lit.
  Setup A's face is small and dim. The darkest stretch (4:08–4:45, brightness about 35 %
  lower) is only in the parts we drop anyway.
- **Framing**: Setup A is badly framed for vertical video: the subject is cut by the right
  edge, with large empty headroom. Cropping in (to about 1.5–2x) toward the right third
  will fix it: the source is 1080×1920, so a 2x crop gives about 540×960 upscaled to
  1080p. That is acceptable for a phone but visibly softer. Setup B needs little or no
  cropping.
- **Look continuity**: A (seated, warm, wide) → B (standing, purple, medium) is a visible
  jump. It can be justified as a chapter change ("Exemple concret") rather than hidden.
- **Audio**: mono AAC 48 kHz. Integrated loudness is **-26.1 LUFS**, about 12 LU too
  quiet for social media (target about -14 LUFS). True peak is -0.4 dBFS, so raising the
  level needs a limiter, not just gain. Loudness range is 17.4 LU (wide, because of
  silences and mic distance). Room echo and noise are not assessed by ear yet.
