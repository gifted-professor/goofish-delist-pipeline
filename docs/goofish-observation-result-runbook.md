# 闲鱼观察结果登记手册

日期：2026-06-22  
用途：把每次浏览器/Profile 实际观察到的结果，登记成统一的“类别台账”。它回答“这页这次跑没跑、为什么停、能不能算覆盖、是否通过隐私检查”。  
边界：只记录页面编号、路由形状、批次、状态类别、控件类别、字段风险、动作门禁、停止原因和隐私检查结果；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

配套机器台账：`goofish-observation-result-ledger.json`  
上游来源：`goofish-page-manifest.json`、`goofish-page-ontology.json`、`goofish-route-context-catalog.json`、`goofish-safe-dom-observation-schema.json`、`goofish-probe-batch-matrix.json`、`goofish-page-change-sentinel.json`、`goofish-visible-label-lexicon.json`。

## 什么时候用

- 登录一个账号后，记录主站、买家页、卖家工作台外壳是否能只读进入。
- 换账号/Profile 后，对比同一个页面是正常、空态、无权限、需要上下文还是静态解释。
- 页面改版或灰度时，判断是允许漂移、需要复核还是必须停。
- 脚本巡检后，生成只含类别的覆盖统计。

## 登记字段

| 字段 | 允许写什么 | 不允许写什么 |
| --- | --- | --- |
| `runId` | 本次运行代号 | 账号名、店铺名、真实用户身份 |
| `accountSlot` | `account-01` 这类槽位 | 会员名、手机号、邮箱 |
| `browserProfileAlias` | Profile 别名 | 浏览器里显示的真实账号 |
| `pageId` | 已知页面编号或 `UNKNOWN_PAGE` | 页面里的个人/交易内容 |
| `routeShape` | path/hash 和参数名 | 订单、商品、用户、会话、地址等具体参数内容 |
| `resultStatus` | 台账枚举 | 自由描述私密页面内容 |
| `stateCategory` | `S0-S10` | 弹窗、二维码、验证页的具体内容 |
| `anchorsObserved` | 锚点名、tab 名、表头名 | 表格行、订单卡、聊天正文、商品标题 |
| `labelMatches` | 词典分组 id | 页面私密文本片段 |
| `controlCategories` | `C0-C4` | 控件旁边的真实业务内容 |
| `fieldRiskSummary` | `F0-F4` 类别 | 字段里的实际个人/交易/经营内容 |
| `actionGateSummary` | `G0-G4` 类别 | 已执行或准备执行的业务动作内容 |
| `stopReasonCategory` | 停止原因类别 | 具体订单、地址、聊天或金额原因 |
| `privacyCheckPassed` | true / false | 未脱敏仍强行标 true |

## 结果状态

| 状态 | 含义 | 后续动作 |
| --- | --- | --- |
| `pending-read-only-observation` | 可只读观察，但本轮还没有填结果 | 先做 Profile 预检，再按批次进入 |
| `passed-read-only` | 路由、锚点、状态、控件和隐私检查都通过 | 可计入本 Profile 覆盖 |
| `stopped-state` | 出现登录、权限、二维码、确认、文件导出或高风险业务态 | 只记状态类别，停止 |
| `stopped-action` | 出现提交、保存、发送、支付、退款、发货、导出、上传等动作边界 | 只记动作/控件类别，停止 |
| `needs-user-context` | 缺少用户给出的具体 URL 或业务上下文 | 不猜参数，等待用户提供 |
| `static-described` | 只能用静态/模块证据解释 | 不主动 live 打开补覆盖 |
| `shell-described` | 只是登录、iframe、下载或容器边界 | 识别边界后停止 |
| `unknown-triaged` | 未知页或灰度页已收口分类 | 走未知页手册复核 |
| `privacy-rejected` | 观察内容触碰隐私持久化红线 | 丢弃结果，只留停止类别 |

## 停止原因类别

| 类别 | 含义 |
| --- | --- |
| `none` | 只读观察通过，无停止原因 |
| `state-stop` | 页面状态要求停止 |
| `action-stop` | 控件或动作要求停止 |
| `privacy-stop` | 输出将包含隐私内容，必须丢弃 |
| `context-stop` | 需要用户上下文，不能猜参数 |
| `static-only` | 只能静态解释 |
| `shell-boundary` | 只到外壳/容器边界 |
| `unknown-route` | 路由未知，先分类再说 |

## 变更判断

