import re
import csv
import os

def parse_loss_log(log_path, output_csv, pattern, has_train_loss=True):
    # 尝试多种编码打开文件
    encodings = ['utf-8', 'gbk', 'latin-1']
    lines = None
    for enc in encodings:
        try:
            with open(log_path, 'r', encoding=enc) as f:
                lines = f.readlines()
                break
        except UnicodeDecodeError:
            continue
    if lines is None:
        print(f"无法解码文件 {log_path}，请检查文件编码。")
        return

    data = []
    for line in lines:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if len(groups) == 2:
                round_num = int(groups[0])
                loss_val = float(groups[1])
                if has_train_loss:
                    data.append([round_num, loss_val, None])
                else:
                    data.append([round_num, None, loss_val])
    if not data:
        print(f"警告：未从 {log_path} 中提取到任何损失数据，请检查日志格式。")
        return

    output_dir = os.path.dirname(output_csv)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["round", "train_loss", "val_loss"])
        writer.writerows(data)

    print(f"成功提取 {len(data)} 轮损失，保存至 {output_csv}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(base_dir, "data")

    # 2节点粒度融合
    log_2node = os.path.join(data_dir, "fusion_2node.log")
    out_2node = os.path.join(data_dir, "granularity_2node_loss.csv")
    if os.path.exists(log_2node):
        pattern_2node = r"Round\s+(\d+):\s+avg_train_loss\s*=\s*([\d\.]+)"
        parse_loss_log(log_2node, out_2node, pattern_2node, has_train_loss=True)
    else:
        print(f"未找到 {log_2node}")

    # 41节点粒度融合
    log_41node = os.path.join(data_dir, "fusion_41node.log")
    out_41node = os.path.join(data_dir, "granularity_41node_loss.csv")
    if os.path.exists(log_41node):
        pattern_41node = r"Round\s+(\d+):\s+avg_train_loss\s*=\s*([\d\.]+)"
        parse_loss_log(log_41node, out_41node, pattern_41node, has_train_loss=True)
    else:
        print(f"未找到 {log_41node}")

    # 41节点不加权
    log_unweighted = os.path.join(data_dir, "fed_optuna_20260326_102433.log")
    out_unweighted = os.path.join(data_dir, "unweighted_41node_loss.csv")
    if os.path.exists(log_unweighted):
        pattern_unweighted = r"Round\s+(\d+):\s+val_loss\s*=\s*([\d\.]+)"
        parse_loss_log(log_unweighted, out_unweighted, pattern_unweighted, has_train_loss=False)
    else:
        print(f"未找到 {log_unweighted}")