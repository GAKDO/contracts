#!/usr/bin/env python3
"""마지막 릴리스 태그와 지금 계약을 비교해 깨지는 변경이 없는지 본다(11/3 고정 뒤 규칙, CONTRIBUTING.md 2번).

사용: python3 scripts/check_breaking.py [기준 git ref, 기본은 가장 최근 v* 태그]

깨지는 변경으로 보는 것:
- OpenAPI: operation(경로 + 메서드) 삭제, components.schemas 삭제, 스키마 속성 삭제, 새 required, enum 값 삭제
- 이벤트·진단 JSON Schema: 기준에 있던 속성 삭제, 새 required (중첩 스키마 포함)
- codes.yaml: 값 목록에서 값 삭제, 키 삭제

새 파일·새 경로·선택 속성·새 값 추가는 깨지지 않으므로 통과한다.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
METHODS = {"get", "post", "put", "patch", "delete"}


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def baseline_ref() -> str | None:
    if len(sys.argv) > 1:
        return sys.argv[1]
    # 태그가 develop의 조상이 아닐 수 있어(main에서 릴리스) describe 대신 버전 순으로 가장 큰 태그를 쓴다
    r = git("tag", "--list", "v*", "--sort=-v:refname")
    tags = r.stdout.split()
    return tags[0] if tags else None


def at_ref(ref: str, path: str) -> str | None:
    r = git("show", f"{ref}:{path}")
    return r.stdout if r.returncode == 0 else None


def tracked(ref: str, pattern: str) -> list[str]:
    r = git("ls-tree", "-r", "--name-only", ref)
    from fnmatch import fnmatch
    return [p for p in r.stdout.splitlines() if fnmatch(p, pattern)]


def object_schemas(node: object, path: str = "") -> dict[str, tuple[set[str], set[str], list | None]]:
    """properties 또는 enum이 있는 모든 하위 스키마를 경로 → (속성, required, enum)으로 모은다."""
    out: dict[str, tuple[set[str], set[str], list | None]] = {}
    if isinstance(node, dict):
        props = node.get("properties")
        enum = node.get("enum")
        if isinstance(props, dict) or isinstance(enum, list):
            out[path] = (set(props or {}), set(node.get("required", []) or []), enum if isinstance(enum, list) else None)
        for k, v in node.items():
            out.update(object_schemas(v, f"{path}/{k}"))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.update(object_schemas(v, f"{path}[{i}]"))
    return out


def compare_schemas(name: str, old: object, new: object, errors: list[str]) -> None:
    a, b = object_schemas(old), object_schemas(new)
    for p, (props, req, enum) in a.items():
        if p not in b:
            continue  # 구조가 옮겨진 경우는 아래 operation·schema 이름 비교가 잡는다
        bprops, breq, benum = b[p]
        for x in sorted(props - bprops):
            errors.append(f"{name}{p}: 속성 삭제 {x}")
        for x in sorted(breq - req):
            errors.append(f"{name}{p}: 새 required {x}")
        if enum is not None and benum is not None:
            for x in sorted(set(map(str, enum)) - set(map(str, benum))):
                errors.append(f"{name}{p}: enum 값 삭제 {x}")


def check_openapi(ref: str, errors: list[str]) -> None:
    for path in tracked(ref, "openapi/*.yaml") + tracked(ref, "openapi/components/*.yaml"):
        old_text = at_ref(ref, path)
        cur = ROOT / path
        if old_text is None:
            continue
        if not cur.exists():
            errors.append(f"{path}: 파일 삭제")
            continue
        old, new = yaml.safe_load(old_text), yaml.safe_load(cur.read_text(encoding="utf-8"))
        ops_old = {(m.upper(), p) for p, item in (old.get("paths") or {}).items() for m in item if m in METHODS}
        ops_new = {(m.upper(), p) for p, item in (new.get("paths") or {}).items() for m in item if m in METHODS}
        for m, p in sorted(ops_old - ops_new):
            errors.append(f"{path}: operation 삭제 {m} {p}")
        s_old = (old.get("components") or {}).get("schemas") or {}
        s_new = (new.get("components") or {}).get("schemas") or {}
        for n in sorted(set(s_old) - set(s_new)):
            errors.append(f"{path}: 스키마 삭제 {n}")
        for n in sorted(set(s_old) & set(s_new)):
            compare_schemas(f"{path}#{n}", s_old[n], s_new[n], errors)


def check_json_schemas(ref: str, errors: list[str]) -> None:
    for path in tracked(ref, "events/*.schema.json") + tracked(ref, "diagnostics/*.schema.json"):
        old_text = at_ref(ref, path)
        cur = ROOT / path
        if old_text is None:
            continue
        if not cur.exists():
            errors.append(f"{path}: 파일 삭제")
            continue
        compare_schemas(path, json.loads(old_text), json.loads(cur.read_text(encoding="utf-8")), errors)


def check_codes(ref: str, errors: list[str]) -> None:
    old_text = at_ref(ref, "codes.yaml")
    if old_text is None:
        return
    old, new = yaml.safe_load(old_text), yaml.safe_load((ROOT / "codes.yaml").read_text(encoding="utf-8"))

    def walk(a: object, b: object, path: str) -> None:
        if isinstance(a, dict):
            if not isinstance(b, dict):
                errors.append(f"codes.yaml {path}: 모양이 바뀜")
                return
            for k in a:
                if k not in b:
                    errors.append(f"codes.yaml {path}.{k}: 키 삭제")
                else:
                    walk(a[k], b[k], f"{path}.{k}" if path else str(k))
        elif isinstance(a, list):
            if not isinstance(b, list):
                errors.append(f"codes.yaml {path}: 모양이 바뀜")
                return
            for x in a:
                if x not in b:
                    errors.append(f"codes.yaml {path}: 값 삭제 {x}")

    walk({k: v for k, v in old.items() if k != "version"}, {k: v for k, v in new.items() if k != "version"}, "")


def main() -> int:
    ref = baseline_ref()
    if ref is None:
        print("기준 태그(v*)가 없어 건너뜁니다. CI는 checkout에 fetch-depth: 0이 필요합니다.")
        return 0
    errors: list[str] = []
    check_openapi(ref, errors)
    check_json_schemas(ref, errors)
    check_codes(ref, errors)
    if errors:
        print(f"깨지는 변경 {len(errors)}건 (기준 {ref}):")
        for e in errors:
            print(f"  - {e}")
        print("11/3 고정 뒤에는 더하는 변경만 합니다. 꼭 필요하면 주 버전·새 라우팅 키로 내고 사람에게 알립니다.")
        return 1
    print(f"깨지는 변경 없음 (기준 {ref})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
