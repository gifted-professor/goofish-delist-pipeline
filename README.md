# goofish

闲鱼页面理解 + 商品指标只读采集。根目录已整理为三个子目录。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `docs/` | 闲鱼页面理解资料（43 份 Markdown + 19 份 JSON）。入口先看 `docs/goofish-readme-first.md`，全量索引看 `docs/goofish-master-index.md`。 |
| `scripts/` | 商品指标采集脚本：`goofish-collect-v3.py`（最新）、`goofish-collect-v2.py`。通过 Chrome CDP（端口 9221）连接已登录 Profile 只读采集。 |
| `data/` | 采集输出（CSV / JSON），脚本自动写入此目录。 |

运行时隐藏文件留在根目录：`.goofish-browser-profile*`（浏览器 Profile）、`.goofish-checkpoint-*.json`（断点）、`.goofish-collect.log`（日志）。

## 安全边界

只读观察页面结构、字段名、按钮名、状态类别；不记录真实账号、订单、地址、聊天、商品标题、金额、图片链接或登录材料。任何支付/发货/退款/发布/发送/导出等动作都停。详见 `docs/goofish-readme-first.md`。
