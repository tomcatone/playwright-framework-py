from __future__ import annotations

from core.http.http_client import HttpClient


class UserApi:
    """用户相关接口封装。

    这是 domain 层：知道"创建用户要 POST /api/users"这类业务规则，
    但具体"怎么发请求"完全委托给 core.http.HttpClient——
    如果哪天要把 httpx 换成别的 HTTP 库，只用改 HttpClient，这里不用动。
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self.client = client or HttpClient()

    def create_user(self, username: str, password: str) -> dict:
        resp = self.client.post("/api/users", json={"username": username, "password": password})
        resp.raise_for_status()
        return resp.json()

    def delete_user(self, user_id: str) -> None:
        self.client.delete(f"/api/users/{user_id}")
