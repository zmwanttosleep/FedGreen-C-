import streamlit as st
import pandas as pd
import numpy as np
import json
from streamlit_echarts import st_echarts, JsCode  # type: ignore
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.sidebar import render_sidebar

st.set_page_config(page_title="联邦学习训练", layout="wide")

# 渲染共享侧边栏
render_sidebar()

# 策略模式选择
strategy = st.sidebar.selectbox("策略模式", ["Phase1", "Phase2", "Phase3", "双模型集成", "三模型集成"])

# 阈值参数
sleep_th = st.sidebar.slider("休眠阈值 (kWh)", min_value=0, max_value=50000, value=20000, step=1000)
mig_th = st.sidebar.slider("迁移阈值 (kWh)", min_value=0, max_value=150000, value=80000, step=1000)
window_size = st.sidebar.slider("滑动窗口大小", min_value=1, max_value=30, value=7, step=1)

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
    
    .echarts-container {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.6) 0%, rgba(26, 26, 46, 0.7) 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
    }
    
    .dataframe-container {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.6) 0%, rgba(26, 26, 46, 0.7) 100%);
        border: 1px solid rgba(0, 255, 136, 0.2);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.1), inset 0 0 30px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        position: relative;
        animation: containerGlow 3s ease-in-out infinite;
    }
    
    @keyframes containerGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 255, 136, 0.1), inset 0 0 30px rgba(0, 0, 0, 0.3); }
        50% { box-shadow: 0 0 30px rgba(0, 255, 136, 0.2), inset 0 0 40px rgba(0, 0, 0, 0.4); }
    }
    
    .dataframe {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: 'Orbitron', monospace;
        color: #e0e0e0;
        position: relative;
        z-index: 1;
    }
    
    .dataframe th {
        background: linear-gradient(180deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 170, 255, 0.1) 100%);
        color: #00ff88;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 12px 15px;
        border-bottom: 2px solid rgba(0, 255, 136, 0.5);
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .dataframe th::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.3), transparent);
        animation: headerShine 3s ease-in-out infinite;
        animation-delay: calc(var(--th-index, 0) * 0.2s);
    }
    
    @keyframes headerShine {
        0% { left: -100%; }
        50%, 100% { left: 100%; }
    }
    
    .dataframe th:hover {
        background: linear-gradient(180deg, rgba(0, 255, 136, 0.4) 0%, rgba(0, 170, 255, 0.2) 100%);
        text-shadow: 0 0 20px rgba(0, 255, 136, 0.8), 0 0 30px rgba(0, 255, 136, 0.4);
        transform: translateY(-2px);
    }
    
    .dataframe td {
        padding: 10px 15px;
        border-bottom: 1px solid rgba(0, 255, 136, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .dataframe td::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 136, 0.05), transparent);
        transform: translateX(-100%);
        transition: transform 0.5s ease;
    }
    
    .dataframe tr:hover td::before {
        transform: translateX(100%);
    }
    
    .dataframe tr {
        position: relative;
        transition: all 0.3s ease;
    }
    
    .dataframe tr:hover {
        transform: scale(1.01);
    }
    
    .dataframe tr:hover td {
        background: rgba(0, 255, 136, 0.15);
        box-shadow: 
            inset 0 0 20px rgba(0, 255, 136, 0.1),
            0 0 10px rgba(0, 255, 136, 0.2);
        color: #ffffff;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }
    
    .dataframe tr:hover td:first-child {
        border-left: 3px solid rgba(0, 255, 136, 0.8);
        padding-left: 12px;
    }
    
    .dataframe tr:hover td:last-child {
        border-right: 3px solid rgba(0, 255, 136, 0.8);
        padding-right: 12px;
    }
    
    .dataframe tr:nth-child(even) td {
        background: rgba(0, 255, 136, 0.03);
    }
    
    .dataframe tr:nth-child(odd) td {
        background: rgba(0, 170, 255, 0.02);
    }
    
    .dataframe tr td {
        animation: rowFadeIn 0.5s ease-out forwards;
        animation-play-state: running;
    }
    
    @keyframes rowFadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
        position: relative;
    }
    
    .stDataFrame::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 10px;
        box-shadow: inset 0 0 50px rgba(0, 255, 136, 0.05);
        pointer-events: none;
        animation: pulseBorder 2s ease-in-out infinite;
    }
    
    @keyframes pulseBorder {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    [data-testid="stDataFrame"] {
        background: transparent !important;
        border: none !important;
    }
    
    .dvn-scroller {
        border-radius: 10px !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .dvn-scroller:hover {
        border-color: rgba(0, 255, 136, 0.4) !important;
        box-shadow: 
            inset 0 0 30px rgba(0, 0, 0, 0.4),
            0 0 20px rgba(0, 255, 136, 0.1) !important;
    }
    
    .dataframe-value-highlight {
        color: #00ff88 !important;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        animation: valuePulse 2s ease-in-out infinite;
    }
    
    @keyframes valuePulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    .stSelectbox label, .stDateInput label, .stSlider label {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    [data-baseweb="select"] {
        background: rgba(15, 52, 96, 0.8) !important;
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        border-radius: 8px !important;
    }
    
    [data-baseweb="select"] * {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif !important;
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
    
    [data-testid="stHeaderActionElements"] {
        display: none !important;
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

particle_html = '<div class="floating-particles">'
for i in range(20):
    left = f"{i * 5}%"
    delay = f"{i * 0.8}s"
    duration = f"{15 + i % 10}s"
    particle_html += f'<div class="particle" style="left: {left}; animation-delay: {delay}; animation-duration: {duration};"></div>'
particle_html += '</div>'
st.markdown(particle_html, unsafe_allow_html=True)

st.title("核心算法训练")

st.markdown("""
<style>
.status-bar {
display: flex;
gap: 12px;
margin: 15px 0 25px 0;
flex-wrap: wrap;
}
.status-card {
flex: 1;
min-width: 140px;
background: linear-gradient(135deg, rgba(15, 52, 96, 0.7) 0%, rgba(26, 26, 46, 0.8) 100%);
border: 1px solid rgba(0, 255, 136, 0.25);
border-radius: 10px;
padding: 14px 16px;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
transition: all 0.3s ease;
}
.status-card:hover {
border-color: rgba(0, 255, 136, 0.5);
transform: translateY(-2px);
box-shadow: 0 6px 20px rgba(0, 255, 136, 0.15);
}
.status-card-label {
font-size: 14px;
color: #aaa;
text-transform: uppercase;
letter-spacing: 1px;
margin-bottom: 8px;
font-weight: 700;
}
.status-card-value {
font-size: 32px;
font-weight: 900;
font-family: 'Orbitron', sans-serif;
text-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
}
.status-card-sub {
font-size: 14px;
color: #aaa;
margin-top: 8px;
font-weight: 700;
}
.train-value { color: #00ff88; }
.val-value { color: #00aaff; }
.test-value { color: #F18F01; }
.metric-value { color: #fff; }
.section-header {
display: flex;
align-items: center;
gap: 10px;
margin: 25px 0 15px 0;
padding-bottom: 10px;
border-bottom: 1px solid rgba(0, 255, 136, 0.2);
}
.section-title {
font-size: 16px;
font-weight: 600;
color: #00ff88;
font-family: 'Orbitron', sans-serif;
letter-spacing: 1px;
}
.section-line {
flex: 1;
height: 1px;
background: linear-gradient(90deg, rgba(0, 255, 136, 0.3), transparent);
}
</style>
<div class="status-bar">
<div class="status-card">
<div class="status-card-label">训练集</div>
<div class="status-card-value train-value">70%</div>
<div class="status-card-sub">2019-2023 · 43,800条</div>
</div>
<div class="status-card">
<div class="status-card-label">验证集</div>
<div class="status-card-value val-value">15%</div>
<div class="status-card-sub">2024 · 9,375条</div>
</div>
<div class="status-card">
<div class="status-card-label">测试集</div>
<div class="status-card-value test-value">15%</div>
<div class="status-card-sub">2025 · 9,375条</div>
</div>
<div class="status-card">
<div class="status-card-label">Proximal μ</div>
<div class="status-card-value metric-value">0.01</div>
<div class="status-card-sub">近端项系数</div>
</div>
<div class="status-card">
<div class="status-card-label">本地轮次</div>
<div class="status-card-value metric-value">5</div>
<div class="status-card-sub">Local Epochs</div>
</div>
<div class="status-card">
<div class="status-card-label">聚合轮次</div>
<div class="status-card-value metric-value">10</div>
<div class="status-card-sub">Federation Rounds</div>
</div>
<div class="status-card">
<div class="status-card-label">参与节点</div>
<div class="status-card-value metric-value">24/42</div>
<div class="status-card-sub">活跃节点数</div>
</div>
</div>
""", unsafe_allow_html=True)

# 读取三个实验的损失数据
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_loss_data(filename):
    """加载损失数据CSV文件"""
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            return df
        except Exception as e:
            st.warning(f"读取 {filename} 失败: {e}")
            return None
    return None

# 加载三个实验的数据
df_2node = load_loss_data("granularity_2node_loss.csv")
df_41node = load_loss_data("granularity_41node_loss.csv")
df_unweighted = load_loss_data("unweighted_41node_loss.csv")

# 准备图表数据
rounds = list(range(1, 11))  # 1-10轮

# 获取各实验的验证损失数据
def get_val_loss(df):
    """获取验证损失数据，优先使用val_loss列，否则使用train_loss"""
    if df is None:
        return []
    if 'val_loss' in df.columns and df['val_loss'].notna().any():
        return df['val_loss'].dropna().tolist()[:10]
    elif 'train_loss' in df.columns:
        return df['train_loss'].dropna().tolist()[:10]
    return []

loss_2node = get_val_loss(df_2node)
loss_41node = get_val_loss(df_41node)
loss_unweighted = get_val_loss(df_unweighted)

# 如果数据不足10轮，用None填充
loss_2node = loss_2node + [None] * (10 - len(loss_2node)) if len(loss_2node) < 10 else loss_2node[:10]
loss_41node = loss_41node + [None] * (10 - len(loss_41node)) if len(loss_41node) < 10 else loss_41node[:10]
loss_unweighted = loss_unweighted + [None] * (10 - len(loss_unweighted)) if len(loss_unweighted) < 10 else loss_unweighted[:10]

line_option = {
    "backgroundColor": "transparent",
    "title": {
        "text": "◉ 全局损失下降曲线对比",
        "textStyle": {
            "color": "#00ff88",
            "fontSize": 18,
            "fontWeight": "bold",
            "fontFamily": "Orbitron",
            "textShadowColor": "rgba(0, 255, 136, 0.8)",
            "textShadowBlur": 15
        },
        "left": "center",
        "top": 5
    },
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "cross",
            "crossStyle": {"color": "rgba(0, 255, 136, 0.3)", "width": 1}
        },
        "backgroundColor": "rgba(10, 10, 26, 0.95)",
        "borderColor": "#00ff88",
        "borderWidth": 2,
        "textStyle": {"color": "#e0e0e0", "fontFamily": "Orbitron"},
        "formatter": JsCode("""function(params) {
            var result = '<div style="font-family:Orbitron;text-align:center;border-bottom:1px solid rgba(0,255,136,0.3);padding-bottom:8px;margin-bottom:8px;">' +
                         '<span style="font-size:16px;font-weight:bold;color:#00ff88;text-shadow:0 0 10px rgba(0,255,136,0.5);">第 ' + params[0].axisValue + ' 轮</span>' +
                         '</div>';
            for (var i = 0; i < params.length; i++) {
                if (params[i].value !== undefined && params[i].value !== null) {
                    var icon = params[i].seriesName === '2节点粒度融合' ? '●' : 
                              params[i].seriesName === '41节点粒度融合' ? '◆' : '▲';
                    result += '<div style="font-family:Orbitron;margin:5px 0;display:flex;align-items:center;justify-content:space-between;min-width:200px;">' +
                              '<span style="color:#c0c0c0;">' + icon + ' ' + params[i].seriesName + '</span>' +
                              '<span style="color:' + params[i].color + ';font-weight:bold;font-size:14px;text-shadow:0 0 5px ' + params[i].color + ';">' + params[i].value.toFixed(6) + '</span>' +
                              '</div>';
                }
            }
            return result;
        }""")
    },
    "legend": {
        "data": ["2节点粒度融合", "41节点粒度融合", "41节点不加权"],
        "top": 40,
        "textStyle": {"color": "#e0e0e0", "fontFamily": "Orbitron", "fontSize": 14},
        "itemGap": 20,
        "itemWidth": 25,
        "itemHeight": 14
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "12%", "top": "22%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": [str(r) for r in rounds],
        "name": "训练轮次",
        "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron", "fontSize": 15},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
        "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron", "fontSize": 14},
        "axisTick": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.05)"}}
    },
    "yAxis": {
        "type": "value",
        "name": "损失值",
        "nameTextStyle": {"color": "#00ff88", "fontFamily": "Orbitron", "fontSize": 15},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
        "axisLabel": {"color": "#c0c0c0", "fontFamily": "Orbitron"},
        "axisTick": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}}
    },
    "dataZoom": [
        {"type": "inside", "xAxisIndex": 0, "filterMode": "filter"},
        {"type": "slider", "xAxisIndex": 0, "filterMode": "filter", "bottom": "2%", 
         "borderColor": "rgba(0, 255, 136, 0.3)", "fillerColor": "rgba(0, 255, 136, 0.2)", 
         "textStyle": {"color": "#c0c0c0"}, "handleStyle": {"color": "#00ff88"}}
    ],
    "series": [
        {
            "name": "2节点粒度融合",
            "type": "line",
            "smooth": 0.4,
            "symbol": "circle",
            "symbolSize": 10,
            "showSymbol": True,
            "data": loss_2node,
            "lineStyle": {"color": "#00ff88", "width": 4, "shadowColor": "rgba(0, 255, 136, 0.5)", "shadowBlur": 10},
            "itemStyle": {"color": "#00ff88", "borderColor": "#fff", "borderWidth": 2},
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.4)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0)"}
                    ]
                }
            },
            "emphasis": {
                "focus": "series",
                "itemStyle": {"shadowBlur": 20, "shadowColor": "#00ff88", "scale": 1.5},
                "lineStyle": {"width": 5}
            },
            "animationDuration": 2000,
            "animationEasing": "elasticOut",
            "animationDelay": 0
        },
        {
            "name": "41节点粒度融合",
            "type": "line",
            "smooth": 0.4,
            "symbol": "diamond",
            "symbolSize": 12,
            "showSymbol": True,
            "data": loss_41node,
            "lineStyle": {"color": "#00aaff", "width": 4, "shadowColor": "rgba(0, 170, 255, 0.5)", "shadowBlur": 10},
            "itemStyle": {"color": "#00aaff", "borderColor": "#fff", "borderWidth": 2},
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 170, 255, 0.4)"},
                        {"offset": 1, "color": "rgba(0, 170, 255, 0)"}
                    ]
                }
            },
            "emphasis": {
                "focus": "series",
                "itemStyle": {"shadowBlur": 20, "shadowColor": "#00aaff", "scale": 1.5},
                "lineStyle": {"width": 5}
            },
            "animationDuration": 2000,
            "animationEasing": "elasticOut",
            "animationDelay": 300
        },
        {
            "name": "41节点不加权",
            "type": "line",
            "smooth": 0.4,
            "symbol": "triangle",
            "symbolSize": 12,
            "showSymbol": True,
            "data": loss_unweighted,
            "lineStyle": {"color": "#ffaa00", "width": 4, "type": "solid", "shadowColor": "rgba(255, 170, 0, 0.5)", "shadowBlur": 10},
            "itemStyle": {"color": "#ffaa00", "borderColor": "#fff", "borderWidth": 2},
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(255, 170, 0, 0.3)"},
                        {"offset": 1, "color": "rgba(255, 170, 0, 0)"}
                    ]
                }
            },
            "emphasis": {
                "focus": "series",
                "itemStyle": {"shadowBlur": 20, "shadowColor": "#ffaa00", "scale": 1.5},
                "lineStyle": {"width": 5}
            },
            "animationDuration": 2000,
            "animationEasing": "elasticOut",
            "animationDelay": 600
        }
    ]
}

