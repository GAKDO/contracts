# 데이터 모델: 진단 결과 JSON v1

| 필드 | 필수 | 형식 | DDL |
| --- | --- | --- | --- |
| schemaVersion | 예 | `diag.v1` | 원본 JSON |
| agentVersion | 예 | 문자열 ≤32 | diagnostic_run.agent_version |
| collectedAt·consentedAt | 예 | ISO 8601 + 오프셋 | diagnostic_run.consented_at |
| os | 예 | type(DeviceOs)·version·arch | diagnostic_run.os |
| device | 예 | serial(≤64)·manufacturer·model·modelName(null 가능) | diagnostic_run.device_serial |
| conditions | 예 | acPower·batteryPercent·thermalState·processCount·uptimeSec (뒤 4개 null 가능) | diagnostic_run.conditions |
| components[] | 예(1~32) | kind·identifier·detail(스칼라 값만) | hardware_component |
| battery | 예 | status·skippedReason·cycleCount·designCapacity·fullChargeCapacity·osMaxCapacityPercent·osCondition | battery_reading |
| storage | 예 | status·skippedReason·protocol·percentageUsed·availableSpare·criticalWarning·mediaErrors·powerOnHours | ssd_health |
| benchmarks[] | 예(0~5) | metric·unit·trials(3)·median | benchmark_result |
| benchmarkSkippedReason | 예 | SkippedReason 또는 null | 원본 JSON |
| sources[] | 예(1~32) | 문자열 | 원본 JSON |

## 상태별 규칙

| 대상 | status | skippedReason | 값 |
| --- | --- | --- | --- |
| battery | OK | null | 두 용량은 `{value, unit}` 필수, 나머지 null 가능 |
| battery | SKIPPED | NO_PERMISSION·UNSUPPORTED·TOOL_ERROR | 모두 null |
| battery | NO_BATTERY | null | 모두 null |
| storage | OK | null | protocol 필수, 나머지 null 가능 |
| storage | SKIPPED | NO_PERMISSION·UNSUPPORTED·TOOL_ERROR | 모두 null |
| benchmarks | 비어 있음 | benchmarkSkippedReason 필수 | 전원 없음이면 NO_AC_POWER |

## codes.yaml 0.4.0에 더한 값 (diagnostics)

battery_status, storage_status, skipped_reason, storage_protocol, battery_condition, thermal_state
