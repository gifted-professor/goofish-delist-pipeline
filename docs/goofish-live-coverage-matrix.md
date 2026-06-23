# 闲鱼登录后 Live 覆盖矩阵

日期：2026-06-22  
用途：把当前已登录浏览器 Profile 的主站与卖家工作台页面做一次只读覆盖巡检，补充静态页面地图之外的“当前能否进入、呈现什么页面态、哪里必须停”。  
边界：本矩阵只记录路由、页面族、页面态、DOM 控件数量、控件类别和停止点；不记录真实账号、店铺、订单、地址、聊天、商品标题、金额、经营数字、图片链接、二维码、验证码、cookie、token 或本地存储。

总索引：`goofish-master-index.md`  
页面清单：`goofish-page-manifest.json`  
探测策略：`goofish-probe-policy.json`  
登录冒烟：`goofish-login-session-smoke-test.md`  
动作门禁：`goofish-action-gate-matrix.md`

## 方法

- 使用当前已登录浏览器 Profile。
- 每个入口只做 `goto` + 等待页面稳定 + DOM 结构读取。
- 不点击按钮，不填表，不打开具体订单，不进入具体会话，不导出，不上传，不保存。
- URL 参数统一写成 `<redacted>` 或 `<probe>`。
- 页面标题只做类别判断，不写真实标题内容。
- 左侧菜单和全站导航会把通用词带到很多页面，所以本矩阵以当前路由、控件数量、输入类型、状态和停止点为准。

## 状态口径

| 状态 | 含义 |
| --- | --- |
| `normal` | 主站页面可进入，未遇到登录、无权限或风控门禁 |
| `normal-workbench` | 卖家工作台页面可进入，外壳/微前端正常承载 |
| `empty-state` | 页面可进入，但当前账号或筛选条件下出现空态 |
| `login-gate-signal` | 页面可进入，但出现登录/账号类信号，继续动作前要人工确认 |
| `gate-state` | 页面本身属于账号检查、站点选择、无权限等门禁族 |
| `risk-signal` | 页面出现风控、付费推广、账号安全或高影响业务信号，后续只读 |

## 主站页面

| 页面 id | 路由 | 页面族 | Live 状态 | 结构锚点 | 停止点 |
| --- | --- | --- | --- | --- | --- |
| `www.home` | `/` | `public-discovery` | `normal` | 搜索输入、公开卡片流、全站导航 | 收藏、联系、购买、发布 |
| `www.search` | `/search?q=<probe>` | `public-discovery` | `normal` | 搜索输入、筛选/排序、结果卡片、确认类按钮信号 | 支付、购买、确认、收藏、发布 |
| `www.machFeeds` | `/mach-feeds` | `public-discovery` | `normal` | 频道流、搜索输入、导航入口 | 支付、收藏、登录切换 |
| `www.personal` | `/personal` | `buyer-account` | `normal` | 个人中心导航、账号页 tab、订单/发布入口 | 编辑资料、管理商品、下架、删除、切号 |
| `www.collection` | `/collection` | `buyer-account` | `normal` | 收藏 tab、账号页导航、列表框架 | 取消收藏、想要、联系、购买 |
| `www.bought` | `/bought` | `buyer-trade` | `normal` | 订单状态 tab、订单卡片框架、操作按钮区 | 支付、确认收货、退款、评价、联系、深层订单 |
| `www.account` | `/account` | `buyer-account` | `login-gate-signal` | 账号设置入口、登录类信号、上传类信号 | 修改资料、上传头像/材料、通知开关、实名、绑定、切号 |
| `www.publish` | `/publish` | `draft-input` | `normal` | 发布表单、文件输入、文本输入、价格/类目类字段 | 上传、保存、发布、覆盖已有商品 |
| `www.feedback` | `/feedback?from=<probe>` | `draft-input` | `normal` | 文本域、文件输入、提交入口 | 上传、提交、发送反馈内容 |
| `www.im` | `/im` | `message` | `normal` | 消息外壳、会话/导航框架 | 打开具体私聊、读私聊正文、发送、上传 |
| `www.login` | `/login` | `identity` | `normal` | 登录容器、iframe 外壳、账号入口 | 扫码、验证码、账号找回、切号 |
| `www.changelog` | `/changelog` | `public-content` | `normal` | 内容页外壳、App/消息类承接信号 | 下载、打开 App、发送、登录切换 |

