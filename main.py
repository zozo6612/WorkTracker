import streamlit as st
import importlib.util
import os
from database.db import init_db

st.set_page_config(
    page_title="WorkTracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 자동 페이지 감지 비활성화를 위한 CSS + 사이드바 버튼 스타일
st.markdown("""
<style>
    /* 자동 생성된 상단 페이지 메뉴 숨기기 */
    [data-testid="stSidebarNav"] {display: none !important;}

    /* 사이드바 버튼 스타일 */
    .nav-btn {
        display: block;
        width: 100%;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-radius: 10px;
        border: none;
        background: transparent;
        color: #8892b0;
        font-size: 14px;
        font-weight: 500;
        text-align: left;
        cursor: pointer;
        transition: all 0.15s;
    }
    .nav-btn:hover {
        background: rgba(108,142,245,0.1);
        color: #fff;
    }
    .nav-btn.active {
        background: rgba(108,142,245,0.2);
        color: #fff;
        border-left: 3px solid #6C8EF5;
    }

    /* Streamlit 기본 버튼을 nav 스타일로 덮어쓰기 */
    div[data-testid="stSidebar"] .stButton button {
        display: block;
        width: 100%;
        padding: 12px 16px;
        margin-bottom: 6px;
        border-radius: 10px;
        border: none !important;
        background: transparent !important;
        color: #8892b0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-align: left !important;
        cursor: pointer;
        transition: all 0.15s;
        box-shadow: none !important;
    }
    div[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(108,142,245,0.1) !important;
        color: #fff !important;
    }

    /* 선택된 버튼 강조 */
    div[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: rgba(108,142,245,0.2) !important;
        color: #fff !important;
        border-left: 3px solid #6C8EF5 !important;
        border-radius: 0 10px 10px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# session_state로 현재 페이지 관리
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "history"


def load_page(filename):
    for folder in ["views", "pages"]:
        path = os.path.join(os.path.dirname(__file__), folder, f"{filename}.py")
        if os.path.exists(path):
            spec   = importlib.util.spec_from_file_location(filename, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    st.error(f"{filename}.py 파일을 찾을 수 없어요.")
    return None


def nav_button(label, page_key):
    """현재 페이지면 primary, 아니면 secondary 버튼"""
    is_active = st.session_state["current_page"] == page_key
    if st.sidebar.button(
        label,
        key=f"nav_{page_key}",
        type="primary" if is_active else "secondary",
        use_container_width=True
    ):
        st.session_state["current_page"] = page_key
        st.rerun()


# 사이드바
with st.sidebar:
     st.markdown("""
    <style>
        /* 사이드바 배경 네이비로 변경 */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] * {
        color: #8892b0;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2d2d4e !important;
    }

    /* 자동 생성된 상단 페이지 메뉴 숨기기 */
    [data-testid="stSidebarNav"] {display: none !important;}

    /* 비활성 버튼 */
    div[data-testid="stSidebar"] .stButton button {
        display: block;
        width: 100%;
        padding: 12px 16px;
        margin-bottom: 6px;
        border-radius: 10px;
        border: 1px solid #2d2d4e !important;
        background: transparent !important;
        color: #8892b0 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        text-align: left !important;
        cursor: pointer;
        transition: all 0.15s;
        box-shadow: none !important;
    }
    div[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(108,142,245,0.1) !important;
        color: #ffffff !important;
        border-color: #6C8EF5 !important;
    }

    /* 활성 버튼 (현재 페이지) */
    div[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background: rgba(108,142,245,0.2) !important;
        color: #ffffff !important;
        border-left: 3px solid #6C8EF5 !important;
        border-top: 1px solid #2d2d4e !important;
        border-right: 1px solid #2d2d4e !important;
        border-bottom: 1px solid #2d2d4e !important;
        border-radius: 0 10px 10px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

    st.divider()

    nav_button("📁  Work History",  "history")
    nav_button("💼  My Work",       "mywork")
    nav_button("📊  주간 보고서",    "report")

# 페이지 라우팅
page = st.session_state["current_page"]
module = load_page(page)
if module:
    module.render()