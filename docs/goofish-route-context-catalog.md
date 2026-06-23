# 闲鱼路由参数与上下文目录

日期：2026-06-22  
用途：把 66 个已知闲鱼页面的进入方式、参数形态、上下文要求和缺上下文时的处理方式统一整理。后续看到 URL/hash 时，先判断能否直接只读、是否需要用户给上下文、是否只能静态解释，或是否必须停在外壳边界。  
边界：只记录路由形态、参数名、参数风险和处理动作；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、cookie、token、localStorage 或 sessionStorage。

总索引：`goofish-master-index.md`  
配套机器目录：`goofish-route-context-catalog.json`  
配套路由索引：`goofish-route-inventory.md`  
配套页面分类器：`goofish-page-classifier-rules.json`  
配套 DOM 观察：`goofish-safe-dom-observation-schema.json` / `goofish-safe-dom-observation-guide.md`  
配套批次矩阵：`goofish-probe-batch-matrix.json` / `goofish-probe-batch-runbook.md`

## 覆盖总账

| 指标 | 数量 |
| --- | ---: |
| 页面总数 | 66 |
| 含参数或站点上下文的页面 | 47 |
| 参数槽位总数 | 57 |
| 需要用户上下文 | 8 |
| 静态/模块解释 | 16 |
| 外壳/容器边界 | 2 |

## 入口方式

| 入口方式 | 数量 | 处理 |
| --- | ---: | --- |
| `DIRECT_LIVE_READ_ONLY` | 39 | Known page can be opened under current profile for read-only structural observation. |
| `LIVE_ENTRY_BOUNDARY_READ` | 1 | Known entry can be opened only to identify download/app/client boundary; do not continue into external action. |
| `USER_CONTEXT_REQUIRED` | 8 | Requires user-provided URL or explicit business context; do not guess parameters. |
| `STATIC_EVIDENCE_ONLY` | 14 | Describe from static evidence; do not open merely for coverage. |
| `INTERNAL_OR_MODULE_ONLY` | 2 | Treat as module/resource path rather than user-facing page. |
| `SHELL_BOUNDARY_ONLY` | 2 | Identify shell/container/login/iframe boundary only. |

## 参数风险口径

| 规则 | 典型参数名 | 风险 | 处理 |
| --- | --- | --- | --- |
| `order-id-param` | `orderId`、`bizOrderId`、`tradeId` | `trade-private` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `item-id-param` | `itemId`、`item_id`、`auctionId` | `item-context` | `REQUIRES_USER_CONTEXT_IF_NOT_PUBLIC_DETAIL` |
| `user-param` | `userId`、`peerUserId`、`userNick`、`nick`、`sellerId`、`buyerId` | `account-identity` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `chat-param` | `conversationId`、`chatId`、`peerId`、`messageId` | `private-message` | `MESSAGE_SHELL_ONLY` |
| `address-logistics-param` | `addressId`、`logisticsId`、`trackingNo`、`mailNo` | `address-logistics` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `invoice-finance-param` | `invoiceId`、`billId`、`fundId`、`payId`、`alipay` | `finance-payment` | `STOP_BEFORE_ACTION` |
| `redirect-param` | `redirectURL`、`redirectUrl`、`returnUrl`、`targetUrl`、`url` | `external-or-embedded-target` | `SHELL_BOUNDARY_ONLY` |
| `scene-source-param` | `scene`、`spm`、`from`、`source` | `tracking-or-entry-context` | `READ_ROUTE_SHAPE_ONLY` |
| `search-query-param` | `q`、`keyword`、`query` | `public-search-context` | `DROP_VALUE_KEEP_INTENT_CATEGORY` |
| `entry-context-param` | `machId`、`publishTimes`、`categoryId` | `route-entry-context` | `READ_ROUTE_SHAPE_ONLY` |
| `seller-site-param` | `site` | `seller-site-context` | `USE_PROFILE_ALIAS_ONLY` |
| `unknown-param` | 未知参数 | `unknown-context` | `READ_ROUTE_SHAPE_ONLY_AND_TRIAGE` |

