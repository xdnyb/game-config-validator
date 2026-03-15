"""
输入层模块。

该模块负责：
1. 读取配置表文件（当前 Demo 支持 CSV）
2. 读取规则配置文件（JSON）
3. 将外部文件转换为统一的数据结构，供规则引擎使用

这是整个框架中的“输入层”。
后续如果要扩展 Excel / JSON / XML，只需要在这一层增加对应的 Loader。
"""

import csv
import json
from typing import Dict, List


def load_csv(file_path: str) -> List[Dict[str, str]]:
    """
    读取 CSV 配表，并将每一行转换为字典。

    返回结果示例：
    [
        {"id": "1", "name": "sword", "price": "100", "reward_id": "10"},
        {"id": "2", "name": "shield", "price": "-5", "reward_id": "999"}
    ]

    说明：
    - key 为表头字段名
    - value 为原始字符串
    - 后续类型转换由具体校验器负责
    """
    rows: List[Dict[str, str]] = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def load_rules(file_path: str) -> Dict:
    """
    读取 JSON 规则配置文件。

    规则配置的目标是将“规则定义”与“程序逻辑”解耦，
    这样当项目规则变化时，可以优先改配置，而不是直接改主程序代码。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)