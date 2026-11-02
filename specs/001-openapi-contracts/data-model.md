# Phase 1 데이터 모델: C1 OpenAPI 5개

필드 이름은 camelCase, ID는 `Uuid`(format uuid, UUIDv7), 시각은 `DateTime`(format date-time, 오프셋 필수). 필드 출처는 GAKDO/docs `design/ddl.md`. 코드 값 타입은 `codes.gen.yaml`의 enum(예: `DeviceStatus` = codes.yaml `device.status`).

## 공통 (components/common.yaml)

| 이름 | 형태 |
| --- | --- |
| `Uuid` | string, format uuid, pattern UUIDv7(`^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`) |
| `DateTime` | string, format date-time, pattern으로 오프셋(`Z` 또는 `±hh:mm`) 강제 |
| `Sha256` | string, `^[0-9a-f]{64}$` |
| `Problem` | `type`(uri, 기본 about:blank), `title`, `status`(int), `detail`, `instance`, **`code`(ErrorCode, 필수)**, `errors`(필드 오류 배열, 400에서만: `{field, message}`) |
| `PingResponse` | `service`, `version`, `commit` (기존 PingController 응답) |
| 파라미터 | `Limit`(1~100, 기본 20), `Cursor`, `IdempotencyKey`(헤더, 필수, 8~128자) |
| 응답 | `BadRequest`(400), `Unauthorized`(401), `Forbidden`(403), `NotFound`(404), `TooManyRequests`(429, `Retry-After` 헤더) — 모두 `application/problem+json` |
| 보안 방식 | `bearerJwt`, `refreshCookie`(cookie `trace_refresh`) |

목록 응답은 서버 파일에서 `{ items: [X], nextCursor: string|null }`으로 각자 정의한다(3.1에 제네릭이 없어서).

## auth-server

| 스키마 | 필드 |
| --- | --- |
| `SignupRequest` | email, password(8~72자), name(1~64), privacyAgreed(boolean, true여야 함) |
| `SignupResponse` | accountId, status(`AccountStatus`=PENDING) |
| `EmailVerifyRequest` | email, code(6자리 숫자) |
| `EmailResendRequest` | email |
| `LoginRequest` | email, password |
| `TokenResponse` | accessToken, tokenType(`Bearer`), expiresIn(초), role(`Role`) — 리프레시는 `Set-Cookie` 헤더 |
| `PasswordResetRequestRequest` | email |
| `PasswordResetRequest` | email, code, newPassword |
| `MeResponse` | accountId, email, name, role, status, rentalIds[] |
| `WithdrawRequest` | password |
| `CaptureLinkCreateRequest` | rentalId, checkpointId |
| `CaptureLinkResponse` | url, expiresAt |
| `CaptureLinkExchangeRequest` | token |
| `CaptureTokenResponse` | accessToken, tokenType, expiresIn, rentalId, checkpointId |
| `BoothTokenRequest` | clientId, clientSecret |
| `BoothTokenResponse` | accessToken, tokenType, expiresIn, boothId |
| `PairingCodeCreateRequest` | checkpointId |
| `PairingCodeResponse` | code(6자리), expiresAt |
| `PairingExchangeRequest` | code |
| `AgentTokenResponse` | accessToken, tokenType, expiresIn, checkpointId |
| `Jwks` | keys[] (`kty`,`kid`,`use`,`alg`,`n`,`e`) |

`Role`(토큰): ADMIN·CUSTOMER는 codes.yaml `auth.role`, BOOTH·AGENT는 토큰 전용 → codes.yaml `auth.token_role: [ADMIN, CUSTOMER, BOOTH, AGENT]`를 더한다(값 추가).

## rental-server

| 스키마 | 필드 |
| --- | --- |
| `RentalCreateRequest` | deviceId, renterRef(1~128) |
| `Rental` | rentalId, deviceId, renterRef, status(`RentalStatus`), startedAt, endedAt, createdAt, checkpoints[`Checkpoint`] |
| `RentalSummary`/`RentalPage` | rentalId, deviceId, serial, modelCode, status, createdAt / items·nextCursor |
| `Checkpoint` | checkpointId, type(`CheckpointType`), status(`CheckpointStatus`), occurredAt |
| `CheckpointCreateRequest` | type |
| `DeviceCreateRequest` | serial, modelCode, os(`DeviceOs`), color?, assetNo? |
| `DeviceUpdateRequest` | color?, assetNo?, os?, status?(`DeviceStatus`) — `additionalProperties: false`라 serial·modelCode를 보내면 400 |
| `Device`/`DevicePage` | deviceId, serial, modelCode, modelName, os, color, assetNo, status, retiredAt, createdAt, updatedAt |
| 쿼리(`GET /devices`) | modelCode, status, q(시리얼·자산번호 일부), limit, cursor |
| `DeviceModelSummary` | modelCode, name, manufacturer, formFactor |
| `DeviceModel` | + spec{cpu, ramGb, ssdGb}, dimensions{widthMm, depthMm, baseHMm, lidHMm}, updatedAt |
| `DeviceModelUpsertRequest` | name, manufacturer?, formFactor, spec?, dimensions |
| `PilotParticipantCreateRequest`/`PilotParticipant` | alias(`^P\d{2,3}$`), deviceId, consentAt / + participantId, createdAt |

## capture-server