node_quality_path = "data/processed/node_quality.csv"
try:
    df_node_quality = pd.read_csv(node_quality_path)
    df_node_quality["node_id"] = df_node_quality["node_id"].astype(int)
except FileNotFoundError:
    df_node_quality = pd.DataFrame({
        "node_id": list(range(8001, 8043)),
        "val_loss": np.random.uniform(0.01, 0.05, 42),
        "status": ["normal"] * 42
    })
    abnormal_indices = np.random.choice(42, 3, replace=False)
    for idx in abnormal_indices:
        df_node_quality.loc[idx, "status"] = "abnormal"
        df_node_quality.loc[idx, "val_loss"] = np.random.uniform(0.08, 0.12)

node_ids = df_node_quality["node_id"].tolist()
val_losses = df_node_quality["val_loss"].tolist()

# 根据val_loss阈值重新判定异常点（与颜色逻辑一致）
# val_loss >= 0.08 认为是异常点
statuses = ["abnormal" if loss >= 0.08 else "normal" for loss in val_losses]

# 计算关键指标
total_nodes = len(node_ids)
normal_nodes = statuses.count("normal")
abnormal_nodes = statuses.count("abnormal")
avg_val_loss = np.mean(val_losses)
min_val_loss = np.min(val_losses)

# 页面顶部指标卡片 - 使用page4样式
st.markdown("##### 联邦学习节点概览")
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

