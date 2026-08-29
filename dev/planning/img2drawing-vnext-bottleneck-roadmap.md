# img2drawing vNext — Workflow Reset & Bottleneck Roadmap

- 상태: **ACTIVE — B00 legacy baseline freeze**
- 기준일: 2026-08-29
- 기준 저장소: `ictseoyoungmin/img2drawing`
- 기준 revision: `25ec454` (`feat: harden R23 evidence provenance`)
- 기준 release line: `0.5.2.dev23 / R23_material_integrated_visual_quality`
- 작업 방식: **Bottleneck / Production WIP Limit = 1**
- 핵심 원칙: **Macro correctness first. Construction → observation → correction → validation.**
- 이 문서의 목적: 기존 R23의 stage/review workflow를 연장하지 않고, 실제 drawing quality와 agent efficiency를 최상위 목표로 하는 vNext workflow를 재설계한다.

---

## 0. Executive decision

R23은 폐기하지 않는다. `25ec454`를 **legacy/reference baseline**으로 보존한다.

그러나 다음 항목은 vNext의 product/runtime architecture에서 더 이상 중심 개념으로 사용하지 않는다.

- mandatory `P1 → P2 → P3 → P4 → P5 → optional P6` stage advancement
- stage별 process-review + visual-review 이중 closure
- `RegionClosureManifest`
- `ResolvedFormManifest`
- exact-region completeness를 미술적 완료의 proxy로 사용하는 방식
- downstream 전체를 행정적으로 invalidation하는 stage-reopen bookkeeping
- visual quality를 증명하기 위해 다수의 JSON/packet/manifest를 작성하는 workflow

vNext의 중심 workflow는 다음 하나다.

중요: **runtime stage state machine은 제거하지만, 실제 크로키 제작에는 ordered construction grammar가 존재한다.**
즉 `관찰 → 동세 → 기본 덩어리 → 균형 → 관절/사지 → 윤곽 → 선택적 디테일 → 명암/강조`라는
전통적인 drawing order는 skill-side 제작 원리로 유지한다. 다만 이 순서를 `P1 CLOSED → P2 CLOSED`
같은 runtime gate로 잠그지 않는다. 뒤 단계에서 앞의 판단이 틀렸음을 발견하면 즉시 그 구조를 수정한다.

```text
READ THE POSE
  관찰 / 무게중심 / 실루엣 특징 / negative space
    ↓
LINE OF ACTION
  1–2개의 큰 흐름
    ↓
MASS BLOCKING
  head / ribcage / pelvis 방향·비틀림·원근
    ↓
BALANCE / PLUMB
  support / centre-of-mass / ground relation 확인
    ↓
JOINTS & LIMBS
  shoulder-elbow-wrist / hip-knee-ankle / cylinder-taper
    ↓
MINIMUM VIABLE WHOLE-FIGURE LIKENESS
    ↓
INSPECT SUBJECT ↔ DRAWING
    ↓
SELECT 1–3 HIGHEST-IMPACT MISMATCHES
    ↓
CORRECT EXPLICIT STROKES
    ↓
INSPECT AGAIN
    ↓
REPEAT NON-LINEARLY
    ↓
CONTOUR REFINEMENT
    ↓
SELECTIVE DETAIL
    ↓
OPTIONAL VALUE / ACCENT
    ↓
FINAL RESIDUAL SWEEP
```

핵심 질문은 더 이상

> “현재 stage의 모든 gate가 닫혔는가?”

가 아니다.

핵심 질문은

> **“현재 subject와 drawing 사이에서 가장 크게 품질을 제한하는 시각적 mismatch는 무엇이며, 그것을 어떻게 가장 적은 stroke 수정으로 줄일 것인가?”**

이다.

---

# 1. Why reset now

## 1.1 R23에서 실제로 잘 닫힌 것

R23의 다음 기술 자산은 유지 가치가 높다.

- explicit vector-like stroke authoring
- `StrokeIR`
- draw / replace / delete / soft-lift semantics
- history-preserving edit provenance
- pencil-contact renderer
- pressure / grade / opacity / taper
- checkpoint / resume
- deterministic replay
- end-to-end timelapse
- subject reference hash binding
- artifact hash integrity
- CI
- strict fresh-worker input/evaluator separation에 대한 contract

최신 R23 hardening은 manifest가 runtime truth를 위조하지 못하도록 lifecycle, P5 retirement, P6 counts, calibration artifacts, PNG hash binding을 강화했다.

이 부분은 **workflow reset 이유가 아니라 보존할 engineering foundation**이다.

## 1.2 현재 workflow가 실패한 방식

### Gemini-type failure

한 fresh-agent 실행은 P1→P5, P3/P4/P5 manifest/review를 모두 완료했다고 보고했지만 최종 그림은 실제 subject에 비해 다음이 약했다.

- torso의 back-three-quarter rotation
- head/neck turn
- near/far arm overlap
- body mass
- rifle/body contact와 topology
- leg stance와 weight
- feet/boot form
- overall likeness

즉 **process complete ≠ visually strong**였다.

### Claude-type failure

다른 fresh-agent 실행은 실제 overlay와 확대 inspection을 사용해 다음 오류를 제대로 잡았다.

- 발목을 boot cuff로 잘못 읽음
- facial centreline이 코를 통과하지 않음
- leg centre path drift
- rifle axis drift
- elbow inference 문제

하지만 P1 3-pass + P2 1-pass 후 P3 진입 전에 비용이 과도해 작업이 중단됐다.

실제로 가장 유용했던 도구는 agent가 별도로 만든 다음 기능이었다.

- 확대 ROI
- subject | drawing | overlay 3-panel board
- drawing stroke를 대비색으로 표시한 overlay
- grid
- row/column measurement
- pixel inspection

즉 **visual truth를 제대로 확인하면 현재 review workflow가 너무 비싸고**, 대충 확인하면 **약한 그림도 PASS**할 수 있다.

## 1.3 Root cause

현재 시스템은 점차 다음 형태가 됐다.

```text
drawing runtime
    ↓
stage orchestration
    ↓
stage contract
    ↓
worker packet
    ↓
local review
    ↓
region manifest
    ↓
visual manifest
    ↓
process review
    ↓
advance/reopen bookkeeping
```

검증 machinery가 drawing machinery보다 커졌다.

vNext는 이 관계를 뒤집는다.

```text
drawing + inspection + correction
        ↓
lightweight provenance
        ↓
verification
```

**검증은 production을 지원한다. production을 대체하지 않는다.**

---

# 2. vNext architecture boundary

## 2.1 KEEP — canonical capabilities and invariants

vNext가 보존하는 것은 기존 클래스나 모듈 이름 자체가 아니라 다음 **capability와 invariant**다.

```text
explicit stroke representation
authored draw / replace / delete / soft-lift semantics
history-preserving local edits
pencil-contact material rendering
pressure / grade / opacity / taper
atomic checkpoint / resume
deterministic replay
end-to-end timelapse
subject and current-state hash binding
```

다음 불변식도 유지한다.

- runtime이 Agent가 작성한 geometry를 몰래 rewrite하지 않는다.
- superseded/deleted/lifted stroke도 history와 replay에서 추적 가능하다.
- 같은 authoritative state는 동일 renderer family로 재현 가능하다.
- inspection/evidence는 exact current drawing state에 bind된다.

`StrokeIR`, `DrawingAction`, `Session`, `History` 등 기존 구현은 **재사용 후보**일 뿐 아직
vNext canonical core로 확정하지 않는다. 이 타입이나 모듈에 `stage`, stage registry, advancement,
review closure 의미론이 섞여 있다면 B01에서 dependency를 감사한 뒤 다음 중 하나를 선택한다.

1. stage-independent 부분만 그대로 재사용
2. 최소한으로 추출/분리
3. legacy adapter 뒤에 격리

기존 클래스 이름을 지키기 위해 vNext contract를 왜곡하지 않는다.

## 2.2 TRANSFORM — keep concept, redesign API

다음은 개념은 유지하지만 interface를 다시 만든다.

| R23 | vNext |
|---|---|
| `prepare_stage_review()` | `inspect()` |
| local review | unified inspection sheet + optional focused crops |
| observation lock | lightweight subject observation snapshot |
| pass memory | correction memory |
| P6 calibration | optional finish/material calibration |
| stage reference | skill-side drawing guidance, not runtime state |
| stage contract | guidance vocabulary, not advancement gate |

