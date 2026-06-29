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
        background-color: #1E2A4A !important;
    }
    [data-testid="stSidebar"] * {
        color: #8899CC !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #2d3d66 !important;
        margin: 8px 0 16px !important;
    }
    .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 13px 18px;
        margin-bottom: 8px;
        border-radius: 10px;
        border: 1px solid #2d3d66;
        background: transparent;
        color: #8899CC !important;
        font-size: 20px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
    }
    .nav-item:hover {
        background: #2d4080;
        border-color: #FF8C42;
        color: #ffffff !important;
    }
    .nav-item.active {
        background: rgba(255,140,66,0.15);
        border-left: 3px solid #FF8C42;
        border-top: 1px solid #2d3d66;
        border-right: 1px solid #2d3d66;
        border-bottom: 1px solid #2d3d66;
        border-radius: 0 10px 10px 0;
        color: #FF8C42 !important;
        font-weight: 600;
    }
    .nav-item i {
        font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

init_db()

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "history"

# 쿼리 파라미터로 페이지 전환 처리
params = st.query_params
if "page" in params:
    st.session_state["current_page"] = params["page"]


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


with st.sidebar:
    st.markdown("""
        <div style='padding:0 4px 30px;'>
            <div style='font-size:30px;font-weight:700;color:#ffffff !important;
                        letter-spacing:-0.3px;'>
                📋 WorkTracker
            </div>
            <div style='font-size:18px;color:#6677AA !important;margin-top:5px;'>
                업무 이력 & 보고서 자동화
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    cur = st.session_state["current_page"]

    pages = [
        ("history", "ti-folder",           "Work History"),
        ("mywork",  "ti-briefcase",         "My Work"),
        ("report",  "ti-report-analytics",  "Weekly Report"),
    ]

    for page_key, icon, label in pages:
        active_class = "active" if cur == page_key else ""
        st.markdown(f"""
            <a href="?page={page_key}" target="_self" style="text-decoration:none;">
                <div class="nav-item {active_class}">
                    <i class="ti {icon}" aria-hidden="true"></i>
                    {label}
                </div>
            </a>
        """, unsafe_allow_html=True)


page   = st.session_state["current_page"]
module = load_page(page)
if module:
    module.render()