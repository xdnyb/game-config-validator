"""
问题模型模块。

该模块用于统一表示“校验发现的问题”。
无论问题来自类型检查、范围检查、唯一性检查、外键检查，
还是业务规则检查，最终都会转换为统一的 Issue 结构，
便于后续在控制台输出或写入 JSON 报告。
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Issue:
    """
    单条校验问题的数据结构。

    字段说明：
    - table: 问题所在表名
    - row: 问题所在行号（按 CSV 真实行号展示，表头为第 1 行）
    - field: 问题所在字段名
    - rule: 触发问题的规则类型
    - message: 详细错误信息
    """
    table: str
    row: int
    field: str
    rule: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """
        将 Issue 转换为字典，便于后续写入 JSON 报告。
        """
        return asdict(self)

    def __str__(self) -> str:
        """
        定义控制台输出格式，便于直接打印问题信息。
        """
        return f"[{self.rule}] {self.table} row={self.row} field={self.field}: {self.message}"