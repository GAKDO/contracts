# OpenAPI

서버별 OpenAPI 3.1 계약(11/3 고정). 원본 표는 GAKDO/docs `design/rest-api-v0.md`, 명세는 `specs/001-openapi-contracts/`.

| 파일 | 서버 | 경로 |
| --- | --- | --- |
| `auth-server.yaml` | auth-server | 17 (ping, JWKS 포함) |
| `rental-server.yaml` | rental-server | 13 |
| `capture-server.yaml` | capture-server | 7 |
| `diagnostics-server.yaml` | diagnostics-server | 3 |
| `report-server.yaml` | report-server | 6 |
| `chat-server.yaml` | chat-server | 2 (11/10 추가, 사이트 도우미 챗봇) |
| `components/common.yaml` | 공통 | Problem(+code), PublicId·DateTime·Sha256, 커서 목록 파라미터, 공통 오류 응답, 인증 방식 |
| `components/codes.gen.yaml` | 생성 | codes.yaml의 enum. **손으로 고치지 않는다** |

## 규칙

- JSON 필드 camelCase, ID는 `PublicId`(NanoID 21자, `^[A-Za-z0-9_-]{21}$`). DB 기본 키(bigint)는 내보내지 않는다(헌법 1.1.0, docs decisions.md 11/2). 시각은 ISO 8601 + 오프셋. 오류는 모두 `application/problem+json`이고 `code`(codes.yaml `error_code`)를 가진다.
- 목록은 `limit`·`cursor` → `{ items, nextCursor }`(마지막이면 `nextCursor: null`).
- 코드 값은 `codes.gen.yaml`만 참조한다. codes.yaml을 고치면 `python3 scripts/gen_openapi_codes.py`로 다시 만들어 함께 커밋한다(CI가 일치 검사).
- 11/3 고정 뒤에는 더하는 변경만 한다(필드·값·경로 삭제나 이름 변경 금지).

## 확장 필드

| 필드 | 위치 | 뜻 |
| --- | --- | --- |
| `x-trace-access` | operation | `roles`(JWT role, codes.yaml `auth.token_role`), `scope`(`NONE`·`OWN_RENTAL`·`CHECKPOINT`·`BOOTH`), `captureToken`(고객 촬영 JWT 허용). 인증 없는 경로는 `security: []`이고 이 필드가 없다 |
| `x-trace-error-codes` | 오류 response | 그 응답이 낼 수 있는 `code` 값 |
| `x-trace-requirements` | operation | 요구사항 ID |
| `x-trace-sse-events` | SSE operation | 이벤트 이름 → 데이터 스키마 |
| `x-trace-internal` | operation | gateway 밖으로 열지 않는 내부 경로 |

scope 뜻: `OWN_RENTAL`은 CUSTOMER가 `rentals` 클레임의 렌탈만(ADMIN은 제한 없음), `CHECKPOINT`는 토큰 `scope`의 시점만, `BOOTH`는 토큰 `scope`의 부스만. 범위 밖은 403 `OUT_OF_SCOPE`.

## 검사

```bash
yamllint -d "{extends: relaxed, rules: {line-length: {max: 160}}}" .
python3 scripts/gen_openapi_codes.py --check
npx -y @redocly/cli@2 lint openapi/*-server.yaml
python3 scripts/check_openapi_coverage.py ../docs/design/rest-api-v0.md --access   # 46/46, 역할 표기 0건
```

## 쓰는 법

- web: `npx openapi-typescript openapi/rental-server.yaml -o src/shared/api/rental.ts`, MSW 목은 각 응답의 `example(s)`.
- 서버: DTO 이름은 스키마 이름(`RentalCreateRequest` 등), 오류는 ProblemDetail에 `code` 속성.
- gateway: `x-trace-access`로 역할 × 경로 테스트 목록을 만든다.
