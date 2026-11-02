# 변경 기록

이 레포의 버전별 변경을 적는다. 형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/)를 따른다.
기능 PR은 `## [Unreleased]` 아래에 한 줄을 더하고, 릴리스 PR에서 `## [x.y.z] - 날짜`로 바꾼다(CONTRIBUTING.md 3번).
main에 버전이 적힌 CHANGELOG가 올라가면 release.yml이 태그와 GitHub Release를 만든다.

## [Unreleased]

### 변경
- ID 형식 `Uuid`(UUIDv7) → `PublicId`(NanoID 21자, `^[A-Za-z0-9_-]{21}$`): OpenAPI 5개·이벤트 봉투(eventId 포함 모든 `*Id`)·예시. DB 기본 키(bigint)는 내보내지 않음 (헌법 1.1.0, docs decisions.md 11/2, **깨지는 변경**)
- codes.yaml 0.5.0: 폰 필수 면 `face_required.PHONE` = TOP·BOT·SF·SB·SL·SR·SCR0 (KB 제외, SCR1 선택, 11/2 확정)
- codes.yaml 조명 값 `OFF`를 따옴표로 감쌈. YAML 1.1 파서(PyYAML·SnakeYAML)가 불리언 false로 읽던 문제 (값은 그대로)
- codes.yaml 0.3.0: 면 코드 설명과 출처별 필수 면 `face_required`를 더함. 부스는 8면(SCR1은 선택, 건너뛰면 사유), 폰은 WE2에서 정함 (11/2)
- 조명 코드에 L4(앞 스침광, 키보드 촬영) 추가, 부스 카메라 코드 CAM을 CAM1(앞 반)·CAM2(뒤 반)로 나눔 (11/1 부스 설계)

### 추가
- 이벤트 봉투 rentalId 경로: `POST /captures/sets` 요청과 페어링 코드 발급 요청에 `rentalId`(필수), AGENT 토큰 응답·JWT에 `rentalId` (C1·C3 보강, 11/3 고정 전)
- 이벤트 스키마 5종(`events/trace.*.schema.json`)과 봉투 `events/envelope.schema.json`, 예시 `examples/events/`, codes.yaml → JSON Schema `$defs` 생성본 `schemas/codes.gen.schema.json`과 이벤트 계약 검사 스크립트 (C3)
- 진단 결과 JSON Schema v1 `diagnostics/result.schema.json`(`diag.v1`), 예시 7개와 예시 검사, codes.yaml 0.4.0 진단 값 6종, diagnostics-server 업로드 본문을 이 스키마 `$ref`로 (C2)
- 서버별 OpenAPI 3.1 계약 5개(auth·rental·capture·diagnostics·report, 경로 46개)와 공통 형식 `openapi/components/common.yaml` (C1)
- codes.yaml 0.3.0: `error_code`(오류 code 34개), `auth.token_role`, `report.chain_status`, `report.progress_stage` (C1)
- codes.yaml → OpenAPI enum 생성 스크립트와 CI 일치 검사, rest-api-v0 경로 대조 스크립트 (C1)
- 블로그(AIGJ-01-002-blog/devlog) CI/CD를 옮겨 초기 구성
