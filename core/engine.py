"""
规则引擎模块。

该模块是整个框架的核心调度层，负责：
1. 读取外部规则配置
2. 遍历每张表对应的规则
3. 根据规则类型分发到对应的校验器
4. 汇总所有校验问题

当前 Demo 中的规则引擎实现为轻量级原型：
- 规则来源：JSON 配置
- 分发方式：按 rule type 调用对应 validator
- 输出结果：统一收集为 Issue 列表

完整版本中，这一层还可以继续扩展为：
- 插件注册机制
- 规则优先级
- 并发调度
- 规则依赖关系管理
"""

from typing import Dict, List
from core.issue import Issue
from core.validators import (
    check_type,
    check_range,
    check_unique,
    check_foreign_key,
    check_conditional_required,
)


def run_validation(all_tables: Dict[str, List[Dict[str, str]]], rules_config: Dict) -> List[Issue]:
    """
    执行所有表的规则校验，并返回统一的问题列表。

    参数说明：
    - all_tables: 所有已加载的表数据
    - rules_config: JSON 读取后的规则配置

    返回：
    - List[Issue]：所有发现的问题
    """
    issues: List[Issue] = []

    # 遍历规则配置中定义的每张表
    for table_name, table_rules in rules_config.items():
        rows = all_tables.get(table_name, [])

        # 遍历这张表的所有规则
        for rule in table_rules:
            rule_type = rule["type"]

            if rule_type == "type":
                issues.extend(
                    check_type(
                        table_name=table_name,
                        rows=rows,
                        field=rule["field"],
                        expected_type=rule["expected"],
                    )
                )

            elif rule_type == "range":
                issues.extend(
                    check_range(
                        table_name=table_name,
                        rows=rows,
                        field=rule["field"],
                        min_value=rule.get("min"),
                        max_value=rule.get("max"),
                    )
                )

            elif rule_type == "unique":
                issues.extend(
                    check_unique(
                        table_name=table_name,
                        rows=rows,
                        field=rule["field"],
                    )
                )

            elif rule_type == "foreign_key":
                ref_table = rule["ref_table"]
                ref_field = rule["ref_field"]
                ref_rows = all_tables.get(ref_table, [])

                issues.extend(
                    check_foreign_key(
                        table_name=table_name,
                        rows=rows,
                        field=rule["field"],
                        ref_table_name=ref_table,
                        ref_rows=ref_rows,
                        ref_field=ref_field,
                    )
                )

            elif rule_type == "conditional_required":
                issues.extend(
                    check_conditional_required(
                        table_name=table_name,
                        rows=rows,
                        if_field=rule["if_field"],
                        operator=rule["operator"],
                        if_value=rule["if_value"],
                        required_field=rule["required_field"],
                    )
                )

            else:
                # 当前 Demo 中未识别的规则类型会被直接跳过。
                # 完整版本中可以考虑记录 warning 或直接抛出配置错误。
                continue

    return issues