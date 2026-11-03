# 계획: 부스 빠른 검사 세트

- codes.yaml에 값 추가 → `scripts/gen_openapi_codes.py`·`gen_schema_codes.py`로 생성본 갱신(CaptureProfile, CaptureFaceRequiredQuickBooth).
- openapi/capture-server.yaml: CaptureSetCreateRequest·CaptureSet에 `profile`, Inspection에 `photoDefects`(PhotoDefect), DetectionBatchRequest에 `analyzedPhotos`(PhotoRef),
  CheckpointMedia에 `photos`, 완료 설명에 QUICK 규칙. 모두 required에 넣지 않는다.
- 이벤트 스키마는 그대로. capture-server는 QUICK 세트도 `trace.capture.uploaded`·`trace.checkpoint.graded`를 지금 형식으로 낸다.
- 구현은 capture_server 같은 브랜치(Flyway 새 파일로 capture_set.profile, defect 좌표 기준 칸).
