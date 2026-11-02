# 수용 기준 대조 (analyze·converge)

| 수용 기준 | 증거 | 결과 |
| --- | --- | --- |
| macOS 예시 통과 | examples/diagnostics/valid/macos.json | 통과 |
| Windows 예시 통과 | examples/diagnostics/valid/windows.json | 통과 |
| SSD 생략 예시 통과 | examples/diagnostics/valid/ssd-skipped.json | 통과 |
| 잘못된 예시 실패(≥2) | invalid/ 4개 | 4개 모두 실패 |
| 컴퓨터 이름·사용자 이름 없음 | additionalProperties false, computer-name.json 실패 | 충족 |
| 용량 값 + 단위 | capacity-without-unit.json 실패 | 충족 |
| null + 생략 사유 | skipped-without-reason.json 실패 | 충족 |
| 3회 중앙값·측정 조건·전원 | trials 3개, conditions 필수, benchmark-without-ac-power.json 실패 | 충족 |
| OpenAPI가 같은 스키마 참조 | DiagnosticUpload `$ref`, redocly 경고 0 | 충족 |

명세·계획·작업 사이 어긋남 없음. Converged.
