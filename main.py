import streamlit as st
import importlib.util
import sys
import os
from database.db import init_db

st.set_page_config(
    page_title="WorkTracker",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

def load_page(filename):
    """파일 경로로 직접 모듈을 불러오는 함수"""
    # views 또는 pages 폴더 둘 다 시도
    for folder in ["views", "pages"]:
        path = os.path.join(os.path.dirname(__file__), folder, f"{filename}.py")
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(filename, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    st.error(f"{filename}.py 파일을 찾을 수 없어요. views 또는 pages 폴더를 확인해주세요.")
    return None

with st.sidebar:
    st.markdown("## 📋 WorkTracker")
    st.caption("업무 이력 & 보고서 자동화")
    st.divider()
    page = st.radio(
        "메뉴 선택",
        ["📁 Work History", "💼 My Work", "📊 주간 보고서"],
        label_visibility="collapsed"
    )

if page == "📁 Work History":
    module = load_page("history")
    if module:
        module.render()
elif page == "💼 My Work":
    module = load_page("mywork")
    if module:
        module.render()
elif page == "📊 주간 보고서":
    module = load_page("report")
    if module:
        module.render()
        