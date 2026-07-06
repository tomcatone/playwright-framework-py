from __future__ import annotations

import httpx

from config.settings import get_settings


class HttpClient:
    """通用 HTTP 客户端：封装 base_url、鉴权头、超时等公共逻辑。

    职责边界很窄——只管"怎么发一个符合规范的 HTTP 请求"，不知道
    "用户"、"订单"这类业务概念（那是 domain 层的事）。这样任何业务模块
    要调接口都可以复用它，不用重复写鉴权头拼接逻辑。
    """

    def __init__(self, base_url: str | None = None, token: str | None = None) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.api_base_url
        self.token = token or settings.api_token

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        self._client = httpx.Client(base_url=self.base_url, headers=headers, timeout=10)

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._client.get(path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self._client.post(path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self._client.delete(path, **kwargs)

    def close(self) -> None:
        self._client.close()