with col_kpi1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%);
                border: 1px solid rgba(33, 150, 243, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;"
         title="参与联邦学习的节点总数">
        <div style="color: #2196F3; font-size: 14px; margin-bottom: 8px; font-weight: 700;">节点总数</div>
        <div style="color: #ffffff; font-size: 32px; font-weight: 900; text-shadow: 0 0 15px rgba(255,255,255,0.4);">{total_nodes}</div>
        <div style="color: #c0c0c0; font-size: 14px; font-weight: 700;">个</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
                border: 1px solid rgba(76, 175, 80, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;"
         title="状态正常的节点数量">
        <div style="color: #4CAF50; font-size: 14px; margin-bottom: 8px; font-weight: 700;">正常节点</div>
        <div style="color: #ffffff; font-size: 32px; font-weight: 900; text-shadow: 0 0 15px rgba(255,255,255,0.4);">{normal_nodes}</div>
        <div style="color: #c0c0c0; font-size: 14px; font-weight: 700;">个</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 99, 132, 0.2) 0%, rgba(255, 99, 132, 0.1) 100%);
                border: 1px solid rgba(255, 99, 132, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;"
         title="状态异常的节点数量">
        <div style="color: #ff6384; font-size: 14px; margin-bottom: 8px; font-weight: 700;">异常节点</div>
        <div style="color: #ffffff; font-size: 32px; font-weight: 900; text-shadow: 0 0 15px rgba(255,255,255,0.4);">{abnormal_nodes}</div>
        <div style="color: #c0c0c0; font-size: 14px; font-weight: 700;">个</div>
    </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%);
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;"
         title="所有节点的平均验证损失">
        <div style="color: #FFC107; font-size: 14px; margin-bottom: 8px; font-weight: 700;">平均验证损失</div>
        <div style="color: #ffffff; font-size: 32px; font-weight: 900; text-shadow: 0 0 15px rgba(255,255,255,0.4);">{avg_val_loss:.4f}</div>
        <div style="color: #c0c0c0; font-size: 14px; font-weight: 700;">最低: {min_val_loss:.4f}</div>
    </div>
    """, unsafe_allow_html=True)

# 准备散点气泡图数据
scatter_data_normal = []
scatter_data_abnormal = []

for i, (node_id, val_loss, status) in enumerate(zip(node_ids, val_losses, statuses)):
    # 计算气泡大小 (根据损失值反比，损失越小气泡越大)
    symbol_size = max(15, min(50, (0.15 - val_loss) * 400))
    
    # 计算颜色 (根据损失值渐变)
    if val_loss < 0.03:
        color = "#00ff88"  # 绿色 - 优秀
    elif val_loss < 0.05:
        color = "#00aaff"  # 蓝色 - 良好
    elif val_loss < 0.08:
        color = "#ffd93d"  # 黄色 - 一般
    else:
        color = "#ff6b6b"  # 红色 - 较差
    
    point = {
        "value": [i % 7, i // 7, float(val_loss)],
        "node_id": int(node_id),
        "symbolSize": symbol_size,
        "itemStyle": {
            "color": {
                "type": "radial",
                "x": 0.5, "y": 0.5, "r": 0.5,
                "colorStops": [
                    {"offset": 0, "color": "#ffffff"},
                    {"offset": 0.3, "color": color},
                    {"offset": 1, "color": color}
                ]
            },
            "shadowBlur": 20,
            "shadowColor": color
        }
    }
    
    if status == "abnormal":
        scatter_data_abnormal.append(point)
    else:
        scatter_data_normal.append(point)

node_quality_scatter_option = {
    "backgroundColor": "transparent",
    "title": {
        "text": "◉ 节点质量分布图",
        "textStyle": {
            "color": "#00ff88",
            "fontSize": 18,
            "fontWeight": "bold",
            "fontFamily": "Orbitron",
            "textShadowColor": "rgba(0, 255, 136, 0.8)",
            "textShadowBlur": 15
        },
        "left": "center",
        "top": 10
    },
    "tooltip": {
        "trigger": "item",
        "backgroundColor": "rgba(10, 10, 26, 0.95)",
        "borderColor": "#00ff88",
        "borderWidth": 2,
        "textStyle": {"color": "#e0e0e0", "fontSize": 14, "fontFamily": "Orbitron"},
        "formatter": JsCode("""function(params) {
            var data = params.data;
            var loss = data.value[2];
            var quality = loss < 0.03 ? '<span style=\"color:#00ff88\">★★★ 优秀</span>' : 
                         loss < 0.05 ? '<span style=\"color:#00aaff\">★★☆ 良好</span>' :
                         loss < 0.08 ? '<span style=\"color:#ffd93d\">★☆☆ 一般</span>' : '<span style=\"color:#ff6b6b\">☆☆☆ 较差</span>';
            return '<div style="font-family:Orbitron;text-align:center;padding:5px;">' +
                   '<div style="font-size:18px;font-weight:bold;color:#00ff88;margin-bottom:10px;text-shadow:0 0 10px rgba(0,255,136,0.5);">节点 ' + data.node_id + '</div>' +
                   '<div style="font-size:14px;color:#c0c0c0;margin-bottom:8px;">验证损失</div>' +
                   '<div style="font-size:20px;font-weight:bold;color:#fff;margin-bottom:10px;text-shadow:0 0 15px rgba(255,255,255,0.5);">' + loss.toFixed(6) + '</div>' +
                   '<div style="font-size:13px;">' + quality + '</div>' +
                   '</div>';
        }""")
    },
    "legend": {
        "data": ["正常节点", "异常节点"],
        "top": 45,
        "textStyle": {"color": "#e0e0e0", "fontSize": 14, "fontFamily": "Orbitron"},
        "itemGap": 20
    },
    "grid": {"left": "10%", "right": "10%", "bottom": "15%", "top": "20%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": ["Col 1", "Col 2", "Col 3", "Col 4", "Col 5", "Col 6", "Col 7"],
        "axisLabel": {"color": "#c0c0c0", "fontSize": 14, "fontFamily": "Orbitron"},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.05)"}},
        "boundaryGap": True
    },
    "yAxis": {
        "type": "category",
        "data": ["Row 6", "Row 5", "Row 4", "Row 3", "Row 2", "Row 1"],
        "axisLabel": {"color": "#c0c0c0", "fontSize": 14, "fontFamily": "Orbitron"},
        "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
        "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.05)"}},
        "boundaryGap": True
    },
    "series": [
        {
            "name": "正常节点",
            "type": "scatter",
            "data": scatter_data_normal,
            "symbol": "circle",
            "label": {
                "show": True,
                "formatter": JsCode("function(params) { return params.data.node_id; }").js_code,
                "fontSize": 12,
                "fontFamily": "Orbitron",
                "color": "#fff",
                "fontWeight": "bold"
            },
            "emphasis": {
                "scale": 1.5,
                "label": {"fontSize": 16},
                "itemStyle": {
                    "shadowBlur": 40,
                    "shadowColor": "#00ff88"
                }
            },
            "animationDuration": 2000,
            "animationEasing": "elasticOut",
            "animationDelay": JsCode("function(idx) { return idx * 80; }")
        },
        {
            "name": "异常节点",
            "type": "effectScatter",
            "data": scatter_data_abnormal,
            "symbol": "circle",
            "rippleEffect": {
                "brushType": "stroke",
                "scale": 3,
                "period": 4
            },
            "itemStyle": {
                "color": "#ff0000",
                "shadowBlur": 30,
                "shadowColor": "#ff0000"
            },
            "label": {
                "show": True,
                "formatter": JsCode("function(params) { return params.data.node_id; }").js_code,
                "fontSize": 12,
                "fontFamily": "Orbitron",
                "color": "#fff",
                "fontWeight": "bold"
            },
            "emphasis": {
                "scale": 1.5,
                "label": {"fontSize": 16}
            },
            "animationDuration": 2000,
            "animationEasing": "elasticOut",
            "animationDelay": JsCode("function(idx) { return idx * 80 + 500; }")
        }
    ]
}

col1, col2 = st.columns(2)
with col1:
    st_echarts(node_quality_scatter_option, height="500px", key=f"node_quality_scatter_{id(node_quality_scatter_option)}")
with col2:
    st_echarts(line_option, height="450px", key=f"line_chart_{id(line_option)}")

with st.expander("查看节点质量详情图表", expanded=False):
    # 准备ECharts数据 - 按节点ID排序
    node_chart_data = []
    for _, row in df_node_quality.iterrows():
        val_loss = float(row["val_loss"])
        status = row["status"]
        node_id = int(row["node_id"])
        
        # 质量评级和颜色
        if val_loss < 0.03:
            quality = "★★★"
            quality_color = "#00ff88"
        elif val_loss < 0.05:
            quality = "★★☆"
            quality_color = "#00aaff"
        elif val_loss < 0.08:
            quality = "★☆☆"
            quality_color = "#ffd93d"
        else:
            quality = "☆☆☆"
            quality_color = "#ff6b6b"
        
        node_chart_data.append({
            "node_id": str(node_id),
            "val_loss": val_loss,
            "quality": quality,
            "quality_color": quality_color,
            "is_normal": status == "normal"
        })
    
    # 按节点ID排序
    node_chart_data.sort(key=lambda x: int(x["node_id"]))
    
    # 计算统计数据
    excellent_count = sum(1 for d in node_chart_data if "★★★" in d["quality"])
    good_count = sum(1 for d in node_chart_data if "★★☆" in d["quality"])
    abnormal_count = sum(1 for d in node_chart_data if not d["is_normal"])
    
    # ECharts 节点质量统计图表 - 柱状图+折线图组合风格
    node_quality_stats_option = {
        "backgroundColor": "transparent",
        "title": {
            "text": "◉ 节点质量统计表",
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
            "axisPointer": {"type": "cross"},
            "backgroundColor": "rgba(10, 10, 26, 0.95)",
            "borderColor": "#00ffcc",
            "borderWidth": 1,
            "textStyle": {
                "color": "#ffffff",
                "fontFamily": "Orbitron"
            },
            "formatter": JsCode("""function(params) {
                var nodeId = params[0].axisValue;
                var valLoss = params[0].data.val_loss !== undefined ? params[0].data.val_loss : params[0].value;
                var quality = params[0].data.quality;
                var qualityColor = params[0].data.quality_color;
                var isNormal = params[0].data.is_normal;
                var statusText = isNormal ? '<span style="color:#00ff88">● 正常</span>' : '<span style="color:#ff0000">● 异常</span>';
                return '<div style="font-family:Orbitron;padding:5px;">' +
                       '<div style="font-size:16px;font-weight:bold;color:' + qualityColor + ';margin-bottom:8px;">节点 ' + nodeId + '</div>' +
                       '<div style="font-size:13px;color:#c0c0c0;margin-bottom:5px;">验证损失: <span style="color:#fff;font-weight:bold;">' + valLoss.toFixed(6) + '</span></div>' +
                       '<div style="font-size:13px;color:#c0c0c0;margin-bottom:5px;">质量评级: <span style="color:' + qualityColor + ';font-weight:bold;">' + quality + '</span></div>' +
                       '<div style="font-size:12px;">' + statusText + '</div>' +
                       '</div>';
            }""")
        },
        "grid": {
            "left": "3%",
            "right": "4%",
            "bottom": "3%",
            "top": "18%",
            "containLabel": True
        },
        "xAxis": {
            "type": "category",
            "data": [d["node_id"] for d in node_chart_data],
            "axisLabel": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron",
                "fontSize": 11,
                "rotate": 45
            },
            "axisLine": {
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.3)"
                }
            }
        },
        "yAxis": {
            "type": "value",
            "name": "验证损失",
            "nameTextStyle": {
                "color": "#00ffcc",
                "fontFamily": "Orbitron"
            },
            "axisLabel": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron",
                "formatter": "{value}"
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
                "name": "验证损失",
                "type": "bar",
                "data": [
                    {
                        "value": d["val_loss"],
                        "val_loss": d["val_loss"],
                        "quality": d["quality"],
                        "quality_color": d["quality_color"],
                        "is_normal": d["is_normal"],
                        "itemStyle": {
                            "color": {
                                "type": "linear",
                                "x": 0,
                                "y": 0,
                                "x2": 0,
                                "y2": 1,
                                "colorStops": [
                                    {"offset": 0, "color": d["quality_color"]},
                                    {"offset": 1, "color": d["quality_color"] + "60"}
                                ]
                            },
                            "borderRadius": [4, 4, 0, 0],
                            "shadowBlur": 5,
                            "shadowColor": d["quality_color"]
                        }
                    } for d in node_chart_data
                ],
                "barWidth": "50%",
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": JsCode("function(params) { return params.data.quality; }").js_code,
                    "color": "#ffffff",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 15,
                        "shadowColor": "rgba(0, 255, 136, 0.5)"
                    }
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            },
            {
                "name": "质量阈值线",
                "type": "line",
                "data": [0.03] * len(node_chart_data),
                "smooth": False,
                "lineStyle": {
                    "color": "#00ff88",
                    "width": 2,
                    "type": "dashed"
                },
                "symbol": "none",
                "silent": True
            },
            {
                "name": "异常标记",
                "type": "scatter",
                "data": [
                    {
                        "value": [i, d["val_loss"]],
                        "symbol": "triangle",
                        "symbolSize": 15,
                        "itemStyle": {
                            "color": "#ff0000",
                            "shadowBlur": 10,
                            "shadowColor": "#ff0000"
                        }
                    } for i, d in enumerate(node_chart_data) if not d["is_normal"]
                ],
                "z": 10
            }
        ],
        "legend": {
            "data": ["验证损失", "质量阈值线", "异常标记"],
            "top": 35,
            "textStyle": {
                "color": "#c0c0c0",
                "fontFamily": "Orbitron"
            }
        }
    }
    
    # 显示ECharts图表
    st_echarts(options=node_quality_stats_option, height="400px", key="node_quality_stats_chart")
    
    # 底部统计栏
    st.markdown(f"""
    <div style="display: flex; gap: 30px; margin-top: 15px; padding: 15px; 
                background: linear-gradient(135deg, rgba(10, 10, 26, 0.95) 0%, rgba(15, 52, 96, 0.9) 100%);
                border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 8px;
                box-shadow: 0 0 20px rgba(0, 255, 136, 0.1);
                font-family: 'Orbitron', sans-serif; font-size: 13px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #888;">优秀节点:</span>
            <span style="color: #00ff88; font-weight: bold; text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);">{excellent_count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #888;">良好节点:</span>
            <span style="color: #00aaff; font-weight: bold; text-shadow: 0 0 5px rgba(0, 170, 255, 0.5);">{good_count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #888;">异常节点:</span>
            <span style="color: #ff0000; font-weight: bold; text-shadow: 0 0 5px rgba(255, 0, 0, 0.5);">{abnormal_count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="color: #888;">总节点数:</span>
            <span style="color: #00ff88; font-weight: bold; text-shadow: 0 0 5px rgba(0, 255, 136, 0.5);">{len(node_chart_data)}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.subheader("实验对比分析")

# 数据量散点图
col3, col4 = st.columns(2)
with col3:
    # 读取 node_train_samples.csv 和 node_quality.csv
    node_train_samples_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "node_train_samples.csv")
    node_quality_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "node_quality.csv")
    
    if os.path.exists(node_train_samples_path) and os.path.exists(node_quality_path):
        try:
            # 读取训练样本数据
            df_train_samples = pd.read_csv(node_train_samples_path)
            # 读取验证损失数据
            df_quality = pd.read_csv(node_quality_path)
            
            # 合并数据
            df_merged = pd.merge(df_train_samples, df_quality[['node_id', 'val_loss']], on='node_id', how='inner')
            
            # 准备散点图数据
            # 将MSE值大于0.05的设为异常值
            normal_data = []
            abnormal_data = []
            for _, row in df_merged.iterrows():
                val_loss = float(row["val_loss"])
                train_samples = int(row["train_samples"])
                node_id = int(row["node_id"])
                # 判定逻辑：MSE > 0.05 为异常
                is_abnormal = val_loss > 0.05
                
                point = {
                    "value": [train_samples, val_loss],
                    "node_id": node_id,
                    "train_samples": train_samples,
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowColor": "#ff0000" if is_abnormal else "#00ff88"
                    }
                }
                if is_abnormal:
                    abnormal_data.append(point)
                else:
                    normal_data.append(point)
            
            # ECharts 科技感散点图配置
            scatter_option = {
                "backgroundColor": "transparent",
                "title": {
                    "text": "数据量散点图：训练样本数 vs 验证损失",
                    "textStyle": {
                        "color": "#00ff88",
                        "fontSize": 16,
                        "fontWeight": "bold",
                        "textShadowColor": "rgba(0, 255, 136, 0.5)",
                        "textShadowBlur": 10
                    },
                    "left": "center",
                    "top": 10
                },
                "tooltip": {
                    "trigger": "item",
                    "backgroundColor": "rgba(10, 10, 26, 0.95)",
                    "borderColor": "#00ff88",
                    "borderWidth": 1,
                    "textStyle": {"color": "#e0e0e0", "fontSize": 14},
                    "formatter": JsCode("""function(params) {
                        return '<div style="font-family:Orbitron;padding:8px;">' +
                               '<div style="font-size:16px;font-weight:bold;color:#00ff88;margin-bottom:8px;">节点 ' + params.data.node_id + '</div>' +
                               '<div style="font-size:13px;color:#c0c0c0;margin-bottom:5px;">训练样本数: <span style="color:#fff;font-weight:bold;">' + params.data.train_samples.toLocaleString() + '</span></div>' +
                               '<div style="font-size:13px;color:#c0c0c0;">验证损失 (MSE): <span style="color:#fff;font-weight:bold;">' + params.data.value[1].toFixed(6) + '</span></div>' +
                               '</div>';
                    }""").js_code
                },
                "grid": {"left": "10%", "right": "10%", "bottom": "15%", "top": "20%", "containLabel": True},
                "xAxis": {
                    "type": "value",
                    "name": "训练样本数",
                    "nameTextStyle": {"color": "#00ff88", "fontSize": 16},
                    "axisLine": {"lineStyle": {"color": "#00ff88", "width": 2}},
                    "axisLabel": {"color": "#e0e0e0"},
                    "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}},
                    "scale": True
                },
                "yAxis": {
                    "type": "value",
                    "name": "验证损失 (MSE)",
                    "nameTextStyle": {"color": "#00ff88", "fontSize": 16},
                    "axisLine": {"lineStyle": {"color": "#00ff88", "width": 2}},
                    "axisLabel": {"color": "#e0e0e0", "fontSize": 14},
                    "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}},
                    "scale": True
                },
                "dataZoom": [
                    {"type": "inside", "xAxisIndex": 0, "filterMode": "filter"},
                    {"type": "inside", "yAxisIndex": 0, "filterMode": "filter"},
                    {"type": "slider", "xAxisIndex": 0, "filterMode": "filter", "bottom": "5%", 
                     "borderColor": "#00ff88", "fillerColor": "rgba(0, 255, 136, 0.2)", "textStyle": {"color": "#e0e0e0"}},
                    {"type": "slider", "yAxisIndex": 0, "filterMode": "filter", "right": "2%",
                     "borderColor": "#00ff88", "fillerColor": "rgba(0, 255, 136, 0.2)", "textStyle": {"color": "#e0e0e0"}}
                ],
                "legend": {
                    "data": ["正常节点", "异常节点"],
                    "top": 45,
                    "textStyle": {"color": "#e0e0e0"}
                },
                "series": [
                    {
                        "name": "正常节点",
                        "type": "scatter",
                        "data": normal_data,
                        "symbolSize": 15,
                        "itemStyle": {
                            "color": {
                                "type": "radial",
                                "x": 0.5, "y": 0.5, "r": 0.5,
                                "colorStops": [
                                    {"offset": 0, "color": "#66ffaa"},
                                    {"offset": 1, "color": "#00ff88"}
                                ]
                            },
                            "borderColor": "#ffffff",
                            "borderWidth": 2
                        },
                        "emphasis": {
                            "scale": 1.5,
                            "itemStyle": {
                                "shadowBlur": 30,
                                "shadowColor": "#00ff88"
                            }
                        },
                        "animationDelay": JsCode("function(idx) { return idx * 30; }").js_code
                    },
                    {
                        "name": "异常节点",
                        "type": "scatter",
                        "data": abnormal_data,
                        "symbolSize": 18,
                        "itemStyle": {
                            "color": {
                                "type": "radial",
                                "x": 0.5, "y": 0.5, "r": 0.5,
                                "colorStops": [
                                    {"offset": 0, "color": "#ff6b6b"},
                                    {"offset": 1, "color": "#ff0000"}
                                ]
                            },
                            "borderColor": "#ffffff",
                            "borderWidth": 2
                        },
                        "emphasis": {
                            "scale": 1.5,
                            "itemStyle": {
                                "shadowBlur": 30,
                                "shadowColor": "#ff0000"
                            }
                        },
                        "animationDelay": JsCode("function(idx) { return idx * 30 + 200; }").js_code
                    }
                ],
                "animation": True,
                "animationDuration": 1500,
                "animationEasing": "elasticOut"
            }
            
            # 显示 ECharts 散点图
            st_echarts(scatter_option, height="450px", key=f"scatter_chart_{id(scatter_option)}")
            

                    
        except Exception as e:
            st.error(f"读取数据文件失败: {e}")
    else:
        missing_files = []
        if not os.path.exists(node_train_samples_path):
            missing_files.append("data/node_train_samples.csv")
        if not os.path.exists(node_quality_path):
            missing_files.append("data/processed/node_quality.csv")
        st.warning(f"未找到以下文件: {', '.join(missing_files)}")

