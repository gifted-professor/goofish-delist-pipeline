# 闲鱼逐页就绪矩阵

日期：2026-06-22  
用途：把每个已识别页面按同一套维度对齐：站点层级、证据等级、稳定锚点、可读内容、任务入口、接口/控件风险、停止点和剩余缺口。  
边界：这是只读理解矩阵，不是完成声明；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于让脚本读取页面 id、路由、层级、锚点、可做动作和停止点。
配套主地图：`goofish-page-map.md`  
配套站点层级：`goofish-site-taxonomy.md`  
配套路由索引：`goofish-route-inventory.md`  
配套证据覆盖：`goofish-evidence-coverage.md`  
配套导航定位：`goofish-navigation-selector-guide.md`  
配套控件清单：`goofish-ui-control-inventory.md`  
配套状态清单：`goofish-page-state-modal-inventory.md`  
配套页面接口对照：`goofish-page-api-crosswalk.md`  
配套任务流手册：`goofish-task-workflow-runbook.md`  
配套动作门禁：`goofish-action-gate-matrix.md`

## 就绪等级

| 等级 | 含义 | 可做 | 不可做 |
| --- | --- | --- | --- |
| R0 | 公开只读就绪 | 打开、搜索、筛选、读公开结构 | 收藏、联系、购买 |
| R1 | 登录只读就绪 | 读字段名、tab、表头、状态类别，输出脱敏 | 写入账号、交易、消息或经营状态 |
| R2 | 草稿辅助就绪 | 填文本/价格/规格/反馈/IM/售后草稿 | 上传、提交、发送、保存、发布 |
| R3 | 确认门禁就绪 | 识别按钮、弹窗和后果，等待用户确认 | 默认点击确定 |
| R4 | 边界只读就绪 | 说明结构、入口、接口风险 | 为了测试触发支付、售后、认证、内部实验 |
| R5 | 外壳/容器就绪 | 判断登录、权限、站点、iframe、下载、无权限 | 把容器当业务页操作 |

## 主站逐页矩阵

