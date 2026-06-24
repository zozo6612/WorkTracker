import streamlit as st
import json
import datetime
from database.db import add_history, get_history, delete_history
from components.ai_summary import extract_keywords


def render():
    st.title("📁 Work History")
    st.caption("메신저·메일·회의 이력을 기록하고 AI로 키워드를 정리해요")

    with st.expander("+ 새 이력 추가", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            h_type = st.selectbox("유형", ["메신저", "이메일", "구두/회의", "기타"])
        with col2:
            h_date = st.date_input("날짜", datetime.date.today())
        with col3:
            h_title = st.text_input("제목 (선택)")

        h_content = st.text_area("내용", height=120,
                                  placeholder="대화 내용, 이메일 본문, 회의 내용 등을 입력하세요...")

        col_ai, col_save = st.columns(2)
        with col_ai:
            if st.button("✦ AI 키워드 요약", use_container_width=True):
                if h_content.strip():
                    with st.spinner("Claude가 키워드를 분석 중..."):
                        kws = extract_keywords(h_content)
                        st.session_state["kw_preview"] = kws
                else:
                    st.warning("내용을 먼저 입력해주세요.")
        with col_save:
            if st.button("💾 저장", type="primary", use_container_width=True):
                if h_content.strip():
                    kw_json = json.dumps(
                        st.session_state.get("kw_preview", []), ensure_ascii=False
                    )
                    add_history(h_type, str(h_date), h_title, h_content, kw_json)
                    st.session_state.pop("kw_preview", None)
                    st.success("저장됐어요!")
                    st.rerun()
                else:
                    st.warning("내용을 입력해주세요.")

        if "kw_preview" in st.session_state:
            st.markdown("**AI 추출 키워드 미리보기:**  " +
                        " ".join([f"`#{k}`" for k in st.session_state["kw_preview"]]))

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        f_year = st.selectbox("연도", ["2026", "2025", "2024"])
    with col2:
        months = ["전체"] + [f"{i:02d}" for i in range(1, 13)]
        f_month = st.selectbox("월", months,
                                format_func=lambda x: "전체" if x == "전체" else f"{int(x)}월")
    with col3:
        f_type = st.selectbox("유형 필터", ["전체", "메신저", "이메일", "구두/회의", "기타"])

    month_val = None if f_month == "전체" else f_month
    type_val  = None if f_type  == "전체" else f_type
    rows = get_history(f_year, month_val, type_val)

    st.caption(f"총 {len(rows)}건")

    type_icons = {"메신저": "🟣", "이메일": "🟠", "구두/회의": "🟢", "기타": "⚪"}

    for row in rows:
        kws = json.loads(row.get("keywords") or "[]")
        with st.container(border=True):
            col_info, col_del = st.columns([9, 1])
            with col_info:
                st.markdown(
                    f"{type_icons.get(row['type'], '⚪')} **{row['type']}** &nbsp;·&nbsp; "
                    f"`{row['date']}` &nbsp; **{row.get('title', '(제목 없음)')}**"
                )
                st.write(row["content"])
                if kws:
                    st.markdown(" ".join([f"`#{k}`" for k in kws]))
            with col_del:
                if st.button("🗑", key=f"del_h_{row['id']}"):
                    delete_history(row["id"])
                    st.rerun()