## 全局处理规则

- Never persist concrete query/hash parameter values.
- Do not construct order, user, chat, address, invoice, payment or redirect parameters.
- For seller pages, record only a site/profile alias, not the real account or store identity.
- Static and module routes are not coverage targets for live probing.
- Shell/container routes stop at boundary identification unless the embedded target is separately reviewed.

## 逐页上下文目录

| 页面 | 路由形态 | 入口方式 | 参数风险 | 可直接开 | 缺上下文处理 |
| --- | --- | --- | --- | --- | --- |
| `www.home` | `/` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.search` | `/search?q=...` | `DIRECT_LIVE_READ_ONLY` | `q`:search-query-param | 是 | allow neutral query or user keyword but drop value |
| `www.machFeeds` | `/mach-feeds?machId=...&publishTimes=...` | `DIRECT_LIVE_READ_ONLY` | `machId`:entry-context-param<br>`publishTimes`:entry-context-param | 是 | use visible link or route shape drop values |
| `www.item` | `/item?id=...&categoryId=...` | `USER_CONTEXT_REQUIRED` | `id`:item-id-param<br>`categoryId`:entry-context-param | 否 | stop and request user provided url or business context |
| `www.personalOther` | `/personal?userId=...` | `USER_CONTEXT_REQUIRED` | `userId`:user-param | 否 | stop and request user provided url or business context |
| `www.personalSelf` | `/personal` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.collection` | `/collection` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.bought` | `/bought` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.orderDetail` | `/order-detail?orderId=...` | `USER_CONTEXT_REQUIRED` | `orderId`:order-id-param | 否 | stop and request user provided url or business context |
| `www.createOrder` | `/create-order?itemId=...` | `USER_CONTEXT_REQUIRED` | `itemId`:item-id-param | 否 | stop and request user provided url or business context |
| `www.paySuccess` | `/pay-success?orderId=...&itemId=...` | `STATIC_EVIDENCE_ONLY` | `orderId`:order-id-param<br>`itemId`:item-id-param | 否 | do not open for coverage describe static signal |
| `www.publish` | `/publish` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.publishScene` | `/publish?scene=xyPcMainPublish` | `STATIC_EVIDENCE_ONLY` | `scene`:scene-source-param | 否 | do not open for coverage describe static signal |
| `www.publishEdit` | `/publish?scene=xyPcMainPublish&itemId=...` | `STATIC_EVIDENCE_ONLY` | `scene`:scene-source-param<br>`itemId`:item-id-param | 否 | do not open for coverage describe static signal |
| `www.im` | `/im` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.imItem` | `/im?itemId=...&peerUserId=...` | `USER_CONTEXT_REQUIRED` | `itemId`:item-id-param<br>`peerUserId`:user-param | 否 | stop and request user provided url or business context |
| `www.account` | `/account` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.accountApi` | `/account/api` | `INTERNAL_OR_MODULE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.feedback` | `/feedback?from=...` | `DIRECT_LIVE_READ_ONLY` | `from`:scene-source-param | 是 | open read structure only |
| `www.changelog` | `/changelog` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.login` | `/login` | `DIRECT_LIVE_READ_ONLY` | 无 | 是 | open read structure only |
| `www.loginRedirect` | `/login?spm=...&redirectURL=...` | `STATIC_EVIDENCE_ONLY` | `spm`:scene-source-param<br>`redirectURL`:redirect-param | 否 | do not open for coverage describe static signal |
| `www.findAccount` | `/find-account` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.selectAccount` | `/select-account` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.loginValidation` | `/login-validation` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.commonVideo` | `/common-video` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.commonVideoLayout` | `/common-video/layout` | `INTERNAL_OR_MODULE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.upgradeBrowser` | `/upgrade-browser` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.playground` | `/playground` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.yhbCreateOrder` | `create-order-yhb package` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `www.yhbOrderDetail` | `order-detail-yhb package` | `STATIC_EVIDENCE_ONLY` | 无 | 否 | do not open for coverage describe static signal |
| `seller.dataOverview` | `#/seller-data/data` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.commodityData` | `#/seller-data/commodity` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.fanData` | `#/seller-data/fanData` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.customerServiceData` | `#/seller-data/customerService` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.itemPublish` | `#/seller-item/publish` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.goodsManage` | `#/seller-item/goods-manage` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.postTemplate` | `#/seller-item/post-temple` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.postTemplateCreate` | `#/seller-item/post-temple/create` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.orderManage` | `#/seller-trade/order-manage` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.orderDetail` | `#/seller-trade/order-manage/order-detail?orderId=...` | `USER_CONTEXT_REQUIRED` | `site`:seller-site-param<br>`orderId`:order-id-param | 否 | stop and request user provided url or business context |
| `seller.refundManage` | `#/seller-trade/refund-manage` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.evaluationManage` | `#/seller-trade/evaluation-manage` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.complaintManage` | `#/seller-trade/complaint-manage` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.refundAddress` | `#/seller-trade/refund-address` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.incomeBill` | `#/seller-finance/income-bill` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.expenseBill` | `#/seller-finance/expense-bill` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.invoiceApply` | `#/seller-finance/invoice-apply` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.basicInfo` | `#/seller-finance/basic-info` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.subAccount` | `#/seller-account/sub-account` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.csDispatch` | `#/im-cs-dispatch/customer-routing-service` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.securityCenter` | `#/seller-sc/home` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.adHome` | `#/seller-ad/home` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.notificationCenter` | `#/notification-center` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.notificationApi` | `#/notification-center/api*` | `STATIC_EVIDENCE_ONLY` | `site`:seller-site-param | 否 | do not open for coverage describe static signal |
| `seller.im` | `#/im` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.imItem` | `#/im?itemId=...` | `USER_CONTEXT_REQUIRED` | `site`:seller-site-param<br>`itemId`:item-id-param | 否 | stop and request user provided url or business context |
| `seller.imDesktop` | `#/im-desktop` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.download` | `#/download` | `LIVE_ENTRY_BOUNDARY_READ` | `site`:seller-site-param | 是 | identify download or client entry only do not download or install |
| `seller.selectSite` | `#/select-site` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.accountCheck` | `#/account-check` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.accountCheckUser` | `#/account-check?userNick=...` | `USER_CONTEXT_REQUIRED` | `site`:seller-site-param<br>`userNick`:user-param | 否 | stop and request user provided url or business context |
| `seller.login` | `#/login` | `SHELL_BOUNDARY_ONLY` | `site`:seller-site-param | 否 | identify shell only do not enter target |
| `seller.noPermission` | `#/no-permission` | `DIRECT_LIVE_READ_ONLY` | `site`:seller-site-param | 是 | open read structure only |
| `seller.iframe` | `#/iframe?url=...` | `SHELL_BOUNDARY_ONLY` | `site`:seller-site-param<br>`url`:redirect-param | 否 | identify shell only do not enter target |
| `seller.playground` | `#/playground` | `STATIC_EVIDENCE_ONLY` | `site`:seller-site-param | 否 | do not open for coverage describe static signal |

