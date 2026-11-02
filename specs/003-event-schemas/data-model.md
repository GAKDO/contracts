# 데이터 모델: C3 이벤트 5종

봉투(모든 이벤트, 필수): `schemaVersion`("1.0") · `eventId`(UUIDv7) · `occurredAt`(ISO 8601 + 오프셋) · `rentalId` · `checkpointId`

| 라우팅 키 | 필수 필드 | 선택 필드 | 코드 값 참조 |
| --- | --- | --- | --- |
| `trace.capture.uploaded` | captureSetId, source, needDetection, photos[1..54]{photoId, face, light, camera, objectKey, sha256} | skippedFaces{면: 사유} | CaptureSource, CaptureFace, CaptureLight, CaptureCamera |
| `trace.inspect.completed` | captureSetId, modelVersion, alignments[]{photoId, method, homography 3×3, errorPx\|null, rectifiedKey}, defects[]{defectId, photoId, class, polygon[[x,y]…≥3], confidence 0~1}, textureKeys{면: 키} | defects[].lengthMm\|null, areaMm2\|null, failedPhotos[]{photoId, reason} | InspectionAlignmentMethod, InspectionDefectClass, CaptureFace |
| `trace.checkpoint.graded` | captureSetId, checkpointType, grade, ruleVersion, newDefectIds[], unjudgeableFaces[], photos[1..54]{photoId, sha256} | — | RentalCheckpointType, InspectionGrade, CaptureFace |
| `trace.diagnostics.recorded` | runId, sha256, baseRunId\|null, flags[]{kind, detail} | — | DiagnosticsFlagKind |
| `trace.record.sealed` | seq≥1, checkpointType, grade, payloadHash, prevHash(seq 1이면 null, 아니면 SHA-256), signedAt | — | RentalCheckpointType, InspectionGrade |

DDL 대응: photo(face·light·camera·object_key·sha256), face_alignment(method·homography·error_px·rectified_key), defect(class·polygon·length_mm·area_mm2·confidence·model_version), grade_result(grade·rule_version), diagnostic_run(sha256), inspection_flag(kind·detail·base_run_id), record_chain(seq·payload_hash·prev_hash·signed_at).
