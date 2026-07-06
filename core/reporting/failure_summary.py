from __future__ import annotations


def build_failure_summary(passed: int, failed: int, skipped: int, flaky: int) -> str:
    """把统计数字组装成一段可读文本。

    刻意做成不依赖任何 IO 的纯函数：不发请求、不读文件，只做字符串拼接。
    这样"消息内容怎么措辞"和"消息怎么送出去"（core/notification）完全解耦，
    改文案不用碰通知逻辑，单元测试也不需要 mock 网络请求。
    """
    return (
        "【自动化测试结果通知】\n"
        f"通过: {passed}  失败: {failed}  跳过: {skipped}  不稳定(重跑后才过): {flaky}\n"
        "详情请查看 Allure / HTML 报告"
    )
