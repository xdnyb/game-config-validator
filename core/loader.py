import csv
import json
from typing import Dict, List


def load_csv(file_path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def load_rules(file_path: str) -> Dict:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)