@st.cache_data
def load_ablation_data():
    """从CSV加载消融实验数据"""
    import os
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "experiments_summary.csv")
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, on_bad_lines='skip')
            
            # 直接使用CSV中的sMAPE字段
            df["sMAPE"] = pd.to_numeric(df["sMAPE"], errors="coerce")
            
            # 过滤有效数据
            df = df.dropna(subset=["sMAPE"])
            df = df.sort_values("sMAPE", ascending=True)
            return df
        except Exception as e:
            st.warning(f"读取实验数据失败: {e}")
            return None
    return None

df_experiments = load_ablation_data()

ablation_datasets = {}
if df_experiments is not None:
    # 2节点实验 - 显示所有数据
    df_2node = df_experiments[df_experiments["node_count"] == 2]
    if not df_2node.empty:
        ablation_datasets["2 节点"] = [
            {"method": row["name"].split("（")[0][:15], "smape": round(float(row["sMAPE"]), 2)}
            for _, row in df_2node.iterrows()
        ]
    
    # 5节点实验 - 显示所有数据
    df_5node = df_experiments[df_experiments["node_count"] == 5]
    if not df_5node.empty:
        ablation_datasets["5 节点"] = [
            {"method": row["name"].split("（")[0][:15], "smape": round(float(row["sMAPE"]), 2)}
            for _, row in df_5node.iterrows()
        ]
    
    # 41节点实验 - 显示所有数据
    df_41node = df_experiments[df_experiments["node_count"] == 41]
    if not df_41node.empty:
        ablation_datasets["41 节点"] = [
            {"method": row["name"].split("（")[0][:15], "smape": round(float(row["sMAPE"]), 2)}
            for _, row in df_41node.iterrows()
        ]
    
    # 全部实验 - 包含CSV所有数据和微调对比数据
    all_experiments = [
        {"method": row["name"][:18], "smape": round(float(row["sMAPE"]), 2)}
        for _, row in df_experiments.iterrows()
    ]
    # 添加微调对比数据到全部实验
    all_experiments.extend([
        {"method": "原始微调", "smape": 72.05},
        {"method": "二次微调", "smape": 71.01},
        {"method": "最佳模型选择", "smape": 71.77}
    ])
    ablation_datasets["全部实验"] = all_experiments

