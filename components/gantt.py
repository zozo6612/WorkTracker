import plotly.graph_objects as go
from datetime import datetime, timedelta

STATUS_COLORS = {
    "done":  "#22c55e",
    "ing":   "#6C8EF5",
    "issue": "#f43f5e",
    "plan":  "#94A3B8",
}
STATUS_LABELS = {
    "done":  "완료",
    "ing":   "진행중",
    "issue": "이슈/리스크",
    "plan":  "다음주 계획",
}


def render_gantt(work_list: list, mode: str = "week", ym: str = "2025-01"):
    if not work_list:
        fig = go.Figure()
        fig.update_layout(height=200, paper_bgcolor="#ffffff")
        return fig

    year, month = map(int, ym.split("-"))
    month_start = datetime(year, month, 1)
    next_month  = month + 1 if month < 12 else 1
    next_year   = year if month < 12 else year + 1
    month_end   = datetime(next_year, next_month, 1) - timedelta(days=1)

    fig = go.Figure()

    for w in work_list:
        try:
            start = datetime.strptime(w["start_date"], "%Y-%m-%d")
            end   = datetime.strptime(w["end_date"],   "%Y-%m-%d")
        except Exception:
            continue

        color    = STATUS_COLORS.get(w["status"], "#94A3B8")
        duration = (end - start).days + 1

        fig.add_trace(go.Bar(
            name=STATUS_LABELS.get(w["status"], w["status"]),
            y=[w["title"]],
            x=[duration],
            base=[start.strftime("%Y-%m-%d")],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=f"{w['progress']}%" if w.get("progress") and w["status"] != "plan" else "",
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=(
                f"<b>{w['title']}</b><br>"
                f"기간: {w['start_date']} ~ {w['end_date']}<br>"
                f"진행률: {w.get('progress', 0)}%<br>"
                f"상태: {STATUS_LABELS.get(w['status'], w['status'])}"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    # 주차별 구분선
    if mode == "week":
        cur = datetime(month_start.year, month_start.month, month_start.day)
        while cur.weekday() != 0:
            cur += timedelta(days=1)
        while cur <= month_end:
            fig.add_vline(
                x=cur.timestamp() * 1000,
                line_dash="dot",
                line_color="#e2e8f0",
                line_width=1
            )
            cur += timedelta(weeks=1)
    else:
        # 일별 구분선
        cur = datetime(month_start.year, month_start.month, month_start.day)
        while cur <= month_end:
            fig.add_vline(
                x=cur.timestamp() * 1000,
                line_dash="dot",
                line_color="#f0f4f9",
                line_width=0.5
            )
            cur += timedelta(days=1)

    # 오늘 표시선
    today = datetime.today()
    if month_start <= today <= month_end:
        fig.add_vline(
            x=today.timestamp() * 1000,
            line_color="#6C8EF5",
            line_width=2,
            annotation_text="오늘",
            annotation_position="top left",
            annotation_font_color="#6C8EF5",
        )

    fig.update_layout(
        barmode="overlay",
        xaxis=dict(
            type="date",
            range=[
                month_start.strftime("%Y-%m-%d"),
                month_end.strftime("%Y-%m-%d")
            ],
            tickformat="%m/%d",
            dtick="D1" if mode == "day" else "D7",
            gridcolor="#f0f4f9",
            showgrid=True,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12)
        ),
        height=max(250, 60 + len(work_list) * 40),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8faff",
        font=dict(family="Segoe UI, sans-serif", size=12),
        margin=dict(l=10, r=20, t=20, b=30),
    )
    return fig