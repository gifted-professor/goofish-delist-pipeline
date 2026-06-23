# 闲鱼页面深化队列

日期：2026-06-22  
用途：把 66 个页面按下一步深化方式排队，避免“为了更细”误触交易、消息、财务、权限或账号动作。  
边界：本队列只安排字段名、表头、tab、按钮类别、状态类别、空态和容器边界观察；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数字、图片链接或登录材料。

总索引：`goofish-master-index.md`  
页面清单：`goofish-page-manifest.json`  
覆盖状态：`goofish-live-coverage-status.json`  
机器队列：`goofish-page-deepening-queue.json`  
动作门禁：`goofish-action-gate-matrix.md`

## 队列总览

| 队列 | 数量 | 下一步 |
| --- | ---: | --- |
| D1 高风险 Live 页 | 18 | 只读表头、状态、按钮类别、弹窗类别 |
| D2 表单/外壳 Live 页 | 14 | 只读字段名、输入类型、校验提示、空态、外壳锚点 |
| D3 低风险 Live 页 | 8 | 只读导航、筛选、公开卡片结构、路由形态 |
| D4 需要用户上下文 | 8 | 等用户给 URL 或业务上下文，不猜参数 |
| D5 只能静态解释 | 16 | 看静态包、接口对照和边界，不强行 live |
| D6 Shell/Container 边界 | 2 | 只识别容器类型，停在嵌入/登录边界 |

## D1 高风险 Live 页

这些页面已经能打开，但动作密度或业务影响高。下一步只做“字段/表头/状态/按钮类别”的深入，不打开行详情。

| 页面组 | 页面 id | 观察重点 | 停止点 |
| --- | --- | --- | --- |
| 买家交易/账号 | `www.bought`, `www.account` | 订单状态、账号设置项、按钮类别 | 支付、确认、退款、评价、资料修改、认证 |
| 卖家交易 | `seller.orderManage`, `seller.refundManage`, `seller.evaluationManage`, `seller.complaintManage`, `seller.refundAddress` | 表头、筛选项、状态类别、操作列名 | 发货、退款、联系、评价、投诉举证、地址编辑 |
| 卖家财务 | `seller.incomeBill`, `seller.expenseBill`, `seller.invoiceApply`, `seller.basicInfo` | tab、日期控件、表头、按钮类别 | 导出、下载、申请发票、修改主体资料 |
| 权限/安全/推广/消息 | `seller.subAccount`, `seller.csDispatch`, `seller.securityCenter`, `seller.adHome`, `seller.notificationCenter`, `seller.im`, `seller.imDesktop` | 权限字段、违规状态、推广入口、消息外壳 | 改权限、申诉、付费投放、打开私聊、发送 |

## D2 表单/外壳 Live 页

这些页面适合继续看字段和校验，但任何提交型动作都停。

| 页面组 | 页面 id | 观察重点 | 停止点 |
| --- | --- | --- | --- |
| 主站草稿/消息/登录 | `www.publish`, `www.feedback`, `www.im`, `www.login` | 表单字段、文件输入、文本域、消息外壳、登录容器 | 上传、发布、提交、发送、扫码、验证码 |
| 卖家商品/数据表 | `seller.customerServiceData`, `seller.itemPublish`, `seller.goodsManage`, `seller.postTemplate`, `seller.postTemplateCreate`, `seller.commodityData` | 输入类型、表格结构、空态、模板字段、商品筛选 | 上传、保存、发布、创建、编辑、下载 |
| 工作台门禁/下载 | `seller.download`, `seller.selectSite`, `seller.accountCheck`, `seller.noPermission` | 外壳锚点、门禁类型、按钮类别 | 下载、安装、切站点、切号、申请权限 |

## D3 低风险 Live 页

这些页面可以继续看公开结构，但仍不写真实商品或账号身份。

| 页面组 | 页面 id | 观察重点 | 停止点 |
| --- | --- | --- | --- |
| 主站公开/账号列表 | `www.home`, `www.search`, `www.machFeeds`, `www.personalSelf`, `www.collection`, `www.changelog` | 导航、筛选、公开卡片结构、内容块 | 收藏、联系、购买、登录切换 |
| 卖家数据外壳 | `seller.dataOverview`, `seller.fanData` | 日期/指标字段名、图表类别、筛选项 | 记录真实指标、导出、下载 |

## D4 需要用户上下文

这些页面必须等用户给具体 URL 或明确业务目标。没有上下文时，不拼参数、不造订单、不打开私聊。

| 页面 id | 需要什么 | 为什么 |
| --- | --- | --- |
| `www.item` | 公开商品 URL | 商品详情包含购买、联系、收藏边界 |
| `www.personalOther` | 公开主页 URL | 公开主页会暴露用户身份 |
| `www.orderDetail` | 明确订单上下文 | 订单详情含交易、地址、物流和金额 |
| `www.createOrder` | 明确下单前核对目标 | 接近提交订单和支付 |
| `www.imItem` | 明确会话上下文 | 私聊和商品关联高敏 |
| `seller.orderDetail` | 卖家订单上下文 | 含买家、物流、钱款和高影响操作 |
| `seller.imItem` | 卖家会话上下文 | 私聊高敏 |
| `seller.accountCheckUser` | 明确账号检查目标 | 涉及账号身份边界 |

## D5 只能静态解释

这些页面只做规则和风险解释，不追求 live 打开。

| 类型 | 页面 id |
| --- | --- |
| 交易结果/特殊交易包 | `www.paySuccess`, `www.yhbCreateOrder`, `www.yhbOrderDetail` |
| 发布变体 | `www.publishScene`, `www.publishEdit` |
| 登录/账号找回 | `www.loginRedirect`, `www.findAccount`, `www.selectAccount`, `www.loginValidation` |
| 内容/兼容/实验 | `www.commonVideo`, `www.upgradeBrowser`, `www.playground`, `seller.playground` |
| 内部模块/API | `www.accountApi`, `www.commonVideoLayout`, `seller.notificationApi` |

## D6 Shell/Container 边界

| 页面 id | 观察重点 | 停止点 |
| --- | --- | --- |
| `seller.login` | 登录 shell 类型 | 扫码、验证码、切号 |
| `seller.iframe` | iframe 容器类型、嵌入来源形态 | 进入外部目标、调用嵌入页动作 |

## 执行口径

1. 先从 D1 做高风险页面“字段/按钮类别”精读，因为这些页面最容易误触。
2. 再做 D2 表单/外壳页，补输入类型、校验提示和空态。
3. D3 只做公开结构增强，不记录身份值。
4. D4 等用户给 URL 或明确业务目标。
5. D5/D6 只补边界和规则，不追求 live 覆盖。

结论：页面深化不再按“想看哪里点哪里”，而是按 D1-D6 队列推进。这样能继续变细，同时把真实账号、交易、消息、财务和权限状态留在安全边界内。
