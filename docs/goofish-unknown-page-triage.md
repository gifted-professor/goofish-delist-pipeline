# 闲鱼未知页面分类手册

日期：2026-06-22  
用途：处理不在 66 个已知页面清单里的闲鱼 URL、hash、灰度页面、门禁页、H5/App 承接页或异常页。目标不是强行补全，而是安全地归类、记录结构和决定下一步。  
边界：只记录路由形状、页面族推断、状态类别、字段名、按钮名、结构锚点和停止原因；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

## 总原则

- 先归类，再观察，不先点击。
- 匹配不到已知页面时，风险只升不降。
- 带真实参数的页面，不猜、不拼、不展开私有值。
- 登录、权限、二维码、确认弹窗、上传下载、导出、支付、退款、发货、投放、认证，都先停。
- 未知页能记录的是“结构证据”，不是业务内容。

## 判断顺序

1. Normalize domain, path, hash, and parameter names. Do not store raw private parameter values.
2. Try exactKnownPageRules. If matched, use the matched page ontology and verification checklist.
3. If exact match fails, detect surface from domain: www, seller, h5/app bridge, or unknown external.
4. Apply parameterRiskRules before any DOM probing. Parameter risk can upgrade a public-looking page to context-required.
5. Apply routeFamilyRules by path/hash prefix to infer family and default gate.
6. Wait only for safe structural anchors. Then apply domSignalRules if route is still ambiguous.
7. Apply stateModalRules. Login, permission, QR, confirm, file/export, and high-risk business states stop the probe.
8. If no rule matches, create an UNKNOWN_PAGE observation with route shape, surface guess, visible structural labels, and stop reason only.

## 路由族规则

| 规则 | 表面 | 匹配 | 推断页面族 | 默认结果 |
| --- | --- | --- | --- | --- |
| `www-public-home` | `www` | `^https://www\.goofish\.com/?(?:[?#].*)?$` | `public-discovery` | `PUBLIC_READ_ONLY` |
| `www-search-like` | `www` | `^/search(?:$|[?#])` | `public-discovery` | `PUBLIC_READ_ONLY` |
| `www-channel-feed-like` | `www` | `^/mach-feeds(?:$|[?#])` | `public-discovery` | `PUBLIC_READ_ONLY` |
| `www-item-param-like` | `www` | `^/item(?:$|[?#])` | `item-detail` | `REQUIRES_USER_CONTEXT` |
| `www-personal-like` | `www` | `^/personal(?:$|[?#])` | `public-profile` | `READ_WITH_REDACTION` |
| `www-buyer-trade-like` | `www` | `^/(bought|order-detail|create-order|pay-success)(?:$|[?#])` | `buyer-trade` | `READ_WITH_REDACTION_OR_CONTEXT` |
| `www-publish-like` | `www` | `^/publish(?:$|[?#])` | `draft-input` | `DRAFT_ONLY` |
| `www-message-like` | `www` | `^/im(?:$|[?#])` | `message` | `MESSAGE_SHELL_ONLY` |
| `www-identity-like` | `www` | `^/(login|find-account|select-account|login-validation|account)(?:$|[?#])` | `identity` | `IDENTITY_GATE` |
| `www-static-content-like` | `www` | `^/(common-video|upgrade-browser|changelog)(?:$|[?#])` | `public-content` | `PUBLIC_OR_STATIC_READ` |
| `www-internal-like` | `www` | `^/(playground|account/api|common-video/layout)(?:$|[?#])` | `internal-module` | `STATIC_OR_INTERNAL_ONLY` |
| `seller-data-like` | `seller` | `^#/seller-data/` | `seller-data` | `SELLER_READ_WITH_REDACTION` |
| `seller-item-like` | `seller` | `^#/seller-item/` | `seller-item` | `SELLER_DRAFT_OR_ITEM_READ` |
| `seller-trade-like` | `seller` | `^#/seller-trade/` | `seller-trade` | `SELLER_TRADE_READ_WITH_REDACTION` |
| `seller-finance-like` | `seller` | `^#/seller-finance/` | `seller-finance` | `SELLER_FINANCE_READ_WITH_REDACTION` |
| `seller-account-like` | `seller` | `^#/seller-account/` | `seller-account` | `SELLER_ACCOUNT_READ_WITH_REDACTION` |
| `seller-security-like` | `seller` | `^#/seller-sc/` | `seller-security` | `SELLER_SECURITY_READ_WITH_REDACTION` |
| `seller-ad-like` | `seller` | `^#/seller-ad/` | `seller-ad` | `SELLER_AD_READ_WITH_REDACTION` |
| `seller-message-like` | `seller` | `^#/(im|im-desktop)(?:$|[?#/])` | `seller-message` | `SELLER_MESSAGE_SHELL_ONLY` |
| `seller-gate-like` | `seller` | `^#/(select-site|account-check|login|no-permission)(?:$|[?#/])` | `seller-gate` | `SELLER_GATE_STOP` |
| `seller-shell-like` | `seller` | `^#/(iframe|download|notification-center)(?:$|[?#/])` | `seller-shell` | `SHELL_OR_CONTAINER_ONLY` |
| `seller-internal-like` | `seller` | `^#/(playground|notification-center/api|notification-center/interface)` | `internal-module` | `STATIC_OR_INTERNAL_ONLY` |

## 参数风险

