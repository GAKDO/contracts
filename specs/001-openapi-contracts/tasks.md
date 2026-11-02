---
description: "C1 OpenAPI 5개 작업 목록"
---

# Tasks: C1 OpenAPI 5개

**Input**: `specs/001-openapi-contracts/` (plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md)

**Tests**: 이 기능의 "테스트"는 계약 검사다 — yamllint, redocly lint, 코드 값 생성본 일치(`gen_openapi_codes.py --check`), 경로 대조(`check_openapi_coverage.py`). 실행 코드 테스트는 없다.

**Organization**: 사용자 이야기별. US1·US2는 같은 파일을 고치므로 서버 파일 단위로 차례로 하고, 서버 파일끼리는 [P]로 나란히 할 수 있다.

## Format: `[ID] [P?] [Story] 설명`

---

## Phase 1: Setup

- [x] T001 `redocly.yaml`(레포 루트) 추가: `extends: [recommended]`, `info-license` 끔, 확장 필드 `x-trace-*` 허용
- [x] T002 [P] `scripts/check_openapi_coverage.py` 작성: rest-api-v0.md의 서버별 표(메서드·경로)를 읽어 `openapi/*-server.yaml`의 operation과 대조, 빠진 것·남는 것·합계(46) 출력, 다르면 종료 코드 1. 예외: `/.well-known/jwks.json`은 `/api/v1` 없이 대조, 표의 쿼리(`?modelCode=…`)는 떼고 비교, ping 5개는 스크립트에 고정 목록

---

## Phase 2: Foundational (모든 이야기의 전제)

- [x] T003 `codes.yaml`에 `error_code`(data-model.md 표의 34개)와 `auth.token_role: [ADMIN, CUSTOMER, BOOTH, AGENT]`, `report.chain_status: [VALID, BROKEN, PENDING]`, `report.progress_stage: [UPLOADED, ALIGNED, INSPECTED, GRADED, SEALED]` 추가, `version: 0.3.0`, 머리 주석 갱신
- [x] T004 `scripts/gen_openapi_codes.py` 작성: codes.yaml의 각 목록 → `openapi/components/codes.gen.yaml`의 enum 스키마(PascalCase 이름: `DeviceStatus`, `CaptureFace`, `ErrorCode` 등), `--check`는 생성 결과와 파일이 다르면 종료 코드 1. 파일 머리에 "생성 파일, 손으로 고치지 않음"
- [x] T005 T004로 `openapi/components/codes.gen.yaml` 생성
- [x] T006 `openapi/components/common.yaml` 작성: `Uuid`·`DateTime`·`Sha256`·`Problem`(code 필수, `ErrorCode` 참조)·`FieldError`·`PingResponse`, 파라미터 `Limit`·`Cursor`·`IdempotencyKey`, 응답 `BadRequest`·`Unauthorized`·`Forbidden`·`NotFound`·`TooManyRequests`, 보안 방식 `bearerJwt`·`refreshCookie`
- [x] T007 `.github/workflows/contracts-ci.yml`에 "코드 값 생성본 일치" 단계 추가(`pip install pyyaml` + `python scripts/gen_openapi_codes.py --check`), OpenAPI 린트 대상을 `openapi/*-server.yaml`로(components는 참조로 함께 검사)

**Checkpoint**: 공통 파일이 lint를 통과(빈 서버 파일 하나로 확인)

---

## Phase 3: US1 서버 담당이 계약대로 API를 만든다 (P1) 🎯 MVP

**Goal**: 경로 46개의 메서드·경로·요청·응답 스키마·상태 코드가 서버 파일 5개에 있음

**Independent Test**: `check_openapi_coverage.py` 46/46, redocly lint 0 오류, path-inventory.md의 응답 열과 일치

