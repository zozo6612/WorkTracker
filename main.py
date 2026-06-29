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

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #1a1a2e !important;
    }
    [data-testid="stSidebar"] * {
        color: #8892b0;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2d2d4e !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
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

init_db()

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
    is_active = st.session_state["current_page"] == page_key
    if st.sidebar.button(
        label,
        key=f"nav_{page_key}",
        type="primary" if is_active else "secondary",
        use_container_width=True
    ):
        st.session_state["current_page"] = page_key
        st.rerun()


with st.sidebar:
    st.markdown("""
        <div style='padding: 0 8px 20px;'>
            <div style='font-size:18px;font-weight:700;color:#ffffff;'>
                📋 WorkTracker
            </div>
            <div style='font-size:12px;color:#8892b0;margin-top:4px;'>
                업무 이력 & 보고서 자동화
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav_button("📁  Work History", "history")
    nav_button("💼  My Work",      "mywork")
    nav_button("📊  주간 보고서",   "report")


page   = st.session_state["current_page"]
module = load_page(page)
if module:
    module.render()