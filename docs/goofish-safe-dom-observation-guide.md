# 闲鱼安全 DOM 观察手册

日期：2026-06-22  
用途：把实际打开页面后的 DOM 观察动作压成统一口径。后续用浏览器继续熟悉页面时，只采结构标签和状态类别，不采真实业务值。  
边界：不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、密码、验证码、cookie、token、localStorage 或 sessionStorage。

## 观察顺序

1. Normalize URL to routeShape and classify page id or UNKNOWN_PAGE.
2. Drop private parameter values before DOM observation.
3. Compare route, anchors, parameters, controls and state against `goofish-page-change-sentinel.json` when a known page looks different.
4. Classify visible Chinese labels with `goofish-visible-label-lexicon.json`; unresolved or ambiguous labels keep the higher-risk candidate until context proves otherwise.
5. Wait for page-specific waitForAnchors or known empty/error state.
6. Classify current state into S0-S10.
7. If stop state is active, record state category and stop.
8. Read only labels and categories from allowedOutputFields.
9. Classify visible controls into readable C0-C2 or stopping C3-C4 categories.
10. If C3/C4 or G3/G4 is visible, record category and stop before action.
11. Apply textRedactionRules and outputBlacklist before saving.
12. Save result only if privacyCheckPassed is true.

## 控件风险层

| 层级 | 含义 | 可记录 | 默认门禁 |
| --- | --- | --- | --- |
| `C0_DISPLAY_NAV` | Navigation, labels, headings, tabs, cards, empty-state containers, close/back/cancel controls. | `visibleLabel`、`roleCategory`、`stateCategory`、`selectedState` | `G0` |
| `C1_FILTER_READ` | Search, sort, filters, date ranges, pagination, non-mutating tab changes. | `fieldName`、`optionNames`、`selectedCategory`、`placeholderCategory` | `G1` |
| `C2_DRAFT_INPUT` | Text, number, template, message, feedback, listing, or appeal draft controls. | `fieldName`、`inputType`、`validationCategory`、`placeholderCategory` | `G2` |
| `C3_FILE_EXTERNAL` | Upload, download, export, QR, app bridge, desktop client, external URL, iframe target. | `controlName`、`fileActionCategory`、`targetCategory` | `G3` |
| `C4_BUSINESS_COMMIT` | Submit, save, publish, send, pay, refund, ship, delete, permission, identity, promotion, dispute actions. | `buttonName`、`actionCategory`、`consequenceCategory` | `G4` |

说明：C0-C2 是可读或草稿层；C3-C4 只能记录类别和停止原因，不能触发。

## 脱敏规则

| 规则 | 命中类别 | 处理 |
| --- | --- | --- |
| `drop-private-values` | account/order/address/chat/item-title/amount/business-metric/image-url/qr/login-material | drop value; keep field or button label only |
| `parameter-shape-only` | URL query or hash parameter | keep parameter name and risk category; drop concrete value |
| `table-header-only` | table/list/grid rows | keep headers and status category; do not keep row values |
| `card-structure-only` | item/order/message/cards | keep card slots and button categories; drop identity text and image URLs |
| `modal-category-only` | modal/dialog/drawer/toast | keep modal type, cancel control, confirm action category; drop private body values |
| `form-schema-only` | form/input/select/upload | keep label, input type, validation category; drop entered values |
| `qr-and-storage-never` | QR content, cookie, token, localStorage, sessionStorage | never read or persist |

## 停止触发器

| 规则 | 来源 | 值 | 处理 |
| --- | --- | --- | --- |
| `state-stop` | `state` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | stop or record category only |
| `gate-stop` | `actionGate` | `G3`、`G4` | ask for explicit user confirmation or stop |
| `control-stop` | `controlRisk` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | record control category only; do not trigger |
| `private-param-stop` | `parameterRiskRules` | `order-id-param`、`item-id-param`、`user-param`、`chat-param`、`address-logistics-param`、`invoice-finance-param`、`redirect-param`、`scene-source-param` | redact parameter value and require context when private |
| `unknown-stop` | `classifierFallback` | `UNKNOWN_PAGE_STOP_OR_READ_STRUCTURE_ONLY` | record route shape and stop reason only |

## 可保存结果格式

```text
pageId: known id or UNKNOWN_PAGE
routeShape: path/hash without private values
surface: www | seller | h5-app-bridge | external | unknown
family: known family or unknown
runMode: LIVE_READ_ONLY | WAIT_FOR_USER_CONTEXT | STATIC_EVIDENCE_ONLY | SHELL_BOUNDARY_ONLY | UNKNOWN_STOP
stateCategory: S0-S10 only
anchorNames: string[] structural labels only
tabNames: string[] labels only
fieldNames: string[] labels only
tableHeaders: string[] labels only
buttonNames: string[] labels only
controlCategories: C0-C4 categories only
statusCategories: string[] categories only
stopPoints: string[] stop categories
stopReason: string, no private values
passEvidence: string[] structural proof only
privacyCheckPassed: boolean; must be true before persisting
```

## 按页面运行方式观察

