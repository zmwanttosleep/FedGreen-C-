import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os
from streamlit_echarts import st_echarts, JsCode
from collections import Counter

# 添加项目根目录到路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from components.sidebar import render_sidebar

st.set_page_config(page_title="节能决策", layout="wide")

# 渲染共享侧边栏
render_sidebar()

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

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 26, 0.95) 0%, rgba(15, 52, 96, 0.9) 100%);
        border-right: 1px solid rgba(0, 255, 136, 0.3);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
    }

    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
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
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.6) 0%, rgba(26, 26, 46, 0.7) 100%);
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

    .stDataFrame {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.6) 0%, rgba(26, 26, 46, 0.7) 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
    }

    .stButton>button {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 10px;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.1);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        border-color: rgba(0, 255, 136, 0.6);
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.3);
        transform: translateY(-2px);
    }
    
    /* 甘特图容器样式 */
    .gantt-container {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.3) 0%, rgba(26, 26, 46, 0.4) 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 15px;
        margin-top: 10px;
    }
    
    .gantt-legend {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 15px;
        padding: 12px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 8px;
        border: 1px solid rgba(0, 255, 136, 0.2);
    }
    
    .gantt-legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #c0c0c0;
        font-size: 12px;
    }
    
    .gantt-legend-color {
        width: 20px;
        height: 12px;
        border-radius: 3px;
    }
    
    .gantt-time-labels {
        display: flex;
        justify-content: space-between;
        padding: 0 10%;
        margin-top: 10px;
        color: #00ff88;
        font-size: 11px;
        font-family: 'Orbitron', sans-serif;
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

# ==================== 加载数据 ====================
def load_data(strategy_phase):
    """根据策略模式加载对应的数据文件"""
    if strategy_phase == "Phase1":
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all.csv')
    elif strategy_phase == "Phase2":
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all_phase2.csv')
    elif strategy_phase == "Phase3":
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all_phase3.csv')
    elif strategy_phase == "双模型集成":
        # 双模型集成使用 Phase2 数据
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all_phase2.csv')
    elif strategy_phase == "三模型集成":
        # 三模型集成使用 Phase3 数据
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all_phase3.csv')
    else:
        # 默认使用 Phase2 数据
        csv_path = os.path.join(base_dir, 'data', 'decision_results_7day_all_phase2.csv')
    
    df = pd.read_csv(csv_path)
    # 转换时间字段 - 严格6小时粒度
    hour_start_map = {0: 0, 1: 6, 2: 12, 3: 18}
    df['start_dt'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour_code'].map(hour_start_map), unit='h')
    df['end_dt'] = df['start_dt'] + pd.Timedelta(hours=6)
    df['datetime'] = df['start_dt']
    # 决策中文映射
    decision_map = {'Migration': '负载均衡', 'Normal': '正常运行', 'Sleep': '休眠'}
    df['decision_cn'] = df['decision'].map(decision_map).fillna('正常运行')
    return df

# 策略对比数据（来自日志）
comparison_data = {
    "策略": ["Phase1", "Phase2", "Phase3", "双模型集成", "三模型集成"],
    "准确率 (%)": [77.75, 77.45, 78.82, 80.53, 81.86],
    "节能 (M kWh)": [249.34, 258.08, 238.12, 258.0, 675.0]
}

# ==================== 侧边栏 / 阈值参数面板 ====================
st.sidebar.markdown("## 阈值参数面板")
# 阈值调节 (根据数据范围调整)
sleep_th = st.sidebar.slider("休眠阈值 (kWh)", min_value=0, max_value=50000, value=20000, step=1000)
mig_th = st.sidebar.slider("迁移阈值 (kWh)", min_value=0, max_value=150000, value=80000, step=1000)
# 滑动窗口大小调节
window_size = st.sidebar.slider("滑动窗口大小", min_value=1, max_value=30, value=7, step=1)
# 策略模式选择 - 放在数据加载之前
strategy = st.sidebar.selectbox("策略模式", ["Phase1", "Phase2", "Phase3", "双模型集成", "三模型集成"])

# 根据策略模式加载对应的数据
df_raw = load_data(strategy)
nodes = sorted(df_raw['node_id'].unique())

# 使用数据中的最新日期作为回测日期默认值，限制日期范围为2024年9月27日到2024年12月31日
latest_date_for_backtest = pd.to_datetime(df_raw['date']).max().date()
min_date = pd.to_datetime(df_raw['date']).min().date()
max_date = pd.to_datetime(df_raw['date']).max().date()

# 使用session_state来存储日期，确保切换策略时日期在有效范围内
if 'backtest_date' not in st.session_state:
    st.session_state.backtest_date = latest_date_for_backtest
elif st.session_state.backtest_date < min_date or st.session_state.backtest_date > max_date:
    # 如果当前日期不在新数据范围内，重置为最新日期
    st.session_state.backtest_date = latest_date_for_backtest

backtest_date = st.sidebar.date_input(
    "历史回测日期", 
    value=st.session_state.backtest_date,
    min_value=min_date, 
    max_value=max_date,
    key='backtest_date_input'
)
# 更新session_state
st.session_state.backtest_date = backtest_date

# ==================== 主页面 ====================
st.title("边缘智能节能策略")

# 页面顶部指标卡片 - 科技风样式
# 兼容不同数据文件的列名
confidence = df_raw['calibrated_confidence'].mean() if 'calibrated_confidence' in df_raw.columns else (df_raw['raw_confidence'].mean() if 'raw_confidence' in df_raw.columns else 0.75)
# 兼容不同数据文件的列名（Phase1使用pred_kw，Phase2/3使用pred_mean_kw）
pred_col_main = 'pred_mean_kw' if 'pred_mean_kw' in df_raw.columns else ('pred_kw' if 'pred_kw' in df_raw.columns else None)
efficiency = df_raw['energy_saved_kwh'].sum() / df_raw[pred_col_main].sum() if 'energy_saved_kwh' in df_raw.columns and pred_col_main else 0
# 根据当前策略模式获取决策准确率
accuracy_map = {
    "Phase1": 77.75,
    "Phase2": 77.45,
    "Phase3": 78.82,
    "双模型集成": 80.53,
    "三模型集成": 81.86
}
decision_accuracy = accuracy_map.get(strategy, 77.45)

st.markdown("""
<style>
.tech-metric-card {
    background: linear-gradient(135deg, rgba(0, 255, 204, 0.1) 0%, rgba(0, 170, 255, 0.05) 100%);
    border: 1px solid rgba(0, 255, 204, 0.3);
    border-radius: 12px;
    padding: 20px 15px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.tech-metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ffcc, transparent);
}
.tech-metric-card:hover {
    border-color: rgba(0, 255, 204, 0.6);
    box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
    transform: translateY(-2px);
}
.tech-metric-label {
    color: #00ffcc;
    font-size: 16px;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.tech-metric-value {
    color: #ffffff;
    font-size: 36px;
    font-weight: bold;
    text-shadow: 0 0 15px rgba(0, 255, 204, 0.5);
}
.tech-metric-unit {
    color: #c0c0c0;
    font-size: 14px;
    margin-left: 4px;
}
</style>
""", unsafe_allow_html=True)

col_metric1, col_metric2, col_metric3 = st.columns(3)
with col_metric1:
    st.markdown(f"""
    <div class="tech-metric-card">
        <div class="tech-metric-label">决策置信度</div>
        <div class="tech-metric-value" style="color:#00ff88">{confidence:.1%}</div>
    </div>
    """, unsafe_allow_html=True)
with col_metric2:
    st.markdown(f"""
    <div class="tech-metric-card">
        <div class="tech-metric-label">策略效率</div>
        <div class="tech-metric-value" style="color:#00aaff">{efficiency:.1%}</div>
    </div>
    """, unsafe_allow_html=True)
with col_metric3:
    st.markdown(f"""
    <div class="tech-metric-card">
        <div class="tech-metric-label">决策准确率</div>
        <div class="tech-metric-value" style="color:#ffaa00">{decision_accuracy:.2f}<span class="tech-metric-unit">%</span></div>
    </div>
    """, unsafe_allow_html=True)

# 基于侧边栏选择的回测日期计算数据
selected_date = backtest_date  # 来自侧边栏的日期选择
selected_month = selected_date.month
selected_year = selected_date.year

# 选中日期的数据
selected_day_data = df_raw[pd.to_datetime(df_raw['date']).dt.date == selected_date]
# 选中月份的数据（截止到选中日期）
selected_month_data = df_raw[(pd.to_datetime(df_raw['date']).dt.month == selected_month) & 
                             (pd.to_datetime(df_raw['date']).dt.year == selected_year) &
                             (pd.to_datetime(df_raw['date']).dt.date <= selected_date)]
# 截止到选中日期的累计数据
selected_cumulative_data = df_raw[pd.to_datetime(df_raw['date']).dt.date <= selected_date]

# 计算各指标值
day_saved = selected_day_data['energy_saved_kwh'].sum()
month_saved = selected_month_data['energy_saved_kwh'].sum()
cost_saved = selected_cumulative_data['cost_saved_eur'].sum()
carbon_saved = selected_cumulative_data['carbon_saved_kg'].sum()/1000

# 创建三列布局：左侧节能收益仪表盘，右侧历史回测卡片，最右侧节能效果对比图
dashboard_col, backtest_col, chart_col = st.columns([1, 0.8, 2])

with dashboard_col:
    # 1. 节能收益仪表盘（四个指标垂直排列）- 科技感动态设计
    st.markdown('<h3 style="margin-bottom: 15px; color: #00ffcc; font-size: 24px;">节能收益</h3>', unsafe_allow_html=True)

    # 添加动态CSS样式
    st.markdown("""
    <style>
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
        50% { box-shadow: 0 0 25px rgba(0, 255, 136, 0.6); }
    }
    @keyframes scan-line {
        0% { transform: translateY(-100%); }
        100% { transform: translateY(100%); }
    }
    @keyframes number-scroll {
        0% { transform: translateY(20px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
    }
    .tech-card {
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .tech-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    .tech-card:hover::before {
        left: 100%;
    }
    .tech-card:hover {
        transform: translateY(-3px) scale(1.02);
        filter: brightness(1.1);
    }
    .scan-effect {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.8), transparent);
        animation: scan-line 2s linear infinite;
    }
    .number-animate {
        animation: number-scroll 0.6s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

    # 卡片1: 今日累计节省 - 绿色主题
    st.markdown(f"""
    <div class="tech-card" style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.25) 0%, rgba(76, 175, 80, 0.05) 100%);
                border: 1px solid rgba(76, 175, 80, 0.6);
                border-radius: 12px;
                padding: 15px 10px;
                text-align: center;
                margin-bottom: 12px;
                cursor: pointer;
                width: 100%;
                box-sizing: border-box;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="显示选中日期当天的节能电量&#10;日期: {selected_date.strftime('%Y-%m-%d')}">
        <div class="scan-effect"></div>
        <div style="color: #4CAF50; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">今日累计节省</div>
        <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">{day_saved:,.0f}</div>
        <div style="color: rgba(76, 175, 80, 0.8); font-size: 16px; margin-top: 5px;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    # 卡片2: 本月累计节省 - 蓝色主题
    st.markdown(f"""
    <div class="tech-card" style="background: linear-gradient(135deg, rgba(33, 150, 243, 0.25) 0%, rgba(33, 150, 243, 0.05) 100%);
                border: 1px solid rgba(33, 150, 243, 0.6);
                border-radius: 12px;
                padding: 15px 10px;
                text-align: center;
                margin-bottom: 12px;
                cursor: pointer;
                width: 100%;
                box-sizing: border-box;
                box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="显示选中月份累计节能电量&#10;月份: {selected_year}年{selected_month}月&#10;截至: {selected_date.strftime('%Y-%m-%d')}">
        <div class="scan-effect"></div>
        <div style="color: #2196F3; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">本月累计节省</div>
        <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(33, 150, 243, 0.5);">{month_saved:,.0f}</div>
        <div style="color: rgba(33, 150, 243, 0.8); font-size: 16px; margin-top: 5px;">kWh</div>
    </div>
    """, unsafe_allow_html=True)

    # 卡片3: 节省电费 - 金色主题
    st.markdown(f"""
    <div class="tech-card" style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.25) 0%, rgba(255, 193, 7, 0.05) 100%);
                border: 1px solid rgba(255, 193, 7, 0.6);
                border-radius: 12px;
                padding: 15px 10px;
                text-align: center;
                margin-bottom: 12px;
                cursor: pointer;
                width: 100%;
                box-sizing: border-box;
                box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="显示截至选中日期的累计电费节省&#10;截至: {selected_date.strftime('%Y-%m-%d')}">
        <div class="scan-effect"></div>
        <div style="color: #FFC107; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">累计节省电费</div>
        <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);">{cost_saved:,.2f}</div>
        <div style="color: rgba(255, 193, 7, 0.8); font-size: 16px; margin-top: 5px;">€</div>
    </div>
    """, unsafe_allow_html=True)

    # 卡片4: 减少碳排放 - 紫色主题
    st.markdown(f"""
    <div class="tech-card" style="background: linear-gradient(135deg, rgba(156, 39, 176, 0.25) 0%, rgba(156, 39, 176, 0.05) 100%);
                border: 1px solid rgba(156, 39, 176, 0.6);
                border-radius: 12px;
                padding: 15px 10px;
                text-align: center;
                cursor: pointer;
                width: 100%;
                box-sizing: border-box;
                box-shadow: 0 4px 15px rgba(156, 39, 176, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="显示截至选中日期的累计碳减排量&#10;截至: {selected_date.strftime('%Y-%m-%d')}">
        <div class="scan-effect"></div>
        <div style="color: #9C27B0; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">减少碳排放</div>
        <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(156, 39, 176, 0.5);">{carbon_saved * 1000:,.0f}</div>
        <div style="color: rgba(156, 39, 176, 0.8); font-size: 16px; margin-top: 5px;">kg CO₂</div>
    </div>
    """, unsafe_allow_html=True)

    # 准备环形图数据 - ECharts 科技版
    donut_data = {
        '指标': ['今日节省', '本月节省', '电费节省', '碳减排'],
        '数值': [day_saved, month_saved, cost_saved * 10, carbon_saved * 1000],
        '原始值': [f'{day_saved:.0f} kWh', f'{month_saved:.0f} kWh', f'{cost_saved:.2f} €', f'{carbon_saved * 1000:.0f} kg'],
        '颜色': ['#00ff88', '#00ccff', '#ffdd00', '#cc66ff']
    }
    
    # ECharts 环形图配置 - 超科技感
    pie_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 节能收益",
            "left": "center",
            "top": 10,
            "textStyle": {
                "color": "#4ddba3",
                "fontSize": 16,
                "fontFamily": "Orbitron",
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "backgroundColor": "rgba(10, 10, 30, 0.95)",
            "borderColor": "#00ff88",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff",
                "fontFamily": "Orbitron"
            },
            "formatter": JsCode("""function(params) {
                return '<div style="font-weight:bold;color:' + params.color + ';margin-bottom:5px;">' + params.name + '</div>' +
                       '<div style="color:#00ffcc">占比: ' + params.percent + '%</div>' +
                       '<div style="color:#ffffff">数值: ' + params.data.original + '</div>';
            }""")
        },
        "series": [
            # 外层发光环
            {
                "type": "pie",
                "radius": ["68%", "72%"],
                "center": ["50%", "55%"],
                "silent": True,
                "itemStyle": {
                    "color": "rgba(0, 255, 136, 0.05)"
                },
                "data": [{"value": 1}],
                "animation": False
            },
            # 中层发光环
            {
                "type": "pie",
                "radius": ["62%", "66%"],
                "center": ["50%", "55%"],
                "silent": True,
                "itemStyle": {
                    "color": "rgba(0, 255, 136, 0.08)"
                },
                "data": [{"value": 1}],
                "animation": False
            },
            # 内层发光环
            {
                "type": "pie",
                "radius": ["56%", "60%"],
                "center": ["50%", "55%"],
                "silent": True,
                "itemStyle": {
                    "color": "rgba(0, 255, 136, 0.12)"
                },
                "data": [{"value": 1}],
                "animation": False
            },
            # 主数据环
            {
                "type": "pie",
                "radius": ["40%", "52%"],
                "center": ["50%", "55%"],
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 8,
                    "borderColor": "#0a0a14",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "position": "outside",
                    "formatter": "{b}\n{d}%",
                    "color": "#e0e0e0",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "labelLine": {
                    "show": True,
                    "length": 15,
                    "length2": 10,
                    "lineStyle": {
                        "color": "rgba(255, 255, 255, 0.3)"
                    }
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 12,
                        "fontWeight": "bold"
                    },
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 255, 136, 0.5)"
                    }
                },
                "data": [
                    {
                        "value": day_saved,
                        "name": "今日节省",
                        "original": f"{day_saved:.0f} kWh",
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#4ddba3"},
                                    {"offset": 1, "color": "#3bb88a"}
                                ]
                            },
                            "shadowBlur": 15,
                            "shadowColor": "rgba(0, 255, 136, 0.6)"
                        }
                    },
                    {
                        "value": month_saved,
                        "name": "本月节省",
                        "original": f"{month_saved:.0f} kWh",
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#6bc4e0"},
                                    {"offset": 1, "color": "#4a9fc4"}
                                ]
                            },
                            "shadowBlur": 15,
                            "shadowColor": "rgba(0, 204, 255, 0.6)"
                        }
                    },
                    {
                        "value": cost_saved * 10,
                        "name": "电费节省",
                        "original": f"{cost_saved:.2f} €",
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#e8d068"},
                                    {"offset": 1, "color": "#d4b84a"}
                                ]
                            },
                            "shadowBlur": 15,
                            "shadowColor": "rgba(255, 221, 0, 0.6)"
                        }
                    },
                    {
                        "value": carbon_saved * 1000,
                        "name": "碳减排",
                        "original": f"{carbon_saved * 1000:.0f} kg",
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0, "y": 0, "x2": 0, "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": "#b88cd9"},
                                    {"offset": 1, "color": "#9a6bb8"}
                                ]
                            },
                            "shadowBlur": 15,
                            "shadowColor": "rgba(204, 102, 255, 0.6)"
                        }
                    }
                ],
                "animationType": "scale",
                "animationEasing": "elasticOut",
                "animationDelay": 500
            }
        ],
        "graphic": [
            # 中心文字
            {
                "type": "text",
                "left": "center",
                "top": "52%",
                "style": {
                    "text": f"{(day_saved + month_saved + cost_saved * 10 + carbon_saved * 1000) / 1000:.1f}K",
                    "textAlign": "center",
                    "fill": "#4ddba3",
                    "fontSize": 18,
                    "fontFamily": "Orbitron",
                    "fontWeight": "bold"
                }
            },
            {
                "type": "text",
                "left": "center",
                "top": "58%",
                "style": {
                    "text": "TOTAL",
                    "textAlign": "center",
                    "fill": "#555555",
                    "fontSize": 10,
                    "fontFamily": "Orbitron",
                    "letterSpacing": 3
                }
            }
        ]
    }

