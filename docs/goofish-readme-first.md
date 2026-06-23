# 闲鱼页面理解先看我

日期：2026-06-22  
用途：给本轮闲鱼页面熟悉工作的最短入口。文档很多时，先看这份，再决定打开哪一份细文档。  
边界：这里只做导航和结论摘要；不记录真实账号、店铺、订单、地址、聊天、商品标题、金额、经营数字、图片链接、二维码内容、验证码、cookie、token 或本地存储。

## 先读哪几份

| 你要做什么 | 先看 |
| --- | --- |
| 快速知道当前做到哪 | `goofish-closeout-summary.md` |
| 判断是不是已经完全完成 | `goofish-completion-audit.md` |
| 找全部文档入口 | `goofish-master-index.md` |
| 看 66 个页面总画像 | `goofish-page-ontology.json` / `goofish-page-ontology-guide.md` |
| 查每页人工说明 | `goofish-page-dossiers.md` |
| 跑多账号/Profile 巡检 | `goofish-account-profile-probe-runbook.md` |
| 记录每次巡检结果 | `goofish-observation-result-runbook.md` |
| 读自己发布商品的想要/浏览数 | `goofish-item-metrics-readiness.md` |

## 当前一句话结论

当前已经把可识别的闲鱼 PC 主站和卖家工作台 66 个页面入口系统化：40 页已在当前登录 Profile 下 live 只读观察，8 页需要真实用户上下文，16 页只能静态解释，2 页是 shell/container 边界。

这足够进入实用小闭环：多 Profile 覆盖对比、页面只读巡检、自发布商品详情页指标读取。  
这还不能证明“全闲鱼所有隐藏/灰度/真实业务状态页面都完整实测”。

## 最安全的继续方式

1. 不交密码、验证码、cookie、token 或本地存储。
2. 每个账号用一个独立浏览器 Profile。
3. 用户本人完成登录。
4. 脚本只读页面结构、字段名、按钮名、状态类别和停止原因。
5. 任何支付、发货、退款、发布、保存、发送、导出、下载、上传、删除、认证、切号都停。

## 商品指标读取短结论

- “我发布的”列表卡片层没有稳定显示“想要/浏览数”。
- 自己发布商品的详情页能看到相关信号。
- 默认只记录字段是否可见；具体数字需要用户单独授权。
- 详情页有“我想要/购买/聊一聊/编辑/下架/删除”等动作边界，只能看，不能点。

## 交给下一个执行者的最短任务

```text
读取 goofish-readme-first.md。
如需全局理解，读 goofish-closeout-summary.md 和 goofish-completion-audit.md。
如需自动化规则，读 goofish-page-ontology.json、goofish-probe-policy.json、goofish-action-gate-rules.json。
如需多账号，按 goofish-account-profile-probe-runbook.md 建独立 Profile。
如需商品想要/浏览数，按 goofish-item-metrics-readiness.md 从商品详情页只读读取。
不要记录真实账号、订单、地址、聊天、商品标题、金额、图片链接或登录材料。
```

## 当前文档体量

本轮输出是一组页面理解资料，而不是一个单一脚本。若只想接着做业务，优先使用上述 5 到 8 份入口文档；其他文档作为细节字典和风险规则。
