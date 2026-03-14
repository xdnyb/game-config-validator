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
    issues: List[Issue] = []

    for table_name, table_rules in rules_config.items():
        rows = all_tables.get(table_name, [])

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

    return issues