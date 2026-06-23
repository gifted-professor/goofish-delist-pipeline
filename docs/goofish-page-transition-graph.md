# 闲鱼页面流转图

日期：2026-06-22  
用途：把页面理解从“有哪些页面”推进到“页面之间怎么走、哪里能安全只读、哪里必须停”。  
边界：本图只记录页面 id、页面组、流转类别和停止点；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数字、图片链接或登录材料。

总索引：`goofish-master-index.md`  
页面清单：`goofish-page-manifest.json`  
覆盖状态：`goofish-live-coverage-status.json`  
深化队列：`goofish-page-deepening-queue.json`  
机器图：`goofish-page-transition-graph.json`

## 流转类别

| 类别 | 含义 |
| --- | --- |
| `SAFE_READ` | 可以打开并只读结构 |
| `READ_WITH_REDACTION` | 可以打开，但只写字段名、表头、按钮类别、状态类别 |
| `REQUIRES_USER_CONTEXT` | 需要用户给具体 URL、订单、商品、会话或账号上下文 |
| `STOP_BEFORE_ACTION` | 只能命名这个入口，不能触发 |
| `STATIC_ONLY` | 只按静态包/模块解释，不为了覆盖强行打开 |
| `SHELL_ONLY` | 只识别 shell/container，不进入嵌入或登录流程 |

## 主站公开发现流

```text
www.home -> www.search -> www.item
www.home -> www.machFeeds -> www.item
www.item -> www.personalOther
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| `www.home` -> `www.search` | `SAFE_READ` | 可看搜索框、筛选、卡片结构 |
| `www.home` -> `www.machFeeds` | `SAFE_READ` | 可看频道流结构 |
| `www.search` / `www.machFeeds` -> `www.item` | `REQUIRES_USER_CONTEXT` | 只在用户给商品 URL 时打开 |
| `www.item` -> `www.personalOther` | `REQUIRES_USER_CONTEXT` | 只在用户明确要看公开主页时打开 |
| `www.item` -> `www.imItem` / `www.createOrder` | `STOP_BEFORE_ACTION` | 联系、聊一聊、立即购买都停 |

## 主站账号与买家流

```text
www.personalSelf <-> www.collection
www.personalSelf <-> www.bought
www.personalSelf <-> www.account
www.bought -> www.orderDetail
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| 个人页、收藏页、买家订单页、账号页之间 | `READ_WITH_REDACTION` | 可读导航、tab、状态类别、按钮类别 |
| `www.bought` -> `www.orderDetail` | `REQUIRES_USER_CONTEXT` | 需要用户指定订单上下文 |
| `www.bought` -> 支付/确认/退款/评价 | `STOP_BEFORE_ACTION` | 不触发交易动作 |
| `www.account` -> 编辑资料/认证/切号 | `STOP_BEFORE_ACTION` | 不改账号状态 |

## 主站草稿、消息、登录流

```text
www.publish -> upload/save/publish
www.feedback -> upload/submit
www.im -> www.imItem
www.login -> scan/verification
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| `www.publish` / `www.feedback` -> 首页 | `SAFE_READ` | 可以返回公开入口 |
| `www.publish` -> 上传/保存/发布 | `STOP_BEFORE_ACTION` | 表单只读，不上传不保存 |
| `www.feedback` -> 上传/提交 | `STOP_BEFORE_ACTION` | 反馈只做草稿辅助 |
| `www.im` -> `www.imItem` | `REQUIRES_USER_CONTEXT` | 不打开具体私聊 |
| `www.login` -> 扫码/验证码 | `STOP_BEFORE_ACTION` | 用户本人处理登录 |

## 卖家数据与商品流

```text
seller.dataOverview -> seller.commodityData
seller.dataOverview -> seller.fanData
seller.dataOverview -> seller.customerServiceData
seller.goodsManage -> seller.itemPublish
seller.postTemplate -> seller.postTemplateCreate
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| 数据总览、商品数据、粉丝数据、客服数据之间 | `READ_WITH_REDACTION` | 只读字段名、指标名、筛选、表头 |
| 商品管理 -> 商品发布 | `READ_WITH_REDACTION` | 可看表单字段，不保存不发布 |
| 运费模板 -> 创建模板 | `READ_WITH_REDACTION` | 可看字段和校验，不保存模板 |
| 数据/商品页 -> 导出/下载/上传/发布/编辑/删除 | `STOP_BEFORE_ACTION` | 全部停 |

