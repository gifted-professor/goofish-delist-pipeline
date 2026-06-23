# 闲鱼覆盖缺口登记

日期：2026-06-22  
用途：说明 `goofish-page-manifest.json` 的 66 个页面中，哪些已经 Live 观察，哪些不应为了补覆盖而强行打开。  
边界：本登记只写页面 id、路由形态、缺口原因和下一步；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数字、图片链接或登录材料。

总索引：`goofish-master-index.md`  
页面清单：`goofish-page-manifest.json`  
Live 矩阵：`goofish-live-coverage-matrix.md`  
机器状态：`goofish-live-coverage-status.json`

## 覆盖总账

| 分类 | 数量 | 含义 |
| --- | ---: | --- |
| 已 Live 只读观察 | 40 | 当前已登录浏览器 Profile 下打开过，只读记录页面态和控件结构 |
| 需要用户上下文 | 8 | 需要真实商品、用户、订单、会话或账号参数；不能猜参数 |
| 只能静态解释 | 16 | 来自前端包、模块、登录/实验/承接资源；不强行实测 |
| Shell/Container 边界 | 2 | 只识别容器，不进入外部或嵌入目标 |
| 未归类 | 0 | 当前 manifest 页面均已分入一种处理方式 |

## 已 Live 只读观察

这些页面可以继续做字段名、表头、tab、控件密度和状态类别分析，但不能执行写入动作。

| 范围 | 页面 id |
| --- | --- |
| 主站公开/账号/交易/草稿/消息/登录 | `www.home`, `www.search`, `www.machFeeds`, `www.personalSelf`, `www.collection`, `www.bought`, `www.publish`, `www.im`, `www.account`, `www.feedback`, `www.changelog`, `www.login` |
| 卖家数据/商品/交易/财务 | `seller.dataOverview`, `seller.commodityData`, `seller.fanData`, `seller.customerServiceData`, `seller.itemPublish`, `seller.goodsManage`, `seller.postTemplate`, `seller.postTemplateCreate`, `seller.orderManage`, `seller.refundManage`, `seller.evaluationManage`, `seller.complaintManage`, `seller.refundAddress`, `seller.incomeBill`, `seller.expenseBill`, `seller.invoiceApply`, `seller.basicInfo` |
| 卖家账号/安全/推广/消息/门禁 | `seller.subAccount`, `seller.csDispatch`, `seller.securityCenter`, `seller.adHome`, `seller.notificationCenter`, `seller.im`, `seller.imDesktop`, `seller.download`, `seller.selectSite`, `seller.accountCheck`, `seller.noPermission` |

## 需要用户上下文

这些页面不是“没搞懂”，而是需要真实上下文才有页面意义。没有用户明确提供的 URL 或业务上下文时，不拼参数、不猜订单、不造状态。

| 页面 id | 路由形态 | 为什么不能主动补覆盖 | 下一步 |
| --- | --- | --- | --- |
| `www.item` | `/item?id=...&categoryId=...` | 需要具体公开商品参数；商品页含购买/联系/收藏边界 | 只在用户给出商品 URL 时打开，并停在购买/联系前 |
| `www.personalOther` | `/personal?userId=...` | 需要具体公开用户参数；可能暴露个人主页身份 | 只在用户给出公开主页 URL 时打开，记录结构不记录身份 |
| `www.orderDetail` | `/order-detail?orderId=...` | 需要真实订单参数；交易、地址、物流、金额高敏 | 只在用户明确要求核对某单时打开，只读字段名和状态类别 |
| `www.createOrder` | `/create-order?itemId=...` | 下单确认页本身接近交易提交 | 只在用户明确要求做下单前核对时打开，停在提交/支付前 |
| `www.imItem` | `/im?itemId=...&peerUserId=...` | 需要具体会话/商品参数；私聊高敏 | 默认不打开具体会话，除非用户明确要求 |
| `seller.orderDetail` | `#/seller-trade/order-manage/order-detail?orderId=...` | 卖家订单详情含买家、地址、物流、钱款和操作 | 只在用户给定订单上下文并确认只读时打开 |
| `seller.imItem` | `#/im?itemId=...` | 卖家具体会话/商品上下文高敏 | 默认只看消息外壳，不读私聊 |
| `seller.accountCheckUser` | `#/account-check?userNick=...` | 需要具体账号身份参数 | 不主动构造；仅记录为账号检查边界 |

## 只能静态解释

这些页面来自静态前端包、模块入口、实验页、登录流程、旧版/特殊包或承接页。它们可以写规则，但不应为了“覆盖率”强行打开或触发。

| 类型 | 页面 id | 处理方式 |
| --- | --- | --- |
| 交易结果/特殊交易包 | `www.paySuccess`, `www.yhbCreateOrder`, `www.yhbOrderDetail` | 只按静态包和交易边界解释，不制造订单状态 |
| 发布变体 | `www.publishScene`, `www.publishEdit` | 只按草稿/编辑边界解释，不带真实 item 参数 |
| 登录/账号找回流程 | `www.loginRedirect`, `www.findAccount`, `www.selectAccount`, `www.loginValidation` | 只识别门禁，不走验证码、找回、切号流程 |
| 内容/兼容/实验 | `www.commonVideo`, `www.upgradeBrowser`, `www.playground`, `seller.playground` | 只记录承接/兼容/实验边界 |
| 内部模块/API | `www.accountApi`, `www.commonVideoLayout`, `seller.notificationApi` | 不是业务页面，不当作可操作页面 |

## Shell/Container 边界

| 页面 id | 路由形态 | 处理方式 |
| --- | --- | --- |
| `seller.login` | `#/login` | 只识别登录 shell；扫码、验证码、切号都停 |
| `seller.iframe` | `#/iframe?url=...` | 只识别 iframe 容器；外部或嵌入目标需要单独审查 |

## 下一步优先级

1. 优先继续深化 40 个已 Live 页面：字段名、表头、状态、按钮类别、空态和弹窗。
2. 对 8 个需要上下文的页面，只在用户给出具体 URL 或明确业务目标时做一次只读观察。
3. 对 16 个静态页面，只补规则和风险解释，不追求 live 打开。
4. 对 2 个 shell/container 页面，只记录边界，不进入外部或嵌入内容。

结论：当前没有“未归类页面”。剩余缺口都是有理由的边界：需要真实上下文、只能静态解释，或属于 shell/container。后续熟悉页面应沿着这些边界继续，而不是为了覆盖率去制造交易、会话、账号或权限状态。
