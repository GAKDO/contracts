# 경로 대조표 (47개)

rest-api-v0.md 표 41개 + ping 5개. scope: NONE·OWN_RENTAL·CHECKPOINT·BOOTH. "촬영"은 CUSTOMER 역할의 촬영 JWT(`captureToken: true`). 추가 응답은 원본 표에 없고 이번에 더한 것.

| # | 파일 | 메서드 | 경로(/api/v1 뒤) | 역할 · scope | 원본 응답 | 추가 응답 | FR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | auth | GET | /auth/ping | 없음 | 200 |  | - |
| 2 | auth | POST | /auth/signup | PUBLIC | 201·400·409 | 429 | FR-USR-01·05 |
| 3 | auth | POST | /auth/email/verify | PUBLIC | 204·400·410 | 429 | FR-USR-05 |
| 4 | auth | POST | /auth/email/resend | PUBLIC | 202·429 |  | FR-USR-05 |
| 5 | auth | POST | /auth/login | PUBLIC | 200·401·403 | 400·429 | FR-AUTH-01 |
| 6 | auth | POST | /auth/refresh | 쿠키 | 200·401 |  | FR-AUTH-01 |
| 7 | auth | POST | /auth/logout | ADMIN·CUSTOMER | 204 | 401 | FR-AUTH-01 |
| 8 | auth | POST | /auth/password/reset-request | PUBLIC | 202 | 400 | FR-USR-06 |
| 9 | auth | POST | /auth/password/reset | PUBLIC | 204·400·410 |  | FR-USR-06 |
| 10 | auth | GET | /auth/me | ADMIN·CUSTOMER | 200 | 401 | FR-USR-03 |
| 11 | auth | DELETE | /auth/me | CUSTOMER | 204·401 | 403 | FR-USR-04 |
| 12 | auth | POST | /auth/capture-links | ADMIN | 201 | 400·401·403 | FR-RNT-04 |
| 13 | auth | POST | /auth/capture-links/exchange | CUSTOMER | 200·409·410 | 400·401·403 | FR-AUTH-02, FR-USR-02 |
| 14 | auth | POST | /auth/booth/token | PUBLIC(클라이언트 비밀) | 200·401 | 400 | FR-AUTH-02 |
| 15 | auth | POST | /auth/pairing-codes | ADMIN | 201 | 400·401·403 | FR-AUTH-02 |
| 16 | auth | POST | /auth/pairing-codes/exchange | PUBLIC | 200·400·410 | 429 | FR-AUTH-02 |
| 17 | auth | GET | /.well-known/jwks.json (내부, /api/v1 없음) | gateway 내부 | 200 |  | FR-AUTH-03 |
| 18 | rental | GET | /rentals/ping | 없음 | 200 |  | - |
| 19 | rental | POST | /rentals | ADMIN | 201·409 | 400·401·403·404 | FR-RNT-01 |
| 20 | rental | GET | /rentals | ADMIN·CUSTOMER(본인만 보임) | 200 | 401·403 | FR-USR-03 |
| 21 | rental | GET | /rentals/{rentalId} | ADMIN·CUSTOMER · OWN_RENTAL | 200·403 | 401·404 | FR-RNT-02 |
| 22 | rental | POST | /rentals/{rentalId}/checkpoints | ADMIN | 201·409 | 400·401·403·404 | FR-RNT-02 |
| 23 | rental | POST | /rentals/{rentalId}/close | ADMIN | 204·409 | 401·403·404 | FR-RNT-02 |
| 24 | rental | POST | /devices | ADMIN | 201·409 | 400·401·403 | FR-RNT-01 |
| 25 | rental | GET | /devices | ADMIN | 200 | 401·403 | FR-RNT-05 |
| 26 | rental | PATCH | /devices/{deviceId} | ADMIN | 200·404·409 | 400·401·403 | FR-RNT-05 |
| 27 | rental | GET | /device-models | ADMIN | 200 | 401·403 | FR-RNT-03 |
| 28 | rental | GET | /device-models/{modelCode} | ADMIN·CUSTOMER | 200·404 | 401·403 | FR-RNT-03 |
| 29 | rental | PUT | /device-models/{modelCode} | ADMIN | 200 | 400·401·403 | FR-RNT-03 |
| 30 | rental | POST | /pilot/participants | ADMIN | 201 | 400·401·403·409 | FR-PIL-01 |
| 31 | capture | GET | /captures/ping | 없음 | 200 |  | - |
| 32 | capture | POST | /captures/sets | BOOTH · BOOTH, 촬영 · CHECKPOINT | 201·403 | 400·401 | FR-CAP-01·05 |
| 33 | capture | POST | /captures/sets/{setId}/complete | BOOTH · BOOTH, 촬영 · CHECKPOINT | 202·409 | 400·401·403·404·422 | FR-CAP-01·02 |
| 33a | capture | POST | /captures/sets/{setId}/uploads | BOOTH · BOOTH, 촬영 · CHECKPOINT | 200 | 400·401·403·404·409 | FR-CAP-05 |
| 34 | capture | POST | /captures/sets/{setId}/detections | BOOTH · BOOTH | 201 | 400·401·403·404·409 | FR-INS-01 |
| 35 | capture | GET | /captures/sets/{setId} | ADMIN, 촬영 · CHECKPOINT | 200 | 401·403·404 | FR-CAP-01 |
| 36 | capture | GET | /captures/checkpoints/{checkpointId}/inspection | ADMIN·CUSTOMER · OWN_RENTAL | 200 | 401·403·404 | FR-INS-03·04 |
| 37 | capture | GET | /captures/checkpoints/{checkpointId}/media | ADMIN·CUSTOMER · OWN_RENTAL | 200 | 401·403·404 | FR-RPT-01 |
| 38 | diagnostics | GET | /diagnostics/ping | 없음 | 200 |  | - |
| 39 | diagnostics | POST | /diagnostics/runs | AGENT · CHECKPOINT | 201·409·422 | 400·401·403 | FR-DIA-05·06 |
| 40 | diagnostics | GET | /diagnostics/checkpoints/{checkpointId} | ADMIN·CUSTOMER · OWN_RENTAL | 200 | 401·403·404 | FR-DIA-06 |
| 41 | report | GET | /reports/ping | 없음 | 200 |  | - |
| 42 | report | GET | /reports/rentals/{rentalId} | ADMIN·CUSTOMER · OWN_RENTAL | 200 | 401·403·404 | FR-RPT-03 |
| 43 | report | GET | /reports/rentals/{rentalId}/stream | ADMIN·CUSTOMER · OWN_RENTAL, 촬영 · CHECKPOINT | 200 SSE | 401·403·404 | FR-RPT-04 |
| 44 | report | GET | /reports/rentals/{rentalId}/chain | ADMIN | 200 | 401·403·404 | FR-INT-01 |
| 45 | report | GET | /verify/{verifyToken} | PUBLIC | 200·404 |  | FR-INT-02·03 |
| 46 | report | GET | /reports/search | ADMIN | 200 | 401·403 | FR-RPT-05 |

`Idempotency-Key` 필수: #33, #39.
