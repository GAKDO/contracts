---
description: "C3 이벤트 스키마 5종 작업 목록"
---

# Tasks: C3 이벤트 스키마 5종

**Tests**: 계약 검사 — `gen_schema_codes.py --check`, `check_events.py`(표 대조·예시 통과·위반 사례 거부), check-jsonschema 메타스키마, yamllint.

## Phase 1: Setup

- [x] T001 `scripts/gen_schema_codes.py`: codes.yaml → `schemas/codes.gen.schema.json`($defs, gen_openapi_codes와 같은 이름), `--check`
- [x] T002 생성본 `schemas/codes.gen.schema.json` 만들기

## Phase 2: Foundational

- [x] T003 `events/envelope.schema.json`: Envelope와 공통 형식(PublicId·DateTime·Sha256·ObjectKey·ModelVersion·SchemaVersion)

## Phase 3: US1 발행하는 쪽이 스키마대로 만든다 (P1)

- [x] T004 [P] `events/trace.capture.uploaded.schema.json` + 예시
- [x] T005 [P] `events/trace.inspect.completed.schema.json` + 예시
- [x] T006 [P] `events/trace.checkpoint.graded.schema.json` + 예시
- [x] T007 [P] `events/trace.diagnostics.recorded.schema.json` + 예시
- [x] T008 [P] `events/trace.record.sealed.schema.json` + 예시(seq·prevHash 조건)

## Phase 4: US2 라우팅 키가 설계서와 같다 (P1)

- [x] T009 `scripts/check_events.py`: 설계서 표 상수와 파일 이름·x-routing-key·x-publisher·소비 큐 대조, 봉투 포함 확인
- [x] T010 `events/README.md` 표와 공통 규칙(버전·닫힌 스키마·멱등·전달), 더한 필드 목록

## Phase 5: US3 해시 체인 재료 (P2)

- [x] T011 check_events.py 위반 사례: 봉투 누락·eventId 형식(UUID·20자·허용 밖 글자·정수)·오프셋 없음·주 버전 2·모르는 필드·코드 값 밖·seq/prevHash 조건

## Phase 6: Polish

- [x] T012 CI '계약 검사'에 생성본 일치(JSON Schema)·이벤트 계약 단계 추가, `jsonschema` 설치
- [x] T013 CHANGELOG [Unreleased] 한 줄

## Analyze / Converge (2026-11-02)

- 명세 FR-001~006 ↔ 작업: 모두 대응(FR-001 T004~T008, FR-002 T003·T009, FR-003 T001·T002·T012, FR-004 T004~T008, FR-005 T009·T012, FR-006 T010·T011)
- 로컬 검사: `check_events.py` 이벤트 5종·62건 통과, 메타스키마 ok, yamllint 오류 0, 생성본 최신, 비밀값 없음 → Converged
