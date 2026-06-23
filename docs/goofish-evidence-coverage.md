# 闲鱼页面证据覆盖清单

日期：2026-06-22  
用途：把“哪些页面实际看过、哪些只是静态确认、哪些只知道能力边界”分开，避免把推断当成实测结论。  
范围：当前工作区 31 个前端 JS 文件、已登录只读页面探索、卖家工作台只读巡检，以及已生成的页面地图/路由/字段/动作/API 文档。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于按页面条目读取证据等级和就绪状态。

配套导航定位：`goofish-navigation-selector-guide.md`，用于在确认证据等级后继续判断页面加载信号、稳定锚点和失败状态。

配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`，用于把证据等级、页面层级、锚点和停止点放到同一行检查。

配套站点层级：`goofish-site-taxonomy.md`，用于把证据覆盖放回主站、卖家工作台、边缘页和容器页的层级中。

配套任务流手册：`goofish-task-workflow-runbook.md`，用于把已确认页面放到买家/卖家任务路径中，明确能读、能写草稿和必须停的位置。

配套控件清单：`goofish-ui-control-inventory.md`，用于把已确认页面继续拆成控件类型和稳定定位点。

配套页面接口对照：`goofish-page-api-crosswalk.md`，用于把已确认页面继续映射到接口家族和高风险能力。

配套状态清单：`goofish-page-state-modal-inventory.md`，用于把已确认页面继续分成正常内容、加载、空态、错误、门禁、弹窗和高风险业务态。

## 证据等级

| 等级 | 说明 | 能做什么 | 不能做什么 |
| --- | --- | --- | --- |
| Live + Static | 浏览器看过页面骨架，且本地前端包/API 线索能对上 | 可只读、截图、读字段名、做脱敏摘要 | 不自动提交、发送、支付、导出、修改 |
| Live Only | 浏览器看过入口或弹层，但静态包价值有限或是外链 | 只读结构和入口类型 | 不外发内容、不下载/安装 |
| Static Only | 从本地包、路由、接口名确认存在，未触发真实业务流程 | 只记录页面能力和风险 | 不主动访问高风险流程 |
| Shell/Container | 登录、权限、站点、iframe、下载、外壳容器 | 用于判断导航或门禁 | 不把容器当业务页面操作 |
| Deep/Param | 带订单、商品、用户、账号等参数的深层页 | 用户明确给上下文后只读 | 不拼真实参数，不猜测访问 |
| Boundary Only | 只记录能力和风险，明确不实测 | 写规则、草稿和确认点 | 不触发真实交易/账号/经营状态 |

## 当前资产证据

| 资产组 | 数量 | 说明 |
| --- | --- | --- |
| 主站公共 JS | 3 | `main.js`、`p_layout.js`、`p_search-index.js` |
| 主站页面/能力包 | 25 | `work/www-assets/full/*.js` |
| 卖家工作台包 | 3 | `idle-seller-data-main.js`、`seller-workbench-main.js`、`seller-workbench-vendors.js` |
| 抽取到的 `mtop` 名称 | 225 | 包括运行时、配置和业务接口名 |
| 业务接口名 | 200 | 已在 `goofish-static-api-audit.md` 按风险组整理 |
| 当前输出文档 | 6 | 页面地图、速查表、路由索引、动作门禁、字段清单、接口审计 |

## 主站页面覆盖

| 页面/路由 | 证据 | 本地包/来源 | 覆盖结论 | 下一步边界 |
| --- | --- | --- | --- | --- |
| `/` 首页 | Live + Static | `p_index.js`、`main.js` | 已理解首页搜索、大类、频道、推荐流和右侧工具条 | 可公开搜索/浏览 |
| `/search?q=...` 搜索 | Live + Static | `p_search-index.js`、`p_layout.js` | 已理解排序、价格、区域、标签筛选和商品卡加载 | 地区弹层避免误点分页 |
| `/mach-feeds?machId=...` 频道流 | Live + Static | `p_mach-feeds-index.js` | 已理解频道/活动商品流结构 | 只读商品卡 |
| `/item?id=...&categoryId=...` 商品详情 | Live + Static | `p_item-index.js` | 已理解图片、价格、描述、保障、卖家卡、推荐、商品码 | 收藏/联系/购买前确认 |
| `/personal` 当前主页 | Live + Static | `p_personal-index.js` | 已理解主页、宝贝、信用、宝贝管理和左侧导航 | 编辑资料/上下架前确认 |
| `/personal?userId=...` 他人主页 | Live + Static | `p_item-index.js`、`p_im-index.js` 线索 | 已确认参数形态和公开主页风险 | 不主动关注/联系 |
| `/collection` 收藏 | Live + Static | `p_collection-index.js` | 已理解收藏 tab、商品卡、取消收藏、我想要 | 变更收藏/购买意向前确认 |
| `/bought` 买到的 | Live + Static | `p_bought-index.js` | 已理解订单 tab、订单卡、常见按钮和售后入口 | 订单内容只脱敏摘要 |
| `/order-detail?orderId=...` 订单详情 | Live + Static | `p_order-detail-index.js` | 已理解订单、物流、地址、售后字段类型 | 不记录真实订单/地址/物流 |
| `/create-order?itemId=...` 确认订单 | Live + Static | `p_create-order-index.js` | 已理解地址、运费、支付方式、优惠区字段 | 不提交订单/支付/改地址 |
| `/publish` 发闲置 | Live + Static | `p_publish-index.js` | 已理解图片、描述、属性、规格、价格、发货设置 | 上传/发布前确认 |
| `/im` 消息 | Live + Static | `p_im-index.js`、`p_layout.js` | 已理解空态、会话框架、输入区和消息接口风险 | 默认不读具体会话 |
| `/account` 账号与安全 | Live + Static | `p_account-index.js`、`p_account-api.js` | 已理解基本信息、通知、认证、安全中心模块 | 不改账号/认证/安全设置 |
| `/feedback?from=...` 反馈 | Live + Static | `p_feedback-index.js` | 已理解反馈类型、问题页面、文本框、截图上传、提交 | 上传/提交前确认 |
| `/changelog` 更新日志 | Live Only | `main.js` 路由线索 | 已做公共只读记录，本地没有独立页面包 | 只读 |
| `/login` 登录 | Live + Static | `p_login-index.js` | 已理解扫码、短信、密码和回跳 | 用户本人处理验证码/扫码 |
| `/pay-success?orderId=...` 支付成功 | Static Only | `p_pay-success-index.js` | 只确认结果页能力 | 不为测试触发支付 |
| `/find-account` 找回账号 | Static Only | `p_find-account-index.js` | PC 包为占位/回首页 | 不主动找回账号 |
| `/select-account` 选择账号 | Static Only | `p_select-account-index.js` | PC 包为占位/回首页 | 多账号走独立 Profile |
| `/login-validation` 登录校验 | Static Only | `p_login-validation-index.js` | 空片段/校验占位 | 不代过风控 |
| `/common-video` 公共视频 | Static Only | `p_common-video-index.js`、`p_common-video-layout.js` | 已理解活动内容配置和视频布局字段 | 不主动播放/下载 |
| `/upgrade-browser` 升级浏览器 | Static Only | `p_upgrade-browser-index.js` | 已理解推荐浏览器提示 | 不自动下载 |
| `/playground` 内部实验 | Static Only | `p_playground-index.js` | 已确认含账号/支付/埋点测试能力 | 禁止主动访问/触发 |
| 验货宝确认订单 | Static Only | `p_create-order-yhb-index.js` | 已确认验货宝确认订单接口和风险 | 不触发下单 |
| 验货宝订单详情 | Static Only | `p_order-detail-yhb-index.js` | 已确认报告、纠纷、评价相关能力 | 不触发售后/评价 |

## 卖家工作台页面覆盖

基础域名：`https://seller.goofish.com/?site=COMMONPRO#...`

| Hash 路由 | 证据 | 覆盖结论 | 下一步边界 |
| --- | --- | --- | --- |
| `#/seller-data/data` | Live + Static | 已理解数据总览日期、指标卡、分布模块 | 不记录真实数字 |
| `#/seller-data/commodity` | Live + Static | 已理解商品数据搜索、表头和下载入口 | 下载前确认 |
| `#/seller-data/fanData` | Live + Static | 已理解粉丝洞察和分布模块 | 不记录真实人群/地域数字 |
| `#/seller-data/customerService` | Live + Static | 已理解客服监控、实时咨询、满意度字段 | 导出前确认 |
| `#/seller-item/publish` | Live + Static | 已理解商品发布字段、草稿状态、发货设置 | 上传/发布前确认 |
| `#/seller-item/goods-manage` | Live + Static | 已理解商品筛选、状态、表头、批量操作 | 改价/下架/编辑前确认 |
| `#/seller-item/post-temple` | Live + Static | 已理解运费模板列表和创建入口 | 新建/删除/设默认前确认 |
| `#/seller-item/post-temple/create` | Live + Static | 已理解模板名称、发货地、计费方式、区域弹窗 | 保存前确认 |
| `#/seller-trade/order-manage` | Live + Static | 已理解订单状态、筛选、表头、发货/备注/联系按钮 | 发货/改物流/联系前确认 |
| `#/seller-trade/order-manage/order-detail?orderId=...` | Deep/Param | 静态确认深层卖家订单详情路由 | 不拼真实订单号 |
| `#/seller-trade/refund-manage` | Live + Static | 已理解退款类型、状态、原因、物流和操作字段 | 同意/拒绝/确认收货前确认 |
| `#/seller-trade/evaluation-manage` | Live + Static | 已理解评价筛选、表头和批量评价 | 评价/举报/联系前确认 |
| `#/seller-trade/complaint-manage` | Live + Static | 已理解投诉状态、表头、详情和违规入口 | 举证/处理前确认 |
| `#/seller-trade/refund-address` | Live + Static | 已理解退货地址表头和操作按钮 | 地址新增/编辑/删除前确认 |
| `#/seller-finance/income-bill` | Live + Static | 已理解收入账单 tab、表头、导出入口 | 不记录真实金额 |
| `#/seller-finance/expense-bill` | Live + Static | 已理解支出账单 tab、表头、导出入口 | 不记录真实费用 |
| `#/seller-finance/invoice-apply` | Live + Static | 已理解申请发票 tab、业务类型、申请/导出入口 | 申请/导出前确认 |
| `#/seller-finance/basic-info` | Live + Static | 已理解开票主体字段名 | 不记录主体真实资料 |
| `#/seller-account/sub-account` | Live + Static | 已理解子账号表头、状态、分流配置 | 新建/停用/改权限前确认 |
| `#/im-cs-dispatch/customer-routing-service` | Live + Static | 已理解客服分流规则表、分组、参与客服 | 保存/启停前确认 |
| `#/seller-sc/home` | Live + Static | 已理解安全中心违规字段和申诉状态 | 查看详情/申诉前确认 |
| `#/seller-ad/home` | Live + Static | 已理解超级擦亮指标、日期和新建计划 | 新建投放前确认 |

## 工作台外壳覆盖

| Hash 路由 | 证据 | 覆盖结论 | 下一步边界 |
| --- | --- | --- | --- |
| `#/notification-center` | Live + Static | 已理解通知中心结构 | 标已读/清未读前确认 |
| `#/notification-center/api*` | Static Only | 内部 API/接口定义模块 | 不当作页面 |
| `#/im` | Live + Static | 已理解工作台消息框架 | 不读/发送具体会话 |
| `#/im-desktop` | Live + Static | 已理解桌面版消息容器 | 下载/安装/发消息前确认 |
| `#/download` | Static + Live entry | 已理解卖家 IM 客户端下载弹层 | 不自动下载/安装 |
| `#/select-site` | Live + Static | 已理解站点选择结构 | 切换前确认 |
| `#/account-check` | Live + Static | 已理解账号检查/继续前往门禁 | 不自动切号/继续 |
| `#/login` | Shell/Container | 工作台登录容器 | 用户本人扫码/验证码 |
| `#/no-permission` | Live + Static | 无权限判断页 | 只作为失败状态 |
| `#/iframe?url=...` | Shell/Container | 外部页面承载容器 | 来源明确后再判断 |
| `#/playground` | Static Only | 内部实验页 | 禁止主动访问 |

## 接口覆盖

| 分组 | 数量 | 证据 | 使用规则 |
| --- | --- | --- | --- |
| 搜索/首页 | 5 | 静态抽取 | 可辅助理解公开搜索，不直接绕页面调用 |
| 个人/收藏 | 5 | 静态抽取 | 只读/脱敏，收藏关系变更前确认 |
| 商品/发布/服务 | 22 | 静态抽取 | 草稿可辅助，发布/编辑/下架前确认 |
| 交易/售后/物流/支付 | 71 | 静态抽取 | 默认高风险，不主动调用 |
| IM/消息 | 46 | 静态抽取 | 不读取/发送具体会话，关系/未读状态变更前确认 |
| 数据/财务/经营分析 | 26 | 静态抽取 | 只读字段，导出下载前确认 |
| 账号/权限/风控 | 10 | 静态抽取 | 只读判断，认证/权限/切号前确认 |
| 其他/基础能力 | 15 | 静态抽取 | 继承入口页面风险 |

## Boundary Only 清单

这些能力已经知道入口、接口或按钮，但不应为了“熟悉页面”而触发：

- 真实支付、提交订单、再次购买。
- 确认收货、延长收货、取消/关闭订单。
- 退款、拒绝退款、退运费、赔付。
- 发货、改物流、批量导入发货、上传发货 Excel。
- 投诉、撤销投诉、举证、申诉、仲裁/纠纷消息。
- 发消息、发商品/订单卡片、文件上传、拉黑/移出黑名单。
- 发布、编辑、改价、上架、下架、删除、批量下架。
- 导出财务、导出数据、下载全量明细、申请发票。
- 新建子账号、停用账号、改权限、改客服分流规则。
- 实名、支付宝认证、账号找回、账号选择、验证码、扫码、风控校验。
- 内部实验页、账号测试、支付测试、埋点测试。

## 缺口和下一步

当前已经覆盖：

- 主站常规页面、边缘静态包、参数形态。
- 卖家工作台左侧菜单、外壳容器、深层卖家订单详情线索。
- 200 个业务接口的风险分组。
- 页面动作门禁和字段敏感等级。

仍不声称完成的部分：

- 平台未暴露给当前账号/当前入口的隐藏页面。
- 需要真实交易、真实售后、真实发货、真实支付、真实认证才能进入的状态页。
- 需要其他账号权限、其他站点身份或特定经营资质才能看到的页面。

后续如果继续深入，应只做公开页或用户明确指定的只读任务路径；不要为了补齐覆盖而制造交易、售后、账号安全或经营状态。
