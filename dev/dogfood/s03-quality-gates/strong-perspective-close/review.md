# S03.1 strong-perspective close figure review

State: `BLOCKED`  
Class: `S03.1 / strong-perspective close figure`  
Date: `2026-09-15`

## Run identity

- reference identifier/source: user-supplied Gojo strong-perspective close figure; Claude package `work/ref.png`
- reference SHA-256 or stable source locator when available: `393e0ca4870079aa1e4723b13847c9d3fcec0750bd659a7827d00d891280a40d`
- worker/model/configuration when available: comparison set labeled `GPT-6 Astra medium`, `Claude Opus 5 high`, `Gemini 3.8 medium`
- fresh-worker confirmation: `unverified` (the packages are user-supplied dogfood, but only package-local evidence is available; the Astra source explicitly reconstructs lost history)
- skill/source commit: uploaded dogfood does not encode one Git commit; renderer/runtime evidence identifies `pillow-pencil-contact-v11 / 1`; S03 review baseline is main after PR #50
- package identity: current dogfood sources identify img2drawing 1.0.3/v11 or recovered 1.0.4-rc0 workspace material; this review does not promote a release
- renderer family: `pillow-pencil-contact-v11 / 1`
- session ID: `vnext-63728daa39f7` (Claude anchor run)

## Required artifacts

The formal artifact block anchors to the Claude run because it preserves the strongest original action/correction history among the supplied packages. Astra and Gemini are supplementary comparison workers below.

```text
session.json opus-img2drawing_croquis_work.zip::work/out/session.checkpoint.json bc9233eccb25fd10c822c334e360940d35350280d83780ed3fa927404bf6dc00
final.png opus-img2drawing_croquis_work.zip::work/out/final.png 623628e3156e5f593688dc3703e8b0090c29ebf56fce6658257c883b77e956af
timelapse.gif 1st-gpt-6-astra-medium.zip::2nd-claude-opus-5-high/work_every_2_actions.gif 79e514e4797e544c13db5cc4e796707d262da6fa7fb0beeff88e1806c639ee87
comparison dogfood_s03_1_review_board.png 6e8aec50db861d74d7568dace79fb23369d66efa1554bb09a954760b1921ce42
```

Supplementary evidence:

- Astra recovered final PNG: `6748dcec916212b3c9b1aa2a22d130971f5fd46f2a547de70cd8094d314ffd90`
- Astra every-2 GIF: `eb01c3c1318d4c717043c5c54a3723f3d506bbbd39de401528a8c8c741c4086d`
- Astra recovered session: `356efd1aa63cfc1e5fb0748f630d0d3812d68268cd9b8df303cf678c239294df`
- Gemini every-2 GIF: `d12a11c90dc8f0d461b63f616736e215dff23a5f03ba2f8a55e30b629925a048`
- Gemini supplied comparison package has no canonical session/source package, so it cannot support a PASS provenance claim.

The Astra recovery README explicitly states that the original workspace/history was absent and that the final visible coordinates were reconstructed; the original correction/deletion history is not claimed to be recovered. That makes Astra useful visual evidence but insufficient canonical fresh-session evidence for PASS.

## Whole-read verdict

- pose/composition: Astra preserves the strongest low-angle composition and foreground-hand emphasis. Claude preserves the broad composition but re-authors identity and hand structure. Gemini loses much of the original projection and reads as a generic diagram.
- perspective propagation: Astra is strongest. Claude keeps a large near hand but its parent hand/arm premise is repeatedly re-authored and no longer follows the reference faithfully. Gemini keeps an enlarged local head/hair area while torso/hand relationships flatten.
- silhouette / overlap / contact: Astra is mostly coherent. Claude's near-hand/coat relation improves through many corrections but remains an authored anatomical solution rather than faithful observed projection. Gemini has unresolved tangencies and generic overlapping primitives.
- subject specificity vs generic symbols: Astra is recognizably closest to the visible subject. Claude intentionally substitutes original styling; Gemini collapses hair to starburst-like symbolic spikes and simplifies the hand/body.
- line hierarchy at presentation scale: all three use the same broad renderer family, but quality differences are dominated by authored geometry/selection rather than renderer behavior. This batch does not isolate a v11 material defect.
- construction/search-mark retirement: Claude does meaningful retirement/correction. Astra recovery cannot prove original construction retirement because the history was reconstructed from final visible marks. Gemini visibly retains weak scaffold/construction lines in the final.

The comparison does not show a renderer-first bottleneck. It shows that instruction execution and reference authority dominate the result.

## Subject-local review

