# -*- coding: utf-8 -*-
"""그림 모음 — 대학 지도(해도 느낌의 위경도 평면 지도), 직업 흐름 지도(전공 → 기술 → 연구소), 성장 막대.

지도는 바깥 타일·토큰 없이 Natural Earth 해안선(data/korea_outline.json)을 Plotly 평면에 그린다.
위도 1°를 경도 1°보다 1/cos(36°)배 길게 그려 한반도 모양이 찌그러지지 않게 한다.
"""
import math

import plotly.graph_objects as go

# ── 색 (app.py의 CSS 토큰과 같은 값) ──
SEA, PAPER, INK, INK2, LINE = "#EDF4F5", "#FFFFFF", "#102A38", "#4A6573", "#BFD6DC"
TIDE, BUOY, CHIP, NEIGH = "#0F7C8C", "#E2552B", "#DCEBEE", "#DCE6E8"
# 묶음 4개 = 순서가 있는 범주 → 한 색(바닷물)의 진함으로만 순서를 보인다 (검증: 단조 밝기·인접 차이·밝은 끝 대비 통과)
TIER_COLORS = ["#0A4B57", "#0F7C8C", "#3A9DAB", "#73B8C2"]
FONT = "IBM Plex Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif"
MONO = "IBM Plex Mono, ui-monospace, monospace"
LAT_SCALE = 1 / math.cos(math.radians(36))

# 도시 이름 — (이름, 경도, 글자 위도). 학교 점과 겹치지 않게 점 아래·바다 쪽으로 조금씩 옮겨 둠
CITIES = [("대전", 127.38, 36.20), ("대구", 128.60, 35.72), ("부산", 129.00, 34.93), ("광주", 126.85, 35.01),
          ("울산", 129.47, 35.60), ("춘천", 127.73, 37.73), ("강릉", 128.90, 37.60), ("전주", 127.15, 35.67),
          ("청주", 127.49, 36.49), ("제주", 126.53, 33.35), ("포항", 129.36, 35.87), ("목포", 126.39, 34.60),
          ("진주", 128.11, 34.98)]


def _rings_xy(rings):
    xs, ys = [], []
    for ring in rings:
        xs += [p[0] for p in ring] + [None]
        ys += [p[1] for p in ring] + [None]
    return xs, ys


def short_name(u):
    """'서울대학교' → '서울대', 'GIST 광주과학기술원' → 'GIST', '국립부경대학교' → '부경대'."""
    if u.split()[0].isascii():
        return u.split()[0]
    s = u.replace("국립", "").replace("여자대학교", "여대").replace("과학기술대학교", "과기대").replace("공과대학교", "공대")
    return s.replace("대학교", "대")


def _hover(r, tier_name):
    depts = "<br>".join("· " + d["name"] for d in r["depts"])
    where = " · ".join(x for x in (r["campus"], r["region"]) if x)
    return f"<b>{r['univ']}</b><br><span style='font-size:11px'>{where} · {tier_name}</span><br>{depts}"


