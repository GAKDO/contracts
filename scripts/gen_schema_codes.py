#!/usr/bin/env python3
"""codes.yaml의 코드 값 목록을 JSON Schema 2020-12 $defs(schemas/codes.gen.schema.json)로 만든다.

이벤트(events/)와 진단 JSON(diagnostics/) 스키마는 코드 값을 복사하지 않고 이 파일의 $defs를 $ref로 참조한다(헌법 I).
이름 규칙은 gen_openapi_codes.py와 같다(rental.status → RentalStatus, capture.face_required.BOOTH → CaptureFaceRequiredBooth).
이 스크립트가 만든 파일은 손으로 고치지 않고, CI는 --check로 생성본이 codes.yaml과 같은지 확인한다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_openapi_codes import CODES, ROOT, build_schemas  # noqa: E402  같은 이름 규칙·문자열 검사를 다시 쓴다

OUT = ROOT / "schemas" / "codes.gen.schema.json"
SCHEMA_ID = "https://raw.githubusercontent.com/GAKDO/contracts/main/schemas/codes.gen.schema.json"


def render(codes: dict) -> str:
    doc = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "TRACE 코드 값 (생성)",
        "description": (
            "생성 파일입니다. 손으로 고치지 말고 codes.yaml을 고친 뒤 "
            f"python3 scripts/gen_schema_codes.py로 다시 만드세요. (codes.yaml version {codes.get('version')})"
        ),
        "$defs": build_schemas(codes),
    }
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="생성본이 최신인지만 확인한다")
    args = parser.parse_args()

    codes = yaml.safe_load(CODES.read_text(encoding="utf-8"))
    text = render(codes)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)}가 codes.yaml과 다릅니다. scripts/gen_schema_codes.py를 실행하세요.", file=sys.stderr)
            return 1
        print("JSON Schema 코드 값 생성본 최신")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} 생성 ({len(build_schemas(codes))}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