| 스키마 | 필드 |
| --- | --- |
| `CaptureSetCreateRequest` | checkpointId, source(`CaptureSource`), photos[`PhotoSpec`] (1~54) |
| `PhotoSpec` | face, light, camera, sha256, contentType(`image/jpeg`·`image/png`), takenAt |
| `CaptureSetCreateResponse` | captureSetId, uploads[{face, light, method(`PUT`), url, headers?, expiresAt}] |
| `CaptureSet` | captureSetId, checkpointId, source, boothId, status(`CaptureSetStatus`), quality(`CaptureQuality`), photos[{face, light, camera, sha256, uploaded(bool), qualityOk}] |
| `DetectionBatchRequest` | modelVersion, detections[{face, light, class(`DefectClass`), polygon[[x,y]], confidence}] |
| `DetectionBatchResponse` | accepted(int) |
| `Inspection` | checkpointId, grade(`Grade`)?, ruleVersion?, reasons[], defects[{defectId, face, class, polygon, lengthMm, areaMm2, confidence, modelVersion, source, match{status(`MatchStatus`), prevDefectId, distanceMm}}] |
| `CheckpointMedia` | checkpointId, expiresAt, textures[{face, url}], crops[{defectId, url}] |

## diagnostics-server

| 스키마 | 필드 |
| --- | --- |
| `DiagnosticUpload` | C2 스키마 참조 자리(C1에서는 object) |
| `DiagnosticRunCreated` | runId, flags[`InspectionFlag`] |
| `InspectionFlag` | kind(`FlagKind`), detail(object), baseRunId |
| `CheckpointDiagnostics` | checkpointId, current(`RunSummary`), previous(`RunSummary`, 없으면 null), flags[] — `RunSummary` = runId, collectedAt, os, battery{cycleCount, designCapacity, fullChargeCapacity, capacityUnit, maxCapacityPct, condition}, ssd{percentUsed, availableSparePct, criticalWarning, powerOnHours, mediaErrors, skippedReason}, components[{kind, identifier}], benchmarks[{metric, median}]. 읽지 못한 값은 null |

## report-server

| 스키마 | 필드 |
| --- | --- |
| `RentalTimeline` | rentalId, modelCode, verifyUrl(첫 봉인 전 null), chainStatus(`ReportChainStatus`: VALID·BROKEN·PENDING), checkpoints[{checkpointId, type, status, occurredAt, grade?, newDefectCount, pins[{defectId, face, x, y, isNew}], diagnosticsSummary{maxCapacityPct, flags[]}, sealedAt?}] |
| `ProgressEvent` (SSE `progress`) | checkpointId, stage(`ReportProgressStage`: UPLOADED·ALIGNED·INSPECTED·GRADED·SEALED), percent(0~100), at |
| `DoneEvent` (SSE `done`) | checkpointId, grade |
| `ChainRecord` / `Chain` | seq, checkpointId, checkpointType, payloadHash, prevHash(null 가능), signature, signedAt / rentalId, valid, records[] |
| `VerifyResponse` | valid, modelName, records[{seq, checkpointType, grade, payloadHash, signedAt}], checkedAt — 개인정보·사진·진단 상세 없음 |
| `ReportSearchPage` | items[{rentalId, serial, modelCode, status, updatedAt}], nextCursor |

## 오류 code 목록 (codes.yaml `error_code`)

| code | 상태 | 쓰는 곳 |
| --- | --- | --- |
| VALIDATION_FAILED | 400 | 공통(형식 오류) |
| UNAUTHENTICATED | 401 | 공통(토큰 없음·만료) |
| FORBIDDEN | 403 | 공통(역할 없음) |
| OUT_OF_SCOPE | 403 | 본인 렌탈·그 시점·자기 부스 밖 |
| NOT_FOUND | 404 | 공통 |
| RATE_LIMITED | 429 | 가입·로그인·코드 확인·페어링 교환 |
| INTERNAL_ERROR | 500 | 공통 |
| CONSENT_REQUIRED | 400 | signup |
| EMAIL_ALREADY_EXISTS | 409 | signup |
| CODE_INVALID | 400 | email/verify, password/reset (남은 횟수는 detail과 `remainingAttempts`) |
| CODE_EXPIRED | 410 | email/verify, password/reset |
| RESEND_TOO_SOON | 429 | email/resend |
| INVALID_CREDENTIALS | 401 | login, DELETE me(비밀번호 틀림) |
| EMAIL_NOT_VERIFIED | 403 | login |
| REFRESH_INVALID | 401 | refresh |
| CAPTURE_LINK_INVALID | 410 | capture-links/exchange(만료·사용됨) |
| RENTAL_LINKED_TO_OTHER | 409 | capture-links/exchange |
| CLIENT_CREDENTIALS_INVALID | 401 | booth/token |
| PAIRING_CODE_INVALID | 400 | pairing-codes/exchange |
| PAIRING_CODE_EXPIRED | 410 | pairing-codes/exchange |
| RENTAL_OPEN_EXISTS | 409 | POST rentals |
| DEVICE_NOT_ACTIVE | 409 | POST rentals(수리 중·폐기 기기, WE1 수용 기준) |
| CHECKPOINT_ORDER_VIOLATION | 409 | POST checkpoints |
| RENTAL_NOT_CLOSABLE | 409 | POST close |
| DEVICE_SERIAL_EXISTS | 409 | POST devices |
| DEVICE_HAS_OPEN_RENTAL | 409 | PATCH devices(진행 중 렌탈 있는데 수리 중·폐기로) |
| PILOT_ALIAS_EXISTS | 409 | POST pilot/participants |
| CAPTURE_FACES_MISSING | 409 | sets complete |
| CAPTURE_HASH_MISMATCH | 409 | sets complete |
| CAPTURE_SET_CLOSED | 409 | sets complete·detections(이미 완료된 세트) |
| DIAGNOSTIC_ALREADY_UPLOADED | 409 | diagnostics runs |
| DIAGNOSTIC_SCHEMA_INVALID | 422 | diagnostics runs |
| DEVICE_SERIAL_MISMATCH | 422 | diagnostics runs |
| IDEMPOTENCY_KEY_CONFLICT | 422 | 같은 키에 다른 본문 |
