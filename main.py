import json
import os
import sys
from core.loader import load_csv, load_rules
from core.engine import run_validation


def main() -> None:
    tables = {
        "item.csv": load_csv("data/item.csv"),
        "reward.csv": load_csv("data/reward.csv"),
    }

    rules_config = load_rules("rules/rules.json")
    issues = run_validation(tables, rules_config)

    os.makedirs("output", exist_ok=True)

    if not issues:
        print("Check passed: no issues found.")
        sys.exit(0)
    else:
        print("Check failed. Issues:")
        for issue in issues:
            print(issue)

        with open("output/report.json", "w", encoding="utf-8") as f:
            json.dump([issue.to_dict() for issue in issues], f, ensure_ascii=False, indent=2)

        print("\nDetailed report saved to output/report.json")
        sys.exit(1)


if __name__ == "__main__":
    main()