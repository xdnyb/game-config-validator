from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Issue:
    table: str
    row: int
    field: str
    rule: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"[{self.rule}] {self.table} row={self.row} field={self.field}: {self.message}"