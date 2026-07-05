"""Loading utilities for the Narrated Puzzle Gameplay Video Corpus.

Manifests are JSONL files; each row describes one clip. Clip payloads
(frames + metadata JSON) live in per-video tar files referenced by the
manifest. See README.md for the schema.
"""

import json
import os
import tarfile
from typing import Dict, Iterator, List, Optional


def load_manifest(manifest_path: str, root: Optional[str] = None) -> Iterator[Dict]:
    """Iterate clip records from a JSONL manifest.

    Args:
        manifest_path: path to a manifest such as clean_v1_verified.jsonl.
        root: optional dataset root; when given, each record gains a
            resolved "tar_path" field pointing at its clip tar.
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if root is not None and "tar" in rec:
                rec["tar_path"] = os.path.join(root, rec["tar"])
            yield rec


def read_clip_members(tar_path: str, clip_id: str) -> Dict[str, bytes]:
    """Return {member_name: bytes} for one clip inside its tar."""
    out = {}
    with tarfile.open(tar_path, "r") as tf:
        for member in tf.getmembers():
            if member.name.startswith(clip_id):
                fobj = tf.extractfile(member)
                if fobj is not None:
                    out[member.name] = fobj.read()
    return out


def load_clip_metadata(tar_path: str, clip_id: str) -> Dict:
    """Load the <clip_id>.json metadata record from a clip tar."""
    members = read_clip_members(tar_path, clip_id)
    key = clip_id + ".json"
    if key not in members:
        raise KeyError(f"{key} not found in {tar_path}")
    return json.loads(members[key].decode("utf-8"))


def load_streaming_episodes(episodes_path: str) -> List[Dict]:
    """Load the labeled streaming episodes file into a list."""
    with open(episodes_path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
