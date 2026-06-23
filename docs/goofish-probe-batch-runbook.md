# 闲鱼页面巡检批次手册

日期：2026-06-22  
用途：把 66 个页面和未知页面处理拆成可执行巡检批次。适合在一个已经登录好的浏览器 Profile 下，按安全顺序继续熟悉页面结构。  
边界：只使用 `accountSlot` 和 `browserProfileAlias` 占位名；不保存真实账号、密码、验证码、二维码内容、cookie、token、localStorage、sessionStorage、订单、地址、聊天、商品标题、金额或经营数据。

## 批次顺序

| 顺序 | 批次 | 页面数 | 是否可自动进入 | 运行方式 | 说明 |
| ---: | --- | ---: | --- | --- | --- |
| 0 | `B0_SESSION_PREFLIGHT` | 0 | 否 | `PREFLIGHT_ONLY` | Confirm browser profile, domain, login boundary, and output redaction before opening page batches. |
| 1 | `B1_LOW_RISK_LIVE_STRUCTURE` | 8 | 是 | `LIVE_READ_ONLY` | Open low-risk or public-ish live pages first and collect route, anchors, tabs, labels, and structural controls. |
| 2 | `B2_FORM_AND_SHELL_LIVE_PASS` | 14 | 是 | `LIVE_READ_ONLY` | Collect field labels, validation categories, upload zones, empty states, shell anchors, and stop before drafts become actions. |
| 3 | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | 18 | 是 | `LIVE_READ_ONLY` | Collect only tabs, filters, headers, button categories, status categories, and modal categories from transaction, finance, permission, security, message, and promotion pages. |
| 4 | `B4_USER_CONTEXT_REQUIRED_PASS` | 8 | 否 | `WAIT_FOR_USER_CONTEXT` | Do not guess parameters. Use only user-provided URLs or business context and record route shape, required parameter type, and risk boundary. |
| 5 | `B5_STATIC_EVIDENCE_PASS` | 16 | 否 | `STATIC_EVIDENCE_ONLY` | Explain static routes, modules, Page signals, API families, and risk boundaries without live navigation. |
| 6 | `B6_SHELL_BOUNDARY_PASS` | 2 | 否 | `SHELL_BOUNDARY_ONLY` | Identify login, iframe, embedded, or container boundaries and stop before embedded or external actions. |
| 7 | `B7_UNKNOWN_PAGE_TRIAGE` | 0 | 否 | `UNKNOWN_STOP` | Classify unknown URL/hash/grey pages using classifier rules and record only route shape, inferred family, state category, anchors, and stop reason. |

## 全局停止边界

- credential capture
- QR content capture
- cookie/token/storage access
- private value logging
- submit
- send
- pay
- refund
- ship
- export
- download
- upload
- save
- publish
- delete
- switch account
- verify identity
- change permission
- install
- direct API call

## 批次详情

### 0. B0_SESSION_PREFLIGHT

目的：Confirm browser profile, domain, login boundary, and output redaction before opening page batches.

是否可自动进入：否，需要用户上下文、静态解释或边界识别。
脱敏页数：0 / 0。
页面族：无页面族。
可读控件：无。
停止控件：无。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| 无固定页面 | 按本批说明执行 | - | - | - | - |

### 1. B1_LOW_RISK_LIVE_STRUCTURE

目的：Open low-risk or public-ish live pages first and collect route, anchors, tabs, labels, and structural controls.

是否可自动进入：是，只读进入。
脱敏页数：4 / 8。
页面族：`buyer-account`、`public-content`、`public-discovery`、`seller-data`。
可读控件：`C0_DISPLAY_NAV`、`C1_FILTER_READ`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `www.home` | `/` | `SAFE_READ` | `G0` | `search box`、`channel entries`、`recommended item cards` | `S6_QR_OR_APP_BRIDGE` |
| `www.search` | `/search?q=...` | `SAFE_READ` | `G0` | `query box`、`sort controls`、`price inputs` | `S6_QR_OR_APP_BRIDGE` |
| `www.machFeeds` | `/mach-feeds?machId=...&publishTimes=...` | `SAFE_READ` | `G0` | `channel title`、`waterfall feed`、`item-card links` | `S6_QR_OR_APP_BRIDGE` |
| `www.personalSelf` | `/personal` | `SAFE_READ` | `G1` | `left navigation`、`home tab`、`item/credit/manage tabs` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.collection` | `/collection` | `SAFE_READ` | `G1` | `collection tab`、`item cards`、`uncollect button` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.changelog` | `/changelog` | `SAFE_READ` | `G0` | `update-log title`、`feature entries` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.dataOverview` | `#/seller-data/data` | `SAFE_READ` | `G1` | `date controls`、`metric cards`、`trend charts` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.fanData` | `#/seller-data/fanData` | `SAFE_READ` | `G1` | `date`、`fan metrics`、`profile distributions` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |

