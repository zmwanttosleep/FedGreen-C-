#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量读取巴塞罗那预处理数据中各节点的 train.pkl（DataFrame），获取训练样本数。
输出 CSV: data/node_train_samples.csv
"""

import pickle
import csv
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 注意：你的数据路径中有嵌套的 barcelona_ready_v1，根据实际结构调整
# 如果你的所有节点都位于 data/barcelona_ready_v1/barcelona_ready_v1/node_XXXX/ 下：
DATA_DIR = PROJECT_ROOT / "data" / "barcelona_ready_v1" / "barcelona_ready_v1"

# 如果实际只有一层，请改为：
# DATA_DIR = PROJECT_ROOT / "data" / "barcelona_ready_v1"

OUTPUT_CSV = PROJECT_ROOT / "data" / "node_train_samples.csv"

def main():
    if not DATA_DIR.exists():
        print(f"错误：目录不存在 {DATA_DIR}")
        print("请检查路径，可能是：")
        print("  - data/barcelona_ready_v1/barcelona_ready_v1")
        print("  - data/barcelona_ready_v1")
        return

    results = []
    # 遍历所有 node_* 子目录
    node_dirs = sorted(DATA_DIR.glob("node_*"))
    if not node_dirs:
        print(f"警告：在 {DATA_DIR} 下未找到 node_* 目录")
        return

    for node_dir in node_dirs:
        node_id = node_dir.name.split("_")[1]   # 提取数字，如 8001
        train_pkl = node_dir / "train.pkl"
        if not train_pkl.exists():
            print(f"警告：节点 {node_id} 缺少 train.pkl")
            continue
        try:
            with open(train_pkl, 'rb') as f:
                df = pickle.load(f)
            # 确保是 DataFrame
            if hasattr(df, 'shape'):
                num_samples = df.shape[0]
            else:
                num_samples = len(df)
            results.append({
                "node_id": node_id,
                "train_samples": num_samples
            })
            print(f"节点 {node_id}: {num_samples} 个训练样本")
        except Exception as e:
            print(f"读取节点 {node_id} 失败: {e}")

    if not results:
        print("未获取到任何样本数")
        return

    # 保存 CSV
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["node_id", "train_samples"])
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ 结果已保存至 {OUTPUT_CSV}")

if __name__ == "__main__":
    main()