## 主站控件密度

| 页面 id | 链接 | 按钮 | 输入 | iframe | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| `www.home` | 1089 | 1 | 1 | 1 | 公开流页面链接密度极高，只能读卡片结构 |
| `www.search` | 128 | 7 | 4 | 1 | 搜索/筛选/确认类控件并存 |
| `www.machFeeds` | 98 | 1 | 1 | 1 | 类频道流页面 |
| `www.personal` | 114 | 0 | 0 | 1 | 个人中心以链接和 tab 为主 |
| `www.collection` | 122 | 0 | 0 | 1 | 收藏列表以链接/卡片为主 |
| `www.bought` | 133 | 48 | 0 | 1 | 买家订单页动作按钮密度高，必须严格套 G3/G4 |
| `www.account` | 93 | 0 | 0 | 1 | 账号页出现登录/上传类风险信号 |
| `www.publish` | 86 | 3 | 9 | 1 | 发布页有文件输入和表单输入 |
| `www.feedback` | 87 | 1 | 2 | 1 | 反馈页有文本域和文件输入 |
| `www.im` | 56 | 0 | 0 | 1 | 本次只看消息外壳，不进入会话 |
| `www.login` | 82 | 0 | 0 | 2 | 登录容器 iframe 明显 |
| `www.changelog` | 90 | 0 | 0 | 1 | 内容/承接页 |

## 卖家工作台页面

