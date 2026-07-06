from __future__ import annotations

import pytest

from assertions.api_assertions import assert_api_response
from assertions.db_assertions import assert_db_field_equals
from domain.models.user import UserResponse


@pytest.mark.regression
def test_create_user_api_response_and_db_record(user_api, db_session):
    """同一个"创建用户"操作，从两个层面验证是否真的做对了：
    1) 接口返回的状态码 + 字段结构是否符合预期 schema（不只是看 200 就完事）
    2) 数据库里是否真的落库、字段值是否正确
       （避免"接口返回成功，但其实压根没写库"这类问题被漏测）

    UI 层面对同一条数据的验证见 tests/regression/test_network_mock.py 中
    test_create_user_via_api_then_login_via_ui。
    """
    response = user_api.client.post(
        "/api/users", json={"username": "db_check_user", "password": "Valid@123"}
    )
    data = assert_api_response(response, expected_status=201, schema=UserResponse)

    assert_db_field_equals(
        db_session,
        table="users",
        where={"id": data["id"]},
        field="username",
        expected="db_check_user",
    )

    # 用返回的 id 直接清理，db_session 走的是独立事务不会影响这里通过 API 造的数据
    user_api.delete_user(data["id"])
