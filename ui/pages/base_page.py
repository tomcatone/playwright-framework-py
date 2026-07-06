from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """所有页面对象的基类：封装通用导航/等待逻辑。

    这一层刻意只依赖 playwright，不 import 任何 core/domain 模块——
    UI 页面对象描述的是"页面长什么样、能做什么操作"，和"怎么发请求""怎么查库"
    是完全不同维度的关注点。这样即使把整个后端接口层重写一遍，UI 页面对象
    也完全不需要改动，反之亦然。
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, path: str = "") -> None:
        self.page.goto(path)

    def wait_for_url_contains(self, fragment: str, timeout: int = 10_000) -> None:
        self.page.wait_for_url(f"**/*{fragment}*", timeout=timeout)
