# 闲鱼逐页验证清单

日期：2026-06-22  
用途：把 66 个闲鱼页面转成可执行的验证清单。下一次打开页面、切换账号 Profile 或继续补覆盖时，按本清单判断每页要等什么、能记录什么、什么证据算通过、哪里必须停。  
边界：只记录页面结构、路由形状、页面族、状态类别、控件类别、表头、字段名、按钮名和停止点；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

## 总览

| 维度 | 数量 |
| --- | ---: |
| 页面总数 | 66 |
| 已 Live 观察 | 40 |
| 需用户上下文 | 8 |
| 静态证据页 | 16 |
| 外壳边界页 | 2 |
| 需要脱敏读取 | 60 |

## 通用通过标准

- The page is matched to a known id or explicitly registered as unknown.
- Only structural anchors, labels, categories, and stop points are recorded.
- The current state is classified into S0-S10 before interacting with controls.
- The default G0-G4 action gate is applied before any control-level decision.
- All private values and login material are excluded from output.
- Any stop state, stop point, or G3/G4 control ends the probe before action.

## 通用失败标准

- A real account, order, address, chat, item title, amount, metric, image URL, QR content, cookie, token, or browser storage value would be captured.
- The probe needs a guessed item, order, user, chat, invoice, payment, or account parameter.
- The page requires payment, shipment, refund, complaint proof, identity verification, permission change, upload, download, export, install, or send action.
- The current page is a static-only or internal module and someone tries to force-open it for coverage.

## 分组验证

### D1 高风险 Live 页

重点：只读 tab、筛选、表头、状态类别和弹窗类别；不读真实行值，不触发经营或交易动作。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.bought` | `/bought` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | confirm receipt / refund / review / delete / complaint |
| `www.account` | `/account` | `READ_WITH_REDACTION` | `G4` | route shape recognized / one or more anchors visible / expected state category assigned | toggle notice / verify identity / switch account / logout / any proactive action beyond naming the boundary |
| `seller.orderManage` | `#/seller-trade/order-manage` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | ship / change logistics / remark / contact / view funds |
| `seller.refundManage` | `#/seller-trade/refund-manage` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | agree refund / refuse refund / compensate / confirm receipt / private value logging |
| `seller.evaluationManage` | `#/seller-trade/evaluation-manage` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | review / report / contact / private value logging / edit/save/send/export/download/submit controls |
| `seller.complaintManage` | `#/seller-trade/complaint-manage` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | submit proof / revoke / refuse / submit material / private value logging |
| `seller.refundAddress` | `#/seller-trade/refund-address` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | add address / edit address / delete address / private value logging / edit/save/send/export/download/submit controls |
| `seller.incomeBill` | `#/seller-finance/income-bill` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | export / historical download / download full detail / private value logging / edit/save/send/export/download/submit controls |
| `seller.expenseBill` | `#/seller-finance/expense-bill` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | export / download / private value logging / edit/save/send/export/download/submit controls |
| `seller.invoiceApply` | `#/seller-finance/invoice-apply` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | apply invoice / export / private value logging / edit/save/send/export/download/submit controls |
| `seller.basicInfo` | `#/seller-finance/basic-info` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | modify entity data / private value logging / edit/save/send/export/download/submit controls |
| `seller.subAccount` | `#/seller-account/sub-account` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | create sub-account / disable account / change permission / private value logging / edit/save/send/export/download/submit controls |
| `seller.csDispatch` | `#/im-cs-dispatch/customer-routing-service` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | save / enable/disable / create group / private value logging / edit/save/send/export/download/submit controls |
| `seller.securityCenter` | `#/seller-sc/home` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | view sensitive detail / appeal / process / private value logging / edit/save/send/export/download/submit controls |
| `seller.adHome` | `#/seller-ad/home` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | create plan / launch paid promotion / private value logging / edit/save/send/export/download/submit controls |
| `seller.notificationCenter` | `#/notification-center` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | mark read / clear unread / private value logging / edit/save/send/export/download/submit controls |
| `seller.im` | `#/im` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | read specific conversation / send / file upload / transfer / upload |
| `seller.imDesktop` | `#/im-desktop` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | download / install / open / private value logging / edit/save/send/export/download/submit controls |

### D2 表单和外壳 Live 页

