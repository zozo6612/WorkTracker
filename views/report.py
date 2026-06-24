import streamlit as st
from database.db import get_work
from utils.ppt_export import create_ppt
from components.ai_summary import generate_weekly_report

def render():
    st.title("주간 보고서")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        week_label = st.selectbox("주차 선택", ["2025년 3주차 (1/13~1/19)", "2025년 2주차 (1/6~1/12)"])
    with col2:
        author = st.text_input("작성자", "홍길동 / 기획팀")

    work_list = get_work()
    sections = {"done": [], "ing": [], "issue": [], "plan": []}
    for w in work_list:
        sections[w["status"]].append(w)

    label_map = {"done": "✅ 완료한 업무", "ing": "🔄 진행중인 업무",
                 "issue": "⚠️ 이슈/리스크", "plan": "📅 다음주 계획"}

    # 보고서 본문
    for key in ["done", "ing", "issue", "plan"]:
        st.markdown(f"#### {label_map[key]}")
        if sections[key]:
            for item in sections[key]:
                prog = f" ({item['progress']}% 완료)" if key == "ing" else ""
                st.markdown(f"- **{item['title']}**{prog}  \n  {item.get('description','')}")
        else:
            st.caption("해당 없음")
        st.divider()

    # 액션 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 텍스트 복사"):
            st.toast("클립보드에 복사됐어요!")
    with col2:
        layout = st.selectbox("PPT 형식", ["summary", "detail", "gantt"],
                               format_func=lambda x: {"summary":"요약형(1장)","detail":"상세형(4장)","gantt":"간트포함"}[x])
    with col3:
        ppt_bytes = create_ppt(work_list, week_label, author, layout)
        st.download_button(
            "📥 PPT 다운로드",
            data=ppt_bytes,
            file_name=f"주간보고서_{week_label[:10]}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        