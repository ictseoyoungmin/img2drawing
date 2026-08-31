# Contour, overlap and selective cleanup

clean은 더 진하게 덧칠한다는 뜻이 아니라 어떤 선이 현재 form을 가장 잘 전달하는지
선택한다는 뜻이다.

## Ownership

외곽·face opening·hair mass·garment·prop가 겹치는 곳에서는 contour ownership을
명시한다. 한 mass가 다른 mass로 넘어갈 때 선을 끊거나 occlusion을 남기고, 독립된
contour를 하나의 welded line으로 합치지 않는다.

## Structure before surface

hair는 cranium 위의 큰 mass, 옷은 shoulder–sleeve–joint chain 위의 hang, footwear는
ankle에서 자라는 volume, prop은 axis·width change·body contact로 먼저 해결한다.
주름·머리카락 한 올·표면 texture는 이런 구조가 읽힌 뒤에만 선택한다.

## Retire without raster editing

새 representation이 이전 선의 정보를 이어받으면 `soft_lift`로 유용한 cue를 남기거나
`delete_stroke`로 현재 branch에서 제거한다. 두 경우 모두 history와 provenance는
보존한다. 파일을 raster-edit하거나 history 밖에서 지우지 말고, fresh render와
inspection으로 실제 개선을 확인한다. 자세한 공통 API는
[`review/stroke-retirement.md`](../review/stroke-retirement.md)의 stage-free 부분을
참조한다.
