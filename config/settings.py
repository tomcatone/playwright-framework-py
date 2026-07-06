from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理所有环境相关配置。

    这是整个框架依赖关系的最底层：不依赖任何其他内部模块，只依赖环境变量/.env 文件。
    所有其他层（core/domain/testing）需要配置项时都从这里读取，
    替换掉散落在各文件里的 `os.environ.get(...)` 调用——改一个环境变量的默认值
    只需要改这一处，而且有类型校验，配置项也集中可见、可审查。
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    base_url: str = "https://example.com"
    api_base_url: str = "https://api.example.com"
    api_token: str | None = None
    database_url: str = "postgresql+psycopg2://user:pass@localhost:5432/testdb"
    feishu_webhook_url: str | None = None

    viewport_width: int = 1440
    viewport_height: int = 900


@lru_cache
def get_settings() -> Settings:
    """全局单例：同一次运行内配置只解析一次。"""
    return Settings()