### 2. B2_FORM_AND_SHELL_LIVE_PASS

目的：Collect field labels, validation categories, upload zones, empty states, shell anchors, and stop before drafts become actions.

是否可自动进入：是，只读进入。
脱敏页数：14 / 14。
页面族：`draft-input`、`identity`、`message`、`seller-data`、`seller-gate`、`seller-item`、`seller-shell`。
可读控件：`C0_DISPLAY_NAV`、`C2_DRAFT_INPUT`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `www.publish` | `/publish` | `READ_WITH_REDACTION` | `G2` | `image/video uploader`、`description`、`category` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `www.im` | `/im` | `READ_WITH_REDACTION` | `G2` | `empty state`、`session list`、`input area` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `www.feedback` | `/feedback?from=...` | `READ_WITH_REDACTION` | `G2` | `feedback type`、`source page option`、`text area` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `www.login` | `/login` | `READ_WITH_REDACTION` | `G4` | `login method`、`scan container`、`verification entry` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `seller.commodityData` | `#/seller-data/commodity` | `READ_WITH_REDACTION` | `G1` | `search`、`date`、`commodity table` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.customerServiceData` | `#/seller-data/customerService` | `READ_WITH_REDACTION` | `G1` | `consultation metrics`、`satisfaction fields`、`customer-service table` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.itemPublish` | `#/seller-item/publish` | `READ_WITH_REDACTION` | `G2` | `image/video uploader`、`title/description`、`category` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.goodsManage` | `#/seller-item/goods-manage` | `READ_WITH_REDACTION` | `G2` | `status tabs`、`search/filter`、`item table` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.postTemplate` | `#/seller-item/post-temple` | `READ_WITH_REDACTION` | `G2` | `template list`、`create entry`、`operation column` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.postTemplateCreate` | `#/seller-item/post-temple/create` | `READ_WITH_REDACTION` | `G2` | `template name`、`shipping location`、`billing mode` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.download` | `#/download` | `READ_WITH_REDACTION` | `G1` | `download button`、`client type` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.selectSite` | `#/select-site` | `READ_WITH_REDACTION` | `G4` | `site/identity list`、`selection button` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `seller.accountCheck` | `#/account-check` | `READ_WITH_REDACTION` | `G4` | `account check`、`continue`、`re-login` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `seller.noPermission` | `#/no-permission` | `READ_WITH_REDACTION` | `G4` | `no-permission message`、`return/jump controls` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |

### 3. B3_HIGH_RISK_LIVE_REDACTED_PASS

目的：Collect only tabs, filters, headers, button categories, status categories, and modal categories from transaction, finance, permission, security, message, and promotion pages.

