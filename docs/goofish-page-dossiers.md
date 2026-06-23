# 闲鱼逐页档案

日期：2026-06-22  
用途：把 66 个闲鱼页面展开成逐页说明，方便人工快速理解“这页是什么、打开看什么、怎样算看懂、哪里必须停”。  
边界：只记录页面结构、路由形状、页面族、风险等级、状态类别、控件类别、字段名、表头、按钮名、停止点和验证证据；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

## 读法

1. 先按 `id` 或 `routePattern` 找页面。
2. 看“风险摘要”决定是否能打开，还是只能静态解释或等用户上下文。
3. 看“等待锚点”判断页面是否加载到可读结构。
4. 看“可读结构”和“允许动作”决定能记录什么。
5. 看“停止点”和“停止状态”，命中就停。
6. 看“通过证据”，满足后才把该页记为本轮已理解。

## 总览

| 页面 | 路由形状 | 页面族 | 风险摘要 | 运行方式 |
| --- | --- | --- | --- | --- |
| [`www.home`](#www-home) | `/` | `public-discovery` | `M0 / R0 / observed-live / SAFE_READ / G0` | `LIVE_READ_ONLY` |
| [`www.search`](#www-search) | `/search?q=...` | `public-discovery` | `M0 / R0 / observed-live / SAFE_READ / G0` | `LIVE_READ_ONLY` |
| [`www.machFeeds`](#www-machfeeds) | `/mach-feeds?machId=...&publishTimes=...` | `public-discovery` | `M0 / R0 / observed-live / SAFE_READ / G0` | `LIVE_READ_ONLY` |
| [`www.item`](#www-item) | `/item?id=...&categoryId=...` | `item-detail` | `M0/M3 / R0/R3 / requires-user-context / REQUIRES_USER_CONTEXT / G1` | `WAIT_FOR_USER_CONTEXT` |
| [`www.personalOther`](#www-personalother) | `/personal?userId=...` | `public-profile` | `M0/M1 / R0/R3 / requires-user-context / REQUIRES_USER_CONTEXT / G1` | `WAIT_FOR_USER_CONTEXT` |
| [`www.personalSelf`](#www-personalself) | `/personal` | `buyer-account` | `M1/M2 / R1/R3 / observed-live / SAFE_READ / G1` | `LIVE_READ_ONLY` |
| [`www.collection`](#www-collection) | `/collection` | `buyer-account` | `M1/M3 / R1/R3 / observed-live / SAFE_READ / G1` | `LIVE_READ_ONLY` |
| [`www.bought`](#www-bought) | `/bought` | `buyer-trade` | `M1/M3 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`www.orderDetail`](#www-orderdetail) | `/order-detail?orderId=...` | `buyer-trade` | `M3 / R1/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1` | `WAIT_FOR_USER_CONTEXT` |
| [`www.createOrder`](#www-createorder) | `/create-order?itemId=...` | `buyer-trade` | `M3/M5 / R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1` | `WAIT_FOR_USER_CONTEXT` |
| [`www.paySuccess`](#www-paysuccess) | `/pay-success?orderId=...&itemId=...` | `buyer-trade` | `M3 / R4 / static-only / STATIC_ONLY / G1` | `STATIC_EVIDENCE_ONLY` |
| [`www.publish`](#www-publish) | `/publish` | `draft-input` | `M2/M3 / R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`www.publishScene`](#www-publishscene) | `/publish?scene=xyPcMainPublish` | `draft-input` | `M2/M3 / R2/R3 / static-only / STATIC_ONLY / G2` | `STATIC_EVIDENCE_ONLY` |
| [`www.publishEdit`](#www-publishedit) | `/publish?scene=xyPcMainPublish&itemId=...` | `draft-input` | `M2/M3 / R3/R4 / static-only / STATIC_ONLY / G2` | `STATIC_EVIDENCE_ONLY` |
| [`www.im`](#www-im) | `/im` | `message` | `M1/M2/M3 / R1/R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`www.imItem`](#www-imitem) | `/im?itemId=...&peerUserId=...` | `message` | `M1/M3 / R3/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G2` | `WAIT_FOR_USER_CONTEXT` |
| [`www.account`](#www-account) | `/account` | `identity` | `M1/M5 / R1/R3 / observed-live / READ_WITH_REDACTION / G4` | `LIVE_READ_ONLY` |
| [`www.accountApi`](#www-accountapi) | `/account/api` | `internal-module` | `M6 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.feedback`](#www-feedback) | `/feedback?from=...` | `draft-input` | `M2/M3 / R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`www.changelog`](#www-changelog) | `/changelog` | `public-content` | `M0 / R0 / observed-live / SAFE_READ / G0` | `LIVE_READ_ONLY` |
| [`www.login`](#www-login) | `/login` | `identity` | `M5 / R5 / observed-live / READ_WITH_REDACTION / G4` | `LIVE_READ_ONLY` |
| [`www.loginRedirect`](#www-loginredirect) | `/login?spm=...&redirectURL=...` | `identity` | `M5 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.findAccount`](#www-findaccount) | `/find-account` | `identity` | `M5 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.selectAccount`](#www-selectaccount) | `/select-account` | `identity` | `M5 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.loginValidation`](#www-loginvalidation) | `/login-validation` | `identity` | `M5 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.commonVideo`](#www-commonvideo) | `/common-video` | `public-content` | `M0/M6 / R0/R4 / static-only / STATIC_ONLY / G0` | `STATIC_EVIDENCE_ONLY` |
| [`www.commonVideoLayout`](#www-commonvideolayout) | `/common-video/layout` | `internal-module` | `M6 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.upgradeBrowser`](#www-upgradebrowser) | `/upgrade-browser` | `public-content` | `M0/M6 / R0/R3 / static-only / STATIC_ONLY / G0` | `STATIC_EVIDENCE_ONLY` |
| [`www.playground`](#www-playground) | `/playground` | `internal-test` | `M6 / R4/R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`www.yhbCreateOrder`](#www-yhbcreateorder) | `create-order-yhb package` | `buyer-trade` | `M3 / R4 / static-only / STATIC_ONLY / G1` | `STATIC_EVIDENCE_ONLY` |
| [`www.yhbOrderDetail`](#www-yhborderdetail) | `order-detail-yhb package` | `buyer-trade` | `M3 / R4 / static-only / STATIC_ONLY / G1` | `STATIC_EVIDENCE_ONLY` |
| [`seller.dataOverview`](#seller-dataoverview) | `#/seller-data/data` | `seller-data` | `M4 / R1/R3 / observed-live / SAFE_READ / G1` | `LIVE_READ_ONLY` |
| [`seller.commodityData`](#seller-commoditydata) | `#/seller-data/commodity` | `seller-data` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.fanData`](#seller-fandata) | `#/seller-data/fanData` | `seller-data` | `M4 / R1/R3 / observed-live / SAFE_READ / G1` | `LIVE_READ_ONLY` |
| [`seller.customerServiceData`](#seller-customerservicedata) | `#/seller-data/customerService` | `seller-data` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.itemPublish`](#seller-itempublish) | `#/seller-item/publish` | `seller-item` | `M2/M4 / R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`seller.goodsManage`](#seller-goodsmanage) | `#/seller-item/goods-manage` | `seller-item` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`seller.postTemplate`](#seller-posttemplate) | `#/seller-item/post-temple` | `seller-item` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`seller.postTemplateCreate`](#seller-posttemplatecreate) | `#/seller-item/post-temple/create` | `seller-item` | `M4 / R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`seller.orderManage`](#seller-ordermanage) | `#/seller-trade/order-manage` | `seller-trade` | `M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.orderDetail`](#seller-orderdetail) | `#/seller-trade/order-manage/order-detail?orderId=...` | `seller-trade` | `M3/M4 / R1/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1` | `WAIT_FOR_USER_CONTEXT` |
| [`seller.refundManage`](#seller-refundmanage) | `#/seller-trade/refund-manage` | `seller-trade` | `M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.evaluationManage`](#seller-evaluationmanage) | `#/seller-trade/evaluation-manage` | `seller-trade` | `M3/M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.complaintManage`](#seller-complaintmanage) | `#/seller-trade/complaint-manage` | `seller-trade` | `M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.refundAddress`](#seller-refundaddress) | `#/seller-trade/refund-address` | `seller-trade` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.incomeBill`](#seller-incomebill) | `#/seller-finance/income-bill` | `seller-finance` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.expenseBill`](#seller-expensebill) | `#/seller-finance/expense-bill` | `seller-finance` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.invoiceApply`](#seller-invoiceapply) | `#/seller-finance/invoice-apply` | `seller-finance` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.basicInfo`](#seller-basicinfo) | `#/seller-finance/basic-info` | `seller-finance` | `M4/M5 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.subAccount`](#seller-subaccount) | `#/seller-account/sub-account` | `seller-account` | `M4/M5 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.csDispatch`](#seller-csdispatch) | `#/im-cs-dispatch/customer-routing-service` | `seller-account` | `M4/M5 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.securityCenter`](#seller-securitycenter) | `#/seller-sc/home` | `seller-security` | `M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.adHome`](#seller-adhome) | `#/seller-ad/home` | `seller-ad` | `M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.notificationCenter`](#seller-notificationcenter) | `#/notification-center` | `seller-shell` | `M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.notificationApi`](#seller-notificationapi) | `#/notification-center/api*` | `internal-module` | `M6 / R5 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |
| [`seller.im`](#seller-im) | `#/im` | `seller-message` | `M3/M4 / R1/R2/R3 / observed-live / READ_WITH_REDACTION / G2` | `LIVE_READ_ONLY` |
| [`seller.imItem`](#seller-imitem) | `#/im?itemId=...` | `seller-message` | `M3/M4 / R3/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G2` | `WAIT_FOR_USER_CONTEXT` |
| [`seller.imDesktop`](#seller-imdesktop) | `#/im-desktop` | `seller-shell` | `M6 / R5/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.download`](#seller-download) | `#/download` | `seller-shell` | `M6 / R5/R3 / observed-live / READ_WITH_REDACTION / G1` | `LIVE_READ_ONLY` |
| [`seller.selectSite`](#seller-selectsite) | `#/select-site` | `seller-gate` | `M5 / R5/R3 / observed-live / READ_WITH_REDACTION / G4` | `LIVE_READ_ONLY` |
| [`seller.accountCheck`](#seller-accountcheck) | `#/account-check` | `seller-gate` | `M5 / R5/R3 / observed-live / READ_WITH_REDACTION / G4` | `LIVE_READ_ONLY` |
| [`seller.accountCheckUser`](#seller-accountcheckuser) | `#/account-check?userNick=...` | `seller-gate` | `M5 / R5 / requires-user-context / REQUIRES_USER_CONTEXT / G4` | `WAIT_FOR_USER_CONTEXT` |
| [`seller.login`](#seller-login) | `#/login` | `seller-gate` | `M5 / R5 / shell-boundary / SHELL_ONLY / G4` | `SHELL_BOUNDARY_ONLY` |
| [`seller.noPermission`](#seller-nopermission) | `#/no-permission` | `seller-gate` | `M5 / R5 / observed-live / READ_WITH_REDACTION / G4` | `LIVE_READ_ONLY` |
| [`seller.iframe`](#seller-iframe) | `#/iframe?url=...` | `seller-shell` | `M6 / R5 / shell-boundary / SHELL_ONLY / G1` | `SHELL_BOUNDARY_ONLY` |
| [`seller.playground`](#seller-playground) | `#/playground` | `internal-test` | `M6 / R5/R4 / static-only / STATIC_ONLY / G4` | `STATIC_EVIDENCE_ONLY` |

## 页面档案

### 001 www.home

- 位置：主站，路由形状 `/`。
- 这页是什么：公开找货和内容发现页。重点理解搜索、频道、筛选、排序、商品卡片和推荐流结构。
- 风险摘要：`M0 / R0 / observed-live / SAFE_READ / G0`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。公开只读。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`search box`、`channel entries`、`recommended item cards`、`sidebar tools`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`open`、`search`、`browse channels`、`read public card structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`。
- 停止点：`message entry`、`publish entry`、`order entry`、`state-changing controls`、`private values outside public structure`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 002 www.search

- 位置：主站，路由形状 `/search?q=...`。
- 这页是什么：公开找货和内容发现页。重点理解搜索、频道、筛选、排序、商品卡片和推荐流结构。
- 风险摘要：`M0 / R0 / observed-live / SAFE_READ / G0`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。公开只读。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`query box`、`sort controls`、`price inputs`、`filter tags`、`item cards`、`pagination`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`change keyword`、`change price range`、`change sort`、`read item-card structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`。
- 停止点：`unstable location panel`、`collect`、`contact`、`purchase`、`state-changing controls`、`private values outside public structure`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 003 www.machFeeds

- 位置：主站，路由形状 `/mach-feeds?machId=...&publishTimes=...`。
- 这页是什么：公开找货和内容发现页。重点理解搜索、频道、筛选、排序、商品卡片和推荐流结构。
- 风险摘要：`M0 / R0 / observed-live / SAFE_READ / G0`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。公开只读。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`channel title`、`waterfall feed`、`item-card links`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read channel feed structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`。
- 停止点：`collect`、`contact`、`purchase`、`state-changing controls`、`private values outside public structure`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 004 www.item

- 位置：主站，路由形状 `/item?id=...&categoryId=...`。
- 这页是什么：商品详情页。重点理解商品信息区、保障标签、卖家卡片、操作按钮和交易入口边界。
- 风险摘要：`M0/M3 / R0/R3 / requires-user-context / REQUIRES_USER_CONTEXT / G1`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。登录只读，输出脱敏。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`image area`、`price area`、`assurance labels`、`seller card`、`action buttons`、`recommendations`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`read public item structure`、`draft question text`。
- 常见状态：`正常内容`、`加载中`、`空态`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`collect`、`chat`、`buy now`、`downshelf`、`delete`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 005 www.personalOther

- 位置：主站，路由形状 `/personal?userId=...`。
- 这页是什么：公开个人主页。重点理解主页资料区、信用信息区、宝贝列表、关注和联系入口边界。
- 风险摘要：`M0/M1 / R0/R3 / requires-user-context / REQUIRES_USER_CONTEXT / G1`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。登录只读，输出脱敏。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`public profile block`、`credit area`、`item list`、`follow/contact entries`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`read public profile structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`二维码或 App 承接`、`确认弹窗`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`。
- 停止点：`follow`、`contact`、`purchase`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 006 www.personalSelf

- 位置：主站，路由形状 `/personal`。
- 这页是什么：买家账号内页面。重点理解个人中心、收藏、账号设置、模块入口和账号态边界。
- 风险摘要：`M1/M2 / R1/R3 / observed-live / SAFE_READ / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`left navigation`、`home tab`、`item/credit/manage tabs`、`filters`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read current profile structure`、`read listing status categories`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`。
- 停止点：`edit profile`、`manage item`、`downshelf`、`delete`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 007 www.collection

- 位置：主站，路由形状 `/collection`。
- 这页是什么：买家账号内页面。重点理解个人中心、收藏、账号设置、模块入口和账号态边界。
- 风险摘要：`M1/M3 / R1/R3 / observed-live / SAFE_READ / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`collection tab`、`item cards`、`uncollect button`、`want button`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read collection structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`。
- 停止点：`uncollect`、`want`、`contact`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 008 www.bought

- 位置：主站，路由形状 `/bought`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M1/M3 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`order tabs`、`order cards`、`more menu`、`logistics record`、`snapshot entry`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read order status categories`、`read button structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`confirm receipt`、`refund`、`review`、`delete`、`complaint`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 009 www.orderDetail

- 位置：主站，路由形状 `/order-detail?orderId=...`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M3 / R1/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。登录只读，输出脱敏。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`status nodes`、`order field labels`、`logistics module`、`after-sale entry`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`read field names`、`read status-node categories`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`any order-state change`、`real order value logging`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 010 www.createOrder

- 位置：主站，路由形状 `/create-order?itemId=...`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M3/M5 / R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。登录只读，输出脱敏。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`sku`、`quantity`、`address fields`、`price-detail block`、`payment area`、`scan-to-pay fallback`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`build pre-order checklist from field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`submit order`、`pay`、`change address`、`bind account`、`verify identity`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 011 www.paySuccess

- 位置：主站，路由形状 `/pay-success?orderId=...&itemId=...`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M3 / R4 / static-only / STATIC_ONLY / G1`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。登录只读，输出脱敏。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`payment result structure`、`order-detail entry`、`recommendations`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify result page structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`trigger payment for testing`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 012 www.publish

- 位置：主站，路由形状 `/publish`。
- 这页是什么：草稿输入页。重点理解表单字段、校验提示、输入区和上传/提交边界。
- 风险摘要：`M2/M3 / R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`image/video uploader`、`description`、`category`、`properties`、`sku`、`price`、`location`、`shipping settings`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`draft listing text`、`check required field categories`。
- 常见状态：`正常内容`、`加载中`、`登录失效`、`确认弹窗`、`表单校验`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S8_FORM_VALIDATION`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`upload`、`save draft`、`publish`、`edit existing item`、`save`、`submit`、`send`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 013 www.publishScene

- 位置：主站，路由形状 `/publish?scene=xyPcMainPublish`。
- 这页是什么：草稿输入页。重点理解表单字段、校验提示、输入区和上传/提交边界。
- 风险摘要：`M2/M3 / R2/R3 / static-only / STATIC_ONLY / G2`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`publish scene parameter`、`publish form fields`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify publish entry shape`。
- 常见状态：`正常内容`、`加载中`、`登录失效`、`确认弹窗`、`表单校验`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S8_FORM_VALIDATION`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`save`、`publish`、`upload`、`submit`、`send`、`overwrite existing content`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 014 www.publishEdit

- 位置：主站，路由形状 `/publish?scene=xyPcMainPublish&itemId=...`。
- 这页是什么：草稿输入页。重点理解表单字段、校验提示、输入区和上传/提交边界。
- 风险摘要：`M2/M3 / R3/R4 / static-only / STATIC_ONLY / G2`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`item context parameter`、`publish/edit form fields`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify edit risk`。
- 常见状态：`正常内容`、`加载中`、`登录失效`、`确认弹窗`、`表单校验`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S8_FORM_VALIDATION`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`overwrite existing item`、`save`、`publish`、`upload`、`submit`、`send`、`overwrite existing content`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 015 www.im

- 位置：主站，路由形状 `/im`。
- 这页是什么：消息页。重点理解会话外壳、输入区、工具栏和发送边界，不读取具体私聊内容。
- 风险摘要：`M1/M2/M3 / R1/R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`empty state`、`session list`、`input area`、`toolbar`、`item/order card tools`、`file tool`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read message-frame structure`、`draft message text`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`确认弹窗`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`read specific private chat`、`send`、`send card`、`upload file`、`upload`、`save`、`submit`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 016 www.imItem

- 位置：主站，路由形状 `/im?itemId=...&peerUserId=...`。
- 这页是什么：消息页。重点理解会话外壳、输入区、工具栏和发送边界，不读取具体私聊内容。
- 风险摘要：`M1/M3 / R3/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G2`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`item-linked chat parameters`、`input area`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`identify item-linked chat entry`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`确认弹窗`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`read specific conversation`、`send`、`upload`、`save`、`submit`、`publish`、`overwrite existing content`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 017 www.account

- 位置：主站，路由形状 `/account`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M1/M5 / R1/R3 / observed-live / READ_WITH_REDACTION / G4`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。禁止主动触发。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`basic info module`、`stay signed in`、`notice switch`、`verification entry`、`security center`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read module names and status categories`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`toggle notice`、`verify identity`、`switch account`、`logout`、`any proactive action beyond naming the boundary`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 018 www.accountApi

- 位置：主站，路由形状 `/account/api`。
- 这页是什么：内部模块或资源页。重点识别模块存在和风险边界，不当作业务页面操作。
- 风险摘要：`M6 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`module path`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`treat as non-page evidence`。
- 常见状态：`网络或接口失败`。
- 可继续状态：`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：无。
- 停止点：`direct call`、`page navigation`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 019 www.feedback

- 位置：主站，路由形状 `/feedback?from=...`。
- 这页是什么：草稿输入页。重点理解表单字段、校验提示、输入区和上传/提交边界。
- 风险摘要：`M2/M3 / R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`feedback type`、`source page option`、`text area`、`screenshot upload`、`submit`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`draft feedback text`。
- 常见状态：`正常内容`、`加载中`、`登录失效`、`确认弹窗`、`表单校验`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S8_FORM_VALIDATION`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`upload screenshot`、`submit`、`upload`、`save`、`send`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 020 www.changelog

- 位置：主站，路由形状 `/changelog`。
- 这页是什么：公共内容或承接页。重点理解静态内容、视频/升级/承接形态和外部跳转边界。
- 风险摘要：`M0 / R0 / observed-live / SAFE_READ / G0`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。公开只读。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`update-log title`、`feature entries`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read public content structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`state-changing controls`、`private values outside public structure`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 021 www.login

- 位置：主站，路由形状 `/login`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M5 / R5 / observed-live / READ_WITH_REDACTION / G4`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。禁止主动触发。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`login method`、`scan container`、`verification entry`、`redirect parameter`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`open login page`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`scan`、`enter verification code`、`bypass risk control`、`any proactive action beyond naming the boundary`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 022 www.loginRedirect

- 位置：主站，路由形状 `/login?spm=...&redirectURL=...`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M5 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`redirect parameter`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify login redirect shape`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`change login parameters`、`bypass risk control`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 023 www.findAccount

- 位置：主站，路由形状 `/find-account`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M5 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`account recovery placeholder`、`redirect behavior`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify page type`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`recover account`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 024 www.selectAccount

- 位置：主站，路由形状 `/select-account`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M5 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`account selection placeholder`、`redirect behavior`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify page type`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`switch account`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 025 www.loginValidation

- 位置：主站，路由形状 `/login-validation`。
- 这页是什么：身份或登录门禁页。重点识别登录、验证、账号选择、站点选择和权限门禁。
- 风险摘要：`M5 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`login validation placeholder`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`identify page type`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`enter verification code`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 026 www.commonVideo

- 位置：主站，路由形状 `/common-video`。
- 这页是什么：公共内容或承接页。重点理解静态内容、视频/升级/承接形态和外部跳转边界。
- 风险摘要：`M0/M6 / R0/R4 / static-only / STATIC_ONLY / G0`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。公开只读。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`video container`、`title/material config`、`playback controls`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`read activity/video container structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`play proactively`、`download`、`capture video`、`state-changing controls`、`private values outside public structure`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 027 www.commonVideoLayout

- 位置：主站，路由形状 `/common-video/layout`。
- 这页是什么：内部模块或资源页。重点识别模块存在和风险边界，不当作业务页面操作。
- 风险摘要：`M6 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`layout package path`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`treat as static evidence`。
- 常见状态：`网络或接口失败`。
- 可继续状态：`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：无。
- 停止点：`page navigation`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 028 www.upgradeBrowser

- 位置：主站，路由形状 `/upgrade-browser`。
- 这页是什么：公共内容或承接页。重点理解静态内容、视频/升级/承接形态和外部跳转边界。
- 风险摘要：`M0/M6 / R0/R3 / static-only / STATIC_ONLY / G0`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。公开只读。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`browser recommendation list`、`download entry`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`read recommendation structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`download`、`install`、`state-changing controls`、`private values outside public structure`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页可按公开结构输出。

### 029 www.playground

- 位置：主站，路由形状 `/playground`。
- 这页是什么：内部测试页。重点识别测试入口，不主动访问或触发测试动作。
- 风险摘要：`M6 / R4/R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`internal test entry`、`login/upload/qr/payment test controls`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`static identification only`。
- 常见状态：`高风险业务态`。
- 可继续状态：无。
- 停止状态：`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`visit proactively`、`trigger test action`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 030 www.yhbCreateOrder

- 位置：主站，路由形状 `create-order-yhb package`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M3 / R4 / static-only / STATIC_ONLY / G1`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。登录只读，输出脱敏。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`YHB order render fields`、`YHB order create interface`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`record structure and risk`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`create YHB order`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 031 www.yhbOrderDetail

- 位置：主站，路由形状 `order-detail-yhb package`。
- 这页是什么：买家交易页。重点理解订单、支付、物流、售后和状态节点结构，只读不触发交易。
- 风险摘要：`M3 / R4 / static-only / STATIC_ONLY / G1`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。登录只读，输出脱敏。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`report fields`、`dispute fields`、`review-related fields`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`read report/status capability shape`。
- 常见状态：`正常内容`、`加载中`、`空态`、`登录失效`、`二维码或 App 承接`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`after-sale action`、`review action`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 032 seller.dataOverview

- 位置：卖家工作台，路由形状 `#/seller-data/data`。
- 这页是什么：卖家数据页。重点理解指标卡、日期筛选、图表和表头，不记录真实经营数值。
- 风险摘要：`M4 / R1/R3 / observed-live / SAFE_READ / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`date controls`、`metric cards`、`trend charts`、`info popovers`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read metric field names and module names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`record real numbers`、`export`、`download`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 033 seller.commodityData

- 位置：卖家工作台，路由形状 `#/seller-data/commodity`。
- 这页是什么：卖家数据页。重点理解指标卡、日期筛选、图表和表头，不记录真实经营数值。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`search`、`date`、`commodity table`、`metric columns`、`pagination`、`download`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read headers and filters`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`download item detail`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 034 seller.fanData

- 位置：卖家工作台，路由形状 `#/seller-data/fanData`。
- 这页是什么：卖家数据页。重点理解指标卡、日期筛选、图表和表头，不记录真实经营数值。
- 风险摘要：`M4 / R1/R3 / observed-live / SAFE_READ / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可做结构只读。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`date`、`fan metrics`、`profile distributions`、`region/user-group modules`。
- 可读结构：`navigationEntries`、`filterControls`、`cardStructure`、`contentBlocks`、`routeShapes`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`。
- 允许动作/观察：`read profile module names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`record real audience numbers`、`export`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify navigation, filters, card structure, content blocks, and route shapes; avoid item identity values.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 035 seller.customerServiceData

- 位置：卖家工作台，路由形状 `#/seller-data/customerService`。
- 这页是什么：卖家数据页。重点理解指标卡、日期筛选、图表和表头，不记录真实经营数值。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`consultation metrics`、`satisfaction fields`、`customer-service table`、`export`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read headers and satisfaction field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`网络或接口失败`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`export customer-service detail`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 036 seller.itemPublish

- 位置：卖家工作台，路由形状 `#/seller-item/publish`。
- 这页是什么：卖家商品页。重点理解商品管理、发布字段、模板、状态 tab 和上下架/删除边界。
- 风险摘要：`M2/M4 / R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`image/video uploader`、`title/description`、`category`、`sku`、`price`、`stock`、`shipping settings`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`draft item listing`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`表单校验`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S8_FORM_VALIDATION`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`upload`、`save`、`publish`、`submit`、`send`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 037 seller.goodsManage

- 位置：卖家工作台，路由形状 `#/seller-item/goods-manage`。
- 这页是什么：卖家商品页。重点理解商品管理、发布字段、模板、状态 tab 和上下架/删除边界。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`status tabs`、`search/filter`、`item table`、`bulk actions`、`operation column`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read filters and headers`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`表单校验`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S8_FORM_VALIDATION`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`edit`、`copy`、`adjust price`、`shelf changes`、`delete`、`upload`、`save`、`submit`、`send`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 038 seller.postTemplate

- 位置：卖家工作台，路由形状 `#/seller-item/post-temple`。
- 这页是什么：卖家商品页。重点理解商品管理、发布字段、模板、状态 tab 和上下架/删除边界。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`template list`、`create entry`、`operation column`、`delete/default confirmation`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read template field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`表单校验`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S8_FORM_VALIDATION`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`create`、`edit`、`delete`、`set default`、`upload`、`save`、`submit`、`send`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 039 seller.postTemplateCreate

- 位置：卖家工作台，路由形状 `#/seller-item/post-temple/create`。
- 这页是什么：卖家商品页。重点理解商品管理、发布字段、模板、状态 tab 和上下架/删除边界。
- 风险摘要：`M4 / R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`template name`、`shipping location`、`billing mode`、`region modal`、`save`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`draft template fields`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`表单校验`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`、`S8_FORM_VALIDATION`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`save real template`、`upload`、`save`、`submit`、`send`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 040 seller.orderManage

- 位置：卖家工作台，路由形状 `#/seller-trade/order-manage`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`order-status tabs`、`search conditions`、`date`、`order table`、`operation column`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read order-status categories and headers`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`ship`、`change logistics`、`remark`、`contact`、`view funds`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 041 seller.orderDetail

- 位置：卖家工作台，路由形状 `#/seller-trade/order-manage/order-detail?orderId=...`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M3/M4 / R1/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G1`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。登录只读，输出脱敏。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`status nodes`、`logistics`、`address-modification area`、`trade messages`、`operation buttons`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`read field names after user-provided context`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`guess order id`、`order action`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 042 seller.refundManage

- 位置：卖家工作台，路由形状 `#/seller-trade/refund-manage`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`refund type`、`status filter`、`reason`、`logistics`、`operation column`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read refund status and field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`agree refund`、`refuse refund`、`compensate`、`confirm receipt`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 043 seller.evaluationManage

- 位置：卖家工作台，路由形状 `#/seller-trade/evaluation-manage`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M3/M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`evaluation filters`、`evaluation table`、`batch review`、`report/contact`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read evaluation fields`、`draft reply text`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`review`、`report`、`contact`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 044 seller.complaintManage

- 位置：卖家工作台，路由形状 `#/seller-trade/complaint-manage`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M3/M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`complaint status`、`complaint table`、`detail/proof entry`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read complaint status`、`draft appeal/proof text`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`submit proof`、`revoke`、`refuse`、`submit material`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 045 seller.refundAddress

- 位置：卖家工作台，路由形状 `#/seller-trade/refund-address`。
- 这页是什么：卖家交易和售后页。重点理解订单、退款、评价、投诉、地址等表格和状态类别。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`address table`、`default status`、`operation column`、`add/edit/delete`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read address table headers`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`add address`、`edit address`、`delete address`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 046 seller.incomeBill

- 位置：卖家工作台，路由形状 `#/seller-finance/income-bill`。
- 这页是什么：卖家财务页。重点理解账单、发票、主体资料、日期筛选和导出/下载边界。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`month/day/detail tabs`、`date`、`business type`、`bill table`、`export/download`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read income field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`export`、`historical download`、`download full detail`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 047 seller.expenseBill

- 位置：卖家工作台，路由形状 `#/seller-finance/expense-bill`。
- 这页是什么：卖家财务页。重点理解账单、发票、主体资料、日期筛选和导出/下载边界。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`month/day/detail tabs`、`expense type`、`bill table`、`export/download`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read expense field names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`export`、`download`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 048 seller.invoiceApply

- 位置：卖家工作台，路由形状 `#/seller-finance/invoice-apply`。
- 这页是什么：卖家财务页。重点理解账单、发票、主体资料、日期筛选和导出/下载边界。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`pending/applied/legacy tabs`、`business type`、`apply`、`export`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read invoice fields and button names`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`apply invoice`、`export`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 049 seller.basicInfo

- 位置：卖家工作台，路由形状 `#/seller-finance/basic-info`。
- 这页是什么：卖家财务页。重点理解账单、发票、主体资料、日期筛选和导出/下载边界。
- 风险摘要：`M4/M5 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`invoice entity form`、`edit/save`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read field names only`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`modify entity data`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 050 seller.subAccount

- 位置：卖家工作台，路由形状 `#/seller-account/sub-account`。
- 这页是什么：卖家账号资料页。重点理解基础资料、主体字段、店铺资料和编辑/保存边界。
- 风险摘要：`M4/M5 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`sub-account table`、`role`、`status`、`routing config`、`new/disable/permission`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read permission field names and status categories`。
- 常见状态：`正常内容`、`加载中`、`空态`、`权限或身份门禁`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`create sub-account`、`disable account`、`change permission`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 051 seller.csDispatch

- 位置：卖家工作台，路由形状 `#/im-cs-dispatch/customer-routing-service`。
- 这页是什么：卖家账号资料页。重点理解基础资料、主体字段、店铺资料和编辑/保存边界。
- 风险摘要：`M4/M5 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`groups`、`reception scope`、`participating service agents`、`switch`、`save`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read routing rule structure`。
- 常见状态：`正常内容`、`加载中`、`空态`、`权限或身份门禁`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`save`、`enable/disable`、`create group`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 052 seller.securityCenter

- 位置：卖家工作台，路由形状 `#/seller-sc/home`。
- 这页是什么：安全和权限页。重点理解安全中心、子账号、权限、客服分流和身份校验边界。
- 风险摘要：`M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`violation table`、`penalty status`、`appeal status`、`detail/appeal`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read violation field names and status categories`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`view sensitive detail`、`appeal`、`process`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 053 seller.adHome

- 位置：卖家工作台，路由形状 `#/seller-ad/home`。
- 这页是什么：推广投放页。重点理解推广入口、计划/付费动作边界和数据只读口径。
- 风险摘要：`M4 / R1/R4 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`date`、`promotion metrics`、`plan entry`、`carousel controls`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read promotion fields`、`draft plan idea`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`高风险业务态`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`create plan`、`launch paid promotion`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 054 seller.notificationCenter

- 位置：卖家工作台，路由形状 `#/notification-center`。
- 这页是什么：卖家外壳或 iframe 容器。重点识别容器、嵌入目标和边界，不进入嵌入动作。
- 风险摘要：`M4 / R1/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`notification list`、`unread status`、`detail entry`、`mark read/clear unread`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read notification structure and categories`。
- 常见状态：`正常内容`、`加载中`、`网络或接口失败`、`权限或身份门禁`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`mark read`、`clear unread`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 055 seller.notificationApi

- 位置：卖家工作台，路由形状 `#/notification-center/api*`。
- 这页是什么：内部模块或资源页。重点识别模块存在和风险边界，不当作业务页面操作。
- 风险摘要：`M6 / R5 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`internal API/interface module`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`treat as non-page`。
- 常见状态：`网络或接口失败`。
- 可继续状态：`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：无。
- 停止点：`direct call`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 056 seller.im

- 位置：卖家工作台，路由形状 `#/im`。
- 这页是什么：卖家消息页。重点理解消息壳、会话入口、桌面端承接和发送/文件边界。
- 风险摘要：`M3/M4 / R1/R2/R3 / observed-live / READ_WITH_REDACTION / G2`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`session list`、`search`、`input area`、`toolbar`、`quick replies`、`file`、`transfer`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read frame`、`draft reply`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`read specific conversation`、`send`、`file upload`、`transfer`、`upload`、`save`、`submit`、`publish`、`overwrite existing content`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 057 seller.imItem

- 位置：卖家工作台，路由形状 `#/im?itemId=...`。
- 这页是什么：卖家消息页。重点理解消息壳、会话入口、桌面端承接和发送/文件边界。
- 风险摘要：`M3/M4 / R3/R4 / requires-user-context / REQUIRES_USER_CONTEXT / G2`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。草稿辅助，停在保存/提交/发送/发布前。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`item-linked message parameter`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`identify entry shape`。
- 常见状态：`正常内容`、`加载中`、`空态`、`确认弹窗`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S2_EMPTY_STATE`。
- 停止状态：`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`。
- 停止点：`guess parameter`、`send`、`upload`、`save`、`submit`、`publish`、`overwrite existing content`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 058 seller.imDesktop

- 位置：卖家工作台，路由形状 `#/im-desktop`。
- 这页是什么：卖家外壳或 iframe 容器。重点识别容器、嵌入目标和边界，不进入嵌入动作。
- 风险摘要：`M6 / R5/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`download/open client prompt`。
- 可读结构：`tabNames`、`filterFieldNames`、`tableHeaders`、`buttonCategories`、`statusCategories`、`modalCategories`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`fieldNames`。
- 允许动作/观察：`read container structure`。
- 常见状态：`正常内容`、`加载中`、`网络或接口失败`、`权限或身份门禁`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`download`、`install`、`open`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify tabs, filters, table headers, status categories, and modal categories; never read row values or trigger operations.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 059 seller.download

- 位置：卖家工作台，路由形状 `#/download`。
- 这页是什么：卖家外壳或 iframe 容器。重点识别容器、嵌入目标和边界，不进入嵌入动作。
- 风险摘要：`M6 / R5/R3 / observed-live / READ_WITH_REDACTION / G1`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。登录只读，输出脱敏。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`download button`、`client type`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read download entry`。
- 常见状态：`正常内容`、`加载中`、`网络或接口失败`、`权限或身份门禁`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`download`、`install`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 060 seller.selectSite

- 位置：卖家工作台，路由形状 `#/select-site`。
- 这页是什么：卖家门禁页。重点识别站点选择、账号检查、无权限和登录边界。
- 风险摘要：`M5 / R5/R3 / observed-live / READ_WITH_REDACTION / G4`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。禁止主动触发。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`site/identity list`、`selection button`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read site-selection structure`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`switch site`、`any proactive action beyond naming the boundary`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 061 seller.accountCheck

- 位置：卖家工作台，路由形状 `#/account-check`。
- 这页是什么：卖家门禁页。重点识别站点选择、账号检查、无权限和登录边界。
- 风险摘要：`M5 / R5/R3 / observed-live / READ_WITH_REDACTION / G4`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。禁止主动触发。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`account check`、`continue`、`re-login`、`switch`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`read gate structure`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`continue`、`re-login`、`switch account`、`any proactive action beyond naming the boundary`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 062 seller.accountCheckUser

- 位置：卖家工作台，路由形状 `#/account-check?userNick=...`。
- 这页是什么：卖家门禁页。重点识别站点选择、账号检查、无权限和登录边界。
- 风险摘要：`M5 / R5 / requires-user-context / REQUIRES_USER_CONTEXT / G4`。必须等用户提供真实 URL 或业务上下文，不猜参数。需要用户上下文后才能继续。禁止主动触发。
- 打开方式：Do not open by guessing parameters. Verify only when the user supplies a URL or business context.
- 等待锚点：`account-check parameter`。
- 可读结构：`routeShape`、`requiredParameterType`、`riskBoundary`、`userConfirmationNeeded`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`identify parameter shape`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`guess real account name`、`any proactive action beyond naming the boundary`。
- 验证通过证据：required parameter type identified；user-provided context confirmed；private parameters redacted；business action boundary recorded。
- 下一步熟悉：Wait for user-supplied URL or context; verify route shape and boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 063 seller.login

- 位置：卖家工作台，路由形状 `#/login`。
- 这页是什么：卖家门禁页。重点识别站点选择、账号检查、无权限和登录边界。
- 风险摘要：`M5 / R5 / shell-boundary / SHELL_ONLY / G4`。只识别外壳或容器边界，停在嵌入/登录/权限前。只识别外壳。禁止主动触发。
- 打开方式：Open shell only if already reachable; identify login, iframe, or container boundary and stop.
- 等待锚点：`login`、`scan`、`verification entry`。
- 可读结构：`containerType`、`embeddedTargetShape`、`permissionBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`open login container`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`scan`、`enter verification code`、`any proactive action beyond naming the boundary`。
- 验证通过证据：container type identified；embedded target shape described；login or permission boundary recorded；no embedded action triggered。
- 下一步熟悉：Verify shell/container type only; stop before embedded login, install, or external app action.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 064 seller.noPermission

- 位置：卖家工作台，路由形状 `#/no-permission`。
- 这页是什么：卖家门禁页。重点识别站点选择、账号检查、无权限和登录边界。
- 风险摘要：`M5 / R5 / observed-live / READ_WITH_REDACTION / G4`。当前已能在登录浏览器 Profile 下只读观察结构。可只读，但输出必须脱敏。禁止主动触发。
- 打开方式：Open route or navigate from known menu in a logged-in profile; wait for structural anchors only.
- 等待锚点：`no-permission message`、`return/jump controls`。
- 可读结构：`fieldNames`、`inputTypes`、`validationHintCategories`、`uploadZones`、`emptyStateCategories`、`shellAnchors`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`。
- 允许动作/观察：`record permission failure`。
- 常见状态：`登录失效`、`权限或身份门禁`、`二维码或 App 承接`。
- 可继续状态：无。
- 停止状态：`S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`。
- 停止点：`any proactive action beyond naming the boundary`。
- 验证通过证据：route shape recognized；one or more anchors visible；expected state category assigned；recordable structure captured without private values。
- 下一步熟悉：Verify fields, validation categories, upload zones, empty states, and shell anchors; stop before save, upload, submit, send, or publish.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 065 seller.iframe

- 位置：卖家工作台，路由形状 `#/iframe?url=...`。
- 这页是什么：卖家外壳或 iframe 容器。重点识别容器、嵌入目标和边界，不进入嵌入动作。
- 风险摘要：`M6 / R5 / shell-boundary / SHELL_ONLY / G1`。只识别外壳或容器边界，停在嵌入/登录/权限前。只识别外壳。登录只读，输出脱敏。
- 打开方式：Open shell only if already reachable; identify login, iframe, or container boundary and stop.
- 等待锚点：`iframe source`、`loading/failure state`。
- 可读结构：`containerType`、`embeddedTargetShape`、`permissionBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`、`buttonNames`。
- 允许动作/观察：`identify container source`。
- 常见状态：`正常内容`、`加载中`、`网络或接口失败`、`权限或身份门禁`、`二维码或 App 承接`、`文件上传下载或导出`。
- 可继续状态：`S0_NORMAL_CONTENT`、`S1_LOADING`、`S3_NETWORK_OR_API_FAILURE`。
- 停止状态：`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT`。
- 停止点：`operate external page without separate review`、`private value logging`、`edit/save/send/export/download/submit controls`。
- 验证通过证据：container type identified；embedded target shape described；login or permission boundary recorded；no embedded action triggered。
- 下一步熟悉：Verify shell/container type only; stop before embedded login, install, or external app action.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

### 066 seller.playground

- 位置：卖家工作台，路由形状 `#/playground`。
- 这页是什么：内部测试页。重点识别测试入口，不主动访问或触发测试动作。
- 风险摘要：`M6 / R5/R4 / static-only / STATIC_ONLY / G4`。只从静态证据理解，不为了补覆盖强行打开。只做静态解释。禁止主动触发。
- 打开方式：Do not open for coverage. Verify from static route, module, signal, or API evidence only.
- 等待锚点：`test entry`。
- 可读结构：`staticRoute`、`moduleName`、`staticApiFamily`、`riskBoundary`、`routeShape`、`pageFamily`、`layer`、`readiness`、`coverageStatus`、`tabNames`、`fieldNames`、`tableHeaders`。
- 允许动作/观察：`static identification only`。
- 常见状态：`高风险业务态`。
- 可继续状态：无。
- 停止状态：`S10_HIGH_RISK_BUSINESS_STATE`。
- 停止点：`visit proactively`、`trigger test action`、`any proactive action beyond naming the boundary`。
- 验证通过证据：static module or route signal identified；API or Page signal mapped to family；risk boundary recorded；no live probing attempted。
- 下一步熟悉：Keep as static evidence; verify module name, static API family, and risk boundary only.
- 输出边界：只写结构、字段名、tab、表头、按钮名、状态类别和停止点；不写真实值。 本页输出需要脱敏。

结论：这份档案是人工读页面时的逐页说明书；机器执行仍以 `goofish-page-dossier-index.json`、`goofish-page-ontology.json` 和 `goofish-page-verification-checklist.json` 为准。