with backtest_col:
    # 历史回测结果卡片（四个指标垂直排列）
    st.markdown('<h3 style="margin-bottom: 15px; color: #00ffcc; font-size: 24px;">历史回测</h3>', unsafe_allow_html=True)
    
    backtest_df = df_raw[pd.to_datetime(df_raw['date']).dt.date == backtest_date]
    if not backtest_df.empty:
        total_real = backtest_df['real_kw'].sum()
        total_saved = backtest_df['energy_saved_kwh'].sum()
        saved_percent = total_saved / (total_real + total_saved) * 100
        correct_rate = backtest_df['decision_correct'].mean() * 100
        
        # 卡片 1: 实际总能耗
        st.markdown(f"""
        <div class="tech-card" style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.25) 0%, rgba(76, 175, 80, 0.05) 100%);
                    border: 1px solid rgba(76, 175, 80, 0.6);
                    border-radius: 12px;
                    padding: 15px 10px;
                    text-align: center;
                    margin-bottom: 12px;
                    width: 100%;
                    box-sizing: border-box;
                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
             title="历史回测日期的实际总能耗">
            <div class="scan-effect"></div>
            <div style="color: #4CAF50; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">实际总能耗</div>
            <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);">{total_real:,.0f}</div>
            <div style="color: rgba(76, 175, 80, 0.8); font-size: 16px; margin-top: 5px;">kWh</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 卡片 2: 模拟节省量
        st.markdown(f"""
        <div class="tech-card" style="background: linear-gradient(135deg, rgba(33, 150, 243, 0.25) 0%, rgba(33, 150, 243, 0.05) 100%);
                    border: 1px solid rgba(33, 150, 243, 0.6);
                    border-radius: 12px;
                    padding: 15px 10px;
                    text-align: center;
                    margin-bottom: 12px;
                    width: 100%;
                    box-sizing: border-box;
                    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
             title="历史回测模拟节省的电量">
            <div class="scan-effect"></div>
            <div style="color: #2196F3; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">模拟节省量</div>
            <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(33, 150, 243, 0.5);">{total_saved:,.0f}</div>
            <div style="color: rgba(33, 150, 243, 0.8); font-size: 16px; margin-top: 5px;">kWh</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 卡片 3: 节省百分比
        st.markdown(f"""
        <div class="tech-card" style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.25) 0%, rgba(255, 193, 7, 0.05) 100%);
                    border: 1px solid rgba(255, 193, 7, 0.6);
                    border-radius: 12px;
                    padding: 12px 8px;
                    text-align: center;
                    margin-bottom: 8px;
                    width: 100%;
                    box-sizing: border-box;
                    box-shadow: 0 4px 15px rgba(255, 193, 7, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="历史回测的节能百分比">
            <div class="scan-effect"></div>
            <div style="color: #FFC107; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">节省百分比</div>
            <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(255, 193, 7, 0.5);">{saved_percent:.1f}</div>
            <div style="color: rgba(255, 193, 7, 0.8); font-size: 16px; margin-top: 5px;">%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 卡片 4: 决策正确率
        st.markdown(f"""
        <div class="tech-card" style="background: linear-gradient(135deg, rgba(156, 39, 176, 0.25) 0%, rgba(156, 39, 176, 0.05) 100%);
                    border: 1px solid rgba(156, 39, 176, 0.6);
                    border-radius: 12px;
                    padding: 12px 8px;
                    text-align: center;
                    width: 100%;
                    box-sizing: border-box;
                    box-shadow: 0 4px 15px rgba(156, 39, 176, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);"
         title="历史回测的决策正确率">
            <div class="scan-effect"></div>
            <div style="color: #9C27B0; font-size: 16px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">决策正确率</div>
            <div class="number-animate" style="color: #ffffff; font-size: 32px; font-weight: bold; text-shadow: 0 0 10px rgba(156, 39, 176, 0.5);">{correct_rate:.1f}</div>
            <div style="color: rgba(156, 39, 176, 0.8); font-size: 16px; margin-top: 5px;">%</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("所选日期无数据")

# 在历史回测卡片下方添加一行：节能收益饼图和策略性能对比图
pie_chart_col, strategy_col = st.columns([1, 2])

with pie_chart_col:
    # 节能收益饼图 - ECharts 超科技感设计
    st_echarts(options=pie_option, height="340px", key="energy_saving_echarts")

with strategy_col:
    # 策略性能对比图 - ECharts 科技感动态版
    strategies = comparison_data['策略']
    accuracy = comparison_data['准确率 (%)']
    energy = comparison_data['节能 (M kWh)']
    
    echarts_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 策略性能对比",
            "left": "center",
            "top": 10,
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
                "type": "shadow",
                "shadowStyle": {
                    "color": "rgba(0, 255, 136, 0.1)"
                }
            },
            "backgroundColor": "rgba(10, 10, 30, 0.95)",
            "borderColor": "#00ff88",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff",
                "fontFamily": "Orbitron"
            },
            "formatter": JsCode("""function(params) {
                var result = '<div style="font-weight:bold;color:#00ff88;margin-bottom:5px;">' + params[0].name + '</div>';
                for (var i = 0; i < params.length; i++) {
                    var item = params[i];
                    result += '<div style="color:' + item.color + '">' + item.marker + ' ' + item.seriesName + ': <b>' + item.value + '</b></div>';
                }
                return result;
            }""")
        },
        "legend": {
            "data": ["准确率 (%)", "节能 (M kWh)"],
            "top": 40,
            "textStyle": {
                "color": "#e0e0e0",
                "fontFamily": "Orbitron",
                "fontSize": 10
            }
        },
        "grid": {
            "left": "10%",
            "right": "10%",
            "bottom": "15%",
            "top": "25%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": strategies,
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(255, 255, 255, 0.2)"
                }
            },
            "axisLabel": {
                "color": "#e0e0e0",
                "fontFamily": "Orbitron",
                "fontSize": 10,
                "rotate": 15
            },
            "axisTick": {
                "show": False
            }
        },
        "yAxis": [
            {
                "type": "value",
                "name": "准确率 (%)",
                "min": 75,
                "max": 85,
                "position": "left",
                "axisLine": {
                    "show": True,
                    "lineStyle": {
                        "color": "#00ff88"
                    }
                },
                "axisLabel": {
                    "color": "#00ff88",
                    "fontFamily": "Orbitron",
                    "fontSize": 9
                },
                "splitLine": {
                    "lineStyle": {
                        "color": "rgba(0, 255, 136, 0.1)"
                    }
                }
            },
            {
                "type": "value",
                "name": "节能 (M kWh)",
                "min": 0,
                "max": 800,
                "position": "right",
                "axisLine": {
                    "show": True,
                    "lineStyle": {
                        "color": "#ffd700"
                    }
                },
                "axisLabel": {
                    "color": "#ffd700",
                    "fontFamily": "Orbitron",
                    "fontSize": 9
                },
                "splitLine": {
                    "lineStyle": {
                        "color": "rgba(255, 215, 0, 0.1)"
                    }
                }
            }
        ],
        "series": [
            {
                "name": "准确率 (%)",
                "type": "bar",
                "data": accuracy,
                "yAxisIndex": 0,
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
                    "borderRadius": [4, 4, 0, 0],
                    "shadowColor": "rgba(0, 255, 136, 0.5)",
                    "shadowBlur": 10,
                    "shadowOffsetY": 3
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}%",
                    "color": "#00ffcc",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowColor": "rgba(0, 255, 136, 0.8)",
                        "shadowBlur": 20
                    }
                },
                "animationDuration": 1500,
                "animationEasing": "elasticOut"
            },
            {
                "name": "节能 (M kWh)",
                "type": "bar",
                "data": energy,
                "yAxisIndex": 1,
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(255, 215, 0, 0.8)"},
                            {"offset": 1, "color": "rgba(255, 170, 0, 0.6)"}
                        ]
                    },
                    "borderRadius": [4, 4, 0, 0],
                    "shadowColor": "rgba(255, 215, 0, 0.4)",
                    "shadowBlur": 8,
                    "shadowOffsetY": 2
                },
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}",
                    "color": "#ffd700",
                    "fontFamily": "Orbitron",
                    "fontSize": 10
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowColor": "rgba(255, 215, 0, 0.8)",
                        "shadowBlur": 15
                    }
                },
                "animationDuration": 1500,
                "animationEasing": "elasticOut",
                "animationDelay": 200
            }
        ]
    }
    
    st_echarts(options=echarts_option, height="320px", key="strategy_comparison_echarts")

