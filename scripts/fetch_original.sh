#!/usr/bin/env bash
# Download the untouched source from the GitHub Release and verify it byte-for-byte.
# The original is NOT stored in git (428 MB > GitHub's 100 MB file limit); the Release is its home.
set -euo pipefail
cd "$(dirname "$0")/.."
URL="https://github.com/22services/nugz_media_content/releases/download/video-brut-nugz/video_01_brut_nugz.MOV"
SHA="3120823ece49226f823d5b24590b418b4e4573afc767142c064a38885b0fe125"
OUT="original/video_01_brut_nugz.MOV"
mkdir -p original
if [ ! -f "$OUT" ]; then curl -fL --retry 4 -o "$OUT.part" "$URL" && mv "$OUT.part" "$OUT"; fi
echo "$SHA  $OUT" | sha256sum -c -
chmod 444 "$OUT"   # read-only: the original must never be modified
