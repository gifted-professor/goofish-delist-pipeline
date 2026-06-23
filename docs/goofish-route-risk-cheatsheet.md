# 闲鱼页面/动作速查表

日期：2026-06-22  
用途：从完整页面地图中抽取执行前最常用的路由、证据等级和风险准入规则。仅记录结构，不含账号、订单、地址、聊天、经营数据。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于按页面条目读取速查表背后的路由、锚点和停止点。

配套详表：`goofish-page-map.md` 是完整页面地图；`goofish-page-readiness-matrix.md` 是逐页就绪矩阵；`goofish-site-taxonomy.md` 是站点层级与页面家族；`goofish-task-workflow-runbook.md` 是任务流与停止点手册；`goofish-ui-control-inventory.md` 是页面控件清单；`goofish-evidence-coverage.md` 是证据覆盖清单；`goofish-route-inventory.md` 是 URL/hash 路由索引；`goofish-navigation-selector-guide.md` 是导航定位指南；`goofish-page-state-modal-inventory.md` 是页面状态与弹窗清单；`goofish-page-api-crosswalk.md` 是页面接口能力对照；`goofish-action-gate-matrix.md` 是动作门禁矩阵；`goofish-page-field-inventory.md` 是页面字段清单；`goofish-static-api-audit.md` 是静态接口审计。

## 速用原则

1. 公开浏览页可以直接打开、搜索、读取和截图。
2. 登录后列表页默认只读，摘要必须脱敏。
3. 发布、反馈、IM、售后文本可以帮写草稿，但不提交。
4. 交易、支付、确认收货、退款、赔付、发货、投诉、账号认证、导出、上传、发消息都必须停下确认。
5. `Static Only` 和 `Boundary Only` 页面不做真实触发，只说明结构和风险。

## 主站路由速查

| 路由 | 页面 | 证据 | 默认动作 | 风险边界 |
| --- | --- | --- | --- | --- |
| `/` | 首页 | Live + Static | 搜索、看推荐、进频道 | 不自动点交易/消息入口 |
| `/search?q=...` | 搜索结果 | Live + Static | 改关键词、价格、排序、标签筛选、读商品卡 | 地区筛选先确认弹层，避免误点分页 |
| `/mach-feeds?machId=...&publishTimes=...` | 频道/活动流 | Live + Static | 读频道商品卡 | 不把频道当独立业务页 |
| `/item?id=...&categoryId=...` | 商品详情 | Live + Static | 读商品、卖家、保障、推荐 | 聊一聊、收藏、立即购买前确认 |
| `/personal` | 个人主页/闲鱼号 | Live + Static | 只读主页、宝贝、信用、管理入口 | 编辑资料、上下架、删除前确认 |
| `/collection` | 我的收藏 | Live + Static | 只读收藏 tab 和卡片 | 取消收藏、我想要前确认 |
| `/bought` | 我买到的 | Live + Static | 只读订单 tab 和订单卡结构 | 确认收货、退款、评价、删除、投诉前确认 |
| `/order-detail?orderId=...` | 订单详情 | Live + Static | 只读订单、物流、状态字段 | 不记录订单号、地址、物流轨迹；售后/收货前确认 |
| `/create-order?itemId=...` | 确认订单 | Live + Static | 只读收货地址/运费/支付方式字段 | 不提交订单、不支付、不改地址 |
| `/publish` | 发闲置 | Live + Static | 可帮写描述/价格/规格/运费草稿 | 上传图片和发布前确认 |
| `/im` | 消息 | Live + Static | 可看空态/框架，可拟草稿 | 不读具体会话，不发送消息 |
| `/account` | 账号与安全 | Live + Static | 只读模块状态 | 通知开关、认证、实名、支付宝、安全设置前确认 |
| `/feedback?from=...` | 用户反馈 | Live + Static | 可拟反馈草稿 | 上传截图、提交前确认 |
| `/changelog` | 更新日志 | Live + Static | 只读 | 低风险 |
| `/pay-success?orderId=...&itemId=...` | 支付成功结果页 | Static Only | 只作为结果页记录 | 不为测试触发支付 |
| `/find-account` | 找回账号占位 | Static Only | 不主动访问 | PC 包会回首页；账号找回由用户本人处理 |
| `/select-account` | 选择账号占位 | Static Only | 不主动访问 | PC 包会回首页；多账号用独立 Profile |
| `/login` | 登录 | Live + Static | 可打开登录页 | 扫码、验证码、风控由用户完成 |
| `/playground` | 内部实验页 | Static Only | 不访问 | 含支付/账号测试能力，禁止触发 |
| `/common-video` | 公共视频落地页 | Static Only | 只读活动内容 | 不下载/上传/主动播放 |
| `/upgrade-browser` | 浏览器升级页 | Static Only | 只读推荐浏览器 | 不自动打开外部下载链接 |
| 验货宝确认订单 | `create-order-yhb` 包 | Static Only | 只记录字段/API | 不触发验货宝下单 |
| 验货宝订单详情 | `order-detail-yhb` 包 | Static Only | 只记录字段/API | 不触发纠纷/评价/售后 |

## 卖家工作台路由速查

基础域名：`https://seller.goofish.com/?site=COMMONPRO#...`

