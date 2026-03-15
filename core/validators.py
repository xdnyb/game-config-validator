"""
校验器模块。

该模块负责实现具体的校验逻辑。
每一种规则类型，都由一个对应的 validator 函数完成实际检查。

当前支持：
- 类型检查
- 范围检查
- 唯一性检查
- 外键检查
- 条件业务规则检查

设计思路：
规则引擎只负责“分发规则”，具体怎么检查由 validators 模块负责，
这样可以让职责更清晰，也方便后续扩展新的规则类型。
"""

from typing import Dict, List, Set
from core.issue import Issue


def parse_int(value: str) -> int:
    """
    将字符串转换为 int。

    说明：
    这里单独拆成函数，便于后续统一处理数值类型转换逻辑。
    """
    return int(value)


def check_type(table_name: str, rows: List[Dict[str, str]], field: str, expected_type: str) -> List[Issue]:
    """
    字段类型检查。

    示例：
    - id 必须是 int
    - price 必须是 int
    - name 必须是 string

    当前 Demo 中主要支持 int / string 两类基础类型。
    """
    issues: List[Issue] = []

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")

        if expected_type == "int":
            try:
                parse_int(value)
            except ValueError:
                issues.append(
                    Issue(
                        table=table_name,
                        row=idx,
                        field=field,
                        rule="type_check",
                        message=f"expected int, got '{value}'",
                    )
                )

        elif expected_type == "string":
            if value is None:
                issues.append(
                    Issue(
                        table=table_name,
                        row=idx,
                        field=field,
                        rule="type_check",
                        message="expected string, got None",
                    )
                )

    return issues


def check_range(table_name: str, rows: List[Dict[str, str]], field: str, min_value=None, max_value=None) -> List[Issue]:
    """
    数值范围检查。

    示例：
    - price 必须 >= 0
    - level 必须在 1~100 之间

    说明：
    范围检查依赖字段本身可转换为 int。
    如果字段本身不是合法整数，也会在这里记录问题。
    """
    issues: List[Issue] = []

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")

        try:
            num = parse_int(value)
        except ValueError:
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="range_check",
                    message=f"value '{value}' is not a valid int",
                )
            )
            continue

        if min_value is not None and num < min_value:
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="range_check",
                    message=f"value {num} < min {min_value}",
                )
            )

        if max_value is not None and num > max_value:
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="range_check",
                    message=f"value {num} > max {max_value}",
                )
            )

    return issues


def check_unique(table_name: str, rows: List[Dict[str, str]], field: str) -> List[Issue]:
    """
    唯一性检查。

    示例：
    - 主键 id 不能重复
    - 某些配置编码字段不能重复

    实现方式：
    使用字典记录已经出现过的值，并保存其首次出现的行号，
    一旦后续再次出现相同值，就记录为重复问题。
    """
    issues: List[Issue] = []
    seen: Dict[str, int] = {}

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")

        if value in seen:
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="unique_check",
                    message=f"duplicate value '{value}', first seen at row {seen[value]}",
                )
            )
        else:
            seen[value] = idx

    return issues


def build_index(rows: List[Dict[str, str]], field: str) -> Set[str]:
    """
    为某张表的某个字段建立索引集合。

    用途：
    - 外键检查时快速判断某个引用值是否存在
    - 通过 set 提高查询效率

    这也是对题目中“性能优化”的一个最小实现体现。
    """
    return {row.get(field, "") for row in rows}


def check_foreign_key(
    table_name: str,
    rows: List[Dict[str, str]],
    field: str,
    ref_table_name: str,
    ref_rows: List[Dict[str, str]],
    ref_field: str,
) -> List[Issue]:
    """
    外键检查 / 多表关联检查。

    示例：
    item.csv 中的 reward_id 必须存在于 reward.csv 的 id 字段中。

    实现思路：
    先为被引用表建立索引，再逐行检查当前表字段值是否存在于该索引中。
    """
    issues: List[Issue] = []
    ref_index = build_index(ref_rows, ref_field)

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")

        # 空值在当前 Demo 中仍会被视为一个待检查值。
        # 后续如果需要更细粒度控制，可以增加 skip_empty 等配置。
        if value not in ref_index:
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="foreign_key_check",
                    message=f"value '{value}' not found in {ref_table_name}.{ref_field}",
                )
            )

    return issues


def check_conditional_required(
    table_name: str,
    rows: List[Dict[str, str]],
    if_field: str,
    operator: str,
    if_value,
    required_field: str,
) -> List[Issue]:
    """
    条件业务规则检查器。

    这是一个简单的自定义业务逻辑示例，用于补充通用规则之外的业务校验能力。

    示例：
    当 price > 100 时，reward_id 必须填写。

    支持的比较运算：
    - gt  : >
    - lt  : <
    - eq  : ==
    - neq : !=
    """
    issues: List[Issue] = []

    for idx, row in enumerate(rows, start=2):
        left_value = row.get(if_field, "")
        target_value = row.get(required_field, "")

        matched = False

        try:
            if operator == "gt":
                matched = int(left_value) > int(if_value)
            elif operator == "lt":
                matched = int(left_value) < int(if_value)
            elif operator == "eq":
                matched = str(left_value) == str(if_value)
            elif operator == "neq":
                matched = str(left_value) != str(if_value)
        except ValueError:
            # 如果条件字段本身无法比较，则这里先跳过。
            # 这类问题通常会由类型检查或范围检查优先报出。
            continue

        # 当条件成立时，required_field 必须非空
        if matched and (target_value is None or str(target_value).strip() == ""):
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=required_field,
                    rule="conditional_required_check",
                    message=(
                        f"field '{required_field}' is required when "
                        f"{if_field} {operator} {if_value}"
                    ),
                )
            )

    return issues