if not ablation_datasets:
    ablation_datasets = {
        "默认数据": [
            {"method": "基线模型", "smape": 68.5},
            {"method": "+贝叶斯优化", "smape": 62.3},
            {"method": "+口径对齐", "smape": 56.8},
            {"method": "+粒度匹配", "smape": 50.2},
            {"method": "+动态加权", "smape": 43.5},
            {"method": "融合模型", "smape": 37.8}
        ]
    }

# 定义筛选选项
filter_options = {
    "节点数": [1, 2, 3, 5, 7, 41, 42, 500],
    "窗口长度": ["7day", "1day", "6hour"],
    "μ值": [0.05, 0.01536, 0.07764],
    "特征选择": ["v1", "v1+清华聚类", "时序特征", "日聚合v1", "v1+清华+SHAP时段权重", "个性化微调", "可学习时段架构"]
}

# 准备筛选数据 - 从CSV中读取所有实验数据用于筛选
all_experiments_for_filter = []
if df_experiments is not None:
    for _, row in df_experiments.iterrows():
        all_experiments_for_filter.append({
            "name": row["name"],
            "node_count": int(row["node_count"]),
            "window": row["window"],
            "smape": round(float(row["sMAPE"]), 2),
            "mu": float(row["μ"]),
            "features": row["features"]
        })

