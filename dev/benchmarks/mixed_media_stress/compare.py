"""Compare the preserved graphite contract across two actually installed wheels."""
import json
from pathlib import Path
import sys

old,new,ink=[json.loads(Path(p).read_text()) for p in sys.argv[1:]]
assert old["version"]=="1.3.0"
assert new["version"]=="1.3.1" and ink["version"]=="1.3.1"
assert old["mode"]==new["mode"]=="graphite" and ink["mode"]=="ink"
for field in ("protocol_sha256","script_sha256","python","numpy","pillow","counts","actions","frames"):
    assert old[field]==new[field]==ink[field],field
for field in ("profile_digest","drawing_state_hash","action_log_sha256","final_pixel_sha256","frame_rgb_hashes"):
    assert old[field]==new[field],field
assert old["mechanical_gate"]==new["mechanical_gate"]==ink["mechanical_gate"]=="PASS"
print("PINNED_V130_GRAPHITE_PARITY_PASS",json.dumps({
    "frames":old["frames"],"final_pixel_sha256":old["final_pixel_sha256"],
    "profile_digest":old["profile_digest"],"gif_byte_identity":old["gif_sha256"]==new["gif_sha256"],
    "baseline_total_sec":old["total_sec"],"current_graphite_total_sec":new["total_sec"],
    "current_ink_total_sec":ink["total_sec"]
}))
