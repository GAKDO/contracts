# 구현 계획: C3 이벤트 스키마 5종

**Branch**: `claude/project-thread-q6o6zf` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## 요약

설계서 "이벤트 계약" 표의 5종을 JSON Schema 2020-12 파일로 고정하고, 봉투는 공통 파일 하나에서 `allOf`로 포함한다. 코드 값은 codes.yaml에서 생성한 `$defs`를 참조한다. 예시와 위반 사례를 CI에서 검증한다.

## 기술 맥락

- 형식: JSON Schema 2020-12(`events/`, `schemas/`), 예시 JSON(`examples/events/`)
- 도구: Python 3.12, pyyaml, jsonschema(referencing), check-jsonschema, yamllint
- `$id`: `https://raw.githubusercontent.com/GAKDO/contracts/main/<경로>`. 상대 `$ref`(`envelope.schema.json#/...`, `../schemas/codes.gen.schema.json#/...`)가 같은 기준으로 풀린다. 검사 스크립트는 내려받지 않고 레포 파일로 레지스트리를 만든다.
- 확장 키워드: `x-routing-key`, `x-publisher`, `x-consumers[]{service, queue}` (2020-12는 모르는 키워드를 주석으로 둔다)

## 헌법 점검

| 원칙 | 점검 | 결과 |
| --- | --- | --- |
| I 계약이 먼저 | 코드 값을 복사하지 않고 생성본 `$ref`, 11/3 전 고정 | 통과 |
| II 서비스 경계 | 이벤트 5종만, 소비자가 REST 없이 일하도록 필요한 필드 포함 | 통과 |
| III 기록은 고칠 수 없다 | 사진·진단 SHA-256, null + 사유, 모델·규칙 버전 | 통과 |
| IV 품질 게이트 | 수용 기준마다 check_events.py 검사, CI 단계 | 통과 |
| V 비밀 | 예시에 비밀값 없음, check-no-secrets 통과 | 통과 |
| VI 단순 | 5종만, recon 제외 | 통과 |

## 구조

```text
events/envelope.schema.json            # $defs: Envelope, SchemaVersion, Uuid, DateTime, Sha256, ObjectKey, ModelVersion
events/trace.<도메인>.<동작>.schema.json  # 5개
examples/events/trace.*.json           # 5개
schemas/codes.gen.schema.json          # 생성본 (scripts/gen_schema_codes.py)
scripts/gen_schema_codes.py            # gen_openapi_codes.build_schemas 재사용
scripts/check_events.py                # 표 대조·예시·위반 사례
```
