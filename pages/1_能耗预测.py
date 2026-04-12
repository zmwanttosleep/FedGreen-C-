import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from streamlit_echarts import st_echarts, JsCode  # type: ignore
import sys
import os
from scipy import stats  # 用于核密度估计
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.sidebar import render_sidebar

st.set_page_config(page_title="能耗预测", layout="wide")

# ==================== 加载真实数据 ====================
@st.cache_data
def load_energy_data(strategy):
    """从CSV加载真实能耗数据，根据策略选择不同文件"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if strategy == "Phase1":
        csv_path = os.path.join(data_dir, 'decision_results_7day_all.csv')
    else:
        csv_path = os.path.join(data_dir, 'decision_results_7day_all_phase2.csv')
    
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # 转换时间字段
            hour_start_map = {0: 0, 1: 6, 2: 12, 3: 18}
            df['datetime'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour_code'].map(hour_start_map), unit='h')
            return df
        except Exception as e:
            st.warning(f"加载数据失败: {e}")
            return None
    return None

# 根据当前策略加载数据
current_strategy = st.session_state.get('energy_predict_strategy', 'Phase1')
df_energy = load_energy_data(current_strategy)

# 渲染共享侧边栏
render_sidebar()

# ==================== 侧边栏 / 策略选择 ====================
# 初始化策略session_state
if 'energy_predict_strategy' not in st.session_state:
    st.session_state.energy_predict_strategy = "Phase1"

def on_strategy_change():
    st.session_state.energy_predict_strategy = st.session_state.strategy_select
    st.rerun()

# 策略选择器
strategy = st.sidebar.selectbox(
    "策略模式",
    options=["Phase1", "Phase2"],
    index=0 if st.session_state.energy_predict_strategy == "Phase1" else 1,
    key='strategy_select',
    on_change=on_strategy_change
)

# 根据策略选择对应的数据文件
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
if st.session_state.energy_predict_strategy == "Phase1":
    csv_path = os.path.join(data_dir, 'decision_results_7day_all.csv')
else:
    csv_path = os.path.join(data_dir, 'decision_results_7day_all_phase2.csv')

# ==================== 侧边栏 / 数据筛选 ====================
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    # 获取日期范围
    min_date = pd.to_datetime(df['date']).min().date()
    max_date = pd.to_datetime(df['date']).max().date()
    
    # 查找12-30的日期作为默认日期
    unique_dates = pd.to_datetime(df['date']).dt.date.unique()
    target_date = None
    for d in unique_dates:
        if d.month == 12 and d.day == 30:
            target_date = d
            break
    # 如果找不到12-30，使用最大日期
    default_date = target_date if target_date else max_date

    # 获取基站列表
    nodes = sorted(df['node_id'].unique())

    # 使用session_state来存储日期和基站
    if 'energy_predict_date' not in st.session_state:
        st.session_state.energy_predict_date = default_date
    if 'energy_predict_node' not in st.session_state:
        if 8004 in nodes:
            st.session_state.energy_predict_node = f"基站 8004"
        else:
            st.session_state.energy_predict_node = f"基站 {nodes[0]}"

    # 定义回调函数 - 当日期或基站改变时更新图表
    def on_date_change():
        st.session_state.energy_predict_date = st.session_state.energy_predict_date_input

    def on_node_change():
        st.session_state.energy_predict_node = st.session_state.energy_predict_node_select

    # 日期选择器
    selected_date = st.sidebar.date_input(
        "历史回测日期",
        value=st.session_state.energy_predict_date,
        min_value=min_date,
        max_value=max_date,
        key='energy_predict_date_input',
        on_change=on_date_change
    )

    # 基站选择器 - 默认选中8004基站
    node_options = [f"基站 {node}" for node in nodes]
    default_index = 0
    if 8004 in nodes:
        default_index = nodes.index(8004)

    selected_node = st.sidebar.selectbox(
        "选择基站",
        options=node_options,
        index=default_index,
        key='energy_predict_node_select',
        on_change=on_node_change
    )



    # 存储数据供主内容区使用（根据选中的基站和日期筛选）
    selected_node_id = int(selected_node.replace('基站 ', ''))
    selected_date_data = df[(pd.to_datetime(df['date']).dt.date == selected_date) & 
                            (df['node_id'] == selected_node_id)]
    if not selected_date_data.empty:
        # 检查列是否存在，使用正确的列名
        if 'real_kw' in selected_date_data.columns:
            st.session_state['energy_total'] = selected_date_data['real_kw'].sum()
        elif 'real' in selected_date_data.columns:
            st.session_state['energy_total'] = selected_date_data['real'].sum()
        else:
            st.session_state['energy_total'] = 0

        # 预测值列兼容Phase1(pred_kw)和Phase2(pred_mean_kw)
        if 'pred_kw' in selected_date_data.columns:
            pred_sum = selected_date_data['pred_kw'].sum()
        elif 'pred_mean_kw' in selected_date_data.columns:
            pred_sum = selected_date_data['pred_mean_kw'].sum()
        elif 'pred' in selected_date_data.columns:
            pred_sum = selected_date_data['pred'].sum()
        else:
            pred_sum = 0

        st.session_state['energy_predict'] = pred_sum
        st.session_state['energy_saved'] = pred_sum - st.session_state['energy_total']
else:
    # 如果文件不存在，使用默认数据
    selected_date = st.session_state.get('energy_predict_date', datetime.now().date())
    selected_node = st.session_state.get('energy_predict_node', '基站 8004')

# 背景CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 25%, #0f3460 50%, #1a1a2e 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
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
    
    .stMetric {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.15), inset 0 0 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: rgba(0, 255, 136, 0.6);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.3), inset 0 0 30px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
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
    
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    [data-testid="stPlotlyChart"] {
        background: transparent;
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
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
    
    .echarts-div {
        position: relative;
        background: transparent;
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 10px;
        box-shadow:
            0 0 20px rgba(0, 255, 136, 0.1),
            inset 0 0 60px rgba(0, 255, 136, 0.05);
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .echarts-div::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(
            45deg,
            rgba(0, 255, 136, 0.3),
            rgba(0, 170, 255, 0.3),
            rgba(138, 43, 226, 0.3),
            rgba(0, 255, 136, 0.3)
        );
        background-size: 400% 400%;
        border-radius: 15px;
        z-index: -1;
        opacity: 0;
        animation: gradientBorder 3s ease infinite;
        transition: opacity 0.4s ease;
    }
    
    .echarts-div::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(0, 255, 136, 0.1),
            transparent
        );
        animation: shimmer 3s infinite;
        pointer-events: none;
    }
    
    .echarts-div:hover {
        border-color: rgba(0, 255, 136, 0.6);
        box-shadow: 
            0 0 40px rgba(0, 255, 136, 0.3),
            inset 0 0 80px rgba(0, 255, 136, 0.1);
        transform: translateY(-3px) scale(1.01);
    }
    
    .echarts-div:hover::before {
        opacity: 1;
    }
    
    @keyframes gradientBorder {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .div-particles {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 0;
    }
    
    .div-particle {
        position: absolute;
        width: 3px;
        height: 3px;
        background: radial-gradient(circle, rgba(0, 255, 136, 0.8) 0%, transparent 70%);
        border-radius: 50%;
        animation: divFloat 15s infinite;
        box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);
    }
    
    @keyframes divFloat {
        0%, 100% {
            transform: translateY(100%) scale(0);
            opacity: 0;
        }
        20% {
            opacity: 0.8;
            transform: scale(1);
        }
        80% {
            opacity: 0.8;
        }
        100% {
            transform: translateY(-100%) scale(0.5);
            opacity: 0;
        }
    }
    
    .pulse-glow {
        animation: pulseGlowEffect 4s ease-in-out infinite;
    }
    
    @keyframes pulseGlowEffect {
        0%, 100% {
            box-shadow: 
                0 0 20px rgba(0, 255, 136, 0.1),
                inset 0 0 60px rgba(0, 255, 136, 0.05);
        }
        50% {
            box-shadow: 
                0 0 35px rgba(0, 255, 136, 0.25),
                inset 0 0 100px rgba(0, 255, 136, 0.1);
        }
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

# 浮动粒子效果
particle_html = '<div class="floating-particles">'
for i in range(20):
    left = f"{i * 5}%"
    delay = f"{i * 0.8}s"
    duration = f"{15 + i % 10}s"
    particle_html += f'<div class="particle" style="left: {left}; animation-delay: {delay}; animation-duration: {duration};"></div>'
particle_html += '</div>'
st.markdown(particle_html, unsafe_allow_html=True)

st.title("基站能耗预测")

# 使用真实数据或模拟数据
if df_energy is not None:
    # 获取选中的基站（从侧边栏存储的session_state中获取）
    selected_node_str = st.session_state.get('energy_predict_node', '基站 8004')
    # 提取基站ID数字
    selected_node = int(selected_node_str.replace('基站 ', ''))
    node_data = df_energy[df_energy['node_id'] == selected_node].sort_values('datetime')

    # 使用侧边栏选择的日期
    # 获取选中日期及前后各1天的数据（共3天）
    selected_date_dt = pd.to_datetime(selected_date)
    date_range_start = selected_date_dt - pd.Timedelta(days=1)
    date_range_end = selected_date_dt + pd.Timedelta(days=1)
    
    # 筛选日期范围内的数据
    recent_data = node_data[(node_data['datetime'] >= date_range_start) & 
                            (node_data['datetime'] <= date_range_end)]

    # 动态获取预测值列名（兼容Phase1和Phase2）
    pred_col = 'pred_kw' if 'pred_kw' in recent_data.columns else 'pred_mean_kw'
    
    # 准备历史数据
    df_hist = pd.DataFrame({
        "timestamp": recent_data['datetime'],
        "实际能耗 (kWh)": recent_data['real_kw'].values
    })

    # 准备预测数据
    df_pred = pd.DataFrame({
        "timestamp": recent_data['datetime'],
        "预测能耗 (kWh)": recent_data[pred_col].values
    })

    # 生成简化的时间标签，只显示日期和时段
    time_labels = []
    prev_date = None
    for i, ts in enumerate(df_hist["timestamp"]):
        curr_date = ts.strftime("%m-%d")
        hour = ts.hour
        
        if curr_date != prev_date:
            # 新的一天，显示日期
            time_labels.append(curr_date)
            prev_date = curr_date
        elif i % 3 == 0:
            # 每隔3个数据点显示一次时间（约每6小时）
            time_labels.append(ts.strftime("%H:%M"))
        else:
            # 其他时间不显示标签
            time_labels.append("")
    all_times = time_labels
else:
    # 使用模拟数据 - 也根据侧边栏日期
    selected_date_dt = pd.to_datetime(selected_date)
    date_range_start = selected_date_dt - pd.Timedelta(days=1)
    
    dates = pd.date_range(start=date_range_start, periods=12, freq="6h")
    df_hist = pd.DataFrame({
        "timestamp": dates,
        "实际能耗 (kWh)": np.random.randint(8000, 15000, len(dates))
    })
    df_pred = pd.DataFrame({
        "timestamp": dates,
        "预测能耗 (kWh)": np.random.randint(8000, 15000, len(dates))
    })

    # 生成简化的时间标签
    time_labels = []
    prev_date = None
    for i, ts in enumerate(df_hist["timestamp"]):
        curr_date = ts.strftime("%m-%d")
        if curr_date != prev_date:
            time_labels.append(curr_date)
            prev_date = curr_date
        elif i % 2 == 0:
            time_labels.append(ts.strftime("%H:%M"))
        else:
            time_labels.append("")
    all_times = time_labels

option = {
    "backgroundColor": "transparent",
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {"type": "cross"}
    },
    "legend": {
        "data": ["实际能耗", "预测能耗"],
        "textStyle": {"color": "#00ff88"},
        "top": 35,
        "left": "center"
    },
    "grid": {
        "left": "10%",
        "right": "10%",
        "top": "20%",
        "bottom": "10%"
    },
    "xAxis": {
        "type": "category",
        "data": all_times,
        "axisLabel": {
            "color": "#00ff88",
            "rotate": 0,
            "interval": "auto",
            "fontSize": 11,
            "hideOverlap": True
        },
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "boundaryGap": False
    },
    "yAxis": {
        "type": "value",
        "name": "能耗 (kWh)",
        "axisLabel": {"color": "#00ff88"},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
    },
    "series": [
        {
            "name": "实际能耗",
            "type": "line",
            "smooth": True,
            "data": df_hist["实际能耗 (kWh)"].tolist(),
            "lineStyle": {"width": 3, "color": "#00ff88"},
            "symbol": "circle",
            "symbolSize": 8,
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0,
                    "y": 0,
                    "x2": 0,
                    "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.6)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0.05)"}
                    ]
                }
            },
            "emphasis": {"focus": "series"}
        },
        {
            "name": "预测能耗",
            "type": "line",
            "smooth": True,
            "data": df_pred["预测能耗 (kWh)"].tolist() if len(df_pred) > 0 else [],
            "lineStyle": {"width": 3, "color": "#ffaa00", "type": "dashed"},
            "symbol": "diamond",
            "symbolSize": 8,
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0,
                    "y": 0,
                    "x2": 0,
                    "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(255, 170, 0, 0.4)"},
                        {"offset": 1, "color": "rgba(255, 170, 0, 0.05)"}
                    ]
                }
            },
            "emphasis": {"focus": "series"}
        }
    ],
    "animation": True,
    "animationDuration": 1500,
    "animationEasing": "cubicOut",
    "title": {
        "text": f"基站{selected_node} 历史能耗 ({selected_date.strftime('%m-%d')}前后)",
        "textStyle": {"color": "#00ff88", "fontSize": 16},
        "left": "center",
        "top": 5
    }
}

# 评估指标 - 使用选中基站的真实数据计算
if df_energy is not None:
    # 动态获取预测值列名（兼容Phase1和Phase2）
    pred_col = 'pred_kw' if 'pred_kw' in node_data.columns else 'pred_mean_kw'
    
    # 使用选中基站的数据进行评估
    y_true = node_data['real_kw'].values
    y_pred = node_data[pred_col].values
    
    # 计算选中基站的能耗指标（使用选中日期当天的数据）
    selected_date_data = node_data[pd.to_datetime(node_data['date']).dt.date == selected_date]
    if not selected_date_data.empty:
        energy_total = selected_date_data['real_kw'].sum()
        energy_predict = selected_date_data[pred_col].sum()
        energy_saved = selected_date_data['energy_saved_kwh'].sum() if 'energy_saved_kwh' in selected_date_data.columns else max(0, energy_predict - energy_total)
    else:
        energy_total = node_data['real_kw'].sum()
        energy_predict = node_data[pred_col].sum()
        energy_saved = max(0, energy_predict - energy_total)
else:
    # 使用模拟数据
    df_eval = df_hist.tail(days*2).copy()
    df_eval["预测能耗 (kWh)"] = np.random.randint(8000, 15000, len(df_eval))
    y_true = df_eval["实际能耗 (kWh)"].values
    y_pred = df_eval["预测能耗 (kWh)"].values
    energy_total = y_true.sum()
    energy_predict = y_pred.sum()
    energy_saved = max(0, energy_predict - energy_total)

rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mae = mean_absolute_error(y_true, y_pred)
smape = np.mean(np.abs(y_pred - y_true) / ((np.abs(y_true) + np.abs(y_pred)) / 2)) * 100

# 创建四列布局：预测精度指标、能耗指标、残差统计指标，图表放到下一行
col_metrics, col_energy, col_residual = st.columns([1, 1, 1])

with col_metrics:
    st.markdown("#### 预测精度")
    # 三个指标卡片垂直排列（缩小高度）
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.2) 0%, rgba(255, 170, 0, 0.1) 100%);
                border: 1px solid rgba(255, 170, 0, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                margin-bottom: 6px;
                cursor: pointer;"
         title="均方根误差 - 衡量预测值与真实值的偏差程度">
        <div style="color: #ffaa00; font-size: 12px; margin-bottom: 2px; font-weight: bold;">RMSE</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{rmse:.2f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(0, 170, 255, 0.1) 100%);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                margin-bottom: 6px;
                cursor: pointer;"
         title="平均绝对误差 - 预测值与真实值绝对差值的平均">
        <div style="color: #00aaff; font-size: 12px; margin-bottom: 2px; font-weight: bold;">MAE</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{mae:.2f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 107, 107, 0.1) 100%);
                border: 1px solid rgba(255, 107, 107, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                cursor: pointer;"
         title="对称平均绝对百分比误差 - 衡量预测精度的百分比指标">
        <div style="color: #ff6b6b; font-size: 12px; margin-bottom: 2px; font-weight: bold;">sMAPE</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{smape:.2f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">%</div>
    </div>
    """, unsafe_allow_html=True)

