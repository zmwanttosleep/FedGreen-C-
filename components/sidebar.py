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
        # 底部状态栏
        st.markdown('<hr style="border-color: rgba(0, 255, 136, 0.3); margin: 15px 0;">', unsafe_allow_html=True)
        if st.session_state.selected_config:
            cat, item = st.session_state.selected_config.split("::")
            st.markdown(f"""
            <div style="font-family: 'Orbitron', sans-serif; font-size: 11px; color: #00ff88; 
                        background: rgba(0, 255, 136, 0.1); padding: 8px; border-radius: 6px; 
                        border: 1px solid rgba(0, 255, 136, 0.3);">
                <div style="opacity: 0.7; margin-bottom: 4px;">当前配置</div>
                <div style="font-weight: bold; font-size: 12px;">{item}</div>
                <div style="opacity: 0.7; font-size: 10px; margin-top: 2px;">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="font-family: 'Orbitron', sans-serif; font-size: 11px; color: #666; 
                        text-align: center; padding: 8px;">
                未选择配置项
            </div>
            """, unsafe_allow_html=True)