| 规则 | 参数名形态 | 风险 | 处理 |
| --- | --- | --- | --- |
| `order-id-param` | `orderId`、`bizOrderId`、`tradeId` | `trade-private` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `item-id-param` | `itemId`、`item_id`、`auctionId` | `item-context` | `REQUIRES_USER_CONTEXT_IF_NOT_PUBLIC_DETAIL` |
| `user-param` | `userId`、`peerUserId`、`userNick`、`nick`、`sellerId`、`buyerId` | `account-identity` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `chat-param` | `conversationId`、`chatId`、`peerId`、`messageId` | `private-message` | `MESSAGE_SHELL_ONLY` |
| `address-logistics-param` | `addressId`、`logisticsId`、`trackingNo`、`mailNo` | `address-logistics` | `REQUIRES_USER_CONTEXT_AND_REDACTION` |
| `invoice-finance-param` | `invoiceId`、`billId`、`fundId`、`payId`、`alipay` | `finance-payment` | `STOP_BEFORE_ACTION` |
| `redirect-param` | `redirectURL`、`redirectUrl`、`returnUrl`、`targetUrl`、`url` | `external-or-embedded-target` | `SHELL_BOUNDARY_ONLY` |
| `scene-source-param` | `scene`、`spm`、`from`、`source` | `tracking-or-entry-context` | `READ_ROUTE_SHAPE_ONLY` |

## DOM/页面锚点规则

| 规则 | 可见结构信号 | 推断页面族 | 默认动作 |
| --- | --- | --- | --- |
| `search-or-feed-dom` | `search box`、`sort controls`、`filter tags`、`item cards`、`waterfall feed` | `public-discovery` | `PUBLIC_READ_ONLY` |
| `item-detail-dom` | `image area`、`price area`、`assurance labels`、`seller card`、`buy now` | `item-detail` | `READ_WITH_TRADE_BOUNDARY` |
| `buyer-order-dom` | `order tabs`、`order cards`、`status nodes`、`address fields`、`payment area` | `buyer-trade` | `READ_WITH_REDACTION` |
| `draft-form-dom` | `form fields`、`text area`、`validation hint`、`upload area`、`submit button` | `draft-input` | `DRAFT_ONLY` |
| `message-shell-dom` | `conversation shell`、`input area`、`toolbar`、`send` | `message` | `MESSAGE_SHELL_ONLY` |
| `seller-table-dom` | `left menu`、`status tabs`、`search conditions`、`table headers`、`operation column` | `seller-trade` | `SELLER_TABLE_READ_WITH_REDACTION` |
| `finance-dom` | `bill tabs`、`date range`、`export button`、`invoice apply` | `seller-finance` | `FINANCE_READ_WITH_EXPORT_BOUNDARY` |
| `identity-gate-dom` | `login methods`、`scan prompt`、`verification entry`、`account check`、`no permission` | `identity` | `STOP_FOR_USER` |
| `shell-container-dom` | `iframe`、`download entry`、`desktop client`、`open app`、`install` | `seller-shell` | `SHELL_BOUNDARY_ONLY` |

## 未知页最小记录格式

```text
页面：UNKNOWN_PAGE
表面：www / seller / h5-app-bridge / external / unknown
路由形状：<去掉真实参数值后的 path/hash>
命中规则：<route/parameter/dom/state 规则 id>
推断页面族：<family 或 unknown>
动作门禁：G0-G4，不能确定时 G4
状态类别：S0-S10
可读：结构锚点、字段名、按钮名、tab、表头、状态类别、停止原因
停止原因：<命中的高风险参数、状态、按钮或边界>
下一步：safe-read / read-with-redaction / needs-user-context / static-only / shell-boundary / stop
隐私：未记录真实账号、订单、地址、聊天、商品标题、金额、图片链接或登录材料
```

## 常见陌生页处置

| 情况 | 处置 |
| --- | --- |
| 新的主站搜索/频道页 | 按 `public-discovery`，只读搜索框、筛选、卡片结构和分页。 |
| 新的商品详情参数页 | 按 `item-detail`，需要用户上下文，只读字段名和按钮名。 |
| 新的订单/支付/售后参数页 | 按交易高风险页，脱敏读取或停止，不猜参数。 |
| 新的发布/编辑/表单页 | 按 `draft-input`，可辅助草稿，上传/保存/提交/发布前停。 |
| 新的消息页 | 按消息外壳，只读输入区和工具栏，不读具体私聊，不发送。 |
| 新的卖家 hash | 先看 `seller-data`、`seller-item`、`seller-trade`、`seller-finance` 等前缀，再按对应页面族只读。 |
| 新的账号/权限/站点页 | 按门禁页，记录门禁类型，扫码、验证码、切号、继续前往都停。 |
| iframe、download、desktop、open app | 按 shell/container，记录容器类型，下载、安装、外部打开前停。 |
| 内部 API、remoteEntry、playground | 按 static/internal，只做静态解释，不主动访问。 |

## 和已知页面的关系

- 精确命中 66 个页面时，优先读 `goofish-page-dossiers.md` 和 `goofish-page-verification-checklist.json`。
- 只命中页面族时，使用 `goofish-page-classifier-rules.json` 的 `familyDefaults`。
- 只命中参数风险时，先按风险处理，再等待用户上下文或停止。
- 路由、参数、DOM 都不命中时，按 UNKNOWN_PAGE 记录缺口，不继续探索私有流程。

结论：未知页面不是空白地带。按本手册先分类、再只读、再收口，就能继续熟悉灰度页和隐藏页，同时不越过交易、消息、财务、权限和登录边界。
