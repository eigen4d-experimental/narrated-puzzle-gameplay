# Narrated Puzzle Gameplay Video Corpus

This dataset is a narrated puzzle-gameplay video corpus with clip-level frames, transcripts, metadata, and streaming supervision derived from gameplay videos. The frame-loadable pool contains 76,336 verified clips spanning 755.631 hours, 8,864 source-video/tar units, and 1,311 unique games; the recommended default subset for training and evaluation is `clean_v1_verified.jsonl`, with 32,868 retrievable clips spanning 335.929 hours and 577 unique games. The dataset is intended for research on video-language grounding, narrated gameplay understanding, action anticipation from narration, and streaming speech/gameplay alignment.

## Quickstart

```bash
# Full storage subtree; use the release subset paths when a smaller public mirror is provided.
gcloud storage cp -r gs://eigen4d-data/puzzle-narration/ ./puzzle-narration/
```

```python
from loader import load_manifest

for sample in load_manifest("puzzle-narration/clean_v1_verified.jsonl", root="puzzle-narration"):
    print(sample["clip_id"], sample["game"], sample["targets"]["target_narration"][:120])
    break
```

## Dataset Structure

### Main Manifests

| File | Role | Rows |
|---|---|---:|
| `_collection_verified_clips.jsonl` | Frame-loadable verified clip pool | 76,336 |
| `clean_v1_manifest.jsonl` | Local clean manifest | 51,137 |
| `clean_v1_verified.jsonl` | Canonical retrievable training manifest | 32,868 |
| `streaming_episodes_3way.jsonl` | Labeled streaming episodes | 2,718 |

### Clip Metadata Schema

| Field | Type | Meaning |
|---|---|---|
| `clip_id` | string | Clip identifier encoding source/video and start/end seconds as `<video_id>_<start>_<end>` |
| `video_id` | string | Source video identifier |
| `source` | string | Source collection, such as `twitch`, `youtube_whisper`, or `internet_archive` |
| `game` | string | Game label |
| `title` | string | Source video title |
| `clip` | object | Clip timing and frame metadata |
| `clip.start` | number | Clip start time in seconds |
| `clip.end` | number | Clip end time in seconds |
| `clip.duration` | number | Clip duration in seconds |
| `clip.fps_sampled` | number | Frame sampling rate |
| `clip.num_frames` | integer | Number of sampled frames |
| `clip.frame_times` | list[number] | Frame timestamps relative to the source video |
| `labels.transcript_source` | string | Transcript source label |
| `labels.asr_model` | string | ASR model label |
| `targets.target_narration` | string | Training narration text |
| `targets.raw_narration` | string | Verbatim narration text |
| `targets.segments` | list[object] | Transcript segments aligned to the clip |

### Streaming Episode Schema

| Field | Type | Meaning |
|---|---|---|
| `clip_id` | string | Source clip identifier |
| `game_id` | string | Game identifier |
| `K` | integer | Episode horizon parameter |
| `gate_labels` | JSON value | Three-way frame labels |
| `plan_mem` | JSON value | Planning-memory supervision |
| `weight` | number | Episode weight |
| `event_delta` | number | Event timing delta |
| `tau` | number | Temporal parameter |
| `is_dense_plan` | boolean | Whether dense planning supervision is present |
| `frame_rel_times` | list[number] | Frame times relative to clip start |
| `word_buckets` | list | Word buckets aligned to frames |
| `silence_frames` | JSON value | Silence-frame indicators |
| `role` | string | Episode role |
| `first_time` | number | First event time |
| `activity_weight` | number | Activity weighting value |
| `source` | string | Source collection |

### Per-Clip Payload

Each clip tar contains:

| Path pattern | Meaning |
|---|---|
| `<clip_id>.json` | Clip metadata and targets |
| `<clip_id>*.jpg` frame sequence | Sampled JPEG video frames associated with the clip |
| `<clip_id>.txt` | Verbatim narration |
| `<clip_id>.segments.json` | Timed transcript segments |

### Directory Layout

