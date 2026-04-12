# 第一行：基站负载分布图 + 24小时趋势
chart_col, trend_col = st.columns([3, 2])

with chart_col:
    st_echarts(options=option, height="500px", key="base_station_timeline_chart")

with trend_col:
    st.markdown("##### 24小时趋势")
    
    hourly_avg_loads = []
    for hour in range(num_hours):
        loads = [d[2] for d in hourly_data.get(hour, []) if d[2] is not None and not (isinstance(d[2], float) and np.isnan(d[2]))]
        avg_load = np.mean(loads) if loads else 0
        hourly_avg_loads.append(round(avg_load, 2))
    
    trend_option = {
        "tooltip": {"trigger": "axis"},
        "grid": {"left": "8%", "right": "5%", "top": "10%", "bottom": "15%"},
        "xAxis": {
            "type": "category",
            "data": hour_labels,
            "axisLabel": {"color": "#00ff88", "fontSize": 8, "rotate": 45},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}}
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": "#00ff88", "fontSize": 8},
            "axisLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.3)"}},
            "splitLine": {"lineStyle": {"color": "rgba(0, 255, 136, 0.1)"}}
        },
        "series": [{
            "type": "line",
            "data": hourly_avg_loads,
            "smooth": True,
            "symbol": "circle",
            "symbolSize": 4,
            "lineStyle": {"width": 2, "color": "#00ff88"},
            "itemStyle": {"color": "#00ff88"},
            "areaStyle": {
                "color": {
                    "type": "linear", "x": 0, "y": 0, "x2": 0, "y2": 1,
                    "colorStops": [
                        {"offset": 0, "color": "rgba(0, 255, 136, 0.3)"},
                        {"offset": 1, "color": "rgba(0, 255, 136, 0.05)"}
                    ]
                }
            }
        }],
        "animation": True
    }
    
    st_echarts(options=trend_option, height="350px", key="hourly_trend_chart")

# 第二行：实时统计卡片
st.markdown("##### 实时统计")
current_hour = 12
current_data = hourly_data.get(current_hour, [])
loads = [d[2] for d in current_data] if current_data else [0]

# 安全计算统计值
avg_load = np.mean(loads) if loads else 0
max_load = max(loads) if loads else 0
min_load = min(loads) if loads else 0

# 使用4列布局显示统计卡片
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 170, 255, 0.2) 0%, rgba(0, 170, 255, 0.1) 100%);
                border: 1px solid rgba(0, 170, 255, 0.5);
                border-radius: 8px;
                padding: 15px 10px;
                text-align: center;
                cursor: pointer;"
         title="当前显示的时段">
        <div style="color: #00aaff; font-size: 12px; margin-bottom: 5px;">当前时段</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{current_hour:02d}:00</div>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.1) 100%);
                border: 1px solid rgba(255, 193, 7, 0.5);
                border-radius: 8px;
                padding: 15px 10px;
                text-align: center;
                cursor: pointer;"
         title="所有基站的平均负载">
        <div style="color: #FFC107; font-size: 12px; margin-bottom: 5px;">平均负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{avg_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(255, 99, 132, 0.2) 0%, rgba(255, 99, 132, 0.1) 100%);
                border: 1px solid rgba(255, 99, 132, 0.5);
                border-radius: 8px;
                padding: 15px 10px;
                text-align: center;
                cursor: pointer;"
         title="所有基站中的最高负载">
        <div style="color: #ff6384; font-size: 12px; margin-bottom: 5px;">最高负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{max_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
                border: 1px solid rgba(76, 175, 80, 0.5);
                border-radius: 8px;
                padding: 15px 10px;
                text-align: center;
                cursor: pointer;"
         title="所有基站中的最低负载">
        <div style="color: #4CAF50; font-size: 12px; margin-bottom: 5px;">最低负载</div>
        <div style="color: #ffffff; font-size: 24px; font-weight: bold;">{min_load:.1f}<span style="font-size: 14px; color: #c0c0c0;">%</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
