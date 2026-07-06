from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings


class DbClient:
    """数据库连接与事务隔离的基础设施。

    职责边界：只提供"怎么开一个事务、怎么查询"的通用能力，不知道
    "用户表长什么样"这类业务细节（那是 domain 层 repository 的事）。

    核心设计：每个用例通过 `transactional_session()` 拿到一个独立事务，
    用例内所有查询/写入都在这个事务里执行，用例结束后统一 rollback，
    保证不会给数据库留下测试脏数据，也不会跟并行执行的其他用例互相影响。
    """

    _engine: Engine | None = None

    @classmethod
    def get_engine(cls) -> Engine:
        if cls._engine is None:
            cls._engine = create_engine(get_settings().database_url, pool_pre_ping=True)
        return cls._engine

    @classmethod
    @contextmanager
    def transactional_session(cls) -> Iterator[Session]:
        engine = cls.get_engine()
        connection = engine.connect()
        transaction = connection.begin()
        session = sessionmaker(bind=connection)()
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()  # 无论成功失败，统一回滚，不落地任何测试数据
            connection.close()

    @staticmethod
    def fetch_one(session: Session, sql: str, params: dict[str, Any] | None = None) -> dict | None:
        row = session.execute(text(sql), params or {}).mappings().first()
        return dict(row) if row else None

    @staticmethod
    def fetch_all(session: Session, sql: str, params: dict[str, Any] | None = None) -> list[dict]:
        rows = session.execute(text(sql), params or {}).mappings().all()
        return [dict(r) for r in rows]
