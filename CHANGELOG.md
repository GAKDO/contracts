# 변경 기록

이 레포의 버전별 변경을 적는다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따른다.
기능 PR은 `## [Unreleased]` 아래에 한 줄을 더하고, 릴리스 PR에서 `## [x.y.z] - 날짜`로 바꾼다(CONTRIBUTING.md 3번).
main에 버전이 적힌 CHANGELOG가 올라가면 release.yml이 태그와 GitHub Release를 만든다.

## [Unreleased]

### 변경
- 페어링 코드 발급 요청에 `deviceSerial`(필수, 등록 시리얼) 추가, AGENT JWT 클레임과 토큰 응답에 `deviceSerial`. diagnostics-server는 진단 `device.serial`을 이 클레임과 대조 (auth-server 0.2.0, 11/2 민서 결정, **깨지는 변경**: 웹 페어링 화면이 시리얼을 보내야 함)
- `BatterySummary`에 `skippedReason`(DiagnosticsSkippedReason 또는 null, 필수) 추가 (diagnostics-server 0.3.0, 11/2 민서 결정)
- 이벤트 `trace.inspect.completed`의 흠집 `polygon` 단위 설명을 mm → 표준 좌표 px(1 px = 0.25 mm)로 고침. REST·DB·capture/faces.md와 맞춤, 값 형식은 그대로 (11/2 C 지적)
- 부스 탐지 저장: 같은 세트에 다시 보내면 그 세트의 부스 탐지를 통째로 바꿈(중복 없음, Idempotency-Key 없음) (11/2 B 질문)
- 세트 생성 `photos` 최대 54 → 80 (카메라 2대를 셈하지 않던 설명을 고침, 부스 실제 29장) (11/2 C 지적)
- 이벤트 `trace.capture.uploaded`·`trace.checkpoint.graded`의 `photos` 최대 54 → 80. 세트 생성 최대와 맞춤(80장 세트가 이벤트 검증에서 떨어지던 틈, 11/2 민서 결정)
- 세트 생성 설명의 URL 다시 받기 경로에 `/api/v1`을 붙임 (문구만, 11/2 C 지적)
- 부스 탐지 `Detection`: `camera`(필수) 추가, `polygon`은 원본 사진 px(`PhotoPolygon`). 표준 좌표 변환은 inspect-worker의 alignments로 capture-server가 (11/2 결정, **깨지는 변경**)
- 기기 수정: 폐기(RETIRED) 기기는 수리 중으로만 되돌림. RETIRED → ACTIVE는 409 `DEVICE_STATUS_TRANSITION_INVALID` (codes.yaml 0.6.0, 11/2 결정)
- 촬영 세트 생성 설명: 같은 세트에서 겹치지 않는 키를 (face, light) → (face, light, camera)로 (문구만, DB·서버는 이미 카메라까지)
- 이벤트 `trace.capture.uploaded`의 `photos[].objectKey` 설명: 버킷 trace-raw → trace-captures와 키 형식 (문구만, 스키마 값 그대로. CA1 구현과 맞춤)
- ID 형식 `Uuid`(UUIDv7) → `PublicId`(NanoID 21자, `^[A-Za-z0-9_-]{21}$`): OpenAPI 5개·이벤트 봉투(eventId 포함 모든 `*Id`)·예시. DB 기본 키(bigint)는 내보내지 않음 (헌법 1.1.0, docs decisions.md 11/2, **깨지는 변경**)
- codes.yaml 0.5.0: 폰 필수 면 `face_required.PHONE` = TOP·BOT·SF·SB·SL·SR·SCR0 (KB 제외, SCR1 선택, 11/2 확정)
- codes.yaml 조명 값 `OFF`를 따옴표로 감쌈. YAML 1.1 파서(PyYAML·SnakeYAML)가 불리언 false로 읽던 문제 (값은 그대로)
- codes.yaml 0.3.0: 면 코드 설명과 출처별 필수 면 `face_required`를 더함. 부스는 8면(SCR1은 선택, 건너뛰면 사유), 폰은 WE2에서 정함 (11/2)
- 조명 코드에 L4(앞 스침광, 키보드 촬영) 추가, 부스 카메라 코드 CAM을 CAM1(앞 반)·CAM2(뒤 반)로 나눔 (11/1 부스 설계)

### 추가
- 이벤트 1.1(선택 필드, 깨지지 않음): `trace.checkpoint.graded.pins`(흠집 핀 face·x·y·isNew), `trace.diagnostics.recorded.maxCapacityPct`, 새 이벤트 `trace.checkpoint.started`(rental-server, 기종 코드·이름·시리얼). 리포트의 핀·기종·배터리 칸을 채우려고 (11/2 민서 결정, RP1 후속)
- report-server 관리자 수동 봉인(시연 우회로) `POST /api/v1/reports/rentals/{rentalId}/checkpoints/{checkpointId}/seal`과 사용 기록 `GET /api/v1/reports/manual-seals`, codes.yaml 0.7.0 `RECORD_ALREADY_SEALED` (11/2 결정, RP1)
- `POST /captures/sets/{setId}/uploads`: 아직 안 올라간 사진의 업로드 URL 다시 받기 (11/2 결정)
- `capture/faces.md`: 면별 표준 좌표 방향·배율(1 px = 0.25 mm) (11/2 결정)
- `diagnostics/influx.md`: InfluxDB `trace-pilot` measurement·태그·필드 이름 (11/2 결정)
- 이벤트 봉투 rentalId 경로: `POST /captures/sets` 요청과 페어링 코드 발급 요청에 `rentalId`(필수), AGENT 토큰 응답·JWT에 `rentalId` (C1·C3 보강, 11/3 고정 전)
- 이벤트 스키마 5종(`events/trace.*.schema.json`)과 봉투 `events/envelope.schema.json`, 예시 `examples/events/`, codes.yaml → JSON Schema `$defs` 생성본 `schemas/codes.gen.schema.json`과 이벤트 계약 검사 스크립트 (C3)
- 진단 결과 JSON Schema v1 `diagnostics/result.schema.json`(`diag.v1`), 예시 7개와 예시 검사, codes.yaml 0.4.0 진단 값 6종, diagnostics-server 업로드 본문을 이 스키마 `$ref`로 (C2)
- 서버별 OpenAPI 3.1 계약 5개(auth·rental·capture·diagnostics·report, 경로 46개)와 공통 형식 `openapi/components/common.yaml` (C1)
- codes.yaml 0.3.0: `error_code`(오류 code 34개), `auth.token_role`, `report.chain_status`, `report.progress_stage` (C1)
- codes.yaml → OpenAPI enum 생성 스크립트와 CI 일치 검사, rest-api-v0 경로 대조 스크립트 (C1)
- 블로그(AIGJ-01-002-blog/devlog) CI/CD를 옮겨 초기 구성
