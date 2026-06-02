"""점수 엔진 — 신호 → 7축 점수 (glass box: 모든 점수가 근거로 분해).

설계 근거: design/05 (경제 3성분 × 제어루프), design/02 (가중치·게이트).
  레버리지(D1·D3·D4·D6) × 신뢰(D2·D5) ^ 복리(D7).
Week 1 = 결정적 축(D1·D4·D6·D7)만 채점. 신뢰·컨텍스트(D2·D3·D5)는 LLM 필요 → 'pending'.
임계치(anchors)는 전부 코드에 노출 — 권위가 아니라 반증 가능한 공개 가설.
"""

# 등급 경계 (모든 축 공통: 체계화된 자율성↑)
LEVELS = [(80, "L4 시스템화"), (60, "L3 자율"), (40, "L2 도구사용"),
          (20, "L1 보조"), (0, "L0 부재")]


def _interp(v, anchors):
    """anchors=[(x,y)...] 오름차순. 선형보간 + clamp. (임계치 = 공개 가설)"""
    if v <= anchors[0][0]:
        return float(anchors[0][1])
    if v >= anchors[-1][0]:
        return float(anchors[-1][1])
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        if x0 <= v <= x1:
            f = (v - x0) / (x1 - x0) if x1 > x0 else 0
            return y0 + f * (y1 - y0)
    return float(anchors[-1][1])


def _level(score):
    for thr, name in LEVELS:
        if score >= thr:
            return name
    return "L0 부재"


def _axis(score, status, signals, evidence, confidence="high"):
    return {
        "score": round(score) if score is not None else None,
        "level": _level(score) if score is not None else None,
        "status": status,            # 'scored' | 'pending'
        "confidence": confidence,    # 'high' | 'low' (측정 신뢰도)
        "signals": signals,
        "evidence": evidence,        # 사람이 읽는 근거(glass box)
    }


