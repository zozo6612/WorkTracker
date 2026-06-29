import streamlit as st
import json
from database.db import add_history, get_history
from components.ai_summary import extract_keywords

def render():
    st.title("Work History")
    st.caption("메신저·메일·회의 이력을 기록하고 AI로 키워드를 정리해요")

    # 입력 폼
    with st.expander("+ 새 이력 추가", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            h_type = st.selectbox("유형", ["메신저", "이메일", "구두/회의", "기타"])
        with col2:
            h_date = st.date_input("날짜")
        with col3:
            h_title = st.text_input("제목 (선택)")

        h_content = st.text_area("내용", height=120, placeholder="대화 내용, 이메일 본문 등을 입력하세요...")

        col_ai, col_save = st.columns([1, 1])
        with col_ai:
            if st.button("✦ AI 키워드 요약"):
                if h_content:
                    with st.spinner("키워드 분석 중..."):
                        keywords = extract_keywords(h_content)
                        st.session_state["keywords_preview"] = keywords
        with col_save:
            if st.button("저장", type="primary"):
                kw = json.dumps(st.session_state.get("keywords_preview", []), ensure_ascii=False)
                add_history(h_type, str(h_date), h_title, h_content, kw)
                st.success("저장됐어요!")
                st.rerun()

    # 필터 + 목록
    col1, col2, col3 = st.columns(3)
    with col1:
        f_year = st.selectbox("연도", ["2025", "2024"])
    with col2:
        f_month = st.selectbox("월", ["전체"] + [f"{i:02d}월" for i in range(1, 13)])
    with col3:
        f_type = st.selectbox("유형 필터", ["전체", "메신저", "이메일", "구두/회의", "기타"])

    month_val = None if f_month == "전체" else f_month[:2]
    type_val = None if f_type == "전체" else f_type
    rows = get_history(f_year, month_val, type_val)

    for row in rows:
        kws = json.loads(row.get("keywords") or "[]")
        with st.container(border=True):
            st.markdown(f"**{row['type']}** · {row['date']}  {row.get('title','')}")
            st.write(row["content"])
            if kws:
                st.markdown(" ".join([f"`#{k}`" for k in kws]))
                