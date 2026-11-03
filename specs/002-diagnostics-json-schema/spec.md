# 기능 명세: C2 진단 결과 JSON Schema v1

**Feature Branch**: `claude/project-thread-h201ph` (Spec Kit 기본값은 `feature/002-diagnostics-json-schema`, 이 세션의 지정 브랜치를 씀)

**Created**: 2026-11-02

**Status**: Converged

**Backlog**: C2 (담당 A, 리뷰 B, 마감 11/3 계약 고정)

**Input**: "진단 에이전트가 서버로 보내는 결과를 JSON Schema(diagnostics/result.schema.json)로 고정한다. 원본은 GAKDO/docs design/diagnostics-json-v0.md다. 배터리 용량은 값과 단위(mAh 또는 mWh)를 함께 보내고, 읽지 못한 항목은 null과 생략 사유를 보낸다. 벤치마크는 3회 중앙값과 측정 조건, 전원 연결 여부를 보낸다. 컴퓨터 이름·사용자 이름은 없다. 수용 기준: macOS 예시, Windows 예시, SSD 생략 예시 3개가 스키마를 통과하고, 잘못된 예시 2개가 실패한다(check-jsonschema)."

## Clarifications

### Session 2026-11-02

사용자 지시("묻지 말고 진행, 정할 것만 알려 달라")에 따라 추천안으로 정하고 PR·보고에 적었다.

- Q: 파일 이름은 backlog의 `result.schema.json`과 diagnostics/README의 `diag.v0.schema.json` 중 무엇? → A: backlog대로 `diagnostics/result.schema.json`
- Q: `schemaVersion` 값은? → A: `diag.v1` (v0은 초안, 11/3 고정본이 v1). C1 예시의 `'1'`은 이 값으로 바꾼다
- Q: SSD·배터리를 생략할 때 키를 빼나, null로 두나? → A: 키는 늘 모두 보내고 값은 null + `skippedReason` (헌법 III, 받는 쪽 형태가 하나)
- Q: 벤치마크를 돌리지 못하면? → A: `benchmarks: []` + `benchmarkSkippedReason`(전원 없음은 `NO_AC_POWER`)
- Q: macOS 배터리 판정 원문("Good")을 그대로 보내나? → A: `NORMAL`·`SERVICE_RECOMMENDED` 두 값으로 바꿔 보낸다(Good·Normal → NORMAL, 그 밖 → SERVICE_RECOMMENDED). 원문은 보내지 않는다

## 사용자 시나리오와 테스트 *(필수)*

### 사용자 이야기 1 - 에이전트 담당이 스키마대로 결과를 만든다 (P1)

B가 AG1(macOS)·AG2(Windows) 에이전트를 만들 때 스키마 파일 하나와 예시만 보고 보낼 JSON을 만든다. 보내기 전에 같은 스키마로 스스로 검사한다.

**독립 테스트**: macOS·Windows·SSD 생략 예시가 `check-jsonschema`를 통과한다.

**수용 시나리오**:

1. **Given** macOS 예시, **When** 스키마로 검사하면, **Then** 통과한다.
2. **Given** Windows 예시(용량 mWh, 사이클·OS 판정·발열 상태 null), **When** 검사하면, **Then** 통과한다.
3. **Given** SSD를 권한 없이 생략한 예시, **When** 검사하면, **Then** 통과하고 `storage.skippedReason`이 `NO_PERMISSION`이다.

### 사용자 이야기 2 - 서버가 잘못된 결과를 거부한다 (P1)

A가 DI1에서 같은 스키마로 업로드를 검증하고 어긋나면 422 `DIAGNOSTIC_SCHEMA_INVALID`를 돌려준다.

**수용 시나리오**:

1. **Given** 컴퓨터 이름(`device.computerName`)이 든 결과, **When** 검사하면, **Then** 실패한다.
2. **Given** 단위 없이 숫자만 있는 배터리 용량, **When** 검사하면, **Then** 실패한다.
3. **Given** SSD를 생략했는데 사유가 null인 결과, **When** 검사하면, **Then** 실패한다.
4. **Given** 전원이 연결되지 않았는데 벤치마크가 있는 결과, **When** 검사하면, **Then** 실패한다.

### 사용자 이야기 3 - OpenAPI가 같은 스키마를 가리킨다 (P2)

C1 `diagnostics-server.yaml`의 업로드 본문 `DiagnosticUpload`가 이 스키마를 `$ref`로 써서 형식이 한 곳에만 있다.

**수용 시나리오**:

1. **Given** OpenAPI 파일, **When** redocly lint를 돌리면, **Then** 오류·경고 없이 통과하고 업로드 예시가 스키마와 맞는다.

### Edge Cases

- 사이클을 OS가 0으로 주면 '모름'이므로 null로 보낸다(0 금지).
- 배터리 없는 기기는 `status: NO_BATTERY`, 값과 사유 모두 null.
- 부품 `detail`에 host·computer·user·owner·account·email·uuid가 든 키는 거부한다.
- 두 용량 단위가 같은지, `median`이 가운데 값인지, 지표 중복은 스키마로 막지 않고 서버(DI1)가 확인한다.

## 요구사항 *(필수)*

- **FR-001**: 진단 결과는 `diagnostics/result.schema.json`(draft 2020-12) 하나로 정의한다. (FR-DIA-01~05)
- **FR-002**: 배터리 용량은 `{value, unit}`, unit은 codes.yaml `diagnostics.capacity_unit`. 값 0은 금지, 모르면 null. (FR-DIA-02)
- **FR-003**: 배터리·SSD는 `status`와 `skippedReason`을 가진다. 생략이면 사유가 있고 값은 모두 null. (FR-DIA-03, 헌법 III)
- **FR-004**: 벤치마크는 지표마다 `trials` 3개와 `median`, 측정 조건 `conditions`(전원·잔량·발열·프로세스 수·가동 시간)를 함께 보낸다. 전원이 없으면 벤치마크는 비고 사유는 `NO_AC_POWER`. (FR-DIA-04)
- **FR-005**: 동의 시각 `consentedAt`이 필수다. (FR-DIA-05)
- **FR-006**: 정해진 필드 밖의 키는 거부한다. 컴퓨터 이름·사용자 이름 필드는 없다. (헌법 V, NFR-02)
- **FR-007**: 시점 ID는 본문에 없다(AGENT 토큰에서).
- **FR-008**: 코드 값은 codes.yaml에서 생성한 `schemas/codes.gen.schema.json`을 `$ref`로 쓰고 복사하지 않는다. 새 값은 codes.yaml 0.4.0에 더한다. (헌법 I)
- **FR-009**: `openapi/diagnostics-server.yaml`의 `DiagnosticUpload`는 이 스키마의 `$ref`다.

## 성공 기준 *(필수)*

- **SC-001**: 통과 예시 3개(macOS·Windows·SSD 생략)가 통과하고, 잘못된 예시 4개가 모두 실패한다(`scripts/check_diagnostics_examples.sh`, CI '계약 검사').
- **SC-002**: 메타스키마 검사와 redocly lint가 오류·경고 0으로 통과한다.
