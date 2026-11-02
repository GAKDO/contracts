#!/usr/bin/env python3
"""codes.yaml의 코드 값 목록을 OpenAPI enum 스키마(openapi/components/codes.gen.yaml)로 만든다.

값은 codes.yaml 한 곳에서만 정한다(헌법 I). 이 스크립트가 만든 파일은 손으로 고치지 않고,
CI는 --check로 생성본이 codes.yaml과 같은지 확인한다.

이름 규칙: <구역><키>를 PascalCase로(rental.status → RentalStatus), 최상위 목록은 키만(error_code → ErrorCode).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CODES = ROOT / "codes.yaml"
OUT = ROOT / "openapi" / "components" / "codes.gen.yaml"


def pascal(*parts: str) -> str:
    return "".join(w[:1].upper() + w[1:] for p in parts for w in p.split("_"))


def check_strings(name: str, values: list) -> None:
    """YAML 1.1 파서는 따옴표 없는 OFF·ON·YES·NO를 불리언으로 읽는다. 문자열이 아니면 바로 알린다."""
    bad = [v for v in values if not isinstance(v, str)]
    if bad:
        raise SystemExit(f"codes.yaml {name}에 문자열이 아닌 값 {bad!r}가 있습니다. 따옴표로 감싸 주세요(예: 'OFF').")


def build_schemas(codes: dict) -> dict[str, dict]:
    """codes.yaml을 읽어 스키마 이름 → enum 스키마 사전을 만든다. 목록이 아닌 값(version)은 건너뛴다."""
    schemas: dict[str, dict] = {}
    for section, body in codes.items():
        if isinstance(body, list):
            check_strings(section, body)
            schemas[pascal(section)] = {"type": "string", "enum": body, "description": f"codes.yaml {section}"}
        elif isinstance(body, dict):
            for key, values in body.items():
                if isinstance(values, list):
                    check_strings(f"{section}.{key}", values)
                    schemas[pascal(section, key)] = {
                        "type": "string",
                        "enum": values,
                        "description": f"codes.yaml {section}.{key}",
                    }
    return schemas


def render(codes: dict) -> str:
    header = (
        "# 생성 파일입니다. 손으로 고치지 말고 codes.yaml을 고친 뒤\n"
        "#   python3 scripts/gen_openapi_codes.py\n"
        f"# 로 다시 만드세요. (codes.yaml version {codes.get('version')})\n"
    )
    doc = {
        "openapi": "3.1.0",
        "info": {"title": "TRACE 코드 값 (생성)", "version": str(codes.get("version"))},
        "paths": {},
        "components": {"schemas": build_schemas(codes)},
    }
    return header + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=160)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="생성본이 최신인지만 확인한다")
    args = parser.parse_args()

    codes = yaml.safe_load(CODES.read_text(encoding="utf-8"))
    text = render(codes)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"{OUT.relative_to(ROOT)}가 codes.yaml과 다릅니다. scripts/gen_openapi_codes.py를 실행하세요.", file=sys.stderr)
            return 1
        print("코드 값 생성본 최신")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)} 생성 ({len(build_schemas(codes))}개)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
