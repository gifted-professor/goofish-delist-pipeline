# 闲鱼路由索引

日期：2026-06-22  
来源：`goofish-page-map.md`、`goofish-route-risk-cheatsheet.md`、`goofish-static-api-audit.md`，以及当前工作区 31 个前端 JS 文件的静态字符串抽取。  
用途：看到一个闲鱼 URL/hash 时，快速判断它属于哪个页面、证据层级、默认能做什么、哪里必须停下确认。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于把本路由索引转换成可校验的页面条目。

配套路由参数与上下文目录：`goofish-route-context-catalog.json` / `goofish-route-context-catalog.md`，用于判断 URL/hash 里的参数名、参数风险、上下文要求和缺上下文时的处理方式。

配套主站操作图谱：`goofish-www-operational-map.md`，用于把主站 path 放回入口、页面族和停止点。

配套卖家工作台操作图谱：`goofish-seller-workbench-operational-map.md`，用于把工作台 hash 放回菜单、权限和停止点。

配套动作门禁：`goofish-action-gate-matrix.md`，用于在定位页面后继续判断按钮、接口动作词和执行准入等级。

配套站点层级：`goofish-site-taxonomy.md`，用于把 URL/hash 放回主站、卖家工作台、页面家族和父子关系中。

配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`，用于在定位 URL/hash 后快速查看该页面当前可读、可辅助、需确认和不可触发的程度。

配套任务流手册：`goofish-task-workflow-runbook.md`，用于把已定位的页面放回搜索、下单、发布、售后、财务、权限等任务路径。

配套控件清单：`goofish-ui-control-inventory.md`，用于在定位页面后判断 tab、筛选、表格、输入、上传、下载、弹窗等控件。

配套页面接口对照：`goofish-page-api-crosswalk.md`，用于在定位页面后判断背后接口家族、读取能力和写入/高风险能力。

配套字段清单：`goofish-page-field-inventory.md`，用于在定位页面后继续判断字段敏感等级和日志记录规则。

配套证据覆盖：`goofish-evidence-coverage.md`，用于确认该路由属于实测、静态确认、容器、深层参数页还是边界能力。

配套导航定位：`goofish-navigation-selector-guide.md`，用于在确认路由后判断页面流转、加载完成信号和稳定锚点。

配套状态清单：`goofish-page-state-modal-inventory.md`，用于在确认路由后判断页面加载、空态、错误、登录、权限、二维码、确认弹窗和高风险业务状态。

## 分层规则

| 层级 | 含义 | 默认处理 |
| --- | --- | --- |
| Live + Static | 浏览器看过页面骨架，且静态包/API 能对上 | 可以只读、搜索、筛选、截图和做脱敏摘要 |
| Static Only | 只从静态包确认，或不适合触发真实流程 | 只记录结构和风险，不主动触发 |
| Shell/Container | 工作台外壳、iframe、登录/权限/站点选择容器 | 只用于导航判断，不做业务动作 |
| Deep/Param | 带订单、商品、用户、账号参数的深层路由 | 不拼真实参数；必须由用户给上下文并确认 |
| Internal/Module | API 模块、微前端资源、埋点或测试路由 | 不当作可访问业务页面 |

## 主站页面索引

基础域名：`https://www.goofish.com`

