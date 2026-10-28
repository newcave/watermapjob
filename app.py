# -*- coding: utf-8 -*-
"""🌊 미래 물 직업 지도 — 학생과 시민을 위한 물 분야 진로 안내 (습작 v0.1)

전 세계 물 연구 논문(OpenAlex)과 국내 학회지(KCI) 집계로 '지금 뜨는 물 기술 10'을 고르고,
그 기술을 하는 직업·공부하면 좋은 전공·K-water 연구소, 그리고 물을 공부할 수 있는 대학을 지도로 보여 준다.

실행: streamlit run app.py
숫자·학교 고치기: data/*.json (화면 코드는 그대로)
"""
import html
import json
import math
import re
from pathlib import Path

import streamlit as st

import viz

APP_VERSION = "v0.2 · 2026-10-28"
DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="미래 물 직업 지도", page_icon="🌊", layout="wide",
                   initial_sidebar_state="collapsed")


@st.cache_data
def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


TECH, KCI, UNIV, ICONS, OUTLINE = (load("tech.json"), load("kci.json"), load("univ.json"),
                                   load("icons.json"), load("korea_outline.json"))
ITEMS = TECH["items"]
esc = html.escape

# ── 모양: 해도(海圖) — 옅은 바다색 바탕, 숫자는 수심 표기처럼 고정폭 ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Do+Hyeon&family=IBM+Plex+Sans+KR:wght@400;500;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
:root {
  --sea:#EDF4F5; --paper:#FFFFFF; --ink:#102A38; --ink-2:#4A6573; --line:#BFD6DC; --tide:#0F7C8C; --buoy:#E2552B; --chip:#DCEBEE;
  --display:"Do Hyeon","IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --body:"IBM Plex Sans KR","Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;
}
html, body, .stApp, .stMarkdown, button, input { font-family: var(--body); }
.stApp { background: var(--sea); color: var(--ink); }
.block-container { max-width: 1120px; padding-top: 1.2rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
.stMarkdown p { margin-bottom: 0; }
.wm h1, .wm h2, .wm h3 { font-family: var(--display); font-weight: 400; letter-spacing: .01em; margin: 0; padding: 0; color: var(--ink); line-height: 1.2; }
.eyebrow { font-family: var(--mono); font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--ink-2); }
.sec { display: grid; gap: 8px; margin: 34px 0 10px; }
.sec h2 { font-size: clamp(1.6rem, 3.2vw, 2.1rem) !important; }
.lede { color: var(--ink-2); max-width: 66ch; margin: 0; font-size: .97rem; }
.num { font-family: var(--mono); font-variant-numeric: tabular-nums; }
/* 머리 */
.hero { position: relative; overflow: hidden; border-radius: 22px; border: 1px solid var(--line); background: var(--paper); }
.hero svg.contour { position: absolute; inset: 0; width: 100%; height: 100%; }
.hero-in { position: relative; display: grid; gap: 14px; padding: clamp(26px, 5vw, 52px) clamp(18px, 5vw, 46px) clamp(22px, 4vw, 38px); }
.hero h1 { font-size: clamp(2.1rem, 6vw, 3.8rem) !important; line-height: 1.1 !important; }
.hero h1 em { font-style: normal; color: var(--tide); }
.hero .sub { margin: 0; max-width: 58ch; color: var(--ink-2); font-size: 1.02rem; }
.sounding { display: flex; flex-wrap: wrap; gap: 10px 22px; align-items: baseline; }
.sounding .big { font-family: var(--mono); font-size: clamp(2.6rem, 8vw, 4.1rem); font-weight: 600; color: var(--buoy); line-height: 1; }
.sounding .cap { max-width: 36ch; font-weight: 500; }
.sounding .cap small { display: block; color: var(--ink-2); font-weight: 400; font-size: .82rem; }
/* 테스트 결과 */
/* 1분 테스트 — 질문마다 한 줄, 선택지는 큰 알약 버튼 */
.st-key-quiz { background: var(--paper); border: 1px solid var(--line); border-radius: 20px; padding: 6px 22px; box-shadow: 0 10px 30px -18px rgba(16,42,56,.35); gap: 0; }
.st-key-qrow1, .st-key-qrow2 { border-top: 1px dashed var(--line); }
.st-key-qrow0, .st-key-qrow1, .st-key-qrow2 { padding: 14px 0; }
.qlab { display: flex; align-items: center; gap: 12px; }
.qn { flex: none; width: 40px; height: 40px; border-radius: 12px; background: var(--chip); color: var(--tide); font-family: var(--mono); font-weight: 600; font-size: .95rem; display: grid; place-items: center; }
.qt { font-family: var(--display); font-size: 1.28rem; line-height: 1.25; color: var(--ink); word-break: keep-all; }
.st-key-quiz [data-testid="stButtonGroup"] { gap: 8px; }
.st-key-quiz [data-testid="stButtonGroup"] button { min-height: 44px; padding: 6px 16px; border-radius: 999px; border: 1.5px solid var(--line); background: var(--sea); color: var(--ink); font-size: .96rem; transition: border-color .15s, background .15s, transform .15s; }
.st-key-quiz [data-testid="stButtonGroup"] button:hover { border-color: var(--tide); color: var(--tide); transform: translateY(-1px); }
.st-key-quiz [data-testid="stButtonGroup"] button[aria-checked="true"],
.st-key-quiz [data-testid="stButtonGroup"] button[aria-checked="true"]:hover { background: var(--tide) !important; border-color: var(--tide) !important; color: #fff !important; box-shadow: 0 6px 14px -8px rgba(15,124,140,.9); }
.st-key-quiz [data-testid="stButtonGroup"] button[aria-checked="true"] * { color: #fff !important; }
.st-key-quiz [data-testid="stButtonGroup"] button p { font-size: .96rem; }
/* 추천 결과 — 바닷물 그러데이션 카드 두 장 */
.match { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 18px; }
.mc { position: relative; overflow: hidden; border-radius: 20px; padding: 18px 20px 16px; display: grid; gap: 12px; align-content: start;
      color: #fff; background: radial-gradient(120% 140% at 100% 0%, #3A9DAB 0%, #0F7C8C 38%, #0A4B57 100%); box-shadow: 0 16px 34px -22px rgba(10,75,87,.9); }
.mc:not(.first) { background: radial-gradient(120% 140% at 100% 0%, #2E7F8E 0%, #0E5E6B 40%, #0B2E3B 100%); }
.mc::after { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .18;
      background: repeating-radial-gradient(circle at 105% -10%, transparent 0 18px, rgba(255,255,255,.55) 18px 19px); }
.mc > * { position: relative; z-index: 1; }
.mc-top { display: flex; justify-content: space-between; align-items: center; }
.rank { font-family: var(--mono); font-size: .74rem; letter-spacing: .12em; background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.35); padding: 3px 10px; border-radius: 999px; }
.grow { font-size: .9rem; font-weight: 600; color: #FFD9C9; }
.mc-body { display: flex; gap: 14px; align-items: center; }
.mc-ill { flex: none; width: 60px; height: 60px; padding: 8px; border-radius: 16px; background: rgba(255,255,255,.12); color: #fff; }
.mc-ill g { fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.mc-ill .f { fill: rgba(255,255,255,.18); } .mc-ill .d { fill: currentColor; stroke: none; }
.mc-job { font-family: var(--display); font-size: 1.65rem; line-height: 1.15; }
.mc-tech { font-size: .88rem; opacity: .85; margin-top: 2px; }
.mc-hits { display: flex; flex-wrap: wrap; gap: 6px; }
.hit { font-size: .8rem; padding: 3px 10px; border-radius: 999px; border: 1px dashed rgba(255,255,255,.35); opacity: .6; }
.hit.on { opacity: 1; border-style: solid; background: rgba(255,255,255,.18); }
.mc-go { justify-self: start; font-size: .85rem; color: #fff !important; text-decoration: none !important; border-bottom: 1px solid rgba(255,255,255,.5); }
.mc-go:hover { border-bottom-color: #fff; }
.tag-ex { font-size: .82rem; color: var(--ink-2); margin: 8px 2px 0 !important; }
/* 기술 카드 */
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.card { background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 18px; display: grid; grid-template-columns: auto 1fr auto; gap: 4px 16px; align-content: start; }
.card.hit { border-color: var(--tide); box-shadow: 0 0 0 2px var(--tide) inset; }
.depth { grid-row: span 3; display: grid; justify-items: center; align-content: start; min-width: 64px; gap: 2px; }
.depth .x { font-family: var(--mono); font-size: 1.55rem; font-weight: 600; color: var(--tide); line-height: 1.1; }
.depth .xl { font-family: var(--mono); font-size: .64rem; color: var(--ink-2); letter-spacing: .06em; text-align: center; }
.card h3 { font-size: 1.42rem !important; grid-column: 2; }
.card .what { color: var(--ink-2); font-size: .92rem; grid-column: 2; margin: 0; }
.ill { grid-column: 3; grid-row: 1 / span 2; width: 58px; height: 58px; color: var(--tide); opacity: .78; }
.ill g { fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.ill .f { fill: var(--chip); } .ill .d { fill: currentColor; stroke: none; }
.facts { grid-column: 1 / -1; display: grid; grid-template-columns: max-content 1fr; gap: 3px 12px; margin: 10px 0 0; padding-top: 10px; border-top: 1px dashed var(--line); font-size: .88rem; }
.facts dt { color: var(--ink-2); } .facts dd { margin: 0; } .facts .job { font-weight: 700; }
.evidence { grid-column: 1 / -1; font-family: var(--mono); font-size: .73rem; color: var(--ink-2); background: var(--chip); border-radius: 8px; padding: 6px 10px; margin-top: 6px; }
/* 국내 */
.kr { display: flex; flex-wrap: wrap; gap: 10px; }
.kr .w { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 8px 12px; display: grid; }
.kr .w b { font-family: var(--display); font-weight: 400; font-size: 1.22rem; }
.kr .w span { font-family: var(--mono); font-size: .73rem; color: var(--ink-2); }
/* 대학 */
.tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }
.tile { background: var(--paper); border: 1px solid var(--line); border-radius: 14px; padding: 10px 14px; }
.tile .v { font-family: var(--mono); font-size: 1.6rem; font-weight: 600; line-height: 1.2; }
.tile .l { font-size: .8rem; color: var(--ink-2); }
.panel { background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 14px 16px; display: grid; gap: 6px; }
.panel h3 { font-size: 1.3rem !important; }
.panel .where { font-family: var(--mono); font-size: .7rem; color: var(--ink-2); }
.tiers { display: grid; gap: 12px; }
.tier { background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 16px 18px; display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 12px 20px; }
.tier-h { display: grid; gap: 4px; align-content: start; border-left: 4px solid var(--tide); padding-left: 12px; }
.tier-h b { font-family: var(--display); font-weight: 400; font-size: 1.26rem; line-height: 1.2; }
.tier-h span { font-size: .8rem; color: var(--ink-2); }
.tier-h .cnt { font-family: var(--mono); font-size: .72rem; }
.unis { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 10px; align-content: start; }
.uni { border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px 11px; display: grid; gap: 6px; align-content: start; background: var(--sea); }
.uni h3 { font-size: 1.08rem !important; }
.uni .where { font-family: var(--mono); font-size: .68rem; color: var(--ink-2); }
.depts { display: flex; flex-wrap: wrap; gap: 6px; }
.dept { font-size: .8rem; line-height: 1.35; padding: 3px 9px; border-radius: 8px; background: var(--paper); border: 1px solid var(--line); color: var(--ink) !important; text-decoration: none !important; }
a.dept { border-color: #87BDC6; } a.dept:hover { border-color: var(--tide); color: var(--tide) !important; }
.dept.off { opacity: .35; }
.note { font-size: .82rem; color: var(--ink-2); margin: 6px 0 0; }
.method { background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 18px; font-size: .88rem; color: var(--ink-2); display: grid; gap: 8px; }
.method p { margin: 0; max-width: 84ch; }
.foot { padding-top: 18px; font-size: .78rem; color: var(--ink-2); }
/* 위젯 */
div[data-testid="stSegmentedControl"] button[aria-checked="true"], div[data-testid="stButtonGroup"] button[kind$="Active"] { background: var(--tide) !important; color: #fff !important; border-color: var(--tide) !important; }
div[data-testid="stPlotlyChart"] { background: var(--paper); border: 1px solid var(--line); border-radius: 16px; padding: 6px; overflow: hidden; }
@media (max-width: 760px) {
  .match, .cards, .tier { grid-template-columns: minmax(0, 1fr); }
  .tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .ill { width: 44px; height: 44px; }
  .uni { display: block; padding: 8px 10px; } .uni h3 { display: inline; } .uni .where { margin-left: 6px; } .uni .depts { margin-top: 5px; }
}
</style>
""", unsafe_allow_html=True)


def md(s):
    st.markdown(f'<div class="wm">{s}</div>', unsafe_allow_html=True)


def section(eyebrow, title, lede=""):
    md(f'<div class="sec"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2>'
       + (f'<p class="lede">{lede}</p>' if lede else "") + "</div>")


def ratio(t):
    return t["b"] / t["a"] if t.get("a") else None


def contour_svg():
    """머리 바탕의 해도 등심선 — 정적 SVG (사인 곡선 16줄)"""
    paths = []
    for k in range(16):
        pts = []
        for px in range(0, 1001, 10):
            u = px / 1000
            y = 340 * (0.10 + k * 0.062) + math.sin(u * 6.1 + k * 0.7) * 10 + math.sin(u * 13.3 + k * 1.9) * 4 + (u - .5) * k * 3.2
            pts.append(f"{px},{y:.1f}")
        op = 0.6 if k % 4 == 0 else 0.28
        paths.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#BFD6DC" stroke-width="1" opacity="{op}"/>')
    return f'<svg class="contour" viewBox="0 0 1000 340" preserveAspectRatio="none" aria-hidden="true">{"".join(paths)}</svg>'


# ── 머리 ──
h = TECH["hero"]
md(f"""<header class="hero">{contour_svg()}<div class="hero-in">
  <span class="eyebrow">미래 물 직업 지도 · 기준 {TECH['as_of'].replace('-', '.')}</span>
  <h1>물 분야에서 <em>지금 뜨는 기술 10</em>,<br>그리고 그 일을 하는 사람들</h1>
  <p class="sub">전 세계 물 연구 논문과 국내 학회지 논문을 세어 봤습니다. 어떤 기술의 논문이 빠르게 늘고 있는지,
  그 기술을 하려면 무엇을 공부하면 좋은지, 어느 대학에서 배울 수 있는지 지도로 모았습니다.</p>
  <div class="sounding"><span class="big num">{h['ratio']}×</span>
    <span class="cap">'{h['text']}' 논문이 3년 만에 {int(h['ratio'])}배로 늘었습니다
      <small>OpenAlex 논문 {h['a']:,}편('22) → {h['b']:,}편('25) · 같은 기간 전체 논문은 {TECH['baseline']['ratio']}배</small></span></div>
</div></header>""")

# ── 1분 테스트 ──
section("1분 테스트", "나에게 맞는 물 기술 찾기", "세 가지를 고르면 잘 맞는 기술 두 개를 골라 드립니다. 아래 지도와 카드에도 표시됩니다.")
EX = TECH["example"]
st.session_state.setdefault("touched", False)


def _touch():
    st.session_state["touched"] = True


# 선택지 앞 작은 그림 — 글자만 있을 때보다 한눈에 고르기 쉽게
EMOJI = {"code": "💻", "science": "🧪", "earth": "🌏", "society": "🏛️", "make": "🛠️", "analyze": "🔬",
         "field": "🧭", "persuade": "📣", "climate": "🌡️", "safe": "🚰", "energy": "⚡", "future": "🚀"}
LABEL = {v: l for q in TECH["quiz"] for v, l in q["opts"]}

pick = {}
with st.container(key="quiz"):
    for n, q in enumerate(TECH["quiz"]):
        with st.container(key=f"qrow{n}"):
            a, b = st.columns([1.25, 2.75], vertical_alignment="center", gap="small")
            a.markdown(f'<div class="qlab"><span class="qn">Q{n + 1}</span><span class="qt">{esc(q["h"])}</span></div>',
                       unsafe_allow_html=True)
            with b:
                # wrap=True: 칸이 좁으면 다음 줄로 넘김 (기본값은 칸 안에서 옆으로 밀려 잘려 보임)
                pick[q["id"]] = st.pills(q["h"], options=[v for v, _ in q["opts"]],
                                         format_func=lambda v: f"{EMOJI.get(v, '')} {LABEL[v]}",
                                         default=EX[q["id"]], required=True, wrap=True,
                                         key=f"q_{q['id']}", on_change=_touch, label_visibility="collapsed")
sel = {k: (v or EX[k]) for k, v in pick.items()}
top = sorted(ITEMS, key=lambda t: -(sum(v in t["tags"] for v in sel.values()) + (ratio(t) or 3) / 100))[:2]
HL = {t["id"] for t in top}
cards = []
for rank, t in enumerate(top, 1):
    r = ratio(t)
    grow = f"{r:.1f}× 성장" if r else "새로 등장"
    chips = "".join(f'<span class="hit{" on" if v in t["tags"] else ""}">{EMOJI.get(v, "")} {esc(LABEL[v])}</span>'
                    for v in sel.values())
    cards.append(f"""<div class="mc{' first' if rank == 1 else ''}">
  <div class="mc-top"><span class="rank">추천 {rank}</span><span class="grow num">{grow}</span></div>
  <div class="mc-body"><svg class="mc-ill" viewBox="0 0 64 64" aria-hidden="true"><g>{ICONS.get(t['id'], '')}</g></svg>
    <div><div class="mc-job">{esc(t['job'].split(' · ')[0])}</div>
    <div class="mc-tech">{esc(t['name'])} · {esc(t['inst'])}</div></div></div>
  <div class="mc-hits">{chips}</div>
  <a class="mc-go" href="#t-{t['id']}">기술 카드 보기 →</a></div>""")
note = "" if st.session_state["touched"] else '<p class="tag-ex">예시 결과예요 — 위에서 직접 골라 보세요</p>'
md(f'<div class="match">{"".join(cards)}</div>{note}')

# ── 직업 흐름 지도 ──
section("job map · 전공 → 기술 → 연구소", "무엇을 공부하면 어떤 물 기술로 이어질까",
        "왼쪽 전공에서 가운데 물 기술로, 다시 오른쪽 K-water 연구소로 이어지는 길입니다. "
        "테스트에서 고른 기술은 주황색으로 표시됩니다. 줄이 여러 기술로 갈라지는 전공일수록 선택지가 넓습니다.")
st.plotly_chart(viz.flow_map(ITEMS, HL), width="stretch", key="flow",
                config={"displayModeBar": False})

# ── 기술 카드 ──
section("10 technologies", "지금 뜨는 물 기술 10",
        f"왼쪽 숫자는 2022년보다 2025년에 논문이 몇 배 나왔는지입니다. 전 세계 논문이 모두 {TECH['baseline']['ratio']}배 늘었으니, "
        "그보다 크면 특히 빠르게 크는 분야입니다.")
html_cards = []
for t in ITEMS:
    r = ratio(t)
    html_cards.append(f"""<article class="card{' hit' if t['id'] in HL else ''}" id="t-{t['id']}">
  <div class="depth"><span class="x">{f'{r:.1f}×' if r else esc(t.get('newBadge', '신규'))}</span>
    <span class="xl">{"'22→'25" if r else '새로 등장'}</span></div>
  <h3>{esc(t['name'])}</h3>
  <svg class="ill" viewBox="0 0 64 64" aria-hidden="true"><g>{ICONS.get(t['id'], '')}</g></svg>
  <p class="what">{esc(t['what'])}</p>
  <dl class="facts"><dt>이런 직업</dt><dd class="job">{esc(t['job'])}</dd>
    <dt>공부하면 좋은 전공</dt><dd>{esc(t['major'])}</dd><dt>K-water에서는</dt><dd>{esc(t['inst'])}</dd></dl>
  <div class="evidence">근거 · {esc(t['ev'])}</div></article>""")
md(f'<div class="cards">{"".join(html_cards)}</div>')

# ── 성장 막대 ──
section("growth · 2022 → 2025", "얼마나 빨리 크고 있나",
        f"막대에 마우스를 올리면 실제 논문 수가 나옵니다. 점선은 전체 논문의 증가({TECH['baseline']['ratio']}배), "
        "주황 막대는 테스트에서 고른 기술입니다.")
st.plotly_chart(viz.growth_bars(ITEMS, TECH["baseline"], HL), width="stretch", key="growth",
                config={"displayModeBar": False})

# ── 국내 ──
section("국내 학회지 · KCI", "우리나라 연구에서는 이런 말이 늘고 있어요",
        f"국내 수자원학회·토목학회 논문 {KCI['n_papers']:,}편(2002~2025)에서 최근 3년에 부쩍 자주 나오는 두 단어 표현입니다. "
        "숫자는 '예전보다 몇 배 자주 나오나'이고, 아직 편수가 적어 참고용입니다.")
md('<div class="kr">' + "".join(f'<div class="w"><b>{esc(k["term"])}</b><span class="num">예전보다 {k["lift"]}배 · 최근 3년 {k["recent_n"]}편</span></div>'
                                for k in KCI["items"]) + "</div>")

# ── 대학 지도 ──
UV, TIERS = UNIV["univs"], UNIV["tiers"]
KIND = {"civil": re.compile(r"토목|건설|사회기반|사회환경|인프라|지역|수자원"), "env": re.compile(r"환경"),
        "sea": re.compile(r"해양|해안|항만")}
KIND_LABEL = {"all": "전체", "civil": "토목·건설환경·수자원", "env": "환경공학", "sea": "해양·해안"}


def kinds(name):
    return {k for k, p in KIND.items() if p.search(name)}


n_uni = len({r["univ"] for r in UV})
n_dept = sum(len(r["depts"]) for r in UV)
section("대학 · 학과 지도", "물을 공부할 수 있는 대학",
        f"토목·건설환경·환경공학처럼 물(수자원·하천·상하수도·수질)을 배우는 학부 학과가 있는 대학 {n_uni}곳(캠퍼스별 {len(UV)}곳), "
        f"학과 {n_dept}개를 학교 누리집과 모집요강에서 확인했습니다. 점이 클수록 물 관련 학과가 많고, 진한 색일수록 앞 묶음입니다. "
        "점을 누르면 학과가 나오고, 학교가 몰린 서울은 오른쪽에 확대해 두었습니다.")
kind = st.segmented_control("학과 종류", options=list(KIND_LABEL), format_func=KIND_LABEL.get, default="all",
                            key="kind") or "all"
match_idx = {i for i, r in enumerate(UV) if kind == "all" or any(kind in kinds(d["name"]) for d in r["depts"])}
dim = set(range(len(UV))) - match_idx
seoul_metro = sum(1 for i in match_idx if UV[i]["region"].split()[0] in ("서울", "경기", "인천"))
md('<div class="tiles">' + "".join(
    f'<div class="tile"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in (
        (len({UV[i]['univ'] for i in match_idx}), "대학"), (len(match_idx), "캠퍼스"),
        (sum(1 for i in match_idx for d in UV[i]['depts'] if kind == 'all' or kind in kinds(d['name'])), "학과"),
        (f"{seoul_metro} : {len(match_idx) - seoul_metro}", "수도권 : 지역 (캠퍼스)"))) + "</div>")

ZX, ZY = (126.875, 127.145), (37.43, 37.665)  # 서울 확대
left, right = st.columns([3, 2], gap="medium")
with left:
    ev_main = st.plotly_chart(
        viz.korea_map(UV, OUTLINE, TIERS, UNIV["kwater"], x_range=(124.6, 130.1), y_range=(33.05, 38.75),
                      height=760, box=(ZX, ZY), dim=dim),
        width="stretch", key="map_main", on_select="rerun", selection_mode="points",
        config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage", "autoScale2d"]})
with right:
    ev_zoom = st.plotly_chart(
        viz.korea_map(UV, OUTLINE, TIERS, None, x_range=ZX, y_range=ZY, height=390, zoom=True, dim=dim),
        width="stretch", key="map_zoom", on_select="rerun", selection_mode="points",
        config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d", "toImage", "autoScale2d"]})

    def _picked(ev):
        try:
            pts = ev["selection"]["points"]
        except (KeyError, TypeError):
            return None
        for p in pts or []:
            cd = p.get("customdata")
            cd = cd[0] if isinstance(cd, list) else cd
            if isinstance(cd, (int, float)) and 0 <= int(cd) < len(UV):
                return int(cd)
        return None

    pick_u = _picked(ev_zoom) if _picked(ev_zoom) is not None else _picked(ev_main)
    if pick_u is None:
        md('<div class="panel"><span class="eyebrow">학교 고르기</span><p class="note" style="margin:0">'
           '지도에서 점을 누르면 이 자리에 학교와 학과가 나옵니다. 마우스를 올려도 볼 수 있어요. '
           '<b style="color:#E2552B">★</b> 은 K-water연구원(대전)입니다.</p></div>')
    else:
        r = UV[pick_u]
        tname = {t["id"]: t["name"] for t in TIERS}[r["tier"]]
        chips = "".join(
            (f'<a class="dept" href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["name"])}</a>' if d["url"]
             else f'<span class="dept">{esc(d["name"])}</span>') for d in r["depts"])
        md(f'<div class="panel"><span class="eyebrow">{esc(tname)}</span><h3>{esc(r["univ"])}</h3>'
           f'<span class="where">{esc(" · ".join(x for x in (r["campus"], r["region"]) if x))}</span>'
           f'<div class="depts">{chips}</div></div>')

# 묶음별 목록 — 순위 없이 묶음 순서, 묶음 안은 가나다순
blocks = []
for i, t in enumerate(TIERS):
    rows = sorted([(j, r) for j, r in enumerate(UV) if r["tier"] == t["id"] and j in match_idx],
                  key=lambda x: (x[1]["univ"][0].isascii(), x[1]["univ"], x[1]["campus"]))   # 가나다 → 영문
    unis = []
    for _, r in rows:
        chips = []
        for d in r["depts"]:
            off = " off" if kind != "all" and kind not in kinds(d["name"]) else ""
            chips.append(f'<a class="dept{off}" href="{esc(d["url"])}" target="_blank" rel="noopener">{esc(d["name"])}</a>'
                         if d["url"] else f'<span class="dept{off}">{esc(d["name"])}</span>')
        where = " · ".join(x for x in (r["campus"], r["region"]) if x)
        unis.append(f'<div class="uni"><h3>{esc(r["univ"])}</h3><span class="where">{esc(where)}</span>'
                    f'<div class="depts">{"".join(chips)}</div></div>')
    body = "".join(unis) or '<p class="note">이 종류의 학과는 이 묶음에 없습니다.</p>'
    blocks.append(f'<div class="tier"><div class="tier-h" style="border-left-color:{viz.TIER_COLORS[i]}">'
                  f'<b>{esc(t["name"])}</b><span>{esc(t["desc"])}</span><span class="cnt">{len(rows)}곳</span></div>'
                  f'<div class="unis">{body}</div></div>')
md('<div class="sec" style="margin-top:22px"><span class="eyebrow">묶음별로 보기</span></div>'
   f'<div class="tiers">{"".join(blocks)}</div>'
   '<p class="note">학과 이름을 누르면 학교 공식 누리집으로 갑니다. 묶음은 입시에서 흔히 쓰는 대략적인 구분이고, '
   '학과의 연구 수준이나 취업 순위가 아닙니다. 같은 묶음 안은 가나다순입니다. 포스텍처럼 물 관련 학과가 대학원에만 있는 곳은 뺐습니다.</p>')

# ── 방법과 출처 ──
section("어떻게 셌나", "방법과 출처")
md(f"""<div class="method">
<p><b>세계 논문 수</b> — OpenAlex(전 세계 학술 논문 데이터베이스)에서 각 키워드가 제목·초록에 들어간 논문을 출판연도별로 셌습니다(2022년 대 2025년). OpenAlex 전체 논문도 같은 기간 {TECH['baseline']['ratio']}배 늘어, 그보다 큰 증가가 '진짜 뜨는' 신호입니다.</p>
<p><b>새로 등장한 오염물질</b> — 수자원 핵심 12개 저널 논문 91,125편(2000~2025)의 제목 단어를 추세검정(Mann-Kendall)과 FDR 보정으로 분석해, 처음 등장한 해와 이후 논문 수를 적었습니다.</p>
<p><b>국내</b> — KCI(한국학술지인용색인) 데이터 활용. 수자원학회·토목학회 논문의 국문 제목·초록을 집계만 했습니다(원문은 싣지 않음).</p>
<p><b>대학·학과</b> — 각 대학의 학과·단과대학·입학처 공식 누리집과 2026~2027학년도 모집요강에서 {UNIV['as_of'][:7].replace('-', '년 ')}월 기준 학부 학과 이름을 확인했습니다. 대학원에만 있는 과정, 건축·조경·도시계획만 다루는 학과, 재직자 과정, 모집이 멈춘 학과는 뺐습니다. 지도의 점은 캠퍼스의 대략 위치입니다. 학과 이름은 해마다 바뀔 수 있으니 지원 전에 학교 누리집에서 다시 확인하세요.</p>
<p><b>지도</b> — 해안선은 Natural Earth(퍼블릭 도메인) 자료입니다.</p>
<p><b>직업 이름과 전공</b>은 이해를 돕기 위한 예시입니다. 실제 직무·학과 이름은 기관과 학교마다 다릅니다.</p>
</div>""")
md(f'<div class="foot">K-water연구원 AI연구소 · 물벗 R&amp;D 에이전트 습작 · 숫자 기준 {TECH["as_of"]} · {APP_VERSION}</div>')