是否可自动进入：是，只读进入。
脱敏页数：18 / 18。
页面族：`buyer-trade`、`identity`、`seller-account`、`seller-ad`、`seller-finance`、`seller-message`、`seller-security`、`seller-shell`、`seller-trade`。
可读控件：`C0_DISPLAY_NAV`、`C2_DRAFT_INPUT`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `www.bought` | `/bought` | `READ_WITH_REDACTION` | `G1` | `order tabs`、`order cards`、`more menu` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.account` | `/account` | `READ_WITH_REDACTION` | `G4` | `basic info module`、`stay signed in`、`notice switch` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `seller.orderManage` | `#/seller-trade/order-manage` | `READ_WITH_REDACTION` | `G1` | `order-status tabs`、`search conditions`、`date` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.refundManage` | `#/seller-trade/refund-manage` | `READ_WITH_REDACTION` | `G1` | `refund type`、`status filter`、`reason` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.evaluationManage` | `#/seller-trade/evaluation-manage` | `READ_WITH_REDACTION` | `G1` | `evaluation filters`、`evaluation table`、`batch review` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.complaintManage` | `#/seller-trade/complaint-manage` | `READ_WITH_REDACTION` | `G1` | `complaint status`、`complaint table`、`detail/proof entry` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.refundAddress` | `#/seller-trade/refund-address` | `READ_WITH_REDACTION` | `G1` | `address table`、`default status`、`operation column` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.incomeBill` | `#/seller-finance/income-bill` | `READ_WITH_REDACTION` | `G1` | `month/day/detail tabs`、`date`、`business type` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.expenseBill` | `#/seller-finance/expense-bill` | `READ_WITH_REDACTION` | `G1` | `month/day/detail tabs`、`expense type`、`bill table` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.invoiceApply` | `#/seller-finance/invoice-apply` | `READ_WITH_REDACTION` | `G1` | `pending/applied/legacy tabs`、`business type`、`apply` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.basicInfo` | `#/seller-finance/basic-info` | `READ_WITH_REDACTION` | `G1` | `invoice entity form`、`edit/save` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.subAccount` | `#/seller-account/sub-account` | `READ_WITH_REDACTION` | `G1` | `sub-account table`、`role`、`status` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.csDispatch` | `#/im-cs-dispatch/customer-routing-service` | `READ_WITH_REDACTION` | `G1` | `groups`、`reception scope`、`participating service agents` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.securityCenter` | `#/seller-sc/home` | `READ_WITH_REDACTION` | `G1` | `violation table`、`penalty status`、`appeal status` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.adHome` | `#/seller-ad/home` | `READ_WITH_REDACTION` | `G1` | `date`、`promotion metrics`、`plan entry` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.notificationCenter` | `#/notification-center` | `READ_WITH_REDACTION` | `G1` | `notification list`、`unread status`、`detail entry` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `seller.im` | `#/im` | `READ_WITH_REDACTION` | `G2` | `session list`、`search`、`input area` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `seller.imDesktop` | `#/im-desktop` | `READ_WITH_REDACTION` | `G1` | `download/open client prompt` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |

### 4. B4_USER_CONTEXT_REQUIRED_PASS

目的：Do not guess parameters. Use only user-provided URLs or business context and record route shape, required parameter type, and risk boundary.

是否可自动进入：否，需要用户上下文、静态解释或边界识别。
脱敏页数：8 / 8。
页面族：`buyer-trade`、`item-detail`、`message`、`public-profile`、`seller-gate`、`seller-message`、`seller-trade`。
可读控件：`C0_DISPLAY_NAV`、`C2_DRAFT_INPUT`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `www.item` | `/item?id=...&categoryId=...` | `REQUIRES_USER_CONTEXT` | `G1` | `image area`、`price area`、`assurance labels` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `www.personalOther` | `/personal?userId=...` | `REQUIRES_USER_CONTEXT` | `G1` | `public profile block`、`credit area`、`item list` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.orderDetail` | `/order-detail?orderId=...` | `REQUIRES_USER_CONTEXT` | `G1` | `status nodes`、`order field labels`、`logistics module` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.createOrder` | `/create-order?itemId=...` | `REQUIRES_USER_CONTEXT` | `G1` | `sku`、`quantity`、`address fields` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.imItem` | `/im?itemId=...&peerUserId=...` | `REQUIRES_USER_CONTEXT` | `G2` | `item-linked chat parameters`、`input area` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `seller.orderDetail` | `#/seller-trade/order-manage/order-detail?orderId=...` | `REQUIRES_USER_CONTEXT` | `G1` | `status nodes`、`logistics`、`address-modification area` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` |
| `seller.imItem` | `#/im?itemId=...` | `REQUIRES_USER_CONTEXT` | `G2` | `item-linked message parameter` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `seller.accountCheckUser` | `#/account-check?userNick=...` | `REQUIRES_USER_CONTEXT` | `G4` | `account-check parameter` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |

### 5. B5_STATIC_EVIDENCE_PASS

目的：Explain static routes, modules, Page signals, API families, and risk boundaries without live navigation.