with chart_col:
    # 2. 节能效果对比图（基于选中日期）- 科技感优化
    st.subheader("节能效果对比")

    # 获取选中日期的前后各1天数据用于对比（共3天）
    selected_date_dt = pd.to_datetime(selected_date)
    date_range_start = selected_date_dt - pd.Timedelta(days=1)
    date_range_end = selected_date_dt + pd.Timedelta(days=1)

    plot_df = df_raw[(df_raw['datetime'] >= date_range_start) &
                     (df_raw['datetime'] <= date_range_end)].sort_values('datetime')

    if len(plot_df) > 0:
        # 检查需要的列是否存在（兼容不同数据文件的列名）
        has_pred = 'pred_mean_kw' in plot_df.columns or 'pred_kw' in plot_df.columns
        has_real = 'real_kw' in plot_df.columns
        has_saved = 'energy_saved_kwh' in plot_df.columns
        
        # 确定实际使用的列名
        pred_col = 'pred_mean_kw' if 'pred_mean_kw' in plot_df.columns else ('pred_kw' if 'pred_kw' in plot_df.columns else None)
        
        # 按时间聚合，计算所有节点的总能耗
        agg_dict = {}
        if pred_col:
            agg_dict[pred_col] = 'sum'
        if has_real:
            agg_dict['real_kw'] = 'sum'
        if has_saved:
            agg_dict['energy_saved_kwh'] = 'sum'
        
        if len(agg_dict) == 0:
            st.warning("数据文件缺少必要的列，无法显示对比图")
        else:
            plot_df_grouped = plot_df.groupby('datetime').agg(agg_dict).reset_index()
            
            fig_compare = go.Figure()
            
            # 确定Y轴最大值
            y_max = 0
            if has_pred and pred_col in plot_df_grouped.columns:
                y_max = max(y_max, plot_df_grouped[pred_col].max())
            if has_real and 'real_kw' in plot_df_grouped.columns:
                y_max = max(y_max, plot_df_grouped['real_kw'].max())
            
            # 添加网格背景效果
            if y_max > 0:
                fig_compare.add_hrect(y0=0, y1=y_max * 1.1,
                                      fillcolor="rgba(0, 255, 136, 0.02)", line_width=0)
            
            # 无策略预测能耗（霓虹红色效果）
            if has_pred and pred_col in plot_df_grouped.columns:
                fig_compare.add_trace(go.Scatter(
                    x=plot_df_grouped['datetime'],
                    y=plot_df_grouped[pred_col],
                    mode='lines',
                    name='无策略（预测能耗）',
                    line=dict(color='#ff3366', width=3, shape='spline'),
                    fill='tonexty',
                    fillcolor='rgba(255, 51, 102, 0.15)',
                    hovertemplate='<b>无策略预测</b><br>时间: %{x}<br>功率: %{y:.0f} kW<extra></extra>'
                ))
            
            # 执行策略实际能耗（霓虹青色效果）
            if has_real and 'real_kw' in plot_df_grouped.columns:
                fig_compare.add_trace(go.Scatter(
                    x=plot_df_grouped['datetime'],
                    y=plot_df_grouped['real_kw'],
                    mode='lines',
                    name='执行策略（实际能耗）',
                    line=dict(color='#00ffcc', width=3, shape='spline'),
                    fill='tozeroy',
                    fillcolor='rgba(0, 255, 204, 0.2)',
                    hovertemplate='<b>执行策略</b><br>时间: %{x}<br>功率: %{y:.0f} kW<extra></extra>'
                ))

            # 添加发光效果标记点
            if has_real and 'real_kw' in plot_df_grouped.columns:
                fig_compare.add_trace(go.Scatter(
                    x=plot_df_grouped['datetime'],
                    y=plot_df_grouped['real_kw'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='#00ffcc',
                        line=dict(width=2, color='#ffffff'),
                        symbol='circle'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 添加选中日期的高亮区域（科技感边框）
            fig_compare.add_vrect(
                x0=selected_date_dt,
                x1=selected_date_dt + pd.Timedelta(days=1),
                fillcolor="rgba(0, 255, 204, 0.08)",
                line=dict(color='rgba(0, 255, 204, 0.5)', width=2, dash='dash'),
                layer="below",
                annotation_text="选中日期",
                annotation_position="top left",
                annotation_font=dict(color='#00ffcc', size=12)
            )
            
            # 计算并显示节能统计
            total_saved = plot_df_grouped['energy_saved_kwh'].sum() if has_saved and 'energy_saved_kwh' in plot_df_grouped.columns else 0
            pred_sum = plot_df_grouped[pred_col].sum() if has_pred and pred_col in plot_df_grouped.columns else 0
            avg_efficiency = (total_saved / pred_sum * 100) if pred_sum > 0 else 0

            fig_compare.update_layout(
            title=dict(
                text=f"<b>能耗对比分析</b><br><sup style='color:#00ffcc'>选中日期节能: {total_saved:,.0f} kWh | 节能效率: {avg_efficiency:.1f}%</sup>",
                font=dict(size=16, color='#00ffcc'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title=dict(text='时间', font=dict(color='#00ffcc')),
                gridcolor='rgba(0, 255, 204, 0.1)',
                linecolor='rgba(0, 255, 204, 0.3)',
                tickfont=dict(color='#c0c0c0'),
                showgrid=True,
                gridwidth=1
            ),
            yaxis=dict(
                title=dict(text='功率 (kW)', font=dict(color='#00ffcc')),
                gridcolor='rgba(0, 255, 204, 0.1)',
                linecolor='rgba(0, 255, 204, 0.3)',
                tickfont=dict(color='#c0c0c0'),
                showgrid=True,
                gridwidth=1
            ),
            plot_bgcolor='rgba(10, 10, 26, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(10, 10, 26, 0.8)',
                bordercolor='rgba(0, 255, 204, 0.3)',
                borderwidth=1,
                font=dict(color='#c0c0c0')
            ),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor='rgba(10, 10, 26, 0.95)',
                bordercolor='#00ffcc',
                font=dict(color='#ffffff')
            ),
            margin=dict(t=80, b=60, l=60, r=40)
            )

            st.plotly_chart(fig_compare, use_container_width=True, config={'displayModeBar': False})

            # 显示选中日期详细统计（科技风指标卡片）
            selected_day_stats = plot_df_grouped[plot_df_grouped['datetime'].dt.date == selected_date]
            if len(selected_day_stats) > 0:
                st.markdown("""
                <style>
                .tech-metric-container {
                    background: linear-gradient(135deg, rgba(0, 255, 204, 0.1) 0%, rgba(0, 170, 255, 0.05) 100%);
                    border: 1px solid rgba(0, 255, 204, 0.3);
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                }
                .tech-metric-label {
                    color: #00ffcc;
                    font-size: 12px;
                    margin-bottom: 5px;
                }
                .tech-metric-value {
                    color: #ffffff;
                    font-size: 24px;
                    font-weight: bold;
                    text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
                }
                </style>
                """, unsafe_allow_html=True)

                col_stat1, col_stat2, col_stat3 = st.columns(3)
                with col_stat1:
                    pred_total = selected_day_stats[pred_col].sum() if has_pred and pred_col in selected_day_stats.columns else 0
                    st.markdown(f"""
                    <div class="tech-metric-container">
                        <div class="tech-metric-label">预测总能耗</div>
                        <div class="tech-metric-value">{pred_total:,.0f} <span style="font-size:14px;color:#c0c0c0">kW</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_stat2:
                    real_total = selected_day_stats['real_kw'].sum() if has_real and 'real_kw' in selected_day_stats.columns else 0
                    st.markdown(f"""
                    <div class="tech-metric-container">
                        <div class="tech-metric-label">实际总能耗</div>
                        <div class="tech-metric-value">{real_total:,.0f} <span style="font-size:14px;color:#c0c0c0">kW</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_stat3:
                    saved_kwh = selected_day_stats['energy_saved_kwh'].sum() if has_saved and 'energy_saved_kwh' in selected_day_stats.columns else 0
                    pred_sum_day = selected_day_stats[pred_col].sum() if has_pred and pred_col in selected_day_stats.columns else 0
                    saved_pct = (saved_kwh / pred_sum_day * 100) if pred_sum_day > 0 else 0
                    st.markdown(f"""
                    <div class="tech-metric-container">
                        <div class="tech-metric-label">节能率</div>
                        <div class="tech-metric-value" style="color:#00ff88">{saved_pct:.1f}<span style="font-size:14px;color:#c0c0c0">%</span></div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning(f"选中日期 {selected_date.strftime('%Y-%m-%d')} 附近没有数据")

# ==================== 双模型/三模型集成学习各节点准确率柱状图 ====================
if strategy in ["双模型集成", "三模型集成"]:
    # 根据策略选择不同的数据文件
    if strategy == "双模型集成":
        csv_file = "Meta-Learner_node_accuracy.csv"
        title = "双模型集成学习各节点准确率"
    else:  # 三模型集成
        csv_file = "ensamble-Learner_node_accuracy.csv"
        title = "三模型集成学习各节点准确率"

    meta_learner_csv = os.path.join(base_dir, 'data', csv_file)
    if os.path.exists(meta_learner_csv):
        df_accuracy = pd.read_csv(meta_learner_csv)

        # 转换准确率为百分比
        df_accuracy['accuracy_pct'] = df_accuracy['accuracy'] * 100

        # 按准确率排序
        df_accuracy = df_accuracy.sort_values('accuracy_pct', ascending=True)

        # 创建柱状图
        fig_accuracy = go.Figure()

        # 根据准确率设置颜色
        colors = ['#ff6b6b' if x < 60 else '#ffd93d' if x < 80 else '#00ff88' for x in df_accuracy['accuracy_pct']]

        fig_accuracy.add_trace(go.Bar(
            x=df_accuracy['node_id'].astype(str),
            y=df_accuracy['accuracy_pct'],
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.3)', width=1)
            ),
            text=[f'{x:.1f}%' for x in df_accuracy['accuracy_pct']],
            textposition='outside',
            textfont=dict(color='#ffffff', size=9),
            hovertemplate='<b>基站 %{x}</b><br>准确率: %{y:.2f}%<extra></extra>'
        ))

        fig_accuracy.update_layout(
            title=dict(
                text=f'<b>{title}</b>',
                font=dict(size=16, color='#00ffcc'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                title='基站ID',
                tickfont=dict(color='#c0c0c0', size=9),
                gridcolor='rgba(0, 255, 204, 0.1)',
                linecolor='rgba(0, 255, 204, 0.3)'
            ),
            yaxis=dict(
                title='准确率 (%)',
                range=[0, 110],
                tickfont=dict(color='#c0c0c0'),
                gridcolor='rgba(0, 255, 204, 0.1)',
                linecolor='rgba(0, 255, 204, 0.3)'
            ),
            plot_bgcolor='rgba(10, 10, 26, 0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0e0'),
            height=350,
            margin=dict(t=50, b=60, l=60, r=40),
            showlegend=False
        )

        # 添加平均线
        avg_accuracy = df_accuracy['accuracy_pct'].mean()
        fig_accuracy.add_hline(
            y=avg_accuracy,
            line=dict(color='#00aaff', width=2, dash='dash'),
            annotation_text=f'平均: {avg_accuracy:.1f}%',
            annotation_position='right',
            annotation_font=dict(color='#00aaff', size=11)
        )

        st.plotly_chart(fig_accuracy, use_container_width=True, config={'displayModeBar': False}, key=f"accuracy_chart_{strategy}")
    else:
        st.info(f"未找到 {csv_file} 文件")

# ==================== 新增模块：策略相关特有展示 ====================
st.subheader("策略详细信息")

# 加载必要的数据文件（如果尚未加载）
@st.cache_data
def load_phase_summary(phase):
    """加载指定阶段的汇总统计"""
    if phase == 1:
        path = os.path.join(base_dir, 'decision', 'outputs', 'summary_stats_7day_all.json')
    elif phase == 2:
        path = os.path.join(base_dir, 'decision', 'outputs', 'summary_stats_7day_all_phase2.json')
    elif phase == 3:
        path = os.path.join(base_dir, 'decision', 'outputs', 'summary_stats_7day_all_phase3.json')
    else:
        return None
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

# 成本矩阵（硬编码，来自日志）
cost_matrix = {
    "高负载": {"休眠": 400, "正常": 3, "迁移": 1},
    "中负载": {"休眠": 200, "正常": 0, "迁移": 2},
    "低负载": {"休眠": 0, "正常": 3, "迁移": 2}
}

# 集成学习特征重要性（来自日志）
ensemble_importance = {
    "Phase1 置信度": 2.88,
    "Phase2 置信度": 1.75,
    "Phase3 置信度": 1.75,
    "Phase2 决策编码": 0.92,
    "Phase3 决策编码": 0.50,
    "Phase1 决策编码": 0.21
}

# 根据当前策略显示特有模块
if strategy == "Phase2":
    # 成本矩阵展示 - ECharts科技感设计
    with st.expander("成本矩阵（Phase2）", expanded=True):
        # 准备成本矩阵数据
        load_states = ["高负载", "中负载", "低负载"]
        decisions = ["休眠", "正常", "迁移"]

        # 硬编码成本矩阵数据 [x, y, value]
        heatmap_data = [
            [0, 0, 400],   # 高负载-休眠
            [1, 0, 3],     # 高负载-正常
            [2, 0, 1],     # 高负载-迁移
            [0, 1, 200],   # 中负载-休眠
            [1, 1, 0],     # 中负载-正常
            [2, 1, 2],     # 中负载-迁移
            [0, 2, 0],     # 低负载-休眠
            [1, 2, 3],     # 低负载-正常
            [2, 2, 2]      # 低负载-迁移
        ]

        # ECharts成本矩阵配置
        cost_matrix_option = {
            "backgroundColor": "transparent",
            "title": {
                "text": "◉ 成本矩阵 (Cost Matrix)",
                "left": "center",
                "top": 10,
                "textStyle": {
                    "color": "#00ffcc",
                    "fontSize": 18,
                    "fontFamily": "Orbitron",
                    "fontWeight": "bold"
                }
            },
            "tooltip": {
                "position": "top",
                "backgroundColor": "rgba(10, 10, 26, 0.95)",
                "borderColor": "#00ffcc",
                "borderWidth": 1,
                "textStyle": {
                    "color": "#ffffff",
                    "fontFamily": "Orbitron"
                },
                "formatter": JsCode("""function(params) {
                    var loadStates = ['高负载', '中负载', '低负载'];
                    var decisions = ['休眠', '正常', '迁移'];
                    var load = loadStates[params.value[1]];
                    var decision = decisions[params.value[0]];
                    var cost = params.value[2];
                    var color = cost <= 1 ? '#00ff88' : cost <= 3 ? '#00ccff' : cost <= 100 ? '#ffcc00' : '#ff3366';
                    var priority = cost <= 1 ? '★★★ 强烈推荐' : cost <= 3 ? '★★☆ 推荐' : cost <= 100 ? '★☆☆ 一般' : '☆☆☆ 避免';
                    return '<div style="background:rgba(10,10,26,0.95);border:1px solid ' + color + ';padding:10px;border-radius:4px;">' +
                           '<div style="color:' + color + ';font-weight:bold;font-size:14px;margin-bottom:5px;">' + load + ' → ' + decision + '</div>' +
                           '<div style="color:#00ffcc;font-size:16px;font-weight:bold;">成本: ' + cost + '</div>' +
                           '<div style="color:#c0c0c0;font-size:11px;margin-top:5px;">' + priority + '</div>' +
                           '</div>';
                }""")
            },
            "grid": {
                "left": "15%",
                "right": "15%",
                "top": "20%",
                "bottom": "15%"
            },
            "xAxis": {
                "type": "category",
                "data": ["休眠", "正常", "迁移"],
                "name": "决策类型",
                "nameLocation": "middle",
                "nameGap": 30,
                "nameTextStyle": {
                    "color": "#00ffcc",
                    "fontSize": 14,
                    "fontFamily": "Orbitron",
                    "fontWeight": "bold"
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontSize": 12,
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "rgba(0, 255, 204, 0.3)",
                        "width": 2
                    }
                },
                "splitArea": {
                    "show": True,
                    "areaStyle": {
                        "color": ["rgba(0, 255, 204, 0.02)", "rgba(0, 255, 204, 0.05)"]
                    }
                }
            },
            "yAxis": {
                "type": "category",
                "data": ["高负载", "中负载", "低负载"],
                "name": "负载状态",
                "nameTextStyle": {
                    "color": "#00ffcc",
                    "fontSize": 14,
                    "fontFamily": "Orbitron",
                    "fontWeight": "bold"
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontSize": 12,
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {
                        "color": "rgba(0, 255, 204, 0.3)",
                        "width": 2
                    }
                },
                "splitArea": {
                    "show": True,
                    "areaStyle": {
                        "color": "rgba(0, 255, 204, 0.02)"
                    }
                }
            },
            "visualMap": {
                "min": 0,
                "max": 400,
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "2%",
                "textStyle": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "inRange": {
                    "color": ["#00ff88", "#00ccff", "#ffcc00", "#ff3366"]
                },
                "text": ["高成本", "低成本"]
            },
            "series": [{
                "name": "成本值",
                "type": "heatmap",
                "data": heatmap_data,
                "label": {
                    "show": True,
                    "fontSize": 16,
                    "fontFamily": "Orbitron",
                    "fontWeight": "bold",
                    "color": "#ffffff"
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowColor": "rgba(0, 255, 204, 0.8)",
                        "borderColor": "#00ffcc",
                        "borderWidth": 3
                    },
                    "label": {
                        "fontSize": 18,
                        "color": "#00ffcc"
                    }
                },
                "itemStyle": {
                    "borderRadius": 8,
                    "borderColor": "rgba(0, 255, 204, 0.2)",
                    "borderWidth": 1
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            }]
        }

        # 创建两列布局：成本矩阵和MC Dropout图并排显示
        cost_col, img_col = st.columns([1, 1.2])

        with cost_col:
            st_echarts(options=cost_matrix_option, height="320px", key="cost_matrix_echarts")

            # 添加图例说明
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 170, 255, 0.05) 100%);
                border: 1px solid rgba(0, 255, 204, 0.3);
                border-radius: 10px;
                padding: 12px;
                margin-top: 8px;
            ">
                <div style="color: #00ffcc; font-family: 'Orbitron', sans-serif; font-size: 12px; margin-bottom: 8px;">
                    ▼ 成本矩阵说明
                </div>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: linear-gradient(135deg, #00ff88, #00cc6a); border-radius: 3px;"></div>
                        <span style="color: #c0c0c0; font-size: 11px;">低成本</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: linear-gradient(135deg, #00ccff, #0099cc); border-radius: 3px;"></div>
                        <span style="color: #c0c0c0; font-size: 11px;">较低成本</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: linear-gradient(135deg, #ffcc00, #cc9900); border-radius: 3px;"></div>
                        <span style="color: #c0c0c0; font-size: 11px;">中等成本</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <div style="width: 16px; height: 16px; background: linear-gradient(135deg, #ff3366, #cc0033); border-radius: 3px;"></div>
                        <span style="color: #c0c0c0; font-size: 11px;">高成本</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with img_col:
            # MC Dropout 不确定性图
            # 优先使用用户指定的路径
            uncertainty_img = os.path.join(base_dir, 'data', 'image', 'uncertainty_7day_all.png')
            if not os.path.exists(uncertainty_img):
                # 回退到旧路径
                uncertainty_img = os.path.join(base_dir, 'decision', 'outputs', 'uncertainty_7day_all.png')

            if os.path.exists(uncertainty_img):
                st.image(uncertainty_img, caption="MC Dropout 不确定性估计（30次前向传播）", use_container_width=True)
            else:
                st.info("未找到不确定性图文件，请运行 Phase2 决策引擎生成。")

elif strategy == "Phase3":
    # 动态阈值参数面板
    thresholds_json = os.path.join(base_dir, 'decision', 'config', 'thresholds_dynamic.json')
    if os.path.exists(thresholds_json):
        with open(thresholds_json, 'r') as f:
            thresholds = json.load(f)
        # 显示滑动窗口参数
        st.markdown("**动态阈值参数**")
        st.metric("滑动窗口大小", "3 天")
        st.metric("更新间隔", "1000 样本")
        # 显示当前时段的阈值示例（取 hour_code=0, is_holiday=0 作为示例）
        example = next((t for t in thresholds.get("thresholds", []) if t.get("hour_code")==0 and t.get("is_holiday")==0), None)
        if example:
            st.write(f"凌晨时段 (00-06) 非节假日阈值：低 = {example['low']:.1f} kWh, 高 = {example['high']:.1f} kWh")
        else:
            st.write("阈值文件格式示例：", thresholds)
    else:
        st.info("动态阈值配置文件未找到，请运行 Phase3 生成。")

elif strategy == "集成学习":
    # 集成学习权重展示（条形图）
    importance_df = pd.DataFrame(list(ensemble_importance.items()), columns=["特征", "重要性"])
    fig_imp = px.bar(importance_df, x="重要性", y="特征", orientation='h', 
                     title="元学习器特征重要性（逻辑回归系数）",
                     color="重要性", color_continuous_scale='Viridis')
    fig_imp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          font=dict(color='#c0c0c0'), title_font_color='#00ffcc')
    st.plotly_chart(fig_imp, use_container_width=True)
    st.caption("集成学习使用逻辑回归融合 Phase1、Phase2、Phase3 的决策和置信度，其中 Phase1 置信度贡献最大 (2.88)。")

# ==================== 甘特图部分（使用 Heatmap 替代 Custom 系列，完全避免 JS 函数） ====================
st.subheader(f"决策时间线甘特图 - 当前策略: {strategy}")

# 基于选中日期的数据过滤
selected_date_gantt = pd.to_datetime(selected_date)
day_start = selected_date_gantt
day_end = selected_date_gantt + pd.Timedelta(days=1)

# 根据当前策略重新加载对应数据（确保数据最新）
df_gantt = load_data(strategy)
day_tasks = df_gantt[(df_gantt['datetime'] >= day_start) & 
                     (df_gantt['datetime'] < day_end)].copy()

if len(day_tasks) > 0:
    try:
        # 每轮显示6个基站
        NODES_PER_PAGE = 6
        
        # 获取所有有数据的基站
        active_nodes = sorted(day_tasks['node_id'].unique())
        total_nodes = len(active_nodes)
        
        # 计算实际轮数
        actual_rounds = (total_nodes + NODES_PER_PAGE - 1) // NODES_PER_PAGE
        
        # 决策类型映射为数值（用于热力图颜色）
        decision_value_map = {'休眠': 0, '负载均衡': 1, '正常运行': 2}
        decision_names = ['休眠', '负载均衡', '正常运行']
        
        # 时间段标签
        time_slots = ['00:00-06:00', '06:00-12:00', '12:00-18:00', '18:00-24:00']
        
        # 为每一轮准备数据
        timeline_options = []
        round_labels = []
        
        for round_idx in range(actual_rounds):
            start_idx = round_idx * NODES_PER_PAGE
            end_idx = min(start_idx + NODES_PER_PAGE, total_nodes)
            display_nodes = active_nodes[start_idx:end_idx]
            
            # Y轴数据 - 基站名称
            y_axis_data = [f"基站{node}" for node in display_nodes]
            
            # 准备热力图数据 [x, y, value]
            # x: 时间段索引 (0-3)
            # y: 基站索引
            # value: 决策类型数值
            heatmap_data = []
            
            for node_idx, node in enumerate(display_nodes):
                node_tasks = day_tasks[day_tasks['node_id'] == node].copy()
                node_tasks = node_tasks.sort_values('hour_code')
                
                for hour_code in range(4):  # 0, 1, 2, 3
                    slot_task = node_tasks[node_tasks['hour_code'] == hour_code]
                    if len(slot_task) > 0:
                        decision = slot_task.iloc[0]['decision_cn']
                    else:
                        decision = '正常运行'
                    
                    value = decision_value_map.get(decision, 2)
                    heatmap_data.append([hour_code, node_idx, value])

            timeline_options.append({
                "title": {"text": f"决策时间线 - 第{round_idx + 1}轮 (基站{start_idx + 1}-{end_idx})"},
                "yAxis": {"data": y_axis_data},
                "series": [{"data": heatmap_data}]
            })
            round_labels.append(f"第{round_idx + 1}轮")

        # 根据策略设置不同的主题色
        theme_colors = {
            "Phase1": "#00ff88",
            "Phase2": "#00aaff", 
            "Phase3": "#ffaa00",
            "双模型集成": "#ff66cc",
            "三模型集成": "#aa66ff"
        }
        current_theme = theme_colors.get(strategy, "#00ff88")

        # ECharts 配置 - 使用 Heatmap，无需 renderItem
        option = {
            "baseOption": {
                "backgroundColor": "transparent",
                "timeline": {
                    "axisType": "category",
                    "autoPlay": True,
                    "playInterval": 3000,
                    "loop": True,
                    "rewind": True,
                    "controlPosition": "left",
                    "data": round_labels,
                    "left": "10%",
                    "right": "10%",
                    "bottom": "2%",
                    "label": {"color": current_theme, "fontSize": 11, "fontWeight": "bold"},
                    "lineStyle": {"color": current_theme, "width": 2},
                    "itemStyle": {"color": current_theme, "borderColor": current_theme, "borderWidth": 2},
                    "checkpointStyle": {"color": "#00aaff", "borderColor": current_theme, "borderWidth": 3, "symbolSize": 16},
                    "controlStyle": {"color": current_theme, "borderColor": current_theme, "itemSize": 20},
                    "emphasis": {"itemStyle": {"color": "#00aaff"}, "controlStyle": {"color": "#00aaff", "borderColor": "#00aaff"}}
                },
                "title": {
                    "text": f"6小时粒度决策监控 ({selected_date.strftime('%Y-%m-%d')}) - {strategy}",
                    "left": "center",
                    "top": 5,
                    "textStyle": {"color": current_theme, "fontSize": 16, "fontWeight": "bold"}
                },
                "tooltip": {
                    "position": "top",
                    "formatter": JsCode(f"""function(params) {{
                        var decisions = ['休眠', '负载均衡', '正常运行'];
                        var timeLabels = ['00:00-06:00', '06:00-12:00', '12:00-18:00', '18:00-24:00'];
                        var decision = decisions[params.value[2]];
                        var timeRange = timeLabels[params.value[0]];
                        var baseName = params.name;
                        return '<div style="background:rgba(10,10,26,0.95);border:1px solid {current_theme};padding:10px;border-radius:4px;">' +
                               '<div style="color:{current_theme};font-weight:bold;margin-bottom:5px;">' + decision + '</div>' +
                               '<div style="color:#c0c0c0;font-size:12px;">基站: <b style="color:#fff;">' + baseName + '</b></div>' +
                               '<div style="color:#c0c0c0;font-size:12px;">时段: <b style="color:#fff;">' + timeRange + '</b></div>' +
                               '<div style="color:#c0c0c0;font-size:12px;">时长: <b style="color:#fff;">6小时</b></div>' +
                               '</div>';
                    }}"""),
                    "backgroundColor": "rgba(10, 10, 26, 0.95)",
                    "borderColor": current_theme,
                    "borderWidth": 1,
                    "textStyle": {"color": "#ffffff"}
                },
                "grid": {"left": "15%", "right": "8%", "top": "18%", "bottom": "18%", "height": "65%"},
                "xAxis": {
                    "type": "category",
                    "data": time_slots,
                    "name": "时间段",
                    "nameLocation": "middle",
                    "nameGap": 30,
                    "nameTextStyle": {"color": current_theme, "fontSize": 12, "fontWeight": "bold"},
                    "axisLabel": {"color": "#c0c0c0", "fontSize": 10},
                    "axisLine": {"lineStyle": {"color": current_theme, "width": 2}},
                    "splitArea": {"show": True, "areaStyle": {"color": ["rgba(255,255,255,0.02)", "rgba(255,255,255,0.05)"]}}
                },
                "yAxis": {
                    "type": "category",
                    "data": [],
                    "name": "基站",
                    "nameTextStyle": {"color": current_theme, "fontSize": 12, "fontWeight": "bold"},
                    "axisLabel": {"color": "#c0c0c0", "fontSize": 11},
                    "axisLine": {"lineStyle": {"color": current_theme, "width": 2}},
                    "splitArea": {"show": True, "areaStyle": {"color": "rgba(255,255,255,0.02)"}}
                },
                "visualMap": {
                    "min": 0,
                    "max": 2,
                    "calculable": False,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "12%",
                    "itemWidth": 20,
                    "itemHeight": 12,
                    "textStyle": {"color": "#c0c0c0"},
                    "pieces": [
                        {"value": 0, "label": "休眠", "color": "#4CAF50"},
                        {"value": 1, "label": "负载均衡", "color": "#FF9800"},
                        {"value": 2, "label": "正常运行", "color": "#607D8B"}
                    ]
                },
                "series": [
                    {
                        "name": "决策",
                        "type": "heatmap",
                        "label": {"show": False},
                        "emphasis": {
                            "itemStyle": {
                                "shadowBlur": 10,
                                "shadowColor": "rgba(0, 0, 0, 0.5)",
                                "borderColor": current_theme,
                                "borderWidth": 2
                            }
                        },
                        "itemStyle": {
                            "borderRadius": 4,
                            "borderColor": "#0a0a14",
                            "borderWidth": 1
                        },
                        "data": []
                    }
                ]
            },
            "options": timeline_options
        }

        # 渲染甘特图
        st_echarts(options=option, height="500px", key=f"gantt_heatmap_{strategy}_{selected_date.strftime('%Y%m%d')}")
        
    except Exception as e:
        st.error(f"甘特图渲染出错: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
else:
    st.warning(f"选中日期 {selected_date.strftime('%Y-%m-%d')} 没有决策数据")