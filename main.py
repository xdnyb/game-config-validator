"""
程序入口模块。

该脚本负责串联整个配表校验框架的主流程：
1. 读取配置表数据
2. 读取 JSON 规则配置
3. 调用规则引擎执行校验
4. 输出控制台结果
5. 生成 JSON 报告
6. 返回退出码，便于接入 CI

额外说明：
- 默认模式下使用带错误的示例数据，方便本地演示
- CI 模式下可切换到合法数据集，保证 workflow 通过
"""

import json
import os
import sys
from core.loader import load_csv, load_rules
from core.engine import run_validation


def main() -> None:
    """
    主程序入口。
    """
    # 通过环境变量控制使用哪套数据：
    # - example: 本地演示数据（包含错误）
    # - ci: CI 使用的合法数据
    data_mode = os.getenv("DATA_MODE", "example")

    if data_mode == "ci":
        tables = {
            "item.csv": load_csv("data/item_valid.csv"),
            "reward.csv": load_csv("data/reward.csv"),
        }
    else:
        tables = {
            "item.csv": load_csv("data/item.csv"),
            "reward.csv": load_csv("data/reward.csv"),
        }

    # 读取规则配置
    rules_config = load_rules("rules/rules.json")

    # 执行规则校验
    issues = run_validation(tables, rules_config)

    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)

    if not issues:
        print("Check passed: no issues found.")
        sys.exit(0)
    else:
        print("Check failed. Issues:")
        for issue in issues:
            print(issue)

        # 将所有问题写入 JSON 报告，便于后续分析或集成到 CI/CD
        with open("output/report.json", "w", encoding="utf-8") as f:
            json.dump([issue.to_dict() for issue in issues], f, ensure_ascii=False, indent=2)

        print("\nDetailed report saved to output/report.json")
        sys.exit(1)


if __name__ == "__main__":
    main()