| 路由形态 | 页面/能力 | 证据 | 来源包/线索 | 默认处理 |
| --- | --- | --- | --- | --- |
| `/` | 首页、搜索入口、频道入口、推荐流 | Live + Static | `p_index.js`、`main.js` | 可搜索、看推荐、进频道 |
| `/search?q=...` | 搜索结果 | Live + Static | `p_search-index.js`、`p_layout.js` | 可改关键词、排序、价格、标签筛选 |
| `/mach-feeds?machId=...&publishTimes=...` | 首页频道/活动商品流 | Live + Static | `p_mach-feeds-index.js` | 只读频道商品卡 |
| `/item?id=...&categoryId=...` | 商品详情 | Live + Static | `p_item-index.js` | 读商品、卖家、保障、推荐 |
| `/personal` | 当前账号主页/我的闲鱼 | Live + Static | `p_personal-index.js` | 只读主页、宝贝、信用和管理入口 |
| `/personal?userId=...` | 他人闲鱼号/卖家主页 | Live + Static | `p_item-index.js`、`p_im-index.js` 线索 | 只读公开主页，不关注/联系 |
| `/collection` | 我的收藏 | Live + Static | `p_collection-index.js` | 只读收藏 tab 和商品卡 |
| `/bought` | 我买到的 | Live + Static | `p_bought-index.js` | 只读订单 tab 和订单卡结构 |
| `/order-detail?orderId=...` | 买家订单详情 | Live + Static | `p_order-detail-index.js` | 只读字段名，订单/地址/物流脱敏 |
| `/create-order?itemId=...` | 确认订单 | Live + Static | `p_create-order-index.js` | 只读确认页，不提交订单 |
| `/pay-success?orderId=...&itemId=...` | 支付成功结果页 | Static Only | `p_pay-success-index.js` | 只作为支付后结果页记录 |
| `/publish` | 发闲置 | Live + Static | `p_publish-index.js` | 可写草稿，上传/发布前确认 |
| `/publish?scene=xyPcMainPublish` | 发布入口场景参数 | Static Only | `p_publish-index.js` | 视作发布页入口，不自动发布 |
| `/publish?scene=xyPcMainPublish&itemId=...` | 编辑/带商品上下文发布 | Static Only | `p_publish-index.js` | 可能编辑商品，必须确认 |
| `/im` | 消息页 | Live + Static | `p_im-index.js`、`p_layout.js` | 可看空态/框架，可拟草稿 |
| `/im?itemId=...&peerUserId=...` | 商品关联会话 | Deep/Param | `p_im-index.js`、详情页按钮 | 不读具体私聊，不发送 |
| `/account` | 账号与安全 | Live + Static | `p_account-index.js` | 只读模块状态 |
| `/account/api` | 账号通知 API 模块路径 | Internal/Module | `main.js` | 不是页面，不主动访问 |
| `/feedback?from=...` | 用户反馈 | Live + Static | `p_feedback-index.js` | 可拟反馈，上传/提交前确认 |
| `/changelog` | 更新日志 | Live Only | `main.js` 路由线索，无独立页面包 | 公共只读 |
| `/login` | 登录 | Live + Static | `p_login-index.js` | 只辅助打开，扫码/验证码由用户本人完成 |
| `/login?spm=...&redirectURL=...` | 登录后回跳 | Static Only | `p_layout.js` 等公共逻辑 | 不改登录参数，不代过风控 |
| `/find-account` | 找回账号占位 | Static Only | `p_find-account-index.js` | PC 包会回首页，不主动找回 |
| `/select-account` | 选择账号占位 | Static Only | `p_select-account-index.js` | PC 包会回首页，多账号走 Profile |
| `/common-video` | 公共视频落地页 | Static Only | `p_common-video-index.js` | 只读活动内容，不下载/上传/主动播放 |
| `/common-video/layout` | 公共视频布局包路径 | Internal/Module | `main.js`、`p_common-video-layout.js` | 不是常规业务入口 |
| `/upgrade-browser` | 浏览器升级提示 | Static Only | `p_upgrade-browser-index.js` | 只读，不打开下载链接 |
| `/playground` | 主站内部实验页 | Static Only | `p_playground-index.js` | 禁止主动访问和支付测试 |

## 主站包到页面

