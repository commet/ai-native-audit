"""리포트 렌더 — 결과 → 자기완결 HTML(인라인 SVG·CSS, 의존성 0).

hero = "남들이 따라할 수 있나?" 스펙트럼 띠(무용어) + 다음 한 끗.
그 아래 7축(속성 그룹) 막대 + glass-box 근거(<details>). 신뢰축은 'Week2' 회색.
서버 불필요 — file:// 로 그냥 열림. 원문 미포함(점수·신호만).
"""
import html

AX_META = {
    "D1": ("위임 고도", "LEVERAGE"), "D3": ("컨텍스트", "LEVERAGE"),
    "D4": ("오케스트레이션", "LEVERAGE"), "D6": ("반복·폐기", "LEVERAGE"),
    "D2": ("검증·신뢰", "TRUST"), "D5": ("한계 운전", "TRUST"),
    "D7": ("자산 복리화", "COMPOUNDING"),
}
GROUP_ORDER = ["LEVERAGE", "TRUST", "COMPOUNDING"]
GROUP_KO = {"LEVERAGE": "레버리지 (크기)", "TRUST": "신뢰 (부호)", "COMPOUNDING": "복리 (지속)"}
GROUP_COLOR = {"LEVERAGE": "#3b82f6", "TRUST": "#ef4444", "COMPOUNDING": "#f59e0b"}
AX_ORDER = ["D1", "D3", "D4", "D6", "D2", "D5", "D7"]


def _spectrum_svg(pos):
    """0~100 위치 마커가 있는 스펙트럼 띠."""
    W, m, bw, h, y = 720, 60, 600, 22, 46
    x = m + bw * max(0, min(100, pos)) / 100
    ticks = [(12, "입문"), (40, "누구나"), (62, "발전 중"), (88, "내 무기")]
    tk = "".join(
        f'<text x="{m+bw*p/100:.0f}" y="{y+h+18}" fill="#9ca3af" font-size="12" '
        f'text-anchor="middle">{t}</text>' for p, t in ticks
    )
    return f'''<svg viewBox="0 0 {W} 110" width="100%" role="img">
  <defs><linearGradient id="g" x1="0" x2="1">
    <stop offset="0" stop-color="#6b7280"/><stop offset="0.5" stop-color="#3b82f6"/>
    <stop offset="1" stop-color="#10b981"/></linearGradient></defs>
  <text x="{m}" y="28" fill="#6b7280" font-size="13">따라하기 쉬움 (누구나)</text>
  <text x="{m+bw}" y="28" fill="#10b981" font-size="13" text-anchor="end">따라잡기 어려움 (당신만의 무기)</text>
  <rect x="{m}" y="{y}" width="{bw}" height="{h}" rx="11" fill="url(#g)" opacity="0.85"/>
  <polygon points="{x:.0f},{y-8} {x-7:.0f},{y-20} {x+7:.0f},{y-20}" fill="#111827"/>
  <line x1="{x:.0f}" y1="{y}" x2="{x:.0f}" y2="{y+h}" stroke="#111827" stroke-width="2"/>
  <text x="{x:.0f}" y="{y-24}" fill="#111827" font-size="13" font-weight="700" text-anchor="middle">너</text>
  {tk}
</svg>'''


def _bar(ax, axis):
    name, group = AX_META[ax]
    color = GROUP_COLOR[group]
    if axis["status"] == "pending":
        return f'''<div class="row pending">
  <div class="lbl">{ax} {name}</div>
  <div class="track"><div class="fill" style="width:0%"></div></div>
  <div class="val">Week 2 · LLM 측정 전</div></div>'''
    sc = axis["score"]
    ev = " · ".join(html.escape(e) for e in axis["evidence"])
    conf = ' <span class="lowc">측정신뢰↓</span>' if axis.get("confidence") == "low" else ""
    return f'''<details class="row">
  <summary>
    <div class="lbl">{ax} {name}</div>
    <div class="track"><div class="fill" style="width:{sc}%;background:{color}"></div></div>
    <div class="val">{sc} <span class="lv">{html.escape(axis["level"])}</span>{conf}</div>
  </summary>
  <div class="ev">근거: {ev}</div></details>'''


