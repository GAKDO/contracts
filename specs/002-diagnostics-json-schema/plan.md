# 구현 계획: C2 진단 결과 JSON Schema v1

**Branch**: `claude/project-thread-h201ph` | **Date**: 2026-11-02 | **Spec**: [spec.md](spec.md)

## 요약

design/diagnostics-json-v0.md 초안을 JSON Schema 2020-12 파일 하나로 옮기고, 예시 7개(통과 3·실패 4)와 검사 스크립트를 CI에 넣는다. 새 코드 값은 codes.yaml 0.4.0에 더하고, C1 OpenAPI의 업로드 본문을 이 스키마의 `$ref`로 바꾼다.

## 기술 맥락

JSON Schema 2020-12, 검사는 CI '계약 검사'와 같은 yamllint·check-jsonschema·redocly lint. 코드 값은 C3가 만든 `scripts/gen_schema_codes.py` → `schemas/codes.gen.schema.json`(`$defs`, 이름은 gen_openapi_codes.py와 같은 PascalCase)을 참조한다.

## 헌법 점검

| 원칙 | 결과 |
| --- | --- |
| I 계약이 먼저 | 코드 값은 codes.yaml에만 더하고 생성본을 `$ref`. 11/3 전이라 C1 업로드 본문 교체 가능(필드 형태가 바뀌지만 아직 쓰는 코드 없음) |
| III 고칠 수 없는 기록 | 읽지 못한 값 null + 사유를 스키마 조건(if/then)으로 강제 |
| IV 테스트 | 수용 기준마다 예시 파일, CI 단계 추가 |
| V 개인정보 | `additionalProperties: false`, detail 키 이름 차단 |
| VI 단순 | 스키마 1개, 스크립트 1개(셸) |

## 구조

```
diagnostics/result.schema.json, diagnostics/README.md
examples/diagnostics/valid/{macos,windows,ssd-skipped}.json
examples/diagnostics/invalid/{computer-name,capacity-without-unit,skipped-without-reason,benchmark-without-ac-power}.json
scripts/check_diagnostics_examples.sh
codes.yaml(0.4.0), openapi/components/codes.gen.yaml, schemas/codes.gen.schema.json(생성)
openapi/diagnostics-server.yaml(DiagnosticUpload $ref, 0.2.0), redocly.yaml
.github/workflows/contracts-ci.yml
```
