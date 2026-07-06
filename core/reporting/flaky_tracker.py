from __future__ import annotations

import json
from pathlib import Path

FLAKY_REPORT_PATH = Path("test-results/flaky-report.json")


class FlakyTracker:
    """记录哪些用例是经过 pytest-rerunfailures 重跑才最终通过的。

    职责边界：只负责"统计 + 落盘"，不知道 pytest hook 的调用时机、
    不知道要不要发通知——这些编排逻辑属于 testing/hooks 层。

    这类用例不应该和"一次就稳定通过"的用例混在一起统计通过率——
    它们是潜在的不稳定因素，需要单独生成清单，定期排查是真 flaky
    还是代码有 race condition，而不是靠重跑一直掩盖下去。
    """

    def __init__(self) -> None:
        self.rerun_counts: dict[str, int] = {}

    def record_rerun(self, nodeid: str) -> None:
        self.rerun_counts[nodeid] = self.rerun_counts.get(nodeid, 0) + 1

    def save(self) -> None:
        FLAKY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [{"nodeid": k, "rerun_count": v} for k, v in sorted(self.rerun_counts.items())]
        FLAKY_REPORT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
