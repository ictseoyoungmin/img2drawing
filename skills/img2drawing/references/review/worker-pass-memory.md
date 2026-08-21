# Worker Pass Memory

A fresh worker must not mentally restart the current stage after every review pass.

`prepare_stage_review()` writes `pass_memory.json` and embeds the same data in
`worker_packet.json/md`.

## What memory carries
On pass 2+:
- previous review digest;
- previous decision;
- previous remaining concerns;
- previous Agent-reported corrections;
- exact drawing actions executed since the previous review;
- the subset of those actions that are correction operations;
- pass-by-pass concern history;
- pass-by-pass correction history.

The next pass begins from `carried_concerns`, which is the previous review's
`remaining_concerns`.

## What runtime must NOT infer
Runtime memory is continuity infrastructure, not an artistic critic.

It must not infer:
- that a concern was resolved because a stroke was replaced;
- that an edit improved the drawing;
- that two differently worded concerns are semantically equivalent;
- that a stage may advance because concern count decreased.

A correction action proves only that an edit happened.

The Agent must inspect fresh whole/local review artifacts and make a new visual
judgement.

## Example progression

Pass 1 review:
- concerns: A, B, C
- decision: REVISE

Between Pass 1 and Pass 2:
- replace stroke for A
- local edit for B

Pass 2 worker packet automatically carries:
- previous concerns A/B/C;
- the exact correction action IDs and reasons.

Pass 2 review may then state:
- A no longer remains;
- B still remains;
- C still remains.

Pass 3 packet carries only the latest remaining concerns B/C while retaining
historical records of earlier passes.

## Provenance chain
Each review record stores:
- `pass_memory_digest`;
- `parent_review_digest`;
- `carried_concerns`;
- `inter_pass_action_ids`.

This makes the hardening chain reconstructable without relying on conversation memory.
