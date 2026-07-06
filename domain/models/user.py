from __future__ import annotations

from pydantic import BaseModel


class UserResponse(BaseModel):
    """用户接口返回结构。

    这是 domain 层的一部分：定义"用户"这个业务概念在系统边界上长什么样。
    字段类型/是否必填的变化会在测试时立刻暴露（通过 assertions.api_assertions
    做 schema 校验），比等到 UI 用到某个字段才发现后端悄悄改了结构要早得多。
    """

    id: str
    username: str
    created_at: str
