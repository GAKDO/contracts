# 조사: C2

- **redocly 예시 검사와 if/then**: `no-invalid-media-type-examples`가 기본값(allowAdditionalProperties false)에서 if/then 안의 부분 스키마에도 `unevaluatedProperties: false`를 붙여 정상 예시를 실패로 본다. 결정: 규칙 옵션 `allowAdditionalProperties: true`. 근거: 스키마의 `additionalProperties: false`는 그대로 검사되어 `hostName` 같은 키를 여전히 잡는다(직접 확인).
- **check-jsonschema와 상대 `$ref`**: `$id`를 두지 않으면 `../schemas/codes.gen.schema.json`을 파일 기준으로 읽는다. `$id`를 URL로 두면 원격을 받으러 가므로 두지 않는다.
- **이름 충돌**: 스키마 안 `DateTime`이 common.yaml의 `DateTime`과 번들에서 겹쳐 `DiagDateTime`으로 이름을 바꿨다.
- **사이클 0**: osquery 사례처럼 사이클 0은 '모름'이라 null(초안 원칙 2).
