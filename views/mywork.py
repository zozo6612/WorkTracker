import streamlit as st
import datetime
from datetime import datetime as dt
from database.db import add_work, add_work_bulk, get_work, delete_work, get_history
from components.gantt import render_gantt
from components.excel_upload import render_excel_upload
from utils.excel_import import parse_work_excel
from components.ai_summary import generate_ai_todo

STATUS_LABELS = {"done": "완료", "ing": "진행중", "issue": "이슈/리스크", "plan": "다음주 계획"}
STATUS_EMOJI  = {"done": "✅", "ing": "🔄", "issue": "⚠️", "plan": "📅"}


def render():
    st.title("💼 My Work")
    st.caption("업무를 등록하고 간트차트로 일정을 시각화하세요")

    with st.expander("+ 업무 추가", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            w_title = st.text_input("업무명 *")
        with col2:
            w_status = st.selectbox(
                "상태",
                list(STATUS_LABELS.keys()),
                format_func=lambda x: STATUS_LABELS[x]
            )
        with col3:
            w_prog = st.number_input("진행률 %", 0, 100, 0, step=5)

        col4, col5 = st.columns(2)
        with col4:
            w_start = st.date_input("시작일", datetime.date.today())
        with col5:
            w_end = st.date_input("종료(예정)일", datetime.date.today())

        w_desc = st.text_area("메모 (선택)", height=80)

        if st.button("💾 저장", type="primary"):
            if w_title.strip():
                add_work(w_title, w_status, str(w_start), str(w_end), w_prog, w_desc)
                st.success("업무가 추가됐어요!")
                st.rerun()
            else:
                st.warning("업무명을 입력해주세요.")

    with st.expander("📤 Excel 업로드", expanded=False):
        render_excel_upload(
            caption="열: 업무명, 상태, 시작일, 종료일, 진행률, 메모 · .xlsx 형식 · 업무명·시작일·종료일 필수",
            uploader_key="work_excel_upload",
            state_prefix="work_excel",
            parse_fn=parse_work_excel,
            preview_rows_fn=lambda r: {
                "업무명": r["title"],
                "상태": STATUS_LABELS.get(r["status"], r["status"]),
                "시작일": r["start_date"],
                "종료일": r["end_date"],
                "진행률": f"{r.get('progress', 0)}%",
                "메모": (r.get("description") or "")[:60],
            },
            save_fn=add_work_bulk,
        )

    # 통계 카드
    all_work = get_work()
    col1, col2, col3, col4 = st.columns(4)
    for col, key in zip([col1, col2, col3, col4], ["done", "ing", "issue", "plan"]):
        cnt = sum(1 for w in all_work if w["status"] == key)
        col.metric(f"{STATUS_EMOJI[key]} {STATUS_LABELS[key]}", cnt)

    st.divider()

    # 간트차트
    st.subheader("간트차트")
    col_mode, col_period = st.columns([1, 2])
    with col_mode:
        mode = st.radio("보기 모드", ["주차별", "일별"], horizontal=True)

    today = dt.today()
    current_year = today.year
    current_ym = today.strftime("%Y-%m")

    with col_period:
        if mode == "주차별":
            year_options = list(range(current_year - 1, current_year + 3))
            default_year_idx = year_options.index(current_year) if current_year in year_options else 0
            period = str(st.selectbox(
                "연도 선택",
                year_options,
                index=default_year_idx,
                format_func=lambda y: f"{y}년",
            ))
        else:
            month_options = [
                (f"{y}-{m:02d}", f"{y}년 {m}월")
                for y in range(current_year - 1, current_year + 3)
                for m in range(1, 13)
            ]
            option_keys = [m[0] for m in month_options]
            option_labels = {m[0]: m[1] for m in month_options}
            default_idx = option_keys.index(current_ym) if current_ym in option_keys else 0
            period = st.selectbox(
                "월 선택",
                option_keys,
                index=default_idx,
                format_func=lambda x: option_labels[x],
            )

    gantt_mode = "week" if mode == "주차별" else "day"
    fig = render_gantt(all_work, gantt_mode, period)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 업무 목록
    st.subheader("업무 목록")
    f_status = st.selectbox(
        "상태 필터",
        ["전체"] + list(STATUS_LABELS.keys()),
        format_func=lambda x: "전체" if x == "전체" else STATUS_LABELS[x]
    )
    filtered = [w for w in all_work if f_status == "전체" or w["status"] == f_status]

    for w in filtered:
        with st.container(border=True):
            col_title, col_badge, col_del = st.columns([6, 2, 1])
            with col_title:
                st.markdown(f"**{w['title']}**")
                st.caption(f"{w['start_date']} ~ {w['end_date']}   {w.get('description', '')}")
            with col_badge:
                st.markdown(f"{STATUS_EMOJI[w['status']]} `{STATUS_LABELS[w['status']]}`")
            with col_del:
                if st.button("🗑", key=f"del_w_{w['id']}"):
                    delete_work(w["id"])
                    st.rerun()
            if w["status"] != "plan":
                st.progress(w["progress"] / 100, text=f"{w['progress']}%")
    
    
    #AI Todo 생성
    all_work    = get_work()
    all_history = get_history()
    today = dt.today()
    week_label = f"{today.year}-W{today.isocalendar().week}"

    sections = {"done": [], "ing": [], "issue": [], "plan": []}
    for w in all_work:
        sections[w["status"]].append(w)

    st.divider()

    for key in ["done", "ing", "issue", "plan"]:
        st.markdown(f"#### {STATUS_EMOJI[key]} {STATUS_LABELS[key]}")
        if sections[key]:
            for item in sections[key]:
                prog        = f" — {item['progress']}% 완료" if key == "ing" and item.get("progress") else ""
                desc        = f"  \n  └ {item['description']}" if item.get("description") else ""
                issue_badge = " 🔴 **조치필요**" if key == "issue" else ""
                st.markdown(f"- **{item['title']}**{prog}{issue_badge}{desc}")
        else:
            st.caption("해당 없음")
        st.divider()

    st.markdown("""
        <div style='background:linear-gradient(135deg,#f0f4ff,#f8f0ff);
                    border:1.5px solid #c4b5fd;border-radius:12px;
                    padding:16px 20px;margin-bottom:8px;'>
            <div style='font-size:14px;font-weight:700;color:#6C8EF5;margin-bottom:8px;'>
                ✦ To Do (AI 추천)
            </div>
            <div style='font-size:12px;color:#5a4fcf;
                        background:#EEF2FF;border-radius:6px;padding:8px 12px;'>
                🤖 Work History · My Work 데이터를 분석해서 다음 주 우선 처리 항목을 추천해드려요
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✦ AI Todo 생성", type="primary", use_container_width=True):
        with st.spinner("Claude가 업무 데이터를 분석 중이에요..."):
            todos = generate_ai_todo(all_work, all_history, week_label)
            st.session_state["ai_todos"] = todos

    if "ai_todos" in st.session_state:
        todos = st.session_state["ai_todos"]
        if not todos:
            st.info("AI Todo를 생성할 데이터가 부족해요. Work History와 My Work에 내용을 입력해주세요.")
        else:
            priority_config = {
                "긴급": {"bg": "#FFF1F2", "color": "#BE123C"},
                "중요": {"bg": "#FFF7ED", "color": "#C2410C"},
                "일반": {"bg": "#F0FDF4", "color": "#15803D"},
            }
            for todo in todos:
                cfg = priority_config.get(todo.get("priority", "일반"), priority_config["일반"])
                tags_html = "".join([
                    f'<span style="font-size:10px;background:#EEF2FF;color:#4338CA;'
                    f'padding:2px 7px;border-radius:4px;margin-right:4px;">#{t}</span>'
                    for t in todo.get("tags", [])
                ])
                st.markdown(f"""
                    <div style='background:#fff;border:1px solid #e8edf5;
                                border-radius:10px;padding:14px 16px;margin-bottom:10px;'>
                        <div style='display:flex;align-items:flex-start;gap:10px;'>
                            <span style='background:{cfg["bg"]};color:{cfg["color"]};
                                         font-size:10px;font-weight:700;
                                         padding:3px 9px;border-radius:99px;
                                         white-space:nowrap;margin-top:2px;flex-shrink:0;'>
                                {todo.get("priority", "일반")}
                            </span>
                            <div>
                                <div style='font-size:13px;font-weight:600;
                                            color:#1a1a2e;margin-bottom:4px;'>
                                    {todo.get("title", "")}
                                </div>
                                <div style='font-size:12px;color:#718096;line-height:1.6;'>
                                    {todo.get("reason", "")}
                                </div>
                                <div style='margin-top:7px;'>{tags_html}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    st.divider()