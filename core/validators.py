from typing import Dict, List, Set
from core.issue import Issue


def parse_int(value: str) -> int:
    return int(value)


def check_type(table_name: str, rows: List[Dict[str, str]], field: str, expected_type: str) -> List[Issue]:
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