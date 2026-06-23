# 闲鱼页面变更哨兵

日期：2026-06-22  
用途：给 66 个已知闲鱼页面建立一套变更判断基线。后续页面改版、灰度、权限变化或多账号差异出现时，用它判断是可接受的结构漂移，还是需要停止、重新分类或要求用户上下文。  
边界：只比较路由形态、参数名、风险类别、结构锚点、tab、字段名、表头、按钮名、状态类别和控件类别；不保存真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、cookie、token、localStorage 或 sessionStorage。

总索引：`goofish-master-index.md`  
配套机器哨兵：`goofish-page-change-sentinel.json`  
配套 DOM 观察：`goofish-safe-dom-observation-schema.json` / `goofish-safe-dom-observation-guide.md`  
配套路由上下文：`goofish-route-context-catalog.json` / `goofish-route-context-catalog.md`  
配套未知页收口：`goofish-page-classifier-rules.json` / `goofish-unknown-page-triage.md`

## 总账

| 指标 | 数量 |
| --- | ---: |
| 页面基线 | 66 |
| 基线签名 | 66 |
| 变更规则类型 | 9 |
| 含停止规则的页面 | 66 |

## 监控层级

| 层级 | 数量 | 含义 |
| --- | ---: | --- |
| `S1_STRUCTURE_MONITOR` | 4 | Low-risk or public structure pages; accept layout and label drift, stop on private params or commit controls. |
| `S2_REDACTED_MONITOR` | 16 | Logged-in, data, finance, file or seller pages; compare structure only with redaction. |
| `S3_HIGH_RISK_READ_ONLY` | 19 | High-risk read-only pages; any action, state or private value escalation stops refresh. |
| `S3_CONTEXT_GATED` | 8 | Known page requires user-provided context; do not fabricate params. |
| `S4_STATIC_OR_MODULE` | 16 | Static, module or bundle-only signal; do not live probe merely for coverage. |
| `S4_BOUNDARY_ONLY` | 3 | Login, iframe, shell, app bridge or download boundary; identify boundary only. |

## 入口方式分布

| 入口方式 | 数量 |
| --- | ---: |
| `DIRECT_LIVE_READ_ONLY` | 39 |
| `USER_CONTEXT_REQUIRED` | 8 |
| `STATIC_EVIDENCE_ONLY` | 14 |
| `INTERNAL_OR_MODULE_ONLY` | 2 |
| `LIVE_ENTRY_BOUNDARY_READ` | 1 |
| `SHELL_BOUNDARY_ONLY` | 2 |

## 全局停止信号

- unknown route without classifier hit
- new order/user/chat/address/invoice/payment/redirect parameter
- S4/S5/S6/S7/S9/S10 state category
- new C3/C4 control category
- output blacklist hit
- attempt to live-probe static/module route
- attempt to enter shell/iframe/download target
- missing user-provided context for context-gated page

## 判定顺序

1. normalize route shape and parameter names
2. classify known page or UNKNOWN_PAGE
3. check entryMode and contextRequirement
4. compare anchors, states and control categories
5. apply alertRules before recording any update
6. persist only structural labels when privacyCheckPassed is true

## 逐页变更哨兵

