# Phase 0 조사: C1 OpenAPI 5개

## R1. 공통 형식을 어디에 둘까

- **결정**: `openapi/components/common.yaml` 한 파일에 두고 서버 파일에서 `$ref: './components/common.yaml#/components/schemas/Problem'`처럼 참조.
- **이유**: Problem Details·커서 목록·보안 방식이 5파일에서 같아야 한다. redocly·openapi-typescript 모두 상대 경로 외부 참조를 따라간다.
- **버린 안**: 파일마다 복사(어긋날 위험), 파일 하나로 합치기(서버별 리뷰·소비 불편, 백로그의 "5개"와 다름).

## R2. codes.yaml 값을 enum으로 어떻게 참조할까

- **결정**: `scripts/gen_openapi_codes.py`가 codes.yaml을 읽어 `openapi/components/codes.gen.yaml`에 `CaptureFace`·`DeviceStatus` 같은 enum 스키마를 만든다. CI에서 `--check`로 생성본이 최신인지 확인한다.
- **이유**: codes.yaml은 값 목록이라 JSON Schema로 바로 `$ref`할 수 없다(배열은 스키마가 아님). codes.yaml 구조를 바꾸면 B·C의 기존 사용처가 깨진다. 생성본 + 일치 검사는 "복사하지 않는다"의 뜻(값이 한 곳에서만 정해짐)을 지킨다.
- **버린 안**: codes.yaml을 JSON Schema로 바꾸기(깨는 변경), 손으로 enum 쓰기(헌법 I 위반).

## R3. 역할·범위 표기

- **결정**: 보안 방식 3개 — `bearerJwt`(http bearer, JWT), `refreshCookie`(apiKey, cookie `trace_refresh`), 인증 없음(`security: []`). 경로마다 확장 필드:
  ```yaml
  x-trace-access:
    roles: [ADMIN, CUSTOMER]
    scope: OWN_RENTAL   # NONE | OWN_RENTAL | CHECKPOINT | BOOTH
    captureToken: false # 촬영 JWT(CUSTOMER + checkpointId)로 부를 수 있는지
  ```
- **이유**: OpenAPI의 OAuth scope는 "본인 렌탈만", "그 시점만" 같은 값 기반 조건을 표현하지 못한다. 확장 필드는 gateway 테스트 목록 생성에 그대로 쓸 수 있고 redocly가 허용한다. JWT 클레임은 설계서대로 `role`, `scope`(checkpointId 또는 boothId), `rentals`.
- **버린 안**: OAuth2 scopes 문자열(조건 표현 불가), description에만 쓰기(기계가 못 읽음).

## R4. 오류 code

- **결정**: codes.yaml `error_code`에 UPPER_SNAKE 값 목록, 생성본 `ErrorCode` enum, `Problem.code`가 참조. 응답마다 `x-trace-error-codes: [..]`로 그 응답이 낼 수 있는 값을 적고 예시를 하나 둔다.
- **이유**: 화면이 `code`로 문장을 고른다(WE1 409 수용 기준). 상태 코드만으로는 409 "진행 중 렌탈"과 409 "기기가 ACTIVE 아님"을 구분 못 한다.

## R5. 목록

- **결정**: 쿼리 `limit`(1~100, 기본 20), `cursor`(불투명 문자열) → `{ items, nextCursor }`(마지막 쪽이면 `nextCursor: null`). `GET /devices`도 같음(사용자 결정).

## R6. SSE 진행률

- **결정**: `text/event-stream`, 이벤트 이름 `progress`(`{checkpointId, stage, percent, at}`), `done`(`{checkpointId, grade}`), `error`(Problem). stage는 `UPLOADED → ALIGNED → INSPECTED → GRADED → SEALED`. 스키마는 `components`에 두고 description에 형식을 적는다.
- **이유**: OpenAPI 3.1은 SSE 이벤트 스키마 표준이 없어서 응답 스키마를 문자열로 두고 이벤트 데이터 스키마를 따로 정의해 참조한다.
- **열린 점**: stage 값은 codes.yaml에 없다. 화면 표시용이라 C 리뷰에서 확인하고, 필요하면 codes.yaml에 더한다.

## R7. 진단 업로드 본문

- **결정**: `POST /diagnostics/runs`의 본문은 `$ref: '../diagnostics/diagnostic-run.v1.schema.json'`(C2가 만들 파일). C2 전까지 lint가 깨지지 않도록 C1에서는 `type: object` + description으로 두고, C2 PR에서 `$ref`로 바꾼다(더하는 변경).

## R8. 버전

- **결정**: 서버 파일 `info.version: 0.1.0`, codes.yaml `0.3.0`. 11/3 머지 시점이 고정본.

## R9. 검사

- **결정**: `redocly.yaml`에 `extends: [recommended]`, 운영상 필요 없는 규칙(`info-license`)만 끔. `operation-4xx-response`, `no-unused-components` 유지. 경로 대조 스크립트는 docs가 contracts CI에 없어서 로컬·PR 본문용으로 둔다.