def render_html(result, meta=None):
    meta = meta or {}
    v = result["verdict"]
    pos = result["spectrum_provisional"]
    # 다음 한 끗: 신뢰축이 게이트(Week2) + 결정적 최저축
    scored = {k: a["score"] for k, a in result["axes"].items() if a["status"] == "scored"}
    low_ax = min(scored, key=scored.get) if scored else None
    low_name = AX_META[low_ax][0] if low_ax else ""
    next_step = (f"검증·신뢰(D2)는 Week 2에 측정 — 해자 판정의 핵심 게이트. "
                 f"결정적 축 중엔 <b>{low_ax} {low_name}({scored.get(low_ax)})</b>가 최저.")

    bars = {g: [] for g in GROUP_ORDER}
    for ax in AX_ORDER:
        bars[AX_META[ax][1]].append(_bar(ax, result["axes"][ax]))
    groups_html = ""
    for g in GROUP_ORDER:
        groups_html += (f'<div class="grp"><div class="gh" style="color:{GROUP_COLOR[g]}">'
                        f'{GROUP_KO[g]}</div>{"".join(bars[g])}</div>')

    gen = html.escape(str(meta.get("generated", "")))
    nsess = result.get("axes") and meta.get("n_sessions", "")
    return f'''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI-Native Audit</title>
<style>
*{{box-sizing:border-box}}body{{font:15px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif;
margin:0;background:#f9fafb;color:#111827}}
.wrap{{max-width:760px;margin:0 auto;padding:32px 20px 64px}}
h1{{font-size:20px;margin:0 0 4px}}.sub{{color:#6b7280;font-size:13px;margin-bottom:24px}}
.hero{{background:#fff;border:1px solid #e5e7eb;border-radius:16px;padding:24px 22px;margin-bottom:20px}}
.q{{font-size:17px;font-weight:700;margin-bottom:8px}}
.verdict{{display:inline-block;font-size:22px;font-weight:800;margin:10px 0 2px}}
.chip{{font-size:11px;color:#6b7280;border:1px solid #d1d5db;border-radius:999px;padding:1px 8px;vertical-align:middle;margin-left:6px}}
.plain{{color:#374151;margin-bottom:14px}}
.next{{background:#f3f4f6;border-radius:10px;padding:12px 14px;font-size:14px}}
.grp{{background:#fff;border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;margin-bottom:14px}}
.gh{{font-size:12px;font-weight:800;letter-spacing:.04em;margin-bottom:10px}}
.row{{margin:7px 0}}details.row>summary{{display:flex;align-items:center;gap:12px;cursor:pointer;list-style:none}}
details.row>summary::-webkit-details-marker{{display:none}}
.lbl{{width:150px;font-size:13px;flex:none}}.track{{flex:1;height:9px;background:#eef2f7;border-radius:6px;overflow:hidden}}
.fill{{height:100%;border-radius:6px}}.val{{width:120px;text-align:right;font-size:13px;font-weight:700;flex:none}}
.lv{{font-weight:400;color:#9ca3af;font-size:11px}}.ev{{font-size:12px;color:#6b7280;padding:6px 0 2px 162px}}
.lowc{{color:#d97706;font-size:10px;border:1px solid #fde68a;border-radius:4px;padding:0 4px;margin-left:4px}}
.pending{{display:flex;align-items:center;gap:12px;opacity:.55}}.pending .val{{font-weight:400;color:#9ca3af;font-size:12px}}
.foot{{color:#9ca3af;font-size:12px;margin-top:18px;line-height:1.7}}
</style>
<div class="wrap">
<h1>AI-Native Audit <span class="chip">v0.1 · 잠정</span></h1>
<div class="sub">관찰된 행동(transcript·git·설정)으로 측정 · {gen} · 세션 {html.escape(str(meta.get("n_sessions","-")))}개 · 전부 로컬</div>

<div class="hero">
  <div class="q">당신의 AI 활용 — 남들이 따라할 수 있나?</div>
  {_spectrum_svg(pos)}
  <div class="verdict" style="color:{'#6b7280' if result.get('trust_pending') else (GROUP_COLOR['COMPOUNDING'] if pos>=75 else GROUP_COLOR['LEVERAGE'])}">{html.escape(v["label"])}<span class="chip">{v["en"]}</span></div>
  <div class="plain">{html.escape(v["plain"])} (잠정 {pos}/100)</div>
  <div class="next">▸ 다음 한 끗: {next_step}</div>
</div>

{groups_html}

<div class="foot">
※ <b>점수 = 검증된 척도가 아니라 공개 가설.</b> 모든 점수는 위 '근거'로 분해됨(클릭). 임계치는 코드(metrics.py)에 노출 — 반박 환영.<br>
※ 신뢰·컨텍스트 축(D2·D3·D5)은 LLM 채점 전(Week 2). 스펙트럼 위치는 그 전까지 <b>잠정</b>.<br>
※ 원문 transcript·코드는 기기를 떠나지 않음. 본 리포트엔 점수·신호 숫자만.
</div>
</div></html>'''
