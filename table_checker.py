import csv
import json
from typing import Any, Dict, List, Set


class Issue:
    def __init__(self, table: str, row: int, field: str, rule: str, message: str):
        self.table = table
        self.row = row
        self.field = field
        self.rule = rule
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table": self.table,
            "row": self.row,
            "field": self.field,
            "rule": self.rule,
            "message": self.message,
        }

    def __str__(self) -> str:
        return f"[{self.rule}] {self.table} row={self.row} field={self.field}: {self.message}"


def load_csv(file_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def parse_int(value: str) -> int:
    return int(value)


def check_type(table_name: str, rows: List[Dict[str, str]], field: str, expected_type: str) -> List[Issue]:
    issues: List[Issue] = []

    for idx, row in enumerate(rows, start=2):  # CSV header at row 1
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


def check_range(table_name: str, rows: List[Dict[str, str]], field: str, min_value: int = None, max_value: int = None) -> List[Issue]:
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
    issues: List[Issue] = []
    seen: Dict[str, int] = {}

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")
        if value in seen:
            first_row = seen[value]
            issues.append(
                Issue(
                    table=table_name,
                    row=idx,
                    field=field,
                    rule="unique_check",
                    message=f"duplicate value '{value}', first seen at row {first_row}",
                )
            )
        else:
            seen[value] = idx

    return issues


def build_index(rows: List[Dict[str, str]], field: str) -> Set[str]:
    return {row.get(field, "") for row in rows}


def check_foreign_key(
    table_name: str,
    rows: List[Dict[str, str]],
    field: str,
    ref_table_name: str,
    ref_rows: List[Dict[str, str]],
    ref_field: str,
) -> List[Issue]:
    issues: List[Issue] = []
    ref_index = build_index(ref_rows, ref_field)

    for idx, row in enumerate(rows, start=2):
        value = row.get(field, "")
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


def main() -> None:
    # 1. 读取两张表
    item_rows = load_csv("item.csv")
    reward_rows = load_csv("reward.csv")

    all_issues: List[Issue] = []

    # 2. 字段类型检查
    all_issues.extend(check_type("item.csv", item_rows, "id", "int"))
    all_issues.extend(check_type("item.csv", item_rows, "price", "int"))
    all_issues.extend(check_type("item.csv", item_rows, "reward_id", "int"))

    # 3. 数值范围检查
    all_issues.extend(check_range("item.csv", item_rows, "price", min_value=0, max_value=999999))

    # 4. 唯一性检查
    all_issues.extend(check_unique("item.csv", item_rows, "id"))
    all_issues.extend(check_unique("reward.csv", reward_rows, "id"))

    # 5. 外键检查
    all_issues.extend(
        check_foreign_key(
            table_name="item.csv",
            rows=item_rows,
            field="reward_id",
            ref_table_name="reward.csv",
            ref_rows=reward_rows,
            ref_field="id",
        )
    )

    # 6. 输出结果
    if not all_issues:
        print("Check passed: no issues found.")
    else:
        print("Check failed. Issues:")
        for issue in all_issues:
            print(issue)

        with open("report.json", "w", encoding="utf-8") as f:
            json.dump([issue.to_dict() for issue in all_issues], f, ensure_ascii=False, indent=2)

        print("\nDetailed report saved to report.json")


if __name__ == "__main__":
    main()