# Playwright 测试框架（Python 3.12 / pytest / 分层架构）

## 环境要求
- Python 3.12

## 快速开始
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps

pytest -m smoke                     # 冒烟用例
pytest -m "not smoke"               # 全量回归
pytest --reruns 2 --reruns-delay 2 --only-rerun "AssertionError|TimeoutError|Error"   # CI 模式
pytest --update-snapshots           # 更新视觉回归基准图
```

## 分层架构

这次重构的核心目标：**单向依赖、职责单一、改一层不牵连其他层**。依赖方向自下而上，上层可以依赖下层，下层永远不知道上层的存在：

```
config          （配置：环境变量集中管理，不依赖任何内部模块）
   ↑
core            （基础设施：日志/HTTP/DB/通知/统计/数据加载，只懂技术，不懂业务）
   ↑
domain          （业务领域：用户等业务概念，组合core能力表达业务规则）
   ↑
assertions      （通用断言：只依赖core，不绑定具体业务表/schema）
   ↑
ui              （页面对象：只依赖Playwright，和core/domain完全零耦合，可独立复用）

testing         （组合根：唯一同时认识core/domain/ui的层，负责装配成pytest fixture/hook）
   ↑
tests           （用例：只依赖testing提供的fixture + domain + ui，不直接碰core）
```

```
playwright-framework-py/
├── config/
│   └── settings.py              # 集中配置（pydantic-settings），替代散落的 os.environ.get
├── core/                          # 基础设施层：每个子包单一职责，互不依赖
│   ├── logging/test_logger.py    # 按用例隔离的日志
│   ├── http/http_client.py       # 通用HTTP客户端（不知道"用户""订单"等业务概念）
│   ├── db/db_client.py           # 数据库事务级隔离查询
│   ├── notification/feishu_notifier.py   # 只管"怎么发消息"
│   ├── reporting/
│   │   ├── flaky_tracker.py      # 只管"怎么统计重跑"
│   │   └── failure_summary.py    # 只管"怎么组装文案"（纯函数，无IO）
│   └── data/loaders.py           # JSON/CSV 数据加载
├── domain/                        # 业务领域层：依赖core，表达业务规则
│   ├── models/user.py            # 用户接口返回结构（pydantic schema）
│   └── user/
│       ├── user_api.py           # 用户相关接口封装（组合core.http）
│       └── user_repository.py    # 用户表查询封装（组合core.db）
├── assertions/                    # 通用断言层：依赖core，不绑定具体表名/schema
│   ├── api_assertions.py         # 状态码 + pydantic schema 校验
│   └── db_assertions.py          # 数据库字段断言
├── ui/                            # UI层：只依赖Playwright，零耦合于core/domain
│   └── pages/
│       ├── base_page.py
│       └── login_page.py
├── testing/                       # 组合根：唯一被允许同时认识所有层的地方
│   ├── fixtures/
│   │   ├── browser_fixtures.py   # base_url/context参数/日志挂载
│   │   └── data_fixtures.py      # user_api（造数据+自动清理）/ db_session（事务隔离）
│   └── hooks/
│       ├── failure_capture.py    # 会话清理 + 失败截图/日志附加到报告
│       └── flaky_reporting.py    # 重跑记录 + 会话结束落盘/通知
├── conftest.py                    # 只做插件聚合（pytest_plugins列表），不写任何业务逻辑
├── data/
│   └── login_cases.json
├── tests/
│   ├── smoke/                    # 冒烟用例，CI优先跑
│   └── regression/                # 全量回归用例
├── Dockerfile                     # 固定浏览器/系统环境，保证视觉回归基准图跨环境一致
└── .github/workflows/tests.yml    # CI流水线
```

## 各层职责与耦合边界

| 层 | 知道什么 | 不知道什么 | 依赖谁 |
|----|----------|------------|--------|
| `config` | 环境变量、默认值 | 任何业务/技术细节 | 无 |
| `core` | 怎么发HTTP请求、怎么查库、怎么写日志 | "用户""订单"这类业务概念 | `config` |
| `domain` | "创建用户要POST /api/users"这类业务规则 | HTTP库具体实现、pytest的存在 | `core`, `config` |
| `assertions` | 怎么校验一条DB记录/一个API响应 | 具体表名、具体schema | `core` |
| `ui` | 页面元素长什么样、能做什么操作 | 接口怎么调、数据库怎么查 | 仅Playwright |
| `testing` | 上面所有层的存在，负责装配 | 无（这层就是干装配的） | 全部 |
| `tests` | 业务场景要验证什么 | 底层实现细节 | `testing`, `domain`, `ui` |

**验证方式**：任何一层的单元测试都不需要 mock 上层的东西——比如给 `core.reporting.failure_summary` 写单测完全不需要 pytest 环境或网络，因为它是纯函数；`ui.pages.LoginPage` 的单测只需要一个 Playwright Page，不需要真的启动整个测试框架。这就是"高内聚、低耦合"在这个项目里的具体体现，不是一句口号。

## 功能对照表

| 需求 | 实现方式 | 位置 |
|------|----------|------|
| 错误截图 | 内置`--screenshot=only-on-failure` + hook里额外全页截图并挂Allure | `testing/hooks/failure_capture.py` |
| 日志收集 | 按nodeid隔离的logger，捕获console/网络事件 | `core/logging/test_logger.py` |
| 报告生成 | pytest-html + Allure 双报告 | `pytest.ini` |
| 用例重跑 | pytest-rerunfailures，本地不开CI显式开，限定异常类型 | `pytest.ini` |
| 数据驱动 | JSON + parametrize，每条数据独立item | `core/data/loaders.py`, `tests/regression/test_login_data_driven.py` |
| 用例隔离 | xdist多进程 + 函数级page/context + 数据库独立事务 | `pytest.ini`, `testing/fixtures/` |
| 标签/POM | smoke/regression/p0标签；页面对象封装 | `pytest.ini`, `ui/pages/` |
| 失败通知/flaky清单 | 飞书webhook + 重跑清单落盘 | `core/notification/`, `core/reporting/` |
| API层/网络mock | httpx封装 + page.route模拟异常 | `domain/user/`, `tests/regression/test_network_mock.py` |
| CI/CD | 容器化运行，冒烟先行，产物上传，失败通知 | `.github/workflows/tests.yml`, `Dockerfile` |
| 数据库/接口断言 | 事务查询DB + pydantic schema校验响应 | `assertions/`, `domain/user/user_repository.py` |
| 视觉回归 | 像素级截图对比，固定环境避免误报 | `tests/regression/test_visual_regression.py`, `Dockerfile` |

## 关键设计取舍
- **conftest.py 只做插件聚合，不写逻辑**：新增一类 fixture/hook 时开新文件放进 `testing/fixtures` 或 `testing/hooks`，在 conftest.py 里加一行注册即可，根文件永远不会膨胀成"什么都塞"的状态。
- **core 层绝对不能 import domain 层**：这是保证"改业务规则不影响基础设施"的硬约束，如果哪天 `core/http/http_client.py` 里出现了 `from domain...` 的 import，说明分层被破坏了。
- **assertions 层保持通用，不硬编码业务表名**：`assert_db_field_equals` 接收 `table` 参数而不是写死 `"users"`，这样同一套断言逻辑能用在任何表上，不用为每个业务表复制一份断言函数。
- **ui 层零依赖 core/domain**：页面对象只表达"页面能做什么"，即使把整个后端接口体系重写一遍，`LoginPage` 也不用改一行。
- **testing 是唯一的"上帝层"**：其他所有层都不允许互相跨层依赖（比如 `assertions` 不该 import `domain`），只有 `testing/fixtures` 和 `testing/hooks` 可以同时认识所有层，因为它们的职责就是"装配"。
- **重跑策略只在 CI 显式开启**，用 `--only-rerun` 限定异常类型，避免把真实bug也悄悄重跑掩盖。
- **flaky 清单独立统计，不混入通过率**：重跑才过的用例本质上是不稳定的，需要被看见。
- **数据库/API造数据都配套自动清理**：`user_api`/`db_session` fixture 保证不留脏数据。
- **视觉回归依赖环境一致性**：用 Dockerfile 固定浏览器/系统版本，避免本地和CI渲染差异导致误报。

## 扩展建议
- 新增一个业务领域（比如"订单"）：在 `domain/order/` 下建 `order_api.py`/`order_repository.py`，在 `domain/models/order.py` 定义schema，参照 `domain/user/` 的写法即可，不需要动其他任何层。
- 如果项目变大，可以给每层加 `__init__.py` 显式声明公开接口（`__all__`），进一步约束"只能从包外部访问哪些符号"。
- `core` 层建议单独抽出去做成内部pip包，多个测试项目共享同一套基础设施，只有 `domain`/`ui`/`tests` 是每个项目特有的。
