#!/usr/bin/env bash
# Read-only analysis of the original: metadata, frame timing, loudness, silences, contact sheet.
# Writes only to analysis/ and a temp dir. Never writes to original/.
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="original/video_01_brut_nugz.MOV"; T="$(mktemp -d)"
ffprobe -v error -show_format -show_streams -of json "$SRC" > "$T/probe.json"
ffprobe -v error -select_streams v:0 -show_entries packet=pts_time -of csv=p=0 "$SRC" \
  | sort -n | awk 'NR>1{d=$1-p; c[sprintf("%.4f",d)]++} {p=$1} END{for(k in c) print k" s: "c[k]" frames"}'
ffmpeg -nostats -hide_banner -i "$SRC" -map 0:a:0 \
  -af "silencedetect=noise=-40dB:d=1.5,ebur128=peak=true" -f null - 2>&1 | grep -E "silence_|I:|LRA:|Peak:"
# HDR (HLG) -> SDR tone-map so thumbnails look right; one frame every 5 s with timecode.
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
ffmpeg -v error -y -i "$SRC" -map 0:v:0 -vf "fps=1/5,zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=216:384,drawtext=fontfile=$FONT:text='%{pts\:hms}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7" "$T/t_%03d.jpg"
ffmpeg -v error -y -i "$T/t_%03d.jpg" -frames:v 1 -vf "scale=144:256,tile=20x5:padding=3:color=white" analysis/contact_sheet_5s.jpg
echo "probe JSON (contains GPS — do not commit unredacted): $T/probe.json"
