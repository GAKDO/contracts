# 기능 명세: C1 OpenAPI 5개 (서버별 REST 계약 고정)

**Feature Branch**: `claude/project-thread-1s3ob8` (Spec Kit 기본값은 `feature/001-openapi-contracts`, 이 세션의 지정 브랜치를 씀)

**Created**: 2026-11-02

**Status**: Draft

**Backlog**: C1 (담당 A, 리뷰 B·C, 마감 11/3 계약 고정)

**Input**: "auth, rental, capture, diagnostics, report 서버의 REST API를 OpenAPI 3.1 파일 5개(openapi/<서버>.yaml)로 고정한다. 원본은 GAKDO/docs design/rest-api-v0.md의 경로·역할 표와 요청·응답 예시다. 모든 오류는 RFC 9457 Problem Details, JSON 필드는 camelCase, ID는 UUIDv7, 시각은 ISO 8601 + 오프셋이다. 각 경로에 필요한 역할(ADMIN, CUSTOMER, BOOTH, AGENT)과 범위를 적고, /api/v1/<경로>/ping은 인증 없음으로 둔다. 코드 값은 codes.yaml을 참조한다. 수용 기준: redocly lint가 통과하고, rest-api-v0.md의 모든 경로가 빠짐없이 있으며, 화면(C)·에이전트(B) 담당이 리뷰에서 승인한다."

## Clarifications

### Session 2026-11-02

- Q: `GET /devices` 목록은 표의 페이지 번호(`page=`)를 유지할까요, 공통 커서 규칙으로 맞출까요? → A: 커서로 통일
- Q: 오류 `code` 값 목록은 어디에 고정할까요? → A: codes.yaml에 `error_code` 목록으로 고정

## 사용자 시나리오와 테스트 *(필수)*

이 기능의 "사용자"는 계약을 읽고 코드를 만드는 팀원(서버 A, 화면 C, 에이전트·부스 B)과 그들의 Claude 세션이다.

### 사용자 이야기 1 - 서버 담당이 계약대로 API를 만든다 (우선순위: P1)

A가 auth·rental·capture·diagnostics·report 서버를 만들 때, 서버마다 하나의 계약 파일만 보고 경로·역할·요청·응답·오류를 그대로 구현한다. 설계 문서의 표를 다시 해석하지 않는다.

**이 우선순위인 이유**: AU1·RE1·CA1·DI1·RP1이 모두 C1에 의존하고, 11/3 계약 고정 전에는 서버 구현을 시작하지 않기로 했다.

**독립 테스트**: 서버 파일 하나만 열어 rest-api-v0.md의 해당 서버 표와 한 줄씩 대조했을 때 빠진 경로·역할·주요 응답이 없다.

**수용 시나리오**:

1. **Given** rest-api-v0.md의 서버별 표, **When** 5개 파일의 경로를 모두 모으면, **Then** 표의 경로 41개와 ping 5개가 하나도 빠지지 않고 메서드까지 같다.
2. **Given** 표의 "주요 응답" 칸, **When** 해당 경로의 응답 목록을 보면, **Then** 표에 적힌 상태 코드가 모두 있고 2xx가 아닌 응답은 Problem Details 형식이다.
3. **Given** 계약 파일, **When** 계약 검사(redocly lint)를 돌리면, **Then** 오류 없이 통과한다.

---

### 사용자 이야기 2 - 화면 담당이 계약에서 타입과 목을 만든다 (우선순위: P1)

C가 WE1~WE4 화면을 만들 때 계약 파일에서 API 타입을 자동으로 만들고, 같은 파일의 예시로 API 목을 만들어 서버 없이 화면을 만든다. 오류 응답의 `code`로 사람이 읽는 문장을 고른다(예: 수리 중 기기로 렌탈을 만들면 409).

**이 우선순위인 이유**: WE1(11/6)이 C1 초안과 목으로 오늘부터 명세·계획을 시작한다.

**독립 테스트**: 화면별 API 표(rest-api-v0.md "화면별로 부르는 API")의 모든 호출에 대해 요청·응답 본문의 필드와 형식, 예시가 계약에 있다.

**수용 시나리오**:

1. **Given** 화면별 API 표, **When** C가 각 호출을 계약에서 찾으면, **Then** 요청 본문·응답 본문의 필드 이름·형식·필수 여부와 예시가 모두 있다.
2. **Given** 오류 응답, **When** C가 409·403·410 같은 응답을 보면, **Then** 그 응답이 낼 수 있는 `code` 값이 적혀 있어 화면 문장을 미리 정할 수 있다.
3. **Given** C의 리뷰, **When** PR에서 승인하면, **Then** C1 수용 기준의 화면 쪽이 충족된다.

