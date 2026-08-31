# Balance, joints, limbs and feet

## Balance

어느 발이 지지하는지, pelvis가 어느 쪽으로 counterbalance하는지, 두 발이 같은
ground plane에 닿는지 먼저 확인한다. shoulder/pelvis tilt와 발 사이 negative
space가 함께 읽혀야 한다. 중심선을 길게 그었다고 balance가 해결되는 것은 아니다.

## Joint chains

관찰 가능한 shoulder, elbow, wrist와 hip, knee, ankle을 각각 찾는다. 소매 끝은
wrist가 아니고, waistband는 hip이 아니며, jean hem은 ankle이고 shoe 아래가
foot이다. 가려진 joint는 visible endpoint와 body connection으로 추론하되,
불확실성을 명시한다.

한 centre-path 곡선은 관절을 통과하며 span의 tangent와 convex/concave 변화를
보존한다. 맞는 joint를 직선으로 잇거나 두 평행선으로 bracket하면 wire dummy나
옷 외곽이 된다. volume과 taper는 다음 representation에서 별도로 추가한다.

## Feet and occlusion

발의 방향·길이·foreshortening은 pose와 weight의 일부이므로 늦은 장식이 아니다.
발목에서 ground로 이어지는 wedge를 관찰하고, 끈·패널·주름은 나중으로 미룬다.
prop나 옷 뒤에 숨은 팔·손도 최소 gesture를 남겨 shoulder rhythm과 torso turn을
잃지 않는다.

## Inspectable hypothesis

첫 whole figure가 subject의 pose로 읽히지 않으면 contour/detail을 추가하지 않는다.
현재 snapshot을 render하고 subject와 나란히 또는 등록 overlay로 본 뒤, 틀린
premise와 responsible stroke를 구분해 명시적으로 교체한다.
