# 빠른 시작: C1 계약 검사·사용

## 검사 (CI '계약 검사'와 같음)

```bash
yamllint -d "{extends: relaxed, rules: {line-length: {max: 160}}}" .
python3 scripts/gen_openapi_codes.py --check          # codes.yaml ↔ openapi/components/codes.gen.yaml
npx -y @redocly/cli@2 lint openapi/*-server.yaml
python3 scripts/check_openapi_coverage.py ../docs/design/rest-api-v0.md   # 46/46
```

codes.yaml을 고치면 `python3 scripts/gen_openapi_codes.py`로 생성본을 다시 만들어 같이 커밋한다.

## 보기

```bash
npx -y @redocly/cli@2 preview-docs openapi/rental-server.yaml
```

## 소비

- web(C): `npx openapi-typescript openapi/rental-server.yaml -o src/shared/api/rental.ts`, MSW 핸들러는 각 응답의 `examples`를 쓴다. 오류 문장은 `Problem.code`로 고른다.
- 서버(A): 경로·DTO 이름은 스키마 이름(`RentalCreateRequest` 등)을 따른다. 오류는 `ProblemDetail`에 `code` 속성을 넣는다.
- gateway(A): `x-trace-access`를 읽어 역할 × 경로 통합 테스트를 만든다.
- agent·booth(B): #14·#16·#32~#34·#39의 요청·응답과 `Idempotency-Key`.