with col4:
    # 四个筛选器在一行显示
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        selected_node_count = st.selectbox(
            "节点数",
            options=filter_options["节点数"],
            index=3,  # 默认选中5
            key="filter_node_count"
        )
    
    with filter_col2:
        selected_window = st.selectbox(
            "窗口长度",
            options=filter_options["窗口长度"],
            index=0,  # 默认选中7day
            key="filter_window"
        )
    
    with filter_col3:
        selected_mu = st.selectbox(
            "μ值",
            options=filter_options["μ值"],
            index=0,  # 默认选中0.05
            key="filter_mu"
        )
    
    with filter_col4:
        selected_features = st.selectbox(
            "特征选择",
            options=filter_options["特征选择"],
            index=0,  # 默认选中v1
            key="filter_features"
        )

# 根据筛选条件过滤数据
filtered_experiments = [
    exp for exp in all_experiments_for_filter
    if exp["node_count"] == selected_node_count
    and exp["window"] == selected_window
    and exp["mu"] == selected_mu
    and exp["features"] == selected_features
]

# 如果没有匹配的实验，显示所有数据
if not filtered_experiments:
    ablation_data = [
        {"method": exp["name"][:20], "smape": exp["smape"]}
        for exp in all_experiments_for_filter
    ]
else:
    ablation_data = [
        {"method": exp["name"][:20], "smape": exp["smape"]}
        for exp in filtered_experiments
    ]

df_ablation = pd.DataFrame(ablation_data)

gradient_colors = [
    {"offset": 0, "color": "#ff6b6b"},
    {"offset": 1, "color": "#ff8e8e"}
], [
    {"offset": 0, "color": "#ffd93d"},
    {"offset": 1, "color": "#ffe066"}
], [
    {"offset": 0, "color": "#6bcbff"},
    {"offset": 1, "color": "#a8e6ff"}
], [
    {"offset": 0, "color": "#00ff88"},
    {"offset": 1, "color": "#66ffaa"}
], [
    {"offset": 0, "color": "#f39c12"},
    {"offset": 1, "color": "#f7b731"}
], [
    {"offset": 0, "color": "#9b59b6"},
    {"offset": 1, "color": "#be90d4"}
], [
    {"offset": 0, "color": "#e74c3c"},
    {"offset": 1, "color": "#ec7063"}
], [
    {"offset": 0, "color": "#3498db"},
    {"offset": 1, "color": "#5dade2"}
], [
    {"offset": 0, "color": "#1abc9c"},
    {"offset": 1, "color": "#48c9b0"}
], [
    {"offset": 0, "color": "#e67e22"},
    {"offset": 1, "color": "#f0a04b"}
]

bar_data = []
for i, row in df_ablation.iterrows():
    bar_data.append({
        "value": row["smape"],
        "itemStyle": {
            "color": {
                "type": "linear",
                "x": 0, "y": 0, "x2": 0, "y2": 1,
                "colorStops": gradient_colors[i % len(gradient_colors)]
            },
            "borderRadius": [8, 8, 0, 0],
            "shadowColor": gradient_colors[i % len(gradient_colors)][0]["color"],
            "shadowBlur": 15,
            "shadowOffsetY": 5
        }
    })

# 构建筛选条件描述文本
filter_desc = f"{selected_node_count}节点-{selected_window}-μ{selected_mu}-{selected_features}"

ablation_option = {
    "backgroundColor": "transparent",
    "title": {
        "text": f"消融实验对比 - {filter_desc}",
        "textStyle": {
            "color": "#00ff88",
            "fontSize": 16,
            "fontWeight": "bold",
            "textShadowColor": "rgba(0, 255, 136, 0.5)",
            "textShadowBlur": 10
        },
        "left": "center",
        "top": 10
    },
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "shadow",
            "shadowStyle": {
                "color": "rgba(0, 255, 136, 0.1)"
            }
        },
        "backgroundColor": "rgba(10, 10, 26, 0.9)",
        "borderColor": "#00ff88",
        "borderWidth": 1,
        "textStyle": {"color": "#e0e0e0"},
        "formatter": "{b}<br/>sMAPE: {c}%"
    },
    "grid": {"left": "3%", "right": "4%", "bottom": "8%", "top": "15%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "data": df_ablation["method"].tolist(),
        "axisLabel": {
            "color": "#e0e0e0",
            "rotate": 30,
            "interval": 0,
            "fontSize": 11
        },
        "axisLine": {
            "lineStyle": {
                "color": "#00ff88",
                "width": 2
            }
        },
        "axisTick": {
            "lineStyle": {"color": "#00ff88"}
        }
    },
    "yAxis": {
        "type": "value",
        "name": "sMAPE (%)",
        "nameTextStyle": {
            "color": "#00ff88",
            "fontSize": 14,
            "padding": [0, 0, 10, 0]
        },
        "min": 0,
        "max": 110,
        "axisLabel": {
            "color": "#e0e0e0",
            "fontSize": 14
        },
        "axisLine": {
            "lineStyle": {
                "color": "#00ff88",
                "width": 2
            }
        },
        "splitLine": {
            "lineStyle": {
                "color": "rgba(0, 255, 136, 0.15)",
                "type": "dashed"
            }
        }
    },
    "dataZoom": [
        {
            "type": "slider",
            "show": True,
            "xAxisIndex": [0],
            "start": 0,
            "end": 50,
            "bottom": 10,
            "height": 20,
            "borderColor": "rgba(0, 255, 136, 0.3)",
            "fillerColor": "rgba(0, 255, 136, 0.2)",
            "backgroundColor": "rgba(10, 10, 26, 0.5)",
            "handleStyle": {
                "color": "#00ff88",
                "shadowBlur": 10,
                "shadowColor": "rgba(0, 255, 136, 0.5)"
            },
            "textStyle": {"color": "#c0c0c0"},
            "brushSelect": False
        },
        {
            "type": "inside",
            "xAxisIndex": [0],
            "start": 0,
            "end": 50,
            "zoomOnMouseWheel": False,
            "moveOnMouseWheel": True,
            "moveOnMouseMove": True
        }
    ],
    "series": [{
        "name": "sMAPE (%)",
        "type": "bar",
        "data": bar_data,
        "barWidth": "45%",
        "label": {
            "show": True,
            "position": "top",
            "formatter": JsCode("function(params) { return params.value.toFixed(2) + '%'; }").js_code,
            "color": "#ffffff",
            "fontSize": 15,
            "fontWeight": "bold",
            "textShadowColor": "rgba(0, 0, 0, 0.8)",
            "textShadowBlur": 4
        },
        "emphasis": {
            "itemStyle": {
                "shadowBlur": 25,
                "shadowColor": "rgba(0, 255, 136, 0.6)"
            },
            "label": {
                "fontSize": 15,
                "color": "#00ff88"
            }
        },
        "animationDuration": 1500,
        "animationEasing": "elasticOut",
        "animationDelay": JsCode("function(idx) { return idx * 200; }").js_code
    }],
    "animation": True,
    "animationDurationUpdate": 1000,
    "animationEasingUpdate": "cubicInOut"
}

