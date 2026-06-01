# Product Brief v0.1 — 개인 AI-Nativeness 진단 (작업명: Telltale / Moat)

> 2026-06-01 설계 workflow 산출 통합본 (rubric·scoring·instrumentation·positioning 4축 병렬 설계 → 통합).
> 상세 설계 = `design/01~04`.

## 0. 설계 충돌 해결 (먼저 결정)

1. **Dimension 수: rubric 7축 vs scoring 6축 vs instrumentation 8축.** rubric의 7축이 가장 행동-흔적 정합적이고 자기기만 함정까지 정의돼 있어 **rubric 7축을 정본(canonical)으로 채택**. scoring 6축은 7축에 매핑, instrumentation의 D7(AX비율)·D8(시계열)은 "축"이 아니라 **측정 레이어 / moat 신호**로 강등(D7은 분모 약해 비-채점 보조, D8은 moat 게이트 시간축 입력). 본 brief는 **rubric 번호만 사용**.
2. **moat 게이트 축 번호 재정렬** → 검증=D2, 컨텍스트=D3, 자산복리=D7 중심(5장).
3. scoring D5 Orchestration ↔ rubric D4, scoring D1 ↔ rubric D1 = 동일축, 번호만 정리.

## 1. 문제 · 인사이트 (한 줄)
**AI를 "잘 쓴다"는 자기보고와 "많이 쓴다"는 사용량은 둘 다 AI-nativeness의 거짓 대리지표다. 진짜는 transcript·git·tool-call에 남은 *행동의 형태*(위임 고도·선택적 검증·컨텍스트 설계·자산 복리)에서만 보인다 — 그리고 그 형태가 모방 가능한지가 곧 해자 여부다.**

비-제너릭 통찰 3개:
- **양(volume)은 native의 반증일 수 있다.** 같은 일을 10번 prompt = 미숙함.
- **보이는 능력(도구·위임량)은 해자가 아니다.** 누구나 도달. 해자는 *안 보이는* 검증·컨텍스트·복리.
- **거의 모든 자기기만 = "분량/빈도를 수준으로 착각".** 그래서 채점은 분량 아닌 *구조·선택성·재사용*만.

## 2. 누구를 위한 것 · JTBD
**P0 (wedge = patient-zero): 1인/소수 AI-레버리지 프리랜서·솔로 빌더.** AI-nativeness가 곧 단가·수주 경쟁력, 데이터(Claude Code transcript·git)가 이미 손에 있음.
> JTBD: "내가 AI로 1인 운영하는 방식이 흉내 못 낼 해자인지, 누구나 따라잡는 수준인지 알고, 약점을 콕 집어 다음 주에 고치고 싶다."

확장: **P1** AI-forward 시니어 IC(이직·승진 증거, self-serve) → **P2** EM/AI-enablement(팀, 객단가, "코칭" 프레임 강제) → **P3** 부트캠프(white-label before/after).

## 3. 핵심 차별 (4-요소 곱 wedge)
| wedge | 메우는 맹점 |
|---|---|
| 개인 단위 | 조직 maturity — 개인이 평균에 묻힘 |
| 관찰된 행동 기반 | 설문·자기보고 — 주장이지 행동 아님 |
| 개인화 처방 | 일반 maturity 단계 — 처방이 뻔함 |
| moat 판정 | 사용량·생산성 메트릭이 답 못 하는 질문 |

> 포지셔닝: *"설문이 아니라 당신이 AI와 실제로 남긴 흔적으로, 당신의 일하는 방식이 경쟁 해자가 될 만큼 AI-native한지 진단하고 다음 한 수를 처방한다."*

## 4. Rubric v0.1 — 7 dimension (정본)
모든 시그널 = transcript/git/파일시스템/설정파일 흔적으로 측정 가능. "응답"이 아니라 "흔적"만 채점. 각 축 L0–L4, 0–100.

| # | Dimension | 정의 | 핵심 자기기만 |
|---|---|---|---|
| D1 | 위임 고도 | AI에 넘기는 작업 추상화 수준 | 분량을 고도로 착각 |
| D2 | 검증·불신 설계 | 틀릴 곳에 *선택적* 검증 배치 | 그럴듯한 톤에 설득; 산문·수치 무검증 |
| D3 | 컨텍스트 엔지니어링 | 무엇을 보여주고 숨길지 설계·영속화 | 긴 프롬프트=좋은 컨텍스트 착각 |
| D4 | 루프·도구 오케스트레이션 | AI를 도구 쥔 실행 에이전트로 운용 | 매 스텝 hand-holding=L2 |
| D5 | 모델 right-sizing·한계 운전 | 모델 능력 곡선에 맞춰 분해·우회 | 능력 경계 모름 |
| D6 | 반복 속도·폐기 비용 | 틀린 산출 미련 없이 버리고 재생성 | 첫 산출 정착·손수정=속도 착각 |
| D7 | 자산 복리화 | 일회성→재사용 자산(스킬·훅·규칙·메모리) | 파일 많음=자산화 착각 |

> consume vs build는 별도 축 아니라 **각 축 L4 천장**(build/originate 흔적 게이트).

