# 闲鱼跨 Profile 覆盖对比手册

日期：2026-06-22  
用途：当使用多个登录账号或浏览器 Profile 继续熟悉闲鱼页面时，用同一套占位台账记录页面结构覆盖和权限差异。  
边界：只使用 `accountSlot`、`browserProfileAlias` 和 `profileTypeCategory`；不保存真实账号、店铺名、手机号、邮箱、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、cookie、token、localStorage 或 sessionStorage。

## 使用方式

1. 每个账号使用独立浏览器 Profile。
2. 每个 Profile 只给占位名，例如 `account-01`、`profile-alias-only`。
3. 用户本人完成登录、扫码、验证码或账号切换。
4. 每个 Profile 先跑 B0，再按 B1-B7 批次记录页面状态类别。
5. 只比较结构类别，不比较真实内容。
6. 任何 `privacyCheckPassed=false` 的结果都不能保存。

## Profile 槽位字段

| 字段 | 说明 |
| --- | --- |
| `accountSlot` | account-01 |
| `browserProfileAlias` | profile-alias-only |
| `profileTypeCategory` | `buyer-only`、`seller-enabled`、`seller-no-permission`、`login-gated`、`unknown` |
| `runDate` | runtime-date |
| `loginHandledByUser` | true |
| `allowedIdentityFields` | `accountSlot`、`browserProfileAlias`、`profileTypeCategory` |
| `forbiddenIdentityFields` | `real account name`、`real store name`、`phone`、`email`、`member id`、`cookie`、`token`、`localStorage`、`sessionStorage`、`QR content` |

## 允许比较的差异

| 差异类别 | 含义 |
| --- | --- |
| `same-structure` | 多个 Profile 看到同样的页面结构。 |
| `login-state-diff` | 某个 Profile 登录态失效或需要重新登录。 |
| `permission-diff` | 某个 Profile 无权限或被账号检查拦截。 |
| `empty-vs-content` | 一个 Profile 是空态，另一个 Profile 有结构内容；只记录类别。 |
| `menu-availability-diff` | 菜单、tab 或入口可见性不同。 |
| `seller-site-diff` | 卖家站点、身份或经营权限导致可见页面不同。 |
| `grey-route-diff` | 某个 Profile 出现灰度路由或实验入口。 |
| `state-modal-diff` | 弹窗、门禁、二维码、确认框等状态不同。 |
| `stop-reason-diff` | 停止原因不同，例如权限、下载、导出、提交边界。 |
| `unknown-page-diff` | 某个 Profile 出现未登记页面，需要走未知页分类器。 |

## 批次覆盖

| 批次 | 页面数 | 跨 Profile 用法 |
| --- | ---: | --- |
| `B0_SESSION_PREFLIGHT` | 0 | Run once per profile before all page batches. |
| `B1_LOW_RISK_LIVE_STRUCTURE` | 8 | Run for each profile when allowed by login and permission state. |
| `B2_FORM_AND_SHELL_LIVE_PASS` | 14 | Run for each profile when allowed by login and permission state. |
| `B3_HIGH_RISK_LIVE_REDACTED_PASS` | 18 | Run for each profile when allowed by login and permission state. |
| `B4_USER_CONTEXT_REQUIRED_PASS` | 8 | Run for each profile when allowed by login and permission state. |
| `B5_STATIC_EVIDENCE_PASS` | 16 | Run for each profile when allowed by login and permission state. |
| `B6_SHELL_BOUNDARY_PASS` | 2 | Run for each profile when allowed by login and permission state. |
| `B7_UNKNOWN_PAGE_TRIAGE` | 0 | Use when a profile exposes a route not present in the known 66-page manifest. |

## 页面台账摘要