| Area | PASS/BLOCKED/N/A | Visible evidence |
| --- | --- | --- |
| head orientation / face feature consequence | BLOCKED | Claude changes identity/styling by policy-like substitution; Gemini face becomes generic; Astra is visually strong but provenance-limited. |
| hair mass → clump → selected accent | BLOCKED | Astra largely follows mass/clump logic; Claude substitutes a different design; Gemini uses repeated radial/starburst spikes. |
| torso / pelvis orientation and depth | BLOCKED | Claude/Gemini do not preserve the reference projection with sufficient fidelity; Astra is better but not valid fresh canonical evidence. |
| arms / sleeves avoid rail or tube shorthand | BLOCKED | Claude's raised sleeve is simplified and near-hand parent relation is repeatedly reconstructed; Gemini uses diagram-like paired boundaries. |
| legs / trousers preserve taper / insertion / rotation | N/A | reference is a close figure crop without a usable full leg chain. |
| hands / feet / shoes preserve observed orientation | BLOCKED | Claude explicitly corrects the visible near hand toward inferred anatomy instead of preserving reference evidence; Gemini hand is generic; Astra is better visually. |
| prop axis / thickness / body contact | N/A | no primary held prop; eyewear/blindfold contact is secondary. |
| clothing fold/hatch causality | BLOCKED | Claude improves fold ownership but also re-authors design; Gemini fold/context marks remain schematic. |
| environment/context line ownership | N/A | comparison outputs intentionally omit most environment; this class is judged primarily on figure projection. |

## Line ownership audit

- mark/group: Claude near-hand digit fan and coat overlap
- primary owner: near-hand silhouette / web-to-tip digit chains versus coat silhouette
- evidence: the action history contains repeated blocking residuals that reopen wrist entry, digit fan, and coat-overlap premises; final geometry is internally cleaner but no longer faithful to the observed reference hand.
- verdict: RETIRE the anatomy-correction premise; reopen reference authority and observed projection.

- mark/group: Gemini radial hair spikes and persistent light scaffold lines
- primary owner: hair mass/clump and provisional construction
- evidence: repeated starburst rays do not describe observed clump grouping, and long weak construction lines survive after descriptive contours are present.
- verdict: RETIRE.

## KEEP / SOFTEN / RETIRE audit

| Mark family | Decision | Why |
| --- | --- | --- |
| Astra final descriptive silhouette/feature lines | KEEP | visually specific, but they do not prove original construction retirement because the session was reconstructed. |
| Claude reference-substituting identity/anatomy edits | RETIRE | they override visible reference evidence and are the wrong parent premise for a faithful reconstruction task. |
| Claude resolved hand/coat correction history | KEEP as diagnostic evidence | it shows useful observation/correction behavior even though the parent authority premise is wrong. |
| Gemini weak body axes/scaffold lines | RETIRE | descriptive geometry is already present and the lines reduce clarity without owning a visible relation. |
| Gemini radial hair symbol lines | RETIRE | they are generic symbolic repetition rather than observed mass/clump evidence. |

## Top remaining visible residuals

### Residual 1
- symptom: reference identity/design is intentionally replaced in the Claude run.
- visible evidence: final head/hair/eyewear/clothing differ materially from the reference; Claude finish record states that because the reference depicts a protected character, hair design, eyewear, face and coat styling are original while pose/camera are preserved.
- blocking: yes
- responsible owner candidate: reference-authority / task-fidelity instruction execution
- parent premise: visible identity/design may be substituted when the worker believes the reference is protected.
- geometry correct: no
- material behavior correct: uncertain but not causal
- next disproof test: repeat a reference-faithful copyrighted-character drawing task with an explicit instruction that visible design/identity must be preserved and verify the worker does not substitute original styling.
- if non-blocking, accepted-limitation rationale: N/A

### Residual 2
- symptom: visible projected anatomy is corrected toward an inferred anatomically coherent hand.
- visible evidence: Claude finish record states the reference reaching hand is not chirally coherent and that the drawing resolves it as an anatomically valid left hand; the correction history repeatedly reopens wrist entry/digit fan from anatomy premises.
- blocking: yes
- responsible owner candidate: observation/reference authority over anatomy plausibility
- parent premise: inferred anatomical correctness outranks the visible projected relation.
- geometry correct: no
- material behavior correct: uncertain but not causal
- next disproof test: give a deliberately unusual but clearly visible foreshortened hand and require preserving apparent projection; verify no anatomy-normalization rewrite occurs unless explicitly requested.
- if non-blocking, accepted-limitation rationale: N/A

### Residual 3
- symptom: cross-worker anti-symbol and retirement behavior is not robust.
- visible evidence: Gemini finishes with radial/starburst hair, generic hand/body primitives, weak perspective propagation, and surviving scaffold lines; Astra is visually strong but its source history is reconstructed rather than canonical.
- blocking: yes
- responsible owner candidate: visual-quality gate execution plus provenance enforcement
- parent premise: recognition/detail can substitute for physical ownership, observed mass grouping, and retirement proof.
- geometry correct: no for Gemini; strong-but-unproven for Astra provenance
- material behavior correct: not isolated
- next disproof test: rerun S03.1 with a fresh worker that receives only current skill/reference, preserving an untouched canonical session and full action-0→latest GIF.
- if non-blocking, accepted-limitation rationale: N/A

## Renderer-candidate notes

No renderer defect is promoted from this class.

The three outputs use the same v11 family yet their quality differs primarily with authored structure and task interpretation. The supplied Gojo studies are also dominated by thin/medium lines, so they do not reproduce the earlier broad-pencil terminal/material stress case. Broad graphite remains a separate material question and is neither confirmed nor cleared here.

## Final class verdict

BLOCKED

Reason:

S03.1 fails at reference authority, anatomy-normalization, anti-symbol robustness, and canonical provenance before a renderer/material bottleneck is reached. Route the evidence to S04 instruction/geometry classification. Do not modify v11 pixels from this dogfood batch.
