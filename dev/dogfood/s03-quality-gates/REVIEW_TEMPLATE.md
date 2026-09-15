# S03 class review template

State: `NOT_RUN | BLOCKED | PASS`  
Class: `<S03.n / class name>`  
Date: `<YYYY-MM-DD>`

## Run identity

- reference identifier/source:
- reference SHA-256 or stable source locator when available:
- worker/model/configuration when available:
- fresh-worker confirmation: `yes / no / unverified`
- skill/source commit:
- package identity:
- renderer family:
- session ID:

`PASS` requires `fresh-worker confirmation: yes`. A `BLOCKED` review may record `no` or
`unverified` when provenance itself is part of the blocking evidence; do not upgrade uncertain
provenance into a PASS claim.

## Required artifacts

Record a path plus SHA-256 for every produced artifact. If an artifact is committed, use its repository path. If kept local for size/privacy reasons, keep the reviewed filename and hash here.

```text
session.json       <path>  <sha256>
final.png          <path>  <sha256>
timelapse.gif      <path>  <sha256>
comparison         <path>  <sha256>
```

Timelapse requirements:

- canonical action 0 → latest;
- normally `every_n=4`;
- PNG and GIF use the same pencil-renderer family;
- no hidden earlier session substituted for the reviewed final.

If the class is BLOCKED because an additional comparison worker omitted source/session evidence,
anchor the formal artifact block above to the best-preserved executed run and list supplementary
workers separately. Missing supplementary evidence must remain a blocking note when it materially
limits the claim.

## Whole-read verdict

- pose/composition:
- perspective propagation:
- silhouette / overlap / contact:
- subject specificity vs generic symbols:
- line hierarchy at presentation scale:
- construction/search-mark retirement:

State whether the drawing became **more specific** or merely **busier** after the last accepted local group.

## Subject-local review

Fill the applicable rows; mark truly non-applicable rows `N/A` rather than silently omitting them.

| Area | PASS/BLOCKED/N/A | Visible evidence |
| --- | --- | --- |
| head orientation / face feature consequence |  |  |
| hair mass → clump → selected accent |  |  |
| torso / pelvis orientation and depth |  |  |
| arms / sleeves avoid rail or tube shorthand |  |  |
| legs / trousers preserve taper / insertion / rotation |  |  |
| hands / feet / shoes preserve observed orientation |  |  |
| prop axis / thickness / body contact |  |  |
| clothing fold/hatch causality |  |  |
| environment/context line ownership |  |  |

## Line ownership audit

List any visible surviving stroke/group whose owner is ambiguous. If none remain, state `none observed`.

```text
mark/group:
primary owner:
evidence:
verdict: KEEP / SOFTEN / RETIRE
```

## KEEP / SOFTEN / RETIRE audit

Summarize provisional/construction families still present in the final drawing.

| Mark family | Decision | Why |
| --- | --- | --- |
|  | KEEP / SOFTEN / RETIRE |  |

A large set of faint marks is not automatically acceptable. If stronger description replaces the information, default to RETIRE.

## Top remaining visible residuals

Name the three largest residuals, or explicitly state that fewer than three remain.

### Residual 1
- symptom:
- visible evidence:
- blocking: `yes/no`
- responsible owner candidate:
- parent premise:
- geometry correct: `yes/no/uncertain`
- material behavior correct: `yes/no/uncertain`
- next disproof test:
- if non-blocking, accepted-limitation rationale:

### Residual 2
- symptom:
- visible evidence:
- blocking: `yes/no`
- responsible owner candidate:
- parent premise:
- geometry correct: `yes/no/uncertain`
- material behavior correct: `yes/no/uncertain`
- next disproof test:
- if non-blocking, accepted-limitation rationale:

### Residual 3
- symptom:
- visible evidence:
- blocking: `yes/no`
- responsible owner candidate:
- parent premise:
- geometry correct: `yes/no/uncertain`
- material behavior correct: `yes/no/uncertain`
- next disproof test:
- if non-blocking, accepted-limitation rationale:

## Renderer-candidate notes

Do not declare a renderer defect here. Record only candidates that should be tested in S04 with authored geometry frozen.

```text
candidate symptom:
why geometry appears correct:
minimal reproduction needed:
expected local pixel/material behavior:
```

## Final class verdict

`PASS | BLOCKED`

Reason:

- `PASS` requires no blocking residual, verified fresh-worker provenance, and complete evidence above.
- `BLOCKED` must identify the highest-impact owner to reopen and may truthfully preserve uncertain provenance.
- Missing evidence cannot be converted into an accepted limitation or a PASS claim.