## 2.3 DEPRECATE from the main workflow

다음은 legacy compatibility 외에는 vNext runtime의 필수 경로에서 제거한다.

- `StageProgress` as workflow authority
- mandatory stage registry
- stage-owned representation state machine
- region closure completeness
- resolved-form closure manifests
- blind packet as required per-stage ceremony
- P6 as a mandatory runtime stage concept
- stage-wide downstream invalidation as the normal correction mechanism

## 2.4 Runtime responsibility

vNext runtime이 판단하지 않는 것:

- anatomy correctness
- pose correctness
- likeness
- which region matters most
- whether a garment fold is artistically right
- whether a drawing is finished

runtime이 책임지는 것:

- authored stroke execution
- edit history
- rendering
- inspection artifact generation
- read-only measurement
- state binding
- checkpoint/replay
- deterministic evidence packaging

Agent가 책임지는 것:

- observation
- prioritization
- correction choice
- visual acceptance

---

# 2.5 Ordered construction grammar — not runtime stages

vNext는 **stage-driven runtime을 제거하지만 drawing order 자체를 제거하지 않는다.**

이 구분은 핵심 contract다.

```text
ORDERED CONSTRUCTION GRAMMAR
= 그림을 잘 만들기 위한 자연스러운 제작 순서

RUNTIME STAGE MACHINE
= 특정 단계를 CLOSED해야 다음 단계 API를 쓸 수 있는 orchestration state
```

vNext는 첫 번째를 유지하고 두 번째를 제거한다.

## 2.5.1 Read the pose — 관찰 및 분석

선을 긋기 전에 subject 전체를 읽는다.

최소 관찰 항목:

- 무게중심과 support side
- 몸 전체의 dominant flow / line-of-action 후보
- head / ribcage / pelvis의 방향 관계
- shoulder와 pelvis의 tilt / opposition
- silhouette에서 subject를 구별하는 큰 특징
- 양팔/양다리 사이 negative space
- ground contact
- 큰 prop이 balance와 silhouette에 주는 영향
- occlusion과 near/far 관계

이 단계의 목적은 JSON을 채우는 것이 아니라 **첫 몇 개의 선이 무엇을 말해야 하는지 결정하는 것**이다.

## 2.5.2 Line of Action — 동세선

가장 먼저 긋는 1–2개의 큰 유기적 흐름이다.

- 척추의 literal contour를 복사하는 선이 아니다.
- 몸의 에너지, 휘어짐, 방향 전환을 압축한다.
- 너무 많은 gesture line을 만들어 pose를 설명하려 하지 않는다.
- 큰 prop의 axis가 balance를 강하게 바꾸면 보조 axis를 둘 수 있지만 body gesture를 대체하지 않는다.

**생동감은 이 단계에서 크게 결정되므로 mass보다 먼저 읽어야 한다.**

## 2.5.3 Mass blocking — 기본 도형화 / 매스 블로킹

다음 세 덩어리를 우선한다.

1. head
2. ribcage
3. pelvis

단순한 구/통/상자는 **generic primitive를 찍는 목적이 아니라 orientation을 설명하는 임시 construction vocabulary**다.

확인할 것:

- tilt
- rotation
- depth
- foreshortening
- head ↔ ribcage ↔ pelvis의 relative direction
- ribcage/pelvis 사이의 twist
- subject의 실제 occupied volume

필요하면 이후 shoulder/upper-limb/thigh mass를 추가한다.

## 2.5.4 Balance / Plumb line — 무게중심 확인

정수리, 목 뒤, torso 중심 등 Agent가 의미 있다고 판단한 anchor에서 ground로 plumb guide를 내려
support foot와 centre-of-mass의 관계를 본다.

이 guide는 anatomy inference가 아니라 **read-only visual aid**다.

검사 목적:

- 인물이 실제로 서 있는가?
- support leg가 weight를 받고 있는가?
- counterbalance leg/arm이 pose를 설명하는가?
- 그림이 subject보다 한쪽으로 밀렸는가?
- feet와 ground relation이 전체 mass를 지지하는가?

plumb line은 항상 영구 drawing stroke일 필요가 없다. inspection guide로만 존재해도 된다.

## 2.5.5 Joints & limbs — 관절과 사지 연결

주요 chain:

- shoulder → elbow → wrist
- hip → knee → ankle

초기에는 관절 위치/길이/각도를 잡고, 곧이어 limb가 **막대기가 아니라 taper와 방향을 가진 volume**으로 읽히게 한다.

- straight measured axis만 남기지 않는다.
- cylinder는 generic tube가 아니라 subject의 foreshortening과 taper를 설명해야 한다.
- hidden joint는 visible chain, silhouette, garment evidence를 사용해 최소한으로 infer한다.
- long boots / loose sleeves / garment edges를 관절 위치로 오독하지 않는다.
- foot direction과 grounding은 초기 construct에 포함한다.

## 2.5.6 Contour refinement — 윤곽선 정리

construction이 대체로 맞은 뒤 실제 외곽과 overlap ownership을 정리한다.

- silhouette
- muscle/clothing volume
- face opening ↔ hair mass
- garment ↔ body connection
- hand/foot/footwear form
- prop ↔ body contact
- near/far overlap

여기서 structure가 틀렸음을 발견하면 contour로 숨기지 않고 곧바로 construction을 수정한다.

## 2.5.7 Selective detail — 선택적 디테일

요청과 pose duration에 따라 선택적으로 추가한다.

- face
- hands
- feet
- grouped hair
- clothing identity
- prop identity
- sparse folds

디테일은 이미 틀린 silhouette/mass를 구조적으로 고치지 못한다.

## 2.5.8 Value / Accent — 선택적 명암과 강조

두 기본 finish profile을 둔다.

### `line_croquis`

- contour hierarchy
- selective accent
- pressure / taper variation
- no broad tonal rendering

### `long_pose_croquis`

- `line_croquis` 내용
- 관찰된 **큰 shadow mass** 1–몇 개
- 제한적 hatching
- form을 설명하는 value grouping

중요한 distinction:

- **금지:** 형태와 무관하게 몸통/다리에 반복하는 broad charcoal band
- **허용:** 실제 빛에서 관찰되는 큰 shadow mass를 단순화해 넣는 것

전체 외곽선을 다시 진하게 긋는 blanket confirmation은 어느 profile에서도 기본값이 아니다.

## 2.5.9 Non-linear correction rule

제작 grammar에는 순서가 있지만 correction에는 일방통행이 없다.

예:

```text
mass blocking 중 line of action 오류 발견
→ line of action 수정
→ mass 재조정

contour refinement 중 pelvis balance 오류 발견
→ pelvis / limb construction 수정
→ contour 재조정

detail 중 face opening과 hair mass 구조 오류 발견
→ head mass / contour 수정
→ detail 재적용
```

따라서 vNext의 핵심 문장은 다음이다.

> **Ordered construction grammar, non-linear correction workflow.**

---

# 3. Target workflow

vNext의 실제 worker loop는 **construction grammar와 correction loop를 결합**한다.

```text
┌──────────────────────────────────┐
│ 1. READ THE POSE                 │
│ weight / flow / silhouette       │
│ negative space / prop relation   │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ 2. LINE OF ACTION                │
│ 1–2 dominant organic flows       │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ 3. MASS BLOCKING                 │
│ head / ribcage / pelvis          │
│ tilt / rotation / depth          │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ 4. BALANCE / PLUMB               │
│ support / CoM / grounding        │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ 5. JOINTS & LIMBS                │
│ joint chains + tapered volumes   │
│ feet + major prop axis           │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ MINIMUM VIABLE WHOLE FIGURE      │
│ already reads as this pose       │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ INSPECTION SHEET                 │
│ subject | drawing | overlay      │
│ + 1–3 enlarged ROIs              │
│ + optional grid/plumb/measure    │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ SELECT TOP 1–3 MISMATCHES        │
│ highest perceptual impact first  │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ EXPLICIT CORRECTIONS             │
│ add / replace / delete / lift    │
└────────────────┬─────────────────┘
                 │
                 └──────────────────↺
                     non-linear:
              construction may reopen
                 at any time
                 ↓
┌──────────────────────────────────┐
│ 6. CONTOUR REFINEMENT            │
│ silhouette / overlap / clothing  │
│ hair / footwear / prop contact   │
└────────────────┬─────────────────┘
                 ↓
             inspect ↔ correct
                 ↓
┌──────────────────────────────────┐
│ 7. SELECTIVE DETAIL              │
│ face / hands / feet / identity   │
└────────────────┬─────────────────┘
                 ↓
             inspect ↔ correct
                 ↓
┌──────────────────────────────────┐
│ 8. OPTIONAL VALUE / ACCENT       │
│ line hierarchy or long-pose      │
│ shadow grouping                  │
└────────────────┬─────────────────┘
                 ↓
┌──────────────────────────────────┐
│ FINAL RESIDUAL SWEEP             │
└────────────────┬─────────────────┘
                 ↓
                DONE
```

