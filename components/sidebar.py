import streamlit as st

# 菜单结构
MENU_STRUCTURE = {
    "联邦学习配置": [
        "2节点基线",
        "3节点扩展",
        "7节点扩展",
        "41节点全量",
        "五节点1天窗口",
        "五节点7天窗口"
    ],
    "特征工程": [
        "双流模型",
        "4G单独训练",
        "5G单独训练",
        "2节点粒度融合",
        "41节点粒度融合"
    ],
    "策略模式": [
        "Phase1",
        "Phase2",
        "Phase3",
        "集成学习"
    ],
    "单节点优化": [
        "单节点最佳",
        "贝叶斯优化",
        "自适应早停",
        "阈值优化",
        "新口径单独",
        "旧口径单独"
    ]
}

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
        # 菜单渲染
        for category, items in MENU_STRUCTURE.items():
            # 展开状态
            is_expanded = st.session_state.expanded_cats.get(category, False)
            
            # 类别按钮
            cols = st.columns([6, 1])
            with cols[0]:
                icon = "▼" if is_expanded else "▶"
                btn_type = "secondary" if is_expanded else "tertiary"
                if st.button(
                    f"{icon} {category}",
                    key=f"cat_{category}",
                    use_container_width=True,
                    type=btn_type
                ):
                    st.session_state.expanded_cats[category] = not is_expanded
                    st.rerun()
            
            # 子项列表
            if is_expanded:
                for item in items:
                    item_key = f"{category}::{item}"
                    is_selected = st.session_state.selected_config == item_key
                    
                    # 根据选中状态设置样式
                    btn_type = "primary" if is_selected else "tertiary"
                    prefix = "●" if is_selected else "○"
                    
                    if st.button(
                        f"{prefix} {item}",
                        key=f"item_{item_key}",
                        use_container_width=True,
                        type=btn_type
                    ):
                        st.session_state.selected_config = item_key
                        st.rerun()
        
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