| 页面 | 层级 | 证据 | 就绪 | 稳定锚点 | 可读/可辅助 | 首要停止点 |
| --- | --- | --- | --- | --- | --- | --- |
| `/` | M0 | Live + Static | R0 | 搜索框、频道入口、推荐商品卡、侧边工具条 | 搜索、看推荐、进频道、读卡片结构 | 消息、发布、订单入口进入登录区 |
| `/search?q=...` | M0 | Live + Static | R0 | 搜索框值、排序、价格输入、标签、商品卡、分页 | 改关键词、价格、排序、标签、读商品卡结构 | 地区弹层不稳定、收藏/联系/购买 |
| `/mach-feeds?machId=...&publishTimes=...` | M0 | Live + Static | R0 | 频道标题、瀑布流、商品卡链接 | 只读频道商品流 | 收藏/联系/购买 |
| `/item?id=...&categoryId=...` | M0/M3 | Live + Static | R0/R3 | 图片区、价格区、保障、卖家卡、按钮、推荐区 | 读商品公开结构、拟咨询草稿 | 收藏、聊一聊、立即购买、下架/删除 |
| `/personal?userId=...` | M0/M1 | Live + Static | R0/R3 | 公开主页、信用区、宝贝列表、关注/联系入口 | 只读公开主页结构 | 关注、联系、购买 |
| `/personal` | M1/M2 | Live + Static | R1/R3 | 左侧导航、主页 tab、宝贝/信用/管理 tab、筛选 | 只读当前主页、发布状态、管理入口 | 编辑资料、上下架、删除 |
| `/collection` | M1/M3 | Live + Static | R1/R3 | 收藏 tab、商品卡、取消收藏、我想要 | 只读收藏结构和状态类别 | 取消收藏、我想要、联系 |
| `/bought` | M1/M3 | Live + Static | R1/R4 | 订单 tab、订单卡、更多菜单、物流记录、宝贝快照 | 读订单状态类别和按钮结构 | 确认收货、退款、评价、删除、投诉 |
| `/order-detail?orderId=...` | M3 | Live + Static | R1/R4 | 状态节点、订单字段名、物流模块、售后/客服入口 | 只读字段名和状态节点 | 任何订单状态变更；不记录真实订单/地址 |
| `/create-order?itemId=...` | M3/M5 | Live + Static | R4 | 规格、数量、地址字段、价格明细、支付区、扫码付款 | 做下单前字段核对清单 | 提交订单、支付、改地址、认证 |
| `/pay-success?orderId=...&itemId=...` | M3 | Static Only | R4 | 支付结果结构、订单详情入口、推荐 | 只识别支付结果页能力 | 不为测试触发支付 |
| `/publish` | M2/M3 | Live + Static | R2/R3 | 图片/视频、描述、类目、属性、规格、价格、所在地、发货设置 | 写发布草稿、检查必填/校验 | 上传、保存草稿、发布、编辑已有商品 |
| `/publish?scene=xyPcMainPublish` | M2/M3 | Static Only | R2/R3 | 发布入口场景参数、发布表单字段 | 视作发布入口 | 保存/发布 |
| `/publish?scene=xyPcMainPublish&itemId=...` | M2/M3 | Static Only | R3/R4 | 带商品上下文的发布/编辑参数 | 识别编辑风险 | 保存、发布、覆盖已有商品 |
| `/im` | M1/M2/M3 | Live + Static | R1/R2/R3 | 空态、会话列表、输入区、工具栏、商品/订单卡、文件 | 看框架、拟消息草稿 | 读具体私聊、发送、发卡片、上传文件 |
| `/im?itemId=...&peerUserId=...` | M1/M3 | Deep/Param | R3/R4 | 商品关联会话参数、输入区 | 识别商品关联会话 | 读取具体会话、发送 |
| `/account` | M1/M5 | Live + Static | R1/R3 | 基本信息、保持登录、通知开关、认证、安全中心 | 只读模块和状态类别 | 通知开关、认证、切号、退出 |
| `/account/api` | M6 | Internal/Module | R5 | API 模块路径 | 不当作页面 | 不主动访问/调用 |
| `/feedback?from=...` | M2/M3 | Live + Static | R2/R3 | 反馈类型、问题页面、文本框、截图上传、提交 | 写反馈草稿 | 上传截图、提交 |
| `/changelog` | M0 | Live Only | R0 | 更新日志标题、功能条目 | 公共只读 | 无业务动作 |
| `/login` | M5 | Live + Static | R5 | 登录方式、扫码、验证码/安全入口、回跳参数 | 打开登录页 | 用户本人扫码/验证码 |
| `/login?spm=...&redirectURL=...` | M5 | Static Only | R5 | 登录回跳参数 | 识别登录回跳 | 不改登录参数，不代过风控 |
| `/find-account` | M5 | Static Only | R5 | 找回账号占位/跳转行为 | 只识别 | 不自动找回 |
| `/select-account` | M5 | Static Only | R5 | 选择账号占位/跳转行为 | 只识别 | 不自动切号 |
| `/login-validation` | M5 | Static Only | R5 | 登录校验占位 | 只识别 | 不代填验证码 |
| `/common-video` | M0/M6 | Static Only | R0/R4 | 视频容器、标题/素材配置、播放控件 | 只读活动/视频容器结构 | 主动播放、下载、抓取视频 |
| `/common-video/layout` | M6 | Internal/Module | R5 | 布局包路径 | 只作为静态证据 | 不当作页面 |
| `/upgrade-browser` | M0/M6 | Static Only | R0/R3 | 浏览器推荐列表、下载入口 | 只读推荐 | 下载/安装 |
| `/playground` | M6 | Static Only | R4/R5 | 内部测试入口、登录/上传/二维码/支付测试控件 | 只静态识别 | 禁止主动访问或触发 |
| 验货宝确认订单 | M3 | Static Only | R4 | 验货宝确认订单字段和接口 | 只记录结构和风险 | 不触发验货宝下单 |
| 验货宝订单详情 | M3 | Static Only | R4 | 报告、纠纷、评价相关字段 | 只读报告/状态能力 | 不触发售后/评价 |

## 卖家工作台逐页矩阵