# 如果数据量大于6，添加自动轮播功能
if len(bar_data) > 6:
    # 添加自动轮播的JavaScript代码
    auto_scroll_js = JsCode("""
        function(chart) {
            var dataLen = chart.getOption().series[0].data.length;
            var showCount = 6; // 每次显示6个数据
            var startPercent = 0;
            var endPercent = (showCount / dataLen) * 100;
            var direction = 1; // 1为向右，-1为向左
            
            setInterval(function() {
                if (direction === 1) {
                    startPercent += 5;
                    endPercent += 5;
                    if (endPercent >= 100) {
                        direction = -1;
                    }
                } else {
                    startPercent -= 5;
                    endPercent -= 5;
                    if (startPercent <= 0) {
                        direction = 1;
                    }
                }
                
                chart.dispatchAction({
                    type: 'dataZoom',
                    start: startPercent,
                    end: endPercent
                });
            }, 2000); // 每2秒滚动一次
        }
    """)
    ablation_option["onReady"] = auto_scroll_js

with col4:
    st_echarts(ablation_option, height="450px", key=f"ablation_chart_{filter_desc}")

# 获取项目根目录（假设脚本在 pages/ 下，向上两级到达项目根目录）
_project_root = os.path.dirname(os.path.dirname(__file__))

# 1. 微调损失曲线图片（尝试多个可能的路径）
st.subheader("个性化微调训练损失曲线")

# 尝试多个可能的图片路径
possible_paths = [
    os.path.join(_project_root, "data", "image", "curves..png"),
    os.path.join(_project_root, "data", "image", "curves1.png"),
    os.path.join(_project_root, "data", "image", "curves.png"),
]

loss_curve_img = None
for path in possible_paths:
    if os.path.exists(path):
        loss_curve_img = path
        break

