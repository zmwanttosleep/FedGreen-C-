import os

# 获取当前文件所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))
page_path = os.path.join(base_dir, 'pages', 'page1_energy.py')

with open(page_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 保留前631行（第一个完整区块）
new_lines = lines[:631]

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

new_lines.append(eval_code)

with open(page_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('File updated successfully!')
print(f'New file has {len(new_lines)} lines')
