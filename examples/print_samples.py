"""Print the first three clips from the canonical manifest."""
import sys
sys.path.insert(0, '..')
from loader import load_manifest

for i, rec in enumerate(load_manifest('clean_v1_verified.jsonl', root='.')):
    print(rec['clip_id'], rec.get('game'), rec['targets']['target_narration'][:100])
    if i >= 2:
        break
