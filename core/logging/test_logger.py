from __future__ import annotations

import logging
import re
from pathlib import Path

LOG_DIR = Path("test-results/logs")


def _safe_name(node_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", node_id)


def create_test_logger(node_id: str) -> tuple[logging.Logger, Path]:
    """为单个用例创建独立 logger + 独立日志文件。

    职责边界：这个模块只管"怎么创建一个按用例隔离的 logger"，不关心调用方
    是浏览器测试还是 API 测试——这正是"高内聚"的体现：单一职责，谁都能复用。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = _safe_name(node_id)
    log_path = LOG_DIR / f"{safe_id}.log"

    logger = logging.getLogger(safe_id)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # 防止 xdist worker 复用同名 logger 导致 handler 重复累加

    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
    logger.propagate = False

    return logger, log_path


def attach_page_logging(page, logger: logging.Logger) -> None:
    """捕获浏览器 console / pageerror / 网络失败，统一写入 logger。

    依赖倒置：接收一个已经创建好的 logger，而不是自己决定往哪写、怎么写——
    “写日志”和“采集浏览器事件”两件事解耦，互不干扰。
    """
    page.on("console", lambda msg: logger.debug(f"[console:{msg.type}] {msg.text}"))
    page.on("pageerror", lambda exc: logger.error(f"[pageerror] {exc}"))
    page.on(
        "requestfailed",
        lambda req: logger.warning(f"[requestfailed] {req.method} {req.url} - {req.failure}"),
    )
    page.on(
        "response",
        lambda res: logger.warning(f"[http {res.status}] {res.url}") if res.status >= 400 else None,
    )