### Runtime interpretation

이 도식의 `1–8`은 **drawing grammar 번호**다. runtime stage id가 아니다.

다음은 valid하다.

```text
3 → inspect → 2를 수정 → 3 재조정 → 5
6 → inspect → 4의 balance 문제 수정 → 5/6 재조정
7 → inspect → 3의 head mass 수정 → 6/7 재적용
```

runtime은 이 이동을 `reopen_stage()`로 관리하지 않는다. explicit stroke history와 correction memory만 보존한다.

---

# 4. Bottleneck status board

```text
SYSTEM
  architecture sketched / contract not frozen

BASELINE
  B00  Legacy R23 freeze + failure dossier                    ACTIVE

FOUNDATION
  B01  vNext contract and architecture cut                    SKELETON
  B02+B03  Inspection Foundation                              SKELETON
           InspectionSheet + basic read-only measurement

CORE WORKFLOW
  B04  Stage-agnostic DrawingSession                          SKELETON
  B05  Observation + construction grammar                         SKELETON
  B06  Correction loop + correction memory                    SKELETON
  B07  Evidence compaction / cost control                      SKELETON

DRAWING QUALITY
  B08  Local edit ergonomics + stroke planning helpers        SKELETON
  B09  Contour / detail / value-accent finish                     SKELETON
  B10  Final residual sweep + completion contract             SKELETON

RELIABILITY
  B11  Resume / replay / timelapse parity                      SKELETON
  B12  Legacy migration / deprecation boundary                SKELETON

DOGFOOD
  B13  Single-subject E2E quality closure                      SKELETON
  B14  Cross-agent same-subject reproducibility                SKELETON
  B15  Diverse-subject generalization                          SKELETON
  B16  Failure-regime hardening                                SKELETON

RELEASE
  B17  Package / CI / docs / release truth                    SKELETON
  B18  Legacy workflow retirement                             SKELETON

CLOSED
  none

NEXT GATE
  pin 25ec454 and close the reproducible R23 failure dossier
```

**Production WIP Limit = 1.**

한 번에 하나만 ACTIVE로 둔다.

다음 slice로 이동하는 이유는 “계획상 다음 번호”가 아니라 **현재 결과의 가장 큰 병목이 닫혔기 때문**이어야 한다.

## 4.1 Lightweight operating control plane

이 2,000줄 이상의 roadmap은 전체 설계와 후보 slice의 **reference map**이다.
일상적인 WIP 상태와 작업 인계를 이 문서에 계속 누적하지 않는다.

운영 상태는 다음의 작은 파일만 authoritative하게 사용한다.

```text
dev/planning/vnext/
  STATUS.md              # 한 화면: SYSTEM / ACTIVE / SKELETON / CLOSED / NEXT GATE
  active/
    B00.md               # ACTIVE bottleneck card는 정확히 하나
  capsules/
    Bxx.md               # CLOSED slice의 압축된 contract/evidence/reopen 조건
  failure-dossier/
    ...
```

B00이 이 control plane을 생성하기 전까지는 위 status board가 bootstrap authority다.

규칙:

- `active/`에는 production card가 최대 하나만 존재한다.
- slice가 닫히면 구현 서사를 capsule로 압축하고 active card를 retire한다.
- roadmap에는 세부 진행 로그를 추가하지 않는다.
- roadmap의 번호는 후보 식별자이지 자동 실행 순서가 아니다.
- Bottleneck 상태는 개발 workflow에만 존재하며 product/runtime state가 아니다.

---

# 5. Slice details

---

## B00 — Legacy R23 freeze + failure dossier

### Goal

vNext 작업이 시작되기 전에 현재 R23을 재현 가능한 baseline으로 고정하고, workflow reset의 근거를 한 곳에 모은다.

### Scope

- `25ec454`를 legacy baseline으로 명시
- 가능하면 tag 또는 dedicated baseline branch 생성
- Gemini dogfood failure 정리
- Claude dogfood cost/failure 정리
- 현재 canonical R23 positive/negative fixtures의 역할 분리
- vNext 작업 중 R23 evidence를 자동 승계하지 않도록 선언

### WIP boundary

B00은 현재 유일한 `ACTIVE` slice다. 새 runtime/inspection 구현은 B00이 닫힐 때까지 시작하지 않는다.
이 slice는 baseline과 reset 근거를 보존하는 짧은 작업이며, 새로운 review schema나 대규모 evidence
machinery를 만드는 프로젝트로 확장하지 않는다.

### Deliverables

```text
dev/planning/vnext/
  STATUS.md
  active/
    B00.md
  BASELINE.md
  failure-dossier/
    gemini.md
    claude.md
    r23-architecture.md
```

### Definition of Closed

- [ ] `25ec454` baseline SHA가 문서와 자동 check에 고정됨
- [ ] R23의 KEEP / TRANSFORM / DEPRECATE 항목이 명확함
- [ ] Gemini failure와 Claude failure가 서로 다른 failure mode로 기록됨
- [ ] 기존 R23 artifact를 vNext PASS evidence로 자동 재사용하지 않음
- [ ] vNext의 목표가 “더 많은 gate”가 아니라 “더 좋은 drawing with less review overhead”로 명시됨
- [ ] B00 closure 후 재사용 가능한 context capsule이 작성됨

### REOPEN

- baseline으로 삼은 SHA가 변경됨
- legacy artifact가 vNext validation에 몰래 재사용됨
- reset 이유와 실제 dogfood evidence가 불일치함

---

## B01 — vNext contract and architecture cut

### Goal

workflow 의미론과 drawing runtime을 분리한다.

### Core decision

새 public surface는 stage를 알 필요가 없어야 한다.

예시:

```python
run = DrawingSession.create(
    subject="subject.png",
    output_dir="run/",
)

run.observe(...)
run.draw(...)
sheet = run.inspect(...)
run.correct(...)
run.finish(...)
```

이 코드는 lifecycle을 설명하는 sketch이지 아직 동결된 최종 API가 아니다. B01에서는 state ownership,
dependency direction, persistence boundary처럼 이후 CLOSED slice를 무효화할 결정만 freeze한다.
`finish()`의 세부 surface처럼 B09 전까지 검증할 수 없는 항목은 speculative contract로 고정하지 않는다.

### Scope

- vNext namespace / package boundary 결정
- 기존 `StrokeIR`, `DrawingAction`, `Session`, history/canvas 계층의 stage dependency audit
- KEEP capability/invariant와 실제 재사용 가능한 구현의 mapping 작성
- StageProgress를 vNext authority에서 제거
- inspection/correction lifecycle 정의
- legacy adapter boundary 정의
- vNext checkpoint schema skeleton 정의

### Non-goals

- drawing quality 자체를 이 slice에서 해결하지 않음
- R23 클래스를 즉시 삭제하지 않음
- compatibility를 위해 vNext design을 stage-oriented로 왜곡하지 않음

### Definition of Closed

- [ ] vNext runtime의 canonical lifecycle이 1페이지 안에 설명 가능
- [ ] `draw()`가 P1/P2/P3를 알 필요 없음
- [ ] `inspect()`가 stage manifest를 생성하지 않음
- [ ] correction은 earlier-stage reopen 없이 history-preserving edit로 가능
- [ ] visual semantics는 Agent authority로 남음
- [ ] legacy compatibility는 adapter에 격리됨
- [ ] 기존 클래스 이름이 아니라 capability/invariant 기준으로 재사용 여부가 결정됨
- [ ] vNext normal path와 frozen R23 path가 동등한 두 production implementation으로 남지 않음

### REOPEN

- vNext core에 다시 `P1`, `P2`, `P3` branching이 들어옴
- correction을 위해 stage bookkeeping이 필요해짐
- runtime이 visual correctness를 판단하기 시작함

---