## 5. Scoring · Moat Threshold
종합은 단순평균 X. 보이지 않는 축에 가중: **D2 0.22·D3 0.20·D7 0.18·D1 0.15·D6 0.13·D4 0.12.** (D5는 v0.1 종합 가중 제외(0), 프로파일·처방엔 노출 — 미해결 #1.)

**프로파일이 점수보다 중요**: 첨탑형(D2·D3·D7↑=모방 어려움, 더 가치) / 균형형 / 함정형(D1·D4↑·D2↓=빠르게 틀린 것 양산).

**Moat 3-게이트 AND**: G1 분별력 D2≥70 AND D3≥70 / G2 복리 D7≥65 / G3 비취약성 최저축≥45 AND D4 비중 상단 아님.
판정: **MOAT**(G1∧G2∧G3, ≈72+) / **EMERGING**(G1 충족·G2 미달) / **COMMODITY**(D1·D4만 높음) / **NOVICE**(다수<40).

**False-positive 안전장치**: FP-1 "많이 쓰는데 안 봄" → `D1_adj = D1×(0.5+0.5·D2/100)` 페널티+COMMODITY 강제. FN-1 "적게 쓰지만 native" 강등 금지. **FN-2 "침묵 검증"**(머릿속·외부 미팅 검증→transcript에 안 남음) → git 정정·외부 산출물 cross-source 보정. *컨설턴트 patient-zero에 직격 = 핵심.*

**처방 = 4요소 필수**: 현재 행동 인용 → 구체 대체 행동 → 측정 지표 → 재측정일. 본인 로그 3개 인용 + 정량 효과.

## 6. Instrumentation MVP
**설문 0개. 동의 1회 → 무개입.** 소스(전부 로컬, 마찰≈0): Claude Code transcript(`~/.claude/projects/**/*.jsonl`, 시그널 80%) + hooks(실시간 append) + git(--numstat·revert) + 정적 스캔(`.claude/`·CLAUDE.md → D4·D7 즉시). 스크린/시간 로깅 **제외**.
분석 2단계: 결정적 메트릭(코드, LLM 불필요) → LLM-as-judge(명세 품질·검증 분류만, **로컬 모델 우선**). 스택: `ainative` CLI(Python) + 로컬 SQLite + 정적 HTML 리포트 + Claude Code plugin. 프라이버시: 원문 기기 안 떠남, 옵트인 시 숫자만, `ainative purge`, collector 오픈소스.

## 7. 포지셔닝 · 네이밍
- **작업명: Telltale**("흔적이 말한다") / 대안 **Moat**(판정 메시지 직결).
- 비즈모델 깔때기: 플러그인+무료 점수 미리보기 → **심층 리포트(처방+moat 판정+4주 플랜) 유료** → 개인 SaaS(시계열·주간 nudge) → B2B 팀 벤치마크 → white-label API.
- 해자 = **데이터 플라이휠**(cohort percentile = 후발 못 따라오는 비교 기준점).
- 메시지: **처방(다음 한 수) 1순위, 점수는 근거.** B2B 개인 랭킹 차단.

## 8. 리스크 (요약)
측정 타당성(점수=가설 라벨·코호트 검증) / 게이밍(패턴 형태라 부풀리기 무력) / 프라이버시(로컬·raw 미전송) / "또 하나의 점수" 피로(처방 1순위) / 차별 침식(cross-tool 중립+cohort+처방 IP) / FN-2 컨설턴트 과소측정(cross-source 기본 내장).

## 9. ★ 빌드 경로 — patient-zero dogfooding MVP (2~4주)
patient-zero = 본인(Claude Code로 멀티위크 컨설팅 분석을 1인 운영). 데이터 이미 있음 → 자기 transcript+git에 바로 진단·검증.

- **Week 1 — 결정적 메트릭 + 정적 스캔 (LLM 없이):** ① JSONL 파서(turn·tool 분포·체인·재편집) → SQLite ② git --numstat+revert 파서(본인 repo 첫 입력, 사실 정정 커밋=D2·D6 ground truth) ③ 정적 스캔(.claude/·CLAUDE.md·MEMORY.md → D4·D7 즉시) ④ D1·D4·D6·D7 raw + 레이더 차트 HTML.
- **Week 2 — LLM-as-judge(D2·D3·D5) + 처방 엔진:** ⑤ transcript 발췌 채점으로 7축 완성 ⑥ 처방 4요소 생성기 ⑦ **자기 진단 1회전** (예상: 종합≈69, 첨탑형 D3·D7강 D2·D4골, EMERGING — D2<70 차단) → construct validity 1차 검증.
- **Week 3 — hook 실시간 + plugin:** ⑧ UserPromptSubmit/PostToolUse/Stop hook → events.jsonl append ⑨ `ainative init`/`report` CLI + plugin 패키징(설치=D7 증거) ⑩ FN-2 보정(git 정정·외부 회의록 cross-source).
- **Week 4 — 검증·반증·시계열:** ⑪ 반증 테스트(합성 transcript로 FP-1/FN-1 발동 확인) ⑫ D8 시계열(5-phase 커밋으로 주차별 추세) ⑬ 자기 진단 리포트 v1 = **첫 마케팅 자산 + 측정 타당성 증거.**

## 10. 미해결 질문 Top 5
1. D5 채점 가능성·가중치 — 독립 축 vs D2/D6 흡수 (v0.2 결정).
2. construct validity — 행동 패턴 ↔ 실제 시장 성과(단가·수주) 상관? (코호트 전까지 "점수=가설" 라벨).
3. moat percentile cold-start — 비교군 부트스트랩(OSS transcript? 합성 페르소나?).
4. LLM-as-judge 재현성·편향 — 결정적 메트릭 커버 범위 + 신뢰구간 노출.
5. 멀티툴 사용자 과소측정 — Claude Code만 보면 병행자 D4·D6 깎임. P1이 진짜 멀티툴이면 wedge 흔들리나?
