import re
import os

# 获取当前文件所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
page_path = os.path.join(base_dir, 'pages', 'page1_energy.py')

with open(page_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第一个 "规则解释" 的位置（第598行附近）
first_rule_idx = content.find('# 规则解释\nst.subheader("🔧 规则解释")', 500)
if first_rule_idx == -1:
    print("Could not find first rule explanation")
    exit(1)

# 保留从开始到第一个 "规则解释" 之前的内容
# 但保留第一个完整的区块（包括规则解释和节能效果统计）
# 第一个区块在 st_echarts(options=option_saving, height="400px", key="energy_saving_chart_1") 之后结束

# 找到第一个 energy_saving_chart_1 之后的位置
first_chart_end = content.find('key="energy_saving_chart_1")', first_rule_idx)
if first_chart_end == -1:
    print("Could not find first chart end")
    exit(1)

# 找到这行的结束位置
first_block_end = content.find('\n', first_chart_end) + 1

# 保留前 first_block_end 个字符
new_content = content[:first_block_end]

# 添加评估指标代码
eval_code = '''

# 评估指标
df_eval = df_hist.tail(days*2).copy()
df_eval["预测能耗 (kWh)"] = np.random.randint(8000, 15000, len(df_eval))

y_true = df_eval["实际能耗 (kWh)"].values
y_pred = df_eval["预测能耗 (kWh)"].values

rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mae = mean_absolute_error(y_true, y_pred)
smape = np.mean(np.abs(y_pred - y_true) / ((np.abs(y_true) + np.abs(y_pred)) / 2)) * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("RMSE", f"{rmse:.2f} kWh", help="均方根误差")
with col2:
    st.metric("MAE", f"{mae:.2f} kWh", help="平均绝对误差")
with col3:
    st.metric("sMAPE", f"{smape:.2f}%", help="对称平均绝对百分比误差")
'''

new_content += eval_code

with open(page_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('File updated successfully!')
print(f'New file length: {len(new_content)} characters')
