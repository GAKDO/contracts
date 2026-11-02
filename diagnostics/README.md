# 진단 결과 JSON

진단 에이전트(B)가 사용자 동의 뒤 `POST /api/v1/diagnostics/runs`로 올리고 diagnostics-server(A)가 검증·저장하는 본문의 계약이다 (C2, FR-DIA-01~05).

- 스키마: `result.schema.json` (JSON Schema draft 2020-12, `schemaVersion: diag.v1`)
- 코드 값: `codes.yaml`의 `device.os`·`diagnostics.*`를 `schemas/codes.gen.schema.json`(생성본)으로 참조한다. 값을 복사하지 않는다.
- 예시: `examples/diagnostics/valid/`(macOS·Windows·SSD 생략, 통과해야 함), `examples/diagnostics/invalid/`(실패해야 함)
- 검사: `scripts/check_diagnostics_examples.sh` (CI '계약 검사'와 같음)
- OpenAPI: `openapi/diagnostics-server.yaml`의 `DiagnosticUpload`가 이 스키마를 `$ref`로 쓴다.
- 원본 초안: GAKDO/docs `design/diagnostics-json-v0.md`

## 규칙 요약

| 규칙 | 스키마에서 |
| --- | --- |
| 정해진 필드 밖의 키는 거부(컴퓨터 이름·사용자 이름이 섞여 들어오지 않게) | 모든 객체 `additionalProperties: false`, 부품 `detail`은 host·computer·user·owner·account·email·uuid가 든 키 거부 |
| 배터리 용량은 값과 단위, 환산하지 않음 | `{value, unit}`(mAh·mWh), 값 0 금지 |
| 읽지 못한 값은 null + 생략 사유 | 배터리·SSD `status: SKIPPED`면 `skippedReason` 필수, 값은 모두 null. 키는 늘 모두 보낸다 |
| 벤치마크는 3회 + 중앙값 + 측정 조건 | `trials` 정확히 3개, `conditions` 필수. 전원이 없으면 `benchmarks: []` + `benchmarkSkippedReason: NO_AC_POWER` |
| 시점은 본문에 없음 | checkpointId 필드 없음(AGENT 토큰에서) |

스키마로 표현하지 않고 서버(DI1)가 확인하는 것: 두 용량의 단위가 같은지, `median`이 `trials`의 가운데 값인지, 지표가 겹치지 않는지, `device.serial`이 렌탈 기기와 같은지(AGENT JWT의 `deviceSerial` 클레임 = 페어링 코드를 만들 때 정한 등록 시리얼과 비교).
