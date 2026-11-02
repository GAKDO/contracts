# 이벤트

RabbitMQ topic exchange `trace.events`로 오가는 이벤트 6종의 JSON Schema(2020-12)를 둔다. 원본 표는 GAKDO/docs `design/mvp-design.md`의 "이벤트 계약"이다.

| 라우팅 키 | 스키마 | 발행 | 소비 (큐) | 예시 |
| --- | --- | --- | --- | --- |
| `trace.capture.uploaded` | [trace.capture.uploaded.schema.json](trace.capture.uploaded.schema.json) | capture-server | inspect-worker (`trace.inspect.requested`) | [예시](../examples/events/trace.capture.uploaded.json) |
| `trace.inspect.completed` | [trace.inspect.completed.schema.json](trace.inspect.completed.schema.json) | inspect-worker | capture-server (`trace.capture.inspected`) | [예시](../examples/events/trace.inspect.completed.json) |
| `trace.checkpoint.graded` | [trace.checkpoint.graded.schema.json](trace.checkpoint.graded.schema.json) | capture-server | report-server (`trace.report.updates`) | [예시](../examples/events/trace.checkpoint.graded.json) |
| `trace.diagnostics.recorded` | [trace.diagnostics.recorded.schema.json](trace.diagnostics.recorded.schema.json) | diagnostics-server | report-server (`trace.report.updates`) | [예시](../examples/events/trace.diagnostics.recorded.json) |
| `trace.checkpoint.started` | [trace.checkpoint.started.schema.json](trace.checkpoint.started.schema.json) | rental-server | report-server (`trace.report.updates`) | [예시](../examples/events/trace.checkpoint.started.json) |
| `trace.record.sealed` | [trace.record.sealed.schema.json](trace.record.sealed.schema.json) | report-server | auth-server 영수증 메일 (`trace.auth.receipts`), web(SSE, report-server가 전달), 검색 색인(선택) | [예시](../examples/events/trace.record.sealed.json) |

## 공통 규칙

- **봉투:** 모든 이벤트에 `schemaVersion`, `eventId`(NanoID 21자), `occurredAt`(ISO 8601 + 오프셋), `rentalId`, `checkpointId`가 있다. 정의는 [envelope.schema.json](envelope.schema.json)의 `$defs/Envelope`이고, 이벤트 스키마는 `allOf`로 포함한다. 모든 `*Id`는 `$defs/PublicId`(NanoID 21자, `^[A-Za-z0-9_-]{21}$`)이고 DB 기본 키(bigint)는 싣지 않는다.
- **버전:** `schemaVersion`은 `<주>.<부>` 문자열이고 지금은 `1.0`이다. 필드를 더하면 부 버전을 올린다(`1.1`). 필드 삭제·이름 변경 같은 깨지는 변경은 하지 않고, 꼭 필요하면 주 버전과 새 라우팅 키로 낸다.
- **닫힌 스키마, 너그러운 소비자:** 스키마는 모르는 필드를 막는다(`unevaluatedProperties: false`). 발행하는 쪽이 오타를 내지 않게 하려는 것이다. 소비하는 쪽은 모르는 필드를 무시해(Jackson `FAIL_ON_UNKNOWN_PROPERTIES=false`, Python은 필요한 키만 읽기) 부 버전이 올라도 깨지지 않게 한다.
- **코드 값:** 면·조명·카메라·등급·시점·흠집 클래스·플래그 종류는 `codes.yaml`을 복사하지 않고 [../schemas/codes.gen.schema.json](../schemas/codes.gen.schema.json)의 `$defs`를 `$ref`로 쓴다. 그 파일은 `python3 scripts/gen_schema_codes.py`로 만든다.
- **읽지 못한 값:** 0이 아니라 `null`(예: `errorPx`, `lengthMm`)이고, 사진 단위 실패는 `failedPhotos`에 사유를 남긴다.
- **멱등:** 같은 `eventId`가 두 번 와도 결과가 같아야 한다. `trace.inspect.completed`의 `defectId`는 worker가 만들어, 다시 와도 같은 흠집을 두 번 저장하지 않게 한다.
- **전달:** 큐는 durable, 메시지는 persistent, `content-type: application/json`, AMQP `message_id`는 `eventId`와 같게 둔다. 처리가 끝난 뒤 ack하고 계속 실패하면 `trace.dlx`로 보낸다.

## 설계서 표보다 더한 필드

설계서 "핵심 필드" 칸에 없지만 소비하는 쪽이 REST 없이 일하려면 필요한 필드를 더했다(서비스끼리는 이벤트로만 주고받는다).

- `trace.capture.uploaded`: `photos[].camera`(부스 카메라 2대가 같은 면·조명을 찍음), `skippedFaces`(건너뛴 선택 면과 사유)
- `trace.inspect.completed`: `alignments[].method`·`rectifiedKey`, `defects[].defectId`·`lengthMm`·`areaMm2`, `failedPhotos`
- `trace.checkpoint.graded`: `captureSetId`, `checkpointType`, `photos[]{photoId, sha256}`(report-server가 해시 체인에 넣을 사진 해시)
- `trace.diagnostics.recorded`: `baseRunId`(비교 기준, 첫 진단은 null)

## 1.1에서 더한 것 (11/2 민서 결정, 선택 필드라 1.0 소비자는 그대로 동작)

- `trace.checkpoint.graded.pins[]`{defectId, face, x, y, isNew}: 리포트 3D 핀(표준 좌표 px 중심)
- `trace.diagnostics.recorded.maxCapacityPct`: 리포트 배터리 최대 용량(%)
- 새 이벤트 `trace.checkpoint.started`(rental-server → report-server): 시점 시작 때 기종 코드·이름·시리얼. 리포트·검증 화면의 기종 이름

## 검사

```sh
python3 scripts/gen_schema_codes.py --check   # 코드 값 생성본이 codes.yaml과 같은지
python3 scripts/check_events.py               # 라우팅 키 = 설계서 표, 예시 통과, 위반 사례 거부
```
