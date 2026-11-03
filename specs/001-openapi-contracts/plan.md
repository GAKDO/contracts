# 구현 계획: C1 OpenAPI 5개

**Branch**: `claude/project-thread-1s3ob8` | **Date**: 2026-11-02 | **Spec**: [spec.md](./spec.md)

**Input**: `specs/001-openapi-contracts/spec.md`

## 요약

rest-api-v0.md의 경로 41개와 ping 5개를 서버별 OpenAPI 3.1 파일 5개(`openapi/<서버>-server.yaml`)로 옮긴다. 여러 파일이 같이 쓰는 형식(Problem Details, 커서 목록, ID·시각 형식, 보안 방식)은 `openapi/components/common.yaml` 한 곳에 두고 `$ref`로 참조한다. 코드 값은 codes.yaml에서 스크립트로 만든 `openapi/components/codes.gen.yaml`을 참조하고, CI가 생성본과 codes.yaml이 어긋나지 않는지 확인한다. 오류 `code`는 codes.yaml에 `error_code`로 더한다(0.3.0). 역할·범위는 `security` + 확장 필드 `x-trace-access`로 경로마다 적는다.

## 기술 맥락

**Language/Version**: OpenAPI 3.1.0(스키마는 JSON Schema 2020-12), YAML

**Primary Dependencies**: `@redocly/cli@2`(린트·번들), `yamllint`, Python 3.12 + PyYAML(코드 값 생성·경로 대조 스크립트)

**Storage**: 해당 없음(파일)

**Testing**: CI '계약 검사'(yamllint·check-jsonschema·redocly lint) + 이번에 더하는 두 검사: 코드 값 생성본 일치(`scripts/gen_openapi_codes.py --check`), 경로 대조(`scripts/check_openapi_coverage.py <rest-api-v0.md>`, 로컬·PR 본문용)

**Target Platform**: 소비자 — Spring 서버 5개(A), web의 openapi-typescript·MSW(C), agent·booth의 HTTP 클라이언트(B), gateway 역할 검사(GW1)

**Project Type**: 계약 레포(스키마만, 실행 코드 없음)

**Performance Goals**: 해당 없음

**Constraints**: 11/3 고정 뒤에는 더하는 변경만. 파일마다 openapi-typescript가 따로 돌 수 있게 외부 `$ref`는 상대 경로만 쓴다. 비밀·실명 예시 금지.

**Scale/Scope**: 경로 46개, 공통 컴포넌트 약 10개, 오류 code 34개

## 헌법 점검

*Phase 0 전 통과, Phase 1 뒤 다시 확인함.*

| 원칙 | 점검 | 결과 |
| --- | --- | --- |
| I. 계약이 먼저다 | 이 기능이 계약 자체. 코드 값은 codes.yaml이 원본이고 OpenAPI는 생성본을 참조(손으로 복사하지 않음). codes.yaml 변경은 값 추가(`error_code`, `auth.token_role`, `report.chain_status`, `report.progress_stage`)만 | 통과 |
| II. 서비스 경계 | 서버마다 파일 하나, 다른 서버 ID는 값(publicId)으로만. 사진은 사전 서명 URL만 주고 본문을 받지 않음 | 통과 |
| III. 기록은 고칠 수 없다 | 사진·진단에 `sha256` 필드, 체인에 `payloadHash`·`prevHash`·`signature`. 읽지 못한 값은 null 허용 + 사유 필드 | 통과 |
| IV. 테스트와 품질 게이트 | 수용 기준 = redocly lint 통과 + 경로 대조 + B·C 승인. CI에 생성본 일치 검사 추가 | 통과 |
| V. 비밀과 개인정보 | 예시는 지어낸 값. 검증 응답에 개인정보 없음. ping만 인증 없음, 역할은 최소 | 통과 |
| VI. 단순하게 | rest-api-v0 표에 있는 경로만. 공통 파일 1개, 스크립트 2개(각 100줄 안팎) | 통과 |

브랜치: 헌법의 Spec Kit 기본값은 `feature/001-openapi-contracts`이지만 이 세션의 지정 브랜치 `claude/project-thread-1s3ob8`를 쓴다(PR 본문에 적음).

원본과 다른 점(PR 본문에 적고 승인받음): `GET /devices`의 `page` → 커서, 오류 `code`를 codes.yaml로 고정, `POST /pilot/participants`에 400·409 추가, 인증 경로마다 401·403 추가.

## 프로젝트 구조

### 문서 (이 기능)

```text
specs/001-openapi-contracts/
├── plan.md              # 이 파일
├── research.md          # Phase 0: 결정과 이유
├── data-model.md        # Phase 1: 공통 형식·서버별 스키마·오류 code 목록
├── quickstart.md        # Phase 1: 검사·소비 방법
├── contracts/
│   ├── path-inventory.md   # 경로 46개 대조표 (메서드·경로·역할·응답·FR)
│   └── access-matrix.md    # x-trace-access 표기 규칙과 역할 × 경로 표 대응
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### 레포 (contracts)

```text
codes.yaml                         # + error_code, auth.token_role, report.*, version 0.3.0
openapi/
├── README.md                      # 파일 목록·규칙 갱신
├── components/
│   ├── common.yaml                # Problem, CursorPage, PublicId, DateTime, 보안 방식, 공통 응답·파라미터
│   └── codes.gen.yaml             # codes.yaml에서 생성 (손으로 고치지 않음)
├── auth-server.yaml               # 16 + ping
├── rental-server.yaml             # 12 + ping
├── capture-server.yaml            # 6 + ping
├── diagnostics-server.yaml        # 2 + ping
└── report-server.yaml             # 5 + ping
redocly.yaml                       # 린트 규칙(recommended + 확장 필드 허용)
scripts/
├── gen_openapi_codes.py           # codes.yaml → codes.gen.yaml, --check
└── check_openapi_coverage.py      # rest-api-v0.md 표 ↔ OpenAPI 경로 대조
.github/workflows/contracts-ci.yml # + 코드 값 생성본 일치 단계
```

**Structure Decision**: 서버별 파일 5개 + 공통 컴포넌트 파일. 공통 형식을 파일마다 복사하면 5곳이 어긋날 위험이 있고, 하나로 합치면 서버별 소비(타입 생성·서버 담당 리뷰)가 어렵다.

## 복잡도 기록

없음(헌법 위반 없음).