- [x] T008 [P] [US1] `openapi/auth-server.yaml`: 경로 17개(#1~#17), data-model auth 스키마, 상태 코드(원본 + 추가), refresh는 `refreshCookie`, login·refresh 200에 `Set-Cookie` 헤더, jwks는 `servers` 별도(내부)
- [x] T009 [P] [US1] `openapi/rental-server.yaml`: 경로 13개(#18~#30), `GET /devices` 커서 파라미터(modelCode·status·q·limit·cursor), `DeviceUpdateRequest`는 `additionalProperties: false`
- [x] T010 [P] [US1] `openapi/capture-server.yaml`: 경로 7개(#31~#37), `CaptureSetCreateRequest`의 photos 1~54개, 업로드 URL 응답
- [x] T011 [P] [US1] `openapi/diagnostics-server.yaml`: 경로 3개(#38~#40), 업로드 본문은 C2 자리(object + description), 읽지 못한 값 nullable
- [x] T012 [P] [US1] `openapi/report-server.yaml`: 경로 6개(#41~#46), SSE `text/event-stream` + `ProgressEvent`·`DoneEvent` 스키마, `VerifyResponse`에 개인정보 필드 없음
- [x] T013 [US1] 검사: yamllint, redocly lint, `check_openapi_coverage.py ../docs/design/rest-api-v0.md` → 46/46

**Checkpoint**: 서버 담당이 구현을 시작할 수 있는 최소 계약

---

## Phase 4: US2 화면 담당이 타입과 목을 만든다 (P1)

**Goal**: 화면별 API 표의 모든 호출에 예시가 있고, 오류 응답마다 낼 수 있는 `code`가 적혀 있음

**Independent Test**: 화면별 API 표의 호출마다 요청·성공 응답 예시가 있고, 2xx가 아닌 응답마다 `x-trace-error-codes`와 Problem 예시가 있음. openapi-typescript가 5파일 모두 오류 없이 타입 생성

- [x] T014 [P] [US2] `openapi/auth-server.yaml`: 요청·성공 응답 `examples`, 오류 응답마다 `x-trace-error-codes` + Problem 예시
- [x] T015 [P] [US2] `openapi/rental-server.yaml`: 같은 작업. `POST /rentals` 409는 `RENTAL_OPEN_EXISTS`·`DEVICE_NOT_ACTIVE` 두 예시(rest-api-v0 오류 예시 그대로 포함)
- [x] T016 [P] [US2] `openapi/capture-server.yaml`: 같은 작업. 촬영 세트 요청·응답은 rest-api-v0 예시 그대로
- [x] T017 [P] [US2] `openapi/diagnostics-server.yaml`: 같은 작업
- [x] T018 [P] [US2] `openapi/report-server.yaml`: 같은 작업. 검증 응답은 rest-api-v0 예시 그대로, SSE 이벤트 예시는 description에
- [x] T019 [US2] 검사: `npx openapi-typescript openapi/<각 파일> -o /tmp/...` 5개 성공, 예시가 스키마에 맞는지 redocly lint(`no-invalid-media-type-examples`)

---

## Phase 5: US3 에이전트·부스 담당이 자기 호출을 확인한다 (P2)

**Goal**: B가 쓰는 경로 6개(#14·#16·#32·#33·#34·#39)의 인증·범위·중복 키·오류가 빠짐없음

**Independent Test**: 6개 경로 각각에서 인증 방법, scope, `Idempotency-Key`(#33·#39), 오류 code를 계약만 보고 설명 가능

- [x] T020 [US3] `openapi/capture-server.yaml`·`openapi/diagnostics-server.yaml`: #33·#39에 `IdempotencyKey` 파라미터(필수)와 422 `IDEMPOTENCY_KEY_CONFLICT`, 같은 키 재요청은 첫 응답을 돌려준다는 description
- [x] T021 [US3] `openapi/auth-server.yaml`: #14·#16 토큰 수명(1시간·10분)과 `scope` 클레임 내용을 description에, 429는 #16만
- [x] T022 [US3] B용 확인표를 PR 본문 초안에(경로·인증·scope·중복 키·오류 code)

---

## Phase 6: US4 gateway가 역할 × 경로 표를 계약에서 읽는다 (P2)

**Goal**: 모든 operation에 `security`와 `x-trace-access`(roles·scope·captureToken)

**Independent Test**: access-matrix.md의 15행이 각 operation의 `x-trace-access`로 재현되고, ping 5개는 `security: []`

- [x] T023 [P] [US4] `openapi/auth-server.yaml`: `security`·`x-trace-access` (공개 경로는 `security: []`)
- [x] T024 [P] [US4] `openapi/rental-server.yaml`: 같음
- [x] T025 [P] [US4] `openapi/capture-server.yaml`: 같음(촬영 JWT는 `captureToken: true`)
- [x] T026 [P] [US4] `openapi/diagnostics-server.yaml`: 같음
- [x] T027 [P] [US4] `openapi/report-server.yaml`: 같음(#43만 `captureToken: true`)
- [x] T028 [US4] `scripts/check_openapi_coverage.py`에 `--access` 옵션: 모든 operation에 `security`가 있고, 인증 경로는 `x-trace-access`가 있는지 확인

---

## Phase 7: Polish

- [x] T029 [P] `openapi/README.md` 갱신: 파일 목록, 공통 규칙, 생성 파일, 검사 명령, `x-trace-access`·`x-trace-error-codes` 뜻
- [x] T030 [P] `CHANGELOG.md`에 0.3.0(codes.yaml)·OpenAPI 0.1.0 항목
- [x] T031 quickstart.md의 검사 전부 실행, `scripts/check-no-secrets.sh` 통과
- [x] T032 PR 본문: 백로그 C1, 요구사항(FR 전체 API), 원본과 다른 점 4가지, 브랜치 이름 사유, B·C 확인표, 검사 결과. PR을 연 뒤 B·C에게 리뷰 요청(SC-004)

---

## Dependencies

- Setup(T001·T002) → Foundational(T003→T004→T005, T006, T007) → US1 → US2·US3·US4 → Polish
- US2·US3·US4는 US1 뒤라면 서로 독립. 같은 서버 파일을 고치므로 한 파일 안에서는 차례로 한다.
- T020은 T010·T011 뒤, T028은 T023~T027 뒤.

## 나란히 할 수 있는 것

```text
US1: T008 · T009 · T010 · T011 · T012 (서버 파일마다)
US2: T014 ~ T018
US4: T023 ~ T027
```

## 구현 전략

1. Setup + Foundational → US1(경로 46개) → T013 검사. 여기서 커밋하면 서버 담당은 시작 가능(MVP).
2. US2(예시·오류 code) → C에게 초안 공유.
3. US3·US4 → B 확인표, gateway 표기.
4. Polish → develop PR, B·C 리뷰 요청(11/3 안).
