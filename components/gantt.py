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


def date_to_num(d: datetime) -> float:
    """날짜를 숫자(일 단위)로 변환"""
    epoch = datetime(1970, 1, 1)
    return (d - epoch).days


def _parse_period(mode: str, period: str):
    """mode에 따라 차트 표시 구간(시작·종료)을 반환합니다."""
    if mode == "week":
        year = int(period.split("-")[0]) if "-" in period else int(period)
        start = datetime(year, 1, 1)
        end = datetime(year, 12, 31)
        return start, end

    year, month = map(int, period.split("-"))
    start = datetime(year, month, 1)
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    end = datetime(next_year, next_month, 1) - timedelta(days=1)
    return start, end


def _build_week_ticks(period_start: datetime, period_end: datetime):
    """연간 주차별 눈금: 매주 월요일에 W{ISO주차} 라벨."""
    tickvals = []
    ticktext = []

    cur = period_start
    while cur.weekday() != 0:
        cur += timedelta(days=1)

    while cur <= period_end:
        _, iso_week, _ = cur.isocalendar()
        tickvals.append(date_to_num(cur))
        ticktext.append(f"W{iso_week}")
        cur += timedelta(weeks=1)

    return tickvals, ticktext


def _build_day_ticks(period_start: datetime, period_end: datetime):
    """월간 일별 눈금: 매일 MM/DD 라벨."""
    tickvals = []
    ticktext = []
    cur = period_start

    while cur <= period_end:
        tickvals.append(date_to_num(cur))
        ticktext.append(cur.strftime("%m/%d"))
        cur += timedelta(days=1)

    return tickvals, ticktext


def render_gantt(work_list: list, mode: str = "week", period: str = "2026-01"):
    if not work_list:
        fig = go.Figure()
        fig.update_layout(height=200, paper_bgcolor="#ffffff")
        return fig

    period_start, period_end = _parse_period(mode, period)
    ps_num = date_to_num(period_start)
    pe_num = date_to_num(period_end)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    fig = go.Figure()

    visible_works = []
    for w in work_list:
        try:
            start = datetime.strptime(w["start_date"], "%Y-%m-%d")
            end = datetime.strptime(w["end_date"], "%Y-%m-%d")
        except Exception:
            continue
        if end < period_start or start > period_end:
            continue
        visible_works.append(w)

    if not visible_works:
        empty_msg = "이 연도에 해당하는 업무가 없어요" if mode == "week" else "이 월에 해당하는 업무가 없어요"
        fig.add_annotation(
            text=empty_msg,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#94A3B8")
        )
        fig.update_layout(height=200, paper_bgcolor="#ffffff")
        return fig

    for w in visible_works:
        start = datetime.strptime(w["start_date"], "%Y-%m-%d")
        end = datetime.strptime(w["end_date"], "%Y-%m-%d")

        display_start = max(start, period_start)
        display_end = min(end, period_end)

        s_num = date_to_num(display_start)
        duration = date_to_num(display_end) - s_num + 1
        color = STATUS_COLORS.get(w["status"], "#94A3B8")
        label = f"{w['progress']}%" if w.get("progress") and w["status"] != "plan" else ""

        fig.add_trace(go.Bar(
            y=[w["title"]],
            x=[duration],
            base=[s_num],
            orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=label,
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

    if mode == "week":
        tickvals, ticktext = _build_week_ticks(period_start, period_end)
        grid_color = "#e2e8f0"
        grid_width = 1
        tick_font_size = 9
    else:
        tickvals, ticktext = _build_day_ticks(period_start, period_end)
        grid_color = "#f0f4f9"
        grid_width = 0.5
        tick_font_size = 10

    shapes = []
    for tv in tickvals:
        shapes.append(dict(
            type="line",
            x0=tv, x1=tv, y0=0, y1=1, yref="paper",
            line=dict(color=grid_color, width=grid_width, dash="dot")
        ))

    annotations = []
    if period_start <= today <= period_end:
        today_num = date_to_num(today)
        shapes.append(dict(
            type="line",
            x0=today_num, x1=today_num, y0=0, y1=1, yref="paper",
            line=dict(color="#6C8EF5", width=2)
        ))
        annotations.append(dict(
            x=today_num, y=1, yref="paper",
            text="오늘", showarrow=False,
            font=dict(color="#6C8EF5", size=11),
            xanchor="left", yanchor="bottom"
        ))

    fig.update_layout(
        barmode="stack",
        xaxis=dict(
            range=[ps_num, pe_num + 1],
            tickvals=tickvals,
            ticktext=ticktext,
            tickfont=dict(size=tick_font_size),
            showgrid=False,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=12),
        ),
        height=max(300, 80 + len(visible_works) * 45),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8faff",
        font=dict(family="Segoe UI, sans-serif", size=12),
        margin=dict(l=10, r=20, t=20, b=40),
        shapes=shapes,
        annotations=annotations,
    )
    return fig