| 判断 | 可以怎么处理 |
| --- | --- |
| `same-baseline` | 可沿用原页面理解 |
| `allowed-drift` | 只更新结构文案或锚点，不更新风险边界 |
| `review-required` | 暂停深化，人工复核页面族、参数和锚点 |
| `stop-required` | 停止本轮；新私密参数、高风险控件、高风险状态、外部承接或未知路由都算停止 |

## 批次登记

### 0. B0_SESSION_PREFLIGHT

页面数：0。运行方式：`PREFLIGHT_ONLY`。默认结果状态：`passed-read-only`、`stopped-state`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：无固定页面；只做 Profile 预检或未知页收口。

### 1. B1_LOW_RISK_LIVE_STRUCTURE

页面数：8。运行方式：`LIVE_READ_ONLY`。默认结果状态：`pending-read-only-observation`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`www.home`、`www.search`、`www.machFeeds`、`www.personalSelf`、`www.collection`、`www.changelog`、`seller.dataOverview`、`seller.fanData`

### 2. B2_FORM_AND_SHELL_LIVE_PASS

页面数：14。运行方式：`LIVE_READ_ONLY`。默认结果状态：`pending-read-only-observation`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`www.publish`、`www.im`、`www.feedback`、`www.login`、`seller.commodityData`、`seller.customerServiceData`、`seller.itemPublish`、`seller.goodsManage`、`seller.postTemplate`、`seller.postTemplateCreate`、`seller.download`、`seller.selectSite`、`seller.accountCheck`、`seller.noPermission`

### 3. B3_HIGH_RISK_LIVE_REDACTED_PASS

页面数：18。运行方式：`LIVE_READ_ONLY`。默认结果状态：`pending-read-only-observation`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`www.bought`、`www.account`、`seller.orderManage`、`seller.refundManage`、`seller.evaluationManage`、`seller.complaintManage`、`seller.refundAddress`、`seller.incomeBill`、`seller.expenseBill`、`seller.invoiceApply`、`seller.basicInfo`、`seller.subAccount`、`seller.csDispatch`、`seller.securityCenter`、`seller.adHome`、`seller.notificationCenter`、`seller.im`、`seller.imDesktop`

### 4. B4_USER_CONTEXT_REQUIRED_PASS

页面数：8。运行方式：`WAIT_FOR_USER_CONTEXT`。默认结果状态：`needs-user-context`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`www.item`、`www.personalOther`、`www.orderDetail`、`www.createOrder`、`www.imItem`、`seller.orderDetail`、`seller.imItem`、`seller.accountCheckUser`

### 5. B5_STATIC_EVIDENCE_PASS

页面数：16。运行方式：`STATIC_EVIDENCE_ONLY`。默认结果状态：`static-described`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`www.paySuccess`、`www.publishScene`、`www.publishEdit`、`www.accountApi`、`www.loginRedirect`、`www.findAccount`、`www.selectAccount`、`www.loginValidation`、`www.commonVideo`、`www.commonVideoLayout`、`www.upgradeBrowser`、`www.playground`、`www.yhbCreateOrder`、`www.yhbOrderDetail`、`seller.notificationApi`、`seller.playground`

### 6. B6_SHELL_BOUNDARY_PASS

