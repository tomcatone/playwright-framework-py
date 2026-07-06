from __future__ import annotations

import httpx

from config.settings import get_settings


def send_feishu_notification(text: str) -> None:
    """推送文本消息到飞书群机器人。

    未配置 webhook 时静默跳过；通知本身失败也不应该影响测试流程的退出码——
    这个模块只负责"怎么发消息"，"什么时候该发"由上层（testing/hooks）决定，
    两件事分开才不会出现"改通知渠道要动测试逻辑"的耦合。
    """
    webhook = get_settings().feishu_webhook_url
    if not webhook:
        return

    payload = {"msg_type": "text", "content": {"text": text}}
    try:
        httpx.post(webhook, json=payload, timeout=5)
    except Exception:
        pass