| 页面/hash | 层级 | 证据 | 就绪 | 稳定锚点 | 可读/可辅助 | 首要停止点 |
| --- | --- | --- | --- | --- | --- | --- |
| `#/seller-data/data` | M4 | Live + Static | R1/R3 | 日期控件、指标卡、趋势图、说明弹层 | 读指标字段和模块名 | 记录真实数字、导出/下载 |
| `#/seller-data/commodity` | M4 | Live + Static | R1/R3 | 搜索、日期、商品表、指标列、分页、下载 | 读表头和筛选项 | 下载商品明细 |
| `#/seller-data/fanData` | M4 | Live + Static | R1/R3 | 日期、粉丝指标、画像分布、地域/人群模块 | 读画像模块名 | 记录真实画像数字、导出 |
| `#/seller-data/customerService` | M4 | Live + Static | R1/R3 | 咨询量、满意度、客服表格、导出 | 读客服表头和满意度字段 | 导出客服明细 |
| `#/seller-item/publish` | M2/M4 | Live + Static | R2/R3 | 图片/视频、标题/描述、类目、规格、价格、库存、发货设置 | 写商品草稿 | 上传、保存、发布 |
| `#/seller-item/goods-manage` | M4 | Live + Static | R1/R3 | 状态 tab、搜索/筛选、商品表、批量操作、操作列 | 读筛选和表头 | 编辑、复制、改价、上下架、删除 |
| `#/seller-item/post-temple` | M4 | Live + Static | R1/R3 | 模板列表、创建入口、操作列、删除/设默认弹窗 | 读模板字段 | 创建、编辑、删除、设默认 |
| `#/seller-item/post-temple/create` | M4 | Live + Static | R2/R3 | 模板名、发货地、计费方式、区域弹窗、保存 | 填模板草稿 | 保存真实模板 |
| `#/seller-trade/order-manage` | M3/M4 | Live + Static | R1/R4 | 订单状态 tab、搜索条件、日期、订单表、操作列 | 读订单状态和表头 | 发货、改物流、备注、联系、查看钱款 |
| `#/seller-trade/order-manage/order-detail?orderId=...` | M3/M4 | Deep/Param | R1/R4 | 状态节点、物流、地址修改、交易消息、操作按钮 | 用户给上下文后只读字段名 | 不拼真实订单号；订单动作前确认 |
| `#/seller-trade/refund-manage` | M3/M4 | Live + Static | R1/R4 | 退款类型、状态筛选、原因、物流、操作列 | 读退款状态和字段 | 同意/拒绝退款、赔付、确认收货 |
| `#/seller-trade/evaluation-manage` | M3/M4 | Live + Static | R1/R3 | 评价筛选、评价表、批量评价、举报/联系 | 读评价字段、拟回复草稿 | 评价、举报、联系 |
| `#/seller-trade/complaint-manage` | M3/M4 | Live + Static | R1/R4 | 投诉状态、投诉表、详情/举证入口 | 读投诉状态、拟申诉草稿 | 举证、撤销、提交材料 |
| `#/seller-trade/refund-address` | M4 | Live + Static | R1/R3 | 地址表、默认状态、操作列、新增/编辑/删除 | 读地址表头和状态类别 | 地址新增/编辑/删除 |
| `#/seller-finance/income-bill` | M4 | Live + Static | R1/R3 | 月/日/明细 tab、日期、业务类型、表格、导出/下载 | 读收入账单字段名 | 导出、历史下载、下载全量明细 |
| `#/seller-finance/expense-bill` | M4 | Live + Static | R1/R3 | 月/日/明细 tab、费用类型、表格、导出/下载 | 读支出账单字段名 | 导出/下载 |
| `#/seller-finance/invoice-apply` | M4 | Live + Static | R1/R3 | 待申请/已申请/旧版 tab、业务类型、申请、导出 | 读发票字段和按钮名 | 申请发票、导出 |
| `#/seller-finance/basic-info` | M4/M5 | Live + Static | R1/R3 | 主体资料表单、编辑/保存 | 只读字段名 | 修改主体资料 |
| `#/seller-account/sub-account` | M4/M5 | Live + Static | R1/R4 | 子账号表、岗位、状态、分流配置、新建/停用/权限 | 读权限字段和状态类别 | 新建、停用、改权限 |
| `#/im-cs-dispatch/customer-routing-service` | M4/M5 | Live + Static | R1/R4 | 分组、接待范围、参与客服、开关、保存 | 读分流规则结构 | 保存、启停、新建分组 |
| `#/seller-sc/home` | M4 | Live + Static | R1/R4 | 违规表、处罚状态、申诉状态、详情/申诉 | 读违规字段和状态类别 | 查看详情、申诉、处理 |
| `#/seller-ad/home` | M4 | Live + Static | R1/R4 | 日期、投放指标、计划入口、轮播控件 | 读推广字段、拟方案 | 新建计划、投放 |
| `#/notification-center` | M4 | Live + Static | R1/R3 | 通知列表、未读状态、详情、标已读/清未读 | 读通知结构和类别 | 标已读、清未读 |
| `#/notification-center/api*` | M6 | Static Only | R5 | 内部 API/接口定义模块 | 不当作页面 | 不主动调用 |
| `#/im` | M3/M4 | Live + Static | R1/R2/R3 | 会话列表、搜索、输入区、工具区、快捷回复、文件、转接 | 看框架、拟回复草稿 | 读具体会话、发送、文件、转接 |
| `#/im?itemId=...` | M3/M4 | Deep/Param | R3/R4 | 商品关联消息参数 | 识别会话入口 | 不拼参数、不发送 |
| `#/im-desktop` | M6 | Live + Static | R5/R3 | 下载/打开客户端提示 | 读容器结构 | 下载、安装、打开 |
| `#/download` | M6 | Static + Live entry | R5/R3 | 下载按钮、客户端类型 | 读下载入口 | 下载/安装 |
| `#/select-site` | M5 | Live + Static | R5/R3 | 站点/身份列表、选择按钮 | 读站点选择结构 | 切换站点 |
| `#/account-check` | M5 | Live + Static | R5/R3 | 账号检查、继续/重新登录/切换 | 读门禁结构 | 继续、重新登录、切账号 |
| `#/account-check?userNick=...` | M5 | Deep/Param | R5 | 带账号名检查参数 | 只识别参数形态 | 不拼真实账号名 |
| `#/login` | M5 | Shell/Container | R5 | 登录、扫码、验证码入口 | 打开登录页 | 用户本人处理 |
| `#/no-permission` | M5 | Live + Static | R5 | 无权限文案、返回/跳转 | 记录权限失败 | 无业务动作 |
| `#/iframe?url=...` | M6 | Shell/Container | R5 | iframe 来源、加载/失败状态 | 识别容器来源 | 外部页面动作另行确认 |
| `#/playground` | M6 | Static Only | R5/R4 | 测试入口 | 只静态识别 | 禁止主动触发 |