def compute(tx, git, cfg):
    """tx=transcript aggregate, git=repo, cfg=config scan → 7축 + 종합."""
    axes = {}

    # ---- D1 위임 고도 (레버리지) : 프롬프트당 도구 + 자율연쇄 ----
    tpp = tx.get("tools_per_prompt", 0)
    chain = tx.get("max_autonomous_chain", 0)
    s_tpp = _interp(tpp, [(1, 15), (3, 35), (6, 55), (10, 72), (16, 88), (25, 95)])
    s_chain = _interp(chain, [(1, 10), (5, 40), (15, 65), (40, 82), (90, 95)])
    d1 = 0.6 * s_tpp + 0.4 * s_chain
    axes["D1"] = _axis(d1, "scored",
        {"tools_per_prompt": tpp, "max_chain": chain},
        [f"프롬프트당 도구 {tpp}회", f"최대 자율 연쇄 {chain}스텝"])

    # ---- D4 오케스트레이션 (레버리지) : 도구 다양성 + 에이전트 + 빌드설정 ----
    dt = tx.get("distinct_tools", 0)
    orch = tx.get("orchestration_calls", 0)
    cfg_orch = cfg.get("global_hooks", 0) + cfg.get("project_hooks", 0) + cfg.get("mcp_servers", 0) + cfg.get("agents", 0)
    s_div = _interp(dt, [(1, 10), (3, 30), (6, 55), (10, 75), (15, 88)])
    floor = 70 if orch >= 5 else (58 if orch >= 1 else 0)
    bonus = _interp(cfg_orch, [(0, 0), (2, 4), (6, 9), (15, 14)])
    d4 = min(98, max(s_div, floor) + bonus)
    axes["D4"] = _axis(d4, "scored",
        {"distinct_tools": dt, "orchestration_calls": orch, "config_orch": cfg_orch},
        [f"도구 종류 {dt}종", f"에이전트·워크플로 호출 {orch}회",
         f"hook·MCP·agent 설정 {cfg_orch}개"])

    # ---- D6 반복·폐기 (레버리지) : 폐기율 + 정정 - 반복땜질 (신뢰도 낮음) ----
    churn = git.get("churn_ratio", 0) if git.get("available") else 0
    interrupts = tx.get("total_interrupts", 0)
    repeated = tx.get("repeated_edit_sessions", 0)
    s_churn = _interp(churn, [(0, 30), (0.3, 50), (0.6, 65), (1.0, 72)])
    penalty = _interp(repeated, [(0, 0), (3, 8), (10, 18)])
    d6 = max(15, min(85, s_churn + min(interrupts, 5) * 2 - penalty))
    axes["D6"] = _axis(d6, "scored",
        {"churn_ratio": churn, "interrupts": interrupts, "repeated_edit_sessions": repeated},
        [f"git 폐기율(del/add) {churn}", f"중단·재지시 {interrupts}회",
         f"반복 편집 세션 {repeated}개(↓)",
         "⚠ 결정적 측정 한계: docs형 repo는 churn이 낮아 과소평가 가능 — Week2 재생성 패턴으로 보정"],
        confidence="low")

    # ---- D7 자산 복리화 (복리, ★최강 결정신호) : 빌드 자산 + 메모리 ----
    assets = cfg.get("build_assets", 0)
    s_assets = _interp(assets, [(0, 12), (2, 35), (5, 55), (10, 72), (20, 88), (40, 95)])
    mem_bonus = (6 if cfg.get("has_memory_index") else 0) + (4 if cfg.get("has_global_claude_md") else 0) + (4 if cfg.get("has_project_claude_md") else 0)
    d7 = min(98, s_assets + mem_bonus)
    axes["D7"] = _axis(d7, "scored",
        {"build_assets": assets, "memory_files": cfg.get("memory_files", 0)},
        [f"빌드 자산(skill·hook·MCP·command·agent) {assets}개",
         f"메모리 파일 {cfg.get('memory_files', 0)}개",
         "계층 메모리 인덱스 보유" if cfg.get("has_memory_index") else "메모리 인덱스 없음"])

    # ---- D2·D3·D5 : LLM 판단 필요 → Week 2 ----
    for ax, name in [("D2", "검증·신뢰"), ("D3", "컨텍스트"), ("D5", "한계 운전")]:
        axes[ax] = _axis(None, "pending", {}, [f"{name}: LLM-judge 필요(Week 2)"])

    # ---- 종합 (결정적 축만, 잠정) ----
    leverage = round((axes["D1"]["score"] + axes["D4"]["score"] + axes["D6"]["score"]) / 3)
    compounding = axes["D7"]["score"]
    # 스펙트럼 위치(따라하기 쉬움 0 ↔ 따라잡기 어려움 100). 신뢰축 빠져 잠정.
    spectrum = round(0.45 * leverage + 0.55 * compounding)

    # 신뢰 축(D2)이 미측정이면 — 이론상 신뢰가 레버리지를 *곱하는* 게이트이므로
    # 해자(MOAT) 확정 불가. '함정형 false-positive'를 우리가 먼저 차단.
    trust_pending = any(axes[a]["status"] == "pending" for a in ("D2",))
    if trust_pending:
        verdict = {"label": "잠정", "en": "PROVISIONAL",
                   "plain": "레버리지·복리는 측정됨 — 검증(신뢰) 축 측정 후 해자 확정"}
    else:
        verdict = _verdict(spectrum)

    return {
        "axes": axes,
        "leverage_index": leverage,        # D1·D4·D6 (D3 보류)
        "compounding_index": compounding,   # D7
        "spectrum_provisional": spectrum,   # 신뢰축(D2) 측정 후 확정
        "verdict": verdict,
        "trust_pending": trust_pending,
        "note": "신뢰·컨텍스트 축(D2·D3·D5)은 Week 2 LLM 채점 전 — 본 점수는 잠정.",
    }


def _verdict(spectrum):
    # 무용어 라벨 (design/06): 누구나 ↔ 당신만의 무기
    if spectrum >= 75:
        return {"label": "내 무기", "en": "MOAT", "plain": "따라잡기 어려운 당신만의 방식"}
    if spectrum >= 55:
        return {"label": "발전 중", "en": "EMERGING", "plain": "무기가 되어가는 중 — 한 끗 남음"}
    if spectrum >= 35:
        return {"label": "누구나", "en": "COMMODITY", "plain": "도구 바뀌면 리셋되는 수준"}
    return {"label": "입문", "en": "NOVICE", "plain": "이제 도구를 쓰기 시작"}
