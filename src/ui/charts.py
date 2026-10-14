# Plotly figure builders that take rows from views.py
# Kept free of Streamlit so they can be tested on their own

import plotly.graph_objects as go

PRIMARY = "#2563EB"
COMPONENT_COLORS = {
    "required skills": "#2563EB",
    "preferred skills": "#60A5FA",
    "interests": "#F59E0B",
    "education": "#94A3B8",
}


def _layout(fig, title, x_title, y_title, height=380):
    fig.update_layout(
        title=title, xaxis_title=x_title, yaxis_title=y_title, height=height,
        margin=dict(l=10, r=10, t=50, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=fig.layout.showlegend,
    )
    return fig


def bar_chart(rows, x, y, title, x_title=None, y_title=None, horizontal=False):
    xs = [r[x] for r in rows]
    ys = [r[y] for r in rows]
    if horizontal:
        fig = go.Figure(go.Bar(x=ys, y=xs, orientation="h", marker_color=PRIMARY, text=ys, textposition="outside"))
        fig.update_yaxes(autorange="reversed")
        return _layout(fig, title, y_title or y, x_title or x, height=max(320, 28 * len(rows) + 80))
    fig = go.Figure(go.Bar(x=xs, y=ys, marker_color=PRIMARY, text=ys, textposition="outside"))
    return _layout(fig, title, x_title or x, y_title or y)


def contribution_chart(rows, title="Score contributions by component"):
    # Horizontal stacked bars, one per recommended career
    careers = list(dict.fromkeys(r["Career"] for r in rows))
    fig = go.Figure()
    for component, color in COMPONENT_COLORS.items():
        points = {r["Career"]: r["Points"] for r in rows if r["Component"] == component}
        fig.add_trace(go.Bar(name=component, y=careers, x=[points.get(c, 0) for c in careers],
                             orientation="h", marker_color=color))
    fig.update_layout(barmode="stack", showlegend=True, legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, 100])
    return _layout(fig, title, "Compatibility score (0 to 100)", "", height=max(320, 50 * len(careers) + 120))


def coverage_chart(gap):
    # Required, preferred and overall coverage from analyze_skill_gap()
    labels, values = [], []
    for label, key in (("Required", "required_coverage"), ("Preferred (optional)", "preferred_coverage"),
                       ("All listed skills", "overall_skill_coverage")):
        if gap.get(key) is not None:
            labels.append(label)
            values.append(round(gap[key] * 100, 1))
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=[PRIMARY, "#60A5FA", "#94A3B8"][: len(values)],
                           text=[f"{v}%" for v in values], textposition="outside"))
    fig.update_yaxes(range=[0, 110])
    return _layout(fig, f"Skill coverage for {gap['career_title']}", "", "Coverage (%)")
