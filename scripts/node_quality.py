import pandas as pd
import os

# 获取当前脚本所在目录：E:\PythonProgram\FedGreen-C\scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录：向上退一级到 E:\PythonProgram\FedGreen-C
project_root = os.path.dirname(script_dir)

# 数据文件相对路径
input_path = os.path.join(project_root, "data", "raw", "lianban", "node_epoch_losses.csv")
output_dir = os.path.join(project_root, "data", "processed")
output_path = os.path.join(output_dir, "node_quality.csv")

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 读取数据
df = pd.read_csv(input_path)

# 取每个节点的最后一条记录（第10轮）的验证损失
node_quality = df.groupby("node")["val_loss"].last().reset_index()
node_quality.columns = ["node_id", "val_loss"]

# 标记异常节点（根据已知异常节点列表）
abnormal_nodes = [8005, 8008, 8012]
node_quality["status"] = node_quality["node_id"].apply(
    lambda x: "abnormal" if x in abnormal_nodes else "normal"
)

# 保存为CSV
node_quality.to_csv(output_path, index=False)
print(f"节点质量文件已生成：{output_path}")