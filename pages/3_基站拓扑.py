import streamlit as st
from streamlit_echarts import st_echarts, JsCode  # type: ignore
import pandas as pd
import numpy as np
import base64
from pathlib import Path
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="基站负载分布",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 渲染共享侧边栏
render_sidebar()

# 在侧边栏添加日期选择器和基站选择器
with st.sidebar:
    st.markdown("<hr style='border-color: rgba(0, 255, 136, 0.3); margin: 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color: #00ff88; font-family: Orbitron, sans-serif; font-size: 14px; margin-bottom: 10px;'>📅 数据日期</div>", unsafe_allow_html=True)
    
    # 日期选择器 - 使用数据中可用的日期范围 (2024-09-27 到 2024-10-01)
    available_dates = [datetime(2024, 9, 27), datetime(2024, 9, 28), datetime(2024, 9, 29), 
                       datetime(2024, 9, 30), datetime(2024, 10, 1)]
    selected_date = st.selectbox(
        "选择日期",
        options=available_dates,
        format_func=lambda x: x.strftime("%Y-%m-%d"),
        index=0,
        key="topo_date_selector"
    )
    
    # 保存到session_state
    if 'topo_selected_date' not in st.session_state:
        st.session_state.topo_selected_date = selected_date
    else:
        st.session_state.topo_selected_date = selected_date
    
    st.markdown(f"<div style='color: #c0c0c0; font-size: 12px; margin-top: 5px;'>当前选择: {selected_date.strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
    
    # 基站选择器
    st.markdown("<hr style='border-color: rgba(0, 255, 136, 0.3); margin: 15px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color: #00ff88; font-family: Orbitron, sans-serif; font-size: 14px; margin-bottom: 10px;'>📡 基站选择</div>", unsafe_allow_html=True)
    
    # 获取所有可用的基站ID
    all_node_ids = [8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010, 
                    8011, 8012, 8013, 8014, 8015, 8016, 8017, 8018, 8019, 8020,
                    8021, 8022, 8023, 8024, 8025, 8026, 8027, 8028, 8029, 8030,
                    8031, 8032, 8033, 8034, 8035, 8036, 8037, 8038, 8039, 8040, 8041, 8042]
    
    # 基站选择下拉框
    selected_node = st.selectbox(
        "选择基站",
        options=["全部基站"] + [f"基站 {node_id}" for node_id in all_node_ids],
        index=0,
        key="topo_node_selector"
    )
    
    # 保存到session_state
    if 'topo_selected_node' not in st.session_state:
        st.session_state.topo_selected_node = selected_node
    else:
        st.session_state.topo_selected_node = selected_node
    
    st.markdown(f"<div style='color: #c0c0c0; font-size: 12px; margin-top: 5px;'>当前选择: {selected_node}</div>", unsafe_allow_html=True)

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
    
    h1 {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #00ff88, #00aaff, #00ff88);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: textShine 3s linear infinite;
        text-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
        font-size: 1.5rem !important;
        margin-bottom: 0 !important;
    }
    
    @keyframes textShine {
        to { background-position: 200% center; }
    }
    
    h2, h3, h4 {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88 !important;
        text-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
        font-size: 1rem !important;
        margin: 0 !important;
    }
    
    .stCaption, .stMarkdown, p, span {
        color: #c0c0c0 !important;
    }
    
    .stMetric {
        background: linear-gradient(135deg, rgba(15, 52, 96, 0.8) 0%, rgba(26, 26, 46, 0.9) 100%);
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 10px;
        padding: 8px;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.15);
    }
    
    .stMetric label {
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.7rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem !important;
    }
    
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    hr {
        border-color: rgba(0, 255, 136, 0.3) !important;
        margin: 5px 0 !important;
    }
    
    section[data-testid="stVerticalBlock"] > div {
        gap: 0.3rem !important;
    }
    
    /* ========== 侧边栏科技风样式 ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 26, 0.98) 0%, rgba(15, 52, 96, 0.95) 100%) !important;
        border-right: 2px solid rgba(0, 255, 136, 0.3);
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.1);
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0.5rem;
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

st.title("基站负载分布")

np.random.seed(42)

num_hours = 24

# 从真实数据文件读取42个节点和负载数据
def load_real_nodes_and_loads(selected_date=None):
    """从多个CSV文件加载真实节点数据和负载数据
    
    Args:
        selected_date: 选择的日期，如果为None则使用默认数据
    """
    import os
    
    # 加载节点质量数据
    node_quality_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "node_quality.csv")
    node_status = {}
    if os.path.exists(node_quality_path):
        df_quality = pd.read_csv(node_quality_path)
        for _, row in df_quality.iterrows():
            node_id = int(row["node_id"])
            node_status[node_id] = "abnormal" if row["val_loss"] >= 0.08 else "normal"
    
    # 加载真实地理坐标数据
    coords_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "barcelona_coords.csv")
    nodes = []
    if os.path.exists(coords_path):
        df_coords = pd.read_csv(coords_path)
        for _, row in df_coords.iterrows():
            try:
                postal_code = str(int(float(row["postal_code"]))).zfill(5)
                node_id = int(postal_code[1:])
                longitude = float(row["longitude"])
                latitude = float(row["latitude"])
                if np.isnan(longitude) or np.isnan(latitude):
                    continue
                nodes.append({
                    "node_id": node_id,
                    "x": longitude,
                    "y": latitude,
                    "status": node_status.get(node_id, "normal"),
                    "postal_code": postal_code
                })
            except (ValueError, TypeError, KeyError):
                continue
    
    # 加载真实负载数据
    loads_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "decision_results_7day_all_phase2.csv")
    hourly_loads = {}  # {hour: {node_id: load}}
    if os.path.exists(loads_path):
        df_loads = pd.read_csv(loads_path)
        
        # 如果有选择日期，则过滤对应日期的数据
        if selected_date is not None:
            # 将选择的日期转换为字符串格式
            date_str = selected_date.strftime("%Y-%m-%d")
            # 检查数据文件中是否有该日期
            available_dates = df_loads["date"].unique()
            if date_str in available_dates:
                df_loads = df_loads[df_loads["date"] == date_str]
            else:
                # 如果选择的日期不存在，使用默认日期（2024-09-27）
                df_loads = df_loads[df_loads["date"] == "2024-09-27"]
        else:
            # 默认使用2024-09-27的数据
            df_loads = df_loads[df_loads["date"] == "2024-09-27"]
        
        # 按小时和节点分组，计算平均负载
        for hour in range(4):  # hour_code: 0-3
            hourly_loads[hour] = {}
            hour_data = df_loads[df_loads["hour_code"] == hour]
            for node_id in hour_data["node_id"].unique():
                node_hour_data = hour_data[hour_data["node_id"] == node_id]
                if not node_hour_data.empty:
                    # 使用 real_kw 作为负载，转换为百分比 (假设最大负载为100000kW)
                    avg_load_kw = node_hour_data["real_kw"].mean()
                    load_pct = min(100, max(0, avg_load_kw / 1000))  # 转换为百分比
                    hourly_loads[hour][int(node_id)] = round(load_pct, 1)
    
    return nodes, hourly_loads

# 从session_state获取选择的日期，如果没有则使用默认日期
selected_date = st.session_state.get('topo_selected_date', datetime(2024, 9, 27).date() if hasattr(datetime(2024, 9, 27), 'date') else datetime(2024, 9, 27))

# 从session_state获取选择的基站
selected_node = st.session_state.get('topo_selected_node', '全部基站')
# 解析选择的基站ID
filter_node_id = None
if selected_node != '全部基站':
    try:
        filter_node_id = int(selected_node.replace('基站 ', ''))
    except:
        filter_node_id = None

# 加载数据（根据选择的日期）
base_coords, real_hourly_loads = load_real_nodes_and_loads(selected_date)

# 如果选择了特定基站，则过滤base_coords
if filter_node_id is not None:
    base_coords = [node for node in base_coords if node['node_id'] == filter_node_id]

num_nodes = len(base_coords)

# 生成小时数据
hourly_data = {}
for hour in range(num_hours):
    data = []
    # 将24小时映射到4个时段 (0-3)
    hour_code = hour // 6  # 0-5->0, 6-11->1, 12-17->2, 18-23->3
    for node in base_coords:
        x = node["x"]
        y = node["y"]
        if x is None or y is None or (isinstance(x, float) and np.isnan(x)) or (isinstance(y, float) and np.isnan(y)):
            continue
        
        # 使用真实负载数据，如果没有则使用模拟数据
        node_id = node['node_id']
        if hour_code in real_hourly_loads and node_id in real_hourly_loads[hour_code]:
            load = real_hourly_loads[hour_code][node_id]
        else:
            # 模拟数据作为后备
            base_load = 30 + 40 * np.sin(hour * np.pi / 12)
            noise = np.random.uniform(-10, 10)
            abnormal_boost = 15 if node.get("status") == "abnormal" else 0
            load = max(10, min(100, base_load + noise + abnormal_boost + np.random.uniform(-5, 15)))
        
        data.append([float(x), float(y), round(float(load), 1), node_id, node.get('postal_code', f"0{node_id}")])
    hourly_data[hour] = data

timeline_data = []
hour_labels = [f"{h:02d}:00" for h in range(num_hours)]

for hour in range(num_hours):
    hour_data = hourly_data.get(hour, [])
    timeline_data.append({
        "title": {"text": f"基站负载分布 - {hour_labels[hour]}"},
        "series": [
            {},  # 地图轮廓线（在baseOption中定义，保持不变）
            {
                "data": [[d[0], d[1], d[2], d[3], d[4]] for d in hour_data] if hour_data else [],
                "symbolSize": JsCode("""function(data) {
                    var load = data[2] || 0;
                    return 5 + (load / 100) * 25;
                }"""),
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                    "opacity": 0.8
                }
            }
        ]
    })

# 巴塞罗那城市轮廓线坐标（基于真实地理边界）
# 根据邮编坐标数据，巴塞罗那大致范围：经度 2.12-2.21，纬度 41.35-41.43
barcelona_outline = [
    # 西北角 (08017, 08035)
    [2.12, 41.43], [2.13, 41.432], [2.14, 41.433],
    # 北边界 (08035, 08016, 08041)
    [2.15, 41.433], [2.16, 41.432], [2.17, 41.428], [2.18, 41.425],
    [2.19, 41.422], [2.20, 41.42], [2.21, 41.425],
    # 东北角 (08019)
    [2.215, 41.428],
    # 东边界 (08019, 08020, 08018)
    [2.21, 41.42], [2.205, 41.415], [2.20, 41.41],
    # 东南角 (08019 区域)
    [2.205, 41.405],
    # 南边界 (08034, 08033, 08032, 08031)
    [2.195, 41.36], [2.185, 41.358], [2.175, 41.356], [2.165, 41.358],
    [2.155, 41.36], [2.145, 41.365], [2.14, 41.37],
    # 西南角 (08038, 08039)
    [2.13, 41.375], [2.125, 41.378],
    # 西边界 (08039, 08017)
    [2.12, 41.385], [2.118, 41.395], [2.119, 41.405],
    # 回到西北角，闭合轮廓
    [2.12, 41.415], [2.12, 41.425], [2.12, 41.43]
]

option = {
    "baseOption": {
        "backgroundColor": "transparent",
        "timeline": {
            "axisType": "category",
            "autoPlay": True,
            "playInterval": 1500,
            "loop": True,
            "rewind": True,
            "controlPosition": "left",
            "data": hour_labels,
            "left": "10%",
            "right": "10%",
            "bottom": "2%",
            "label": {"color": "#00ff88", "fontSize": 12},
            "lineStyle": {"color": "rgba(0, 255, 136, 0.5)"},
            "itemStyle": {"color": "#00ff88", "borderColor": "#00ff88"},
            "checkpointStyle": {"color": "#00aaff", "borderColor": "#00ff88", "borderWidth": 2},
            "controlStyle": {"color": "#00ff88", "borderColor": "#00ff88"},
            "emphasis": {"itemStyle": {"color": "#00aaff"}, "controlStyle": {"color": "#00aaff"}}
        },
        "title": {
            "text": "基站负载分布 - 00:00",
            "left": "center",
            "textStyle": {"color": "#00ff88", "fontSize": 18, "fontFamily": "Orbitron"}
        },
        "tooltip": {
            "trigger": "item",
            "formatter": JsCode("function(params) { return '邮政编码: ' + params.data[4] + '<br/>节点: ' + params.data[3] + '<br/>负载: ' + params.data[2] + '%'; }"),
            "backgroundColor": "rgba(15, 52, 96, 0.9)",
            "borderColor": "#00ff88",
            "textStyle": {"color": "#fff"}
        },
        "visualMap": {
            "min": 0, "max": 100, "calculable": True,
            "inRange": {"color": ["#00ff00", "#ffff00", "#ff0000"]},
            "textStyle": {"color": "#c0c0c0"},
            "left": "left", "bottom": "12%"
        },
        "grid": {"left": "10%", "right": "8%", "top": "15%", "bottom": "18%"},
        "xAxis": {
            "type": "value", "name": "经度",
            "nameTextStyle": {"color": "#00ff88", "fontSize": 14},
            "axisLabel": {"color": "#c0c0c0", "fontSize": 12},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}},
            "min": 2.10, "max": 2.23
        },
        "yAxis": {
            "type": "value", "name": "纬度",
            "nameTextStyle": {"color": "#00ff88", "fontSize": 14},
            "axisLabel": {"color": "#c0c0c0", "fontSize": 12},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}},
            "min": 41.34, "max": 41.44
        },
        "series": [
            # 巴塞罗那城市轮廓线
            {
                "type": "line",
                "data": barcelona_outline,
                "lineStyle": {
                    "color": "rgba(0, 255, 136, 0.4)",
                    "width": 2,
                    "type": "solid"
                },
                "symbol": "none",
                "silent": True,
                "z": 1
            },
            # 基站数据 - 气泡大小随负载变化
            {
                "type": "scatter",
                "data": [[d[0], d[1], d[2], d[3], d[4]] for d in hourly_data.get(0, [])] if hourly_data.get(0, []) else [],
                "symbolSize": JsCode("""function(data) {
                    // 负载值越大，气泡越大 (5-30范围)
                    var load = data[2] || 0;
                    return 5 + (load / 100) * 25;
                }"""),
                "label": {"show": True, "formatter": JsCode("function(params) { return params.data[4]; }"), "position": "right", "color": "#c0c0c0", "fontSize": 10},
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowColor": "rgba(0, 0, 0, 0.5)",
                    "opacity": 0.8
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 20,
                        "shadowColor": "rgba(0, 0, 0, 0.8)",
                        "opacity": 1
                    },
                    "scale": 1.2
                },
                "animation": True,
                "animationDurationUpdate": 500,
                "animationEasingUpdate": "cubicInOut",
                "z": 10
            }
        ]
    },
    "options": timeline_data
}

# 初始化当前时段
if 'topo_current_hour' not in st.session_state:
    st.session_state.topo_current_hour = 12

# 自动轮播：每1.5秒更新一次时段（与ECharts时间轴同步）
# 使用占位符来强制刷新
auto_play = st.checkbox("自动轮播", value=True, key="auto_play_checkbox")
if auto_play:
    # 自动递增时段
    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0
    
    import time
    current_time = time.time()
    if current_time - st.session_state.last_update > 1.5:  # 1.5秒间隔
        st.session_state.topo_current_hour = (st.session_state.topo_current_hour + 1) % 24
        st.session_state.last_update = current_time
        st.rerun()

# 使用session_state中的当前时段
current_hour = st.session_state.topo_current_hour

# 第一行：基站负载分布图
st_echarts(options=option, height="500px", key="base_station_timeline_chart")

# 根据当前时段获取数据
current_data = hourly_data.get(current_hour, [])
loads = [d[2] for d in current_data] if current_data else [0]

# 安全计算统计值
avg_load = np.mean(loads) if loads else 0
max_load = max(loads) if loads else 0
min_load = min(loads) if loads else 0

# 第二行：实时统计卡片（纵向）+ 3D地球视图
stats_col, globe_col = st.columns([1, 2])

with stats_col:

    # 平均负载
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%);
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                margin-bottom: 10px;
                cursor: pointer;"
         title="所有基站的平均负载">
        <div style="color: #FFC107; font-size: 16px; font-weight: bold; margin-bottom: 3px;">平均负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{avg_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 最高负载
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 99, 132, 0.2) 0%, rgba(255, 99, 132, 0.1) 100%);
                border: 1px solid rgba(255, 99, 132, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                margin-bottom: 10px;
                cursor: pointer;"
         title="所有基站中的最高负载">
        <div style="color: #ff6384; font-size: 16px; font-weight: bold; margin-bottom: 3px;">最高负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{max_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 最低负载
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
                border: 1px solid rgba(76, 175, 80, 0.5);
                border-radius: 8px;
                padding: 12px 8px;
                text-align: center;
                cursor: pointer;"
         title="所有基站中的最低负载">
        <div style="color: #4CAF50; font-size: 16px; font-weight: bold; margin-bottom: 3px;">最低负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{min_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

with globe_col:
    st.markdown("##### 3D 地球视图")

    # 读取本地图片并转换为base64
    import base64
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "image", "2353e6521ddb9f4897eca7689dfb0cca.jpeg")
    try:
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        earth_texture_url = f"data:image/jpeg;base64,{img_base64}"
    except Exception as e:
        st.warning(f"无法加载本地图片，使用默认地球贴图: {e}")
        earth_texture_url = "https://echarts.apache.org/examples/data-gl/asset/earth.jpg"
    
    # 中国主要城市坐标（经度, 纬度, 大小, 城市名称）- 只保留杭州和南昌
    china_cities = [
        {"name": "杭州", "value": [120.1551, 30.2741, 0]},  # 高度0贴在地球表面
        {"name": "南昌", "value": [115.8579, 28.6820, 0]},  # 高度0贴在地球表面
    ]
    
    # 巴塞罗那坐标（经度, 纬度, 大小, 城市名称）- 高度0贴在地球表面
    barcelona_coords = [
        {"name": "巴塞罗那", "value": [2.1734, 41.3851, 0]},  # 高度0贴在地球表面
    ]
    
    # 中国版图轮廓线坐标（经度, 纬度, 高度0）- 橙色，高度0表示贴在地球表面
    china_outline_coords = [
        # 从东北开始顺时针绘制
        [135.0, 53.5, 0],   # 黑龙江最北
        [130.0, 48.0, 0],   # 黑龙江
        [125.0, 44.0, 0],   # 吉林
        [123.0, 42.0, 0],   # 辽宁
        [120.0, 40.0, 0],   # 河北东部
        [117.0, 39.0, 0],   # 天津
        [116.4, 40.0, 0],   # 北京
        [114.5, 38.0, 0],   # 河北西部
        [112.5, 37.0, 0],   # 山西
        [111.0, 35.0, 0],   # 河南
        [108.9, 34.3, 0],   # 西安
        [103.8, 36.1, 0],   # 兰州
        [101.8, 36.6, 0],   # 西宁
        [87.6, 43.8, 0],    # 乌鲁木齐
        [82.0, 45.0, 0],    # 新疆西部
        [80.0, 40.0, 0],    # 新疆南部
        [78.0, 35.0, 0],    # 西藏西部
        [88.0, 28.0, 0],    # 西藏南部
        [91.0, 27.0, 0],    # 藏南
        [95.0, 25.0, 0],    # 云南西部
        [100.2, 25.0, 0],   # 云南
        [102.7, 25.0, 0],   # 昆明
        [108.3, 22.8, 0],   # 广西南宁
        [110.3, 20.0, 0],   # 海南海口
        [111.0, 18.0, 0],   # 海南南部
        [112.0, 20.0, 0],   # 海南东部
        [113.3, 23.1, 0],   # 广州
        [114.1, 22.5, 0],   # 深圳/香港
        [117.3, 39.4, 0],   # 回到东北附近闭合
        [120.0, 30.0, 0],   # 上海
        [122.0, 31.0, 0],   # 东海
        [125.0, 35.0, 0],   # 黄海
        [130.0, 42.0, 0],   # 朝鲜半岛附近
        [135.0, 53.5, 0],   # 闭合到起点
    ]
    
    # 巴塞罗那城市轮廓线坐标（经度, 纬度, 高度0）- 绿色，高度0表示贴在地球表面
    barcelona_outline_coords = [
        # 巴塞罗那市区大致轮廓（从北开始顺时针）
        [2.15, 41.42, 0],   # 北部
        [2.18, 41.43, 0],   # 东北
        [2.22, 41.42, 0],   # 东
        [2.25, 41.40, 0],   # 东南海边
        [2.23, 41.38, 0],   # 南海边
        [2.20, 41.36, 0],   # 西南海边
        [2.16, 41.35, 0],   # 西南
        [2.12, 41.36, 0],   # 西
        [2.10, 41.38, 0],   # 西北
        [2.11, 41.40, 0],   # 西北
        [2.13, 41.42, 0],   # 回到北部
        [2.15, 41.42, 0],   # 闭合
    ]
    
    globe_option = {
        "backgroundColor": "transparent",
        "globe": {
            "baseTexture": earth_texture_url,
            "shading": "realistic",
            "realisticMaterial": {
                "roughness": 0.9,
                "metalness": 0.1
            },
            "environment": "none",
            "light": {
                "ambient": {
                    "intensity": 0.4
                },
                "main": {
                    "intensity": 1.2,
                    "shadow": False
                },
                "postEffect": {
                    "enable": True,
                    "bloom": {
                        "enable": True,
                        "intensity": 0.3
                    }
                }
            },
            "atmosphere": {
                "show": True,
                "glowPower": 8,
                "color": "#00aaff"
            },
            "viewControl": {
                "autoRotate": True,
                "autoRotateSpeed": 2,
                "distance": 180,
                "minDistance": 100,
                "maxDistance": 400,
                "panSensitivity": 0.6,
                "rotateSensitivity": 1.0,
                "zoomSensitivity": 1.0,
                "mouseControl": True,
                "touchControl": True
            }
        },
        "series": [
            {
                "name": "中国城市",
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "data": china_cities,
                "symbol": "diamond",
                "symbolSize": 15,
                "itemStyle": {
                    "color": "#ff6600",
                    "opacity": 1.0,
                    "borderColor": "#ffaa00",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}",
                    "textStyle": {
                        "color": "#ffaa00",
                        "fontSize": 14,
                        "fontWeight": "bold",
                        "backgroundColor": "rgba(0,0,0,0.7)",
                        "padding": [6, 10],
                        "borderRadius": 4,
                        "borderColor": "#ff6600",
                        "borderWidth": 1
                    }
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "#ffaa00",
                        "opacity": 1,
                        "borderColor": "#fff",
                        "borderWidth": 3
                    }
                }
            },
            {
                "name": "巴塞罗那",
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "data": barcelona_coords,
                "symbol": "diamond",
                "symbolSize": 25,
                "itemStyle": {
                    "color": "#00ff88",
                    "opacity": 1.0,
                    "borderColor": "#00ffcc",
                    "borderWidth": 3
                },
                "label": {
                    "show": True,
                    "formatter": "{b}",
                    "textStyle": {
                        "color": "#00ff88",
                        "fontSize": 16,
                        "fontWeight": "bold",
                        "backgroundColor": "rgba(0,0,0,0.7)",
                        "padding": [6, 10],
                        "borderRadius": 4,
                        "borderColor": "#00ff88",
                        "borderWidth": 1
                    }
                },
                "emphasis": {
                    "itemStyle": {
                        "color": "#00ffcc",
                        "opacity": 1,
                        "borderColor": "#fff",
                        "borderWidth": 4
                    }
                }
            },
            {
                "name": "脉冲光环",
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "data": [
                    {"name": "杭州脉冲", "value": [120.1551, 30.2741, 0]}
                ],
                "symbol": "circle",
                "symbolSize": 40,
                "itemStyle": {
                    "color": "transparent",
                    "borderColor": "#ff6600",
                    "borderWidth": 2,
                    "opacity": 0.6
                },
                "zlevel": 5
            },
            {
                "name": "脉冲光环-南昌",
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "data": [
                    {"name": "南昌脉冲", "value": [115.8579, 28.6820, 0]}
                ],
                "symbol": "circle",
                "symbolSize": 35,
                "itemStyle": {
                    "color": "transparent",
                    "borderColor": "#ff6600",
                    "borderWidth": 2,
                    "opacity": 0.6
                },
                "zlevel": 5
            },
            {
                "name": "脉冲光环-巴塞罗那",
                "type": "scatter3D",
                "coordinateSystem": "globe",
                "data": [
                    {"name": "巴塞罗那脉冲", "value": [2.1734, 41.3851, 0]}
                ],
                "symbol": "circle",
                "symbolSize": 50,
                "itemStyle": {
                    "color": "transparent",
                    "borderColor": "#00ff88",
                    "borderWidth": 3,
                    "opacity": 0.8
                },
                "zlevel": 5
            },
            {
                "name": "中国连线",
                "type": "lines3D",
                "coordinateSystem": "globe",
                "data": [
                    # 杭州和南昌之间的连线
                    {"coords": [[120.1551, 30.2741], [115.8579, 28.6820]]},  # 杭州-南昌
                ],
                "lineStyle": {
                    "color": "#ff8800",
                    "width": 4,
                    "opacity": 0.6
                },
                "effect": {
                    "show": True,
                    "period": 3,
                    "trailWidth": 6,
                    "trailLength": 0.5,
                    "trailOpacity": 1,
                    "trailColor": "#ffaa00"
                }
            },
            {
                "name": "巴塞罗那-中国连线",
                "type": "lines3D",
                "coordinateSystem": "globe",
                "data": [
                    {"coords": [[2.1734, 41.3851], [120.1551, 30.2741]]},  # 巴塞罗那-杭州
                    {"coords": [[2.1734, 41.3851], [115.8579, 28.6820]]},  # 巴塞罗那-南昌
                ],
                "lineStyle": {
                    "color": "#00ff88",
                    "width": 4,
                    "opacity": 0.6
                },
                "effect": {
                    "show": True,
                    "period": 4,
                    "trailWidth": 6,
                    "trailLength": 0.5,
                    "trailOpacity": 1,
                    "trailColor": "#00ffaa"
                }
            },
            {
                "name": "数据粒子",
                "type": "lines3D",
                "coordinateSystem": "globe",
                "data": [
                    {"coords": [[2.1734, 41.3851], [120.1551, 30.2741]]},
                    {"coords": [[2.1734, 41.3851], [115.8579, 28.6820]]},
                    {"coords": [[120.1551, 30.2741], [115.8579, 28.6820]]},
                ],
                "lineStyle": {
                    "color": "transparent",
                    "width": 0
                },
                "effect": {
                    "show": True,
                    "period": 2,
                    "constantSpeed": 80,
                    "trailWidth": 8,
                    "trailLength": 0.1,
                    "trailOpacity": 1,
                    "trailColor": "#ffffff"
                },
                "zlevel": 20
            },
            {
                "name": "中国版图轮廓",
                "type": "lines3D",
                "coordinateSystem": "globe",
                "data": china_outline_coords,
                "lineStyle": {
                    "color": "#ff8800",
                    "width": 6,
                    "opacity": 1.0
                },
                "itemStyle": {
                    "color": "#ff8800"
                },
                "blendMode": "lighter",
                "silent": True,
                "zlevel": 10
            },
            {
                "name": "巴塞罗那城市轮廓",
                "type": "lines3D",
                "coordinateSystem": "globe",
                "data": barcelona_outline_coords,
                "lineStyle": {
                    "color": "#00ff88",
                    "width": 8,
                    "opacity": 1.0
                },
                "itemStyle": {
                    "color": "#00ff88"
                },
                "blendMode": "lighter",
                "silent": True,
                "zlevel": 10
            }
        ]
    }
    
    st_echarts(options=globe_option, height="500px", key="globe_chart")

# 第三行：24小时趋势图
trend_container = st.container()

with trend_container:
    st.markdown("##### 24小时趋势")
    
    hourly_avg_loads = []
    for hour in range(num_hours):
        loads = [d[2] for d in hourly_data.get(hour, []) if d[2] is not None and not (isinstance(d[2], float) and np.isnan(d[2]))]
        avg_load = np.mean(loads) if loads else 0
        hourly_avg_loads.append(round(avg_load, 2))
    
    # 计算统计数据用于显示
    max_load_value = max(hourly_avg_loads) if hourly_avg_loads else 0
    min_load_value = min(hourly_avg_loads) if hourly_avg_loads else 0
    avg_load_value = np.mean(hourly_avg_loads) if hourly_avg_loads else 0
    
    trend_option = {
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(10, 10, 26, 0.9)",
            "borderColor": "rgba(0, 255, 136, 0.5)",
            "borderWidth": 1,
            "textStyle": {"color": "#00ff88", "fontSize": 13},
            "formatter": JsCode("""function(params) {
                var data = params[0];
                return '<div style="font-weight:bold;margin-bottom:5px;">' + data.name + '</div>' +
                       '<div style="color:#00ff88;">平均负载: <span style="font-size:16px;font-weight:bold;">' + data.value + '%</span></div>';
            }"""),
            "axisPointer": {
                "type": "cross",
                "crossStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 1, "type": "dashed"}
            }
        },
        "grid": {"left": "10%", "right": "5%", "top": "15%", "bottom": "15%"},
        "xAxis": {
            "type": "category",
            "data": hour_labels,
            "axisLabel": {"color": "#00ff88", "fontSize": 11, "rotate": 30},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
            "axisTick": {"alignWithLabel": True, "lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}}
        },
        "yAxis": {
            "type": "value",
            "name": "负载 (%)",
            "nameTextStyle": {"color": "#00ff88", "fontSize": 12},
            "axisLabel": {"color": "#00ff88", "fontSize": 11, "formatter": "{value}%"},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.5)", "width": 2}},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)", "type": "dashed"}},
            "min": 0,
            "max": 100
        },
        "series": [{
            "name": "平均负载",
            "type": "line",
            "data": hourly_avg_loads,
            "smooth": True,
            "symbol": "circle",
            "symbolSize": 8,
            "lineStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 1, "y2": 0,
                    "colorStops": [
                        {"offset": 0, "color": "#00ff88"},
                        {"offset": 0.5, "color": "#00aaff"},
                        {"offset": 1, "color": "#00ff88"}
                    ]
                },
                "width": 3,
                "shadowBlur": 10,
                "shadowColor": "rgba(0, 255, 136, 0.5)"
            },
            "itemStyle": {
                "color": "#00ff88",
                "borderColor": "#fff",
                "borderWidth": 2
            },
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.3)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0.05)"}
                    ]
                }
            },
            "markPoint": {
                "data": [
                    {"type": "max", "name": "最高", "itemStyle": {"color": "#ff6b6b"}},
                    {"type": "min", "name": "最低", "itemStyle": {"color": "#4ecdc4"}}
                ],
                "label": {"color": "#ffffff", "fontSize": 10, "fontWeight": "bold"},
                "symbolSize": 40
            },
            "markLine": {
                "data": [{"type": "average", "name": "平均"}],
                "lineStyle": {"color": "rgba(255, 193, 7, 0.8)", "type": "dashed", "width": 2},
                "label": {"color": "#FFC107", "fontSize": 10, "formatter": "平均: {c}%"}
            }
        }],
        "animation": True,
        "animationDuration": 2000,
        "animationEasing": "cubicOut",
        "dataZoom": [{
            "type": "inside",
            "start": 0,
            "end": 100
        }]
    }
    
    st_echarts(options=trend_option, height="500px", key="hourly_trend_chart")