| 页面 | 入口方式 | 监控层级 | 基线签名 | 观察锚点 | 停止控件 | 停止状态 | 变更规则 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `www.home` | `DIRECT_LIVE_READ_ONLY` | `S1_STRUCTURE_MONITOR` | `49845adf` | `search box`、`channel entries`、`recommended item cards`、`sidebar tools` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.search` | `DIRECT_LIVE_READ_ONLY` | `S1_STRUCTURE_MONITOR` | `8eee1cfa` | `query box`、`sort controls`、`price inputs`、`filter tags`、`item cards`、`pagination` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.machFeeds` | `DIRECT_LIVE_READ_ONLY` | `S1_STRUCTURE_MONITOR` | `2d43c3a9` | `channel title`、`waterfall feed`、`item-card links` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.item` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `031d0ad3` | `image area`、`price area`、`assurance labels`、`seller card`、`action buttons`、`recommendations` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `www.personalOther` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `3cf54d65` | `public profile block`、`credit area`、`item list`、`follow/contact entries` | `C4_BUSINESS_COMMIT` | `S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `www.personalSelf` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `93b286a1` | `left navigation`、`home tab`、`item/credit/manage tabs`、`filters` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.collection` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `7efc9bb1` | `collection tab`、`item cards`、`uncollect button`、`want button` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.bought` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `6952b4fd` | `order tabs`、`order cards`、`more menu`、`logistics record`、`snapshot entry` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.orderDetail` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `f77e3475` | `status nodes`、`order field labels`、`logistics module`、`after-sale entry` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `www.createOrder` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `211fe901` | `sku`、`quantity`、`address fields`、`price-detail block`、`payment area`、`scan-to-pay fallback` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `www.paySuccess` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `ed2d59bb` | `payment result structure`、`order-detail entry`、`recommendations` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.publish` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `a63a3f30` | `image/video uploader`、`description`、`category`、`properties`、`sku`、`price`、`location`、`shipping settings` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.publishScene` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `7028efb2` | `publish scene parameter`、`publish form fields` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.publishEdit` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `41fbbea1` | `item context parameter`、`publish/edit form fields` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.im` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `0356540d` | `empty state`、`session list`、`input area`、`toolbar`、`item/order card tools`、`file tool` | `C3_FILE_EXTERNAL` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.imItem` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `70af8534` | `item-linked chat parameters`、`input area` | `C3_FILE_EXTERNAL` | `S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `www.account` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `dee07e78` | `basic info module`、`stay signed in`、`notice switch`、`verification entry`、`security center` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.accountApi` | `INTERNAL_OR_MODULE_ONLY` | `S4_STATIC_OR_MODULE` | `1ff5e416` | `module path` | `C4_BUSINESS_COMMIT` | 无 | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.feedback` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `1d4de971` | `feedback type`、`source page option`、`text area`、`screenshot upload`、`submit` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S4_LOGIN_EXPIRED`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.changelog` | `DIRECT_LIVE_READ_ONLY` | `S1_STRUCTURE_MONITOR` | `68d57e48` | `update-log title`、`feature entries` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.login` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `fdb77aed` | `login method`、`scan container`、`verification entry`、`redirect parameter` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `www.loginRedirect` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `402bbe74` | `redirect parameter` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.findAccount` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `8f3521f5` | `account recovery placeholder`、`redirect behavior` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.selectAccount` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `d3e70a48` | `account selection placeholder`、`redirect behavior` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.loginValidation` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `5df729ec` | `login validation placeholder` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.commonVideo` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `a7f6c44e` | `video container`、`title/material config`、`playback controls` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.commonVideoLayout` | `INTERNAL_OR_MODULE_ONLY` | `S4_STATIC_OR_MODULE` | `22fbc9a8` | `layout package path` | `C4_BUSINESS_COMMIT` | 无 | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.upgradeBrowser` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `2fd9c4a5` | `browser recommendation list`、`download entry` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.playground` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `37c23492` | `internal test entry`、`login/upload/qr/payment test controls` | `C4_BUSINESS_COMMIT` | `S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.yhbCreateOrder` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `f49d0736` | `YHB order render fields`、`YHB order create interface` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `www.yhbOrderDetail` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `d9535aa0` | `report fields`、`dispute fields`、`review-related fields` | 无 | `S4_LOGIN_EXPIRED`、`S6_QR_OR_APP_BRIDGE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `seller.dataOverview` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `f2f5362d` | `date controls`、`metric cards`、`trend charts`、`info popovers` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.commodityData` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `74405a34` | `search`、`date`、`commodity table`、`metric columns`、`pagination`、`download` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.fanData` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `5705c846` | `date`、`fan metrics`、`profile distributions`、`region/user-group modules` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.customerServiceData` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `b5d90e58` | `consultation metrics`、`satisfaction fields`、`customer-service table`、`export` | `C3_FILE_EXTERNAL` | `S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.itemPublish` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `8deb0201` | `image/video uploader`、`title/description`、`category`、`sku`、`price`、`stock`、`shipping settings` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.goodsManage` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `1b3e8aaf` | `status tabs`、`search/filter`、`item table`、`bulk actions`、`operation column` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.postTemplate` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `cf2df6b6` | `template list`、`create entry`、`operation column`、`delete/default confirmation` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.postTemplateCreate` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `209a2928` | `template name`、`shipping location`、`billing mode`、`region modal`、`save` | `C3_FILE_EXTERNAL`、`C4_BUSINESS_COMMIT` | `S8_FORM_VALIDATION`、`S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.orderManage` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `31946ad5` | `order-status tabs`、`search conditions`、`date`、`order table`、`operation column` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.orderDetail` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `d04fb17d` | `status nodes`、`logistics`、`address-modification area`、`trade messages`、`operation buttons` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `seller.refundManage` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `9470e7c8` | `refund type`、`status filter`、`reason`、`logistics`、`operation column` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.evaluationManage` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `3a8f227a` | `evaluation filters`、`evaluation table`、`batch review`、`report/contact` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.complaintManage` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `39c783ba` | `complaint status`、`complaint table`、`detail/proof entry` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.refundAddress` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `c977dd22` | `address table`、`default status`、`operation column`、`add/edit/delete` | `C4_BUSINESS_COMMIT` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.incomeBill` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `b06c3bde` | `month/day/detail tabs`、`date`、`business type`、`bill table`、`export/download` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.expenseBill` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `a0d9d578` | `month/day/detail tabs`、`expense type`、`bill table`、`export/download` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.invoiceApply` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `a8e528d9` | `pending/applied/legacy tabs`、`business type`、`apply`、`export` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.basicInfo` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `eee7de72` | `invoice entity form`、`edit/save` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.subAccount` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `e6c26ecf` | `sub-account table`、`role`、`status`、`routing config`、`new/disable/permission` | `C4_BUSINESS_COMMIT` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.csDispatch` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `633211c7` | `groups`、`reception scope`、`participating service agents`、`switch`、`save` | `C4_BUSINESS_COMMIT` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.securityCenter` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `73d617cb` | `violation table`、`penalty status`、`appeal status`、`detail/appeal` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.adHome` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `1d79bee5` | `date`、`promotion metrics`、`plan entry`、`carousel controls` | 无 | `S7_CONFIRM_DIALOG`、`S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.notificationCenter` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `365e6b20` | `notification list`、`unread status`、`detail entry`、`mark read/clear unread` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.notificationApi` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `decd9659` | `internal API/interface module` | `C4_BUSINESS_COMMIT` | 无 | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |
| `seller.im` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `a9645de9` | `session list`、`search`、`input area`、`toolbar`、`quick replies`、`file`、`transfer` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.imItem` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `cd482fd7` | `item-linked message parameter` | `C3_FILE_EXTERNAL` | `S7_CONFIRM_DIALOG`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `seller.imDesktop` | `DIRECT_LIVE_READ_ONLY` | `S2_REDACTED_MONITOR` | `46d78a33` | `download/open client prompt` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.download` | `LIVE_ENTRY_BOUNDARY_READ` | `S4_BOUNDARY_ONLY` | `569d8b38` | `download button`、`client type` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.selectSite` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `689be932` | `site/identity list`、`selection button` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.accountCheck` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `000f7dd7` | `account check`、`continue`、`re-login`、`switch` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.accountCheckUser` | `USER_CONTEXT_REQUIRED` | `S3_CONTEXT_GATED` | `af58c9cd` | `account-check parameter` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>missing-user-context:stop |
| `seller.login` | `SHELL_BOUNDARY_ONLY` | `S4_BOUNDARY_ONLY` | `69a63af8` | `login`、`scan`、`verification entry` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>shell-target-change:stop |
| `seller.noPermission` | `DIRECT_LIVE_READ_ONLY` | `S3_HIGH_RISK_READ_ONLY` | `54b4dfcc` | `no-permission message`、`return/jump controls` | `C4_BUSINESS_COMMIT` | `S4_LOGIN_EXPIRED`、`S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop |
| `seller.iframe` | `SHELL_BOUNDARY_ONLY` | `S4_BOUNDARY_ONLY` | `f81440c6` | `iframe source`、`loading/failure state` | `C3_FILE_EXTERNAL` | `S5_PERMISSION_OR_IDENTITY_GATE`、`S6_QR_OR_APP_BRIDGE`、`S9_FILE_OR_EXPORT` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>shell-target-change:stop |
| `seller.playground` | `STATIC_EVIDENCE_ONLY` | `S4_STATIC_OR_MODULE` | `fa3e818d` | `test entry` | `C4_BUSINESS_COMMIT` | `S10_HIGH_RISK_BUSINESS_STATE` | route-family-mismatch:review<br>new-private-parameter:stop<br>anchor-loss:review<br>state-escalation:stop<br>control-escalation:stop<br>output-blacklist-hit:stop<br>static-live-probe-attempt:stop |

## 更新和收口规则

- 文案、顺序、卡片数量、空态和加载态变化，先按结构漂移记录。
- 新增订单、用户、会话、地址、发票、支付、外部跳转参数时，只记录参数名和风险，停止进入详情。
- 新增上传、下载、导出、保存、发布、发送、支付、退款、发货、权限、认证、投放、投诉处理控件时，只记录控件类别，停止操作。
- Static、Internal、Module 页面不能为了覆盖率改成 Live 探测。
- Shell、iframe、登录、下载、App 承接页面只识别边界，嵌入目标另行审查。
- 未知路由先走 `goofish-unknown-page-triage.md`，不能直接套已知页面规则。

## 最小变更记录格式

```text
pageId: <known id or UNKNOWN_PAGE>
baselineSignature: <known signature if matched>
changeType: anchor-drift / parameter-risk / state-escalation / control-escalation / unknown-route / shell-target-change
oldCategory: <structural category only>
newCategory: <structural category only>
decision: accept-structural-update / review-before-update / stop-before-action / require-user-context
privacy: no concrete parameter values, no private row/card/chat/order/account values
```

结论：这份哨兵让“页面变了”也能按同一套规则处理。小的结构漂移可更新，参数、控件、状态、外壳和未知路由风险升级必须停下。
