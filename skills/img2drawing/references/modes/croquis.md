# Croquis mode

## Purpose

짧은 시간 안에 pose energy, balance, major mass, silhouette, line economy를 읽는다.
얼굴·값·표면 디테일은 요청과 residual이 요구할 때만 남긴다.

## Suggested grammar

```text
whole pose → line of action → head/ribcage/pelvis → balance → limbs/feet
→ inspect → selective contour
```

이는 runtime stage가 아니다. 뒤의 inspection이 앞의 가설을 반박하면 앞의 mass나
limb를 다시 그린다. feet와 큰 prop이 pose를 설명하면 초기에 포함한다.

## Completion questions

pose, stance, major silhouette, limb relation, ground contact, prop/body relation 중
material한 mismatch가 남아 있는가? Dense face/value를 생략해도 괜찮지만, 생략을
이유로 macro likeness를 포기하지 않는다.
