from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from ui.pages.login_page import LoginPage


@pytest.mark.regression
def test_login_page_visual(page: Page) -> None:
    """全页面视觉回归对比。

    首次运行会在 tests/__snapshots__/ 下生成基准图（baseline），之后每次运行
    都和基准图做像素级 diff，超过阈值就判定失败，并在 test-results 里生成
    actual/expected/diff 三张图方便定位差异位置。

    基准图需要提交到代码仓库；且必须保证"生成基准图"和"后续比对"用的是
    同一浏览器版本 + 同一操作系统（字体渲染、抗锯齿天然有差异，跨环境比对
    会大量误报）——这也是为什么 CI 要固定用官方 Playwright Docker 镜像跑，
    而不是随便一台 ubuntu-latest 装浏览器就完事。
    """
    login_page = LoginPage(page)
    login_page.open()

    expect(page).to_have_screenshot(
        "login-page.png",
        full_page=True,
        animations="disabled",  # 关闭CSS动画/过渡，避免截图时机不同导致的偶发差异
        mask=[page.locator("[data-testid='current-time']")],  # 屏蔽时间戳等动态内容区域
        max_diff_pixel_ratio=0.02,  # 容忍2%以内的像素差异（抗锯齿等细微渲染噪声）
    )


@pytest.mark.regression
def test_login_button_visual(page: Page) -> None:
    """局部元素级视觉回归：只对比某个组件而不是整页。
    好处：页面其他区域的正常变动（比如公告栏文案更新）不会导致这条用例误报失败，
    定位速度也比对着一整张全页 diff 图找差异快得多。
    """
    login_page = LoginPage(page)
    login_page.open()

    expect(login_page.login_button).to_have_screenshot("login-button.png")
