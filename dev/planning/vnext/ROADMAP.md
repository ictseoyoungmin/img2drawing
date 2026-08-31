# img2drawing vNext B00–B18 roadmap

Updated: 2026-08-31
Workflow: Bottleneck, Production WIP Limit = 1

이 roadmap은 HTML 계획의 B00–B18을 실제 HEAD에 맞춘 현재 상태표다. 자세한
실행 계약은 `slices/`, 닫힌 결과는 `capsules/`를 사용한다.

## Status board

| ID | State now | Goal | Depends | Working document |
|---|---|---|---|---|
| B00 | CLOSED | R23 baseline / failure dossier | — | `capsules/B00.md` |
| B01 | CLOSED | vNext architecture cut | B00 | `capsules/B01.md` |
| B02+B03 | CLOSED | Inspection + measurement foundation | B01 | `capsules/B02-B03.md` |
| B04 | CLOSED | Stage-agnostic `DrawingSession` | B02+B03 | `capsules/B04.md` |
| B05 | CLOSED | Embedded R23 attention leak 제거 및 fresh-worker proof 완료 | B04 | `capsules/B05.md` |
| B06 | CLOSED | Residual-driven correction + resume-safe provenance | B05 reclosed | `capsules/B06.md` |
| B07 | CLOSED | Evidence / cost control (R1/R2 reclosed) | B06 | `capsules/B07.md` |
| B08 | CLOSED | `DrawingIntent` + mode/style scaffolding hardening | B07 | `capsules/B08.md` |
| B09 | SKELETON | Mode-aware finish / recognition | B08 | `slices/B09.md` |
| B10 | SKELETON | Intent-aware completion | B09 | `slices/B10.md` |
| B11 | SKELETON | Canonical `RenderProfile` + replay/GIF parity | B10 | `slices/B11.md` |
| B12 | SKELETON | Legacy runtime / persistence isolation | B11 | `slices/B12.md` |
| B13 | SKELETON | Same-subject E2E closure | B12 | `slices/B13.md` |
| B14 | SKELETON | Cross-agent reproducibility | B13 | `slices/B14.md` |
| B15 | SKELETON | Drawing-mode generalization | B14 | `slices/B15.md` |
| B16 | SKELETON | Style / free-draw hardening | B15 | `slices/B16.md` |
| B17 | SKELETON | Release truth | B16 | `slices/B17.md` |
| B18 | SKELETON | Physical R23 retirement | B17 | `slices/B18.md` |

## Dependency flow

```text
B00 → B01 → B02+B03 → B04 → B05 CLOSED
                                ↓
B06 CLOSED → B07 CLOSED → B08 CLOSED → B09 → B10 → B11 → B12 → B13 → B14 → B15 → B16 → B17 → B18
```

`B08`은 내부적으로 `DrawingIntent → ModeGuide → StyleGuide → override` 순서로
얕게 scaffold한 뒤 실제 dogfood가 필요한 계약만 고정한다. 그 내부 순서는 동시
production WIP를 허용하지 않는다.

## Product expansion line

```text
stable stage-free core
→ observed residual correction (B06 closed)
→ low-cost evidence loop
→ orthogonal drawing intent
→ visible mode-specific finish
→ intent-aware completion
→ canonical output/replay
→ legacy isolation
→ same-subject and cross-agent proof
→ tonal/free-draw/style generalization
→ release truth and retirement
```

## Global release exit

vNext release line은 다음을 모두 직접 입증해야 한다.

- new-task worker가 Pn 없이 observe/draw/inspect/correct/finish를 수행한다.
- 대표 croquis/figure/tonal/free-draw intent가 하나의 core를 재사용한다.
- mode/style 차이가 metadata가 아니라 visible authoring behavior로 보인다.
- PNG/replay/GIF가 canonical renderer provenance를 공유한다.
- package/docs/examples/CI가 같은 canonical route를 가리킨다.
- legacy R23은 명시적 compatibility path 밖에서 로드되거나 안내되지 않는다.

## Source reconciliation

- 제품/설계/slice 입력: `temp/img2drawing_vnext_universal_drawing_plan.html`
- 기존 상세 초안: `temp/img2drawing-vnext-plan-dev-v2/`
- 실제 상태: HEAD, tests, evidence, CLOSED capsules
- 상태 보정: HTML의 `B05 ACTIVE`는 실제 작업에서 두 번째로 좁게 재오픈해 embedded
  R23 attention leak을 제거한 뒤 `CLOSED`로 정정했다. 다음 후보는 B06이다.