with col_energy:
    st.markdown("#### 能耗统计")
    # 三个能耗指标卡片垂直排列（缩小高度）
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
                border: 1px solid rgba(76, 175, 80, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                margin-bottom: 6px;
                cursor: pointer;"
         title="当日实际总能耗">
        <div style="color: #4CAF50; font-size: 12px; margin-bottom: 2px; font-weight: bold;">当日总能耗</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{energy_total:,.0f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(156, 39, 176, 0.2) 0%, rgba(156, 39, 176, 0.1) 100%);
                border: 1px solid rgba(156, 39, 176, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                margin-bottom: 6px;
                cursor: pointer;"
         title="当日预测总能耗">
        <div style="color: #9C27B0; font-size: 12px; margin-bottom: 2px; font-weight: bold;">当日预测</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{energy_predict:,.0f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%);
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 6px;
                padding: 8px 6px;
                text-align: center;
                cursor: pointer;"
         title="当日节约能耗">
        <div style="color: #FFC107; font-size: 12px; margin-bottom: 2px; font-weight: bold;">当日节能</div>
        <div style="color: #ffffff; font-size: 18px; font-weight: bold;">{energy_saved:,.0f}</div>
        <div style="color: #c0c0c0; font-size: 10px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

with col_residual:
    st.markdown("#### 残差统计")
    # 四个残差指标卡片垂直排列（缩小高度）
    mean_residual = np.mean(y_true - y_pred)
    std_residual = np.std(y_true - y_pred)
    max_pos_residual = np.max(y_true - y_pred)
    max_neg_residual = np.min(y_true - y_pred)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 255, 136, 0.1) 100%);
                border: 1px solid rgba(0, 255, 136, 0.5);
                border-radius: 6px;
                padding: 6px 4px;
                text-align: center;
                margin-bottom: 4px;
                cursor: pointer;"
         title="整体残差均值">
        <div style="color: #00ff88; font-size: 11px; margin-bottom: 1px; font-weight: bold;">残差均值</div>
        <div style="color: #ffffff; font-size: 16px; font-weight: bold;">{mean_residual:.2f}</div>
        <div style="color: #c0c0c0; font-size: 9px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(0, 170, 255, 0.1) 100%);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 6px;
                padding: 6px 4px;
                text-align: center;
                margin-bottom: 4px;
                cursor: pointer;"
         title="整体残差标准差">
        <div style="color: #00aaff; font-size: 11px; margin-bottom: 1px; font-weight: bold;">残差标准差</div>
        <div style="color: #ffffff; font-size: 16px; font-weight: bold;">{std_residual:.2f}</div>
        <div style="color: #c0c0c0; font-size: 9px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(255, 107, 107, 0.1) 100%);
                border: 1px solid rgba(255, 107, 107, 0.5);
                border-radius: 6px;
                padding: 6px 4px;
                text-align: center;
                margin-bottom: 4px;
                cursor: pointer;"
         title="最大正残差 (低估)">
        <div style="color: #ff6b6b; font-size: 11px; margin-bottom: 1px; font-weight: bold;">最大正残差</div>
        <div style="color: #ffffff; font-size: 16px; font-weight: bold;">{max_pos_residual:.2f}</div>
        <div style="color: #c0c0c0; font-size: 9px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 170, 0, 0.2) 0%, rgba(255, 170, 0, 0.1) 100%);
                border: 1px solid rgba(255, 170, 0, 0.5);
                border-radius: 6px;
                padding: 6px 4px;
                text-align: center;
                cursor: pointer;"
         title="最大负残差 (高估)">
        <div style="color: #ffaa00; font-size: 11px; margin-bottom: 1px; font-weight: bold;">最大负残差</div>
        <div style="color: #ffffff; font-size: 16px; font-weight: bold;">{max_neg_residual:.2f}</div>
        <div style="color: #c0c0c0; font-size: 9px; font-weight: bold;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