| 页面 id | 路由 | 页面族 | Live 状态 | 结构锚点 | 停止点 |
| --- | --- | --- | --- | --- | --- |
| `seller.dataOverview` | `#/seller-data/data` | `seller-data` | `normal-workbench` | 工作台外壳、日期/指标类输入 | 记录真实数字、导出、下载 |
| `seller.commodityData` | `#/seller-data/commodity` | `seller-data` | `normal-workbench` | 搜索、表格、下载入口 | 记录商品真实数据、下载明细 |
| `seller.fanData` | `#/seller-data/fanData` | `seller-data` | `normal-workbench` | 日期/单选输入、粉丝数据外壳 | 记录画像数字、导出 |
| `seller.customerServiceData` | `#/seller-data/customerService` | `seller-data` | `empty-state` | 表格、导出入口、空态 | 导出客服明细、记录客户/客服真实值 |
| `seller.itemPublish` | `#/seller-item/publish` | `seller-item` | `normal-workbench` | 文件输入、发布表单、单选/搜索输入 | 上传、保存、发布 |
| `seller.goodsManage` | `#/seller-item/goods-manage` | `seller-item` | `normal-workbench` | 商品表、筛选、复选框、批量/设置入口 | 编辑、复制、改价、上下架、删除 |
| `seller.postTemplate` | `#/seller-item/post-temple` | `seller-item` | `empty-state` | 模板表、筛选、创建入口 | 创建、编辑、删除、设默认 |
| `seller.postTemplateCreate` | `#/seller-item/post-temple/create` | `seller-item` | `normal-workbench` | 模板表单、价格类输入、单选项 | 保存真实模板 |
| `seller.orderManage` | `#/seller-trade/order-manage` | `seller-trade` | `normal-workbench` | 订单表、筛选、复选框、高密度按钮 | 发货、备注、联系、改物流、查看钱款 |
| `seller.refundManage` | `#/seller-trade/refund-manage` | `seller-trade` | `normal-workbench` | 退款表、筛选、确认类入口 | 同意/拒绝退款、赔付、确认收货 |
| `seller.evaluationManage` | `#/seller-trade/evaluation-manage` | `seller-trade` | `normal-workbench` | 评价表、筛选、联系/评价入口 | 评价、举报、联系 |
| `seller.complaintManage` | `#/seller-trade/complaint-manage` | `seller-trade` | `normal-workbench` | 投诉表、投诉/联系入口 | 举证、撤销、拒绝、提交材料 |
| `seller.refundAddress` | `#/seller-trade/refund-address` | `seller-trade` | `normal-workbench` | 地址表、编辑/删除入口 | 新增、编辑、删除、设默认 |
| `seller.incomeBill` | `#/seller-finance/income-bill` | `seller-finance` | `normal-workbench` | 财务表、导出/下载入口 | 导出、下载全量明细、记录金额 |
| `seller.expenseBill` | `#/seller-finance/expense-bill` | `seller-finance` | `empty-state` | 财务表、导出/下载入口、空态 | 导出、下载、记录金额 |
| `seller.invoiceApply` | `#/seller-finance/invoice-apply` | `seller-finance` | `normal-workbench` | 发票表、导出/下载入口、复选框 | 申请发票、导出、下载 |
| `seller.basicInfo` | `#/seller-finance/basic-info` | `seller-finance` | `normal-workbench` | 主体信息表、财务外壳 | 修改主体资料、记录真实主体值 |
| `seller.subAccount` | `#/seller-account/sub-account` | `seller-account` | `empty-state` | 子账号表、新建入口、空态 | 新建、停用、改权限 |
| `seller.csDispatch` | `#/im-cs-dispatch/customer-routing-service` | `seller-account` | `empty-state` | 客服分流表、新建入口、空态 | 新建规则、保存分流配置 |
| `seller.securityCenter` | `#/seller-sc/home` | `seller-security` | `normal-workbench` | 违规/安全表、筛选输入、按钮区 | 查看敏感详情、申诉、处理、删除 |
| `seller.adHome` | `#/seller-ad/home` | `seller-ad` | `risk-signal` | 推广/投放外壳、新建入口、指标输入 | 新建计划、付费投放、记录投放数据 |
| `seller.notificationCenter` | `#/notification-center` | `seller-shell` | `normal-workbench` | 通知外壳、消息类别 | 打开敏感通知详情、下载 |
| `seller.im` | `#/im` | `seller-message` | `normal-workbench` | 消息外壳、搜索输入 | 打开具体私聊、发送、读取私聊正文 |
| `seller.imDesktop` | `#/im-desktop` | `seller-shell` | `normal-workbench` | 桌面消息外壳、搜索输入 | 打开具体私聊、发送 |
| `seller.download` | `#/download` | `seller-shell` | `normal-workbench` | 下载容器外壳 | 下载、安装、打开外部程序 |
| `seller.selectSite` | `#/select-site` | `seller-gate` | `normal-workbench` | 站点选择外壳 | 切换站点、切换账号 |
| `seller.accountCheck` | `#/account-check` | `seller-gate` | `gate-state` | 账号检查外壳、登录类入口 | 继续登录、账号检查、切号 |
| `seller.noPermission` | `#/no-permission` | `seller-gate` | `normal-workbench` | 权限外壳 | 申请/变更权限 |

## 卖家控件密度

