# 역할·범위 표기 (x-trace-access)

```yaml
security: [{ bearerJwt: [] }]      # 인증 없음은 security: []
x-trace-access:
  roles: [ADMIN, CUSTOMER]         # 토큰 role 클레임 (auth.token_role)
  scope: OWN_RENTAL                # NONE | OWN_RENTAL | CHECKPOINT | BOOTH
  captureToken: false              # 촬영 JWT(CUSTOMER + scope=checkpointId) 허용 여부
```

- `OWN_RENTAL`: CUSTOMER는 `rentals` 클레임에 있는 렌탈만(ADMIN은 제한 없음). 밖이면 403 `OUT_OF_SCOPE`.
- `CHECKPOINT`: 토큰 `scope`의 checkpointId와 요청의 시점이 같아야 함(AGENT, 촬영).
- `BOOTH`: 토큰 `scope`의 boothId 부스 것만.
- 역할이 다르면 403 `FORBIDDEN`, 토큰이 없으면 401 `UNAUTHENTICATED`.

## rest-api-v0 "역할 × 경로 표"와 대응

| 경로 묶음 | 경로 # (path-inventory) | roles · scope · captureToken |
| --- | --- | --- |
| 가입·인증·로그인·재설정·부스 토큰·페어링 교환 | 2·3·4·5·8·9·14·16 | 인증 없음 |
| 내 정보·로그아웃 | 7·10 | ADMIN·CUSTOMER · NONE · false |
| 탈퇴 | 11 | CUSTOMER · NONE · false |
| QR 링크·페어링 코드 발급 | 12·15 | ADMIN · NONE |
| QR 교환 | 13 | CUSTOMER · NONE · false |
| 기기·기종 목록, 렌탈·기기·기종 쓰기, 파일럿 | 19·22·23·24·25·26·27·29·30 | ADMIN · NONE |
| 렌탈 읽기, 기종 치수 읽기 | 20·21·28 | ADMIN·CUSTOMER · OWN_RENTAL(21) |
| 촬영 세트 생성·완료·URL 다시 받기 | 32·33·33a | BOOTH(BOOTH) + 촬영(CHECKPOINT) · captureToken true |
| 탐지 결과 올리기 | 34 | BOOTH · BOOTH |
| 검사 결과·사진 URL 읽기 | 36·37 | ADMIN·CUSTOMER · OWN_RENTAL |
| 진단 올리기 | 39 | AGENT · CHECKPOINT |
| 진단 결과 읽기 | 40 | ADMIN·CUSTOMER · OWN_RENTAL |
| 리포트·진행률 | 42·43 | ADMIN·CUSTOMER · OWN_RENTAL, 43만 captureToken true |
| 체인 전체·검색 | 44·46 | ADMIN |
| 검증 | 45 | 인증 없음 |

#35(세트 상태 읽기)는 원본 경로 표에 ADMIN·촬영으로 있으나 역할 × 경로 표에 행이 없어, 경로 표를 따른다.
