# Tone, value and fill

값을 만드는 것은 stroke를 많이 쌓는 일이 아니라 region 하나를 선언하는 일이다.

## Form before value

값은 **이미 성립한 형체를 보강하는 수단**이다. silhouette, contour, overlap이 틀린
상태를 어두운 hatch나 reserved light로 가려서 해결하지 않는다.

fill을 넣기 전에 현재 그림을 line-only / tone-off 상태라고 가정해서 다시 읽는다.
이 상태에서도 다음이 보여야 한다.

- 팔과 다리의 실제 두께와 앞뒤 관계
- 몸통과 팔다리의 분리 및 접속
- 재킷·치마·부츠 같은 큰 착장 덩어리의 부피
- 손과 prop의 접촉 및 주요 overlap

이 중 하나가 값이 있어야만 읽힌다면 현재 bottleneck은 value가 아니라 form이다.
`replace_stroke()`, `replace_segment()`, `soft_lift()` 등으로 contour/overlap premise를
먼저 고치고 다시 inspect한다. 그 뒤에만 tone을 추가한다.

`ReservedLight`도 같은 원칙을 따른다. 이미 올바르게 분리된 형태 안에서 subject에
실제로 관찰되는 rim light, fold light, reflected light를 남기는 장치이지, 존재하지 않는
팔-몸통 경계나 부피를 만들어내는 장치가 아니다.

## Region fill로 값을 만든다

검은 옷, 스타킹, 부츠, 머리 그림자처럼 넓은 값 영역은 `DrawingSession.fill_region()`
하나로 만든다. 개별 명암선을 손으로 반복해서 쌓지 않는다.

```python
fill_id = session.fill_region(
    jacket_polygon,
    value=120,                    # subject에서 읽은 평균 값 (0 검정 - 255 종이)
    part="jacket_tone",
    angle=74.0,
    observation_id="observation-0001",
    reason="black tactical jacket, lit from image-right",
)
```

`value`는 **subject에서 직접 측정해서 넣는다.** opacity/pressure를 추측하지 않는다.
그 둘은 캘리브레이션된 [tone scale](../../src/img2drawing/data/tone_scale.json)에서
자동으로 결정된다.

### 왜 opacity를 직접 쓰지 않는가

pencil-contact 렌더러의 침착량은 opacity 숫자에 비례하지 않는다. `opacity=0.24`는
합리적으로 보이지만 거의 빈 종이로 렌더된다. 한 dogfood 세션은 이 사실을 모른 채
값을 한 단계 움직이려고 stroke 372개를 쌓았고, 최종 session이 31만 줄이 되었다.
렌더러 특성은 그림의 provenance가 아니므로 세션 안에서 탐색하지 않는다.

**세션 안에서 renderer probe를 돌리지 않는다.** 캘리브레이션이 틀렸다고 판단되면
`dev/calibration/calibrate_tone_scale.py`를 다시 돌려 표를 갱신한다.

## 값이 틀렸으면 region 자체를 수정한다

fresh inspection이 이전 value premise를 반박하면 같은 영역에 fill을 하나 더 겹치지
않는다. `replace_fill_region()`으로 기존 fill identity를 유지한 채 새 정의를 append한다.

```python
from img2drawing import replace_fill_region

correction_action_id = replace_fill_region(
    session,
    fill_id,
    value=90,
    reason="fresh inspection shows the jacket is darker than the first estimate",
    observation_id="observation-0001",
)
```

`replace_fill_region()`은 새 `action_id`를 반환한다. residual correction을 기록할 때 그
값을 그대로 `record_correction(..., action_ids=[correction_action_id])`에 사용한다. generated
hatch stroke 수백 개를 correction action으로 열거하지 않는다.

## 빛은 남기는 것이지 지우는 것이 아니다

옷의 하이라이트, 이미 contour/overlap로 분리된 팔이나 착장의 rim light, 부츠의 끈
패널처럼 어두운 덩어리 안에서 실제로 관찰되는 밝은 부분은 **칠한 뒤 지우지 않는다.**
fill이 처음부터 비워두게 한다.

```python
session.fill_region(
    sock_polygon, value=65, part="sock_tone", angle=82.0,
    reserved=[{"path": [(338, 950), (330, 1120), (336, 1232)],
               "width": 6.0, "strength": 1.0, "note": "rim light down the shin"}],
    observation_id="observation-0001",
    reason="black over-knee sock with a rim light on the leading edge",
)
```

`strength=1.0`은 예약한 빛을 완전히 남기고, 낮은 값은 일부 명암을 통과시킨다.

## 값의 위계

한 그림 안에서 값 군(family)은 서너 단계면 충분하다. 단계마다 `fill_region`을 한 번씩
쓰고, 같은 영역에 여러 번 덧대어 값을 만들지 않는다. 영역의 명암 밀도는 `value` 하나로
조절한다. 이미 만든 영역의 판단을 바꿀 때는 `replace_fill_region()`을 사용한다.

## 하지 말 것

- form이 line-only 상태에서 읽히지 않는데 hatch로 두께·분리를 대신하는 것.
- `for` 루프로 개별 명암선을 만들어 `draw_many()`에 넘기는 것. `fill_region()`이 있다.
- 직선 명암선을 일정 간격으로 샘플링해 점 10~20개로 저장하는 것.
- 값이 안 나온다고 같은 영역에 fill을 여러 번 겹치는 것. 기존 region을 revise한다.
- opacity/pressure/grade를 직접 조합해 값을 맞추는 것. `value`로 말한다.
