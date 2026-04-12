import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_echarts import st_echarts, JsCode
import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.sidebar import render_sidebar

# ========== 页面配置 ==========
st.set_page_config(
    page_title="融易调——异构基站节能决策系统",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 渲染共享侧边栏
render_sidebar()

# ==================== 侧边栏 / 策略模式选择 ====================
# 策略模式选择
strategy = st.sidebar.selectbox("策略模式", ["Phase1", "Phase2", "Phase3", "双模型集成", "三模型集成"])

# ==================== 侧边栏 / 数据筛选 ====================
# 根据策略加载对应的数据文件
data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# 根据策略选择对应的数据文件
if strategy == "Phase1":
    csv_path = os.path.join(data_dir, 'decision_results_7day_all.csv')
elif strategy == "Phase2":
    csv_path = os.path.join(data_dir, 'decision_results_7day_all_phase2.csv')
elif strategy == "Phase3":
    csv_path = os.path.join(data_dir, 'decision_results_7day_all_phase3.csv')
else:
    # 默认使用 Phase2 数据
    csv_path = os.path.join(data_dir, 'decision_results_7day_all_phase2.csv')

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # 获取日期范围
    min_date = pd.to_datetime(df['date']).min().date()
    max_date = pd.to_datetime(df['date']).max().date()
    default_date = max_date
    
    # 获取基站列表
    nodes = sorted(df['node_id'].unique())
    
    # 使用session_state来存储日期和基站
    if 'home_date' not in st.session_state:
        st.session_state.home_date = default_date
    if 'home_node' not in st.session_state:
        if 8001 in nodes:
            st.session_state.home_node = f"基站 8001"
        else:
            st.session_state.home_node = f"基站 {nodes[0]}"
    
    # 定义回调函数 - 当日期或基站改变时更新图表
    def on_date_change():
        st.session_state.home_date = st.session_state.home_date_input
    
    def on_node_change():
        st.session_state.home_node = st.session_state.home_node_select
    
    # 日期选择器
    selected_date = st.sidebar.date_input(
        "历史回测日期",
        value=st.session_state.home_date,
        min_value=min_date,
        max_value=max_date,
        key='home_date_input',
        on_change=on_date_change
    )
    
    # 基站选择器 - 默认选中8001基站
    node_options = [f"基站 {node}" for node in nodes]
    default_index = 0
    if 8001 in nodes:
        default_index = nodes.index(8001)
    
    selected_node = st.sidebar.selectbox(
        "选择基站",
        options=node_options,
        index=default_index,
        key='home_node_select',
        on_change=on_node_change
    )
    
# ========== 完整 CSS 样式 ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 25%, #0f3460 50%, #1a1a2e 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 255, 136, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 136, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
    }
    
    .stApp::after {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(0, 170, 255, 0.1) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(138, 43, 226, 0.05) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: pulseGlow 8s ease-in-out infinite;
    }
    
    @keyframes pulseGlow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    /* ========== 侧边栏科技风样式 ========== */
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 26, 0.7) !important;
        border-right: 1px solid rgba(0, 255, 136, 0.2);
        box-shadow: 0 0 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0.5rem;
    }
    
    .sidebar-header {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88;
        font-size: 1.1rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0.5rem;
        border-bottom: 1px solid rgba(0, 255, 136, 0.3);
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        background: rgba(0, 255, 136, 0.05);
        border-radius: 8px;
    }
    
    .sidebar-search {
        margin-bottom: 1rem;
    }
    
    .sidebar-search input {
        background: rgba(15, 52, 96, 0.8) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 8px !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
        font-size: 12px !important;
    }
    
    .sidebar-search input::placeholder {
        color: rgba(0, 255, 136, 0.5) !important;
    }
    
    .sidebar-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.3), transparent);
        margin: 0.8rem 0;
    }
    
    .sidebar-section-title {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88;
        font-size: 0.9rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 5px rgba(0, 255, 136, 0.3);
    }
    
    .sidebar-info {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.7);
        margin-top: 0.3rem;
        text-align: center;
    }
    
    .sidebar-info .highlight {
        color: #00ff88;
        font-weight: bold;
        text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(15, 52, 96, 0.8) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div > div {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
    }
    
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem;
        background: rgba(10, 10, 26, 0.9);
        border-top: 1px solid rgba(0, 255, 136, 0.2);
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        color: #00ff88;
    }
    
    /* ========== 主内容区样式 ========== */
    [data-testid="stSidebar"] + section {
        margin-left: 0;
    }
    
    /* 关键指标卡片样式 */
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2), inset 0 0 20px rgba(0, 255, 136, 0.05);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.1), transparent);
        transition: left 0.6s ease;
    }
    
    .kpi-card:hover::before {
        left: 100%;
    }
    
    .kpi-card:hover {
        border-color: rgba(0, 255, 136, 0.5);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.3), inset 0 0 30px rgba(0, 255, 136, 0.1);
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .kpi-label {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    
    .kpi-value {
        font-family: 'Orbitron', sans-serif;
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
        margin-bottom: 5px;
    }
    
    .kpi-delta {
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        color: #00ff88;
    }
    
    .kpi-delta.negative {
        color: #ff6b6b;
    }
    
    /* 阶梯图容器 */
    .step-chart-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.25);
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2), inset 0 0 20px rgba(0, 255, 136, 0.05);
        backdrop-filter: blur(10px);
    }
    
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.25);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2), inset 0 0 20px rgba(0, 255, 136, 0.05);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: rgba(0, 255, 136, 0.4);
        box-shadow: 0 8px 40px rgba(0, 0, 0, 0.25), inset 0 0 25px rgba(0, 255, 136, 0.08);
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.08);
    }
    
    .stMetric label {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
    }
    
    h1 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #00ff88, #00aaff, #00ff88);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShine 3s linear infinite;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
    }
    
    @keyframes textShine {
        to { background-position: 200% center; }
    }
    
    h2, h3, h4 {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88 !important;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }
    
    .stCaption, .stMarkdown, p, span {
        color: #c0c0c0 !important;
    }
    
    .element-container {
        position: relative;
        z-index: 1;
    }
    
    [data-testid="stPlotlyChart"] {
        background: transparent !important;
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15), inset 0 0 15px rgba(0, 255, 136, 0.03);
    }

    /* ECharts图表容器透明背景 */
    .element-container:has(> div > canvas) {
        background: transparent !important;
    }

    [data-testid="stArrowVegaLiteChart"] {
        background: transparent !important;
    }

    /* 针对streamlit-echarts的容器 */
    .stMarkdown + div {
        background: transparent !important;
    }

    /* 图表外层容器 */
    .stChart {
        background: transparent !important;
    }

    /* 修复streamlit-echarts canvas黑色背景问题 */
    iframe {
        background: transparent !important;
    }

    /* 针对ECharts timeline图表的容器 */
    div:has(> iframe) {
        background: transparent !important;
    }

    /* 所有canvas元素的父容器 */
    canvas {
        background: transparent !important;
    }

    /* streamlit-echarts组件的容器 */
    [data-testid="stVerticalBlock"] div:has(iframe) {
        background: transparent !important;
    }

    /* 基站负载分布图特定容器 */
    div[id*="echarts_base_station"] {
        background: transparent !important;
    }

    /* 所有包含ECharts的div */
    div[style*="position: relative"] {
        background: transparent !important;
    }
    
    .stSelectbox label, .stDateInput label, .stSlider label {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    [data-baseweb="select"] {
        background: rgba(15, 52, 96, 0.8) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
    }
    
    [data-baseweb="select"] * {
        color: #ffffff !important;
    }
    
    input[type="date"] {
        background: rgba(15, 52, 96, 0.8) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="slider"] {
        background: rgba(15, 52, 96, 0.5) !important;
    }
    
    [data-baseweb="slider"] [role="slider"] {
        background: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
    }
    
    hr {
        border-color: rgba(0, 255, 136, 0.3) !important;
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(10, 10, 26, 0.8);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ff88, #00aaff);
        border-radius: 4px;
    }
    
    .nav-button {
        display: inline-block;
        padding: 5px 12px;
        margin: 0 2px;
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 5px;
        background: rgba(255, 255, 255, 0.05);
        color: #00ff88 !important;
        text-decoration: none !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
        backdrop-filter: blur(10px);
    }
    
    .nav-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.2), transparent);
        transition: left 0.5s ease;
        z-index: -1;
    }
    
    .nav-button:hover::before {
        left: 100%;
    }
    
    .nav-button:hover {
        border-color: rgba(0, 255, 136, 0.6);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        transform: translateY(-2px);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 170, 255, 0.2) 100%);
        border-color: rgba(0, 255, 136, 0.6);
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }
    
    .floating-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: #00ff88;
        border-radius: 50%;
        opacity: 0.6;
        animation: float 20s infinite;
        box-shadow: 0 0 10px #00ff88;
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.6;
        }
        90% {
            opacity: 0.6;
        }
        100% {
            transform: translateY(-100vh) rotate(720deg);
            opacity: 0;
        }
    }
    
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    /* 配置详情卡片 */
    .config-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 255, 136, 0.25);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15), inset 0 0 15px rgba(0, 255, 136, 0.03);
        backdrop-filter: blur(10px);
    }
    
    /* 侧边栏导航链接字体大小 */
    [data-testid="stSidebarNavLink"] p {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebarNavLink"] {
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 数据读取函数 ==========
@st.cache_data
def load_kpi_data():
    """从CSV读取关键指标数据，如果没有则使用默认值"""
    try:
        if os.path.exists("kpi_data.csv"):
            df = pd.read_csv("kpi_data.csv")
            return {
                "best_smape": float(df["best_smape"].iloc[0]),
                "total_improvement": float(df["total_improvement"].iloc[0]),
                "node_count": int(df["node_count"].iloc[0]),
                "compression_ratio": float(df["compression_ratio"].iloc[0])
            }
    except:
        pass
    
    # 默认演示数据
    return {
        "best_smape": 2.35,
        "total_improvement": 23.8,
        "node_count": 42,
        "compression_ratio": 8.5
    }

@st.cache_data
def load_step_data():
    """读取精度提升阶梯数据"""
    try:
        # 读取真实实验数据
        csv_path = os.path.join(os.path.dirname(__file__), "data", "experiments_summary.csv")
        if os.path.exists(csv_path):
            # 手动指定列名（CSV实际列：name, node_count, nodes, sMAPE, μ, features）
            df = pd.read_csv(csv_path, on_bad_lines='skip', header=None,
                             names=["name", "node_count", "nodes", "sMAPE", "μ", "features"],
                             skiprows=1)  # 跳过原始表头行
            # 清理sMAPE列：移除中文句号等非数字字符
            df["sMAPE"] = df["sMAPE"].astype(str).str.replace("。", "").str.replace(",", "")
            df["sMAPE"] = pd.to_numeric(df["sMAPE"], errors="coerce")
            # 移除sMAPE为NaN的行
            df = df.dropna(subset=["sMAPE"])
            # 按sMAPE降序排列（从基线到最优，呈现阶梯下降效果）
            df = df.sort_values("sMAPE", ascending=False)
            # 选择关键节点展示精度提升路径
            key_experiments = [
                ("基线(3节点)", 103.04, "3节点"),
                ("基线(7节点)", 102.16, "7节点"),
                ("单节点基线", 55.42, "2节点7天窗口基线"),
                ("双流模型", 51.90, "双流模型"),
                ("4G单独训练", 47.57, "4G单独训练"),
                ("5G单独训练", 35.98, "5G单独训练"),
                ("五节点1天窗口", 36.18, "五节点1天窗口基线"),
                ("2节点粒度融合", 33.88, "2节点粒度融合"),
                ("41节点粒度融合", 40.81, "41节点粒度融合"),
                ("五节点7天窗口", 31.82, "五节点7天窗口基线"),
                ("知识迁移加权", 37.93, "E4知识迁移加权"),
                ("节点加权", 39.25, "E2节点加权"),
                ("粒度融合", 39.25, "E3粒度融合"),
                ("可学习时段权重", 39.62, "E5可学习时段权重"),
                ("混合口径", 58.12, "混合口径"),
                ("两阶段训练", 60.54, "两阶段训练"),
                ("单节点最佳", 61.73, "v1单节点最佳"),
                ("贝叶斯优化", 62.64, "贝叶斯优化最佳"),
                ("自适应早停", 68.15, "Step2自适应早停"),
                ("阈值优化", 69.93, "Step1阈值优化"),
                ("新口径单独", 70.78, "新口径单独"),
                ("旧口径单独", 65.53, "旧口径单独"),
            ]
            # 从CSV中匹配数据并按sMAPE降序排列
            experiment_data = []
            for name, default_smape, search_key in key_experiments:
                matched = df[df["name"].str.contains(search_key, na=False)]
                if not matched.empty:
                    val = matched.iloc[0]["sMAPE"]
                    if pd.notna(val):
                        experiment_data.append((name, round(float(val), 2)))
                else:
                    experiment_data.append((name, round(default_smape, 2)))
            
            # 按sMAPE值降序排列（从大到小，呈现阶梯下降）
            experiment_data.sort(key=lambda x: x[1], reverse=True)
            stage_names = [x[0] for x in experiment_data]
            smape_values = [x[1] for x in experiment_data]
            return smape_values, stage_names
    except Exception as e:
        st.warning(f"读取实验数据失败: {e}")
    
    # 默认演示数据：从基线到最优的sMAPE下降路径
    return (
        [103.04, 102.16, 55.42, 51.90, 47.57, 40.81, 36.18, 35.98, 33.88, 31.82],  # sMAPE值
        ["基线(3节点)", "基线(7节点)", "单节点基线", "双流模型", "4G/5G单独", 
         "41节点粒度融合", "五节点1天窗口", "5G单独训练", "2节点粒度融合", "五节点7天窗口基线"]  # 阶段名称
    )

# ========== 菜单数据结构 ==========
MENU_STRUCTURE = {
    "单节点优化": [
        "单节点基线",
        "自适应早停",
        "贝叶斯优化",
        "v1特征选择"
    ],
    "口径修复": [
        "单节点基线",
        "自适应早停",
        "贝叶斯优化",
        "v1特征选择",
        "口径协同"
    ],
    "日聚合联邦": [
        "日聚合联邦 1天窗口 (2节点)",
        "日聚合联邦 7天窗口 (2节点)",
        "日聚合联邦 1天窗口 (41节点)",
        "日聚合联邦 7天窗口 (41节点)"
    ],
    "多源协同": [
        "单节点基线",
        "自适应早停",
        "贝叶斯优化",
        "v1特征选择",
        "口径协同",
        "日聚合联邦 1天窗口 (2节点)",
        "日聚合联邦 7天窗口 (2节点)",
        "日聚合联邦 1天窗口 (41节点)",
        "日聚合联邦 7天窗口 (41节点)",
        "粒度融合 (2节点)",
        "粒度融合 (41节点)",
        "知识迁移加权 (2节点)",
        "知识迁移加权 (41节点)",
        "可学习时段权重 (2节点)",
        "双流模型 (7天+清华)",
        "节点加权 (41节点)"
    ],
    "代际协同": [
        "4G+5G协同 (FedRep)"
    ]
}

# 配置项详细说明
CONFIG_DESCRIPTIONS = {
    "单节点基线": "基础单节点训练配置，使用默认超参数作为基准对照组。",
    "自适应早停": "根据验证集损失动态调整早停策略，防止过拟合并节省训练时间。",
    "贝叶斯优化": "使用贝叶斯优化自动搜索最优超参数组合，提升模型性能。",
    "v1特征选择": "基于V1版本的特征选择策略，保留关键特征，降低维度。",
    "口径协同": "多口径数据对齐与协同处理机制，解决数据不一致问题。",
    "日聚合联邦 1天窗口 (2节点)": "单日数据聚合，2个联邦节点协同训练，适合快速迭代。",
    "日聚合联邦 7天窗口 (2节点)": "7天滑动窗口聚合，2个联邦节点，兼顾时效性与稳定性。",
    "日聚合联邦 1天窗口 (41节点)": "单日数据聚合，41个联邦节点大规模协同，全局模型精度高。",
    "日聚合联邦 7天窗口 (41节点)": "7天滑动窗口，41个联邦节点分布式训练，适合长期预测。",
    "粒度融合 (2节点)": "2节点细粒度特征融合策略，提升局部模型表达能力。",
    "粒度融合 (41节点)": "41节点大规模粒度融合，全局与局部特征联合建模。",
    "知识迁移加权 (2节点)": "2节点间知识迁移与自适应加权，加速收敛。",
    "知识迁移加权 (41节点)": "41节点知识迁移网络，动态权重分配，平衡各节点贡献。",
    "可学习时段权重 (2节点)": "时段敏感的可学习权重机制，适配2节点场景。",
    "双流模型 (7天+清华)": "双时间流架构，结合7天窗口与清华特征集，多尺度建模。",
    "节点加权 (41节点)": "41节点重要性自适应加权算法，优化联邦聚合策略。",
    "4G+5G协同 (FedRep)": "基于FedRep的4G/5G跨代际联邦学习，异构网络协同。"
}

# ========== 主内容区 ==========

# 页面标题
st.markdown("<h1 style='text-align: center; color: #00ff88; margin-top: 10px; margin-bottom: 20px; font-family: Orbitron, sans-serif; font-size: 1.8rem;'>融易调——从联邦失效到个性化突破的异构基站节能决策系统</h1>", unsafe_allow_html=True)

# 粒子效果
particle_html = '<div class="floating-particles">'
for i in range(20):
    left = f"{i * 5}%"
    delay = f"{i * 0.8}s"
    duration = f"{15 + i % 10}s"
    particle_html += f'<div class="particle" style="left: {left}; animation-delay: {delay}; animation-duration: {duration};"></div>'
particle_html += '</div>'
st.markdown(particle_html, unsafe_allow_html=True)

# ========== 关键指标卡片区域（新增）==========
# 使用两列布局：左侧核心性能指标（垂直排列），右侧实验依赖关系图
kpi_graph_col1, kpi_graph_col2 = st.columns([1, 3])

with kpi_graph_col1:
    st.markdown("<h3 style='color: #00ff88; margin-top: 0px; margin-bottom: 15px; font-family: Orbitron, sans-serif;'>核心性能指标</h3>", unsafe_allow_html=True)
    
    # 指标 1: 联邦最佳预测 sMAPE
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%); 
                border: 1px solid rgba(76, 175, 80, 0.5); 
                border-radius: 10px; 
                padding: 12px 8px; 
                text-align: center;
                cursor: pointer;
                margin-bottom: 10px;"
         title="联邦最佳预测 sMAPE 指标&#10;较基线提升 67.1%">
        <div style="color: #4CAF50; font-size: 14px; margin-bottom: 6px; font-family: 'Orbitron', sans-serif; font-weight: bold;">联邦最佳预测 sMAPE</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">31.75%</div>
        <div style="color: #4CAF50; font-size: 13px; margin-top: 4px; font-weight: bold;">↓ 较基线 -67.1%</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 指标 2: 参与节点数
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%); 
                border: 1px solid rgba(33, 150, 243, 0.5); 
                border-radius: 10px; 
                padding: 12px 8px; 
                text-align: center;
                cursor: pointer;
                margin-bottom: 10px;"
         title="参与联邦学习的节点数量&#10;覆盖全国多个区域">
        <div style="color: #2196F3; font-size: 14px; margin-bottom: 6px; font-family: 'Orbitron', sans-serif; font-weight: bold;">参与节点数</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">52</div>
        <div style="color: #2196F3; font-size: 13px; margin-top: 4px; font-weight: bold;">全范围覆盖</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 指标 3: 决策准确率
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(156, 39, 176, 0.2) 0%, rgba(156, 39, 176, 0.1) 100%); 
                border: 1px solid rgba(156, 39, 176, 0.5); 
                border-radius: 10px; 
                padding: 12px 8px; 
                text-align: center;
                cursor: pointer;
                margin-bottom: 10px;"
         title="智能决策系统的准确率&#10;基于历史决策验证">
        <div style="color: #9C27B0; font-size: 14px; margin-bottom: 6px; font-family: 'Orbitron', sans-serif; font-weight: bold;">决策准确率</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">81.86%</div>
        <div style="color: #9C27B0; font-size: 13px; margin-top: 4px; font-weight: bold;">高精度智能决策</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 指标 4: 总节能
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%); 
                border: 1px solid rgba(255, 193, 7, 0.5); 
                border-radius: 10px; 
                padding: 12px 8px; 
                text-align: center;
                cursor: pointer;"
         title="系统累计节约的能源总量&#10;相当于减少碳排放约 10 万吨">
        <div style="color: #FFC107; font-size: 14px; margin-bottom: 6px; font-family: 'Orbitron', sans-serif; font-weight: bold;">总节能</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">675M kWh</div>
        <div style="color: #FFC107; font-size: 13px; margin-top: 4px; font-weight: bold;">累计节约能耗</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_graph_col2:
    # ========== 实验依赖关系图（Graph - 新增）==========
    st.markdown("<h3 style='color: #00ff88; margin-top: 0px; margin-bottom: 15px; font-family: Orbitron, sans-serif;'>实验依赖关系图</h3>", unsafe_allow_html=True)

    # 实验节点sMAPE值映射（基于CSV数据）
    node_smape_map = {
        "数据预处理": None,
        "4G/5G分布分析": None,
        "单节点基线": 61.73,
        "自适应早停": 68.15,
        "贝叶斯优化": 62.64,
        "v1特征选择": 58.12,
        "口径协同": 58.12,
        "2节点FedProx验证": None,
        "24节点联邦过夜跑": None,
        "归一化修复": None,
        "粒度融合2节点": 33.88,
        "粒度融合41节点": 39.25,
        "双流模型": 51.90,
        "知识迁移加权": None,
        "可学习时段权重": 39.62,
        "节点加权": 39.25,
        "五节点窗口对比": None,
        "优化方法验证": None,
        "可学习时段测试": None,
        "优化版基线测试": None,
        "SHAP窗口分析": None,
        "多节点批量SHAP": None,
        "原始微调": None,
        "二次微调": None,
        "最佳模型选择": 31.82,
        "决策引擎(阈值)": None,
        "决策引擎(成本敏感)": None,
        "决策引擎(动态阈值)": None,
        "集成学习决策": None,
    }
    
    # 实验依赖关系图数据
    experiment_nodes = [
        # 类别0: 数据准备
        {"name": "数据预处理", "category": 0, "symbolSize": 50, "value": node_smape_map.get("数据预处理")},
        {"name": "4G/5G分布分析", "category": 0, "symbolSize": 38, "value": node_smape_map.get("4G/5G分布分析")},
        
        # 类别1: 单节点优化
        {"name": "单节点基线", "category": 1, "symbolSize": 45, "value": node_smape_map.get("单节点基线")},
        {"name": "自适应早停", "category": 1, "symbolSize": 38, "value": node_smape_map.get("自适应早停")},
        {"name": "贝叶斯优化", "category": 1, "symbolSize": 40, "value": node_smape_map.get("贝叶斯优化")},
        {"name": "v1特征选择", "category": 1, "symbolSize": 40, "value": node_smape_map.get("v1特征选择")},
        {"name": "口径协同", "category": 1, "symbolSize": 40, "value": node_smape_map.get("口径协同")},
        
        # 类别2: 联邦训练基础
        {"name": "2节点FedProx验证", "category": 2, "symbolSize": 42, "value": node_smape_map.get("2节点FedProx验证")},
        {"name": "24节点联邦过夜跑", "category": 2, "symbolSize": 38, "value": node_smape_map.get("24节点联邦过夜跑")},
        {"name": "归一化修复", "category": 2, "symbolSize": 42, "value": node_smape_map.get("归一化修复")},
        
        # 类别3: 多源协同与粒度融合
        {"name": "粒度融合2节点", "category": 3, "symbolSize": 45, "value": node_smape_map.get("粒度融合2节点")},
        {"name": "粒度融合41节点", "category": 3, "symbolSize": 50, "value": node_smape_map.get("粒度融合41节点")},
        {"name": "双流模型", "category": 3, "symbolSize": 40, "value": node_smape_map.get("双流模型")},
        {"name": "知识迁移加权", "category": 3, "symbolSize": 38, "value": node_smape_map.get("知识迁移加权")},
        {"name": "可学习时段权重", "category": 3, "symbolSize": 38, "value": node_smape_map.get("可学习时段权重")},
        {"name": "节点加权", "category": 3, "symbolSize": 38, "value": node_smape_map.get("节点加权")},
        
        # 类别4: 窗口与基线对比
        {"name": "五节点窗口对比", "category": 4, "symbolSize": 42, "value": node_smape_map.get("五节点窗口对比")},
        {"name": "优化方法验证", "category": 4, "symbolSize": 40, "value": node_smape_map.get("优化方法验证")},
        {"name": "可学习时段测试", "category": 4, "symbolSize": 38, "value": node_smape_map.get("可学习时段测试")},
        {"name": "优化版基线测试", "category": 4, "symbolSize": 38, "value": node_smape_map.get("优化版基线测试")},
        
        # 类别5: 可解释性
        {"name": "SHAP窗口分析", "category": 5, "symbolSize": 40, "value": node_smape_map.get("SHAP窗口分析")},
        {"name": "多节点批量SHAP", "category": 5, "symbolSize": 40, "value": node_smape_map.get("多节点批量SHAP")},
        
        # 类别6: 个性化微调
        {"name": "原始微调", "category": 6, "symbolSize": 42, "value": node_smape_map.get("原始微调")},
        {"name": "二次微调", "category": 6, "symbolSize": 42, "value": node_smape_map.get("二次微调")},
        {"name": "最佳模型选择", "category": 6, "symbolSize": 44, "value": node_smape_map.get("最佳模型选择")},
        
        # 类别7: 决策应用
        {"name": "决策引擎(阈值)", "category": 7, "symbolSize": 42, "value": node_smape_map.get("决策引擎(阈值)")},
        {"name": "决策引擎(成本敏感)", "category": 7, "symbolSize": 42, "value": node_smape_map.get("决策引擎(成本敏感)")},
        {"name": "决策引擎(动态阈值)", "category": 7, "symbolSize": 42, "value": node_smape_map.get("决策引擎(动态阈值)")},
        {"name": "集成学习决策", "category": 7, "symbolSize": 48, "value": node_smape_map.get("集成学习决策")},
    ]
    
    experiment_links = [
        # 数据准备 → 单节点优化
        {"source": "数据预处理", "target": "单节点基线"},
        {"source": "数据预处理", "target": "4G/5G分布分析"},
        
        # 单节点优化链
        {"source": "单节点基线", "target": "自适应早停"},
        {"source": "单节点基线", "target": "贝叶斯优化"},
        {"source": "贝叶斯优化", "target": "v1特征选择"},
        {"source": "v1特征选择", "target": "口径协同"},
        
        # 联邦训练基础
        {"source": "v1特征选择", "target": "2节点FedProx验证"},
        {"source": "2节点FedProx验证", "target": "24节点联邦过夜跑"},
        {"source": "24节点联邦过夜跑", "target": "归一化修复"},
        
        # 多源协同
        {"source": "归一化修复", "target": "粒度融合2节点"},
        {"source": "粒度融合2节点", "target": "粒度融合41节点"},
        {"source": "归一化修复", "target": "双流模型"},
        {"source": "粒度融合2节点", "target": "知识迁移加权"},
        {"source": "粒度融合2节点", "target": "可学习时段权重"},
        {"source": "粒度融合41节点", "target": "节点加权"},
        
        # 窗口与基线
        {"source": "归一化修复", "target": "五节点窗口对比"},
        {"source": "五节点窗口对比", "target": "优化方法验证"},
        {"source": "粒度融合2节点", "target": "可学习时段测试"},
        {"source": "归一化修复", "target": "优化版基线测试"},
        
        # 可解释性
        {"source": "单节点基线", "target": "SHAP窗口分析"},
        {"source": "SHAP窗口分析", "target": "多节点批量SHAP"},
        {"source": "五节点窗口对比", "target": "多节点批量SHAP"},
        
        # 个性化微调
        {"source": "粒度融合41节点", "target": "原始微调"},
        {"source": "原始微调", "target": "二次微调"},
        {"source": "二次微调", "target": "最佳模型选择"},
        {"source": "五节点窗口对比", "target": "原始微调"},
        
        # 决策应用
        {"source": "最佳模型选择", "target": "决策引擎(阈值)"},
        {"source": "决策引擎(阈值)", "target": "决策引擎(成本敏感)"},
        {"source": "决策引擎(阈值)", "target": "决策引擎(动态阈值)"},
        {"source": "决策引擎(成本敏感)", "target": "集成学习决策"},
        {"source": "决策引擎(动态阈值)", "target": "集成学习决策"},
    ]
    
    categories = [
        {"name": "数据准备", "itemStyle": {"color": "#00aaff"}},
        {"name": "单节点优化", "itemStyle": {"color": "#00ff88"}},
        {"name": "联邦训练基础", "itemStyle": {"color": "#ffd93d"}},
        {"name": "多源协同", "itemStyle": {"color": "#ff6b6b"}},
        {"name": "窗口与基线", "itemStyle": {"color": "#9b59b6"}},
        {"name": "可解释性", "itemStyle": {"color": "#e84393"}},
        {"name": "个性化微调", "itemStyle": {"color": "#1e88e5"}},
        {"name": "决策应用", "itemStyle": {"color": "#ff8c42"}},
    ]
    
    graph_option = {
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(10, 10, 26, 0.95)",
            "borderColor": "#00ff88",
            "borderWidth": 1,
            "textStyle": {"color": "#e0e0e0"},
            "formatter": JsCode("""function(params) {
                var name = params.data.name;
                var value = params.data.value;
                var category = params.data.category;
                var categories = ['数据准备', '单节点优化', '联邦训练基础', '多源协同', '窗口与基线', '可解释性', '个性化微调', '决策应用'];
                var result = '<div style="font-weight:bold;color:#00ff88;margin-bottom:5px;">' + name + '</div>';
                result += '<div style="color:#c0c0c0;font-size:12px;">类别: ' + categories[category] + '</div>';
                if (value !== null && value !== undefined) {
                    result += '<div style="color:#ffd700;font-size:14px;font-weight:bold;margin-top:5px;">sMAPE: ' + value + '%</div>';
                }
                return result;
            }""")
        },
        "legend": {
            "data": ["数据准备", "单节点优化", "联邦训练", "粒度融合", "基线对比"],
            "top": 10,
            "textStyle": {"color": "#00ff88", "fontFamily": "Orbitron"}
        },
        "series": [{
            "type": "graph",
            "layout": "force",
            "data": experiment_nodes,
            "links": experiment_links,
            "categories": categories,
            "roam": True,
            "label": {
                "show": True,
                "position": "right",
                "color": "#e0e0e0",
                "fontFamily": "Orbitron",
                "fontSize": 11
            },
            "edgeSymbol": ["none", "arrow"],
            "edgeSymbolSize": [0, 10],
            "force": {
                "repulsion": 300,
                "edgeLength": 100,
                "gravity": 0.1
            },
            "lineStyle": {
                "color": "#00ff88",
                "curveness": 0.2,
                "width": 2,
                "opacity": 0.8
            },
            "emphasis": {
                "focus": "adjacency",
                "lineStyle": {
                    "width": 4,
                    "color": "#ffd93d"
                },
                "itemStyle": {
                    "shadowBlur": 20,
                    "shadowColor": "#00ff88"
                }
            },
            "animationDuration": 2000,
            "animationEasing": "cubicOut"
        }]
    }
    
    # ========== 方案1关键：使用唯一key和独立容器 ==========
    # 生成唯一key（使用时间戳+随机数确保唯一性）
    graph_key = f"experiment_graph_{int(time.time() * 1000)}_{id(graph_option)}"
    
    # 使用独立容器包裹第一个图表
    graph_container = st.container()
    with graph_container:
        st_echarts(options=graph_option, height="400px", key=graph_key)
    
    # 添加DOM隔离分隔线
    st.markdown("<div style='height: 30px; clear: both;'></div>", unsafe_allow_html=True)

