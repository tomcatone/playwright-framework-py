from __future__ import annotations

import pytest
from playwright.sync_api import Page, Route, expect

from ui.pages.login_page import LoginPage


@pytest.mark.regression
def test_login_when_api_returns_500(page: Page, logger):
    """通过 page.route 拦截登录接口，模拟后端返回 500，验证前端异常提示是否正确。
    好处：不依赖真实后端制造故障，本地/CI 都能稳定复现这类异常分支，
    也不会因为真实调了后端接口而产生脏数据。"""

    def handle_route(route: Route) -> None:
        route.fulfill(status=500, content_type="application/json", body='{"message": "internal error"}')

    page.route("**/api/login", handle_route)

    login_page = LoginPage(page)
    login_page.open()
    login_page.login("valid_user", "Valid@123")

    expect(page.get_by_text("服务异常，请稍后重试")).to_be_visible()


@pytest.mark.regression
def test_create_user_via_api_then_login_via_ui(page: Page, logger, user_api):
    """用 API 直接造一个用户（比走 UI 注册流程快很多），
    再验证这个用户能通过 UI 正常登录。造出来的用户会在用例结束后被自动清理。"""
    user = user_api.create_and_track(username="api_created_user", password="Valid@123")
    logger.info(f"通过 API 创建用户: {user}")

    login_page = LoginPage(page)
    login_page.open()
    login_page.login("api_created_user", "Valid@123")
    login_page.expect_login_success()
