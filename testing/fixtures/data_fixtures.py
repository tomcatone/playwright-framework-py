from __future__ import annotations

import pytest

from core.db.db_client import DbClient
from domain.user.user_api import UserApi


@pytest.fixture
def db_session():
    """每个用例独立的数据库事务：用例内查询/写入都在这个事务中，
    结束后统一 rollback，既保证隔离性，也不需要手写清理 SQL。"""
    with DbClient.transactional_session() as session:
        yield session


@pytest.fixture
def user_api():
    """提供 API 造数据能力，用例结束后自动清理所创建的数据，
    避免脏数据累积、影响下一轮测试的隔离性。

    这个 fixture 是"组合根"的典型体现：它知道 domain.user.UserApi 的存在，
    并且负责编排它的生命周期（创建、追踪、清理），但 UserApi 本身完全不知道
    自己是在 pytest 场景下被使用的。
    """
    api = UserApi()
    created_user_ids: list[str] = []

    def create_and_track(username: str, password: str) -> dict:
        user = api.create_user(username, password)
        created_user_ids.append(user["id"])
        return user

    api.create_and_track = create_and_track  # type: ignore[attr-defined]

    yield api

    for uid in created_user_ids:
        try:
            api.delete_user(uid)
        except Exception:
            pass  # 清理失败不应影响用例本身的通过/失败判定
    api.client.close()