| Hash 路由 | 页面 | 默认动作 | 风险边界 |
| --- | --- | --- | --- |
| `#/seller-data/data` | 数据总览 | 只读指标结构 | 不导出，不记录真实数字 |
| `#/seller-data/commodity` | 商品数据 | 搜索/筛选/读表头 | 下载前确认 |
| `#/seller-data/fanData` | 粉丝数据 | 只读日期和分布模块 | 不记录真实人群/地域数字 |
| `#/seller-data/customerService` | 客服数据 | 只读表头/满意度字段 | 导出数据前确认 |
| `#/seller-item/publish` | 商品发布 | 填草稿 | 上传、发布前确认 |
| `#/seller-item/goods-manage` | 商品管理 | 只读筛选和列表结构 | 复制、编辑、改价、下架、批量下架前确认 |
| `#/seller-item/post-temple` | 运费模版 | 只读/准备模板草稿 | 创建、编辑、删除、设默认前确认 |
| `#/seller-item/post-temple/create` | 创建运费模版 | 可看字段/填草稿 | 创建前确认 |
| `#/seller-trade/order-manage` | 订单管理 | 只读状态和筛选 | 发货、改物流、备注、查看钱款、联系买家前确认 |
| `#/seller-trade/refund-manage` | 退款管理 | 只读退款字段 | 同意/拒绝退款、管理地址模板前确认 |
| `#/seller-trade/evaluation-manage` | 评价管理 | 只读评价字段 | 评价、批量评价、举报、联系前确认 |
| `#/seller-trade/complaint-manage` | 投诉管理 | 只读投诉字段 | 投诉详情处理、举证、联系前确认 |
| `#/seller-trade/refund-address` | 退货地址 | 只读表头 | 新增、编辑、删除、设默认前确认 |
| `#/seller-finance/income-bill` | 收入账单 | 只读 tab/表头 | 导出、下载明细前确认 |
| `#/seller-finance/expense-bill` | 支出账单 | 只读 tab/表头 | 导出、历史下载前确认 |
| `#/seller-finance/invoice-apply` | 申请发票 | 只读 tab/表头 | 申请发票、导出前确认 |
| `#/seller-finance/basic-info` | 基本/开票信息 | 只读字段名 | 不记录主体资料，修改前确认 |
| `#/seller-account/sub-account` | 子账号管理 | 只读表头 | 新建、停用、改权限/分流前确认 |
| `#/im-cs-dispatch/customer-routing-service` | 客服分流 | 只读规则表 | 新建/启停/保存规则前确认 |
| `#/seller-sc/home` | 安全中心 | 只读违规字段 | 申诉/处理/跳详情前确认 |
| `#/seller-ad/home` | 超级擦亮 | 只读字段 | 新建投放/推广前确认 |
| `#/notification-center` | 通知中心 | 只读通知结构 | 标已读、清未读前确认 |
| `#/im` | 工作台消息 | 可看框架/拟草稿 | 发送消息前确认 |
| `#/im-desktop` | 桌面版消息容器 | 只读 | 下载、安装、发消息前确认 |
| `#/select-site` | 站点选择 | 只读 | 切换站点前确认 |
| `#/account-check` | 账号检查 | 只读 | 登录其他账号/继续前往前确认 |
| `#/no-permission` | 无权限页 | 判断权限失败 | 无操作 |
| `#/login` | 工作台登录 | 可打开 | 扫码/验证码由用户完成 |
| `#/playground` | 内部实验页 | 不访问 | 禁止触发测试能力 |

## 动作风险速查

| 任务 | 推荐入口 | 可自动做 | 必须确认 |
| --- | --- | --- | --- |
| 搜货/比价 | `/search`、`/item` | 搜索、筛选、读公开字段 | 收藏、联系、购买 |
| 看某商品 | `/item?id=...` | 读标题、价格、保障、卖家公开信息 | 聊一聊、立即购买、收藏 |
| 看收藏 | `/collection` | 读 tab 和卡片结构 | 取消收藏、我想要 |
| 看买家订单 | `/bought`、`/order-detail` | 读状态和字段名，脱敏摘要 | 确认收货、退款、评价、投诉 |
| 发闲置 | `/publish` 或 `#/seller-item/publish` | 写描述/价格/规格/运费草稿 | 上传图片、发布 |
| 反馈问题 | `/feedback` | 写反馈草稿 | 上传截图、提交 |
| 发消息 | `/im` 或 `#/im` | 拟消息草稿 | 发送、发商品/订单卡片 |
| 卖家查订单 | `#/seller-trade/order-manage` | 只读筛选和状态 | 发货、改物流、备注、联系 |
| 卖家处理售后 | `#/seller-trade/refund-manage`、`#/seller-trade/complaint-manage` | 只读和拟草稿 | 同意/拒绝/举证/赔付 |
| 卖家看数据 | `#/seller-data/*` | 读字段和表头 | 下载/导出 |
| 财务/发票 | `#/seller-finance/*` | 读 tab 和字段名 | 导出、申请发票、改开票信息 |
| 子账号/分流 | `#/seller-account/sub-account`、`#/im-cs-dispatch/*` | 读表头/规则结构 | 新建、停用、保存规则 |
| 多账号切换 | 独立浏览器 Profile | 选择 Profile、确认登录态 | 账号找回、扫码、验证码、认证 |

## 多账号最小规则

- 一个闲鱼账号对应一个独立浏览器 Profile。
- 只保存账号别名和 Profile 路径，不保存 cookie、token、密码、验证码、二维码内容。
- 执行前先确认当前 Profile 的登录态。
- 出现扫码、验证码、认证、账号选择、账号找回时交给用户本人。
- 不通过复制 cookie 或“密钥”来切换账号。

## 日志脱敏速查

允许记录：页面路径、页面标题、字段名、按钮名、tab 名、表头名、状态类别、风险等级、是否需要确认。  
禁止记录：昵称、手机号、订单号、物流单号、商品 ID、地址、聊天内容、投诉/评价正文、金额明细、cookie、token、localStorage、sessionStorage。
