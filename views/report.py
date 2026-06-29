import streamlit as st
from database.db import get_work, get_history
from utils.ppt_export import create_ppt
from components.ai_summary import generate_weekly_report, generate_ai_todo

STATUS_LABELS = {"done": "완료한 업무", "ing": "진행중인 업무", "issue": "이슈/리스크", "plan": "다음주 계획"}
STATUS_EMOJI  = {"done": "✅", "ing": "🔄", "issue": "⚠️", "plan": "📅"}


def render():
    st.title("📊 주간 보고서")
    st.caption("등록된 업무를 기반으로 주간 보고서를 자동 생성합니다")

    col1, col2 = st.columns(2)
    with col1:
        week_label = st.text_input("보고 기간", "2025년 3주차 (1/13 ~ 1/19)")
    with col2:
        author = st.text_input("작성자", "홍길동 / 기획팀")

    all_work    = get_work()
    all_history = get_history()

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

    col1, col2, col3 = st.columns(3)
    with col1:
        report_text = "\n\n".join([
            f"[{STATUS_LABELS[k]}]\n" + (
                "\n".join(
                    f"- {w['title']}" + (f" ({w['description']})" if w.get("description") else "")
                    for w in sections[k]
                ) if sections[k] else "해당 없음"
            )
            for k in ["done", "ing", "issue", "plan"]
        ])
        st.download_button(
            "📋 텍스트 다운로드",
            report_text,
            file_name="주간보고서.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        layout = st.selectbox(
            "PPT 형식",
            ["summary", "detail"],
            format_func=lambda x: {"summary": "요약형 (1장)", "detail": "상세형 (4장)"}[x]
        )
    with col3:
        ppt_bytes = create_ppt(all_work, week_label, author, layout)
        st.download_button(
            "📥 PPT 다운로드",
            data=ppt_bytes,
            file_name=f"주간보고서_{week_label[:8]}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True
        )