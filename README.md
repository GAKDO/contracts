# contracts

TRACE 레포들이 함께 지키는 **계약의 원본**입니다. 서버·화면·에이전트·부스는 여기 정의를 따르고, 바꿀 때는 이 레포 PR을 먼저 머지합니다.

| 폴더·파일 | 내용 | 상태 |
|---|---|---|
| `codes.yaml` | 면·조명·흠집 클래스·등급·시점·기기 상태 등 코드 값(DB CHECK 제약과 같음) | 초안 |
| `openapi/` | 서버별 OpenAPI 3.1 | 11/3까지 |
| `diagnostics/` | 진단 결과 JSON Schema와 예시 | 11/3까지 |
| `events/` | RabbitMQ 이벤트 스키마 | 11/3까지 |
| `capture/faces.md` | 면별 표준 좌표 방향·배율(펼친 이미지, 3D 텍스처, 촬영 가이드 기준) | 11/2 확정 |
| `diagnostics/influx.md` | 파일럿 추이 InfluxDB `trace-pilot` 이름 | 11/2 확정 |

- 담당: A (B·C 리뷰)
- 설계: [GAKDO/docs](https://github.com/GAKDO/docs)
- CI: `계약 검사`(YAML·JSON Schema·OpenAPI 린트), `비밀값 검사`, `release`, 알림