是否可自动进入：否，需要用户上下文、静态解释或边界识别。
脱敏页数：14 / 16。
页面族：`buyer-trade`、`draft-input`、`identity`、`internal-module`、`internal-test`、`public-content`。
可读控件：`C0_DISPLAY_NAV`、`C1_FILTER_READ`、`C2_DRAFT_INPUT`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `www.paySuccess` | `/pay-success?orderId=...&itemId=...` | `STATIC_ONLY` | `G1` | `payment result structure`、`order-detail entry`、`recommendations` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.publishScene` | `/publish?scene=xyPcMainPublish` | `STATIC_ONLY` | `G2` | `publish scene parameter`、`publish form fields` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `www.publishEdit` | `/publish?scene=xyPcMainPublish&itemId=...` | `STATIC_ONLY` | `G2` | `item context parameter`、`publish/edit form fields` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` |
| `www.accountApi` | `/account/api` | `STATIC_ONLY` | `G4` | `module path` | 无 |
| `www.loginRedirect` | `/login?spm=...&redirectURL=...` | `STATIC_ONLY` | `G4` | `redirect parameter` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `www.findAccount` | `/find-account` | `STATIC_ONLY` | `G4` | `account recovery placeholder`、`redirect behavior` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `www.selectAccount` | `/select-account` | `STATIC_ONLY` | `G4` | `account selection placeholder`、`redirect behavior` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `www.loginValidation` | `/login-validation` | `STATIC_ONLY` | `G4` | `login validation placeholder` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `www.commonVideo` | `/common-video` | `STATIC_ONLY` | `G0` | `video container`、`title/material config`、`playback controls` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `www.commonVideoLayout` | `/common-video/layout` | `STATIC_ONLY` | `G4` | `layout package path` | 无 |
| `www.upgradeBrowser` | `/upgrade-browser` | `STATIC_ONLY` | `G0` | `browser recommendation list`、`download entry` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |
| `www.playground` | `/playground` | `STATIC_ONLY` | `G4` | `internal test entry`、`login/upload/qr/payment test controls` | `S10_HIGH_RISK_BUSINESS_STATE` |
| `www.yhbCreateOrder` | `create-order-yhb package` | `STATIC_ONLY` | `G1` | `YHB order render fields`、`YHB order create interface` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `www.yhbOrderDetail` | `order-detail-yhb package` | `STATIC_ONLY` | `G1` | `report fields`、`dispute fields`、`review-related fields` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` |
| `seller.notificationApi` | `#/notification-center/api*` | `STATIC_ONLY` | `G4` | `internal API/interface module` | 无 |
| `seller.playground` | `#/playground` | `STATIC_ONLY` | `G4` | `test entry` | `S10_HIGH_RISK_BUSINESS_STATE` |

### 6. B6_SHELL_BOUNDARY_PASS

目的：Identify login, iframe, embedded, or container boundaries and stop before embedded or external actions.

是否可自动进入：否，需要用户上下文、静态解释或边界识别。
脱敏页数：2 / 2。
页面族：`seller-gate`、`seller-shell`。
可读控件：`C0_DISPLAY_NAV`。
停止控件：`C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT`。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| `seller.login` | `#/login` | `SHELL_ONLY` | `G4` | `login`、`scan`、`verification entry` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` |
| `seller.iframe` | `#/iframe?url=...` | `SHELL_ONLY` | `G1` | `iframe source`、`loading/failure state` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` |

### 7. B7_UNKNOWN_PAGE_TRIAGE

目的：Classify unknown URL/hash/grey pages using classifier rules and record only route shape, inferred family, state category, anchors, and stop reason.

是否可自动进入：否，需要用户上下文、静态解释或边界识别。
脱敏页数：0 / 0。
页面族：无页面族。
可读控件：无。
停止控件：无。

| 页面 | 路由形状 | 流转 | 门禁 | 等待锚点 | 停止状态 |
| --- | --- | --- | --- | --- | --- |
| 无固定页面 | 按本批说明执行 | - | - | - | - |

## 批次结果格式

```text
batchId: <B0-B7>
accountSlot: account-01
browserProfileAlias: profile-alias-only
pagesAttempted: <number>
pagesPassed: <number>
pagesStopped: <number>
pagesSkipped: <number>
stopReasons: <category strings only>
privacyCheckPassed: true / false
```

## 执行建议

1. 每个账号/Profile 先做 B0，不通过就不要跑页面。
2. B1 到 B3 可以在登录状态稳定时只读执行，但 B3 输出必须脱敏。
3. B4 只在用户给出具体 URL 或上下文时执行，不猜参数。
4. B5 只做静态说明，不为了覆盖率打开内部页。
5. B6 只认外壳边界，不进入 iframe、登录、下载或外部承接动作。
6. B7 是未知页面收口，不把陌生页当作已知安全页。
7. 任意批次出现 C3/C4 控件、G3/G4 动作或 S4/S5/S6/S7/S9/S10 状态，都记录原因后停。

结论：这份批次手册把“继续熟悉所有页面”变成可重复的 Profile 巡检流程。它让页面探索从低风险结构开始，逐步进入表单、高风险只读、上下文页、静态页和外壳页。