if loss_curve_img:
    # 读取图片并转换为base64
    import base64
    with open(loss_curve_img, "rb") as f:
        img_bytes = f.read()
        img_base64 = base64.b64encode(img_bytes).decode()
    
    # 使用HTML显示图片，添加透明背景样式，调整比例为60%宽度
    st.markdown(f"""
    <div style="background: transparent; display: flex; justify-content: center;">
        <img src="data:image/png;base64,{img_base64}" 
             style="width: 60%; background: transparent;" 
             alt="微调损失曲线"/>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("未找到微调损失曲线图片，请检查路径：data/image/curves.png")

# 2. 各节点最佳验证 sMAPE 柱状图（ECharts Timeline轮播）
st.subheader("各节点最佳验证 sMAPE")
best_model_csv = os.path.join(_project_root, "data", "final_comparison.csv")
if os.path.exists(best_model_csv):
    df_best = pd.read_csv(best_model_csv)
    
    # 准备数据 - 按node_id排序
    df_best = df_best.sort_values('node_id').reset_index(drop=True)
    
    # 每10个节点为一组
    group_size = 10
    total_nodes = len(df_best)
    num_groups = (total_nodes + group_size - 1) // group_size
    
    # 准备timeline的options
    timeline_options = []
    colors = ["#00ff88", "#00aaff", "#ffd93d", "#ff6b6b", "#9b59b6", "#e74c3c", "#1abc9c", "#f39c12"]
    
    for group_idx in range(num_groups):
        start_idx = group_idx * group_size
        end_idx = min((group_idx + 1) * group_size, total_nodes)
        group_data = df_best.iloc[start_idx:end_idx]
        
        node_ids = group_data['node_id'].astype(str).tolist()
        best_smapes = group_data['best_smape'].tolist()
        best_models = group_data['best_model'].tolist()
        
        # 构建series数据
        series_data = []
        for i, (smape, model) in enumerate(zip(best_smapes, best_models)):
            color = "#00ff88" if model == "secondary" else "#00aaff"
            series_data.append({
                "value": round(smape, 2),
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": color},
                            {"offset": 1, "color": color + "80"}
                        ]
                    },
                    "borderRadius": [6, 6, 0, 0],
                    "shadowBlur": 10,
                    "shadowColor": color
                }
            })
        
        option = {
            "title": {
                "text": f"节点 {group_data['node_id'].iloc[0]} - {group_data['node_id'].iloc[-1]}",
                "left": "center",
                "textStyle": {
                    "color": "#00ff88",
                    "fontSize": 14,
                    "fontFamily": "Orbitron"
                }
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(10, 10, 26, 0.95)",
                "borderColor": "#00ff88",
                "borderWidth": 1,
                "textStyle": {"color": "#ffffff", "fontFamily": "Orbitron"},
                "formatter": JsCode("""function(params) {
                    var data = params[0];
                    return '<div style="font-family:Orbitron;padding:5px;">' +
                           '<div style="font-size:14px;font-weight:bold;color:#00ff88;margin-bottom:5px;">节点 ' + data.name + '</div>' +
                           '<div style="font-size:13px;color:#c0c0c0;">sMAPE: <span style="color:#fff;font-weight:bold;">' + data.value + '%</span></div>' +
                           '</div>';
                }""")
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
                "data": node_ids,
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.3)", "width": 1}
                }
            },
            "yAxis": {
                "type": "value",
                "name": "sMAPE (%)",
                "nameTextStyle": {
                    "color": "#00ff88",
                    "fontFamily": "Orbitron"
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.3)", "width": 1}
                },
                "splitLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}
                }
            },
            "series": [{
                "type": "bar",
                "data": series_data,
                "barWidth": "60%",
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}%",
                    "color": "#ffffff",
                    "fontSize": 11,
                    "fontFamily": "Orbitron"
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            }]
        }
        timeline_options.append({
            "title": {"text": f"节点 {group_data['node_id'].iloc[0]} - {group_data['node_id'].iloc[-1]}"},
            "series": [{"data": series_data}],
            "xAxis": [{"data": node_ids}]
        })
    
    # 构建完整的timeline配置
    best_smape_timeline_option = {
        "baseOption": {
            "backgroundColor": "transparent",
            "title": {
                "text": "◉ 各节点最佳验证 sMAPE",
                "left": "center",
                "top": 5,
                "textStyle": {
                    "color": "#00ff88",
                    "fontSize": 16,
                    "fontWeight": "bold",
                    "fontFamily": "Orbitron",
                    "textShadowColor": "rgba(0, 255, 136, 0.5)",
                    "textShadowBlur": 10
                }
            },
            "timeline": {
                "axisType": "category",
                "autoPlay": True,
                "playInterval": 3000,
                "data": [f"第{i+1}组" for i in range(num_groups)],
                "left": "10%",
                "right": "10%",
                "bottom": "2%",
                "symbol": "circle",
                "symbolSize": 10,
                "lineStyle": {
                    "color": "rgba(0, 255, 136, 0.5)",
                    "width": 2
                },
                "itemStyle": {
                    "color": "#00ff88"
                },
                "checkpointStyle": {
                    "color": "#00ff88",
                    "borderColor": "#ffffff",
                    "borderWidth": 2
                },
                "controlStyle": {
                    "showNextBtn": True,
                    "showPrevBtn": True,
                    "color": "#00ff88",
                    "borderColor": "#00ff88",
                    "itemSize": 20
                },
                "label": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "#00aaff"
                    },
                    "label": {
                        "color": "#00ff88"
                    }
                }
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(10, 10, 26, 0.95)",
                "borderColor": "#00ff88",
                "borderWidth": 1,
                "textStyle": {"color": "#ffffff", "fontFamily": "Orbitron"},
                "formatter": JsCode("""function(params) {
                    var data = params[0];
                    return '<div style="font-family:Orbitron;padding:5px;">' +
                           '<div style="font-size:14px;font-weight:bold;color:#00ff88;margin-bottom:5px;">节点 ' + data.name + '</div>' +
                           '<div style="font-size:13px;color:#c0c0c0;">sMAPE: <span style="color:#fff;font-weight:bold;">' + data.value + '%</span></div>' +
                           '</div>';
                }""")
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "top": "20%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.3)", "width": 1}
                }
            },
            "yAxis": {
                "type": "value",
                "name": "sMAPE (%)",
                "nameTextStyle": {
                    "color": "#00ff88",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.3)", "width": 1}
                },
                "splitLine": {
                    "lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}
                }
            },
            "series": [{
                "type": "bar",
                "barWidth": "60%",
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}%",
                    "color": "#ffffff",
                    "fontSize": 11,
                    "fontFamily": "Orbitron"
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            }]
        },
        "options": timeline_options
    }
    
    st_echarts(best_smape_timeline_option, height="450px", key="best_smape_timeline_chart")
    
    # 显示统计信息
    avg_smape = df_best['best_smape'].mean()
    min_smape = df_best['best_smape'].min()
    max_smape = df_best['best_smape'].max()
    secondary_count = (df_best['best_model'] == 'secondary').sum()
    
    # 使用科技感卡片样式显示统计信息
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
        font-size: 13px;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Orbitron', sans-serif;
    }
    .tech-metric-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: bold;
        text-shadow: 0 0 15px rgba(0, 255, 204, 0.5);
        font-family: 'Orbitron', sans-serif;
    }
    .tech-metric-unit {
        color: #c0c0c0;
        font-size: 12px;
        margin-left: 4px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">平均 sMAPE</div>
            <div class="tech-metric-value" style="color:#00ff88">{avg_smape:.2f}<span class="tech-metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">最低 sMAPE</div>
            <div class="tech-metric-value" style="color:#00aaff">{min_smape:.2f}<span class="tech-metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">最高 sMAPE</div>
            <div class="tech-metric-value" style="color:#ff6b6b">{max_smape:.2f}<span class="tech-metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat4:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">二次微调最优</div>
            <div class="tech-metric-value" style="color:#ffd93d">{secondary_count}<span class="tech-metric-unit">个节点</span></div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("未找到节点最佳模型分配表，请检查路径：data/final_comparison.csv")

# 3. 三模型集成各节点决策准确率柱状图（ECharts Timeline轮播）
st.subheader("三模型集成各节点决策准确率")
accuracy_csv = os.path.join(_project_root, "data", "ensamble-Learner_node_accuracy.csv")
if os.path.exists(accuracy_csv):
    df_accuracy = pd.read_csv(accuracy_csv)
    
    # 转换准确率为百分比
    df_accuracy['accuracy_pct'] = df_accuracy['accuracy'] * 100
    
    # 按node_id排序（从左往右轮播）
    df_accuracy = df_accuracy.sort_values('node_id').reset_index(drop=True)
    
    # 每10个节点为一组
    group_size = 10
    total_nodes = len(df_accuracy)
    num_groups = (total_nodes + group_size - 1) // group_size
    
    # 准备timeline的options
    timeline_options = []
    
    for group_idx in range(num_groups):
        start_idx = group_idx * group_size
        end_idx = min((group_idx + 1) * group_size, total_nodes)
        group_data = df_accuracy.iloc[start_idx:end_idx]
        
        node_ids = group_data['node_id'].astype(str).tolist()
        accuracy_pcts = group_data['accuracy_pct'].tolist()
        
        # 构建series数据
        series_data = []
        for acc_pct in accuracy_pcts:
            # 根据准确率设置颜色
            if acc_pct < 60:
                color = "#ff6b6b"  # 红色 - 较低
            elif acc_pct < 80:
                color = "#ffd93d"  # 黄色 - 中等
            else:
                color = "#00ff88"  # 绿色 - 较高
            
            series_data.append({
                "value": round(acc_pct, 2),
                "itemStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0, "y": 0, "x2": 0, "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": color},
                            {"offset": 1, "color": color + "80"}
                        ]
                    },
                    "borderRadius": [6, 6, 0, 0],
                    "shadowBlur": 10,
                    "shadowColor": color
                }
            })
        
        timeline_options.append({
            "title": {"text": f"节点 {group_data['node_id'].iloc[0]} - {group_data['node_id'].iloc[-1]}"},
            "series": [{"data": series_data}],
            "xAxis": [{"data": node_ids}]
        })
    
    # 计算平均准确率用于markLine
    avg_accuracy = df_accuracy['accuracy_pct'].mean()
    
    # 构建完整的timeline配置
    accuracy_timeline_option = {
        "baseOption": {
            "backgroundColor": "transparent",
            "title": {
                "text": "◉ 三模型集成各节点决策准确率",
                "left": "center",
                "top": 5,
                "textStyle": {
                    "color": "#00ffcc",
                    "fontSize": 16,
                    "fontWeight": "bold",
                    "fontFamily": "Orbitron",
                    "textShadowColor": "rgba(0, 255, 204, 0.5)",
                    "textShadowBlur": 10
                }
            },
            "timeline": {
                "axisType": "category",
                "autoPlay": True,
                "playInterval": 3000,
                "data": [f"第{i+1}组" for i in range(num_groups)],
                "left": "10%",
                "right": "10%",
                "bottom": "2%",
                "symbol": "circle",
                "symbolSize": 10,
                "lineStyle": {
                    "color": "rgba(0, 255, 204, 0.5)",
                    "width": 2
                },
                "itemStyle": {
                    "color": "#00ffcc"
                },
                "checkpointStyle": {
                    "color": "#00ffcc",
                    "borderColor": "#ffffff",
                    "borderWidth": 2
                },
                "controlStyle": {
                    "showNextBtn": True,
                    "showPrevBtn": True,
                    "color": "#00ffcc",
                    "borderColor": "#00ffcc",
                    "itemSize": 20
                },
                "label": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "#00aaff"
                    },
                    "label": {
                        "color": "#00ffcc"
                    }
                }
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(10, 10, 26, 0.95)",
                "borderColor": "#00ff88",
                "borderWidth": 1,
                "textStyle": {"color": "#ffffff", "fontFamily": "Orbitron"},
                "formatter": JsCode("""function(params) {
                    var data = params[0];
                    return '<div style="font-family:Orbitron;padding:5px;">' +
                           '<div style="font-size:14px;font-weight:bold;color:#00ffcc;margin-bottom:5px;">节点 ' + data.name + '</div>' +
                           '<div style="font-size:13px;color:#c0c0c0;">准确率: <span style="color:#fff;font-weight:bold;">' + data.value + '%</span></div>' +
                           '</div>';
                }""")
            },
            "grid": {
                "left": "3%",
                "right": "4%",
                "bottom": "15%",
                "top": "20%",
                "containLabel": True
            },
            "xAxis": {
                "type": "category",
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 204, 0.3)", "width": 1}
                }
            },
            "yAxis": {
                "type": "value",
                "name": "准确率 (%)",
                "max": 110,
                "nameTextStyle": {
                    "color": "#00ffcc",
                    "fontFamily": "Orbitron",
                    "fontSize": 12
                },
                "axisLabel": {
                    "color": "#c0c0c0",
                    "fontFamily": "Orbitron"
                },
                "axisLine": {
                    "lineStyle": {"color": "rgba(0, 255, 204, 0.3)", "width": 1}
                },
                "splitLine": {
                    "lineStyle": {"color": "rgba(0, 255, 204, 0.1)", "type": "dashed"}
                }
            },
            "series": [{
                "type": "bar",
                "barWidth": "60%",
                "label": {
                    "show": True,
                    "position": "top",
                    "formatter": "{c}%",
                    "color": "#ffffff",
                    "fontSize": 11,
                    "fontFamily": "Orbitron"
                },
                "markLine": {
                    "silent": True,
                    "data": [{
                        "yAxis": round(avg_accuracy, 2),
                        "name": "平均值",
                        "lineStyle": {"color": "#00aaff", "type": "dashed", "width": 2},
                        "label": {
                            "formatter": "平均: {c}%",
                            "color": "#00aaff",
                            "fontSize": 11,
                            "fontFamily": "Orbitron"
                        }
                    }]
                },
                "animationDuration": 1000,
                "animationEasing": "elasticOut"
            }]
        },
        "options": timeline_options
    }
    
    st_echarts(accuracy_timeline_option, height="450px", key="ensemble_accuracy_timeline_chart")
    
    # 显示统计信息（科技感卡片样式）
    high_acc = (df_accuracy['accuracy_pct'] >= 80).sum()
    low_acc = (df_accuracy['accuracy_pct'] < 60).sum()
    
    col_acc1, col_acc2, col_acc3, col_acc4 = st.columns(4)
    with col_acc1:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">平均准确率</div>
            <div class="tech-metric-value" style="color:#00ff88">{avg_accuracy:.2f}<span class="tech-metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_acc2:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">高准确率节点数</div>
            <div class="tech-metric-value" style="color:#00aaff">{high_acc}<span class="tech-metric-unit">个(≥80%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_acc3:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">低准确率节点数</div>
            <div class="tech-metric-value" style="color:#ff6b6b">{low_acc}<span class="tech-metric-unit">个(<60%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col_acc4:
        st.markdown(f"""
        <div class="tech-metric-card">
            <div class="tech-metric-label">总节点数</div>
            <div class="tech-metric-value" style="color:#ffd93d">{total_nodes}<span class="tech-metric-unit">个</span></div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("未找到三模型集成准确率数据文件")