# 图表放到下一行
st_echarts(
    options=option,
    height="350px",
    key=f"energy_trend_chart_{selected_date}"
)

# ==================== 残差分布直方图（ECharts科技感样式） ====================
st.subheader("残差分布分析")

# 计算整体残差
residuals = y_true - y_pred

# 计算KDE数据
kde = stats.gaussian_kde(residuals)
x_min, x_max = residuals.min(), residuals.max()
x_grid = np.linspace(x_min, x_max, 100)
kde_values = kde(x_grid)

# 计算直方图数据
hist, bin_edges = np.histogram(residuals, bins=30, density=True)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

mean_residual = np.mean(residuals)
std_residual = np.std(residuals)

# ECharts 残差分布图配置
residual_dist_option = {
    "backgroundColor": "transparent",
    "title": {
        "text": "◉ 整体预测残差分布 (真实值 - 预测值)",
        "left": "center",
        "top": 5,
        "textStyle": {
            "color": "#00ff88",
            "fontSize": 16,
            "fontFamily": "Orbitron",
            "fontWeight": "bold"
        }
    },
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "cross",
            "crossStyle": {"color": "rgba(0, 255, 136, 0.3)"}
        },
        "backgroundColor": "rgba(10, 10, 26, 0.95)",
        "borderColor": "#00ff88",
        "borderWidth": 1,
        "textStyle": {"color": "#ffffff", "fontFamily": "Orbitron"}
    },
    "legend": {
        "data": ["残差分布", "核密度估计"],
        "top": 35,
        "textStyle": {"color": "#00ff88", "fontFamily": "Orbitron"}
    },
    "grid": {
        "left": "10%",
        "right": "10%",
        "top": "20%",
        "bottom": "15%"
    },
    "xAxis": {
        "type": "value",
        "name": "残差 (kWh)",
        "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron"},
        "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron"},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}},
        "min": round(x_min, 2),
        "max": round(x_max, 2)
    },
    "yAxis": {
        "type": "value",
        "name": "概率密度",
        "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron"},
        "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron"},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
    },
    "series": [
        {
            "name": "残差分布",
            "type": "bar",
            "data": [[round(bin_centers[i], 2), round(hist[i], 6)] for i in range(len(hist))],
            "barWidth": "90%",
            "itemStyle": {
                "color": {
                    "type": "linear",
                    "x": 0,
                    "y": 0,
                    "x2": 0,
                    "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.8)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0.2)"}
                    ]
                },
                "borderRadius": [2, 2, 0, 0]
            },
            "animationDuration": 1000,
            "animationEasing": "elasticOut"
        },
        {
            "name": "核密度估计",
            "type": "line",
            "smooth": True,
            "data": [[round(x_grid[i], 2), round(kde_values[i], 6)] for i in range(len(x_grid))],
            "lineStyle": {"width": 3, "color": "#ffaa00"},
            "symbol": "none",
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0,
                    "y": 0,
                    "x2": 0,
                    "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(255, 170, 0, 0.4)"},
                        {"offset": 1, "color": "rgba(255, 170, 0, 0.05)"}
                    ]
                }
            },
            "animationDuration": 1500,
            "animationEasing": "cubicOut"
        },
        {
            "name": "均值",
            "type": "line",
            "markLine": {
                "silent": True,
                "symbol": "none",
                "lineStyle": {"color": "#ff6b6b", "width": 2, "type": "dashed"},
                "label": {
                    "formatter": f"均值: {mean_residual:.2f} kWh",
                    "color": "#ff6b6b",
                    "fontFamily": "Orbitron"
                },
                "data": [{"xAxis": round(mean_residual, 2)}]
            }
        },
        {
            "name": "零误差线",
            "type": "line",
            "markLine": {
                "silent": True,
                "symbol": "none",
                "lineStyle": {"color": "rgba(255, 255, 255, 0.5)", "width": 1.5, "type": "dotted"},
                "label": {
                    "formatter": "零误差线",
                    "color": "rgba(255, 255, 255, 0.7)",
                    "fontFamily": "Orbitron"
                },
                "data": [{"xAxis": 0}]
            }
        },
        {
            "name": "±1σ范围",
            "type": "line",
            "markArea": {
                "silent": True,
                "itemStyle": {"color": "rgba(0, 255, 136, 0.1)"},
                "data": [
                    [
                        {"xAxis": round(mean_residual - std_residual, 2)},
                        {"xAxis": round(mean_residual + std_residual, 2)}
                    ]
                ],
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#00ff88",
                    "fontFamily": "Orbitron",
                    "formatter": f"±1σ ({std_residual:.0f} kWh)"
                }
            }
        }
    ]
}