| 页面 id | 按钮 | 输入 | 表格 | iframe | 说明 |
| --- | ---: | ---: | ---: | ---: | --- |
| `seller.dataOverview` | 0 | 30 | 0 | 1 | 指标页输入/筛选较多 |
| `seller.commodityData` | 25 | 8 | 2 | 1 | 商品数据页有表格和下载入口 |
| `seller.fanData` | 0 | 6 | 0 | 1 | 粉丝数据页偏图表/筛选 |
| `seller.customerServiceData` | 5 | 15 | 4 | 1 | 客服数据页表格多，当前空态 |
| `seller.itemPublish` | 5 | 13 | 0 | 1 | 发布页含文件输入 |
| `seller.goodsManage` | 29 | 39 | 2 | 1 | 商品管理页筛选/批量操作密集 |
| `seller.postTemplate` | 8 | 4 | 2 | 1 | 运费模板列表当前空态 |
| `seller.postTemplateCreate` | 4 | 9 | 0 | 1 | 模板创建表单含价格类输入 |
| `seller.orderManage` | 105 | 48 | 2 | 1 | 订单管理页动作最密集，必须最高警惕 |
| `seller.refundManage` | 61 | 17 | 2 | 1 | 退款管理页动作密集 |
| `seller.evaluationManage` | 47 | 36 | 2 | 1 | 评价管理页含联系/评价入口 |
| `seller.complaintManage` | 46 | 10 | 2 | 1 | 投诉管理页含投诉/联系入口 |
| `seller.refundAddress` | 23 | 10 | 1 | 1 | 地址页含编辑/删除入口 |
| `seller.incomeBill` | 10 | 5 | 1 | 1 | 收入账单含导出/下载 |
| `seller.expenseBill` | 6 | 4 | 1 | 1 | 支出账单当前空态但仍有导出/下载 |
| `seller.invoiceApply` | 9 | 7 | 1 | 1 | 发票页含复选框和导出/下载 |
| `seller.basicInfo` | 0 | 0 | 1 | 1 | 主体资料表只读 |
| `seller.subAccount` | 1 | 0 | 2 | 1 | 子账号表当前空态 |
| `seller.csDispatch` | 2 | 0 | 1 | 1 | 分流配置表当前空态 |
| `seller.securityCenter` | 43 | 5 | 2 | 1 | 安全中心含违规/申诉相关入口 |
| `seller.adHome` | 10 | 8 | 0 | 1 | 推广页为付费/经营影响高风险 |
| `seller.notificationCenter` | 0 | 0 | 0 | 1 | 通知外壳 |
| `seller.im` | 2 | 1 | 0 | 1 | 卖家消息外壳 |
| `seller.imDesktop` | 2 | 1 | 0 | 1 | 桌面消息外壳 |
| `seller.download` | 0 | 0 | 0 | 1 | 下载容器 |
| `seller.selectSite` | 0 | 0 | 0 | 1 | 站点门禁外壳 |
| `seller.accountCheck` | 0 | 0 | 0 | 1 | 账号检查门禁 |
| `seller.noPermission` | 0 | 0 | 0 | 1 | 权限门禁外壳 |

## 本轮增量结论

- 当前 Profile 的主站登录态覆盖更清楚：个人、收藏、订单、发布、反馈、消息外壳均可打开。
- `/account` 虽能打开，但出现登录/账号类信号，后续只做结构观察，涉及资料修改或认证时停。
- 买家订单页和卖家订单管理页是当前动作按钮最密集的两类页面，不能用通用点击策略。
- 卖家工作台大多数一级菜单可进入，且基本都由 iframe/微前端外壳承载。
- 卖家数据、财务、推广页面即使只是可见，也不能记录真实数值；只写字段名、表头、控件类别。
- 卖家交易、退款、评价、投诉、地址页均具备高影响操作入口；后续任何自动化都必须先进入 G3/G4 停止判断。
- 消息页当前只确认外壳、搜索/输入类结构，不读取具体私聊。
- 空态不是失败；它说明该页面结构可进入，但当前账号/状态下没有可展示行或该筛选无结果。

## 下一轮建议

1. 用本矩阵补充 `goofish-page-readiness-matrix.md` 的 Live 状态备注。
2. 对深层参数页保持只登记规则：`/item?id=...`、`/order-detail?orderId=...`、`#/seller-trade/order-manage/order-detail?orderId=...` 不猜参数。
3. 若要继续实测，只做“打开公开详情页/打开空态列表/打开表单不保存”三类低风险动作。
4. 若要多账号试跑，先新建独立 Profile，再重复本矩阵，不跨 Profile 复用登录材料。

结论：当前已登录 Profile 可以覆盖主站账号页、买家交易页、发布/反馈/消息外壳，以及卖家工作台大多数一级菜单。页面理解可以继续深入到表头、控件和状态层，但真实业务值和任何提交型动作必须继续隔离。