# ========== 精度提升路线图（阶梯图 - 新增）==========
smape_values, stage_names = load_step_data()

# 确保数据有效并转换为Python原生类型
if not smape_values or len(smape_values) == 0 or len(smape_values) != len(stage_names):
    smape_values = [103.04, 102.16, 55.42, 51.90, 47.57, 40.81, 36.18, 35.98, 33.88, 31.82]
    stage_names = ["基线(3节点)", "基线(7节点)", "单节点基线", "双流模型", "4G/5G单独", 
                   "41节点粒度融合", "五节点1天窗口", "5G单独训练", "2节点粒度融合", "五节点7天窗口基线"]

# 强制转换为Python原生float类型（避免numpy类型问题）
clean_data = [float(v) for v in smape_values]
clean_labels = [str(l) for l in stage_names]

# 调试输出（取消注释查看数据）
# st.write(f"精度提升路线图数据: {clean_data}")
# st.write(f"标签: {clean_labels}")

# ========== 关键修复：使用完全独立的变量名 step_chart_option ==========
step_chart_option = {
    "backgroundColor": "transparent",
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"},
        "formatter": "{b}<br/>sMAPE: {c}%"
    },
    "grid": {
        "left": "3%",
        "right": "4%",
        "bottom": "15%",
        "top": "15%",
        "containLabel": True
    },
    "xAxis": {
        "type": "category",
        "data": clean_labels,
        "axisLabel": {
            "color": "#00ff88",
            "fontSize": 11,
            "rotate": 30,
            "interval": 0
        },
        "axisLine": {
            "lineStyle": {
                "color": "rgba(0, 255, 136, 0.5)",
                "width": 2
            }
        },
        "axisTick": {
            "alignWithLabel": True,
            "lineStyle": {"color": "#00ff88"}
        }
    },
    "yAxis": {
        "type": "value",
        "name": "sMAPE (%)",
        "nameTextStyle": {
            "color": "#00ff88",
            "fontFamily": "Orbitron"
        },
        "min": 25,
        "max": 110,
        "axisLabel": {"color": "#00ff88"},
        "axisLine": {
            "lineStyle": {
                "color": "rgba(0, 255, 136, 0.5)",
                "width": 2
            }
        },
        "splitLine": {
            "lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}
        }
    },
    "series": [
        {
            "name": "sMAPE",
            "type": "line",
            "step": "middle",
            "data": clean_data,
            "connectNulls": True,
            "lineStyle": {
                "color": "#00ff88",
                "width": 4,
                "shadowColor": "rgba(0, 255, 136, 0.8)",
                "shadowBlur": 15
            },
            "itemStyle": {
                "color": "#00ff88",
                "borderWidth": 3,
                "borderColor": "#ffffff",
                "shadowColor": "rgba(0, 255, 136, 0.5)",
                "shadowBlur": 10
            },
            "symbol": "circle",
            "symbolSize": 12,
            "label": {
                "show": True,
                "position": "top",
                "formatter": "{c}%",
                "color": "#00ff88",
                "fontSize": 11,
                "fontFamily": "Orbitron",
                "fontWeight": "bold"
            },
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.5)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0.05)"}
                    ]
                }
            },
            "markPoint": {
                "data": [
                    {
                        "type": "min",
                        "name": "最优",
                        "label": {
                            "formatter": "最优\n{c}%",
                            "color": "#ffffff",
                            "fontSize": 10
                        },
                        "itemStyle": {"color": "#00aaff"}
                    },
                    {
                        "type": "max",
                        "name": "基线",
                        "label": {
                            "formatter": "基线\n{c}%",
                            "color": "#ffffff",
                            "fontSize": 10
                        },
                        "itemStyle": {"color": "#F18F01"}
                    }
                ],
                "symbolSize": 50
            },
            "markLine": {
                "data": [
                    {
                        "type": "average",
                        "name": "平均",
                        "label": {
                            "formatter": "平均: {c}%",
                            "color": "#00ff88"
                        },
                        "lineStyle": {
                            "color": "rgba(0, 255, 136, 0.5)",
                            "type": "dashed"
                        }
                    }
                ]
            }
        }
    ],
    "animation": True,
    "animationDuration": 2000,
    "animationEasing": "cubicOut"
}