## B02+B03 — Inspection Foundation

### Goal

현재 가장 높은-impact 병목인 **“Agent가 subject와 drawing의 차이를 빠르고 정확하게 보는 능력”**을 먼저 해결한다.

기존 B02 `InspectionSheet`와 B03 read-only measurement를 하나의 tightly-coupled production
slice로 취급한다. 좌표 mapping, ROI 확대, grid/plumb/basic measurement 없이 sheet만 먼저
닫지 않는다. `B02+B03`은 하나의 ACTIVE slot만 소비하며 별도의 두 구현으로 진행하지 않는다.

### Output

한 번의 호출로 기본적으로 단 하나의 visual sheet를 만든다.

```text
┌───────────────────┬───────────────────┬───────────────────┐
│ SUBJECT           │ DRAWING           │ CONTRAST OVERLAY  │
├───────────────────┴───────────────────┴───────────────────┤
│ ROI 1 enlarged    │ ROI 2 enlarged    │ ROI 3 enlarged    │
└───────────────────────────────────────────────────────────┘
```

### Requirements

- subject / drawing 같은 registration
- subject ↔ canvas coordinate mapping이 명시적
- drawing은 overlay에서 red/cyan 등 강한 대비 표현
- subject 감광 옵션
- ROI를 충분히 확대
- ROI 좌표/scale 표시
- one-call grid / point / distance / angle
- Agent-selected plumb / ground guide
- 필요 시 row/column profile과 pixel sample
- raw drawing과 altered overlay를 명확히 구분
- no semantic judgement
- state hash binding

### Suggested API

```python
sheet = InspectionSheet.create(
    subject="subject.png",
    drawing="current_drawing.png",
    registration=registration,
    rois=[
        ROI("head", box=...),
        ROI("pelvis_legs", box=...),
        ROI("rifle_body", box=...),
    ],
    overlay="contrast",
    grid=False,
    guides=[
        PlumbLine(anchor=(...)),
        GroundGuide(y=...),
    ],
)
```

이 slice는 B04 `DrawingSession`보다 먼저 닫히므로 standalone public contract로 검증한다.
B04가 닫힐 때 `run.inspect(...)`는 이 동일 implementation을 호출하는 얇은 facade가 될 수 있지만,
두 번째 inspection path를 만들지 않는다.

`PlumbLine`과 `GroundGuide`는 Agent가 anchor/ground를 지정하는 read-only inspection guide다.
runtime이 centre-of-mass나 balance를 자동 판정하지 않는다.

### Principles

측정 도구는 **evidence**만 제공한다.

결정을 하지 않는다.

### Minimum tools

```python
measure.grid(...)
measure.point(...)
measure.distance(...)
measure.angle(...)
measure.horizontal_profile(...)
measure.vertical_profile(...)
measure.sample_pixel(...)
measure.map_subject_to_canvas(...)
measure.plumb_line(...)
measure.ground_guide(...)
```

### Deferred assistive extensions

- local edge visualization
- silhouette interval candidates
- orientation field
- gradient/LoG previews

단, 모두 `assistive_only`.

이 deferred 목록은 Inspection Foundation closure를 이유 없이 늘리지 않는다. known dogfood mismatch를
판별하는 데 실제로 필요하다는 증거가 생긴 기능만 같은 ACTIVE slice 안에서 추가한다. 그렇지 않으면
future candidate로 남긴다.

### Definition of Closed

- [ ] 코 5px 수준의 alignment mismatch를 확대 view에서 판별 가능
- [ ] 검은 재킷/부츠 위에서도 drawing stroke 위치가 overlay에서 보임
- [ ] whole view와 local ROI를 별도 이미지 여러 개 열지 않고 한 장에서 읽을 수 있음
- [ ] inspection sheet는 current drawing state에 hash-bind됨
- [ ] subject ↔ canvas coordinate mapping이 명시적
- [ ] grid overlay를 one-call로 생성 가능
- [ ] 두 점 거리/각도 확인 가능
- [ ] row/column profile을 이미지/JSON으로 볼 수 있음
- [ ] pixel sample provenance가 남음
- [ ] sheet/measurement 생성 자체가 PASS/FAIL을 만들지 않음
- [ ] measurement 결과가 stroke를 자동 이동시키지 않음
- [ ] Gemini/Claude dogfood fixture에서 useful한 known mismatch를 실제로 판별 가능
- [ ] Claude dogfood에서 만든 임시 inspection/measurement script 대부분을 대체함
- [ ] B04가 사용할 수 있는 standalone contract와 context capsule이 존재

### REOPEN

- Agent가 다시 별도 Pillow script로 확대 보드를 만들어야 함
- 검은 영역 위 stroke가 안 보임
- ROI가 너무 작아 판정 불가
- sheet가 너무 복잡해 whole view를 읽기 어려움
- helper가 anatomy를 자동 판정함
- measurement가 geometry truth로 승격됨
- worker가 여전히 같은 측정 script를 외부에서 재작성함

---

## B04 — Stage-agnostic DrawingSession

### Goal

StrokeIR/history/renderer를 보존하면서 새 workflow용 최소 orchestration API를 만든다.

### Required operations

```text
create
resume
observe
draw
draw_many
replace_stroke
replace_segment
soft_lift
delete_stroke
inspect
checkpoint
finish
```

### State

최소 상태만 가진다.

```text
subject
observation snapshot
current StrokeIR
history cursor
inspection history
correction memory
finish metadata
```

### Explicitly absent

```text
current_stage
stage_index
region closure
resolved form closure
P6 preflight
stage advance
stage reopen
```

### Definition of Closed

- [ ] 간단한 10-stroke drawing을 stage 정보 없이 생성/수정/재개 가능
- [ ] R23 renderer 결과와 material parity 유지
- [ ] every mutation atomic checkpoint
- [ ] inspect artifact는 exact current state와 bind
- [ ] no stage-specific import required in vNext normal path
- [ ] unit tests가 workflow state machine이 아닌 drawing state invariants에 집중

### REOPEN

- stage semantics가 core API에 재진입
- correction 때문에 branch rewind가 필수
- resume가 inspection/correction continuity를 잃음

---

## B05 — Observation + construction grammar

### Goal

runtime stage를 다시 만들지 않으면서, **크로키를 실제로 잘 시작하는 ordered construction grammar**를
fresh worker가 자연스럽게 수행하게 한다.

이 slice의 핵심은 “20–40개 선을 아무 순서로나 채운다”가 아니다.

다음 다섯 construction phases가 하나의 **연속된 initial construct** 안에서 작동해야 한다.

```text
5.1 Read the pose
5.2 Line of action
5.3 Head / ribcage / pelvis mass blocking
5.4 Balance / plumb check
5.5 Joints / limbs / feet / major prop
```

이 번호는 runtime stage가 아니다.

### B05.1 Read the pose — 관찰 및 분석

그리기 전 whole-view에서 최소 다음을 읽는다.

- support side / counterbalance
- dominant body flow
- shoulder / pelvis tilt
- head ↔ torso turn
- silhouette 특징
- negative spaces
- ground relation
- major prop axis / overlap
- occluded limb evidence

출력은 거대한 `ObservationContract`가 아니라 짧은 working note여도 된다.

예:

```json
{
  "weight": "image-left support leg",
  "flow": "head-left → torso-right → pelvis-left reversal",
  "silhouette_keys": ["bob hair opening", "outward right boot", "diagonal rifle"],
  "negative_spaces": ["right arm↔torso", "between legs"],
  "uncertain": ["far elbow under jacket"]
}
```

### B05.2 Line of Action — 동세선

첫 drawing marks는 1–2개의 큰 flow를 명확히 한다.

- body energy
- spine/torso rhythm
- major reversal
- optional major-prop axis

Success:

- 나머지 anatomy를 지워도 pose energy가 subject와 같은 방향으로 읽힘
- generic straight spine / centre pole이 아님
- prop axis가 body gesture를 대체하지 않음

### B05.3 Mass blocking — 기본 도형화 / 매스 블로킹

head / ribcage / pelvis를 우선 배치한다.

각 mass는 단순 primitive 이름보다 다음 관계가 중요하다.

- centre
- width / height
- tilt
- rotation
- depth
- overlap
- relative scale
- ribcage ↔ pelvis twist

필요하면 shoulder girdle, upper limb, thigh mass를 최소한으로 추가한다.