页面数：2。运行方式：`SHELL_BOUNDARY_ONLY`。默认结果状态：`shell-described`、`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：`seller.login`、`seller.iframe`

### 7. B7_UNKNOWN_PAGE_TRIAGE

页面数：0。运行方式：`UNKNOWN_STOP`。默认结果状态：`passed-read-only`、`stopped-state`、`stopped-action`、`privacy-rejected`。

记录口径：只写尝试数、通过数、停止类别、隐私检查是否通过；页面内容只写结构类别。

页面：无固定页面；只做 Profile 预检或未知页收口。

## 66 页空白结果模板

| 页面 | 批次 | 入口模式 | 运行方式 | 首次默认状态 | 默认停止类别 | 脱敏 |
| --- | --- | --- | --- | --- | --- | --- |
| `www.home` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 否 |
| `www.search` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 否 |
| `www.machFeeds` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 否 |
| `www.item` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `www.personalOther` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `www.personalSelf` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.collection` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.bought` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.orderDetail` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `www.createOrder` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `www.paySuccess` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.publish` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.publishScene` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.publishEdit` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.im` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.imItem` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `www.account` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.accountApi` | `B5_STATIC_EVIDENCE_PASS` | `INTERNAL_OR_MODULE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.feedback` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.changelog` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 否 |
| `www.login` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `www.loginRedirect` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.findAccount` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.selectAccount` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.loginValidation` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.commonVideo` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 否 |
| `www.commonVideoLayout` | `B5_STATIC_EVIDENCE_PASS` | `INTERNAL_OR_MODULE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.upgradeBrowser` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 否 |
| `www.playground` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.yhbCreateOrder` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `www.yhbOrderDetail` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `seller.dataOverview` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.commodityData` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.fanData` | `B1_LOW_RISK_LIVE_STRUCTURE` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.customerServiceData` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.itemPublish` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.goodsManage` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.postTemplate` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.postTemplateCreate` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.orderManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.orderDetail` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `seller.refundManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.evaluationManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.complaintManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.refundAddress` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.incomeBill` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.expenseBill` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.invoiceApply` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.basicInfo` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.subAccount` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.csDispatch` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.securityCenter` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.adHome` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.notificationCenter` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.notificationApi` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |
| `seller.im` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.imItem` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `seller.imDesktop` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.download` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_ENTRY_BOUNDARY_READ` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.selectSite` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.accountCheck` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.accountCheckUser` | `B4_USER_CONTEXT_REQUIRED_PASS` | `USER_CONTEXT_REQUIRED` | `WAIT_FOR_USER_CONTEXT` | `needs-user-context` | `context-stop-until-user-supplies-route` | 是 |
| `seller.login` | `B6_SHELL_BOUNDARY_PASS` | `SHELL_BOUNDARY_ONLY` | `SHELL_BOUNDARY_ONLY` | `shell-described` | `shell-boundary` | 是 |
| `seller.noPermission` | `B2_FORM_AND_SHELL_LIVE_PASS` | `DIRECT_LIVE_READ_ONLY` | `LIVE_READ_ONLY` | `pending-read-only-observation` | `stop-if-state-or-action-escalates` | 是 |
| `seller.iframe` | `B6_SHELL_BOUNDARY_PASS` | `SHELL_BOUNDARY_ONLY` | `SHELL_BOUNDARY_ONLY` | `shell-described` | `shell-boundary` | 是 |
| `seller.playground` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `STATIC_EVIDENCE_ONLY` | `static-described` | `static-only` | 是 |

## 单页登记模板

```text
runId: run-YYYYMMDD-01
accountSlot: account-01
browserProfileAlias: profile-alias-only
batchId: B1_LOW_RISK_LIVE_STRUCTURE
pageId: www.home
routeShape: /
entryMode: DIRECT_LIVE_READ_ONLY
runMode: LIVE_READ_ONLY
resultStatus: passed-read-only / stopped-state / stopped-action / privacy-rejected
stateCategory: S0-S10 category only
anchorsObserved: anchor names only
labelMatches: lexicon group ids only
controlCategories: C0-C4 categories only
fieldRiskSummary: F0-F4 categories only
actionGateSummary: G0-G4 categories only
stopReasonCategory: none / state-stop / action-stop / privacy-stop / context-stop / static-only / shell-boundary / unknown-route
changeDecision: same-baseline / allowed-drift / review-required / stop-required
privacyCheckPassed: true / false
```

## 批次汇总模板

```text
batchId: B1_LOW_RISK_LIVE_STRUCTURE
accountSlot: account-01
browserProfileAlias: profile-alias-only
pagesAttempted: number only
pagesPassedReadOnly: number only
pagesStoppedByState: number only
pagesStoppedByAction: number only
pagesNeedUserContext: number only
pagesStaticDescribed: number only
pagesShellDescribed: number only
pagesPrivacyRejected: number only
privacyCheckPassed: true / false
```

## 质量门

1. 任何一条记录只要触碰真实个人、交易、经营、图片、二维码或登录材料，就标 `privacy-rejected` 并丢弃明细。
2. 任何未知中文文案如果不能被词典归类，就先按 `UNKNOWN_STOP` 处理。
3. 任何 `S4/S5/S6/S7/S9/S10` 状态都先停，不继续点。
4. 任何 `C3/C4` 控件或 `G3/G4` 动作都先停，不执行。
5. `needs-user-context` 页面只能用用户给出的 URL 或上下文，不能自己编参数。
6. `static-described` 和 `shell-described` 不算 live 操作通过，只算解释或边界确认。
7. `privacyCheckPassed=false` 的记录不能进入覆盖统计。

结论：这份登记手册把“看过一个账号以后效果如何”变成可复用台账。后面每换一个账号/Profile，只填同一套状态和类别，就能比较页面覆盖、权限差异、空态差异和停止原因，同时不保存敏感内容。
