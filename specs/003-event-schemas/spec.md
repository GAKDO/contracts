# 기능 명세: C3 이벤트 스키마 5종

**Feature Branch**: `claude/project-thread-q6o6zf` (Spec Kit 기본값은 `feature/003-event-schemas`, 이 세션의 지정 브랜치를 씀)

**Created**: 2026-11-02

**Status**: Converged

**Backlog**: C3 (담당 A, 마감 11/3 계약 고정) · 요구사항 FR-CAP-05, FR-INS-01~04, FR-INT-01

**Input**: "RabbitMQ trace.events로 오가는 이벤트 5종의 JSON Schema(events/*.schema.json)를 만든다. 원본은 GAKDO/docs design/mvp-design.md의 "이벤트 계약" 표다. 모든 이벤트는 schemaVersion, eventId(UUIDv7, 11/2 NanoID 21자로 바뀜), occurredAt, rentalId, checkpointId 봉투를 가진다. 수용 기준: 이벤트마다 예시 1개가 스키마를 통과하고, 라우팅 키가 설계서 표와 같다."

## Clarifications

### Session 2026-11-02

사용자 지시("묻지 말고 진행, 정할 것만 모아 보고")에 따라 아래는 추천안으로 정하고 PR·보고에 적었다.

- Q: `schemaVersion` 형식은? → A: 문자열 `<주>.<부>`, 지금은 `1.0`. 필드 추가는 부 버전, 깨지는 변경은 주 버전 + 새 라우팅 키
- Q: 모르는 필드를 허용할까? → A: 스키마는 닫고(`unevaluatedProperties: false`) 소비자는 모르는 필드를 무시(너그러운 소비자)
- Q: JSON Schema가 codes.yaml을 어떻게 참조하나? → A: `scripts/gen_schema_codes.py`가 `schemas/codes.gen.schema.json`($defs)을 만들고 CI가 `--check`. C2(진단 JSON)도 같은 파일을 쓴다
- Q: 설계서 "핵심 필드"에 없는 필드가 필요하면? → A: 소비자가 REST 없이 일할 수 있게 더하고 events/README.md "설계서 표보다 더한 필드"에 적는다(사진 해시를 report-server에 넘기는 `trace.checkpoint.graded.photos` 등)

## 사용자 시나리오와 테스트 *(필수)*

"사용자"는 이벤트를 발행·소비하는 코드를 만드는 팀원과 그들의 Claude 세션이다.

### 사용자 이야기 1 - 발행하는 쪽이 스키마대로 이벤트를 만든다 (P1)

capture-server(CA1·CA2), inspect-worker(ML2), diagnostics-server(DI1), report-server(RP1)를 만들 때 라우팅 키 하나당 스키마 파일 하나를 보고 본문을 만든다.

**독립 테스트**: 스키마 파일만 보고 예시와 같은 본문을 만들 수 있고, 그 본문이 스키마를 통과한다.

**수용 시나리오**:

1. **Given** 이벤트 5종, **When** `examples/events/<키>.json`을 스키마로 검증하면, **Then** 모두 통과한다.
2. **Given** 봉투 필드가 빠졌거나 eventId가 NanoID 21자가 아니거나 occurredAt에 오프셋이 없는 본문, **When** 검증하면, **Then** 실패한다.
3. **Given** codes.yaml에 없는 코드 값(면·등급·흠집 클래스·플래그·시점), **When** 검증하면, **Then** 실패한다.

### 사용자 이야기 2 - 라우팅 키와 큐가 설계서와 같다 (P1)

RabbitMQ 선언(exchange·queue·binding)을 만들 때 스키마의 `x-routing-key`·`x-publisher`·`x-consumers`를 그대로 쓴다.

**수용 시나리오**:

1. **Given** 설계서 "이벤트 계약" 표, **When** 스키마 파일 이름과 `x-routing-key`·발행자·소비 큐를 대조하면, **Then** 5개가 모두 같다.

### 사용자 이야기 3 - 해시 체인 재료가 이벤트로 모인다 (P2)

report-server(RP1)가 사진·진단 해시를 REST 없이 이벤트로만 받아 체인을 만든다(FR-INT-01).

**수용 시나리오**:

1. **Given** `trace.checkpoint.graded`와 `trace.diagnostics.recorded`, **When** report-server가 받으면, **Then** 사진 SHA-256 목록과 진단 SHA-256이 모두 있다.
2. **Given** `trace.record.sealed`, **When** seq가 1이면 prevHash는 null, 2 이상이면 SHA-256이어야 하고, 어기면 검증이 실패한다.

### Edge Cases

- 출고(OUT)는 이전 시점이 없다: `newDefectIds`는 빈 배열, `baseRunId`는 null.
- 부스 세트는 Jetson이 탐지를 REST로 올렸으므로 `needDetection: false`, `trace.inspect.completed.defects`는 빈 배열.
- 정합에 실패한 사진은 `failedPhotos[]{photoId, reason}`로, 잴 수 없는 값은 null로 남긴다(헌법 III).
- 같은 이벤트가 두 번 와도 결과가 같다: `eventId`와 worker가 만든 `defectId`로 거른다.

## 요구사항 *(필수)*

- **FR-001**: 이벤트 5종마다 `events/<라우팅 키>.schema.json`(JSON Schema 2020-12)이 있다.
- **FR-002**: 모든 이벤트는 `events/envelope.schema.json#/$defs/Envelope`(schemaVersion·eventId·occurredAt·rentalId·checkpointId, 모두 필수)를 포함한다.
- **FR-003**: 코드 값은 `schemas/codes.gen.schema.json`을 `$ref`로 참조하고 값을 복사하지 않는다. 생성본은 CI에서 codes.yaml과 대조한다.
- **FR-004**: 이벤트마다 `examples/events/<키>.json` 예시 1개가 있고 스키마를 통과한다.
- **FR-005**: 스키마의 `x-routing-key`·`x-publisher`·`x-consumers`가 설계서 표와 같고, CI가 대조한다.
- **FR-006**: 스키마는 모르는 필드를 막고, 버전·호환 규칙은 events/README.md에 적는다.

## 성공 기준 *(필수)*

- **SC-001**: `python3 scripts/check_events.py`가 이벤트 5종 예시 통과와 위반 사례 57건(예시 5건과 합쳐 62건) 거부를 확인한다.
- **SC-002**: CI '계약 검사'(yamllint·메타스키마·생성본 일치·이벤트 계약·OpenAPI 린트)가 초록이다.
- **SC-003**: CA1·ML2·DI1·RP1 명세가 이벤트 필드를 설계서가 아니라 이 스키마에서 인용할 수 있다.

## 가정

- 설계서 표의 "web(SSE)"는 RabbitMQ 큐가 아니라 report-server가 SSE로 전달하는 것이라 대조 대상 큐에서 뺀다. 검색 색인은 선택이라 큐를 정하지 않는다.
- 3DGS 실험 이벤트(`trace.recon.*`)는 이 기능 범위가 아니다.
