# 闲鱼页面到接口能力对照表

日期：2026-06-22  
用途：把“路由/页面”和“前端包暴露的接口能力”接起来，方便判断一个页面背后可能牵到哪些读取、写入、交易、消息、财务或权限动作。  
边界：只记录接口名、接口家族、来源包和风险结论；不调用接口，不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据或图片链接。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于按页面 id 对齐路由、层级、接口风险和停止点。
配套主地图：`goofish-page-map.md`  
配套站点层级：`goofish-site-taxonomy.md`  
配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`  
配套路由索引：`goofish-route-inventory.md`  
配套任务流手册：`goofish-task-workflow-runbook.md`  
配套控件清单：`goofish-ui-control-inventory.md`  
配套接口审计：`goofish-static-api-audit.md`  
配套动作门禁：`goofish-action-gate-matrix.md`  
配套状态清单：`goofish-page-state-modal-inventory.md`

## 读法

| 标记 | 含义 | 默认处理 |
| --- | --- | --- |
| A0 | 无业务接口或仅静态内容 | 只读页面结构 |
| A1 | 公开读取接口 | 可公开只读、搜索、筛选 |
| A2 | 登录后读取接口 | 可只读，输出必须脱敏 |
| A3 | 会写入账号/商品/消息/经营状态 | 用户逐项确认后才可执行 |
| A4 | 支付、交易、售后、发货、认证、权限、内部测试 | 不主动触发；只说明结构和风险 |

判断规则：

1. 页面层和接口层风险不一致时，按更高风险处理。
2. 即使接口名看起来是 `query/list/render/detail`，只要返回订单、地址、财务、客服、粉丝、风控、聊天内容，就按登录后敏感只读处理。
3. 出现 `create`、`publish`、`pay`、`refund`、`refuse`、`agree`、`send`、`update`、`delete`、`clean`、`export`、`download`、`consign`、`blacklist`、`remark`、`proof`、`dispute`，默认进入确认或禁止主动触发层。
4. 本表只作为页面理解和自动化防线，不作为直接调用接口的依据。

## 主站公共能力

| 来源包 | 能力 | 代表接口 | 风险 |
| --- | --- | --- | --- |
| `main.js` | 主入口、路由注册、续登、公共标题 | 无稳定业务写接口 | A0/A2 |
| `p_layout.js` | 顶部搜索建议、用户导航、登录跳转、IM 红点 | `mtop.taobao.idlemtopsearch.pc.search.suggest`、`mtop.idle.web.user.page.nav`、`mtop.taobao.idlemessage.pc.redpoint.query` | A1/A2 |
| `p_layout.js` | 消息会话同步、未读清理、登录 token | `mtop.taobao.idlemessage.pc.session.sync`、`mtop.taobao.idlemessage.pc.systems.unread.clean`、`mtop.taobao.idlemessage.pc.login.token` | A3 |
| `p_account-api.js` | 账号通知设置 | `mtop.taobao.idlemessage.pc.profile.notice.query`、`mtop.taobao.idlemessage.pc.profile.notice.update` | 查询 A2，更新 A3 |

## 主站页面对照

| 页面/路由 | 来源包 | 只读接口线索 | 写入/高风险接口线索 | 结论 |
| --- | --- | --- | --- | --- |
| `/` 首页 | `p_index.js` | `mtop.taobao.idlehome.home.webpc.feed` | 无页面专属写接口 | A1，可搜索和读推荐 |
| `/search?q=...` 搜索 | `p_search-index.js`、`p_layout.js` | `mtop.taobao.idlemtopsearch.pc.search`、`search.suggest`、`search.shade`、`division.all.get`、`filter.hitnum.pc.get`、`local.poi.get` | 与发布包共享 `draft.edit`、`draft.publish`、`idleitem.publish` 等能力 | 搜索筛选 A1；发布相关入口 A3/A4 |
| `/mach-feeds?...` 频道流 | `p_mach-feeds-index.js` | `mtop.taobao.idlehome.home.webpc.feed` | 无页面专属写接口 | A1，当作主题商品流 |
| `/item?id=...` 商品详情 | `p_item-index.js` | `mtop.taobao.idle.pc.detail`、`item.web.recommend.list`、`cloud.video.query`、`cat.configs` | `mtop.taobao.idle.collect.item`、`item.downshelf`、`trade.common.sku.selector` | 读详情 A1/A2；收藏、购买、下架 A3/A4 |
| `/personal` 当前主页 | `p_personal-index.js` | `user.page.head`、`user.page.account`、`xyh.item.list`、`favor.item.list` | `trade.rate.list`、`attention.relation` | 只读主页 A2；关注/关系变更 A3 |
| `/personal?userId=...` 他人主页 | `p_personal-index.js`、详情页线索 | 公开主页、宝贝、信用、评价字段 | `attention.relation`、联系/会话入口 | 公开可读；关注和联系 A3 |
| `/collection` 收藏 | `p_collection-index.js` | `user.page.head`、`favor.item.list`、`xyh.item.list` | `collect.item`、`attention.relation` | 列表只读 A2；取消收藏/关注 A3 |
| `/bought` 买到的 | `p_bought-index.js` | `idle.web.trade.bought.list`、`trade.order.render`、`trade.order.close.reason.get`、`mtee.risk.get` | `trade.order.cancel`、`trade.order.create`、`order.modify.price.render`、地址查询、延长收货/调价 | 订单列表只读 A2；任何订单动作 A4 |
| `/order-detail?orderId=...` 买家订单详情 | `p_order-detail-index.js` | `idle.web.trade.order.detail`、物流查询、订单渲染、商品详情/推荐 | `trade.data.update`、`order.cancel`、`order.create`、`order.modify.price.render`、`unconsign.detail`、地址查询 | 详情只读 A2；交易/物流/售后动作 A4 |
| `/create-order?itemId=...` 确认订单 | `p_create-order-index.js` | `trade.order.render`、`user.page.nav` | `trade.order.create`、`trade.pay.info.query`、地址查询 | 只读确认页 A2；下单/支付/地址 A4 |
| `/pay-success?orderId=...` 支付结果 | `p_pay-success-index.js` | 订单渲染、推荐、风控状态 | 支付信息、创单、取消、调价、地址查询 | 结果页只读 A2；支付/订单动作 A4 |
| `/publish` 发闲置 | `p_publish-index.js` | `idleitem.preget`、`service.status.query`、`property.search`、`local.poi.get` | `draft.edit`、`draft.publish`、`idleitem.publish`、`idleitem.edit`、`prepublish.check`、服务卡 | 可辅助草稿 A2/A3；发布/保存/编辑 A4 |
| `/im` 消息 | `p_im-index.js`、`p_layout.js` | 会话同步、用户查询、红点、商品工具查询、快捷回复列表、交易头信息 | `message.card.send`、未读清理、黑名单、文件权限、语音转换、取消订单/调价等订单卡能力 | 默认只看框架 A2；读具体私聊/发送/清未读/拉黑 A3/A4 |
| `/account` 账号与安全 | `p_account-index.js`、`p_account-api.js` | `user.page.account`、`profile.notice.query`、`user.page.nav` | `profile.notice.update`、消息未读清理、关注关系、IM token | 状态只读 A2；通知开关/账号动作 A3 |
| `/feedback?from=...` 反馈 | `p_feedback-index.js` | `user.page.nav` | 截图上传和提交属于页面动作，未在本包暴露独立高风险 mtop 名称 | 可写草稿；上传/提交 A3 |
| `/login` | `p_login-index.js` | 登录页面结构 | 登录、验证码、扫码由平台流程处理 | A4，用户本人完成 |
| `/find-account` | `p_find-account-index.js` | 页面标题/跳转占位 | 找回账号流程 | A4，只识别不代办 |
| `/select-account` | `p_select-account-index.js` | 页面标题/跳转占位 | 选择/切换账号流程 | A4，多账号走 Profile 隔离 |
| `/login-validation` | `p_login-validation-index.js` | 登录校验占位 | 验证码/风控校验 | A4，不代填验证码 |
| `/common-video` | `p_common-video-index.js` | `gaia.idle.data.gw.v2.index.get` | 无页面专属写接口 | A1/A0，只读活动/视频容器 |
| `/upgrade-browser` | `p_upgrade-browser-index.js` | 无业务 mtop | 下载链接 | A0，只读；下载安装前确认 |
| `/changelog` | 主入口路由线索 | 当前没有独立业务接口包 | 无 | A0，只读更新日志 |
| `/playground` | `p_playground-index.js` | `user.page.nav` | `idle.user.account.sub.test`、支付/上传/登录测试入口 | A4，内部实验不主动访问 |
| 验货宝确认订单 | `p_create-order-yhb-index.js` | `yhb.order.create.render` 也属于下单前渲染 | `yhb.order.create`、支付信息、地址查询 | A4，不触发验货宝下单 |
| 验货宝订单详情 | `p_order-detail-yhb-index.js` | `pc.trade.full.info`、`galaxy.report.detail`、推荐 | `yhb.dispute.apply.list`、评价执行、收藏关系 | A4，只读报告/状态，不售后/评价 |

## 卖家工作台公共能力

| 来源包 | 能力 | 代表接口 | 风险 |
| --- | --- | --- | --- |
| `seller-workbench-main.js` | 工作台外壳、菜单、登录商家、身份、子账号导航 | `sys.menu.query`、`query.login.merchant.info`、`user.business.identity.get`、`idle.user.account.sub.nav` | A2 |
| `seller-workbench-main.js` | 备注修改 | `user.remark.update` | A3 |
| `seller-workbench-vendors.js` | 订单、发货、退款、投诉、评价、客服、财务、地址、IM 的共享接口 | 多个 `merchant.*`、`logistics.*`、`idlemessage.*`、`dispute.*` 接口 | A2/A3/A4 |
| `idle-seller-data-main.js` | 数据罗盘、客服数据、粉丝/流量/退款/商品指标 | `datacompass.*.summary/list/query` | A2 |
| `idle-seller-data-main.js` | 数据导出和 Excel URL | `datacompass.*.export`、`*.excel.url` | A3 |

## 卖家工作台页面对照

| 页面/hash | 主要来源 | 只读能力 | 写入/高风险能力 | 结论 |
| --- | --- | --- | --- | --- |
| `#/seller-data/data` 数据总览 | `idle-seller-data-main.js` | 数据罗盘起始时间、商家信息、买家画像、粉丝、流量、营销、退款概要 | 报表导出、Excel URL、账号 mock apply/cancel | 指标只读 A2；导出/账号模拟 A3/A4 |
| `#/seller-data/commodity` 商品数据 | `idle-seller-data-main.js` | 商品列表、商品指标、类目查询、商品流量 | 商品列表导出、用户市场商品列表 | 表头可读 A2；导出 A3 |
| `#/seller-data/fanData` 粉丝数据 | `idle-seller-data-main.js` | 粉丝洞察、粉丝汇总、用户画像 | 画像明细导出相关能力 | 脱敏只读 A2；导出 A3 |
| `#/seller-data/customerService` 客服数据 | `idle-seller-data-main.js` | 客服概览、咨询明细、分流、评价列表 | 客服明细/概览/分流/评价导出、Excel URL | 只读 A2；导出 A3 |
| `#/seller-item/publish` 商品发布 | `seller-workbench-vendors.js`、发布相关包 | 类目、属性、服务状态、草稿结构 | 发布、编辑、保存、上传 | 草稿辅助 A2/A3；发布 A4 |
| `#/seller-item/goods-manage` 商品管理 | `seller-workbench-vendors.js` | 商品统计、商品列表、状态筛选 | 改价、下架、删除、批量操作 | 列表只读 A2；经营动作 A3/A4 |
| `#/seller-item/post-temple` 运费模板 | `seller-workbench-vendors.js` | 模板列表、地址和物流配置 | 新建、编辑、删除、设默认 | 只读 A2；保存/删除 A3 |
| `#/seller-item/post-temple/create` 创建模板 | `seller-workbench-vendors.js` | 发货地、计费方式、区域结构 | 保存模板、区域规则 | 草稿 A2/A3；保存 A3 |
| `#/seller-trade/order-manage` 订单管理 | `seller-workbench-vendors.js` | 订单表、关闭原因、物流渲染、交易头信息 | 发货、重新发货、批量延长收货、提醒收货、关单、改价、备注、导入发货 | 列表只读 A2；履约/订单动作 A4 |
| `#/seller-trade/order-manage/order-detail?orderId=...` 卖家订单详情 | `seller-workbench-vendors.js` | 订单详情、物流、地址修改信息、交易消息 | 同意/拒绝改地址、发货、备注、关单、改价 | 深层页只读 A2；真实订单动作 A4 |
| `#/seller-trade/refund-manage` 退款管理 | `seller-workbench-vendors.js` | 退款详情、退运费详情、赔付详情、原因列表 | 同意退款、拒绝退款、拒绝退运费、赔付支付/拒绝 | A4，高风险售后 |
| `#/seller-trade/evaluation-manage` 评价管理 | `seller-workbench-vendors.js` | 评价列表、评价状态 | `merchant.rate.create`、联系/举报 | 只读 A2；评价动作 A3/A4 |
| `#/seller-trade/complaint-manage` 投诉管理 | `seller-workbench-vendors.js` | 投诉详情、退钱页、纠纷创建页 | 投诉拒绝、撤销、举证、主动/被动举证、创建纠纷 | A4，高风险纠纷 |
| `#/seller-trade/refund-address` 退货地址 | `seller-workbench-vendors.js` | 退货地址列表 | 新增/编辑/删除/默认地址相关动作 | 地址只读 A2；修改 A3 |
| `#/seller-finance/income-bill` 收入账单 | `seller-workbench-vendors.js`、数据包 | 收入表、日期、业务类型 | 下载、导出、Excel URL | 财务只读 A2；导出 A3 |
| `#/seller-finance/expense-bill` 支出账单 | `seller-workbench-vendors.js`、数据包 | 支出表、费用类型 | 下载、导出、Excel URL | 财务只读 A2；导出 A3 |
| `#/seller-finance/invoice-apply` 申请发票 | `seller-workbench-vendors.js` | 发票申请记录、业务类型 | 申请发票、导出、修改开票资料 | 只读 A2；申请/导出 A3 |
| `#/seller-finance/basic-info` 基础信息 | `seller-workbench-vendors.js` | 发票主体、资质字段 | 修改主体资料、保存 | 只读字段名 A2；修改 A3 |
| `#/seller-account/sub-account` 子账号管理 | `seller-workbench-main.js`、`idle-seller-data-main.js` | 子账号导航、用户组成员列表、商家身份 | 新建、停用、改权限、分流配置 | 权限只读 A2；变更 A4 |
| `#/im-cs-dispatch/customer-routing-service` 客服分流 | `seller-workbench-vendors.js` | 客服/分组/分流规则列表 | 保存规则、启停、接待转移 | 只读 A2；保存/启停 A4 |
| `#/seller-sc/home` 安全中心 | `seller-workbench-vendors.js` | 风控/违规/处罚状态、风险查询 | 申诉、处理、证明材料 | 只读 A2；处理/申诉 A4 |
| `#/seller-ad/home` 超级擦亮 | `idle-seller-data-main.js`、营销接口 | 营销数据、活动列表、投放指标 | 新建计划、付费投放、营销增强 | 只读 A2；投放 A4 |
| `#/notification-center` 通知中心 | `seller-workbench-main.js`、共享包 | 通知列表、未读状态 | 标已读、清未读 | 结构只读 A2；状态变更 A3 |
| `#/im` 工作台消息 | `seller-workbench-vendors.js` | 会话、客服信息、快捷回复列表、文件权限 | 发送卡片、发文件、快捷回复维护、黑名单、转接/离开/重进会话、标已读 | 框架只读 A2；消息/关系动作 A3/A4 |
| `#/im-desktop` 桌面版 IM | 工作台外壳 | 下载/打开客户端入口 | 下载、安装、打开本机客户端 | A3，确认后才下载/安装 |
| `#/select-site` 站点选择 | `seller-workbench-main.js` | 站点/身份列表 | 切换站点 | A3，确认后才切换 |
| `#/account-check` 账号检查 | `seller-workbench-main.js` | 账号检查、身份判断 | 继续前往、重新登录、切账号 | A3/A4 |
| `#/login` 工作台登录 | 工作台外壳 | 登录态判断 | 登录/扫码/验证码 | A4，用户本人完成 |
| `#/no-permission` 无权限 | 工作台外壳 | 无权限状态 | 无业务动作 | A0，只作为失败状态 |
| `#/iframe` 外部容器 | 工作台外壳 | iframe 加载和权限状态 | 外部页面内动作未知 | A3/A4，不能跨域盲点 |
| `#/download` 下载入口 | 工作台外壳 | 下载说明 | 下载/安装 | A3 |
| `#/playground` 工作台实验 | 工作台外壳/共享包 | 测试结构 | 测试动作 | A4，不主动触发 |