## 需要用户上下文的页面

| 页面 | 路由形态 | 需要的上下文 | 参数风险 | 停止点 |
| --- | --- | --- | --- | --- |
| `www.item` | `/item?id=...&categoryId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `id`:item-id-param<br>`categoryId`:entry-context-param | collect、chat、buy now、downshelf、delete |
| `www.personalOther` | `/personal?userId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `userId`:user-param | follow、contact、purchase |
| `www.orderDetail` | `/order-detail?orderId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `orderId`:order-id-param | any order-state change、real order value logging |
| `www.createOrder` | `/create-order?itemId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `itemId`:item-id-param | submit order、pay、change address、bind account、verify identity |
| `www.imItem` | `/im?itemId=...&peerUserId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `itemId`:item-id-param<br>`peerUserId`:user-param | read specific conversation、send |
| `seller.orderDetail` | `#/seller-trade/order-manage/order-detail?orderId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `site`:seller-site-param<br>`orderId`:order-id-param | guess order id、order action |
| `seller.imItem` | `#/im?itemId=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `site`:seller-site-param<br>`itemId`:item-id-param | guess parameter、send |
| `seller.accountCheckUser` | `#/account-check?userNick=...` | user-provided-url、user-described-current-business-context、visible-link-after-user-confirmation | `site`:seller-site-param<br>`userNick`:user-param | guess real account name |

