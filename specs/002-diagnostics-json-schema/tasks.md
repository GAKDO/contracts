# Tasks: C2 진단 결과 JSON Schema v1

**Tests**: 계약 검사(메타스키마, 예시 통과·실패, redocly lint, 코드 생성본 일치).

## Phase 1: Foundational
- [x] T001 codes.yaml 0.4.0: diagnostics에 battery_status·storage_status·skipped_reason·storage_protocol·battery_condition·thermal_state, 생성본 다시 만들기
- [x] T002 `schemas/codes.gen.schema.json` 참조 확인(C3 생성 스크립트)

## Phase 2: US1·US2 스키마와 예시
- [x] T003 [US1] `diagnostics/result.schema.json` 작성(필드·조건·개인정보 차단)
- [x] T004 [P] [US1] 통과 예시 3개 `examples/diagnostics/valid/`
- [x] T005 [P] [US2] 실패 예시 4개 `examples/diagnostics/invalid/`
- [x] T006 [US2] `scripts/check_diagnostics_examples.sh`와 CI 단계 "진단 JSON 예시 (C2)"

## Phase 3: US3 OpenAPI
- [x] T007 [US3] `DiagnosticUpload`를 `$ref`로, 업로드 예시를 macOS 예시로, info.version 0.2.0
- [x] T008 [US3] redocly 예시 검사 옵션(research.md), lint 경고 0 확인

## Phase 4: 마무리
- [x] T009 diagnostics/README.md, CHANGELOG [Unreleased]
- [x] T010 analyze·converge: 명세 수용 기준 ↔ 예시 파일 대조 (checklists/requirements.md)
