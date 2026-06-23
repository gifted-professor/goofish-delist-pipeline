# 闲鱼安全页面探测规程

日期：2026-06-22  
用途：把“只读熟悉页面”落成可执行的探测协议。后续人工或脚本逐页巡检时，按本规程决定进入前检查、页面稳定判断、可读取字段、停止条件和输出格式。  
边界：本规程只允许页面级只读探测和草稿辅助；不保存真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、验证码、cookie、token 或本地存储。

总索引：`goofish-master-index.md`  
配套统一页面画像：`goofish-page-ontology.json` / `goofish-page-ontology-guide.md`  
配套逐页档案：`goofish-page-dossiers.md` / `goofish-page-dossier-index.json`  
配套未知页分类：`goofish-page-classifier-rules.json` / `goofish-unknown-page-triage.md`  
配套路由上下文：`goofish-route-context-catalog.json` / `goofish-route-context-catalog.md`  
配套页面变更：`goofish-page-change-sentinel.json` / `goofish-page-change-sentinel.md`  
配套可见文案：`goofish-visible-label-lexicon.json` / `goofish-visible-label-lexicon.md`  
配套 DOM 观察：`goofish-safe-dom-observation-schema.json` / `goofish-safe-dom-observation-guide.md`  
配套巡检批次：`goofish-probe-batch-matrix.json` / `goofish-probe-batch-runbook.md`  
配套逐页验证：`goofish-page-verification-checklist.json` / `goofish-page-verification-checklist.md`  
配套账号 Profile 巡检：`goofish-account-profile-probe-template.json` / `goofish-account-profile-probe-runbook.md`  
配套跨 Profile 覆盖：`goofish-cross-profile-coverage-ledger.json` / `goofish-cross-profile-coverage-runbook.md`  
配套页面清单：`goofish-page-manifest.json`  
配套机器策略：`goofish-probe-policy.json`  
配套登录实测：`goofish-login-session-smoke-test.md`  
配套 Live 覆盖：`goofish-live-coverage-matrix.md`  
配套覆盖状态：`goofish-live-coverage-status.json`  
配套缺口登记：`goofish-coverage-gap-register.md`  
配套深化队列：`goofish-page-deepening-queue.json` / `goofish-page-deepening-queue.md`  
配套流转图：`goofish-page-transition-graph.json` / `goofish-page-transition-graph.md`  
配套动作规则：`goofish-action-gate-rules.json` / `goofish-action-execution-guard.md`  
配套状态规则：`goofish-state-modal-rules.json` / `goofish-state-modal-handling.md`  
配套导航定位：`goofish-navigation-selector-guide.md`  
配套状态弹窗：`goofish-page-state-modal-inventory.md`  
配套动作门禁：`goofish-action-gate-matrix.md`  
配套字段清单：`goofish-page-field-inventory.md`  
配套主站图谱：`goofish-www-operational-map.md`  
配套卖家图谱：`goofish-seller-workbench-operational-map.md`

## 探测总原则

1. 先识别页面，不先点击按钮。
2. 先读 URL/path/hash，再读页面标题、tab、表头、卡片结构、输入区或空态。
3. 只记录字段名、按钮名、状态类别、控件类别、页面族和停止点。
4. 任何写入、提交、保存、发送、上传、下载、导出、支付、发货、退款、评价、认证、切号、权限变更都停。
5. 遇到登录、验证码、二维码、实名、支付、APP 承接、无权限、确认弹窗，停下并记录状态类别。
6. 登录后冒烟观察只记录 Profile 别名和页面状态，不记录页面标题里的账号/店铺/商品身份。

## 探测阶段

| 阶段 | 目标 | 可做 | 停止条件 |
| --- | --- | --- | --- |
| P0 Profile 检查 | 确认当前浏览器 Profile 和账号别名 | 只读判断是否登录、是否进入目标域名 | 需要扫码/验证码/切号 |
| P1 路由识别 | 判断是主站、卖家工作台、H5/App 承接或未知页 | 读 URL/path/hash、参数形态 | 参数含真实订单/账号/地址且非用户明确提供 |
| P2 页面稳定 | 等待页面锚点或空态出现 | 等标题、tab、表头、商品卡、订单卡、输入区、空态 | 长时间 loading、网络失败、权限失败 |
| P3 证据分级 | 对齐 Live + Static、Static Only、Deep/Param、Shell/Container | 查 manifest 和证据覆盖 | Static Only/Deep/Param 被当成可操作页 |
| P4 字段读取 | 只读字段名、按钮名、结构 | 摘要字段类别和控件类别 | 需要读取真实行值、聊天正文、订单详情值 |
| P5 动作过滤 | 判断页面上按钮和接口动作等级 | 只标 G0-G4，不默认执行 | G3/G4 动作出现 |
| P6 状态处理 | 识别弹窗、二维码、登录、无权限、确认框 | 记录状态类别 | 弹窗确认、扫码、上传、下载、提交 |
| P7 输出摘要 | 生成脱敏页面理解结果 | 写路由、层级、证据、锚点、可读项、停止点 | 输出真实个人/交易/经营内容 |
| P8 退出/复位 | 结束当前页探测 | 不关闭登录态，不清理用户数据 | 需要改变账号或业务状态 |

