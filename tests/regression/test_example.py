from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


# 用例隔离：不要用模块级变量保存 page/context，pytest-playwright 的 page fixture
# 默认函数级作用域，每个用例都拿到全新的浏览器上下文，天然避免状态串扰。
def test_search_returns_results(page: Page, logger):
    logger.info("打开首页")
    page.goto("/")
    page.get_by_placeholder("搜索").fill("playwright")
    page.keyboard.press("Enter")
    expect(page.get_by_test_id("search-results")).to_be_visible()


@pytest.mark.flaky
def test_third_party_widget(page: Page, logger):
    """已知偶发不稳定的用例，配合 pytest.ini 里 --only-rerun 规则，
    仅在命中指定异常类型时才重跑，避免掩盖非预期错误"""
    logger.info("加载依赖三方接口的组件")
    page.goto("/third-party-widget")
    expect(page.get_by_text("加载完成")).to_be_visible(timeout=15_000)
