"""
根 conftest.py 只做一件事：把 testing/ 下按职责拆分的 fixture 和 hook 模块
注册为 pytest 插件。不在这里写任何具体逻辑——这是分层架构的组合根，
但连组合根本身也不该膨胀成一个"什么都塞"的文件。

新增一类 fixture/hook 时，在 testing/fixtures 或 testing/hooks 下开新文件，
然后在这里加一行即可，不需要动其他任何插件的代码。
"""
pytest_plugins = [
    "testing.fixtures.browser_fixtures",
    "testing.fixtures.data_fixtures",
    "testing.hooks.failure_capture",
    "testing.hooks.flaky_reporting",
]
