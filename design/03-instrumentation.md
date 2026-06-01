# Design — Instrumentation / Plug-in

설계 원칙: **설문 0개.** 자기보고는 신호로 안 씀. 작업하며 자연히 떨어지는 부산물(transcript·git·tool-call)만 수집. 마찰 1↑ = 채택 절반↓ → "동의 한 번 → 무개입".

## 1. 데이터 소스 평가
| 소스 | 접근성 | 신호 밀도 | 마찰 | 민감도 | MVP |
|---|---|---|---|---|---|
| Claude Code transcript (`~/.claude/projects/**/*.jsonl`) | 높음 | **최상**(prompt·tool_use·result·thinking) | 0 | 높음 | **핵심** (단일로 80%) |
| Claude Code hooks (PreToolUse/PostToolUse/Stop/SessionEnd) | 높음 | 높음(실시간·타이밍) | 낮음(1회) | 높음 | **핵심** |
| git 이력 (log·reflog·diff) | 높음 | 중상(빈도·diff·메시지·revert) | 0 | 중 | **핵심**("실제 land 시키나" 검증) |
| IDE·터미널 활동 (셸 history·확장) | 중 | 중(비-AI 작업 비율 분모) | 중 | 중 | Phase 2 |
| 스크린/시간 로그 | 낮음 | 낮음(노이즈) | **높음** | **최상** | **제외** |
| 타 AI 도구 (ChatGPT/Cursor/Copilot) | 낮음~중 | 높음 | 중 | 높음 | Phase 3 |

핵심: **transcript+hook+git 셋이 로컬에 이미 있고 마찰≈0.** 스크린 로깅은 ROI·동의 측면에서 버림.

## 2. Rubric → 시그널 매핑 (측정 가능성)
- **D1 위임 폭** — tool_use 종류 분포·Task 호출·멀티스텝 비율 (transcript/hook). **상.**
- **D2 위임 깊이/자율성** — turn 사이 자율 체인 길이·turn당 tool_use·interrupt·plan-mode (transcript/hook). **상.**
- **D3 명세 품질** — prompt 길이·구조(제약·예시·성공기준)·재프롬프트까지 turn·첫 시도 성공률 (transcript). **중**(LLM-judge).
- **D4 검증·신뢰 보정** — 산출 후 테스트·diff 리뷰·재질문 비율·맹목 수용 비율 (transcript/git/hook). **중.**
- **D5 반복·수렴 효율** — 목표당 turn·재편집·에러→수정 루프·revert율 (transcript/git). **상.**
- **D6 도구·환경 셋업** — 커스텀 hook·subagent·MCP·command·CLAUDE.md 정교함 (정적 스캔). **상.** *본 제품 자체가 이 축 증거 생성.*
- **D7 AX vs 손작업 비율** — AI 보조 산출 vs 수작업 (git·IDE). **하**(분모 약함, "AI 세션 내"로 정직히 한정).
- **D8 학습·적응 곡선** — 위 지표 시계열 추세 (다주 누적). **중.** *moat 판정 핵심.*

> moat: D1·D2·D6·D8 동시 상위 + D4 보정 = 복제 어려운 워크플로 자본. 단발 고득점은 해자 아님.

## 3. MVP 아키텍처 (전부 로컬)
```
Claude Code ──hook──▶ collector (append JSONL)
~/.claude/projects/*.jsonl ── reader ──┐
git repos ── git log/diff ─────────────┤
~/.claude/ 설정 ── static scan ────────┤
                                       ▼
                              analysis pass (로컬 LLM-judge + 결정적 메트릭)
                                       │
                              report.html (로컬)
        (옵트인 시에만) ──▶ 익명 점수만 클라우드
```

**구현 = Claude Code 플러그인** (설치 한 번):
- (a) Hook 등록(PostToolUse/UserPromptSubmit/Stop) → `~/.ainative/events.jsonl` **append만**(수 ms, 분석은 hook 밖).
- (b) Transcript reader — hook="지금부터", reader="지금까지". 공백 0.
- (c) git collector — `log --numstat`·revert/reset 탐지·메시지. 읽기 전용.
- (d) 정적 스캔 — `~/.claude/`·프로젝트 `.claude/`에서 hook·subagent·MCP·command·CLAUDE.md 인벤토리 → D6 즉시.
- (e) Analysis pass — ① 결정적 메트릭(turn·tool 분포·체인·revert·재편집, 코드, LLM 불필요) ② LLM-as-judge(명세 품질·검증 분류만, **로컬 모델 우선** Ollama / 아니면 사용자 자기 키).

스택: `ainative` CLI(MVP Python, hook 핫패스만 경량) + 로컬 SQLite + 원본 JSONL 보존 + 정적 HTML 리포트(서버 X) + Claude Code plugin 패키징.

## 4. 프라이버시·동의·로컬 우선
- **로컬 우선·기본 오프라인**: 원시 데이터 절대 기기 안 떠남. 클라우드는 명시 옵트인 시 **점수·메트릭(숫자)만**.
- **명시 동의 1회 + 범위 고지**(`ainative init`이 읽는 경로·안 보내는 것 명시). 동의 없이 미작동.
- **로컬 LLM-judge 우선**, 외부 API는 "당신 키로 당신이 호출", 제품 중개 X.
- **레다션**(secret·PII 마스킹) + **사용자 소유·`ainative purge` 단일 삭제** + **gitignore·secret 제외** + **collector 오픈소스**(검증 가능).

## 5. "Workflow에 녹인다" UX
- 수집은 항상·수동적·비가시(hook append 수 ms, 팝업 0).
- 리포트는 당겨서(`ainative report`) 또는 옵트인 주간 1회 한 줄 알림. 흐름 차단 0.
- 처방은 구체·개인화("지난주 `auth.ts` 7회 재편집—매번 부분 명세; 첫 prompt에 실패 케이스 3개 줬다면 평균 2.1왕복 절감").
- 개입은 옵트인 nudge로만(기본 꺼짐 — 잔소리 제품 방지).
- **자기 자신이 D6 증거**: 이 플러그인 설치·hook 구성 행위 자체가 점수에 반영.

## 부록: 정직한 한계
- D7(AX 비율) 분모 약함 → "AI 세션 내"로 범위 한정.
- 멀티툴 사용자 과소측정 → Phase 3 커넥터 전까지 "단일툴 편향" 명시.
- LLM-judge 재현성·편향 → 결정적 메트릭 1차, 판단 항목 보조+신뢰구간.
- moat 판정은 D8 시계열 충분히 쌓여야 유효(1주는 스냅샷).
