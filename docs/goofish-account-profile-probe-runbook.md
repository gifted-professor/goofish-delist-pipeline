# 闲鱼账号 Profile 巡检说明

日期：2026-06-22  
用途：说明如何用 `goofish-account-profile-probe-template.json` 在不同登录账号或浏览器 Profile 下继续熟悉闲鱼页面。  
边界：本说明不保存真实账号、密码、验证码、二维码内容、cookie、token、localStorage、sessionStorage、订单、地址、聊天、商品标题、金额或经营数据。

## 核心原则

每个账号最好对应一个独立浏览器 Profile。你只需要告诉我本轮用哪个 `accountSlot` 和哪个 `browserProfileAlias`；真实登录、扫码、验证码、账号切换都由你在浏览器里完成，不把登录材料交给我。

## 推荐流程

1. 准备一个浏览器 Profile，例如 `profile-alias-only`。
2. 你在浏览器里登录目标闲鱼账号。
3. 用 `goofish-account-profile-probe-template.json` 建立本轮任务。
4. 先跑 D3 低风险 Live 页，再跑 D2 表单/外壳页，再跑 D1 高风险只读页。
5. D4 需要用户上下文的页面，只在你给出真实 URL 或上下文后检查。
6. D5 静态页只做静态解释，不为了补覆盖强开。
7. D6 外壳页只识别登录、iframe、下载或容器边界。
8. 每页只记录结构、字段名、tab、表头、按钮名、状态类别和停止点。

## 任务批次

| 批次 | 作用 | 是否可自动进入 | 停止边界 |
| --- | --- | --- | --- |
| D3 低风险 Live | 首页、搜索、频道、低风险数据壳 | 可以只读进入 | 收藏、联系、购买、私有值 |
| D2 表单和外壳 Live | 发布、反馈、消息壳、商品管理、站点/账号壳 | 可以只读进入 | 上传、保存、发布、发送、提交 |
| D1 高风险 Live | 订单、售后、财务、账号、安全、客服、推广 | 可以只读进入但必须脱敏 | 真实行值、导出、下载、权限、交易动作 |
| D4 需要用户上下文 | 商品详情、订单详情、聊天商品页 | 等用户给上下文 | 不猜参数，不读私有值 |
| D5 静态证据 | 静态模块、内部页、承接页 | 不主动进入 | 只解释静态信号 |
| D6 外壳边界 | 登录、iframe、容器 | 只识别边界 | 不进入嵌入动作或外部安装 |

## 每页结果格式

```text
accountSlot：account-01
browserProfileAlias：profile-alias-only
页面：<pageId>
状态：passed / stopped / skipped / needs-user-context / static-described / shell-described
当前页面态：S0-S10 类别
看到的锚点：结构锚点名称
看到的控件：按钮名、tab、字段名、表头
停止原因：命中的停止点
隐私检查：未记录真实账号、订单、地址、聊天、商品标题、金额、图片链接或登录材料
```

## 多账号轮换方式

| 做法 | 推荐度 | 原因 |
| --- | --- | --- |
| 一个账号一个浏览器 Profile | 推荐 | 登录态隔离清晰，便于回到同一账号继续看。 |
| 同一个 Profile 内频繁切号 | 不推荐 | 容易触发账号检查、站点选择、验证码或权限混淆。 |
| 把 cookie/token 当密钥给我 | 禁止 | 它们等同登录材料，不能进入文档或任务模板。 |
| 给我 `accountSlot` 占位名 | 推荐 | 能区分轮次，又不暴露真实账号身份。 |

## 什么时候需要你介入

- 页面要求扫码、验证码、实名、登录恢复或账号找回。
- 页面要求切换账号、切换站点、继续前往或确认授权。
- 页面要进入真实订单、真实商品、真实聊天或真实售后详情。
- 页面出现支付、退款、发货、投诉举证、导出、下载、上传、保存、提交、发送或发布。

## 和其他文件的关系

| 文件 | 作用 |
| --- | --- |
| `goofish-account-profile-probe-template.json` | 每个账号/Profile 的机器可读巡检任务模板。 |
| `goofish-page-verification-checklist.json` | 66 个页面的逐页验证标准。 |
| `goofish-page-verification-checklist.md` | 人工逐页验证清单。 |
| `goofish-page-ontology.json` | 每页统一画像。 |
| `goofish-safe-probe-protocol.md` | P0-P8 安全探测步骤。 |
| `goofish-cross-profile-coverage-ledger.json` | 多账号/Profile 覆盖差异台账。 |
| `goofish-cross-profile-coverage-runbook.md` | 多账号/Profile 覆盖对比说明。 |

结论：可以做多账号页面熟悉，但不要给我登录密钥。最稳的方式是你登录不同浏览器 Profile，我用占位 Profile 名和页面验证模板继续只读巡检。
