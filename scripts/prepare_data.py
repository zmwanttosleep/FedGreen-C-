#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/prepare_data.py
从 daily_logs/*.md 中提取实验汇总表，输出 data/experiments_summary.csv
"""

import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
LOGS_DIR = PROJECT_ROOT / "daily_logs"
OUTPUT_CSV = PROJECT_ROOT / "data" / "experiments_summary.csv"


def clean_text(text: str) -> str:
    """去除Markdown标记"""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text.strip()


def parse_smape(value: str) -> Optional[float]:
    if not value:
        return None
    m = re.search(r'(\d+(?:\.\d+)?)%?', str(value))
    if m:
        return float(m.group(1))
    return None


def parse_nodes_from_name(name: str) -> Tuple[Optional[int], Optional[str]]:
    name_clean = clean_text(name)
    node_count = None
    nodes_str = None

    # 匹配 "2节点"、"41节点" 等
    m = re.search(r'(\d+)节点', name_clean)
    if m:
        node_count = int(m.group(1))

    # 匹配节点列表：8001-8024 或 8001,8002
    m2 = re.search(r'\b(\d{4,}(?:[-,]\d{4,})+)\b', name_clean)
    if m2:
        maybe_nodes = m2.group(1)
        if ',' in maybe_nodes:
            nodes_str = maybe_nodes
            node_count = len(maybe_nodes.split(','))
        elif '-' in maybe_nodes:
            parts = maybe_nodes.split('-')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                nodes_str = maybe_nodes
                start, end = int(parts[0]), int(parts[1])
                node_count = end - start + 1
    return node_count, nodes_str


def parse_window(name: str) -> str:
    name_low = name.lower()
    if '1天' in name_low or '1day' in name_low or '4步' in name_low:
        return '1day'
    if '7天' in name_low or '7day' in name_low or '28步' in name_low:
        return '7day'
    if '6小时' in name_low:
        return '6hour'
    return ''


def parse_mu(name: str, context: str = '') -> Optional[float]:
    for text in [name, context]:
        m = re.search(r'[μµ]?\s*=\s*([\d\.]+)', text)
        if m:
            return float(m.group(1))
        m = re.search(r'mu[\s]*([\d\.]+)', text, re.I)
        if m:
            return float(m.group(1))
    return None


def parse_features(name: str, context: str = '') -> str:
    combined = (name + ' ' + context).lower()
    if 'v1' in combined:
        return 'v1'
    if 'v2.5' in combined:
        return 'v2.5'
    if '清华' in combined:
        return 'v1+清华聚类'
    if '时序' in combined:
        return '时序特征'
    return ''


def extract_experiments_from_text(content: str) -> List[Dict]:
    experiments = []
    lines = content.splitlines()
    for i, line in enumerate(lines):
        # 查找 sMAPE 相关行
        m = re.search(r'(?:sMAPE|SMAPE)[\s:=]*(\d+(?:\.\d+)?%)', line, re.I)
        if not m:
            m = re.search(r'(\d+(?:\.\d+)?%)', line)
            if not m or not ('smape' in line.lower() or '误差' in line or '测试准确率' in line):
                continue
        smape_val = parse_smape(m.group(1))
        if smape_val is None:
            continue

        # 向前查找实验名称
        name = ''
        for j in range(max(0, i - 5), i):
            candidate = lines[j].strip()
            if candidate and not re.match(r'^[\s\|:\-]+$', candidate):
                candidate = clean_text(candidate)
                if len(candidate) > 3 and not candidate.startswith('#'):
                    name = candidate
                    break
        if name:
            experiments.append({
                'raw_name': name,
                'smape': smape_val,
                'context': '\n'.join(lines[max(0, i - 3):i + 3])
            })

    # 去重
    unique = {}
    for exp in experiments:
        key = (exp['raw_name'], exp['smape'])
        if key not in unique:
            unique[key] = exp
    return list(unique.values())


def extract_from_tables(content: str) -> List[Dict]:
    experiments = []
    lines = content.splitlines()
    in_table = False
    header = None
    for line in lines:
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if any(k in line.lower() for k in ['实验', '模型', 'smape', '节点']):
                    header = cells
                continue
            if header:
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) == len(header):
                    row = dict(zip(header, cells))
                    smape = None
                    for k, v in row.items():
                        if 'smape' in k.lower() or '误差' in k or '准确率' in k:
                            smape = parse_smape(v)
                            break
                    if smape:
                        name = ''
                        for k in ['实验', '模型', '方法', '配置']:
                            if k in row:
                                name = row[k]
                                break
                        if name:
                            experiments.append({
                                'raw_name': name,
                                'smape': smape,
                                'context': str(row)
                            })
        else:
            in_table = False
            header = None
    return experiments


def merge_and_enhance(experiments: List[Dict]) -> List[Dict]:
    results = []
    seen_names = set()
    for exp in experiments:
        raw_name = exp['raw_name']
        smape = exp['smape']
        context = exp.get('context', '')

        if raw_name in seen_names:
            continue
        seen_names.add(raw_name)

        node_count, nodes = parse_nodes_from_name(raw_name)
        window = parse_window(raw_name)
        mu = parse_mu(raw_name, context)
        features = parse_features(raw_name, context)

        results.append({
            'name': clean_text(raw_name),
            'node_count': node_count if node_count is not None else '',
            'nodes': nodes if nodes else '',
            'window': window,
            'smape': smape,
            'mu': mu if mu is not None else '',
            'features': features
        })
    return results


def main():
    if not LOGS_DIR.exists():
        print(f"错误：日志目录不存在 {LOGS_DIR}")
        return

    all_experiments = []
    for md_file in sorted(LOGS_DIR.glob("*.md")):
        print(f"处理文件: {md_file.name}")
        content = md_file.read_text(encoding='utf-8')
        table_exps = extract_from_tables(content)
        text_exps = extract_experiments_from_text(content)
        combined = table_exps + text_exps
        if combined:
            print(f"  提取到 {len(combined)} 条候选实验")
            all_experiments.extend(combined)

    if not all_experiments:
        print("未找到任何实验记录。")
        return

    final_exps = merge_and_enhance(all_experiments)
    final_exps.sort(key=lambda x: x['smape'] if isinstance(x['smape'], (int, float)) else 999)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['name', 'node_count', 'nodes', 'window', 'smape', 'mu', 'features']
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for exp in final_exps:
            row = {k: exp.get(k, '') for k in fieldnames}
            writer.writerow(row)

    print(f"\n✅ 实验汇总表已生成：{OUTPUT_CSV}")
    print(f"共 {len(final_exps)} 条实验记录。")


if __name__ == "__main__":
    main()