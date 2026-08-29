# img2drawing project handoff

이 문서는 다음 agent가 현재 상태를 빠르게 파악하고 작업을 이어가기 위한 기준점이다.

## 현재 상태

- 기준일: 2026-08-29
- 최신 커밋: `9dc743e Reopen and harden P3 reference run`
- 작업 트리: 이 파일을 추가하기 전에는 clean 상태
- 현재 reference run 단계: `P4_structural_connections`
- P1/P2/P3 predecessor 및 P3 reopen 결과는 `dev/p3_reference_run/`에 있다.

P3의 첫 branch는 downstream whole/crop/overlay audit에서 다음 문제로 실패했다.

- torso가 평평한 직사각형처럼 보임
- 양쪽 다리가 rail처럼 평행하게 보임
- head가 방향 없는 egg처럼 보임

그 branch는 `run/reopen_archive/reopen_01/`에 보관되었고, `P3_primary_masses`를 새로 6-pass 재구성했다. 이후 왼쪽 지지 다리의 overlay 좌표가 바지 폭과 맞지 않는 문제를 다시 발견하여 pelvis 접점부터 허벅지·무릎·종아리·발목 station을 사진 실루엣 기준으로 수정했다.

## 이어서 읽을 파일

작업 시작 전에 다음 순서로 읽는다.

1. `skills/img2drawing/SKILL.md`
2. `skills/img2drawing/playbooks/autonomous-stage-hardening.md`
3. `skills/img2drawing/playbooks/full-body-croquis.md`
4. `skills/img2drawing/references/stages/p4-structural-connections.md`
5. `skills/img2drawing/references/review/self-visual-audit.md`
6. `skills/img2drawing/references/review/reopen-recovery.md`

P3에서 보완한 핵심 규칙은 다음과 같다.

- process packet이 완성되어도 visual PASS를 의미하지 않는다.
- 매 mutation 후 raw whole view, subject beside drawing, same-coordinate overlay, high-risk crop을 모두 다시 본다.
- 각 stage-purpose assertion은 `PASS`, `FAIL`, `UNCERTAIN` 중 하나로 기록한다.
- 하나라도 실패하거나 critical uncertainty/stale evidence가 있으면 `decision="revise"`로 둔다.
- 현재 stage가 아니라 이전 stage의 `must_preserve` 정보가 깨졌다면 가장 이른 책임 stage에 `run.reopen_stage()`를 호출한다.
- `delete_stroke`/`soft_lift`는 representation ownership이 넘어갈 때 사용한다. action 발생 자체는 개선의 증거가 아니다.

## P3 결과와 검증 자료

- 전체 비교: `dev/p3_reference_run/compare.png`
- 최종 overlay: `dev/p3_reference_run/overlay.png`
- 최종 raw P3: `dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/current_drawing.png`
- 최종 visual gate: `dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/visual_fidelity_review.json`
- 8-region closure: `dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/region_closure_manifest.json`
- blind packet: `dev/p3_reference_run/run/reviews/P3_primary_masses/pass_06/blind_visual_packet.json`
- reopen 사유/대상: `dev/p3_reference_run/run/reopens/reopen_01.json`
- canonical trace: `dev/p3_reference_run/canonical_trace.json`
- resumable checkpoint: `dev/p3_reference_run/run/session/checkpoint.json`

현재 canonical trace는 P3를 `advance`하여 P4를 가리키지만, P4 drawing 작업은 아직 시작하지 않았다. P3 최종 overlay를 다시 확인한 뒤 P4를 시작해야 한다.

## 재생성 및 검증 명령

P3 reference run 전체를 처음부터 재생성할 때:

```bash
python3 dev/p3_reference_run/build.py
```

이 명령은 `dev/p3_reference_run/run/`을 fresh P1/P2 predecessor부터 다시 만든다. P3의 의도적인 실패 branch를 기록하고 reopen한 뒤 corrected six-pass branch를 생성한다. 공개 reference build에서는 선택적 timelapse을 끈 상태다.

테스트:

```bash
PYTHONPATH=skills/img2drawing/src python3 -m pytest -q dev/tests
```

마지막 확인 결과는 `53 passed`였다. 환경에 설치된 skill validator도 별도로 실행해 skill 구조를 확인한다. canonical trace, blind packet, visual fidelity review schema도 통과했다.

## Git/산출물 정책

`.gitignore`는 P3의 반복 산출물을 제외하고 다음만 커밋 대상으로 남긴다.

- source script, README, root `canonical_trace.json`, `compare.png`, `overlay.png`
- resumable `checkpoint.json`/`session.json`
- `reopen_01` provenance와 최종 P3 pass-6 review JSON/worker packet
- 최종 raw drawing 및 비교용 선택 pass drawing

P1/P2 predecessor review, P3 중간 pass packet, crop/overlay/diff PNG, reopen archive, timelapse, duplicate final compare는 무시된다. 무시된 raster는 checkpoint에서 재생성할 수 있다.

## 다음 작업: P4

P4의 책임은 P3 volume 위에 실제 구조를 연결하는 것이다. 현재 contract에서 허용되는 예는 hair의 큰 mass, 옷이 volume에 걸리는 방식, footwear/hand의 resolved form, major prop structure다. P3에서 금지된 facial feature, individual hair strand, finished garment seam을 P4 전 단계로 끌어올리지 않는다.

P4 작업 중 P3의 torso/leg/head volume이 다시 overlay에서 틀린 것으로 드러나면 P4에서 선으로 보상하지 말고 P3를 reopen한다. 반대로 P3 volume이 유지되고 P4 구조만 틀린 경우에는 P4 안에서 `revise`한다.

정상적인 P4 루프는 다음과 같다.

```text
read P4 contract → whole observation → bounded structural strokes
→ prepare_stage_review → raw/subject/overlay/high-risk crop audit
→ PASS/FAIL/UNCERTAIN 기록 → revise 또는 advance
```

일반 drawing/review/final/timelapse 렌더러는 `img2drawing.render.pillow_pencil_contact`만 사용한다. legacy `pillow` renderer를 되살리지 않는다.

## 알려진 주의점

- `DrawingRun` runtime은 artifact freshness와 history binding을 검증하지만 그림의 예술적 정확성을 자동 판정하지 않는다. 다음 agent도 blind packet을 읽고 직접 visual 판단해야 한다.
- 공개용 JSON/MD에는 호스트별 절대경로를 넣지 않는다. 새 산출물을 추가할 때 경로가 checkout 상대경로인지 확인한다.
- 일반 `local_review.schema.json`은 현재 P3 생성물의 `grammar`/`task_target` 표현과 완전히 일치하지 않고, generic `review.schema.json`은 P3의 subject-only authority order와 맞지 않는 부분이 있다. 이 문제를 발견해도 P3 canonical/blind/visual gate 및 전체 테스트 통과 사실과 혼동하지 말고, schema/runtime 계약을 바꿀 때는 별도 수정으로 다룬다.
- 새 변경은 사용자가 별도로 commit을 요청하기 전까지 자동 commit하지 않는다.
