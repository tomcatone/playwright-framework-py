from __future__ import annotations

from sqlalchemy.orm import Session

from core.db.db_client import DbClient


class UserRepository:
    """用户表的查询封装。

    domain 层知道"用户存在 users 表里，主键是 id"这类业务事实，
    但"怎么开事务、怎么执行 SQL"委托给 core.db.DbClient。
    好处：断言层（assertions/db_assertions.py）不需要知道表名/字段名，
    调用方只需要说"给我 id=xxx 的用户"，表结构变化只影响这一个文件。
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, user_id: str) -> dict | None:
        return DbClient.fetch_one(self.session, "SELECT * FROM users WHERE id = :id", {"id": user_id})
