# img2drawing vNext full roadmap

Updated: 2026-09-01
Workflow: Bottleneck · Production WIP Limit = 1

이 문서는 최신 HEAD와 현재 사용자 결정에 맞춘 전체 계획이다. 핵심 변경은 **새
fresh visual dogfood를 B09–B18 구현 사이에 끼워 넣지 않는 것**이다. 먼저 남은
product surface를 완성하고 freeze한 뒤 D01–D06 통합 dogfood campaign으로 검증한다.

## Phase A — foundation

| ID | State | Goal | Authority |
|---|---|---|---|
| B00 | CLOSED | R23 baseline / failure dossier | `capsules/B00.md` |
| B01 | CLOSED | vNext architecture cut | `capsules/B01.md` |
| B01-R1 | CLOSED | subject observation / boundary-method hardening | `STATUS.md` + preserved dogfood evidence |
| B02+B03 | CLOSED | inspection + measurement foundation | `capsules/B02-B03.md` |
| B04 | CLOSED | stage-free `DrawingSession` | `capsules/B04.md` |
| B05 | CLOSED | construction grammar + canonical Pn de-anchoring | `capsules/B05.md` |
| B06 | CLOSED | residual-driven correction + provenance | `capsules/B06.md` |
| B07 | CLOSED | bounded evidence / telemetry | `capsules/B07.md` |
| B07-R1 | CLOSED | value-region authoring + session compaction + form-before-value | `STATUS.md` |
| B08 | CLOSED | orthogonal `DrawingIntent` / mode / style scaffold | `capsules/B08.md` |

Foundation 결과:

```text
observe/read subject or intent
→ draw through one authoritative history
→ inspect bounded evidence
→ record highest-impact residual
→ edit responsible representation
→ fresh inspect
```

## Phase B — complete the product surface

| ID | State now | Goal | Depends |
|---|---|---|---|
| B09 | CLOSED | Finish / recognition authoring | B08 + B01-R1/B07-R1 |
| B10 | CLOSED | Intent-aware completion | B09 |
| B11 | CLOSED | Canonical `RenderProfile` + replay/GIF parity | B10 |
| B12 | ACTIVE | Legacy runtime / persistence isolation | B11 |
| B13 | SKELETON | Reference authority + subjectless runtime | B12 |
| B14 | SKELETON | Drawing-mode capability completion | B13 |
| B15 | SKELETON | Style authoring completion | B14 |
| B16 | SKELETON | Agent authoring / editing ergonomics | B15 |
| B17 | SKELETON | Package / public API / release-candidate truth | B16 |
| B18 | SKELETON | Dogfood-ready system freeze | B17 |

Dependency flow:

```text
B00…B08 CLOSED
      ↓
B09 → B10 → B11 → B12 → B13 → B14 → B15 → B16 → B17 → B18
      [NO NEW FRESH DOGFOOD BETWEEN THESE SLICES]
```

각 B09–B18은 synthetic/deterministic fixture, unit/integration regression, 이미
보존된 evidence로 기술적 contract를 닫는다. fresh unseen subject나 cross-agent
quality claim은 하지 않는다.

### B09 — Finish / recognition authoring

`pose | subject | form_light | expressive` finish intent가 실제 authoring policy로
연결되도록 한다. recognition은 P7이나 lifecycle gate가 아니라 관계 품질 target이다.
Face/hair/hands/feet/clothing/prop는 존재 여부가 아니라 spacing, overlap, contact,
termination, topology 등 subject-specific relation으로 다룬다. **Form before value**를
유지하며 detail/tone이 macro error를 덮지 못한다.

### B10 — Intent-aware completion

`done`을 stage/checklist가 아니라 declared intent에 대한 material residual 부재로
정의한다. `FinishRecord`는 current drawing state, intent digest, final inspection,
accepted limitations에 묶인 Agent decision provenance이며 artistic PASS certificate가
아니다. finish 이후 material mutation은 record를 stale하게 만든다.

### B11 — Canonical RenderProfile / replay / GIF

`StyleGuide`와 rendering을 분리하고 renderer/version/material/paper/supersample/
seed/compositing을 versioned `RenderProfile`로 묶는다. vNext action0→latest replay,
end-to-end GIF, canonical PNG parity를 한 history/profile에서 보장한다.

### B12 — Legacy isolation

canonical vNext import/use path가 stage registry, stage review, reopen, Pn persistence를
로드하지 않도록 explicit compatibility namespace/adapter로 격리한다. shared
stroke/history/renderer core는 복제하지 않는다. 물리적 R23 삭제는 아직 하지 않는다.

### B13 — Reference authority + subjectless runtime

B08에서 선언만 가능했던 imaginative/hybrid/free-draw를 실제 runtime capability로
완성한다.