## 接口家族到页面的反向索引

| 接口家族 | 主要页面 | 风险解释 |
| --- | --- | --- |
| `idlehome.home.webpc.feed` | 首页、频道、搜索推荐 | 公开商品流，默认只读 |
| `idlemtopsearch.pc.*` | 搜索、公共布局 | 搜索建议和搜索结果可读；地区/定位弹层要等稳定 |
| `idle.web.user.page.*` | 个人、收藏、账号、公共导航 | 登录后个人结构；输出脱敏 |
| `idle.web.xyh.item.list`、`favor.item.list` | 个人、收藏 | 商品列表只读；商品标题/ID 不写入文档 |
| `idle.collect.item`、`attention.relation` | 商品、收藏、个人 | 改变收藏/关注关系，必须确认 |
| `idle.pc.detail`、`item.web.recommend.list` | 商品详情、订单详情推荐 | 商品结构可读；下单/联系另算 |
| `idleitem.*`、`idle.pc.idleitem.*` | 发布、搜索发布入口、卖家发布 | 草稿/编辑/发布，保存和发布前确认 |
| `trade.order.*`、`trade.pay.*` | 买到的、订单详情、确认订单、支付结果、IM 订单卡 | 交易/支付/订单状态，高风险 |
| `logistic.*` | 订单详情、卖家发货、地址 | 物流和地址敏感；发货/改地址高风险 |
| `merchant.refund.*`、`compensate.*`、`postage.refund.*` | 卖家退款/售后 | 退款、赔付、退运费拒绝，高风险 |
| `cco.shop.complain.*`、`merchant.dispute.*` | 投诉、纠纷 | 举证、撤销、拒绝、创建纠纷，高风险 |
| `idlemessage.*` | 主站 IM、工作台 IM、公共布局、账号通知 | 会话/未读/发送/黑名单/文件/快捷回复；默认只看框架 |
| `datacompass.*` | 卖家数据、商品数据、粉丝、客服、财务 | 经营数据只读脱敏；导出/Excel URL 前确认 |
| `seller.platform.*`、`usergroup.*`、`account.sub.*` | 工作台外壳、子账号、权限 | 身份、权限、站点和子账号，变更前确认 |
| `alipay.verify.*`、登录/验证相关 | 账号、支付、认证、登录流程 | 用户本人处理，不代过认证/验证码 |

## 自动化准入规则

1. 先用 `goofish-route-inventory.md` 定位页面和证据等级。
2. 再用本表看页面包背后的接口家族，确认是否牵到交易、消息、财务、权限或账号状态。
3. 再用 `goofish-page-state-modal-inventory.md` 判断当前页面是否处于加载、空态、登录、无权限、二维码或确认弹窗。
4. 最后用 `goofish-action-gate-matrix.md` 决定动作等级。
5. 若任何一层达到 A3/G3 或 A4/G4，必须停下让用户确认；A4 默认只说明结构和风险。

结论：主站公开浏览和搜索可以做只读巡检；登录后个人、收藏、订单、消息和账号页只能脱敏只读；卖家工作台几乎每个经营页都连接到导出、发货、售后、客服、财务或权限接口，必须把“页面可见”与“动作可执行”严格分开。