st_echarts(options=residual_dist_option, height="450px", key="residual_dist_chart")

# 按时段分析
st.subheader("按时段残差分析")

# 确保 df_energy 存在且包含 hour_code
if df_energy is not None:
    # 动态获取预测值列名（兼容Phase1和Phase2）
    pred_col = 'pred_kw' if 'pred_kw' in df_energy.columns else 'pred_mean_kw'
    
    # 使用选中基站的数据进行残差分析
    node_data_residual = df_energy[df_energy['node_id'] == selected_node].copy()
    node_data_residual['residual'] = node_data_residual['real_kw'] - node_data_residual[pred_col]
    
    # 按时段箱线图 - ECharts科技感样式
    hour_labels = {0: '0:00-6:00', 1: '6:00-12:00', 2: '12:00-18:00', 3: '18:00-24:00'}

    # 准备箱线图数据
    boxplot_data = []
    boxplot_categories = []
    for hour in sorted(node_data_residual['hour_code'].unique()):
        subset = node_data_residual[node_data_residual['hour_code'] == hour]['residual']
        # 计算箱线图统计量: [min, Q1, median, Q3, max]
        q1 = subset.quantile(0.25)
        median = subset.median()
        q3 = subset.quantile(0.75)
        iqr = q3 - q1
        lower_fence = max(subset.min(), q1 - 1.5 * iqr)
        upper_fence = min(subset.max(), q3 + 1.5 * iqr)

        boxplot_data.append([
            round(lower_fence, 2),
            round(q1, 2),
            round(median, 2),
            round(q3, 2),
            round(upper_fence, 2)
        ])
        boxplot_categories.append(hour_labels.get(hour, f'时段{hour}'))

    # ECharts 箱线图配置
    boxplot_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 各时段残差分布对比",
            "left": "center",
            "top": 5,
            "textStyle": {
                "color": "#00ff88",
                "fontSize": 16,
                "fontFamily": "Orbitron",
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(10, 10, 26, 0.95)",
            "borderColor": "#00ff88",
            "borderWidth": 1,
            "textStyle": {"color": "#ffffff", "fontFamily": "Orbitron"},
            "formatter": JsCode("""function(param) {
                return '<div style="font-weight:bold;color:#00ff88;margin-bottom:5px;">' + param.name + '</div>' +
                       '<div style="color:#c0c0c0">最大值: <span style="color:#00ff88">' + param.data[5] + ' kWh</span></div>' +
                       '<div style="color:#c0c0c0">上四分位: <span style="color:#00aaff">' + param.data[4] + ' kWh</span></div>' +
                       '<div style="color:#c0c0c0">中位数: <span style="color:#ffaa00">' + param.data[3] + ' kWh</span></div>' +
                       '<div style="color:#c0c0c0">下四分位: <span style="color:#00aaff">' + param.data[2] + ' kWh</span></div>' +
                       '<div style="color:#c0c0c0">最小值: <span style="color:#00ff88">' + param.data[1] + ' kWh</span></div>';
            }""")
        },
        "grid": {
            "left": "10%",
            "right": "10%",
            "top": "20%",
            "bottom": "15%"
        },
        "xAxis": {
            "type": "category",
            "data": boxplot_categories,
            "name": "时段",
            "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron"},
            "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron"},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
            "splitLine": {"show": False}
        },
        "yAxis": {
            "type": "value",
            "name": "残差 (kWh)",
            "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron"},
            "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron"},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
        },
        "series": [
            {
                "name": "残差分布",
                "type": "boxplot",
                "data": boxplot_data,
                "itemStyle": {
                    "color": "rgba(0, 255, 136, 0.3)",
                    "borderColor": "#00ff88",
                    "borderWidth": 2
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "rgba(0, 255, 136, 0.5)",
                        "borderColor": "#00ff88",
                        "borderWidth": 3,
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 255, 136, 0.5)"
                    }
                },
                "animationDuration": 1200,
                "animationEasing": "cubicOut"
            }
        ]
    }

    st_echarts(options=boxplot_option, height="400px", key="residual_boxplot_chart")
    
    # 按时段统计 - 使用ECharts制作科技感表格
    st.subheader("各时段残差统计")

    # 准备残差统计数据（使用选中基站的数据）
    hour_stats_data = []
    for hour in sorted(node_data_residual['hour_code'].unique()):
        sub = node_data_residual[node_data_residual['hour_code'] == hour]['residual']
        hour_stats_data.append({
            '时段': hour_labels.get(hour, f'{hour}'),
            '样本数': len(sub),
            '均值': round(sub.mean(), 2),
            '标准差': round(sub.std(), 2),
            '最小值': round(sub.min(), 2),
            '最大值': round(sub.max(), 2),
            '中位数': round(sub.median(), 2)
        })

    # ECharts 残差统计表格配置
    residual_table_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 各时段残差统计表",
            "left": "center",
            "top": 5,
            "textStyle": {
                "color": "#00ffcc",
                "fontSize": 16,
                "fontFamily": "Orbitron",
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(10, 10, 26, 0.95)",
            "borderColor": "#00ffcc",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff",
                "fontFamily": "Orbitron"
            }
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "top": "15%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": [d['时段'] for d in hour_stats_data],
            "axisLabel": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron",
                "fontSize": 12
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.3)"
                }
            }
        },
        "yAxis": {
            "type": "value",
            "name": "残差 (kWh)",
            "nameTextStyle": {
                "color": "#00ffcc",
                "fontFamily": "Orbitron"
            },
            "axisLabel": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron"
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.3)"
                }
            },
            "splitLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.1)"
                }
            }
        },
        "series": [
            {
                "name": "均值",
                "type": "bar",
                "data": [d['均值'] for d in hour_stats_data],
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "#00ff88"},
                            {"offset": 1, "color": "#00cc6a"}
                        ]
                    },
                    "borderRadius": [4, 4, 0, 0]
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#00ff88",
                    "fontFamily": "Orbitron",
                    "fontSize": 11
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowColor": "rgba(0, 255, 136, 0.5)"
                    }
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            },
            {
                "name": "标准差",
                "type": "line",
                "data": [d['标准差'] for d in hour_stats_data],
                "smooth": True,
                "lineStyle": {
                    "color": "#ffaa00",
                    "width": 3
                },
                "symbol": "circle",
                "symbolSize": 8,
                "itemStyle": {
                    "color": "#ffaa00"
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#ffaa00",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "animationDuration": 1200,
                "animationEasing": "cubicOut"
            }
        ],
        "legend": {
            "data": ["均值", "标准差"],
            "top": 35,
            "textStyle": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron"
            }
        }
    }

    # 显示残差统计图表
    st_echarts(options=residual_table_option, height="300px", key="residual_stats_chart")

    # 详细数据表格 - 使用HTML自定义样式
    # 使用pandas DataFrame显示表格，更可靠
    df_stats = pd.DataFrame(hour_stats_data)
    
    # 自定义样式显示
    st.markdown("""
    <style>
    .residual-stats-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Orbitron', sans-serif;
        font-size: 12px;
    }
    .residual-stats-table th {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 170, 255, 0.2) 100%);
        color: #00ffcc;
        padding: 10px 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid rgba(0, 255, 204, 0.3);
    }
    .residual-stats-table td {
        color: #c0c0c0;
        padding: 8px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.1);
    }
    .residual-stats-table tr:nth-child(even) {
        background: rgba(0, 255, 136, 0.05);
    }
    .residual-stats-table tr:hover {
        background: rgba(0, 255, 136, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 构建HTML表格
    html_table = '<table class="residual-stats-table"><thead><tr>'
    html_table += ''.join([f'<th>{col}</th>' for col in df_stats.columns])
    html_table += '</tr></thead><tbody>'
    
    for _, row in df_stats.iterrows():
        html_table += '<tr>'
        for i, (col, val) in enumerate(row.items()):
            if col == '时段':
                html_table += f'<td style="color: #00ff88; font-weight: bold;">{val}</td>'
            elif col == '均值' and val >= 0:
                html_table += f'<td style="color: #00ff88;">{val:.2f}</td>'
            elif col == '均值' and val < 0:
                html_table += f'<td style="color: #ff6b6b;">{val:.2f}</td>'
            else:
                # 根据数据类型格式化
                if isinstance(val, float):
                    html_table += f'<td>{val:.2f}</td>'
                else:
                    html_table += f'<td>{val}</td>'
        html_table += '</tr>'
    
    html_table += '</tbody></table>'
    st.markdown(html_table, unsafe_allow_html=True)

    # 按时段误差指标 - ECharts科技感图表
    st.subheader("各时段预测精度评估")

    # 准备精度评估数据（使用选中基站的数据）
    hour_metrics_data = []
    # 动态获取预测值列名（兼容Phase1和Phase2）
    pred_col = 'pred_kw' if 'pred_kw' in df_energy.columns else 'pred_mean_kw'
    
    # 获取选中基站的数据
    node_data_metrics = df_energy[df_energy['node_id'] == selected_node]
    
    for hour in sorted(node_data_metrics['hour_code'].unique()):
        sub = node_data_metrics[node_data_metrics['hour_code'] == hour]
        y_true_h = sub['real_kw'].values
        y_pred_h = sub[pred_col].values
        rmse_h = np.sqrt(mean_squared_error(y_true_h, y_pred_h))
        mae_h = mean_absolute_error(y_true_h, y_pred_h)
        smape_h = np.mean(np.abs(y_pred_h - y_true_h) / ((np.abs(y_true_h) + np.abs(y_pred_h)) / 2)) * 100
        hour_metrics_data.append({
            '时段': hour_labels.get(hour, f'{hour}'),
            'RMSE': round(rmse_h, 2),
            'MAE': round(mae_h, 2),
            'sMAPE': round(smape_h, 2)
        })

    # ECharts 精度评估图表配置
    accuracy_chart_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 各时段预测精度评估",
            "left": "center",
            "top": 5,
            "textStyle": {
                "color": "#00ffcc",
                "fontSize": 16,
                "fontFamily": "Orbitron",
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {
                "type": "shadow",
                "shadowStyle": {
                    "color": "rgba(0, 255, 136, 0.1)"
                }
            },
            "backgroundColor": "rgba(10, 10, 26, 0.95)",
            "borderColor": "#00ffcc",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff",
                "fontFamily": "Orbitron"
            },
            "formatter": JsCode("""function(params) {
                var result = '<div style="font-weight:bold;color:#00ffcc;margin-bottom:5px;">' + params[0].name + '</div>';
                for (var i = 0; i < params.length; i++) {
                    var item = params[i];
                    var unit = item.seriesName === 'sMAPE' ? '%' : ' kWh';
                    result += '<div style="color:' + item.color + '">' + item.marker + ' ' + item.seriesName + ': <b>' + item.value + unit + '</b></div>';
                }
                return result;
            }""")
        },
        "legend": {
            "data": ["RMSE", "MAE", "sMAPE"],
            "top": 35,
            "textStyle": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron"
            }
        },
        "grid": {
            "left": "10%",
            "right": "10%",
            "top": "20%",
            "bottom": "15%"
        },
        "xAxis": {
            "type": "category",
            "data": [d['时段'] for d in hour_metrics_data],
            "axisLabel": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron",
                "fontSize": 12
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.3)"
                }
            }
        },
        "yAxis": [
            {
                "type": "value",
                "name": "误差 (kWh)",
                "position": "left",
                "nameTextStyle": {
                    "color": "#00ffcc",
                    "fontFamily": "Orbitron"
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "rgba(0, 255, 204, 0.3)"
                    }
                },
                "splitLine": {
                    "lineStyle": {
                        "color": "rgba(0, 255, 204, 0.1)"
                    }
                }
            },
            {
                "type": "value",
                "name": "sMAPE (%)",
                "position": "right",
                "nameTextStyle": {
                    "color": "#ffaa00",
                    "fontFamily": "Orbitron"
                },
                "axisLabel": {
                    "color": "#ffaa00",
                    "fontFamily": "Orbitron",
                    "formatter": "{value}%"
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "rgba(255, 170, 0, 0.3)"
                    }
                },
                "splitLine": {
                    "show": False
                }
            }
        ],
        "series": [
            {
                "name": "RMSE",
                "type": "bar",
                "data": [d['RMSE'] for d in hour_metrics_data],
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "#00ff88"},
                            {"offset": 1, "color": "#00cc6a"}
                        ]
                    },
                    "borderRadius": [4, 4, 0, 0]
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#00ff88",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            },
            {
                "name": "MAE",
                "type": "bar",
                "data": [d['MAE'] for d in hour_metrics_data],
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "#00ccff"},
                            {"offset": 1, "color": "#0099cc"}
                        ]
                    },
                    "borderRadius": [4, 4, 0, 0]
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#00ccff",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "animationDuration": 1200,
                "animationEasing": "elasticOut"
            },
            {
                "name": "sMAPE",
                "type": "line",
                "yAxisIndex": 1,
                "data": [d['sMAPE'] for d in hour_metrics_data],
                "smooth": True,
                "lineStyle": {
                    "color": "#ffaa00",
                    "width": 3
                },
                "symbol": "diamond",
                "symbolSize": 10,
                "itemStyle": {
                    "color": "#ffaa00"
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "color": "#ffaa00",
                    "fontFamily": "Orbitron",
                    "fontSize": 10,
                    "formatter": "{c}%"
                },
                "animationDuration": 1400,
                "animationEasing": "cubicOut"
            }
        ]
    }

    # 显示精度评估图表
    st_echarts(options=accuracy_chart_option, height="320px", key="accuracy_metrics_chart")

    # 详细精度数据表格 - 使用HTML自定义样式（与残差统计表一致）
    df_accuracy = pd.DataFrame(hour_metrics_data)
    
    st.markdown("""
    <style>
    .accuracy-stats-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Orbitron', sans-serif;
        font-size: 12px;
    }
    .accuracy-stats-table th {
        background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(255, 170, 0, 0.2) 100%);
        color: #00ffcc;
        padding: 10px 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid rgba(0, 255, 204, 0.3);
    }
    .accuracy-stats-table td {
        color: #c0c0c0;
        padding: 8px;
        text-align: center;
        border: 1px solid rgba(0, 255, 204, 0.1);
    }
    .accuracy-stats-table tr:nth-child(even) {
        background: rgba(0, 170, 255, 0.05);
    }
    .accuracy-stats-table tr:hover {
        background: rgba(0, 255, 136, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 构建HTML表格
    html_acc_table = '<table class="accuracy-stats-table"><thead><tr>'
    html_acc_table += ''.join([f'<th>{col}</th>' for col in df_accuracy.columns])
    html_acc_table += '</tr></thead><tbody>'
    
    for _, row in df_accuracy.iterrows():
        html_acc_table += '<tr>'
        for col, val in row.items():
            if col == '时段':
                html_acc_table += f'<td style="color: #00ff88; font-weight: bold;">{val}</td>'
            elif col == 'RMSE':
                html_acc_table += f'<td style="color: #00ff88; font-weight: bold;">{val:.2f}</td>'
            elif col == 'MAE':
                html_acc_table += f'<td style="color: #00ccff; font-weight: bold;">{val:.2f}</td>'
            elif col == 'sMAPE':
                html_acc_table += f'<td style="color: #ffaa00; font-weight: bold;">{val:.2f}%</td>'
            else:
                html_acc_table += f'<td>{val}</td>'
        html_acc_table += '</tr>'
    
    html_acc_table += '</tbody></table>'
    st.markdown(html_acc_table, unsafe_allow_html=True)

else:
    st.info("暂无数据，无法按时段分析")