| 页面 | 批次 | 运行方式 | 基线覆盖 | 默认门禁 | 脱敏 |
| --- | --- | --- | --- | --- | --- |
| `www.home` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G0` | 否 |
| `www.search` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G0` | 否 |
| `www.machFeeds` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G0` | 否 |
| `www.item` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G1` | 是 |
| `www.personalOther` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G1` | 是 |
| `www.personalSelf` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `www.collection` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `www.bought` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `www.orderDetail` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G1` | 是 |
| `www.createOrder` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G1` | 是 |
| `www.paySuccess` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G1` | 是 |
| `www.publish` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `www.publishScene` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G2` | 是 |
| `www.publishEdit` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G2` | 是 |
| `www.im` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `www.imItem` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G2` | 是 |
| `www.account` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G4` | 是 |
| `www.accountApi` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.feedback` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `www.changelog` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G0` | 否 |
| `www.login` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G4` | 是 |
| `www.loginRedirect` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.findAccount` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.selectAccount` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.loginValidation` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.commonVideo` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G0` | 否 |
| `www.commonVideoLayout` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.upgradeBrowser` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G0` | 否 |
| `www.playground` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `www.yhbCreateOrder` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G1` | 是 |
| `www.yhbOrderDetail` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G1` | 是 |
| `seller.dataOverview` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.commodityData` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.fanData` | `B1_LOW_RISK_LIVE_STRUCTURE` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.customerServiceData` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.itemPublish` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `seller.goodsManage` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `seller.postTemplate` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `seller.postTemplateCreate` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `seller.orderManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.orderDetail` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G1` | 是 |
| `seller.refundManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.evaluationManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.complaintManage` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.refundAddress` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.incomeBill` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.expenseBill` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.invoiceApply` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.basicInfo` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.subAccount` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.csDispatch` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.securityCenter` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.adHome` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.notificationCenter` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.notificationApi` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |
| `seller.im` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G2` | 是 |
| `seller.imItem` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G2` | 是 |
| `seller.imDesktop` | `B3_HIGH_RISK_LIVE_REDACTED_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.download` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G1` | 是 |
| `seller.selectSite` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G4` | 是 |
| `seller.accountCheck` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G4` | 是 |
| `seller.accountCheckUser` | `B4_USER_CONTEXT_REQUIRED_PASS` | `WAIT_FOR_USER_CONTEXT` | `requires-user-context` | `G4` | 是 |
| `seller.login` | `B6_SHELL_BOUNDARY_PASS` | `SHELL_BOUNDARY_ONLY` | `shell-boundary` | `G4` | 是 |
| `seller.noPermission` | `B2_FORM_AND_SHELL_LIVE_PASS` | `LIVE_READ_ONLY` | `observed-live` | `G4` | 是 |
| `seller.iframe` | `B6_SHELL_BOUNDARY_PASS` | `SHELL_BOUNDARY_ONLY` | `shell-boundary` | `G1` | 是 |
| `seller.playground` | `B5_STATIC_EVIDENCE_PASS` | `STATIC_EVIDENCE_ONLY` | `static-only` | `G4` | 是 |

## 单页对比格式

```text
pageId: <known page id or UNKNOWN_PAGE>
accountSlot: account-01
browserProfileAlias: profile-alias-only
profileTypeCategory: buyer-only / seller-enabled / seller-no-permission / login-gated / unknown
status: passed / stopped / skipped / needs-user-context / static-described / shell-described / blocked-by-login / blocked-by-permission / unknown-page
observedStateCategory: S0-S10 only
coverageDeltaCategory: same-as-baseline / newly-visible / newly-hidden / permission-gated / login-gated / empty-state / grey-route / unknown-structure / static-only / shell-boundary
diffCategory: same-structure / login-state-diff / permission-diff / empty-vs-content / menu-availability-diff / seller-site-diff / grey-route-diff / state-modal-diff / stop-reason-diff / unknown-page-diff
stopReasonCategory: category only, no private values
privacyCheckPassed: true / false
```

## 对比规则

- Compare only categories, never private values.
- A profile can prove a page is structurally visible, gated, empty, static, or shell-boundary; it cannot prove hidden pages do not exist globally.
- Permission differences must be recorded as categories such as permission-gated or seller-site-diff.
- Empty states are valid observations and must not be filled by creating data.
- Unknown pages go through the classifier and are recorded as gaps, not as known safe pages.
- Any result with privacyCheckPassed false must be discarded before saving.

## 典型结论写法

- `account-01` 和 `account-02` 在 `seller.orderManage` 都只能脱敏只读，结构一致。
- `account-01` 在 `seller.subAccount` 是 `permission-gated`，`account-02` 是 `same-as-baseline`，属于 `permission-diff`。
- `account-03` 出现新 hash，按 `unknown-page-diff` 记录，并进入 `B7_UNKNOWN_PAGE_TRIAGE`。
- 某页面为空态只能写 `empty-state`，不能为了验证创建订单、商品、退款或聊天。

结论：跨 Profile 对比的价值在于找出页面结构、权限和灰度差异，而不是收集账号内容。台账只保存类别，这样可以逐步熟悉更多页面状态，同时保护账号和交易数据。