| 包名 | 对应页面/能力 |
| --- | --- |
| `main.js` | 路由注册、主入口、公共页面索引 |
| `p_layout.js` | 顶部搜索、登录跳转、用户导航、IM 红点、公共布局 |
| `p_search-index.js` | 搜索页、搜索建议、筛选 |
| `p_index.js` | 首页 |
| `p_mach-feeds-index.js` | 频道/活动商品流 |
| `p_item-index.js` | 商品详情 |
| `p_personal-index.js` | 个人主页 |
| `p_collection-index.js` | 收藏 |
| `p_bought-index.js` | 买到的订单 |
| `p_order-detail-index.js` | 普通订单详情 |
| `p_create-order-index.js` | 普通确认订单 |
| `p_pay-success-index.js` | 支付成功页 |
| `p_publish-index.js` | 主站发闲置/编辑发布 |
| `p_im-index.js` | 主站消息 |
| `p_account-index.js` / `p_account-api.js` | 账号与安全、通知开关 API |
| `p_feedback-index.js` | 用户反馈 |
| `p_login-index.js` / `p_login-validation-index.js` | 登录页/登录校验占位 |
| `p_find-account-index.js` / `p_select-account-index.js` | 找回账号/选择账号占位 |
| `p_common-video-index.js` / `p_common-video-layout.js` | 公共视频活动页 |
| `p_upgrade-browser-index.js` | 浏览器升级提示 |
| `p_create-order-yhb-index.js` | 验货宝确认订单 |
| `p_order-detail-yhb-index.js` | 验货宝订单详情 |
| `p_playground-index.js` | 内部实验/支付测试页 |
| `p_$.js` | 极小运行占位包 |

## 卖家工作台页面索引

基础域名：`https://seller.goofish.com/?site=COMMONPRO#...`

| Hash 路由 | 页面/能力 | 证据 | 默认处理 |
| --- | --- | --- | --- |
| `#/seller-data/data` | 数据总览 | Live + Static | 只读指标结构，不记录真实数字 |
| `#/seller-data/commodity` | 商品数据 | Live + Static | 搜索/筛选/读表头，下载前确认 |
| `#/seller-data/fanData` | 粉丝数据 | Live + Static | 只读日期和分布模块 |
| `#/seller-data/customerService` | 客服数据 | Live + Static | 只读表头，导出前确认 |
| `#/seller-item/publish` | 商品发布 | Live + Static | 可填草稿，上传/发布前确认 |
| `#/seller-item/goods-manage` | 商品管理 | Live + Static | 只读筛选和列表结构 |
| `#/seller-item/post-temple` | 运费模版 | Live + Static | 只读或准备草稿 |
| `#/seller-item/post-temple/create` | 创建运费模版 | Live + Static | 可看字段，创建前确认 |
| `#/seller-trade/order-manage` | 订单管理 | Live + Static | 只读状态和筛选 |
| `#/seller-trade/order-manage/order-detail?orderId=...` | 卖家订单详情深层页 | Deep/Param | 不拼真实订单号；只在用户确认后打开 |
| `#/seller-trade/refund-manage` | 退款管理 | Live + Static | 只读退款字段 |
| `#/seller-trade/evaluation-manage` | 评价管理 | Live + Static | 只读评价字段 |
| `#/seller-trade/complaint-manage` | 投诉管理 | Live + Static | 只读投诉字段 |
| `#/seller-trade/refund-address` | 退货地址 | Live + Static | 只读表头，地址脱敏 |
| `#/seller-finance/income-bill` | 收入账单 | Live + Static | 只读 tab/表头，导出前确认 |
| `#/seller-finance/expense-bill` | 支出账单 | Live + Static | 只读 tab/表头，导出前确认 |
| `#/seller-finance/invoice-apply` | 申请发票 | Live + Static | 只读 tab/表头，申请前确认 |
| `#/seller-finance/basic-info` | 基本/开票信息 | Live + Static | 只读字段名，不记录主体资料 |
| `#/seller-account/sub-account` | 子账号管理 | Live + Static | 只读表头，权限变更前确认 |
| `#/im-cs-dispatch/customer-routing-service` | 客服分流 | Live + Static | 只读规则表，保存/启停前确认 |
| `#/seller-sc/home` | 安全中心 | Live + Static | 只读违规字段，申诉/处理前确认 |
| `#/seller-ad/home` | 超级擦亮 | Live + Static | 只读字段，新建投放前确认 |

