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
