import pandas as pd
import os

# 使用相对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'data', 'experiments_summary.csv')
df = pd.read_csv(csv_path, on_bad_lines='skip')
print("列名:", df.columns.tolist())
print("\n前5行数据:")
print(df.head())
print("\n数据类型:")
print(df.dtypes)