## 页面族探测模板

| 页面族 | 进入方式 | 等待锚点 | 可读 | 禁止 |
| --- | --- | --- | --- | --- |
| 公开发现 | `/`、`/search`、`/mach-feeds` | 搜索框、排序、商品卡、频道流 | 筛选控件、卡片结构、分页结构 | 收藏、联系、购买 |
| 商品详情 | `/item?id=...` | 价格区、保障、卖家卡、按钮区 | 商品字段名、保障类别、按钮名 | 收藏、聊一聊、立即购买 |
| 公开主页 | `/personal?userId=...` | 主页区、信用区、宝贝列表 | 公开结构、tab、入口关系 | 关注、联系、购买 |
| 买家账号 | `/personal`、`/collection`、`/account` | 左侧导航、tab、模块名 | 字段名、状态类别 | 编辑资料、通知开关、切号 |
| 买家交易 | `/bought`、`/order-detail`、`/create-order` | 订单 tab、字段名、物流/支付模块 | 状态节点名、字段名、按钮名 | 下单、支付、确认收货、退款、评价 |
| 草稿输入 | `/publish`、`/feedback` | 表单字段、校验提示、文本框 | 表单结构、草稿建议 | 上传、保存、发布、提交 |
| 消息 | `/im`、`#/im` | 空态/会话框架、输入区、工具栏 | 框架、工具按钮、草稿文本 | 读具体私聊、发送、发文件 |
| 卖家数据 | `#/seller-data/*` | 日期、指标卡、表头、图表 | 指标字段名、筛选项 | 记录真实数字、导出 |
| 卖家商品 | `#/seller-item/*` | 状态 tab、表头、发布字段 | 表头、筛选、草稿字段 | 保存、发布、上下架、删除 |
| 卖家交易 | `#/seller-trade/*` | 订单/退款/评价/投诉 tab、表头 | 状态类别、字段名、操作列名 | 发货、退款、投诉举证、评价 |
| 卖家财务 | `#/seller-finance/*` | 财务 tab、日期、表头、导出按钮 | 字段名、tab、按钮名 | 导出、下载、申请发票、修改主体资料 |
| 权限/账号 | `/login`、`#/select-site`、`#/account-check` | 登录、站点、账号检查、无权限 | 门禁类型、按钮名 | 扫码、验证码、切号、继续前往 |
| 容器/内部 | `/playground`、`#/iframe`、`#/download` | 容器来源、下载入口、测试标识 | 容器类型、风险边界 | 访问实验、调用 API、下载安装 |

## 安全等待规则

| 情况 | 等待方式 | 失败处理 |
| --- | --- | --- |
| 商品流/瀑布流 | 等 2-5 秒，滚动一次，再看商品卡或空态 | 仍无内容则记录加载失败 |
| 工作台 hash | 等左侧菜单、顶部区、目标表头或空态 | 未进入目标页则记录门禁或路由失败 |
| 表格页 | 等 tab、筛选区、表头、分页任一稳定锚点 | 不读取真实行值 |
| 表单页 | 等字段名、输入框、校验提示 | 不上传、不保存 |
| 消息页 | 等空态、会话框架或输入区 | 不打开具体会话，除非用户明确要求 |
| 登录/二维码 | 等登录页或弹层可见 | 停下让用户处理，不保存二维码 |
| 确认弹窗 | 等标题、取消/确认按钮可见 | 不点确认，记录弹窗类别 |

## 输出格式

```text
页面：<route/hash>
页面族：<public-discovery / buyer-trade / seller-finance ...>
层级：M0-M6
证据：Live + Static / Static Only / Deep/Param / Shell/Container
状态：正常 / 加载 / 空态 / 登录 / 无权限 / 弹窗 / 高风险业务态
锚点：标题、tab、表头、卡片、输入区、空态之一
可读：字段名、按钮名、tab、表头、状态类别
停止点：上传 / 保存 / 发布 / 发送 / 支付 / 发货 / 退款 / 导出 / 权限 / 认证
隐私：未记录真实账号、订单、地址、聊天、商品标题、金额或登录材料
```

## 红线清单

- 不调用接口替代页面操作。
- 不复制或保存 cookie、token、localStorage、sessionStorage、密码、验证码。
- 不为补覆盖制造订单、支付、退款、发货、投诉、评价、发票、认证或投放状态。
- 不把深层参数页当普通页面乱拼参数。
- 不把 H5/App 承接页当 PC 可操作页面。
- 不把页脚 SEO、埋点字符串、资源 URL、第三方库字符串当业务页面。

结论：本规程把页面理解压成一套可执行的安全探测顺序。后续无论人工还是脚本，只要按 P0-P8 执行，就能继续熟悉页面结构，同时避免误触账号、交易、消息、财务、权限和身份流程。
