# S09 — Resumable streaming timelapse exporter

State: **production integration slice / resumable writer**

S09 moves the GIF writer itself out of the all-frames-in-memory / all-frame-PNG-spool model. It does not yet replace the canonical renderer with the S02–S08 incremental compositor; instead it creates the durable production writer/checkpoint contract that the exact incremental renderer can plug into next without changing resume semantics.

## What changes

`export_timelapse_streaming()`:

- renders only one staging PNG at a time;
- uses one deterministic global GIF palette;
- optionally writes only the changed GIF bounding box for subsequent frames;
- fsyncs each committed GIF frame and append-only frame journal;
- atomically replaces `checkpoint.json` after a frame is durable;
- resumes from the last committed frame boundary;
- truncates uncommitted/corrupt GIF and journal tails before append;
- rejects a checkpoint when session digest, final state, sampling, renderer contract, palette size, delta mode, or overlay mode changed;
- keeps final native-frame parity against one canonical final render;
- atomically closes the final rename boundary and can recover when interruption occurs between completed checkpoint/manifest and the final GIF rename.

The output directory contains:

```text
checkpoint.json
frames.journal.jsonl
timelapse.tmp.gif   # while incomplete
timelapse.gif       # after completion
manifest.json
.frame.png           # one overwritten staging frame while running
```

No per-frame PNG directory is created.

## Durable frame commit order

```text
write GIF frame
→ flush + fsync GIF
→ append frame journal record
→ flush + fsync journal
→ atomic checkpoint.json replace
```

If a process/WSL interruption lands after any earlier step, resume truncates both append-only files to the byte offsets stored in the last checkpoint and continues without duplicating a committed frame.

## Resume compatibility key

The checkpoint binds:

- session id;
- action-log SHA-256;
- final state SHA-256;
- final history cursor;
- sampling mode/every_n;
- renderer id + renderer kwargs;
- final-renderer kwargs;
- palette color count;
- delta-bbox mode;
- debug-overlay mode.

A mismatch fails closed with `ResumeMismatchError` instead of silently appending incompatible frames.

## Regression

`dev/tests/test_streaming_timelapse_resume.py` covers:

1. uninterrupted every_n=2 export;
2. forced interruption after 3 committed frames;
3. injected corrupt partial GIF tail;
4. resume/truncate/append;
5. byte-identical final GIF and decoded-frame sequence versus uninterrupted export;
6. final native-frame parity;
7. recovery of the final atomic rename boundary;
8. sampling-contract mismatch rejection.

The local pre-PR regression passes `2 passed`.

## Boundary to S02–S08

This slice intentionally leaves the renderer callback contract intact. The current implementation still calls the canonical renderer for each selected state. The next integration step is to place the proven S05 forward traversal + S07 alpha-active exact compositor + S08 eligibility/fallback behind the same streaming writer. Resume/checkpoint format should remain stable while that renderer implementation changes.