## 卖家交易与财务流

```text
seller.orderManage -> seller.refundManage
seller.orderManage -> seller.evaluationManage
seller.orderManage -> seller.complaintManage
seller.refundManage -> seller.refundAddress
seller.incomeBill -> seller.expenseBill -> seller.invoiceApply -> seller.basicInfo
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| 交易列表、退款、评价、投诉、退货地址之间 | `READ_WITH_REDACTION` | 只读状态、筛选、表头、操作列名 |
| 订单管理 -> 订单详情 | `REQUIRES_USER_CONTEXT` | 需要用户明确订单上下文 |
| 交易页 -> 发货/退款/联系/评价/举证/地址编辑 | `STOP_BEFORE_ACTION` | 不触发任何交易或售后动作 |
| 收入、支出、发票、主体信息之间 | `READ_WITH_REDACTION` | 只读 tab、日期、表头、按钮类别 |
| 财务页 -> 导出/下载/申请发票/修改主体 | `STOP_BEFORE_ACTION` | 不记录真实金额，不下载 |

## 卖家账号、安全、推广、消息流

```text
seller.subAccount -> seller.csDispatch
seller.notificationCenter -> seller.im -> seller.imDesktop
seller.im -> seller.imItem
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| 子账号 -> 客服分流 | `READ_WITH_REDACTION` | 只读权限字段和规则结构 |
| 通知中心 -> 消息外壳 | `READ_WITH_REDACTION` | 不打开敏感通知和具体私聊 |
| 卖家 IM -> 商品关联会话 | `REQUIRES_USER_CONTEXT` | 需要用户明确会话上下文 |
| 子账号/客服/安全/推广 -> 改权限/保存/申诉/投放 | `STOP_BEFORE_ACTION` | 不影响店铺经营状态 |

## 卖家 shell 与门禁流

```text
seller.selectSite -> seller.dataOverview
seller.noPermission -> seller.accountCheck
seller.iframe -> embeddedTarget
```

| 流转 | 类别 | 处理 |
| --- | --- | --- |
| 站点选择 -> 工作台首页 | `READ_WITH_REDACTION` | 不切换站点 |
| 无权限 -> 账号检查 | `SHELL_ONLY` | 只记录门禁类型 |
| iframe -> 嵌入目标 | `REQUIRES_USER_CONTEXT` | 不进入未知外部目标 |
| 下载/登录/站点/权限相关动作 | `STOP_BEFORE_ACTION` | 不下载、不安装、不扫码、不切号、不申请权限 |

## 静态页组

| 静态组 | 页面 |
| --- | --- |
| 交易结果/特殊交易包 | `www.paySuccess`, `www.yhbCreateOrder`, `www.yhbOrderDetail` |
| 发布变体 | `www.publishScene`, `www.publishEdit` |
| 登录/账号找回 | `www.loginRedirect`, `www.findAccount`, `www.selectAccount`, `www.loginValidation` |
| 内容/兼容/内部 | `www.commonVideo`, `www.commonVideoLayout`, `www.upgradeBrowser`, `www.playground`, `www.accountApi` |
| 卖家内部 | `seller.notificationApi`, `seller.playground` |

结论：后续页面熟悉应沿着 `SAFE_READ` 和 `READ_WITH_REDACTION` 继续，只把 `REQUIRES_USER_CONTEXT` 作为用户明确给 URL 后的只读入口，所有 `STOP_BEFORE_ACTION` 只命名、不触发。