def korea_map(univs, outline, tiers, kwater, *, x_range, y_range, height, zoom=False, box=None, dim=None):
    """univs: 화면에 보일 학교 목록(dict), dim: 흐리게 둘 학교 index 집합(필터에서 빠진 곳)."""
    fig = go.Figure()
    for key in ("chn", "jpn", "prk"):
        xs, ys = _rings_xy(outline[key])
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=NEIGH,
                                 line=dict(color=NEIGH, width=0.5), hoverinfo="skip", showlegend=False))
    xs, ys = _rings_xy(outline["kor"])
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=PAPER,
                             line=dict(color="#9CC3CB", width=1), hoverinfo="skip", showlegend=False))

    if box:   # 본 지도 위에 '수도권 확대' 범위를 점선 상자로
        (x0, x1), (y0, y1) = box
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1, line=dict(color=INK2, width=1, dash="dot"))
        fig.add_annotation(x=x0, y=y1, text="서울 확대 →", showarrow=False, xanchor="right", yanchor="bottom",
                           font=dict(size=11, color=INK2, family=FONT))

    if not zoom:   # 도시 이름 — 흐린 글씨, 점과 겹치지 않게 아래쪽
        fig.add_trace(go.Scatter(x=[c[1] for c in CITIES], y=[c[2] for c in CITIES], mode="text",
                                 text=[c[0] for c in CITIES], textfont=dict(size=10, color="#7C97A3", family=FONT),
                                 hoverinfo="skip", showlegend=False))

    dim = dim or set()
    tier_name = {t["id"]: t["name"] for t in tiers}
    for ti, t in enumerate(tiers):
        rows = [(i, r) for i, r in enumerate(univs) if r["tier"] == t["id"]]
        for faded in (True, False):
            sel = [(i, r) for i, r in rows if (i in dim) == faded]
            if not sel:
                continue
            fig.add_trace(go.Scatter(
                x=[r["lon"] for _, r in sel], y=[r["lat"] for _, r in sel],
                mode="markers+text" if zoom else "markers",
                text=[short_name(r["univ"]) + ("(ERICA)" if "ERICA" in r["campus"] else "") for _, r in sel] if zoom else None,
                textposition=[_label_pos(r) for _, r in sel] if zoom else None,
                textfont=dict(size=10, color=INK2 if faded else INK, family=FONT),
                marker=dict(size=[(9 + 3 * len(r["depts"])) * (1.25 if zoom else 1) for _, r in sel],
                            color=TIER_COLORS[ti], opacity=0.18 if faded else 0.95,
                            line=dict(color=PAPER, width=1.5)),
                name=t["name"], legendgroup=t["id"], showlegend=not faded and not zoom,
                customdata=[i for i, _ in sel],
                hovertext=[_hover(r, tier_name[r["tier"]]) for _, r in sel], hoverinfo="text",
            ))

    if kwater:
        fig.add_trace(go.Scatter(
            x=[kwater["lon"]], y=[kwater["lat"]], mode="markers+text", text=[kwater["name"]],
            textposition="middle right", textfont=dict(size=11, color=BUOY, family=FONT),
            marker=dict(symbol="star", size=17, color=BUOY, line=dict(color=PAPER, width=1.5)),
            name="K-water연구원", showlegend=not zoom, hovertext=[f"<b>{kwater['name']}</b><br>{kwater['note']}"],
            hoverinfo="text"))

    grid = dict(showgrid=True, gridcolor="#D3E3E7", griddash="dot", gridwidth=1, zeroline=False,
                showline=False, ticks="", tickfont=dict(size=9, color="#86A0AB", family=MONO), fixedrange=False)
    step = 0.05 if zoom else 1
    xt = [round(math.floor(x_range[0] / step) * step + k * step, 2) for k in range(int((x_range[1] - x_range[0]) / step) + 3)]
    yt = [round(math.floor(y_range[0] / step) * step + k * step, 2) for k in range(int((y_range[1] - y_range[0]) / step) + 3)]
    xt = [v for v in xt if x_range[0] < v < x_range[1] and (zoom or float(v).is_integer())]
    yt = [v for v in yt if y_range[0] < v < y_range[1] and (zoom or float(v).is_integer())]
    fig.update_xaxes(range=x_range, tickvals=xt, ticktext=[f"{v:g}°E" for v in xt], constrain="domain", **grid)
    fig.update_yaxes(range=y_range, tickvals=yt, ticktext=[f"{v:g}°N" for v in yt], scaleanchor="x",
                     scaleratio=LAT_SCALE, constrain="domain", **grid)
    fig.update_layout(
        height=height, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor=PAPER, plot_bgcolor=SEA,
        font=dict(family=FONT, color=INK), dragmode="pan", hovermode="closest", clickmode="event+select",
        hoverlabel=dict(bgcolor=INK, font=dict(color=PAPER, family=FONT, size=12), bordercolor=INK, align="left"),
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", bgcolor="rgba(255,255,255,0)",
                    font=dict(size=11), itemclick="toggle", itemdoubleclick="toggleothers", itemsizing="constant"),
    )
    return fig


# 수도권 확대 지도에서 이름이 겹치지 않게 학교마다 글자 위치를 정함 (없으면 오른쪽)
ZOOM_POS = {
    "연세대학교": "middle left", "이화여자대학교": "middle right", "홍익대학교": "bottom left", "서울대학교": "bottom center",
    "중앙대학교": "middle right", "동국대학교": "bottom center", "국민대학교": "top center", "고려대학교": "middle left",
    "서울시립대학교": "middle right", "광운대학교": "middle left", "서울과학기술대학교": "top right",
    "한양대학교|서울캠퍼스": "bottom center", "건국대학교": "bottom right", "세종대학교": "top right",
    "가천대학교": "middle left",
}