**머리는 generic 원, torso는 generic 상자, pelvis는 symmetric box를 떨어뜨리는 것으로 닫지 않는다.**
primitive는 subject orientation을 설명할 때만 유효하다.

### B05.4 Balance / Plumb — 무게중심 확인

initial construct가 커지기 전에 plumb check를 수행한다.

InspectionSheet에 Agent-selected guide를 얹어 다음을 본다.

- head/neck/torso anchor와 support foot 관계
- centre mass가 base of support 위에 있는지
- subject보다 whole figure가 좌/우로 drift하지 않았는지
- counterbalance leg/arm이 pose를 설명하는지
- 두 발의 ground height와 contact

이 단계는 permanent stroke를 강제하지 않는다.
필요하면 inspection-only guide로 끝낸다.

### B05.5 Joints & limbs — 관절과 사지 연결

다음 chain을 subject에서 읽어 배치한다.

```text
shoulder → elbow → wrist
hip → knee → ankle
```

그 뒤 막대기에서 멈추지 않고, 필요한 최소한의 taper/volume을 사용해 limb direction과
foreshortening을 읽히게 한다.

필수:

- both arms
- both legs
- occluded limb minimum hypothesis
- foot direction
- grounding
- hand/foot endpoint
- large prop의 global axis/extent

주의:

- boot cuff ≠ ankle
- sleeve edge ≠ arm axis
- waistband ≠ hip joint
- hair silhouette ≠ cranium
- clothing outer edge ≠ underlying limb centre

### Minimum viable whole-figure likeness

B05가 끝날 때 그림은 아직 clean contour나 detail drawing이 아니다.

하지만 다음은 이미 보여야 한다.

- 이 사람의 head/body orientation
- 이 pose의 weight distribution
- 두 팔/두 다리의 관계
- head/ribcage/pelvis의 twist
- feet direction / ground
- major prop과 body relation
- characteristic negative space

즉 **“generic mannequin with the right objects”가 아니라 “이 subject의 구조적 likeness”**여야 한다.

### First inspection

B05 종료 직후 B06로 넘어가기 전에 InspectionSheet를 반드시 본다.

권장 first sheet:

```text
whole subject
whole drawing
contrast overlay
head/torso ROI
pelvis/legs ROI
prop/contact ROI (있을 때)
plumb guide
```

이 first inspection에서 macro mismatch가 보이면 B05 construction을 바로 수정한다.
“이건 이미 line-of-action phase가 끝났다”는 이유로 보존하지 않는다.

### Definition of Closed

- [ ] drawing 전 whole-pose observation이 짧게라도 존재
- [ ] 1–2개의 dominant line of action이 pose energy를 설명
- [ ] head / ribcage / pelvis가 subject-specific orientation과 scale을 가짐
- [ ] plumb/balance check가 support/ground relation을 검사
- [ ] both arms / both legs / feet / major prop이 initial construct에 존재
- [ ] occluded limb가 이유 없이 누락되지 않음
- [ ] limb가 pure stick/rail 상태에서 멈추지 않음
- [ ] subject의 characteristic negative spaces가 대체로 읽힘
- [ ] first InspectionSheet에서 전체 구조를 직접 비교할 수 있음
- [ ] stage closure/manifest 없이 이 모든 작업을 수행 가능

### REOPEN

- initial construct가 generic stick dummy에 머묾
- line of action 없이 landmark 배치부터 시작함
- generic primitive가 subject mass를 대체함
- plumb/balance를 확인하지 않아 figure가 기울거나 drift함
- feet/prop/occluded limb를 “나중 단계”로 미룸
- 너무 상세하게 시작해 macro correction cost가 커짐
- ordered grammar를 runtime stage machine으로 다시 구현함

---

## B06 — Correction loop + correction memory

### Goal

vNext의 실제 중심 workflow를 구현한다.

B06은 unit/schema evidence만으로 닫지 않는다. B05 initial construct와 B06 correction loop를 연결한
즉시, 같은 sniper subject로 **early structural dogfood**를 수행한다. 이 dogfood는 B13의 완성형
E2E release evidence를 대체하지 않지만, B07 이후로 진행할 수 있는지 판단하는 필수 closure gate다.

### Loop

```text
inspect
  ↓
write observations
  ↓
select top 1–3 defects
  ↓
apply corrections
  ↓
inspect fresh
  ↓
verify previous defects + scan new residuals
```

### Correction priority

기본 우선순위:

1. whole pose / line of action / registration
2. balance / plumb / grounding
3. mass / silhouette / negative space
4. overlap / contact / depth
5. part shape
6. identity/detail
7. line quality

이 순서는 dogma가 아니라 default prioritization guidance다.

### Correction memory

각 loop는 다음만 기억한다.

```json
{
  "previous_findings": [...],
  "selected_bottlenecks": [...],
  "actions_since_review": [...],
  "resolved": [...],
  "still_open": [...],
  "new_findings": [...]
}
```

### Definition of Closed

- [ ] correction action이 해결의 증거로 취급되지 않음
- [ ] 이전 concern을 fresh sheet에서 재검사함
- [ ] fresh residual sweep이 존재
- [ ] same mismatch가 3회 반복되면 observation strategy를 바꿈
- [ ] stage reopen 없이 upstream-like correction 가능
- [ ] history에는 superseded branches가 모두 남음
- [ ] review JSON은 사람이 읽어도 짧음
- [ ] same sniper subject에서 B05 initial construct → inspect → correct loop가 실제로 실행됨
- [ ] early dogfood drawing이 generic stick/rail figure가 아니라 subject의 macro pose를 읽히게 함
- [ ] torso/head turn, balance, leg stance, feet, prop/body relation의 high-impact mismatch를 sheet에서 다룸
- [ ] worker가 custom inspection/measurement script를 재발명하지 않음
- [ ] P1/P2/P3 manifest ceremony 없이 structural correction을 완료함
- [ ] visual artifact와 review overhead를 R23/Claude baseline과 비교 기록함
- [ ] early dogfood evidence가 약하면 B07로 가지 않고 B02+B03/B04/B05/B06 중 earliest premise를 REOPEN함

### REOPEN

- manifest 작성량이 다시 증가
- correction loop가 stage transition으로 변질
- same issue redraw만 반복
- correction history 때문에 agent가 current image보다 narrative에 끌림

---

## B07 — Evidence compaction / cost control

### Goal

Claude dogfood에서 드러난 **visual inspection cost explosion**을 줄인다.

### Principles

- default visual read = one sheet
- ROI는 1–3개
- full raw images는 필요할 때만
- historical review artifact를 매번 재열지 않음
- current state 중심

### Features

- tiled single-sheet evidence
- thumbnail + zoom hierarchy
- optional raw source links
- inspect mode presets:
  - `quick`
  - `focused`
  - `deep`
- pass artifact deduplication
- stale evidence auto-marking

### Metrics to record

hard release gate가 아니라 comparative benchmark로 기록:

- visual artifacts opened per correction loop
- number of loops to useful likeness
- wall-clock/runtime
- agent token/image usage where observable
- number of custom helper scripts needed
- correction survival rate

### Definition of Closed

- [ ] default correction loop는 1 review sheet로 시작 가능
- [ ] normal loop에서 8–10 local images를 생성하지 않음
- [ ] deep inspection은 uncertainty가 있을 때만 opt-in
- [ ] current state 찾기 위해 수십 개 artifact를 탐색할 필요 없음
- [ ] Claude baseline보다 명백히 낮은 review overhead

### REOPEN

- quality가 떨어졌는데 cost만 줄어듦
- quick mode가 오류를 숨김
- agent가 다시 수동 crop pipeline을 만듦

---

## B08 — Local edit ergonomics + stroke planning helpers

### Goal

Agent가 “어떻게 선을 만들지”보다 “무엇을 관찰하고 고칠지”에 집중하게 한다.

### Important constraint

helper는 geometry를 자동 결정하지 않는다.

### Candidate primitives

```python
stroke.polycurve(points, ...)
stroke.tapered_curve(points, ...)
stroke.closed_contour(points, ...)
stroke.hair_group(points, ...)
stroke.fold_curve(points, ...)
stroke.parallel_structure(centerline, widths, ...)
stroke.boot_block(points, ...)
```

그러나 helper는 **subject 좌표를 받는 renderer-side authoring utility**일 뿐이다.

### Also include

- ergonomic defaults for eraser tools
- default preset injection
- clear action validation errors
- explicit provenance note correction / annotation API

