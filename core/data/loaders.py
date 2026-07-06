from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json_data(relative_path: str) -> list[dict[str, Any]]:
    """从 JSON 文件加载数据驱动用例数据"""
    path = Path(relative_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_csv_data(relative_path: str) -> list[dict[str, Any]]:
    """从 CSV 文件加载数据驱动用例数据（首行为表头）"""
    path = Path(relative_path)
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def case_id(case: dict[str, Any], key: str = "caseName") -> str:
    """为 pytest.mark.parametrize 生成可读的用例 id，便于在报告/终端里识别具体数据"""
    return str(case.get(key, "case"))
