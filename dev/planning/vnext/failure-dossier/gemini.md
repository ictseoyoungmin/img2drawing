# Gemini failure dossier

Failure mode: **process-complete R23 run accepted a visually weak drawing**.

## Evidence

- Source log: external evidence ID `gemini-log`
- Source SHA-256: `eea743b1850c368f297f231d34aeda29d7b77016646ecdbe23a1eccfd5886eb1`
- Relevant log ranges: lines 89–129 (claimed completion) and 138–170 (self-evaluation).
- Cross-check: external evidence ID `r23-assessment`, lines 9–14.

## What happened

The fresh Gemini run reported a complete P1→P5 pipeline, including an eight-region
`RegionClosureManifest`, a P4/P5 `ResolvedFormManifest`, retired guide strokes, and
final artifacts (`drawing.png`, `subject_vs_final.png`, `review_manifest.json`). Its
own visual table called gesture, proportion/balance, forms/gear, and line quality
Pass or good.

The independent R23 assessment rejected that acceptance after looking at the final
comparison. It identified material mismatch in:

- back-three-quarter torso rotation and head turn;
- arm overlap/contact with the body;
- shorts/thigh mass, leg stance, and overall body volume;
- rifle/body topology and contact;
- feet/boots, which read as oversized geometric wedges;
- head, which read as a shell-like generic form;
- rifle, which read as a set of long lines rather than a connected object.

The result therefore satisfied the ceremony while failing the drawing goal. The
assessment’s concise diagnosis is: **process complete ≠ visually strong**.

## Root cause and impact

The run could turn the presence of stage artifacts and manifest decisions into a
successful-looking completion record without resolving the highest-impact visual
mismatches. More region fields, review packets, or a stricter manifest would add
ceremony but would not establish that the whole drawing communicates this subject’s
pose.

This is a false-positive workflow failure, not evidence that the pencil renderer,
StrokeIR, action history, checkpoint, replay, or timelapse capabilities should be
discarded.

## B00 disposition

- Keep this run as historical R23 failure evidence.
- Do not reuse its `PASS` claims, artifacts, coordinates, or manifests as vNext
  validation evidence.
- Make visual inspection and agent-owned prioritization primary in vNext; runtime
  evidence remains read-only and state-bound.
- Retest the same subject only through a future vNext dogfood gate, not in B00.

## Authority note

The Gemini log records what the worker claimed and how it self-evaluated. The visual
failure characterization above follows the separate R23 assessment, not the worker’s
own PASS language.
