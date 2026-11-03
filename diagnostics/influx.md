# InfluxDB `trace-pilot` 쓰기 규칙

파일럿 추이 대시보드(FR-PIL-02)용 시계열입니다. diagnostics-server(DI2)가 진단 실행을 저장할 때 쓰고, 학교 Grafana가 읽습니다.
원본은 PostgreSQL `diagnostics`이고, 여기는 대시보드용 사본입니다. (11/2 결정: C 제안 `web/specs/003-pilot-trend-dashboard/data-model.md`를 확정, `alias` 태그는 뺌)

- 버킷: `trace-pilot` (공유 인프라, `trace` 접두사)
- 시각(`_time`): 진단 JSON의 측정 시각
- codes.yaml 값은 번역하지 않고 그대로 태그 값으로 쓴다.
- 서비스끼리 REST를 부르지 않으므로 파일럿 별칭(P01 등)은 쓰지 않는다. 대시보드에서 별칭이 필요하면 Grafana 값 매핑(deviceId → 별칭)으로 보여 준다.

## measurement `trace_battery` (진단 실행마다 1점)

| 종류 | 이름 | 값 | 출처(진단 JSON) |
|---|---|---|---|
| tag | `deviceId` | 기기 publicId | 렌탈 기기 |
| tag | `checkpoint` | 시점 종류(codes.yaml `rental.checkpoint_type`) | 토큰의 시점 |
| field | `healthPercent` (float) | fullChargeCapacity ÷ designCapacity × 100 | battery. 둘 중 하나라도 null이면 쓰지 않음 |
| field | `cycleCount` (int) | 충전 사이클 | battery.cycleCount, null이면 쓰지 않음 |
| field | `osMaxCapacityPercent` (int) | OS 최대 용량 % | battery.osMaxCapacityPercent(macOS), null이면 쓰지 않음 |

## measurement `trace_benchmark` (지표마다 1점)

| 종류 | 이름 | 값 |
|---|---|---|
| tag | `deviceId`, `checkpoint` | 위와 같음 |
| tag | `metric` | codes.yaml `diagnostics.benchmark_metric` |
| tag | `unit` | benchmarks[].unit |
| field | `median` (float) | benchmarks[].median |

필드가 하나도 없는 점(예: 배터리 값이 모두 null)은 쓰지 않는다.
