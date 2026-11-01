# contracts

TRACE의 OpenAPI·진단 JSON Schema·이벤트 스키마·codes.yaml 레포입니다. 담당: A (B·C 리뷰). 이 레포의 기능: C1, C2, C3 (GAKDO/docs `speckit/backlog.md`).

## 먼저 읽을 것

- 헌법: `.specify/memory/constitution.md` (모든 명세·계획·구현의 기준. 원본은 GAKDO/docs `speckit/constitution.md`)
- 기능 목록과 붙여 넣을 설명: GAKDO/docs [`speckit/backlog.md`](https://github.com/GAKDO/docs/blob/main/speckit/backlog.md)
- 설계서: [`design/mvp-design.md`](https://github.com/GAKDO/docs/blob/main/design/mvp-design.md), REST API: [`design/rest-api-v0.md`](https://github.com/GAKDO/docs/blob/main/design/rest-api-v0.md), 테이블: [`design/ddl.md`](https://github.com/GAKDO/docs/blob/main/design/ddl.md), 결정: [`decisions.md`](https://github.com/GAKDO/docs/blob/main/decisions.md)
- 계약 원본: [GAKDO/contracts](https://github.com/GAKDO/contracts) (OpenAPI·JSON Schema·`codes.yaml`)

## 명령

- 검사: CI '계약 검사'와 같은 `yamllint`·`check-jsonschema`·`redocly lint` (`.github/workflows/contracts-ci.yml` 참고)

## Spec Kit으로 기능 하나 만들기

1. `git switch develop && git pull`
2. `/speckit-specify` + backlog.md의 설명 → `feature/<번호>-<이름>` 브랜치와 `specs/<번호>-<이름>/spec.md`
3. `/speckit-clarify` → 질문에 답하기
4. `/speckit-plan` + 아래 "계획에 줄 기술 설명"
5. `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge` (Converged까지 반복)
6. 로컬 검사가 통과하면 PR을 `develop`으로. 본문에 요구사항 ID를 적고 `specs/` 문서도 함께 올린다

## 계획에 줄 기술 설명

`/speckit-plan` 뒤에 그대로 붙여 넣습니다.

```
OpenAPI 3.1 YAML(openapi/<서버>.yaml), JSON Schema 2020-12(diagnostics/, events/), 예시는 examples/에. 검사는 CI '계약 검사'와 같은 yamllint·check-jsonschema·redocly lint. codes.yaml 값을 enum으로 참조하고 복사하지 않는다.
```

## 꼭 지킬 것

- 계약(API·이벤트·진단 JSON·코드 값)을 바꿔야 하면 코드를 고치지 말고 멈추고 사람에게 알린다.
- 비밀번호·토큰·키·학번을 코드·문서·커밋에 넣지 않는다. 설정은 환경 변수로 받는다.
- 커밋은 `<종류>(<범위>): <내용>`(feat·fix·refactor·test·docs·chore·ci), 문서·PR·주석은 한국어.
- 레포 이름은 `_server`, 클러스터 안 서비스·이미지 이름은 `-server`(예: `auth-server`).
