from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.settings import get_settings
from core.logging.test_logger import attach_page_logging, create_test_logger


@pytest.fixture(scope="session")
def base_url() -> str:
    """覆盖 pytest-playwright 默认的 base_url fixture，统一从 config.settings 读取，
    方便在不同环境（dev/staging/CI）切换而无需改代码。"""
    return get_settings().base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """全局浏览器 context 参数（截图/video/trace 的失败时录制策略走 CLI 参数即可，
    见 pytest.ini 中 --screenshot/--video/--tracing，这里只统一视口大小）"""
    settings = get_settings()
    return {
        **browser_context_args,
        "viewport": {"width": settings.viewport_width, "height": settings.viewport_height},
    }


# ---------------------------------------------------------------------------
# 用例相互隔离：pytest-playwright 的 `page` fixture 默认是函数级作用域，每个用例
# 都会创建全新的 browser context + page，不共享 cookie/localStorage/登录态。
# 这里不覆盖它的生命周期，只是在其基础上附加日志监听。
# ---------------------------------------------------------------------------
@pytest.fixture
def logger(request: pytest.FixtureRequest, page: Page):
    """每个用例独立 logger，自动挂接页面事件监听。"""
    test_logger, log_path = create_test_logger(request.node.nodeid)
    attach_page_logging(page, test_logger)
    test_logger.info(f">>> Test started: {request.node.nodeid}")

    yield test_logger

    test_logger.info("<<< Test finished")
    # 把日志路径挂到 node 上，供 testing/hooks/failure_capture.py 里的失败截图 hook 一并处理
    request.node._log_path = log_path