---

### 사용자 이야기 3 - 에이전트·부스 담당이 자기 호출을 확인한다 (우선순위: P2)

B가 진단 에이전트(AG1·AG2)와 부스(BO1·BO2)를 만들 때 페어링 교환, 진단 업로드, 부스 토큰, 촬영 세트 생성·완료, 탐지 결과 올리기의 계약을 확인한다. 특히 중복 요청 키와 토큰 범위를 계약에서 읽는다.

**이 우선순위인 이유**: AG1이 11/9, BO2가 11/6이라 C1보다 늦게 시작하지만 계약 고정 뒤에는 깨는 변경을 할 수 없다.

**독립 테스트**: B가 쓰는 6개 경로(#14·#16·#32·#33·#34·#39)에서 인증 방법, 범위(boothId·checkpointId), `Idempotency-Key`, 오류 응답을 계약만 보고 설명할 수 있다.

**수용 시나리오**:

1. **Given** 진단 업로드 경로, **When** B가 계약을 보면, **Then** AGENT 역할·`checkpointId` 범위·`Idempotency-Key` 헤더·201/409/422 응답이 적혀 있다.
2. **Given** B의 리뷰, **When** PR에서 승인하면, **Then** C1 수용 기준의 에이전트 쪽이 충족된다.

---

### 사용자 이야기 4 - gateway가 역할 × 경로 표를 계약에서 읽는다 (우선순위: P2)

A가 gateway(GW1)의 역할 검사와 통합 테스트를 만들 때, 경로마다 필요한 역할과 범위를 계약에서 읽는다.

**이 우선순위인 이유**: FR-AUTH-03의 수용 기준(역할 × 경로 표)이 이 정보로 테스트된다.

**독립 테스트**: rest-api-v0.md "역할 × 경로 표"의 모든 칸이 계약 파일의 경로별 역할 표기로 재현된다.

**수용 시나리오**:

1. **Given** 경로 하나, **When** 계약을 보면, **Then** 허용 역할(PUBLIC·ADMIN·CUSTOMER·촬영·BOOTH·AGENT)과 범위 조건(본인, 그 시점만, 자기 부스)이 기계가 읽을 수 있는 형태로 적혀 있다.
2. **Given** `/api/v1/<경로>/ping`, **When** 계약을 보면, **Then** 인증 없음으로 적혀 있다.

### 엣지 케이스

- 경로 앞부분이 여러 개인 서버(rental: `/rentals`·`/devices`·`/device-models`·`/pilot`, report: `/reports`·`/verify`)는 한 파일에 모두 담는다. ping은 서버마다 하나(`/api/v1/auth/ping`, `/rentals/ping`, `/captures/ping`, `/diagnostics/ping`, `/reports/ping`)다.
- gateway를 거치지 않는 내부 경로(`/.well-known/jwks.json`)도 auth 파일에 넣되 내부용으로 표시한다.
- 쿠키로만 인증하는 경로(`/auth/refresh`)와 클라이언트 비밀로 받는 경로(`/auth/booth/token`)는 Bearer와 다른 인증 방법으로 적는다.
- SSE 경로(`/reports/rentals/{rentalId}/stream`)는 JSON이 아닌 `text/event-stream`이고, 이벤트 형식을 적는다.
- "선택"으로 표시된 경로(`/reports/search`)도 계약에는 넣는다(수용 기준이 "빠짐없이"이므로).
- 항상 202를 돌려주는 경로(`/auth/password/reset-request`)는 계정 존재 여부를 응답으로 드러내지 않는다.
- 검증 응답(`/verify/{verifyToken}`)에는 사진·진단 상세와 개인정보 필드가 없다.

## 요구사항 *(필수)*

### 기능 요구사항

- **FR-001**: 계약은 서버마다 한 파일, 모두 5개다: auth-server, rental-server, capture-server, diagnostics-server, report-server.
- **FR-002**: rest-api-v0.md의 서버별 표에 있는 모든 경로(41개)와 서버별 ping(5개)을 메서드·경로 그대로 담는다.
- **FR-003**: 경로마다 표의 "하는 일", "요구사항" ID, 필요한 역할과 범위 조건을 적는다.
- **FR-004**: 경로마다 표의 "주요 응답"에 있는 상태 코드를 모두 적고, 인증이 필요한 경로에는 401·403을 더한다.
- **FR-005**: 2xx가 아닌 모든 응답은 RFC 9457 Problem Details 형식(`application/problem+json`)이고 `code` 필드를 가진다.
- **FR-006**: 요청·응답 본문의 모든 필드는 camelCase이고, ID는 UUIDv7 형식, 시각은 ISO 8601 + 오프셋 형식으로 적는다.
- **FR-007**: 면·조명·카메라·시점·상태·등급 같은 코드 값은 codes.yaml 0.2.0의 값만 쓰고, 값 목록을 손으로 다르게 쓰지 않는다.
- **FR-008**: 모든 목록 응답은 공통 규칙(`limit`, `cursor` → `items`, `nextCursor`)을 따른다. `GET /devices`도 표의 `page=` 대신 커서를 쓴다(원본과 다른 점으로 PR 본문에 적는다).
- **FR-009**: 촬영 완료와 진단 업로드는 `Idempotency-Key` 요청 헤더를 필수로 적는다.
- **FR-010**: 가입·로그인·코드 확인·페어링 교환에는 429(분당 10회 초과) 응답을 적는다.
- **FR-011**: rest-api-v0.md의 요청·응답 예시(촬영 세트 만들기, 검증, 오류 예시)를 계약의 예시로 그대로 옮기고, 화면별 API 표의 호출마다 성공 예시를 하나 이상 둔다.
- **FR-012**: 오류 `code` 값은 codes.yaml에 `error_code` 목록(UPPER_SNAKE, 예: `RENTAL_OPEN_EXISTS`)으로 고정하고, 계약은 그 목록을 참조한다. 응답마다 그 응답이 낼 수 있는 `code` 값을 적는다. 함께 JWT `role` 클레임 값 `auth.token_role`(ADMIN·CUSTOMER·BOOTH·AGENT), 체인 상태 `report.chain_status`, 진행 단계 `report.progress_stage`도 codes.yaml에 더한다. 값 추가이므로 부 버전(0.3.0)을 올린다.
- **FR-013**: 계약 파일은 계약 검사(yamllint·redocly lint)를 통과한다.
- **FR-014**: 계약에 비밀번호·토큰·키 같은 비밀 값이나 실제 개인정보 예시를 넣지 않는다(예시 값은 지어낸 값).

### 핵심 데이터

- **계약 파일(서버별)**: 서버 이름, 버전, 경로 목록, 공통 형식(Problem Details, 목록, 오류 code).
- **경로**: 메서드, 경로, 역할·범위, 요청(헤더·본문), 응답(상태 코드별 본문), 요구사항 ID.
- **공통 형식**: Problem Details(+code), 커서 목록, UUIDv7 ID, 오프셋 시각, codes.yaml 값.

## 성공 기준 *(필수)*

### 측정 가능한 결과

- **SC-001**: rest-api-v0.md의 경로 41개 + ping 5개가 계약에 100% 있다(대조표로 확인).
- **SC-002**: 계약 검사가 5개 파일 모두 오류 0건으로 통과한다.
- **SC-003**: 화면별 API 표의 호출 100%에 요청·응답 필드와 예시가 있어, C가 서버 없이 목을 만들 수 있다.
- **SC-004**: C와 B가 PR에서 각각 승인한다(11/3 안).
- **SC-005**: 역할 × 경로 표의 모든 칸(15행 × 6열)이 계약의 역할 표기와 일치한다.

## 가정

- 원본은 GAKDO/docs `design/rest-api-v0.md`(경로·역할·응답)이고, 표에 없는 필드 이름·형식은 `design/ddl.md`의 테이블과 `design/mvp-design.md`에서 가져온다. 원본과 다르게 정한 것은 PR 본문에 적어 리뷰받는다.
- 진단 업로드 본문의 상세 형식은 C2(진단 결과 JSON Schema)가 정하고, C1은 그 스키마를 참조하는 자리만 둔다. 이벤트 형식은 C3의 범위라 넣지 않는다.
- 파일 이름은 contracts `openapi/README.md`대로 `<서버>-server.yaml`이다.
- 계약 버전은 0.1.0으로 시작하고, 11/3 고정 뒤에는 더하는 변경만 한다.
- MinIO 업로드(PUT)와 gateway 자체 경로는 이 계약의 범위가 아니다.