```text
observed    → readable subject is evidence authority
imaginative → subjectless canvas + declared intent is authority
hybrid      → preserved reference constraints + explicit transformations are authority
```

subjectless `DrawingSession`과 reference 없는 inspection/correction semantics를
지원하되 fake overlay/reference authority를 만들지 않는다.

### B14 — Drawing-mode capability completion

하나의 core 위에 `croquis`, `figure_drawing`, `tonal_study`, `line_study`, `free_draw`
ModeGuide capability를 완성한다. ModeGuide는 observations/grammar/omissions/finish
emphasis/completion questions만 설명하며 stage count/cursor/advance/PASS를 갖지 않는다.

### B15 — Style authoring completion

작은 evidence-backed preset surface와 `base + explicit overrides + optional custom
prose structuring`을 완성한다. 최소 시작점은 `pencil_loose`, `graphite_academic`,
`graphite_tonal`. Style은 geometry truth를 바꾸거나 post-filter가 되어서는 안 된다.

### B16 — Agent authoring / editing ergonomics

이미 존재하는 draw/replace/segment/lift/delete/fill primitives를 worker가 장시간
수정 루프에서 안전하게 찾고 사용할 수 있도록 query/edit surface를 정리한다.
새 ownership lifecycle을 만들지 않고 `part`, `role`, provenance, supersession을
재사용한다.

### B17 — Package / public API / release-candidate truth

wheel/sdist, clean install, canonical examples, API/support matrix, docs link/package
content audit, versioning, migration command, CI를 canonical vNext truth에 맞춘다.
이 단계는 제품 품질 검증 완료를 주장하지 않는다.

### B18 — Dogfood-ready system freeze

기능 구현 종료선이다. canonical API/session schema/intent/RenderProfile/mode/style/
legacy adapter boundary를 freeze하고 known implementation TODO를 닫는다. 이후 새
기능을 추가하지 않고 dogfood defect는 responsible B-slice를 REOPEN한다.

## Phase C — full dogfood campaign

B18 이후에만 시작한다. 상세 계약은 [`VALIDATION_RELEASE.md`](VALIDATION_RELEASE.md).

```text
D01 difficult observed croquis
D02 observed figure / subject recognition
D03 tonal study
D04 observed free-draw
D05 imaginative + hybrid
D06 cross-agent reproducibility
```

공통 규칙:

- unseen/fresh input을 사용한다.
- answer image, authored coordinate table, prior session/trace, Pn packet을 주지 않는다.
- cost와 visual quality를 함께 본다.
- 문제가 나오면 새 feature slice를 만들기보다 responsible B-slice를 REOPEN한다.

예:

```text
D02 face/hair relation failure → B09 REOPEN
D05 subjectless persistence failure → B13 REOPEN
GIF parity failure → B11 REOPEN
edit surface failure → B16 REOPEN
```

## Phase D — harden / release

D01–D06이 통과한 뒤에만 진행한다.

```text
R01 consolidation       repeated dogfood fixes만 canonical docs/API에 흡수
R02 final regression    representative modes + checkpoint/resume + PNG/replay/GIF
R03 physical R23 retirement
R04 release
```

R03에서만 남은 stage runtime/review manifests/Pn references/stale exports/legacy
package data를 실제 삭제하거나 time-bounded adapter로 남기는 최종 결정을 실행한다.
frozen Git baseline과 historical evidence는 삭제하지 않는다.

## Global release exit

최종 release는 다음을 모두 직접 입증해야 한다.

- new-task worker가 Pn 없이 `observe/declare → draw → inspect → correct → finish`를 수행한다.
- observed/imaginative/hybrid가 같은 authoritative session/history core를 사용한다.
- croquis/figure/tonal/line/free-draw mode 차이가 metadata가 아니라 authoring behavior로 보인다.
- style 차이가 post-filter가 아니라 authored line/value/edge/detail decisions로 보인다.
- tone을 제거해도 major form/overlap이 읽힌다.
- canonical session cost가 brute-force microstroke로 폭증하지 않는다.
- PNG/replay/GIF가 canonical renderer provenance와 final-state parity를 공유한다.
- package/docs/examples/CI가 같은 canonical vNext route를 가리킨다.
- legacy R23은 explicit compatibility/history 경계 밖에서 normal route로 노출되지 않는다.

## Planning authority

- 실제 상태: `STATUS.md`
- architecture invariant: `CONTRACT.md`
- implementation cards: `slices/B09.md` … `slices/B18.md`
- post-freeze validation/release: `VALIDATION_RELEASE.md`
- 과거 HTML/temp 계획은 제품 입력/역사 자료이며 상태 권위가 아니다.
