from __future__ import annotations

import shutil
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page


# ---------------------------------------------------------------------------
# 会话级清理：清空上一轮的报告/日志产物，避免不同轮次结果互相污染
# ---------------------------------------------------------------------------
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    for d in ("test-results", "playwright-report", "allure-results"):
        shutil.rmtree(d, ignore_errors=True)
        Path(d).mkdir(parents=True, exist_ok=True)
    Path("test-results/logs").mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 错误截图 + 日志收集：失败时自动截图、附加日志到 Allure 报告。
# 通过 pytest hook 在用例执行完（setup/call/teardown 三阶段）后判断结果，
# 避免每条用例手写 try/except 截图代码。
#
# 这个 hook 只做"失败时如何采集证据"，不关心证据是怎么产生的（日志来自
# core.logging，截图直接调 page API）——采集时机和采集内容来源解耦。
# ---------------------------------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page: Page | None = item.funcargs.get("page")
    if page is not None:
        try:
            screenshot_dir = Path("test-results/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"{item.nodeid.replace('::', '__').replace('/', '_')}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            allure.attach.file(
                str(screenshot_path), name="failure-screenshot", attachment_type=allure.attachment_type.PNG
            )
        except Exception:
            # page 可能已经关闭/崩溃，截图失败不应掩盖原始失败原因
            pass

    log_path = getattr(item, "_log_path", None)
    if log_path and Path(log_path).exists():
        allure.attach.file(str(log_path), name="test-log", attachment_type=allure.attachment_type.TEXT)
