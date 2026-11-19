# Nugz Media Content

Repository for original video assets and media editing.

## Workspace layout

| Folder | Content |
|---|---|
| `original/` | Untouched sources (git-ignored; fetched from Releases by `scripts/fetch_original.sh`, SHA-256 verified, read-only) |
| `analysis/` | Metadata (`video_metadata.json`, GPS redacted), `scene_breakdown.md`, `editing_proposal.md`, transcripts, contact sheet |
| `exports/` | Derived renders (git-ignored media) |
| `scripts/` | Reproducible fetch / analysis / transcription scripts |
