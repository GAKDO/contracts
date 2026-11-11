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

1. 부스 운영자가 목록에서 기기를 고르고 버튼을 누르면 BOT·TOP을 CAM1·CAM2, 조명 L1(확산, VL49)·L2(왼쪽 스침광, LED 바 #1)·L3(뒤쪽 스침광, LED 바 #2)로 찍는다(사진 12장, booth #21과 같음). 얕은 긁힘은 옆 스침광에서 보인다(민서 11/3).
2. 부스가 `profile: QUICK` 세트를 만들고 사진을 올린 뒤 완료하고, Jetson 탐지 결과를 보낸다.
3. capture-server가 정합 없이 그 탐지로 등급을 매기고(A = 문제 없음), 관리자 화면이 원본 사진 위에 흠집 폴리곤을 겹쳐 본다.

## 요구사항

- FR-1 codes.yaml `capture.profile: [FULL, QUICK]`, `capture.face_required_quick.BOOTH: [TOP, BOT]`를 더한다.
- FR-2 세트 생성 요청·세트 응답에 선택 필드 `profile`을 더한다. 빼면 FULL. QUICK + source=PHONE은 400.
- FR-3 QUICK 세트 완료는 `face_required_quick`로 검사한다.
- FR-4 QUICK 세트는 완료 + 부스 탐지가 있으면 정합 없이 등급을 매긴다. 시점 비교는 하지 않는다(match = null). 같은 면·같은 카메라의 조명만 다른 사진에 겹친 흠집은 등급을 셀 때만 하나로 센다. 겹침 기준은 같은 면·같은 카메라에서 흠집 폴리곤 중심이 원본 px 20 px 안(부스 카메라·받침이 고정이라 조명만 바꾼 사진은 거의 같은 자리). 다른 카메라 사진은 합치지 않는다. 흠집(`Defect`)은 합치지 않고 사진별로 그대로 돌려주므로, 관리자 화면은 각 흠집의 camera·light로 그 사진에 겹쳐 그린다(대표 사진 고르기 없음).
- FR-5 검사 결과 `Inspection`에 선택 필드 `photoDefects`(PhotoDefect: 면·조명·카메라·원본 px polygon)를 더한다. QUICK 세트는 흠집을 여기에만 넣고 `defects`는 빈 배열(`Defect.polygon`은 늘 표준 좌표, 민서 11/3 결정).
- FR-5b 부스 탐지 요청에 선택 필드 `analyzedPhotos`를 더한다. QUICK 세트는 필수이고 TOP·BOT 세트 사진을 모두 담아야 한다(아니면 400). 흠집 없는 사진은 여기에만 넣는다.
- FR-6 `CheckpointMedia`에 선택 필드 `photos`(면·조명·카메라·보기 URL)를 더한다.
- FR-7 기존 필드·경로·코드 값은 바꾸지 않는다. 이벤트·리포트에는 선택 필드 `compared`만 더한다(리뷰 반영).

## 수용 기준

- profile 없이 만든 부스 세트는 지금처럼 8면이 있어야 완료된다.
- QUICK 세트는 TOP·BOT만으로 완료되고, 부스 탐지가 오면 정합 없이 등급이 나온다(흠집 0개면 A).
- QUICK 폰 세트는 400이다.
- `계약 검사` CI(yamllint·코드 생성본·이벤트·redocly)가 통과한다.

## 범위 밖

- `trace.capture.uploaded`에 profile 싣기(MVP에는 inspect-worker가 없음, 2단계에 워커를 다시 켤 때 추가)
- QUICK 세트의 mm 길이 환산(부스 카메라 배율 실측 뒤)

## 리뷰 반영 (11/3)

- 두 카메라가 면의 앞·뒤 반을 나눠 찍으므로 QUICK 필수 면(TOP·BOT)은 CAM1·CAM2 사진이 모두 있어야 완료된다. 하나라도 없으면 409 CAPTURE_FACES_MISSING.
- QUICK은 앞 시점과 비교하지 않는다. trace.checkpoint.graded와 리포트 TimelineCheckpoint에 선택 필드 `compared`를 더해 false로 알린다(이벤트 1.2. 출고·기준선도 false, 값이 없는 1.1 이벤트는 OUT이면 false, 그 밖에는 true). newDefectIds 빈 배열이 '신규 없음'으로 읽히지 않게 한다.
- 원본 px 흠집은 `Defect`가 아니라 별도 필드 `photoDefects`로 돌려준다(민서 11/3 결정). 기존 소비자는 `defects[].polygon`을 늘 표준 좌표로 읽어도 된다.
- 일부 사진만 분석한 탐지 요청으로 등급이 나지 않게, QUICK 탐지 요청은 `analyzedPhotos`로 TOP·BOT 사진 전부의 분석 완료를 알린다.
- 탐지가 완료보다 먼저 와도 완료할 때 등급을 매긴다.
