# 명세: 기기별 렌탈 이력 목록·상세

- 기능 브랜치: `claude/project-thread-qohtf2` (contracts, rental_server, gateway, web)
- 날짜: 2026-11-06
- 요청: 11/6 강사님 브리핑 피드백 4번("기기별 대여·렌탈 이력을 목록으로 보고 상세 조회가 되는가") → 민서 진행 승인
- 계약 1.0.0 고정 이후 **추가만** 하는 변경
- 관련 요구사항: FR-RNT-05(기기 관리), FR-RNT-02(렌탈과 세 시점 상태)

## 배경

관리자는 렌탈 목록과 렌탈 상세는 볼 수 있지만, 기기 하나를 골라 그 기기가 지금까지 누구에게 언제 대여됐는지 볼 길이 없다.
`GET /rentals`에 기기 거르기가 없고, 기기 하나를 읽는 경로(`GET /devices/{deviceId}`)도 없다.

## 사용자 시나리오

1. 관리자가 기기 목록에서 기기를 누르면 기기 상세(시리얼·기종·상태)와 그 기기의 렌탈 이력 표가 보인다.
2. 이력 표의 행마다 대여자 참조·렌탈 상태·지금 시점·출고 시작·종료 때가 보인다(최근 생성 순).
3. 행을 누르면 기존 렌탈 상세(세 시점·봉인·리포트)로 간다.

## 요구사항

- FR-1 `GET /api/v1/rentals`에 쿼리 `deviceId`(선택, PublicId). 주면 그 기기의 렌탈만. 역할별 거르기(CUSTOMER 클레임·BOOTH OPEN)는 그대로 겹친다. 없는 기기 ID면 빈 목록.
- FR-2 `RentalSummary`에 선택 필드 `renterRef`·`startedAt`·`endedAt`. rental-server는 항상 보낸다.
- FR-3 새 경로 `GET /api/v1/devices/{deviceId}`(ADMIN) → `Device`, 없으면 404.
- FR-4 기존 필드·경로·코드 값은 바꾸지 않는다.

## 수용 기준

- 기기 A·B에 렌탈이 있을 때 `deviceId=A`로 부르면 A의 렌탈만 최근 생성 순으로 나온다.
- `deviceId`와 `status`를 같이 주면 둘 다 맞는 렌탈만 나온다.
- 목록 항목에 `renterRef`·`startedAt`·`endedAt`이 렌탈 상세와 같은 값으로 있다.
- `GET /devices/{deviceId}`는 등록된 기기를 주고, 없는 ID는 404 `NOT_FOUND`.
- `계약 검사` CI(yamllint·코드 생성본·redocly)가 통과한다.

## 범위 밖

- 기기 목록에 렌탈 횟수 열(필요하면 다음에)
- 기기별 진단·흠집 추이(11/10 이후 diagnostics 재도입 때)
