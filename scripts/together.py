import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# 文件路径
train_file = os.path.join(project_root, "data", "node_train_samples.csv")
quality_file = os.path.join(project_root, "data", "processed", "node_quality.csv")
output_file = os.path.join(project_root, "data", "node_metadata.csv")

# 读取
df_train = pd.read_csv(train_file)
df_quality = pd.read_csv(quality_file)

# 合并
merged = pd.merge(df_train, df_quality, on="node_id", how="inner")
merged.to_csv(output_file, index=False)

print(f"合并完成，新文件保存至：{output_file}")
print("原文件未被修改。")