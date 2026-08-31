# Tone, value and fill

값을 만드는 것은 stroke를 많이 쌓는 일이 아니라 region 하나를 선언하는 일이다.

## Region fill로 값을 만든다

검은 옷, 스타킹, 부츠, 머리 그림자처럼 넓은 값 영역은 `DrawingSession.fill_region()`
하나로 만든다. 개별 명암선을 손으로 반복해서 쌓지 않는다.

```python
session.fill_region(
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

## 빛은 남기는 것이지 지우는 것이 아니다

옷의 하이라이트, 팔과 몸통 사이의 끊김, 부츠의 끈 패널처럼 어두운 덩어리 안의 밝은
부분은 **칠한 뒤 지우지 않는다.** fill이 처음부터 비워두게 한다.

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
조절한다.

## 하지 말 것

- `for` 루프로 개별 명암선을 만들어 `draw_many()`에 넘기는 것. `fill_region()`이 있다.
- 직선 명암선을 일정 간격으로 샘플링해 점 10~20개로 저장하는 것.
- 값이 안 나온다고 같은 영역에 fill을 여러 번 겹치는 것. `value`를 낮춘다.
- opacity/pressure/grade를 직접 조합해 값을 맞추는 것. `value`로 말한다.