### Provenance correction

geometry를 바꾸지 않고 observation text를 supersede할 수 있어야 한다.

예:

```python
run.annotate(
    target_action="A142",
    correction="forearm is moderately foreshortened, not barely foreshortened"
)
```

### Definition of Closed

- [ ] common curved stroke를 hand-written dense point list 없이 만들 수 있음
- [ ] authored control points와 generated render points의 provenance 차이가 명확함
- [ ] runtime이 몰래 geometry를 rewrite하지 않음
- [ ] eraser/edit API의 preset boilerplate 감소
- [ ] provenance-only correction 가능
- [ ] primitives가 “generic mannequin geometry”를 만들지 않음

### REOPEN

- helper가 subject observation을 대체
- generated curve가 provenance를 속임
- primitive 사용이 결과를 generic하게 만듦

---

## B09 — Contour / detail / value-accent finish

### Goal

construction과 correction loop가 macro structure를 충분히 잡은 뒤,
drawing grammar의 후반부인 **6. contour refinement → 7. selective detail → 8. optional value/accent**
를 수행한다.

이 역시 runtime stage가 아니라 finish capability다.

### Entry condition

Agent가 current whole-view에서 다음을 만족한다고 판단해야 한다.

- pose / line of action holds
- head-ribcage-pelvis mass relation holds
- balance / grounding holds
- silhouette / negative space가 크게 틀리지 않음
- overlap/contact holds
- major prop structure holds
- no high-impact structural mismatch remains

하나라도 크게 틀렸으면 finish하지 않고 B06 correction loop로 돌아간다.

### B09.1 Contour refinement — 윤곽선 정리

construction 위에 실제 subject의 contour ownership을 정한다.

책임:

- decisive silhouette
- muscle / soft form transitions where relevant
- clothing volume and openings
- hair outer mass + face opening
- joint convex/concave turns
- hands / feet / footwear
- prop structure and body contact
- near/far occlusion handoff

`clean`은 darker가 아니라 **decided**를 의미한다.

Contour를 그리다가 underlying mass/balance가 틀렸다는 사실을 발견하면
contour로 숨기지 않고 construction stroke를 수정한다.

### B09.2 Selective detail — 선택적 디테일

요청의 drawing mode와 available time/detail budget에 맞춰 선택적으로 추가한다.

Candidate details:

- eye/nose/mouth/chin relation
- grouped hair locks
- hand/finger grouping
- footwear construction
- garment identity
- anchor/tension/compression folds
- prop identity-defining subparts

짧은 croquis에서는 거의 생략 가능하다.

긴 croquis나 identity-sensitive task에서는 더 적극적으로 사용한다.

디테일 수가 많다고 finish가 좋아지는 것은 아니다.

### B09.3 Line calibration

실제 canvas-size calibration sheet를 사용한다.

```text
straight
C curve
S curve
taper-in
taper-out
construction / form / accent
```

actual-size + 50%.

Agent는 실제 렌더를 보고 현재 canvas에서:

- readable construction
- normal form line
- selective accent

의 pressure / grade / width / opacity hierarchy를 선택한다.

외부 drawing engine의 숫자를 그대로 복사하지 않는다.

### B09.4 Finish profiles

#### `line_croquis`

기본값.

- contour selection
- sparse interior form line
- selective detail
- line weight hierarchy
- taper / pressure accents
- no broad tonal fill

#### `long_pose_croquis`

긴 포즈에서 opt-in.

- `line_croquis` 전체
- 관찰된 large shadow mass
- limited hatching
- major plane/value grouping

large shadow mass는 form/lighting observation에 근거해야 한다.

다음과 구분한다.

```text
VALID:
observed cast/form shadow를 큰 단순 shape로 묶음

INVALID:
몸통과 다리에 굵은 charcoal band를 반복해 volume처럼 보이게 함
```

### B09.5 Selective restatement

accent는 high-information 영역에만 사용한다.

예:

- weight-bearing contact
- head/face focal turn
- overlap handoff
- important garment anchor
- prop contact
- foreground contour segment

전체 silhouette를 다시 진하게 따라가는 blanket confirmation은 금지한다.

### Construction retirement

더 이상 필요한 설명을 하지 않는 exploratory line은:

- `soft_lift`
- `delete_stroke`

로 정리할 수 있다.

단, history는 보존한다.

### Definition of Closed

- [ ] contour가 generic outline이 아니라 subject mass/overlap을 설명
- [ ] contour refinement 중 structural defect 발견 시 ordinary correction loop로 복귀
- [ ] detail은 identity/high-information purpose를 가짐
- [ ] short croquis에서 detail omission이 valid
- [ ] calibration PNG가 actual renderer path 사용
- [ ] line hierarchy가 construction / form / accent로 읽힘
- [ ] accent가 whole-outline blanket darkening으로 변하지 않음
- [ ] `long_pose_croquis`에서 관찰된 large shadow mass를 표현 가능
- [ ] broad arbitrary charcoal band는 재등장하지 않음
- [ ] construction retirement history 보존
- [ ] P5/P6 runtime state 없이 수행 가능

### REOPEN

- finish가 second geometry pipeline이 됨
- contour가 잘못된 construction을 덮음
- hair/face defect를 detail로 숨김
- detail count가 품질 proxy가 됨
- broad charcoal/value band 재등장
- 모든 contour가 동일한 dark weight로 변함
- line quality가 CAD/brush 느낌으로 회귀
- 장시간 포즈에서도 value grouping을 표현할 방법이 없음

---

## B10 — Final residual sweep + completion contract

### Goal

완료 판정을 단순화하되 약한 결과를 쉽게 닫지 못하게 한다.

### Completion question

```text
Does any remaining mismatch materially limit:
- pose identity
- mass/silhouette
- depth/overlap/contact
- major part recognition
- requested identity/detail
- line readability/material?
```

### Final review

최소:

- raw subject
- raw drawing
- final InspectionSheet
- high-risk ROI only when relevant

### Completion record

```json
{
  "status": "done",
  "remaining_material_mismatches": [],
  "accepted_minor_residuals": [...],
  "final_observation": "...",
  "final_artifacts": [...]
}
```

### Definition of Closed

- [ ] region count가 아니라 material mismatch 기준
- [ ] accepted residual은 low-impact 이유가 명확함
- [ ] known high-impact mismatch가 남아 있으면 DONE 불가
- [ ] completion record가 짧고 artifact-bound
- [ ] visual decision은 Agent/evaluator 소유

### REOPEN

- checklist complete라서 weak image가 닫힘
- accepted residual이 structural defect를 숨김
- final review가 old rationale에 의존

---

## B11 — Resume / replay / timelapse parity

### Goal

workflow reset으로 기존 img2drawing의 가장 강한 engineering feature를 잃지 않는다.

### Requirements

- full session preservation
- resume from latest authoritative state
- correction memory restoration
- inspection history lookup
- deterministic replay
- final rendering parity
- end-to-end GIF from action 0 to latest action
- same pencil renderer family
- default timelapse sampling suitable for long runs

### Definition of Closed

- [ ] fresh process에서 resume 후 correction loop 즉시 이어짐
- [ ] re-render hash parity 또는 documented deterministic tolerance
- [ ] deleted/replaced/soft-lift strokes가 replay에 정확히 반영
- [ ] GIF가 action 0부터 latest까지 끊기지 않음
- [ ] PNG와 GIF의 pencil material family가 동일
- [ ] legacy session 변환 path 또는 명시적 unsupported policy 존재

### REOPEN

- resume 후 review context 분실
- GIF가 중간부터 시작
- timelapse가 ballpoint/uniform line처럼 보임
- history mutation으로 이전 action 소실

---

## B12 — Legacy migration / deprecation boundary

### Goal

R23을 끌고 가면서 vNext를 오염시키지 않는다.

### Strategy

권장 구조:

```text
img2drawing/
  vnext/
    session.py
    inspection.py
    measurement.py
    correction.py
    finish.py

  legacy/
    r23_adapter.py
```

최종 package 구조는 구현 후 조정 가능하지만 **dependency direction**은 고정한다.

```text
legacy → vNext core allowed
vNext core → legacy forbidden
```

### Tasks

- R23 session read adapter 여부 결정
- old stage artifacts read-only archive 지원
- deprecated API warning
- migration guide
- release line separation

### Definition of Closed

