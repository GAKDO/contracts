# 빠른 확인

```bash
pip install check-jsonschema yamllint pyyaml
python scripts/gen_schema_codes.py --check && python scripts/gen_openapi_codes.py --check
check-jsonschema --check-metaschema diagnostics/result.schema.json
scripts/check_diagnostics_examples.sh
npx -y @redocly/cli@2 lint openapi/*-server.yaml
```

에이전트(B)는 보내기 전에 `check-jsonschema --schemafile diagnostics/result.schema.json out.json`(또는 같은 스키마로 파이썬 jsonschema)로 스스로 검사한다.
