from __future__ import annotations

import pytest
from playwright.sync_api import Page

from core.data.loaders import case_id, load_json_data
from ui.pages.login_page import LoginPage

CASES = load_json_data("data/login_cases.json")


# 关键点：用 @pytest.mark.parametrize 而不是在一个 test 函数内 for 循环断言。
# 好处：
# 1) 用例互相隔离 —— 每条数据是独立的 pytest item，各自独立的 page/context，
#    一条数据失败不影响其余数据的执行与报告展示
# 2) --reruns 重跑时可以精确重跑某一条参数化用例，而不是整组重来
# 3) 报告里每条数据单独一行（形如 test_login[正确账号密码]），定位问题更直接
#
# 页面操作都收敛到 ui.pages.LoginPage 里，用例只表达业务意图，不关心具体 selector。
@pytest.mark.regression
@pytest.mark.parametrize("case", CASES, ids=lambda c: case_id(c))
def test_login(page: Page, logger, case: dict):
    logger.info(f"执行数据: {case}")

    login_page = LoginPage(page)
    login_page.open()
    login_page.login(case["username"], case["password"])

    if case["expect_success"]:
        login_page.expect_login_success()
    else:
        login_page.expect_login_failed()
