#!/usr/bin/env bash
# 진단 JSON 예시 검사 (C2 수용 기준): valid/의 예시는 모두 스키마를 통과하고, invalid/의 예시는 하나하나 실패해야 한다.
# 쓰는 법: scripts/check_diagnostics_examples.sh   (check-jsonschema 필요: pip install check-jsonschema)
set -euo pipefail
cd "$(dirname "$0")/.."

schema=diagnostics/result.schema.json
fail=0

shopt -s nullglob
valid=(examples/diagnostics/valid/*.json)
invalid=(examples/diagnostics/invalid/*.json)
if [ ${#valid[@]} -eq 0 ] || [ ${#invalid[@]} -eq 0 ]; then
  echo "예시가 없습니다: examples/diagnostics/valid·invalid" >&2
  exit 1
fi

for f in "${valid[@]}"; do
  if check-jsonschema --schemafile "$schema" "$f" >/dev/null 2>&1; then
    echo "통과(기대대로): $f"
  else
    echo "실패(통과해야 함): $f" >&2
    check-jsonschema --schemafile "$schema" "$f" >&2 || true
    fail=1
  fi
done

for f in "${invalid[@]}"; do
  if check-jsonschema --schemafile "$schema" "$f" >/dev/null 2>&1; then
    echo "통과(실패해야 함): $f" >&2
    fail=1
  else
    echo "실패(기대대로): $f"
  fi
done

exit $fail
