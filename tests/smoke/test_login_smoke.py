from __future__ import annotations

import pytest
from playwright.sync_api import Page

from ui.pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.p0
def test_login_happy_path(page: Page, logger):
    """核心链路冒烟用例：只验证最关键的"正确账号能登录成功"，
    CI 中优先跑这条，几秒内就能判断主流程是否被破坏，不用等全量回归跑完。"""
    login_page = LoginPage(page)
    login_page.open()
    login_page.login("valid_user", "Valid@123")
    login_page.expect_login_success()
