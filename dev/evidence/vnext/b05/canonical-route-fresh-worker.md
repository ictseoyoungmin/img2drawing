# B05 canonical route — fresh-worker reading evidence

Status: `PASS`
Recorded: 2026-08-31
Method: clean-route reading probe with only the skill, bundled subject, and a new
croquis request in scope

## Input

```yaml
skill: skills/img2drawing/SKILL.md
subject: skills/img2drawing/examples/full_body_croquis/subject.png
request: "이 subject로 stage-free croquis를 그려라"
answer_image: none
task_stage_targets: none
```

## Files read by the fresh route

```yaml
- skills/img2drawing/SKILL.md
- skills/img2drawing/references/INDEX.md
- skills/img2drawing/references/modes/croquis.md
- skills/img2drawing/references/observation/visual-observation.md
- skills/img2drawing/references/construction/gesture-and-masses.md
- skills/img2drawing/references/construction/balance-and-limbs.md
- skills/img2drawing/references/review/residual-correction.md
```

## Files not read by the fresh route

```yaml
legacy_gateway: NO
legacy_files_not_read:
  - skills/img2drawing/references/legacy-r23.md
  - skills/img2drawing/references/stages/*
  - skills/img2drawing/playbooks/*
  - skills/img2drawing/references/review/dual-reference-review.md
  - skills/img2drawing/references/review/when-to-advance.md
```

## Reported route trace

```yaml
first_runtime_selected: DrawingSession
first_authoring_api: author_initial_construct
inspection_api: inspect_initial_construct
loop: observe → draw → inspect → correct → repeat → finish
correction_choices:
  - add explicit stroke with draw/draw_many
  - soften or partially retire a cue with soft_lift/soft_lift_segment
  - remove a complete visible stroke with delete_stroke
fresh_snapshot_after_mutation: required
phase_gate_or_cursor: none
```

## Boundary evidence

`SKILL.md` ends its canonical route with one short R23 continuation pointer. The former
embedded `<details>` body is physically absent, so a worker reading the skill receives no
Pn progression, stage review machinery, manifest contract, or reopen procedure unless it
explicitly chooses the legacy gateway. `INDEX.md` likewise names only `legacy-r23.md` in
its legacy section and leaves the detailed compatibility inventory behind that gateway.