# ========== 方案1关键：使用完全不同的唯一key和独立容器 ==========
# 生成完全不同的唯一key（使用不同的时间戳+不同的标识符）
step_key = f"step_chart_{int(time.time() * 1000)}_{id(step_chart_option)}_{hash(tuple(clean_data)) & 0xFFFFFFFF}"

# 使用独立容器包裹第二个图表（与第一个完全隔离）
step_container = st.container()
with step_container:
    # 渲染第二个图表，确保key与第一个完全不同
    st_echarts(options=step_chart_option, height="320px", key=step_key)

# 配置详情展示（如果已选择）
if st.session_state.selected_config:
    cat, item = st.session_state.selected_config.split("::")
    
    with st.expander(f"当前实验配置: {item}", expanded=True):
        cols = st.columns(4)
        
        with cols[0]:
            st.metric("配置类别", cat)
        with cols[1]:
            node_count = "2" if "2节点" in item else ("41" if "41节点" in item else "1")
            st.metric("联邦节点", f"{node_count} 个")
        with cols[2]:
            window = "7天" if "7天" in item else ("1天" if "1天" in item else "N/A")
            st.metric("时间窗口", window)
        with cols[3]:
            status = "基线" if "基线" in item else ("优化中" if any(x in item for x in ["早停", "贝叶斯", "优化"]) else "就绪")
            st.metric("配置状态", status)
        
        # 配置说明
        desc = CONFIG_DESCRIPTIONS.get(item, "暂无详细说明")
        st.info(f"**配置说明**: {desc}")

