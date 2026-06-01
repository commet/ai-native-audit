# AI-Native Audit (가칭) — 개인 AI-nativeness 진단 프로덕트

> **상태**: v0.1 설계 중 (2026-06-01 착수). 특정 클라이언트 프로젝트와 **무관한 독립 프로덕트**.
> **씨앗**: "내가 일하고·사고하고·AI를 활용하는 방식이 *구체적으로* AI-native한가?"라는 질문을 AI 사용자들이 궁금해한다는 통찰.

## 무엇인가
개인이 **실제로** 일하는 방식이 진짜 AI-native한지를 — 설문이 아니라 **관찰된 행동**(Claude Code/대화 transcript, git 패턴, prompt·tool-call 패턴)으로 — 진단하고, 강점/약점을 점수화하고, 더 AI-native해지는 **개인화된** 처방을 주는 도구. 플러그인으로 workflow에 녹임.

## 차별 (보편 조언과 다른 점)
- **개인 단위** (조직 maturity 설문 X)
- **관찰 행동 기반** (자기보고 X)
- **개인화 처방** (보편 조언 X)
- **moat 판정** ("이 수준이 경쟁 해자가 되나")

## 구조 (설계 산출 후 채워짐)
```
ai-native-audit/
├── README.md
├── 00-product-brief.md      # 통합 브리프 (예정)
└── design/
    ├── 01-rubric.md         # 역량 dimension·레벨 (예정)
    ├── 02-scoring.md        # 점수·moat threshold·처방 (예정)
    ├── 03-instrumentation.md# plug-in 수집·측정 (예정)
    └── 04-positioning.md    # 경쟁·wedge·네이밍 (예정)
```

> Patient-zero = 본인(프리랜서 AI 컨설턴트, Claude Code 1인 운영). 첫 dogfooding 대상.

---

## 현재 상태 / 다음에 여기서 재개 (2026-06-01)

**완료 (설계 v0.1):**
- `00-product-brief.md` — 통합 브리프
- `design/01-rubric.md` — 7축(레버리지4·신뢰2·복리1)
- `design/02-scoring.md` — 가중치·moat 3게이트·FP/FN
- `design/03-instrumentation.md` — 수집·MVP·프라이버시
- `design/04-positioning.md` — 경쟁·wedge·네이밍
- `design/05-rubric-derivation-and-validity.md` — ★ 왜 이 기준인가(경제 3성분×제어루프 도출) + 타당도 사다리
- `design/06-scoring-visualization.md` — 채점 hero visual 4안 (**결정 대기**)

**Prior art 결론**: 기존은 다 토큰/비용·모델품질·조직도입. **개인+관찰행동+역량점수+moat판정+처방** 사분면은 비어 있음. (최근접 lucemia/claude-session-analyzer는 같은 신호로 *모델*을 판정, descriptive only.)

**핵심 미결정 2개:**
1. 채점 hero visual: 잠정 **A+C+D 레이어드** (design/06) — 사용자 확인 필요.
2. (없음 — 이론·타당도는 잠김)

**설계가 확정한 기술 플랜 반영 3가지 (코딩 시 반드시):**
1. scoring = 가산 평균 X, **곱셈 게이트**(신뢰가 레버리지를 곱함). `metrics.py`.
2. 모든 축 **L4 = "build 증거" 필수** (정적 스캔 hook/skill/MCP/룰 인벤토리). `scan_config.py` 1급.
3. **glass-box 강제** — 모든 점수가 인용 근거(실제 transcript/git 인스턴스)로 분해. 신뢰=제품.

**▶ 다음 단계 (Week 1 MVP, 아직 코드 0):**
- ① `~/.claude/projects/**/*.jsonl` 실제 스키마 1개 열어 확인 → ② `parse_transcript.py` → ③ `parse_git.py`(--numstat·revert) → ④ `scan_config.py` → ⑤ `metrics.py`(결정적 D1·D4·D6·D7, 곱셈게이트) → ⑥ `report.py`(순수 SVG) → ⑦ 본인 데이터로 첫 실제 자기진단.
- 스택: Python 3 **표준 라이브러리만**, 로컬 전용, 네트워크 0.
- Week2 = LLM-judge(D2·D3·D5)+처방 / Week3 = hook 실시간+plugin / Week4 = 반증·시계열.
