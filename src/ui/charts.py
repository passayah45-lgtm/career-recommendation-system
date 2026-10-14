# Plotly figure builders that take rows from views.py
# Kept free of Streamlit so they can be tested on their own
# Colors and fonts come from src/ui/theme.py so charts match the rest of the app

import plotly.graph_objects as go

from src.ui.theme import BORDER, COMPONENT_COLORS, COVERAGE_COLORS, LEVEL_PALETTE, NAVY, TEAL, TEXT_MUTED

PRIMARY = TEAL
FONT = dict(family="Source Sans Pro, Segoe UI, Arial, sans-serif", size=13, color=TEXT_MUTED)


def _layout(fig, title, x_title, y_title, height=380):
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=16, color=NAVY)),
        xaxis_title=x_title, yaxis_title=y_title, height=height, font=FONT,
        margin=dict(l=10, r=20, t=56, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=fig.layout.showlegend, bargap=0.35,
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=BORDER, font=dict(color=NAVY, size=13)),
    )
    fig.update_xaxes(gridcolor="#E6EBF2", zerolinecolor=BORDER, linecolor=BORDER)
    fig.update_yaxes(gridcolor="#E6EBF2", zerolinecolor=BORDER, linecolor=BORDER)
    return fig


def bar_chart(rows, x, y, title, x_title=None, y_title=None, horizontal=False, colors=None):
    # x_title names the category axis and y_title the value axis, in both orientations
    # colors is an optional list cycled over the bars, otherwise every bar uses the primary teal
    x_title = x if x_title is None else x_title
    y_title = y if y_title is None else y_title
    xs = [r[x] for r in rows]
    ys = [r[y] for r in rows]
    marker = [colors[i % len(colors)] for i in range(len(rows))] if colors else PRIMARY
    if horizontal:
        fig = go.Figure(go.Bar(x=ys, y=xs, orientation="h", marker_color=marker, text=ys, textposition="outside",
                               cliponaxis=False, hovertemplate=f"%{{y}}<br>{y}: %{{x}}<extra></extra>"))
        fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
        return _layout(fig, title, y_title, x_title, height=max(320, 28 * len(rows) + 90))
    fig = go.Figure(go.Bar(x=xs, y=ys, marker_color=marker, text=ys, textposition="outside", cliponaxis=False,
                           hovertemplate=f"%{{x}}<br>{y}: %{{y}}<extra></extra>"))
    return _layout(fig, title, x_title, y_title)


def contribution_chart(rows, title="Score contributions by component"):
    # Horizontal stacked bars, one per recommended career
    careers = list(dict.fromkeys(r["Career"] for r in rows))
    fig = go.Figure()
    for component, color in COMPONENT_COLORS.items():
        points = {r["Career"]: r["Points"] for r in rows if r["Component"] == component}
        fig.add_trace(go.Bar(name=component.capitalize(), y=careers, x=[points.get(c, 0) for c in careers],
                             orientation="h", marker_color=color,
                             hovertemplate=f"%{{y}}<br>{component.capitalize()}: %{{x:.1f}} points<extra></extra>"))
    fig.update_layout(barmode="stack", showlegend=True,
                      legend=dict(orientation="h", y=-0.2, x=0, title=dict(text="")))
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(range=[0, 100])
    return _layout(fig, title, "Compatibility score (0 to 100)", "", height=max(320, 50 * len(careers) + 140))


def coverage_chart(gap, height=380):
    # Required, preferred and overall coverage from analyze_skill_gap()
    labels, values = [], []
    for label, key in (("Required", "required_coverage"), ("Preferred<br>(optional)", "preferred_coverage"),
                       ("All listed<br>skills", "overall_skill_coverage")):
        if gap.get(key) is not None:
            labels.append(label)
            values.append(round(gap[key] * 100, 1))
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=COVERAGE_COLORS[: len(values)],
                           text=[f"{v:.0f}%" for v in values], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}: %{y:.0f}% of skills<extra></extra>"))
    fig.update_yaxes(range=[0, 110], ticksuffix="%")
    return _layout(fig, f"Skill coverage for {gap['career_title']}", "", "Coverage", height=height)


def donut_chart(rows, label_key, value_key, title, center_text=None, colors=LEVEL_PALETTE):
    # Donut with a legend that shows each value, total in the middle
    labels = [r[label_key] for r in rows]
    values = [r[value_key] for r in rows]
    total = sum(values)
    fig = go.Figure(go.Pie(
        labels=[f"{lab} ({val})" for lab, val in zip(labels, values)], values=values, hole=0.62, sort=False,
        direction="clockwise", marker=dict(colors=colors[: len(rows)], line=dict(color="#FFFFFF", width=2)),
        textinfo="none", hovertemplate="%{label}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=12)),
                      annotations=[dict(text=center_text or f"<b>{total}</b>", x=0.5, y=0.5, showarrow=False,
                                        font=dict(size=18, color=NAVY))])
    return _layout(fig, title, "", "", height=340)