## 跨页能力就绪

| 能力 | 覆盖页面 | 就绪 | 核心停顿 |
| --- | --- | --- | --- |
| 公开找货 | `/`、`/search`、`/mach-feeds`、`/item` | R0 | 收藏/联系/购买 |
| 买家账号只读 | `/personal`、`/collection`、`/bought`、`/account` | R1 | 账号设置、收藏关系、订单动作 |
| 交易链路识别 | `/item`、`/create-order`、`/pay-success`、`/order-detail` | R4 | 下单、支付、确认收货、退款 |
| 发布草稿 | `/publish`、`#/seller-item/publish` | R2/R3 | 上传、保存、发布 |
| 消息框架 | `/im`、`#/im`、`#/im-desktop` | R1/R2/R3 | 读具体会话、发送、文件、卡片 |
| 卖家经营数据 | `#/seller-data/*`、`#/seller-finance/*` | R1/R3 | 导出、下载、记录真实数字 |
| 卖家交易售后 | `#/seller-trade/*` | R1/R4 | 发货、退款、评价、投诉、举证 |
| 权限和身份 | `/login`、`/account`、`#/select-site`、`#/account-check`、`#/login` | R5 | 验证码、扫码、认证、切号、改权限 |
| 容器和内部页 | `/playground`、`#/playground`、`#/iframe`、`/account/api` | R5 | 不主动访问或触发 |

## 仍不作为完成证明的缺口

- 未暴露给当前账号、当前站点或当前权限的隐藏页面。
- 需要真实支付、真实下单、真实售后、真实发货、真实认证才能出现的状态页。
- 需要其他账号、其他站点身份或特定经营资质才能进入的页面。
- 平台未来新增、改版或灰度页面。

结论：当前矩阵已经能把已识别页面放到统一执行口径下，但“所有闲鱼页面”仍按证据约束处理；未知/隐藏/真实交易触发页不为了补全而主动制造。
