import streamlit as st
import datetime
from datetime import datetime as dt
from database.db import add_work, get_work, delete_work
from components.gantt import render_gantt

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

    # 통계 카드
    all_work = get_work()
    col1, col2, col3, col4 = st.columns(4)
    for col, key in zip([col1, col2, col3, col4], ["done", "ing", "issue", "plan"]):
        cnt = sum(1 for w in all_work if w["status"] == key)
        col.metric(f"{STATUS_EMOJI[key]} {STATUS_LABELS[key]}", cnt)

    st.divider()

    # 간트차트
    st.subheader("간트차트")
    col_mode, col_month = st.columns([1, 2])
    with col_mode:
        mode = st.radio("보기 모드", ["주차별", "일별"], horizontal=True)
    with col_month:
        # 현재 연도 기준으로 전년도 ~ 내후년까지 자동 생성
        today        = dt.today()
        current_year = today.year
        current_ym   = today.strftime("%Y-%m")

        month_options = [
            (f"{y}-{m:02d}", f"{y}년 {m}월")
            for y in range(current_year - 1, current_year + 3)
            for m in range(1, 13)
        ]

        option_keys   = [m[0] for m in month_options]
        option_labels = {m[0]: m[1] for m in month_options}

        # 현재 달을 기본값으로
        default_idx = option_keys.index(current_ym) if current_ym in option_keys else 0

        ym = st.selectbox(
            "월 선택",
            option_keys,
            index=default_idx,
            format_func=lambda x: option_labels[x]
        )

    gantt_mode = "week" if mode == "주차별" else "day"
    fig = render_gantt(all_work, gantt_mode, ym)
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