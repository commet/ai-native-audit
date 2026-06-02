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
├── ainative/               # Week 1 MVP (Python, stdlib only, 로컬 전용)
│   ├── parse_transcript.py  # 세션 JSONL → 위임·오케스트레이션·반복 신호
│   ├── parse_git.py         # repo → 폐기율·정정·커밋규율
│   ├── scan_config.py       # ~/.claude·.claude 인벤토리 → 빌드자산(D4·D7)
│   ├── metrics.py           # 신호 → 7축 점수 (glass box, 임계치 공개)
│   ├── report.py            # → 자기완결 HTML(인라인 SVG)
│   └── cli.py               # ainative scan / report
└── design/                  # 01 rubric · 02 scoring · 03 instrumentation
                             # 04 positioning · 05 도출·타당도 · 06 시각화
```

> Patient-zero = 본인(프리랜서 AI 컨설턴트, Claude Code 1인 운영). 첫 dogfooding 대상.

## 써보기 (30초, 로컬·네트워크 0)
```bash
# Claude Code를 써온 머신에서 (Python 3.9+)
python -m ainative scan      # ~/.claude/projects 분석 → ainative_result.json
python -m ainative report    # report.html 생성 후 브라우저로 열기
#   옵션: --repo <git경로>  --transcripts <경로>  --no-open
```
원문 transcript·코드는 기기를 떠나지 않음. 리포트엔 점수·신호 숫자만.

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

**락된 결정 (2026-06-01):**
- **HTML-first.** 3표면: ① 수집·트리거=터미널(로컬·마찰0) / ② 정독=브라우저 `report.html`(진짜 비주얼=hero) / ③ 공유·증명=웹 카드(opt-in, 점수만, 직후 단계).
- **판정 무용어화**: "해자/MOAT" 용어 X → **"남들이 따라할 수 있나?" 스펙트럼 띠**(따라하기 쉬움 ↔ 당신만의 무기) + 내 마커 + "다음 한 끗" 처방. (design/06)
- **MVP = ①② 로컬만** (계정·호스팅 0). dogfooding으로 본인 실제 점수 확인 → 그다음 ③ 공유카드.
- 비주얼 = SVG(브라우저). 터미널은 한 줄 글랜스만.

**설계가 확정한 기술 플랜 반영 3가지 (코딩 시 반드시):**
1. scoring = 가산 평균 X, **곱셈 게이트**(신뢰가 레버리지를 곱함). `metrics.py`.
2. 모든 축 **L4 = "build 증거" 필수** (정적 스캔 hook/skill/MCP/룰 인벤토리). `scan_config.py` 1급.
3. **glass-box 강제** — 모든 점수가 인용 근거(실제 transcript/git 인스턴스)로 분해. 신뢰=제품.

**✅ Week 1 MVP 완료 (2026-06-02)** — 본인 62개 세션으로 검증:
- 파이프라인 end-to-end 작동: `scan`(transcript+git+config → 7축) → `report`(SVG HTML).
- 결정적 축 채점: D1 위임·D4 오케스트레이션·D6 반복(저신뢰)·D7 복리.
- ★ 정직성 게이트: 신뢰축(D2) 미측정이면 **MOAT 단정 안 함 → "잠정(PROVISIONAL)"**. (우리 이론의 '함정형 false-positive' 자가 차단.)
- glass-box: 모든 점수가 근거로 분해(`<details>` 클릭), 임계치는 `metrics.py`에 공개.

**▶ 다음 (Week 2):**
- LLM-judge로 D2 검증·D3 컨텍스트·D5 한계운전 채점 → 스펙트럼·해자 판정 확정.
- 처방 엔진(본인 로그 인스턴스 3개 인용 + 7일 측정).
- 그 후 Week3 hook 실시간+plugin / Week4 반증·시계열 / ③ 공유 카드.
- 결정 대기: 채점 hero visual은 design/06에서 **스펙트럼+처방 우선으로 확정** (잔여는 세부 폴리시).