## 静态、模块和外壳页面

| 页面 | 路由形态 | 入口方式 | 处理 |
| --- | --- | --- | --- |
| `www.paySuccess` | `/pay-success?orderId=...&itemId=...` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.publishScene` | `/publish?scene=xyPcMainPublish` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.publishEdit` | `/publish?scene=xyPcMainPublish&itemId=...` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.accountApi` | `/account/api` | `INTERNAL_OR_MODULE_ONLY` | do not open for coverage describe static signal |
| `www.loginRedirect` | `/login?spm=...&redirectURL=...` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.findAccount` | `/find-account` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.selectAccount` | `/select-account` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.loginValidation` | `/login-validation` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.commonVideo` | `/common-video` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.commonVideoLayout` | `/common-video/layout` | `INTERNAL_OR_MODULE_ONLY` | do not open for coverage describe static signal |
| `www.upgradeBrowser` | `/upgrade-browser` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.playground` | `/playground` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.yhbCreateOrder` | `create-order-yhb package` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `www.yhbOrderDetail` | `order-detail-yhb package` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `seller.notificationApi` | `#/notification-center/api*` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |
| `seller.download` | `#/download` | `LIVE_ENTRY_BOUNDARY_READ` | identify download or client entry only do not download or install |
| `seller.login` | `#/login` | `SHELL_BOUNDARY_ONLY` | identify shell only do not enter target |
| `seller.iframe` | `#/iframe?url=...` | `SHELL_BOUNDARY_ONLY` | identify shell only do not enter target |
| `seller.playground` | `#/playground` | `STATIC_EVIDENCE_ONLY` | do not open for coverage describe static signal |

## 单个 URL 判定顺序

1. 先把 URL/hash 归一成 `routeShapeForLogging`，去掉真实参数值。
2. 用 `goofish-route-context-catalog.json` 命中 `pageId`，读取 `entryMode` 和 `contextRequirement`。
3. 若 `entryMode=USER_CONTEXT_REQUIRED`，只接受用户给出的 URL 或明确业务上下文，不拼参数。
4. 若参数命中订单、用户、会话、地址物流、发票财务、外部跳转，记录参数名和风险后停。
5. 若是搜索、频道、场景、站点参数，只保留参数名和类别，不保留值。
6. 若是 Static、Internal、Shell 页面，不为覆盖率强行打开；只写静态信号或外壳状态。

## 最小输出格式

```text
pageId: <known id or UNKNOWN_PAGE>
routeShape: <path/hash with parameter names only>
entryMode: DIRECT_LIVE_READ_ONLY / USER_CONTEXT_REQUIRED / STATIC_EVIDENCE_ONLY / SHELL_BOUNDARY_ONLY
parameters: parameter names + risk rule ids only
contextRequirement: one catalog value
missingContextAction: stop / static describe / shell identify / read structure
privacy: no concrete parameter values, no account/order/address/chat/item/amount/login material
```

结论：这份目录把“页面”和“上下文”分开了。页面可以被理解，参数值不能被保存；能直接只读的页面继续按批次跑，需要上下文的页面等用户给目标，静态和外壳页面只解释边界。
