import requests
import pandas as pd
from io import StringIO
import os

# 数据 URL
url = "https://media.githubusercontent.com/media/tsinghua-fib-lab/NetData/refs/heads/main/Performance_5G_Weekend.csv"

# 保存路径（建议放在 data/raw 下）
save_dir = r"E:\PythonProgram\FedGreen-C\data\raw"
os.makedirs(save_dir, exist_ok=True)
excel_path = os.path.join(save_dir, "Performance_5G_Weekend.xlsx")

print("正在下载数据...")
try:
    # 发送请求，设置超时 30 秒
    response = requests.get(url, timeout=30)
    response.raise_for_status()  # 如果状态码不是 200，抛出异常
    print("下载成功！")

    # 将 CSV 内容读入 pandas DataFrame
    df = pd.read_csv(StringIO(response.text))
    print(f"数据行数：{len(df)}，列数：{len(df.columns)}")

    # 保存为 Excel
    df.to_excel(excel_path, index=False)
    print(f"✅ 已保存至：{excel_path}")

    # 显示前 5 行（可选）
    print("\n前5行数据预览：")
    print(df.head())

except requests.exceptions.RequestException as e:
    print(f"❌ 网络请求失败：{e}")
except Exception as e:
    print(f"❌ 数据处理失败：{e}")