| 运行方式 | 页面数 | 处理 |
| --- | ---: | --- |
| `LIVE_READ_ONLY` | 40 | 打开页面，只读结构锚点、tab、字段名、表头、按钮名和状态类别。 |
| `WAIT_FOR_USER_CONTEXT` | 8 | 等用户给具体 URL 或上下文；不猜参数，不展开私有值。 |
| `STATIC_EVIDENCE_ONLY` | 16 | 只从静态证据记录模块、路由和风险边界，不强行打开。 |
| `SHELL_BOUNDARY_ONLY` | 2 | 只识别登录、iframe、下载、外部承接等容器边界。 |

## 页面观察计划摘要

| 页面 | 运行方式 | 等待锚点 | 可读控件 | 停止控件 | 停止状态 | 脱敏 |
| --- | --- | --- | --- | --- | --- | --- |
| `www.home` | `LIVE_READ_ONLY` | `search box`、`channel entries`、`recommended item cards`、`sidebar tools` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | 否 |
| `www.search` | `LIVE_READ_ONLY` | `query box`、`sort controls`、`price inputs`、`filter tags` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | 否 |
| `www.machFeeds` | `LIVE_READ_ONLY` | `channel title`、`waterfall feed`、`item-card links` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | 否 |
| `www.item` | `WAIT_FOR_USER_CONTEXT` | `image area`、`price area`、`assurance labels`、`seller card` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.personalOther` | `WAIT_FOR_USER_CONTEXT` | `public profile block`、`credit area`、`item list`、`follow/contact entries` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | 是 |
| `www.personalSelf` | `LIVE_READ_ONLY` | `left navigation`、`home tab`、`item/credit/manage tabs`、`filters` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | 是 |
| `www.collection` | `LIVE_READ_ONLY` | `collection tab`、`item cards`、`uncollect button`、`want button` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | 是 |
| `www.bought` | `LIVE_READ_ONLY` | `order tabs`、`order cards`、`more menu`、`logistics record` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.orderDetail` | `WAIT_FOR_USER_CONTEXT` | `status nodes`、`order field labels`、`logistics module`、`after-sale entry` | `C0_DISPLAY_NAV` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.createOrder` | `WAIT_FOR_USER_CONTEXT` | `sku`、`quantity`、`address fields`、`price-detail block` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.paySuccess` | `STATIC_EVIDENCE_ONLY` | `payment result structure`、`order-detail entry`、`recommendations` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.publish` | `LIVE_READ_ONLY` | `image/video uploader`、`description`、`category`、`properties` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.publishScene` | `STATIC_EVIDENCE_ONLY` | `publish scene parameter`、`publish form fields` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.publishEdit` | `STATIC_EVIDENCE_ONLY` | `item context parameter`、`publish/edit form fields` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.im` | `LIVE_READ_ONLY` | `empty state`、`session list`、`input area`、`toolbar` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.imItem` | `WAIT_FOR_USER_CONTEXT` | `item-linked chat parameters`、`input area` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.account` | `LIVE_READ_ONLY` | `basic info module`、`stay signed in`、`notice switch`、`verification entry` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.accountApi` | `STATIC_EVIDENCE_ONLY` | `module path` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | 无 | 是 |
| `www.feedback` | `LIVE_READ_ONLY` | `feedback type`、`source page option`、`text area`、`screenshot upload` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `www.changelog` | `LIVE_READ_ONLY` | `update-log title`、`feature entries` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 否 |
| `www.login` | `LIVE_READ_ONLY` | `login method`、`scan container`、`verification entry`、`redirect parameter` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.loginRedirect` | `STATIC_EVIDENCE_ONLY` | `redirect parameter` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.findAccount` | `STATIC_EVIDENCE_ONLY` | `account recovery placeholder`、`redirect behavior` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.selectAccount` | `STATIC_EVIDENCE_ONLY` | `account selection placeholder`、`redirect behavior` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.loginValidation` | `STATIC_EVIDENCE_ONLY` | `login validation placeholder` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `www.commonVideo` | `STATIC_EVIDENCE_ONLY` | `video container`、`title/material config`、`playback controls` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 否 |
| `www.commonVideoLayout` | `STATIC_EVIDENCE_ONLY` | `layout package path` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | 无 | 是 |
| `www.upgradeBrowser` | `STATIC_EVIDENCE_ONLY` | `browser recommendation list`、`download entry` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 否 |
| `www.playground` | `STATIC_EVIDENCE_ONLY` | `internal test entry`、`login/upload/qr/payment test controls` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.yhbCreateOrder` | `STATIC_EVIDENCE_ONLY` | `YHB order render fields`、`YHB order create interface` | `C0_DISPLAY_NAV` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `www.yhbOrderDetail` | `STATIC_EVIDENCE_ONLY` | `report fields`、`dispute fields`、`review-related fields` | `C0_DISPLAY_NAV` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.dataOverview` | `LIVE_READ_ONLY` | `date controls`、`metric cards`、`trend charts`、`info popovers` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.commodityData` | `LIVE_READ_ONLY` | `search`、`date`、`commodity table`、`metric columns` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.fanData` | `LIVE_READ_ONLY` | `date`、`fan metrics`、`profile distributions`、`region/user-group modules` | `C0_DISPLAY_NAV`、`C1_FILTER_READ` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.customerServiceData` | `LIVE_READ_ONLY` | `consultation metrics`、`satisfaction fields`、`customer-service table`、`export` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.itemPublish` | `LIVE_READ_ONLY` | `image/video uploader`、`title/description`、`category`、`sku` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.goodsManage` | `LIVE_READ_ONLY` | `status tabs`、`search/filter`、`item table`、`bulk actions` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.postTemplate` | `LIVE_READ_ONLY` | `template list`、`create entry`、`operation column`、`delete/default confirmation` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.postTemplateCreate` | `LIVE_READ_ONLY` | `template name`、`shipping location`、`billing mode`、`region modal` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.orderManage` | `LIVE_READ_ONLY` | `order-status tabs`、`search conditions`、`date`、`order table` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.orderDetail` | `WAIT_FOR_USER_CONTEXT` | `status nodes`、`logistics`、`address-modification area`、`trade messages` | `C0_DISPLAY_NAV` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.refundManage` | `LIVE_READ_ONLY` | `refund type`、`status filter`、`reason`、`logistics` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.evaluationManage` | `LIVE_READ_ONLY` | `evaluation filters`、`evaluation table`、`batch review`、`report/contact` | `C0_DISPLAY_NAV` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.complaintManage` | `LIVE_READ_ONLY` | `complaint status`、`complaint table`、`detail/proof entry` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.refundAddress` | `LIVE_READ_ONLY` | `address table`、`default status`、`operation column`、`add/edit/delete` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.incomeBill` | `LIVE_READ_ONLY` | `month/day/detail tabs`、`date`、`business type`、`bill table` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.expenseBill` | `LIVE_READ_ONLY` | `month/day/detail tabs`、`expense type`、`bill table`、`export/download` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.invoiceApply` | `LIVE_READ_ONLY` | `pending/applied/legacy tabs`、`business type`、`apply`、`export` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.basicInfo` | `LIVE_READ_ONLY` | `invoice entity form`、`edit/save` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.subAccount` | `LIVE_READ_ONLY` | `sub-account table`、`role`、`status`、`routing config` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.csDispatch` | `LIVE_READ_ONLY` | `groups`、`reception scope`、`participating service agents`、`switch` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.securityCenter` | `LIVE_READ_ONLY` | `violation table`、`penalty status`、`appeal status`、`detail/appeal` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.adHome` | `LIVE_READ_ONLY` | `date`、`promotion metrics`、`plan entry`、`carousel controls` | `C0_DISPLAY_NAV` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | 是 |
| `seller.notificationCenter` | `LIVE_READ_ONLY` | `notification list`、`unread status`、`detail entry`、`mark read/clear unread` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.notificationApi` | `STATIC_EVIDENCE_ONLY` | `internal API/interface module` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | 无 | 是 |
| `seller.im` | `LIVE_READ_ONLY` | `session list`、`search`、`input area`、`toolbar` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.imItem` | `WAIT_FOR_USER_CONTEXT` | `item-linked message parameter` | `C0_DISPLAY_NAV`、`C2_DRAFT_INPUT` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.imDesktop` | `LIVE_READ_ONLY` | `download/open client prompt` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.download` | `LIVE_READ_ONLY` | `download button`、`client type` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.selectSite` | `LIVE_READ_ONLY` | `site/identity list`、`selection button` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `seller.accountCheck` | `LIVE_READ_ONLY` | `account check`、`continue`、`re-login`、`switch` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `seller.accountCheckUser` | `WAIT_FOR_USER_CONTEXT` | `account-check parameter` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `seller.login` | `SHELL_BOUNDARY_ONLY` | `login`、`scan`、`verification entry` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `seller.noPermission` | `LIVE_READ_ONLY` | `no-permission message`、`return/jump controls` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | 是 |
| `seller.iframe` | `SHELL_BOUNDARY_ONLY` | `iframe source`、`loading/failure state` | `C0_DISPLAY_NAV` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | 是 |
| `seller.playground` | `STATIC_EVIDENCE_ONLY` | `test entry` | `C0_DISPLAY_NAV` | `C4_BUSINESS_COMMIT` | `S10_HIGH_RISK_BUSINESS_STATE` | 是 |

## 结果保存前检查

- 只保存 route shape，不保存真实参数值。
- 只保存字段名、按钮名、tab 名、表头和状态类别，不保存行值、卡片值、聊天正文或商品标题。
- 只保存图片/二维码/文件的类别，不保存 URL、内容或文件本身。
- 看到 C3/C4 控件、G3/G4 动作或 S4/S5/S6/S7/S9/S10 状态时，记录原因后停止。
- `privacyCheckPassed` 不是 true，就不要把观察结果落盘。

结论：这份手册把浏览器里“看页面”的动作限制在结构层。它让后续继续熟悉页面时可复查、可自动化，也能避免误碰交易、消息、财务、权限、登录和文件边界。