```text
puzzle-narration/
  clean_v1_manifest.jsonl
  clean_v1_verified.jsonl
  _collection_verified_clips.jsonl
  streaming_episodes_3way.jsonl
  visual_2d_gate.jsonl
  clip_quality.jsonl
  clips_frames/
  whisper/
  internet_archive/
  youtube_diverse/
  twitch/
  twitch_transcripts/
  manifests/by_video/
```

## Statistics

### Corpus Counts

| Manifest / pool | Clips | Source-video units / tars | Unique games | Hours |
|---|---:|---:|---:|---:|
| `_collection_verified_clips.jsonl` frame-loadable pool | 76,336 | 8,864 per-source video/tar units; 8,819 unique video ids | 1,311 | 755.631 |
| `clean_v1_manifest.jsonl` local clean manifest | 51,137 | 6,237 | 1,004 | 502.863 |
| `clean_v1_verified.jsonl` canonical retrievable training manifest | 32,868 | 3,763 | 577 | 335.929 |
| `streaming_episodes_3way.jsonl` labeled streaming episodes | 2,718 | not encoded in file | not computed from file | not encoded in file |

### Canonical Manifest by Source

| Source | Clips | Source-video units | Hours |
|---|---:|---:|---:|
| `twitch` | 17,548 | 3,112 | 170.115 |
| `youtube_whisper` | 13,433 | 604 | 146.079 |
| `internet_archive` | 1,887 | 47 | 19.735 |

### Streaming Labels

| Quantity | Count / rate |
|---|---:|
| Episodes | 2,718 |
| Frames | 53,623 |
| `<silent>` frames | 34,710 |
| `<speak_event>` frames | 15,982 |
| `<speak_plan>` frames | 2,931 |
| Spoken rate | 0.3527 |
| Plan-of-spoken rate | 0.155 |
| Off-game-gated frames | 853 |

### Storage Inventory

| Prefix | Objects | Bytes | Notes |
|---|---:|---:|---|
| `gs://eigen4d-data/puzzle-narration/` | 333,769 | 28,997,015,043,824 | Entire subtree, including raw media, frame tars, transcripts, manifests, and dataset artifacts |

## Construction and Provenance

Candidate videos were enumerated from search, channel, Twitch, YouTube, and Internet Archive sources. Audio was processed with VAD, ASR, word-snapped clip windowing, hallucination and loop filtering, frame extraction, and tar/manifest emission. Frames were sampled at 2 fps, scaled to 320 pixels wide with original aspect ratio, capped at 120 frames per clip, and encoded as JPEG.

Visual filtering used four evenly spaced frames per clip to classify two-dimensional puzzle gameplay, accepting clearly two-dimensional and isometric/semi-three-dimensional puzzle gameplay and rejecting full three-dimensional games, non-puzzle games, trailers, reviews, reactions, blank screens, desktop captures, IRL footage, talking-head footage, facecam-only content, and non-game content. Additional quality fields include narration match, exploration score, reasoning density, first-time likelihood, activity, and supporting signals.

The clean verification pass checked 38,089 manifest entries: 32,868 verified good with speech, 5,221 failed, for an 86.29% verified rate and 13.71% failed rate. Failure reasons were `no_frame_times_or_segments` (3,698), `stream_s1_spread_fail` (1,171), and `no_entry_or_frames` (352). Streaming data uses `DELTA=0.5` seconds, `N_MAX=25`, and `fps=2.0`.

## Loading Utilities

The repository is expected to ship a `loader.py` module with:

```python
from loader import load_manifest, load_clip, load_streaming_episodes

samples = load_manifest("puzzle-narration/clean_v1_verified.jsonl", root="puzzle-narration")
clip = load_clip(next(samples), root="puzzle-narration")  # metadata, frames, narration, segments
episodes = load_streaming_episodes("puzzle-narration/streaming_episodes_3way.jsonl")
```

`load_manifest(path, root=None)` yields clip metadata dictionaries. `load_clip(sample, root)` resolves the per-clip tar payload and returns a dictionary containing metadata, sampled frames, narration text, and transcript segments. `load_streaming_episodes(path)` yields streaming episode dictionaries.