重点：只读字段名、输入类型、校验类别、上传区和空态；停在保存、上传、提交、发送、发布前。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.publish` | `/publish` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | upload / save draft / publish / edit existing item / save |
| `www.im` | `/im` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | read specific private chat / send / send card / upload file / upload |
| `www.feedback` | `/feedback?from=...` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | upload screenshot / submit / upload / save / send |
| `www.login` | `/login` | `READ_WITH_REDACTION` | `G4` | route shape recognized / one or more anchors visible / expected state category assigned | scan / enter verification code / bypass risk control / any proactive action beyond naming the boundary |
| `seller.commodityData` | `#/seller-data/commodity` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | download item detail / private value logging / edit/save/send/export/download/submit controls |
| `seller.customerServiceData` | `#/seller-data/customerService` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | export customer-service detail / private value logging / edit/save/send/export/download/submit controls |
| `seller.itemPublish` | `#/seller-item/publish` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | upload / save / publish / submit / send |
| `seller.goodsManage` | `#/seller-item/goods-manage` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | edit / copy / adjust price / shelf changes / delete |
| `seller.postTemplate` | `#/seller-item/post-temple` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | create / edit / delete / set default / upload |
| `seller.postTemplateCreate` | `#/seller-item/post-temple/create` | `READ_WITH_REDACTION` | `G2` | route shape recognized / one or more anchors visible / expected state category assigned | save real template / upload / save / submit / send |
| `seller.download` | `#/download` | `READ_WITH_REDACTION` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | download / install / private value logging / edit/save/send/export/download/submit controls |
| `seller.selectSite` | `#/select-site` | `READ_WITH_REDACTION` | `G4` | route shape recognized / one or more anchors visible / expected state category assigned | switch site / any proactive action beyond naming the boundary |
| `seller.accountCheck` | `#/account-check` | `READ_WITH_REDACTION` | `G4` | route shape recognized / one or more anchors visible / expected state category assigned | continue / re-login / switch account / any proactive action beyond naming the boundary |
| `seller.noPermission` | `#/no-permission` | `READ_WITH_REDACTION` | `G4` | route shape recognized / one or more anchors visible / expected state category assigned | any proactive action beyond naming the boundary |

### D3 低风险 Live 页

重点：只读导航、筛选、卡片结构、内容块和路由形状；不记录商品身份值。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.home` | `/` | `SAFE_READ` | `G0` | route shape recognized / one or more anchors visible / expected state category assigned | message entry / publish entry / order entry / state-changing controls / private values outside public structure |
| `www.search` | `/search?q=...` | `SAFE_READ` | `G0` | route shape recognized / one or more anchors visible / expected state category assigned | unstable location panel / collect / contact / purchase / state-changing controls |
| `www.machFeeds` | `/mach-feeds?machId=...&publishTimes=...` | `SAFE_READ` | `G0` | route shape recognized / one or more anchors visible / expected state category assigned | collect / contact / purchase / state-changing controls / private values outside public structure |
| `www.personalSelf` | `/personal` | `SAFE_READ` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | edit profile / manage item / downshelf / delete / private value logging |
| `www.collection` | `/collection` | `SAFE_READ` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | uncollect / want / contact / private value logging / edit/save/send/export/download/submit controls |
| `www.changelog` | `/changelog` | `SAFE_READ` | `G0` | route shape recognized / one or more anchors visible / expected state category assigned | state-changing controls / private values outside public structure |
| `seller.dataOverview` | `#/seller-data/data` | `SAFE_READ` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | record real numbers / export / download / private value logging / edit/save/send/export/download/submit controls |
| `seller.fanData` | `#/seller-data/fanData` | `SAFE_READ` | `G1` | route shape recognized / one or more anchors visible / expected state category assigned | record real audience numbers / export / private value logging / edit/save/send/export/download/submit controls |

### D4 需要用户上下文页

重点：只在用户给出真实 URL 或业务上下文后读结构；不猜 item/order/user/chat 参数。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.item` | `/item?id=...&categoryId=...` | `REQUIRES_USER_CONTEXT` | `G1` | required parameter type identified / user-provided context confirmed / private parameters redacted | collect / chat / buy now / downshelf / delete |
| `www.personalOther` | `/personal?userId=...` | `REQUIRES_USER_CONTEXT` | `G1` | required parameter type identified / user-provided context confirmed / private parameters redacted | follow / contact / purchase / private value logging / edit/save/send/export/download/submit controls |
| `www.orderDetail` | `/order-detail?orderId=...` | `REQUIRES_USER_CONTEXT` | `G1` | required parameter type identified / user-provided context confirmed / private parameters redacted | any order-state change / real order value logging / private value logging / edit/save/send/export/download/submit controls |
| `www.createOrder` | `/create-order?itemId=...` | `REQUIRES_USER_CONTEXT` | `G1` | required parameter type identified / user-provided context confirmed / private parameters redacted | submit order / pay / change address / bind account / verify identity |
| `www.imItem` | `/im?itemId=...&peerUserId=...` | `REQUIRES_USER_CONTEXT` | `G2` | required parameter type identified / user-provided context confirmed / private parameters redacted | read specific conversation / send / upload / save / submit |
| `seller.orderDetail` | `#/seller-trade/order-manage/order-detail?orderId=...` | `REQUIRES_USER_CONTEXT` | `G1` | required parameter type identified / user-provided context confirmed / private parameters redacted | guess order id / order action / private value logging / edit/save/send/export/download/submit controls |
| `seller.imItem` | `#/im?itemId=...` | `REQUIRES_USER_CONTEXT` | `G2` | required parameter type identified / user-provided context confirmed / private parameters redacted | guess parameter / send / upload / save / submit |
| `seller.accountCheckUser` | `#/account-check?userNick=...` | `REQUIRES_USER_CONTEXT` | `G4` | required parameter type identified / user-provided context confirmed / private parameters redacted | guess real account name / any proactive action beyond naming the boundary |