- [ ] vNext normal import path에 R23 stage classes가 필요 없음
- [ ] old sessions를 최소 read/replay 가능하거나 unsupported를 명확히 선언
- [ ] legacy adapter가 new API shape를 결정하지 않음
- [ ] deprecation timeline 문서화

### REOPEN

- compatibility 때문에 vNext에 stage semantics 재도입
- two workflows가 장기간 같은 priority로 유지됨

---

## B13 — Single-subject E2E quality closure

### Goal

현재 문제를 드러낸 same sniper-girl subject에서 vNext가 **더 좋은 그림을 더 적은 ceremony로** 만드는지 검증한다.

### Input

- packaged vNext skill
- same `subject.png`
- one user goal

### Worker condition

개발 좌표를 직접 넘기지 않는다.

### Compare against

- Gemini R23 result
- Claude partial R23 result
- current R23 canonical outputs

### Evaluate

- whole pose / line of action
- head / ribcage / pelvis mass relation
- balance / plumb / grounding
- torso rotation
- head turn
- arm overlap
- leg stance
- feet
- rifle topology/contact
- contour quality
- selective detail discipline
- line/value hierarchy
- completion cost

### Definition of Closed

- [ ] final drawing이 Gemini result보다 명백히 높은 likeness
- [ ] Claude가 지적한 critical geometry traps를 runtime inspection tools로 검출 가능
- [ ] P1/P2 manifest ceremony 없이 E2E 완료
- [ ] custom inspection helper script 재발명 불필요
- [ ] review evidence량이 R23 strict path보다 감소
- [ ] full session + end-to-end GIF 제공
- [ ] final whole-view residual sweep에서 high-impact defect 없음

### REOPEN

- 좋은 그림을 만들었지만 subject-specific hardcoding 사용
- cost가 R23보다 더 큼
- inspection quality가 낮아져 mismatch를 놓침

---

## B14 — Cross-agent same-subject reproducibility

### Goal

한 agent의 숙련도에만 의존하지 않는지 확인한다.

### Workers

최소 서로 다른 두 agent/session.

예:

- Claude-family worker
- Gemini-family 또는 다른 coding agent

### Inputs

동일:

- packaged skill
- subject
- user goal

개발 conversation/handoff 없이 실행.

### Evaluate

- both complete?
- same gross pose?
- both detect major mismatches?
- both use inspection tool rather than inventing bespoke pipelines?
- one agent only produces schema-complete weak result?

### Definition of Closed

- [ ] 두 worker 모두 E2E 완료
- [ ] 둘 다 macro identity threshold를 만족
- [ ] 한 worker가 ceremony를 스킵해도 core integrity 유지
- [ ] API가 특정 agent의 reasoning style에 과적합되지 않음
- [ ] failure differences가 skill guidance 개선으로 환원 가능

### REOPEN

- 한 agent만 사용 가능
- 다른 agent가 API boilerplate에서 막힘
- agent별 결과 variance가 너무 큼

---

## B15 — Diverse-subject generalization

### Goal

한 전신 캐릭터 subject를 벗어난다.

### Subject matrix

한 번에 모두 하지 않는다. 하나씩 진행한다.

1. front / front-three-quarter human
2. side/back-three-quarter human
3. dynamic crouch/run/jump
4. severe limb occlusion
5. no-prop figure
6. large-prop figure
7. stylized non-realistic character
8. upper-body / portrait-biased crop

### Rule

한 subject가 실패하면 다음 subject로 넘어가지 않는다.

가장 높은-impact failure regime를 먼저 harden한다.

### Definition of Closed

- [ ] 최소 4개의 서로 다른 failure regime에서 E2E 성공
- [ ] subject-specific coordinate heuristic 없음
- [ ] inspection ROI selection이 subject마다 유연
- [ ] stage vocabulary 없이도 macro→detail hierarchy 유지
- [ ] no systematic failure across view orientation

### REOPEN

- 특정 view만 잘 그림
- prop 유무에 workflow가 무너짐
- stylized subject에서 anatomy prior를 강요

---

## B16 — Failure-regime hardening

### Goal

다양한 dogfood에서 반복적으로 나타난 failure를 일반 capability로 해결한다.

### Candidate regimes

- hair silhouette eats face opening
- dark garment hides overlay
- long boots confuse ankle
- garment edge mistaken for limb axis
- rifle/prop becomes rails
- torso/arm contour welding
- feet become generic wedges
- head becomes generic circle/helmet
- limbs become parallel rails
- line becomes CAD-like
- detail pass destroys line hierarchy
- agent accepts weak whole pose because local checks pass

### Process

각 failure마다:

```text
failure
→ earliest general cause
→ smallest reusable capability/guidance change
→ same-subject retest
→ different-subject regression
```

### Definition of Closed

- [ ] fixes are general, not coordinate patches
- [ ] each hardening has at least one negative fixture
- [ ] no new mandatory bureaucracy introduced unless proven necessary
- [ ] visual improvement verified directly

### REOPEN

- failure is “solved” only by adding another manifest
- tests pass but artifact remains weak
- fix harms another subject regime

---

## B17 — Package / CI / docs / release truth

### Goal

vNext implementation과 실제 package가 일치한다.

### Package requirements

- source authority clear
- no build/dist duplicate tree in installed skill
- no embedded dogfood coordinates
- minimal runtime dependencies
- install docs accurate
- smoke test after clean install
- checkpoint/resume test
- InspectionSheet test
- replay/timelapse test

### CI layers

#### Mechanical CI

- unit tests
- schema/state migration tests
- package install
- deterministic artifact tests
- no stale absolute paths

#### Dogfood CI

자동 art-quality score는 만들지 않는다.

가능하면 lightweight fixture 생성만 수행하고, visual approval는 release evidence로 별도 관리.

### Docs

최종 skill-facing docs는 workflow를 짧게 설명해야 한다.

Fresh worker가 처음 읽어야 할 핵심은:

```text
1. observe whole
2. make whole-figure construct
3. inspect one sheet
4. fix biggest mismatch
5. repeat
6. finish only after structure holds
7. final residual sweep
```

### Definition of Closed

- [ ] clean package install 성공
- [ ] README/dependency/version 일치
- [ ] skill docs에 legacy workflow가 primary로 보이지 않음
- [ ] fresh worker가 별도 developer explanation 없이 시작 가능
- [ ] release artifacts hashes current source와 일치
- [ ] independent evaluator가 representative outputs 검토
- [ ] current release limitations 명시

### REOPEN

- package가 source와 다름
- build/lib duplicate가 worker를 오도
- docs가 runtime과 불일치
- release label이 actual dogfood evidence보다 강한 주장

---

## B18 — Legacy workflow retirement

### Goal

vNext가 실제로 우수함이 증명된 후 R23 workflow를 primary product에서 내려놓는다.

### Preconditions

B13–B17 CLOSED 전에는 진행하지 않는다.

### Actions

- R23 stage workflow를 legacy namespace/archive로 이동
- primary docs에서 제거
- old examples를 legacy label
- stage manifests를 compatibility-only로 전환
- release notes에 migration path 기록

### Definition of Closed

- [ ] default user workflow가 vNext only
- [ ] R23 자료가 history/reference로는 접근 가능
- [ ] new worker가 R23과 vNext 중 무엇을 써야 할지 혼동하지 않음
- [ ] legacy code가 active maintenance surface를 과도하게 늘리지 않음

### REOPEN

- vNext가 일부 중요한 R23 capability를 아직 잃고 있음
- migration 때문에 user session이 손상됨
- legacy 제거 후 replay/provenance 기능 회귀

---

# 6. Dependency and selection map

이 도식은 **hard prerequisite와 feedback 위치**만 나타낸다. 번호순 자동 progression이 아니다.

```text
B00 legacy baseline
 ↓
B01 architecture contract
 ↓
B02+B03 Inspection Foundation       # one production slice
 ↓
B04 minimal stage-agnostic session
 ↓
B05 initial construction grammar
 ↓
B06 correction loop
 ↓
D0 EARLY STRUCTURAL DOGFOOD
 ├── weak evidence → earliest false premise REOPENED
 └── holds         → rank the remaining candidates again

REMAINING CANDIDATE POOL
  B07  evidence cost control
  B08  edit ergonomics
  B09  finish capability ──→ B10 completion contract
  B11  resume/replay parity
  B12  legacy boundary
  B13  full single-subject E2E
  B14  cross-agent reproducibility
  B15  diverse subjects
  B16  repeated failure hardening
  B17  release truth
  B18  legacy retirement
```

