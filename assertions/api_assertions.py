from __future__ import annotations

import httpx
from pydantic import BaseModel


def assert_api_response(
    response: httpx.Response,
    expected_status: int = 200,
    schema: type[BaseModel] | None = None,
) -> dict:
    """校验接口返回的状态码，以及可选的响应结构（pydantic schema）。

    不依赖任何具体业务 schema——调用方传入 domain 层定义好的模型
    （如 domain.models.user.UserResponse），断言层本身不需要知道
    "用户"长什么样，只需要知道"怎么用一个 pydantic 模型去校验"。

    schema 校验能提前发现"字段被后端悄悄改名/删掉/类型变了"这类
    只看状态码发现不了的问题。校验通过后返回解析好的 JSON，供后续做具体字段断言。
    """
    assert response.status_code == expected_status, (
        f"期望状态码 {expected_status}，实际 {response.status_code}，响应体: {response.text}"
    )
    data = response.json()
    if schema is not None:
        schema.model_validate(data)  # 结构/类型不匹配会抛 pydantic.ValidationError，测试直接失败
    return data
