import streamlit as st

def init_session_state():
    """初始化session state"""
    if "selected_node" not in st.session_state:
        st.session_state.selected_node = 8001
    if "selected_config" not in st.session_state:
        st.session_state.selected_config = None
    if "expanded_cats" not in st.session_state:
        st.session_state.expanded_cats = {}

def render_sidebar():
    """渲染共享侧边栏"""
    init_session_state()
    
    with st.sidebar:
        pass
