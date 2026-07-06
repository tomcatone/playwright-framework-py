from __future__ import annotations

import pytest

from core.notification.feishu_notifier import send_feishu_notification
from core.reporting.failure_summary import build_failure_summary
from core.reporting.flaky_tracker import FlakyTracker

_flaky_tracker = FlakyTracker()


# ---------------------------------------------------------------------------
# flaky 隔离清单：pytest-rerunfailures 在真正判定失败前，
# 每次失败重跑都会产生一条 outcome == "rerun" 的报告，这里逐条记录下来。
# ---------------------------------------------------------------------------
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.outcome == "rerun":
        _flaky_tracker.record_rerun(report.nodeid)


# ---------------------------------------------------------------------------
# 失败通知：整个 session 结束后，如果存在失败用例，推送摘要到飞书群
# （需配置环境变量 FEISHU_WEBHOOK_URL，未配置则静默跳过，不影响本地开发）。
# 同时把 flaky 隔离清单落盘，供后续排查/统计使用。
#
# 这里只做"编排"：什么时候该统计、什么时候该发通知，具体的统计逻辑在
# core.reporting.FlakyTracker，具体的文案组装在 core.reporting.failure_summary，
# 具体的发送机制在 core.notification —— 三件事三个模块，改任何一件不影响其他两件。
# ---------------------------------------------------------------------------
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _flaky_tracker.save()

    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is None:
        return

    passed = len(terminal.stats.get("passed", []))
    failed = len(terminal.stats.get("failed", []))
    skipped = len(terminal.stats.get("skipped", []))
    flaky = len(_flaky_tracker.rerun_counts)

    if failed > 0:
        summary = build_failure_summary(passed=passed, failed=failed, skipped=skipped, flaky=flaky)
        send_feishu_notification(summary)
