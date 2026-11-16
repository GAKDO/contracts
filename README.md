# contracts

TRACE 레포들이 함께 지키는 **계약의 원본**입니다. 서버·화면·에이전트·부스·챗봇은 여기 정의를 따르고, 바꿀 때는 이 레포 PR을 먼저 머지합니다.

11/3에 1.0.0으로 고정했고, 그 뒤로는 **깨지지 않는 변경만** 더합니다(선택 필드·새 경로·코드 값 추가. 이름 변경·삭제 없음). 바뀐 것은 [CHANGELOG.md](CHANGELOG.md)의 `[Unreleased]`에 날짜와 요청한 사람을 적습니다.

| 폴더·파일 | 내용 |
|---|---|
| [`codes.yaml`](codes.yaml) | 면·조명·흠집 클래스·등급·시점·기기 상태·검수 상태·소셜 제공자·점검 플래그·오류 코드 등 코드 값(DB CHECK 제약과 같음). 1.0.0 |
| [`openapi/`](openapi/README.md) | 서버별 OpenAPI 3.1: auth-server · rental-server · capture-server · diagnostics-server · report-server · chat-server(11/10 추가). 공통 컴포넌트와 codes.yaml에서 만든 `components/codes.gen.yaml` |
| [`diagnostics/`](diagnostics/README.md) | 진단 결과 JSON Schema `diag.v1`(`result.schema.json`). 잠금·디스크 상태 `checks`(11/7), 보안 보호·위협 건수(11/12) |
| [`events/`](events/README.md) | RabbitMQ `trace.events` 이벤트 7종 JSON Schema(`trace.checkpoint.graded` 1.3에 사람 검수 `review`) |
| `examples/` | 진단 JSON(맞는 예·틀린 예)과 이벤트 예시. CI가 스키마로 검사 |
| [`capture/faces.md`](capture/faces.md) | 면별 표준 좌표 방향·배율(펼친 이미지, 3D 텍스처, 촬영 가이드 기준) |
| `diagnostics/influx.md` | 파일럿 추이 InfluxDB 이름(11/2). **11/6 결정으로 InfluxDB는 쓰지 않고**, 추이는 web이 저장된 진단을 모아 그림 |

11/3 이후 더한 주요 계약: 부스 빠른 검사 세트(`profile: QUICK`)·일회용 부스 6자리 코드, 공개 보유 기기 목록(catalog), AI 후보 사람 검수와 놓친 흠집 직접 추가, 반납 정산, 소셜 로그인(구글·깃허브·카카오·네이버)과 비밀번호 없는 탈퇴, 사이트 도우미 챗봇, 진단 잠금·보안 상태 점검, 수령·반납 검사 방식 고정, 봉인 전 진단 다시 하기.

API 문서(Redoc): https://gakdo.github.io/docs/api/mvp.html

- 담당: A (B·C 리뷰)
- 설계: [GAKDO/docs](https://github.com/GAKDO/docs) `design/mvp-design.md`(요구사항·이벤트 계약), `design/rest-api-v0.md`(역할 × 경로 표)
- 코드 값을 쓰는 쪽은 `codes.yaml`을 복사하지 않고 생성 파일(`openapi/components/codes.gen.yaml`, `schemas/codes.gen.schema.json`)을 참조합니다. codes.yaml을 고치면 `python3 scripts/gen_openapi_codes.py`와 `python3 scripts/gen_schema_codes.py`로 다시 만들어 함께 커밋합니다(CI가 일치 검사)

## CI

| 워크플로 | 하는 일 |
|---|---|
| `계약 검사` | yamllint, 코드 값 생성본 일치, JSON Schema 메타스키마, 이벤트 계약(라우팅 키·예시·위반 사례), 진단 JSON 예시, redocly lint |
| `비밀값 검사`·`release`·알림 | 다른 레포와 같음 |