## 卖家工作台外壳和容器

| Hash 路由 | 类型 | 处理 |
| --- | --- | --- |
| `#/notification-center` | 通知中心页面 | 只读通知结构，标已读/清未读前确认 |
| `#/notification-center/api` | 内部 API 模块 | 不当作页面 |
| `#/notification-center/api/clean_unread_notifications` | 内部 API 模块 | 不主动调用 |
| `#/notification-center/api/read_notify_status_sync` | 内部 API 模块 | 不主动调用 |
| `#/notification-center/interface` | 内部接口定义 | 不当作页面 |
| `#/im` | 工作台消息 | 可看框架，可拟草稿，发送前确认 |
| `#/im?itemId=...` | 工作台商品关联消息线索 | Deep/Param | 不拼参数，不发送 |
| `#/im-desktop` | 桌面版 IM 容器 | 只读，下载/安装/发消息前确认 |
| `#/download` | 工作台下载弹层/入口 | 下载或安装前确认 |
| `#/select-site` | 站点/身份选择 | 只读，切换站点前确认 |
| `#/account-check` | 账号检查 | 只读，登录其他账号/继续前往前确认 |
| `#/account-check?userNick=...` | 带账号名检查 | Deep/Param | 不拼真实账号名 |
| `#/login` | 工作台登录 | 扫码/验证码由用户本人完成 |
| `#/no-permission` | 无权限页 | 只作为权限失败判断 |
| `#/iframe?url=...` | 外部页面 iframe 容器 | 只在来源明确时使用 |
| `#/playground` | 工作台内部实验页 | 禁止主动访问 |

## 静态噪声和不当页面处理的线索

| 线索 | 判断 | 处理 |
| --- | --- | --- |
| `#/Integrated/index` | 静态抽到的集成/登录相关 hash，未作为业务页实测 | 不主动访问，除非后续实测确认 |
| `#/notification-center-api...` | 可能是打包后的模块名变体 | 不当作页面 |
| `#/xianyu.pc_*` | 埋点/事件名称被 hash 抽取误伤 | 忽略 |
| `seller-data/.../remoteEntry.js` | 微前端资源路径 | 不是页面 |
| `/search?...replace`、`ponyfill` 类字符串 | 第三方库或 URL 处理函数误伤 | 忽略 |
| 图片、字体、安装包、OSS 链接 | 静态资源 | 不纳入页面索引 |

## 判断顺序

1. 先看域名：`www.goofish.com` 走主站规则，`seller.goofish.com` 走工作台 hash 规则。
2. 再看是否带订单、商品、用户、账号、地址、发票、物流、支付参数。
3. 参数页默认按更高风险处理，哪怕页面本身可只读。
4. 遇到 `create`、`publish`、`pay`、`refund`、`refuse`、`agree`、`send`、`update`、`delete`、`clean`、`export`、`download`、`consign`、`blacklist`、`remark`、`proof`、`dispute` 相关动作，一律停下确认。
5. 对于账号选择、账号找回、登录校验、验证码、扫码、认证、实名、支付宝、安全中心，不做代操作。

## 当前缺口判断

- 已确认：主站常规页面、主站边缘静态包、卖家工作台左侧菜单、工作台外壳容器、接口风险层。
- 只静态确认：支付成功、验货宝下单/详情、公共视频、浏览器升级、账号找回/选择、登录校验、内部实验页。
- 不应为了补全而触发：真实支付、确认收货、退款/赔付、投诉举证、发货导入、发送消息、导出财务/数据、账号认证/切换。
- 如果后续继续加深，下一步应只做公开/只读页或用户明确给出的具体任务路径，不主动制造交易或账号安全场景。