def _label_pos(r):
    return ZOOM_POS.get(r["univ"] + "|" + r["campus"]) or ZOOM_POS.get(r["univ"], "middle right")


def flow_map(tech, highlight=()):
    """직업 흐름 지도 — 공부(전공) → 물 기술 → K-water 연구소. 기술 하나 = 같은 굵기 1, 전공·연구소로 나눠 흐른다."""
    def majors(t):
        return [m.strip().replace("(수자원)", "") for m in t["major"].split(",")]

    def insts(t):
        return [s.strip() for s in t["inst"].split("·")]

    major_nodes = sorted({m for t in tech for m in majors(t)}, key=lambda m: -sum(m in majors(t) for t in tech))
    tech_nodes = [t["name"] for t in tech]
    inst_nodes = sorted({s for t in tech for s in insts(t)})
    labels = major_nodes + tech_nodes + inst_nodes
    idx = {n: i for i, n in enumerate(labels)}
    src, dst, val, col = [], [], [], []
    for t in tech:
        on = t["id"] in highlight
        c = "rgba(15,124,140,0.55)" if on else "rgba(191,214,220,0.55)"
        for m in majors(t):
            src.append(idx[m]); dst.append(idx[t["name"]]); val.append(1 / len(majors(t))); col.append(c)
        for s in insts(t):
            src.append(idx[t["name"]]); dst.append(idx[s]); val.append(1 / len(insts(t))); col.append(c)
    hl_names = {t["name"] for t in tech if t["id"] in highlight}
    node_col = ([INK2] * len(major_nodes)
                + [BUOY if n in hl_names else TIDE for n in tech_nodes]
                + ["#0A4B57"] * len(inst_nodes))
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=labels, color=node_col, pad=9, thickness=12, line=dict(color=PAPER, width=1),
                  hovertemplate="<b>%{label}</b><extra></extra>"),
        link=dict(source=src, target=dst, value=val, color=col,
                  hovertemplate="%{source.label} → %{target.label}<extra></extra>"),
        textfont=dict(family=FONT, size=12, color=INK),
    ))
    fig.update_layout(height=max(560, 20 * len(major_nodes)), margin=dict(l=8, r=14, t=34, b=8),
                      paper_bgcolor=PAPER, font=dict(family=FONT, color=INK),
                      annotations=[dict(x=x, y=1.05, xref="paper", yref="paper", showarrow=False, text=f"<b>{t}</b>",
                                        font=dict(size=12, color=INK2), xanchor=a)
                                   for x, t, a in ((0, "공부하면 좋은 전공", "left"), (0.5, "지금 뜨는 물 기술", "center"),
                                                   (0.995, "K-water 연구소", "right"))])
    return fig


def growth_bars(tech, baseline, highlight=()):
    rows = sorted([t for t in tech if t.get("a")], key=lambda t: t["b"] / t["a"])
    ratio = [t["b"] / t["a"] for t in rows]
    fig = go.Figure(go.Bar(
        x=ratio, y=[t["name"] for t in rows], orientation="h",
        marker=dict(color=[BUOY if t["id"] in highlight else TIDE for t in rows], line=dict(width=0),
                    cornerradius=4),
        text=[f"{r:.1f}×" for r in ratio], textposition="outside", cliponaxis=False,
        textfont=dict(family=MONO, size=12, color=INK),
        customdata=[[t["a"], t["b"]] for t in rows],
        hovertemplate="<b>%{y}</b><br>%{customdata[0]:,}편('22) → %{customdata[1]:,}편('25)<extra></extra>",
    ))
    fig.add_vline(x=baseline["ratio"], line=dict(color=INK2, width=1.5, dash="dash"))
    fig.add_annotation(x=baseline["ratio"], y=1.02, yref="paper", text=f"전체 논문 {baseline['ratio']}×", showarrow=False,
                       xanchor="left", font=dict(size=11, color=INK2, family=MONO))
    fig.update_xaxes(range=[0, 12.6], ticksuffix="×", gridcolor="#E3EDF0", zeroline=False, tickfont=dict(family=MONO))
    fig.update_yaxes(tickfont=dict(size=13))
    fig.update_layout(height=40 * len(rows) + 70, margin=dict(l=8, r=40, t=30, b=8), bargap=0.42,
                      paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=dict(family=FONT, color=INK), showlegend=False,
                      hoverlabel=dict(bgcolor=INK, font=dict(color=PAPER, family=FONT)))
    return fig