B00→B06과 D0까지는 현재 확인된 hard dependency다. D0 이후의 다음 ACTIVE는 번호가 아니라
다음 기준으로 다시 선택한다.

```text
Priority = Impact × Uncertainty × Reusability
```

예를 들어 D0에서 inspection cost가 여전히 가장 큰 문제면 B07을 선택한다. stroke authoring
boilerplate가 correction을 막으면 B08을 선택한다. resume가 실제 dogfood를 중단시키면 B11이
먼저 올 수 있다. 단, B09 finish보다 B10 final completion이 먼저 올 수 없고, B13–B17이 닫히기
전에는 B18을 시작하지 않는 hard dependency는 유지한다.

**Bottleneck slice graph를 새 runtime stage graph로 번역하지 않는다.**

---

# 7. Global closure rules

## 7.1 Macro correctness first

다음이 틀렸으면 detail/renderer를 다듬지 않는다.

- pose
- mass
- silhouette
- major overlap
- grounding
- major object relation

## 7.2 Construction → observation → correction → validation

validation artifact를 많이 만든다고 closure하지 않는다.

## 7.3 One highest-impact bottleneck

한 loop에서 최대 1–3개 문제만 수정한다.

작은 디테일 20개보다 torso rotation 하나를 먼저 고친다.

## 7.4 Visual evidence wins over checklist

테스트/CI/schema가 PASS해도 실제 drawing이 약하면 OPEN이다.

## 7.5 Reopen the premise, not the bookkeeping

vNext에서는 stage reopen 대신 **현재 그림에서 잘못된 premise 자체를 수정**한다.

필요하면 큰 영역 전체를 replace한다.

## 7.6 Stop polishing when no longer limiting quality

detail 추가가 perceptual quality를 더 이상 크게 올리지 않으면 끝낸다.

---

# 8. Global metrics — observe, do not optimize blindly

이 수치들은 release gate를 자동 결정하지 않는다.

변화의 방향을 보는 telemetry다.

## Quality

- whole-pose likeness
- silhouette/mass fidelity
- negative-space fidelity
- overlap/contact readability
- head/face orientation
- feet/grounding
- prop topology
- line hierarchy
- pencil material quality

## Efficiency

- number of inspection loops
- images opened/read
- number of generated evidence artifacts
- custom helper scripts created by worker
- correction actions
- redraw ratio
- session completion rate
- wall-clock / token or image usage where observable

## Generalization

- subjects completed
- view regimes completed
- agents completed
- repeated failure regimes
- coordinate hardcoding incidents

---

# 9. Explicit non-goals

vNext reset 동안 다음은 하지 않는다.

- 새로운 renderer family 추가
- image generation 사용
- automatic pose estimator를 geometry authority로 승격
- CV score로 art-quality PASS 자동화
- 3D mannequin solver를 core dependency로 추가
- P1–P6와 동일한 새 stage 이름을 다시 만드는 것
- 모든 subject category를 한 번에 지원
- dashboard/reporting UI 확대
- provenance를 이유로 drawing API를 복잡하게 만드는 것

---

# 10. Repository transition proposal

권장 transition layout:

```text
skills/img2drawing/
  SKILL.md
  playbooks/
    vnext-drawing-loop.md
    finishing.md

  references/
    observation/
    drawing/
    pencil/

  src/img2drawing/
    core/
    canvas/
    render/
    provenance/

    inspection/
      sheet.py
      overlay.py
      measurement.py

    vnext/
      session.py
      correction.py
      memory.py
      finish.py

    legacy/
      r23/
        ...

dev/
  planning/
    vnext/
  dogfood/
    vnext/
  tests/
    vnext/
  release/
```

실제 file tree는 구현 중 바뀔 수 있다.

중요한 것은 dependency direction이다.

이 layout은 기존 tree 전체를 `vnext/`와 `legacy/r23/` 양쪽에 복사하라는 뜻이 아니다.
R23은 frozen/read-only baseline이며 active production implementation으로 병행 확장하지 않는다.
공유 가능한 stage-independent implementation은 한 곳만 authority를 가지며, legacy 쪽에는 필요한
adapter와 archive boundary만 둔다. B01 dependency audit 전에는 대규모 파일 이동이나 duplicate tree를 만들지 않는다.

---

# 11. Suggested first production sequence

현재 가장 적절한 실제 작업 순서는 다음이다.

```text
NOW
 ↓
B00 — baseline/failure dossier                         ACTIVE
 ↓
B01 — architecture cut
 ↓
B02+B03 — Inspection Foundation                       one slice
 ↓
B04 — minimal stage-agnostic session
 ↓
B05 — ordered construction grammar
 ↓
B06 — correction loop
 ↓
D0 — EARLY STRUCTURAL DOGFOOD (B06 closure gate)
 ↓
RE-RANK remaining candidates by current bottleneck
```

B09 finish mode까지 전부 구현한 뒤 처음 dogfood하지 않는다.

**D0는 B06의 Definition of Closed에 포함한다.** B05/B06 직후 unfinished prototype이라도 실제 subject로 그려서,
`Read → Line of Action → Mass → Balance → Joints/Limbs` grammar와 correction loop가
R23보다 실제로 좋은 whole-figure likeness를 만드는지 확인한다.

초기 dogfood에서 여전히 다음 현상이 보이면 B07 이후로 내려가지 말고 upstream을 REOPEN한다.

- inspection이 느림
- drawing이 generic
- torso/legs가 rail-like
- worker가 old P-stage mental model로 돌아감
- custom scripts를 다시 만듦
- artifact ceremony가 다시 증가

early dogfood가 통과해도 B07을 자동으로 ACTIVE로 만들지 않는다. 관측된 결과에 따라 remaining
candidate의 Impact × Uncertainty × Reusability를 다시 평가한다.

---

# 12. Release philosophy

vNext의 release closure는 다음 네 축이 모두 필요하다.

```text
1. ENGINEERING
   state/history/render/resume/replay correct

2. VISUAL
   actual drawings materially strong

3. EFFICIENCY
   review machinery does not dominate production

4. GENERALIZATION
   different subject + different agent works
```

어느 하나라도 빠지면 final CLOSED가 아니다.

특히 다음 문장은 release rule로 유지한다.

> **A mechanically valid run can still be a bad drawing.**
>
> **A visually good one-off script can still be a bad skill.**
>
> **A general skill that is too expensive to finish can still be a failed workflow.**

---

# 13. Final target

vNext가 성공했을 때 fresh worker가 이해해야 하는 workflow는 아래 정도로 짧아야 한다.

```text
Read the whole pose before drawing:
weight, dominant flow, silhouette, negative space, ground and prop relation.

Draw one or two lines of action.

Block the head, ribcage and pelvis as oriented masses.
Check their tilt, rotation, scale and twist.

Check balance with a plumb/ground guide.

Place the major joints and connect the limbs as observed, tapered forms.
Include both feet, occluded limbs and the major prop early.

Now the whole figure must already read as this subject's pose.

Render one inspection sheet:
subject, drawing, contrast overlay, 1–3 uncertain enlarged regions,
and optional grid/plumb measurements.

Name only the 1–3 mismatches that hurt likeness most.
Correct those strokes explicitly.

Inspect again.
Do not treat an edit as proof that it worked.
Move backward in the construction grammar whenever the evidence requires it.

Repeat until pose, balance, mass, overlap and major part identity hold.

Then refine the contour.

Add only the detail the requested croquis duration/finish needs.

Calibrate pencil hierarchy and add selective accents.
For a long pose, optionally group the observed large shadow masses;
do not substitute arbitrary charcoal bands for form.

Finish with one fresh whole-view residual sweep.

Keep the full session, replay and end-to-end timelapse.
```

이를 한 문장으로 압축하면:

> **Ordered construction grammar, non-linear visual correction, lightweight evidence.**

즉 fresh worker는 그림을 만들 때 무엇을 먼저 봐야 하는지는 분명히 알지만,
runtime gate 때문에 잘못된 구조를 끝까지 보존하거나 수십 개의 manifest를 작성하지 않아야 한다.

이 정도의 설명으로 fresh worker가 실제로 좋은 결과를 낼 수 있어야 한다.

그렇지 않다면 workflow는 아직 충분히 단순하거나 강하지 않은 것이다.