# 仪表盘布局 - 左右两栏布局：左侧能耗指标（垂直分布），右侧能耗趋势图
metrics_col, trend_col = st.columns([1, 2])

with metrics_col:
    st.markdown("<h3 style='color: #00ff88; margin-top: 0px; margin-bottom: 15px;'>能耗指标</h3>", unsafe_allow_html=True)
    
    # 能耗指标垂直分布
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%); 
                border: 1px solid rgba(76, 175, 80, 0.5); 
                border-radius: 10px; 
                padding: 15px; 
                text-align: center;
                margin-bottom: 12px;"
         title="当前总能耗">
        <div style="color: #4CAF50; font-size: 14px; margin-bottom: 5px; font-family: 'Orbitron', sans-serif; font-weight: bold;">当前总能耗</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">12,345 kWh</div>
        <div style="color: #4CAF50; font-size: 16px; margin-top: 3px; font-weight: bold;">↓ 3.2%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%); 
                border: 1px solid rgba(33, 150, 243, 0.5); 
                border-radius: 10px; 
                padding: 15px; 
                text-align: center;
                margin-bottom: 12px;"
         title="峰值能耗">
        <div style="color: #2196F3; font-size: 14px; margin-bottom: 5px; font-family: 'Orbitron', sans-serif; font-weight: bold;">峰值能耗</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">15,678 kWh</div>
        <div style="color: #ff6b6b; font-size: 16px; margin-top: 3px; font-weight: bold;">↑ 2.1%</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(156, 39, 176, 0.2) 0%, rgba(156, 39, 176, 0.1) 100%); 
                border: 1px solid rgba(156, 39, 176, 0.5); 
                border-radius: 10px; 
                padding: 15px; 
                text-align: center;"
         title="平均能耗">
        <div style="color: #9C27B0; font-size: 14px; margin-bottom: 5px; font-family: 'Orbitron', sans-serif; font-weight: bold;">平均能耗</div>
        <div style="color: #ffffff; font-size: 22px; font-weight: bold; font-family: 'Orbitron', sans-serif;">8,923 kWh</div>
        <div style="color: #4CAF50; font-size: 16px; margin-top: 3px; font-weight: bold;">↓ 1.5%</div>
    </div>
    """, unsafe_allow_html=True)

with trend_col:
    st.markdown("<h3 style='color: #00ff88; margin-top: 0px; margin-bottom: 15px;'>能耗趋势</h3>", unsafe_allow_html=True)
    
    # 使用真实数据加载能耗趋势 - 只展示当前选中基站的当日数据
    if os.path.exists(csv_path) and 'selected_date' in locals() and selected_node != "全部基站":
        # 获取当前选中基站ID
        node_id = int(selected_node.replace("基站 ", ""))
        
        # 根据侧边栏选择的日期和基站筛选数据
        day_trend_data = df[(pd.to_datetime(df['date']).dt.date == selected_date) & 
                            (df['node_id'] == node_id)].copy()
        
        if not day_trend_data.empty:
            # 按hour_code排序，确保时间顺序正确
            day_trend_data = day_trend_data.sort_values('hour_code')
            
            # 时间段映射 - 24小时分成四个时段
            hour_labels = {
                0: "00:00-06:00",
                1: "06:00-12:00",
                2: "12:00-18:00",
                3: "18:00-24:00"
            }

            # 获取唯一的hour_code并排序
            unique_hours = sorted(day_trend_data['hour_code'].unique())

            # 准备数据 - 只使用唯一的时段
            times = [hour_labels.get(hc, f"时段{hc+1}") for hc in unique_hours]

            # 获取真实能耗数据 - 按hour_code分组取平均值（去重）
            if 'real_kw' in day_trend_data.columns:
                # 按hour_code分组，取平均值
                grouped = day_trend_data.groupby('hour_code')['real_kw'].mean()
                true_values = [grouped.get(hc, 0) for hc in unique_hours]
            else:
                true_values = []

            # 获取预测能耗数据（优先使用pred_mean_kw，其次pred_kw）- 按hour_code分组取平均值
            if 'pred_mean_kw' in day_trend_data.columns:
                grouped = day_trend_data.groupby('hour_code')['pred_mean_kw'].mean()
                pred_values = [grouped.get(hc, 0) for hc in unique_hours]
            elif 'pred_kw' in day_trend_data.columns:
                grouped = day_trend_data.groupby('hour_code')['pred_kw'].mean()
                pred_values = [grouped.get(hc, 0) for hc in unique_hours]
            else:
                pred_values = []
        else:
            # 无数据时使用默认值
            times = ["00:00-06:00", "06:00-12:00", "12:00-18:00", "18:00-24:00"]
            true_values = []
            pred_values = []
    else:
        # 未选择具体基站或无数据时使用默认值
        times = ["00:00-06:00", "06:00-12:00", "12:00-18:00", "18:00-24:00"]
        true_values = []
        pred_values = []
    
    # 构建series数据
    series_list = []
    
    # 添加真实值系列（如果有数据）
    if true_values:
        series_list.append({
            "name": "真实值",
            "type": "line",
            "smooth": True,
            "data": true_values,
            "lineStyle": {"width": 3, "color": "#2E8B57"},
            "symbol": "circle",
            "symbolSize": 8,
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(46, 139, 87, 0.8)"},
                        {"offset": 1, "color": "rgba(46, 139, 87, 0.1)"}
                    ]
                }
            }
        })
    
    # 添加预测值系列（如果有数据）
    if pred_values:
        series_list.append({
            "name": "预测值",
            "type": "line",
            "smooth": True,
            "data": pred_values,
            "lineStyle": {"width": 2, "color": "#F18F01", "type": "dashed"},
            "symbol": "diamond",
            "symbolSize": 8,
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(241, 143, 1, 0.6)"},
                        {"offset": 1, "color": "rgba(241, 143, 1, 0.05)"}
                    ]
                }
            }
        })
    
    # 如果没有数据，显示提示
    if not series_list:
        if selected_node == "全部基站":
            st.info("请选择具体基站查看能耗趋势")
        else:
            st.info(f"基站 {selected_node} 在 {selected_date} 没有能耗数据")
    
    # 构建图表配置
    legend_data = [s["name"] for s in series_list]
    
    energy_option = {
        "backgroundColor": "transparent",
        "tooltip": {"trigger": "axis"},
        "legend": {"data": legend_data, "textStyle": {"color": "#00ff88"}},
        "xAxis": {
            "type": "category", 
            "data": times,
            "axisLabel": {"color": "#00ff88"}
        },
        "yAxis": {
            "type": "value", 
            "name": "能耗 (kWh)",
            "axisLabel": {"color": "#00ff88"},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
        },
        "series": series_list
    }
    st_echarts(options=energy_option, height="320px", key=f"echarts_energy_{selected_date}_{selected_node}_{strategy}")

# ========== 图表监控区域 - 三列等宽布局 ==========
col_chart1, col_chart2, col_chart3 = st.columns([1, 1, 1])

with col_chart1:
    st.markdown("<h4 style='color: #00ff88; margin-top: 10px; margin-bottom: 5px;'>决策精度提升</h4>", unsafe_allow_html=True)

    # 决策精度提升数据 - 各阶段策略准确率对比
    decision_accuracy_data = {
        "stages": ['Phase1', 'Phase2', 'Phase3', '双模型集成', '三模型集成'],
        "accuracy": [77.75, 77.45, 78.82, 80.53, 81.86]
    }

    decision_accuracy_option = {
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "axis",
            "formatter": "{b}<br/>决策精度: {c}%"
        },
        "grid": {
            "left": "12%",
            "right": "5%",
            "top": "15%",
            "bottom": "15%"
        },
        "xAxis": {
            "type": "category",
            "data": decision_accuracy_data["stages"],
            "axisLabel": {
                "color": "#00ff88",
                "fontSize": 10,
                "rotate": 15
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 136, 0.3)"
                }
            }
        },
        "yAxis": {
            "type": "value",
            "name": "准确率 (%)",
            "min": 76,
            "max": 83,
            "nameTextStyle": {
                "color": "#00ff88",
                "fontSize": 10
            },
            "axisLabel": {
                "color": "#00ff88",
                "fontSize": 10,
                "formatter": "{value}%"
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 136, 0.3)"
                }
            },
            "splitLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 136, 0.1)"
                }
            }
        },
        "series": [
            {
                "name": "决策精度",
                "type": "line",
                "data": decision_accuracy_data["accuracy"],
                "smooth": True,
                "lineStyle": {
                    "width": 3,
                    "color": "#00aaff",
                    "shadowColor": "rgba(0, 170, 255, 0.5)",
                    "shadowBlur": 10
                },
                "itemStyle": {
                    "color": "#00aaff",
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                },
                "symbol": "circle",
                "symbolSize": 8,
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}%",
                    "color": "#00aaff",
                    "fontSize": 9,
                    "fontWeight": "bold"
                },
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(0, 170, 255, 0.4)"},
                            {"offset": 1, "color": "rgba(0, 170, 255, 0.05)"}
                        ]
                    }
                },
                "markPoint": {
                    "data": [
                        {
                            "coord": [4, 81.86],
                            "name": "最高准确率",
                            "label": {
                                "formatter": "最高\n81.86%",
                                "color": "#ffffff",
                                "fontSize": 9
                            },
                            "itemStyle": {"color": "#00ff88"}
                        }
                    ],
                    "symbolSize": 45
                }
            }
        ],
        "animation": True,
        "animationDuration": 1500,
        "animationEasing": "cubicOut"
    }

    st_echarts(
        options=decision_accuracy_option,
        height="220px",
        key=f"echarts_decision_accuracy_{int(time.time())}"
    )

with col_chart2:
    st.markdown("<h4 style='color: #00ff88; margin-top: 10px; margin-bottom: 5px;'>基站负载分布</h4>", unsafe_allow_html=True)

    # 使用真实数据加载基站负载分布 - 基于选中日期，展示所有基站
    if os.path.exists(csv_path) and 'selected_date' in locals():
        # 获取选中日期所有基站的负载数据
        day_load_data = df[pd.to_datetime(df['date']).dt.date == selected_date].copy()

        if not day_load_data.empty and 'node_id' in day_load_data.columns:
            # 按基站分组，计算平均负载（使用real_kw作为负载指标）
            node_load = day_load_data.groupby('node_id')['real_kw'].mean().reset_index()
            # 按基站ID排序
            node_load = node_load.sort_values('node_id')

            station_names = [f"基站 {int(n)}" for n in node_load['node_id']]
            load_values = node_load['real_kw'].tolist()
        else:
            # 无数据时使用默认值
            station_names = ['基站 1', '基站 2', '基站 3', '基站 4', '基站 5']
            load_values = [65, 45, 80, 30, 75]
    else:
        # 无数据时使用默认值
        station_names = ['基站 1', '基站 2', '基站 3', '基站 4', '基站 5']
        load_values = [65, 45, 80, 30, 75]

    # 颜色配置 - 使用实验依赖关系图的节点颜色（更艳丽）
    colors = [
        {"offset": 0, "color": "#00aaff"}, {"offset": 1, "color": "#0066cc"},  # 蓝色
        {"offset": 0, "color": "#00ff88"}, {"offset": 1, "color": "#00cc66"},  # 绿色
        {"offset": 0, "color": "#ffd93d"}, {"offset": 1, "color": "#ffaa00"},  # 黄色
        {"offset": 0, "color": "#ff6b6b"}, {"offset": 1, "color": "#cc3333"},  # 红色
        {"offset": 0, "color": "#9b59b6"}, {"offset": 1, "color": "#7d3c98"},  # 紫色
        {"offset": 0, "color": "#e84393"}, {"offset": 1, "color": "#c2185b"},  # 粉色
        {"offset": 0, "color": "#1e88e5"}, {"offset": 1, "color": "#1565c0"},  # 深蓝色
        {"offset": 0, "color": "#ff8c42"}, {"offset": 1, "color": "#e65100"}   # 橙色
    ]

    # 将数据分成每组5个基站
    group_size = 5
    total_groups = (len(station_names) + group_size - 1) // group_size

    # 构建timeline数据
    timeline_data = []
    options_list = []

    for group_idx in range(total_groups):
        start_idx = group_idx * group_size
        end_idx = min(start_idx + group_size, len(station_names))

        group_names = station_names[start_idx:end_idx]
        group_values = load_values[start_idx:end_idx]

        # 构建该组的柱状图数据
        bar_data = []
        for i, value in enumerate(group_values):
            color_idx = (i % 5) * 2
            bar_data.append({
                "value": round(value, 1),
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [colors[color_idx], colors[color_idx + 1]]
                    }
                }
            })

        timeline_data.append(f"第{group_idx + 1}组")

        option = {
            "backgroundColor": "transparent",
            "title": {
                "text": f"{group_names[0]} - {group_names[-1]}",
                "textStyle": {"color": "#00ff88", "fontSize": 10},
                "left": "center",
                "top": 0
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": "{b}<br/>负载: {c} kWh"
            },
            "xAxis": {
                "type": "category",
                "data": group_names,
                "axisLabel": {
                    "color": "#00ff88",
                    "fontSize": 11
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}
                }
            },
            "yAxis": {
                "type": "value",
                "name": "负载 (kWh)",
                "min": 0,
                "nameTextStyle": {"color": "#00ff88", "fontSize": 10},
                "axisLabel": {"color": "#00ff88", "fontSize": 10},
                "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
                "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
            },
            "grid": {
                "left": "15%",
                "right": "5%",
                "top": "20%",
                "bottom": "15%"
            },
            "series": [
                {
                    "name": "基站负载",
                    "type": "bar",
                    "data": bar_data,
                    "barWidth": "50%",
                    "showBackground": True,
                    "backgroundStyle": {
                        "color": "rgba(0, 255, 136, 0.05)",
                        "borderRadius": [3, 3, 0, 0]
                    },
                    "itemStyle": {"borderRadius": [3, 3, 0, 0]},
                    "emphasis": {
                        "itemStyle": {"shadowBlur": 20, "shadowColor": "rgba(0, 255, 136, 0.5)"}
                    }
                }
            ]
        }
        options_list.append(option)

    # 构建带timeline的图表配置
    base_station_timeline_option = {
        "backgroundColor": "transparent",
        "baseOption": {
            "timeline": {
                "axisType": "category",
                "autoPlay": True,
                "playInterval": 2000,  # 2秒切换一次
                "data": timeline_data,
                "show": True,
                "bottom": -25,
                "left": "5%",
                "right": "5%",
                "symbolSize": 6,
                "lineStyle": {"color": "rgba(0, 255, 136, 0.3)"},
                "itemStyle": {"color": "#00ff88"},
                "checkpointStyle": {"color": "#00aaff", "borderColor": "#00ff88"},
                "controlStyle": {
                    "showNextBtn": False,
                    "showPrevBtn": False,
                    "color": "#00ff88",
                    "borderColor": "#00ff88"
                },
                "label": {"color": "#00ff88", "fontSize": 8, "show": False}
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"}
            },
            "yAxis": {
                "type": "value",
                "name": "负载 (kWh)",
                "min": 0,
                "nameTextStyle": {"color": "#00ff88", "fontSize": 10},
                "axisLabel": {"color": "#00ff88", "fontSize": 10},
                "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
                "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
            },
            "grid": {
                "left": "15%",
                "right": "5%",
                "top": "18%",
                "bottom": "15%"
            }
        },
        "options": options_list
    }

    st_echarts(
        options=base_station_timeline_option,
        height="240px",
        key=f"echarts_base_station_timeline_{selected_date}_{strategy}"
    )

with col_chart3:
    st.markdown("<h4 style='color: #00ff88; margin-top: 10px; margin-bottom: 5px;'>节能效果分析</h4>", unsafe_allow_html=True)

    # 使用真实数据计算节能效果 - 根据选中基站筛选
    if os.path.exists(csv_path) and 'selected_date' in locals() and selected_node != "全部基站":
        # 获取当前选中基站ID
        node_id = int(selected_node.replace("基站 ", ""))

        # 获取选中日期和基站的节能数据
        day_energy_data = df[(pd.to_datetime(df['date']).dt.date == selected_date) &
                             (df['node_id'] == node_id)].copy()

        if not day_energy_data.empty:
            # 计算已节约的能耗（energy_saved_kwh列的总和）
            saved_energy = day_energy_data['energy_saved_kwh'].sum() if 'energy_saved_kwh' in day_energy_data.columns else 0

            # 计算实际总能耗
            real_energy = day_energy_data['real_kw'].sum() if 'real_kw' in day_energy_data.columns else 0

            # 计算预测总能耗
            pred_energy = day_energy_data['pred_mean_kw'].sum() if 'pred_mean_kw' in day_energy_data.columns else 0

            # 计算可节约的能耗（预测值 - 实际值，如果预测值 > 实际值）
            potential_save = max(0, pred_energy - real_energy)

            # 计算不可节约的能耗（实际能耗 - 已节约）
            unsaved_energy = max(0, real_energy - saved_energy)

            # 如果数据为0，使用默认值
            if saved_energy == 0 and potential_save == 0 and unsaved_energy == 0:
                saved_energy = 28
                potential_save = 42
                unsaved_energy = 30
        else:
            saved_energy = 28
            potential_save = 42
            unsaved_energy = 30
    else:
        saved_energy = 28
        potential_save = 42
        unsaved_energy = 30

    # 构建饼图数据
    total = saved_energy + potential_save + unsaved_energy
    if total > 0:
        saved_pct = round(saved_energy / total * 100, 1)
        potential_pct = round(potential_save / total * 100, 1)
        unsaved_pct = round(unsaved_energy / total * 100, 1)
    else:
        saved_pct = 28
        potential_pct = 42
        unsaved_pct = 30

    # ========== 关键修复：使用独立的变量名 energy_pie_option ==========
    energy_pie_option = {
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "item",
            "formatter": f"{{a}} <br/>{{b}}: {{c}} kWh ({{d}}%)"
        },
        "legend": {
            "orient": "vertical",
            "right": "2%",
            "top": "center",
            "textStyle": {
                "color": "#00ff88",
                "fontSize": 10
            },
            "itemWidth": 10,
            "itemHeight": 10
        },
        "series": [
            {
                "name": "节能效果",
                "type": "pie",
                "radius": ["35%", "55%"],
                "center": ["40%", "50%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 5,
                    "borderColor": "rgba(10, 10, 26, 0.8)",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "position": "outside",
                    "formatter": "{d}%",
                    "color": "#00ff88",
                    "fontSize": 11
                },
                "labelLine": {
                    "show": True,
                    "length": 8,
                    "length2": 8,
                    "lineStyle": {
                        "color": "#00ff88"
                    }
                },
                "data": [
                    {
                        "value": round(saved_energy, 0),
                        "name": "已节约",
                        "itemStyle": {
                            "color": {
                                "type": "radial",
                                "x": 0.5, "y": 0.5, "r": 0.5,
                                "colorStops": [
                                    {"offset": 0, "color": "#00ff88"},
                                    {"offset": 1, "color": "#00cc66"}
                                ],
                                "global": False
                            }
                        }
                    },
                    {
                        "value": round(potential_save, 0),
                        "name": "可节约",
                        "itemStyle": {
                            "color": {
                                "type": "radial",
                                "x": 0.5, "y": 0.5, "r": 0.5,
                                "colorStops": [
                                    {"offset": 0, "color": "#00aaff"},
                                    {"offset": 1, "color": "#0066cc"}
                                ],
                                "global": False
                            }
                        }
                    },
                    {
                        "value": round(unsaved_energy, 0),
                        "name": "不可节约",
                        "itemStyle": {
                            "color": {
                                "type": "radial",
                                "x": 0.5, "y": 0.5, "r": 0.5,
                                "colorStops": [
                                    {"offset": 0, "color": "#ffd93d"},
                                    {"offset": 1, "color": "#ffaa00"}
                                ],
                                "global": False
                            }
                        }
                    }
                ],
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 255, 136, 0.5)"
                    }
                },
                "animationType": "scale",
                "animationEasing": "elasticOut",
                "animationDelay": 0
            }
        ],
        "animation": True,
        "animationDuration": 1200
    }

    st_echarts(
        options=energy_pie_option,
        height="220px",
        key=f"echarts_energy_pie_{selected_date}_{selected_node}_{strategy}"
    )