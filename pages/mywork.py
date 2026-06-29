import streamlit as st
from database.db import add_work, get_work
from components.gantt import render_gantt

def render():
    st.title("My Work")

    # 업무 입력 폼
    with st.expander("+ 업무 추가"):
        col1, col2, col3 = st.columns(3)
        with col1:
            w_title = st.text_input("업무명 *")
        with col2:
            w_status = st.selectbox("상태", ["ing", "done", "issue", "plan"],
                                    format_func=lambda x: {"ing":"진행중","done":"완료","issue":"이슈/리스크","plan":"다음주 계획"}[x])
        with col3:
            w_prog = st.number_input("진행률 %", 0, 100, 0)

        col4, col5 = st.columns(2)
        with col4:
            w_start = st.date_input("시작일")
        with col5:
            w_end = st.date_input("종료(예정)일")
        w_desc = st.text_area("메모", height=80)

        if st.button("저장", type="primary"):
            add_work(w_title, w_status, str(w_start), str(w_end), w_prog, w_desc)
            st.success("업무가 추가됐어요!")
            st.rerun()

    # 통계 카드
    all_work = get_work()
    col1, col2, col3, col4 = st.columns(4)
    for col, key, label in zip([col1,col2,col3,col4],
                                ["done","ing","issue","plan"],
                                ["완료","진행중","이슈/리스크","다음주 계획"]):
        with col:
            cnt = sum(1 for w in all_work if w["status"] == key)
            st.metric(label, cnt)

    # 간트차트
    st.subheader("간트차트")
    col_mode, col_month = st.columns(2)
    with col_mode:
        mode = st.radio("보기 모드", ["주차별", "일별"], horizontal=True)
    with col_month:
        ym = st.selectbox("월 선택", ["2025-01", "2025-02", "2025-03"])

    fig = render_gantt(all_work, "week" if mode == "주차별" else "day", ym)
    st.plotly_chart(fig, use_container_width=True)

    # 업무 목록
    for w in all_work:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{w['title']}**")
                st.caption(f"{w['start_date']} ~ {w['end_date']}  |  {w.get('description','')}")
            with col2:
                st.markdown(f"`{w['status']}`")
            if w["status"] != "plan":
                st.progress(w["progress"] / 100)
                