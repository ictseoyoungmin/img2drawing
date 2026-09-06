# S06 — Edit-aware dirty-region compositor

State: **CLOSED AS A DEV PROTOTYPE**

Production runtime behavior is unchanged. S06 extends the S04 persistent supersampled graphite canvas beyond append-only histories so the real Lucy 546-action session can cross its replace/delete tail without falling back to full-frame replay.

## Premise

The real Lucy session contains 546 actions:

- 397 `stroke.add`
- 144 `stroke.replace`
- 5 `stroke.delete`

The first replacement begins after the long add-only prefix. S04 therefore proved the incremental idea but could not finish the complete history.

## Edit invalidation rule

For every sampled transition, S06 compares the authoritative current stroke set with the previous sampled state.

- add-only extension: composite only the new cached masks;
- replace/content change: dirty `old_bounds ∪ new_bounds`;
- delete: dirty `old_bounds`;
- multiple disjoint edits: keep separate high-resolution dirty regions instead of one large union.

Each edit region is rebuilt from transparent graphite using the current authoritative active stroke order and exact S02/S03 cached 8-bit material masks. The rebuilt patch **replaces** that region of the persistent high-resolution graphite canvas; this restores graphite that had previously been hidden underneath a deleted/replaced stroke. Only the affected native-resolution area is then Lanczos-resampled using the S04 halo rule.

Explicit eraser-tool strokes remain fail-closed in this prototype because they are destructive ordered operations rather than independently compositable source-over layers. Lucy uses history delete/replace actions, not eraser-tool strokes.

## Hot-path correction

The first implementation still scanned full stroke dataclass equality on every sampled frame. On the long add-only prefix this accidentally reintroduced large O(frames × active geometry) work. S06 reopens that implementation detail and checks authoritative order-prefix plus object identity first. S05 forward replay reuses unchanged immutable `Stroke` objects, so append-only sampling avoids content equality entirely.

## Exact Lucy full replay

Workload:

- 941×1672 output
- supersample 4
- 546 actions
- every_n=4
- 138 sampled frames
- exact S03 material kernel
- S05 forward history traversal

Compute-only full replay:

```text
wall                         21.4456 s
history traversal             0.1489 s
advance/recomposition        18.9820 s
native dirty updates          1.5858 s
first-time materialization   18.3804 s
material cache entries            541
material mask cache          78,977,721 bytes
dirty native pixels           4,713,996
persistent ss4 RGBA canvas  100,694,528 bytes
```

History transitions observed by sampled replay:

```text
added      397
changed    144
removed      5
```

The compositor rebuilt 71 high-resolution edit regions and recomposited 1,652 cached stroke layers across those regions.

The final native frame SHA-256 is exactly the known canonical Lucy final PNG:

```text
ef1baa6e78ceb0adf0ec44fbcde2fd96788e1ab05de56128fd2c14ab8fe54dd0
```

## Edit-frame parity

Independent full recomposition with the exact S03 material cache was run at edit-boundary cursors 392, 396, 400, 448, 540, 544, and 546. All selected full-frame RGBA hashes match the S06 dirty compositor exactly.

Cursor 396 was additionally checked against the production canonical `pillow-pencil-contact-v9` renderer and matched exactly. Cursor 546 matches the previously certified canonical Lucy final PNG exactly.

Synthetic regression separately covers replacement, deletion, and soft-lift-like opacity/content mutation while overlapping strokes are present; every state matches an independent full recomposition.

## Full timelapse proof

A bounded local streaming encoder consumed the 138 exact native frames directly without writing a PNG per frame. It produced a same-resolution 941×1672 GIF in about 22.09 s end-to-end, including rendering and encoding, while preserving exact final PNG parity. The local GIF encoder is evidence only and is not part of the S06 repository change; canonical frame-delivery/manifest cleanup remains a later exporter slice.

## Decision

**S06 premise passes.** Carry forward:

1. S05 forward authoritative history traversal;
2. S02/S03 content-addressed exact material masks;
3. S04 persistent high-resolution graphite canvas and dirty Lanczos output patching;
4. edit dirty-region rebuild from current authoritative active strokes;
5. separate disjoint dirty regions rather than one global edit union.

Production integration is still deferred. The remaining product work is primarily:

- bounded memory / tile-backed persistent canvas strategy;
- explicit eraser/segment edit semantics;
- canonical streaming frame delivery and manifest cleanup;
- removal of redundant final render and corrected work budgeting;
- end-to-end production exporter regression on Lucy and replacement-heavy fixtures.
