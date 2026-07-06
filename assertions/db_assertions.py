from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from core.db.db_client import DbClient


def assert_db_record_exists(session: Session, table: str, where: dict[str, Any]) -> dict:
    """断言数据库中存在满足条件的记录，返回该记录供后续字段级断言使用。

    保持通用（不绑定具体表名），是断言层和 domain 层解耦的关键：
    domain 层的 Repository 知道"用户表叫 users"，这里只知道"给个表名和条件去查"。

    注意：`table` 和 `where` 的 key 必须是可信的内部常量，不能来自外部输入，
    这里用命名参数绑定值本身（防注入），但字段名/表名是字符串拼接，
    调用方需保证这些名字不是外部可控的。
    """
    conditions = " AND ".join(f"{k} = :{k}" for k in where)
    sql = f"SELECT * FROM {table} WHERE {conditions} LIMIT 1"  # noqa: S608
    row = DbClient.fetch_one(session, sql, where)
    assert row is not None, f"数据库表 {table} 中未找到满足条件 {where} 的记录"
    return row


def assert_db_field_equals(
    session: Session, table: str, where: dict[str, Any], field: str, expected: Any
) -> None:
    """断言数据库记录中指定字段的值，用于验证接口/UI操作是否真的正确落库
    （而不是只有接口返回了"成功"，实际数据没写对）"""
    row = assert_db_record_exists(session, table, where)
    actual = row.get(field)
    assert actual == expected, f"字段 {field} 期望 {expected!r}，实际 {actual!r}（完整记录: {row}）"