### D5 静态证据页

重点：只从静态模块、路由、Page 信号和接口族理解；不为了补覆盖强开。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.paySuccess` | `/pay-success?orderId=...&itemId=...` | `STATIC_ONLY` | `G1` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | trigger payment for testing / private value logging / edit/save/send/export/download/submit controls |
| `www.publishScene` | `/publish?scene=xyPcMainPublish` | `STATIC_ONLY` | `G2` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | save / publish / upload / submit / send |
| `www.publishEdit` | `/publish?scene=xyPcMainPublish&itemId=...` | `STATIC_ONLY` | `G2` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | overwrite existing item / save / publish / upload / submit |
| `www.accountApi` | `/account/api` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | direct call / page navigation / any proactive action beyond naming the boundary |
| `www.loginRedirect` | `/login?spm=...&redirectURL=...` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | change login parameters / bypass risk control / any proactive action beyond naming the boundary |
| `www.findAccount` | `/find-account` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | recover account / any proactive action beyond naming the boundary |
| `www.selectAccount` | `/select-account` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | switch account / any proactive action beyond naming the boundary |
| `www.loginValidation` | `/login-validation` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | enter verification code / any proactive action beyond naming the boundary |
| `www.commonVideo` | `/common-video` | `STATIC_ONLY` | `G0` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | play proactively / download / capture video / state-changing controls / private values outside public structure |
| `www.commonVideoLayout` | `/common-video/layout` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | page navigation / any proactive action beyond naming the boundary |
| `www.upgradeBrowser` | `/upgrade-browser` | `STATIC_ONLY` | `G0` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | download / install / state-changing controls / private values outside public structure |
| `www.playground` | `/playground` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | visit proactively / trigger test action / any proactive action beyond naming the boundary |
| `www.yhbCreateOrder` | `create-order-yhb package` | `STATIC_ONLY` | `G1` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | create YHB order / private value logging / edit/save/send/export/download/submit controls |
| `www.yhbOrderDetail` | `order-detail-yhb package` | `STATIC_ONLY` | `G1` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | after-sale action / review action / private value logging / edit/save/send/export/download/submit controls |
| `seller.notificationApi` | `#/notification-center/api*` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | direct call / any proactive action beyond naming the boundary |
| `seller.playground` | `#/playground` | `STATIC_ONLY` | `G4` | static module or route signal identified / API or Page signal mapped to family / risk boundary recorded | visit proactively / trigger test action / any proactive action beyond naming the boundary |

### D6 外壳边界页

重点：只识别登录、iframe、容器或下载边界；不进入嵌入页或外部动作。

| 页面 | 路由形状 | 流转 | 动作 | 验证通过证据 | 主要停止点 |
| --- | --- | --- | --- | --- | --- |
| `seller.login` | `#/login` | `SHELL_ONLY` | `G4` | container type identified / embedded target shape described / login or permission boundary recorded | scan / enter verification code / any proactive action beyond naming the boundary |
| `seller.iframe` | `#/iframe?url=...` | `SHELL_ONLY` | `G1` | container type identified / embedded target shape described / login or permission boundary recorded | operate external page without separate review / private value logging / edit/save/send/export/download/submit controls |

## 单页检查步骤

1. 用 URL/path/hash 匹配 `id` 和 `routePattern`。
2. 先看 `liveCoverage`，判断能不能打开，还是只能等用户上下文或静态解释。
3. 等 `waitFor` 里的结构锚点，不用真实业务值作为加载完成依据。
4. 记录 `recordableEvidence` 里的结构类别。
5. 用 `acceptableStates` 和 `stopStates` 判断当前页面态。
6. 命中 `pageStopPoints` 或 `gateStopPoints` 就停。
7. 只在 `passEvidence` 都能成立时，把该页面标为本轮验证通过。

## 推荐输出格式

```text
页面：<id>
路由：<routePattern>
覆盖：<liveCoverage>
流转：<transitionClass>
动作门禁：<defaultActionGate>
当前状态：<S0-S10>
通过证据：结构锚点 / 字段名 / tab / 表头 / 按钮名 / 状态类别
停止点：<命中的 stop point>
结论：通过 / 需用户上下文 / 静态解释 / 停在外壳 / 停在高风险动作前
隐私：未记录真实账号、订单、地址、聊天、商品标题、金额、图片链接或登录材料
```

结论：这份清单负责回答“下一次怎样证明这个页面已经安全看懂了”。更细的页面画像看 `goofish-page-ontology.json`，实际逐页巡检输入看 `goofish-page-verification-checklist.json`。
