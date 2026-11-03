# 명세: 부스 빠른 검사 세트(위·아래 2면)

- 기능 브랜치: `claude/project-thread-fbmwhp` (contracts, capture_server)
- 날짜: 2026-11-03
- 요청: 11/3 강사님 리뷰 → 최소 MVP 재조정(민서 승인). 계약 1.0.0 고정 이후 **추가만** 하는 변경
- 관련 요구사항: FR-CAP-01(세트 완료), FR-INS-01·04(탐지·등급), NFR-01(부스 한 세트 30초)

## 배경

MVP는 "부스에서 위·아래를 찍어 문제 있음/없음을 바로 판정"이다. 지금 계약은 부스 세트에 8면이 모두 있어야 완료되고
(`capture.face_required.BOOTH`), 등급은 inspect-worker 정합(INSPECTED)이 와야 매겨진다. 집 PC 상시 워커는 중단했으므로
2면 세트를 정합 없이 판정하는 길이 필요하다.

## 사용자 시나리오

1. 부스 운영자가 목록에서 기기를 고르고 버튼을 누르면 BOT·TOP을 CAM1·CAM2, 조명 L1로 찍는다(사진 4장).
2. 부스가 `profile: QUICK` 세트를 만들고 사진을 올린 뒤 완료하고, Jetson 탐지 결과를 보낸다.
3. capture-server가 정합 없이 그 탐지로 등급을 매기고(A = 문제 없음), 관리자 화면이 원본 사진 위에 흠집 폴리곤을 겹쳐 본다.

## 요구사항

- FR-1 codes.yaml `capture.profile: [FULL, QUICK]`, `capture.face_required_quick.BOOTH: [TOP, BOT]`를 더한다.
- FR-2 세트 생성 요청·세트 응답에 선택 필드 `profile`을 더한다. 빼면 FULL. QUICK + source=PHONE은 400.
- FR-3 QUICK 세트 완료는 `face_required_quick`로 검사한다.
- FR-4 QUICK 세트는 완료 + 부스 탐지가 있으면 정합 없이 등급을 매긴다. 시점 비교는 하지 않는다(match = null).
- FR-5 `Defect`에 선택 필드 `coordinateSpace`(STANDARD·PHOTO)·`camera`·`light`를 더한다. QUICK은 PHOTO(원본 px), 길이·넓이 null.
- FR-6 `CheckpointMedia`에 선택 필드 `photos`(면·조명·카메라·보기 URL)를 더한다.
- FR-7 기존 필드·경로·코드 값·이벤트 스키마는 바꾸지 않는다.

## 수용 기준

- profile 없이 만든 부스 세트는 지금처럼 8면이 있어야 완료된다.
- QUICK 세트는 TOP·BOT만으로 완료되고, 부스 탐지가 오면 정합 없이 등급이 나온다(흠집 0개면 A).
- QUICK 폰 세트는 400이다.
- `계약 검사` CI(yamllint·코드 생성본·이벤트·redocly)가 통과한다.

## 범위 밖

- `trace.capture.uploaded`에 profile 싣기(MVP에는 inspect-worker가 없음, 2단계에 워커를 다시 켤 때 추가)
- QUICK 세트의 mm 길이 환산(부스 카메라 배율 실측 뒤)
