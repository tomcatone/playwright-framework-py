from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from ui.pages.base_page import BasePage


class LoginPage(BasePage):
    """登录页元素与操作封装。

    用例只调用 login()/expect_login_success() 这类业务语义方法，
    不直接操作 selector，UI 改版时只需要改这一个文件。
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.username_input = page.get_by_label("用户名")
        self.password_input = page.get_by_label("密码")
        self.login_button = page.get_by_role("button", name="登录")
        self.error_message = page.get_by_text("用户名或密码错误")

    def open(self) -> None:
        self.goto("/login")

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def expect_login_success(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/dashboard"))

    def expect_login_failed(self) -> None:
        expect(self.error_message).to_be_visible()
