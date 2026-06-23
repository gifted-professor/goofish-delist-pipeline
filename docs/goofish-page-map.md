# 闲鱼 Goofish 页面熟悉笔记

日期：2026-06-22  
状态：已登录态下的第一轮只读探索，已剔除账号、订单、聊天、经营数据等隐私内容。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于把长笔记里的页面结论转换成脚本可读条目。

配套速查表：`goofish-route-risk-cheatsheet.md`，用于执行前快速判断路由、证据等级、风险和是否需要确认。

配套接口审计：`goofish-static-api-audit.md`，用于查看本地前端包暴露的 `mtop` 接口、来源包和风险分组。

配套页面接口对照：`goofish-page-api-crosswalk.md`，用于按页面判断背后接口家族、读取能力和写入/高风险能力。

配套任务流手册：`goofish-task-workflow-runbook.md`，用于把搜索、详情、下单前确认、发布、卖家订单、售后、财务、权限等任务拆成页面路径和停止点。

配套控件清单：`goofish-ui-control-inventory.md`，用于按页面查看 tab、筛选、输入框、表格、分页、上传、下载、二维码、弹窗和按钮控件。

配套站点层级：`goofish-site-taxonomy.md`，用于按主站、卖家工作台、页面家族、父子关系和参数深度查看全站结构。

配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`，用于按页面横向查看证据、层级、锚点、可读内容、任务入口、风险和停止点。

配套路由索引：`goofish-route-inventory.md`，用于按 URL/hash 快速判断页面、证据层级和动作边界。

配套动作门禁：`goofish-action-gate-matrix.md`，用于按页面、按钮和接口动作词判断能否直接执行、是否只读或是否必须确认。

配套字段清单：`goofish-page-field-inventory.md`，用于按页面判断哪些字段可记录、哪些只能脱敏、哪些禁止写入日志。

配套证据覆盖：`goofish-evidence-coverage.md`，用于区分 Live + Static、Static Only、Deep/Param、Shell/Container 和 Boundary Only 页面。

配套导航定位：`goofish-navigation-selector-guide.md`，用于判断页面流转、加载完成信号、稳定锚点和失败状态。

配套状态清单：`goofish-page-state-modal-inventory.md`，用于判断加载、空态、错误、登录、权限、二维码、确认弹窗和高风险业务状态。

## 总体结构

闲鱼网页版分成两套主要界面：

1. `www.goofish.com`：买家/普通网页版主体，包括首页、搜索、频道、商品详情、个人页、订单、收藏、发布、消息、反馈。
2. `seller.goofish.com`：鱼小铺卖家 PC 工作台，包括数据、商品、小铺、交易、财务等后台模块。

当前登录态可以访问 `www.goofish.com` 主体，也能进入 `seller.goofish.com` 的数据总览页。

## 公共页框架

大多数 `www.goofish.com` 页面都有相同外壳：

- 顶部：闲鱼 Logo、搜索框、热搜词、账号入口、订单入口。
- 中部：页面主体内容。
- 右侧固定工具条：`发闲置`、`消息`、`APP`、`反馈`、`客服`、`回顶部`。
- 商品详情页右侧工具条会多一个：`商品码`。
- 底部：阿里系站点链接、备案、隐私政策、用户协议、闲鱼规则、意见征集、算法备案等。

## 登录

入口：

- 首页右上角 `登录`
- `/login`

方式：

- 短信登录
- 密码登录
- 闲鱼 App 扫码登录

注意：

- 当前测试扫码登录成功后，页面顶部从 `登录` 变为头像/账号入口。
- 多账号不要混用同一个浏览器资料。推荐一个账号对应一个独立 Profile。
- 验证码、扫码、风控确认必须由用户本人完成。

## 首页 `/`

标题：`闲鱼 - 闲不住？上闲鱼！`

核心区域：

- 顶部搜索框，placeholder 会动态变化。
- 热搜词入口，点击进入 `/search?q=关键词`。
- 左侧大类入口：手机/数码/电脑、服饰/箱包/运动、技能/卡券/潮玩、母婴/美妆/个护、家具/家电/家装、文玩/珠宝/礼品、食品/宠物/花卉、图书/游戏/音像、汽车/电动车/租房、五金/设备/农牧。
- 中部频道卡片：如衣橱捡漏、二次元、手机数码、省钱卡券。
- 推荐瀑布流：商品卡片，点击进入 `/item?id=...&categoryId=...`。

自动化锚点：

- 搜索框：`input[type=text]`
- 搜索按钮：文本 `搜索`
- 商品卡片链接：`/item?id=...`
- 频道页链接：`/mach-feeds?machId=...`

## 搜索页 `/search?q=...`

标题格式：`关键词_闲鱼`

核心区域：

- 搜索框保留当前关键词。
- 排序/筛选：`综合`、`新降价`、`新发布`、`价格`、`区域`。
- 价格区间有两个 `¥` 输入框和 `确定`。
- 快速筛选标签：`个人闲置`、`验货宝`、`验号担保`、`包邮`、`超赞鱼小铺`、`全新`、`严选`、`转卖`。
- 商品瀑布流需要等待和滚动后加载。

商品卡片信息：

- 商品图
- 标题/描述摘要
- 价格
- 想要人数
- 地区
- 卖家信用/回复速度

注意：

- 排序和筛选点击后不一定改变 URL，很多状态在前端内部维护。
- 商品加载是异步的，刚进入可能显示 `加载中...`。

## 频道页 `/mach-feeds?machId=...`

用途：

- 首页频道卡片的独立瀑布流页面。
- 例如手机数码、衣橱捡漏、二次元、省钱卡券。

结构：

- 顶部搜索和热搜词与首页一致。
- 主体是频道商品瀑布流。
- 商品卡片仍进入 `/item?id=...&categoryId=...`。

## 商品详情页 `/item?id=...&categoryId=...`

标题格式：`商品标题_闲鱼`

核心区域：

- 顶部卖家卡：头像、昵称、地区、来闲鱼时间、卖出件数、好评率、信用标签。
- 左侧图片列表/大图。
- 右侧商品信息：
  - 价格
  - 想要人数、浏览数
  - 保障标签，如描述不符包邮退、7 天无理由等，视商品而定
  - 标题和描述
  - 属性，如品牌、成色
- 主操作：
  - `聊一聊` -> `/im?itemId=...&peerUserId=...`
  - `立即购买` -> `/create-order?itemId=...`
  - `收藏`
- 下方：为你推荐商品列表。
- 右侧工具：`商品码`。

安全边界：

- `聊一聊` 会进入会话，不应自动发送消息。
- `立即购买` 只可进入确认页；提交订单/支付必须用户确认。
- `收藏` 会改变账号状态，执行前需要用户确认。

## 商品码

入口：

- 商品详情页右侧工具条 `商品码`

行为：

- 打开扫码查看弹层。
- 文案包含 `APP扫码查看`。

用途：

- 商品分享/手机端查看。

## APP 弹层

入口：

- 右侧工具条 `APP`

行为：

- 打开 `扫码下载APP` 弹层。

## 个人页 `/personal`

标题格式：`账号/店铺名_闲鱼`

结构：

- 左侧工作台菜单：
  - 我的闲鱼
  - 我的交易
  - 我发布的
  - 我卖出的
  - 我买到的
  - 我的收藏
  - 账户设置
  - 个人资料
  - 账号与安全
- 顶部个人/店铺资料卡：
  - 头像
  - 昵称
  - 地区
  - 粉丝数/关注数
  - 简介
  - `编辑资料`
- 主体标签：
  - `宝贝`
  - `信用及评价`
  - `宝贝管理`
- 宝贝筛选：
  - `综合`
  - 自定义分类
  - `在售`
  - `已售出`
  - `筛选`

注意：

- `/personal?userId=...` 是他人卖家页/闲鱼号页。
- 当前账号自己的 `/personal` 兼具公开主页和管理入口。
- `编辑资料`、`宝贝管理` 都可能改变资料或商品状态，执行前需要确认。

## 收藏页 `/collection`

标题：`我的收藏_闲鱼`

结构：

- 复用个人工作台左侧菜单。
- 主体为收藏商品卡片。
- 每张卡片可进入商品详情，也有 `我想要` 入口进入 IM。

安全边界：

- 点击 `我想要` 会进入联系卖家流程，不应自动发送消息。
- 取消收藏属于账号状态变更，需要确认。

## 买到的订单页 `/bought`

标题：`我买到的_闲鱼`

结构：

- 复用个人工作台左侧菜单。
- 订单筛选状态：
  - `全部`
  - `待付款`
  - `待发货`
  - `待收货`
  - `待评价`
  - 退款/售后相关状态
- 订单卡常见按钮：
  - `更多`
  - `联系卖家`
  - `再次购买`
  - `确认收货`
  - `物流记录`
  - `去评价`
  - `查看钱款`

安全边界：

- `确认收货`、`去评价`、`再次购买`、退款/售后相关操作都必须用户确认。
- 订单页包含商品名、卖家、状态等隐私内容，不应写入日志或总结。

## 订单详情页 `/order-detail?orderId=...`

标题：`订单详情_闲鱼`

字段/模块：

- 订单详情
- 订单编号
- 收货地址
- 物流/快递
- 卖家/买家
- 退款/售后

常见按钮：

- `查看详情`
- `确认收货`
- `再次购买`
- `我要退款`
- `物流记录`
- `延长收货`
- `联系卖家`
- `查看`

安全边界：

- 此页包含收货地址和物流信息，是高敏页面。
- 任何确认收货、退款、延长收货、评价、支付动作都需要用户明确确认。

## 创建订单页 `/create-order?itemId=...`

标题：`创建订单_闲鱼`

字段/模块：

- 收货地址
- 快递/运费
- 支付方式，如支付宝
- 商品信息
- 订单确认信息

安全边界：

- 这里会读取收货地址、支付方式等敏感信息。
- 可以只读或辅助检查。
- 提交订单、立即支付、改地址、选支付方式都必须用户确认。

## 发布页 `/publish`

标题：`发闲置_闲鱼`

结构：

- 基础信息：
  - 宝贝图片，文件上传
  - 宝贝描述，最多 1500 字
  - 属性规格，上传主图/填写内容后会智能识别属性
  - 商品规格，支持添加规格类型，最多 2 类
- 价格：
  - 价格
  - 原价
  - 鱼小铺软件服务费提示：成交额含运费的一定比例
- 发货设置：
  - 包邮
  - 按距离计费
  - 一口价
  - 无需邮寄
  - 支持自提
  - 宝贝所在地
- 底部固定按钮：`发布`

安全边界：

- 上传图片、填写内容可以辅助。
- 真正点击 `发布` 前必须用户确认。

## 消息页 `/im`

标题：`聊天_闲鱼`

结构：

- 入口可来自右侧工具条 `消息`，也可来自商品详情 `聊一聊`。
- `/im` 未选中具体会话时能看到消息模块框架。
- `/im?itemId=...&peerUserId=...` 是商品关联会话入口。

注意：

- 消息页包含联系人和聊天记录。
- 不应自动读取/总结私聊内容，除非用户明确要求。
- 发送消息是外部副作用，必须确认具体内容和对象。

## 账号与安全 `/account`

标题：`账号与安全_闲鱼`

结构：

- 复用个人工作台左侧菜单。
- 账号安全相关入口包含：
  - 实名认证
  - 支付宝
  - 安全中心

安全边界：

- 这里属于高敏账号设置区。
- 不自动改手机号、实名、支付绑定、安全设置。

## 反馈页 `/feedback?from=...`

标题：`我要反馈_闲鱼`

结构：

- 闲鱼用户反馈中心。
- 反馈类型：
  - 我要提功能/体验建议
  - 我要反馈故障
- 问题页面选项：
  - 首页
  - 搜索
  - 商品详情
  - 交易
  - 闲鱼号
  - 其它
- 反馈文本框：最多 500 字。
- 截图上传：最多 5 张，支持 JPG、JPEG、PNG、APNG、GIF、BMP。
- 按钮：`提交`

安全边界：

- 提交反馈会向闲鱼发送内容，必须用户确认。

## 更新日志 `/changelog`

标题：`更新日志_闲鱼`

内容：

- PC 工作台上线公告。
- 网页版发闲置能力更新。
- 网页版 IM 功能更新。

关键外链：

- `https://seller.goofish.com/`：鱼小铺 PC 工作台
- `/publish`：网页版发闲置

## 客服

入口：

- 右侧工具条 `客服`

链接：

- `https://alimebot.goofish.com/intl/index.htm?from=wkbRssQuvW`

注意：

- 这是外部客服机器人/阿里客服页面。
- 提问会对外发送内容，需要确认。

## 卖家 PC 工作台 `seller.goofish.com`

当前可访问入口：

- `https://seller.goofish.com/?site=COMMONPRO#/seller-data/data`

标题：

- `数据总览 - 闲鱼卖家工作台`

顶部：

- 通知
- 消息
- 下载
- 当前店铺/账号入口

左侧模块：

- 数据：
  - 数据总览
  - 商品数据
  - 粉丝数据
  - 客服数据
- 小铺：
  - 子账号管理
  - 客服分流
  - 安全中心
- 商品：
  - 商品发布
  - 商品管理
  - 运费模版
- 交易：
  - 订单管理
  - 退款管理
  - 评价管理
  - 投诉管理
  - 退货地址
- 财务：
  - 收入账单
  - 支出账单
  - 申请发票
  - 开票信息

数据总览模块：

- 时间筛选：近 1 天、近 7 天、近 30 天，以及开始日期/结束日期。
- 商品数据、交易数据、复购情况、客服数据等指标卡。

注意：

- 工作台内子模块切换不是普通链接，菜单由登录后的后台配置下发。
- 非当前分组的子菜单虽然存在于 DOM，但父容器高度可能是 0，直接按文字点击容易不生效。
- 稳定做法是先展开父分组，再点子菜单；也可以直接打开已确认 hash 路由。
- 商品管理、订单管理、退款、发货、财务、子账号、安全中心都属于高敏后台操作区。

## 自动化安全分级

低风险，可直接做：

- 打开首页、搜索页、频道页、商品详情页。
- 搜索关键词。
- 读取商品公开信息。
- 比较价格、地区、想要人数、卖家信用、保障标签。
- 打开 APP/商品码弹层。

中风险，需要先说明但通常可辅助：

- 进入订单列表/订单详情只读查看。
- 进入创建订单页只读查看。
- 进入消息页只看会话框架。
- 填写发布页草稿但不发布。
- 填写反馈草稿但不提交。

高风险，必须用户明确确认：

- 发送消息。
- 收藏/取消收藏。
- 立即购买、提交订单、支付。
- 确认收货。
- 退款/售后。
- 去评价。
- 修改账号资料、安全设置、实名、支付宝绑定。
- 发布闲置。
- 商品上架/下架/删除/编辑。
- 卖家后台的订单、退款、发货、财务、子账号和安全操作。

## 已知技术点

- 登录态来自扫码后浏览器 Profile 保存的 cookie/session。
- `www.goofish.com` 和 `seller.goofish.com` 都能识别当前登录态。
- 搜索和频道瀑布流是异步加载，自动化需要等待和滚动。
- 搜索筛选状态不一定反映在 URL 中。
- 许多入口是 `target="_blank"` 或内部前端路由，自动化时要留意新标签页。
- 页面 DOM 会包含大量页脚 SEO 链接，定位时应优先用可见区域、稳定 href、按钮文本和页面上下文，不要盲目抓全页面文本。

## 下一轮建议

1. 深挖卖家工作台子模块的真实路由和可操作表格，但必须避免导出/修改/发货/退款。
2. 单独测试搜索筛选：价格、地区、包邮、全新、严选、转卖等状态是否可从 DOM 或请求参数稳定读取。
3. 建一份“任务到页面路径”的操作手册，例如：找货、比价、收藏、联系卖家、发闲置、查订单、查物流、卖家处理订单。
4. 如需多账号，建立账号名到独立浏览器 Profile 的映射，避免 cookie 混用。

## 第二轮补充：卖家工作台模块

卖家工作台菜单不是普通链接，而是 React/SPA 侧边栏。稳定点击方式：

1. 先点左侧大组标题，如 `商品`、`交易`、`财务`、`数据`、`小铺`、`推广`。
2. 等子菜单容器高度展开后，再点子菜单项。
3. 非当前分组的子菜单虽然在 DOM 中存在，但父容器高度为 0，直接点子项通常不会生效。

已确认的工作台路由：

| 模块 | 路由 | 结构 |
| --- | --- | --- |
| 数据总览 | `#/seller-data/data` | 近 1 天/近 7 天/近 30 天，日期区间，商品/交易/复购/客服等指标卡 |
| 商品数据 | `#/seller-data/commodity` | 商品名称搜索、日期筛选、商品曝光/浏览/询单/支付/退款数据表 |
| 粉丝数据 | `#/seller-data/fanData` | 日期筛选、粉丝数据、粉丝洞察、性别分布、属性分布、地域分布、人群分布 |
| 客服数据 | `#/seller-data/customerService` | 日期筛选、客服账号维度数据、满意度/响应率/评价相关表格，可导出 |
| 商品发布 | `#/seller-item/publish` | 图片/视频、描述、规格、价格、库存、包邮/运费、所在地，最终发布按钮 |
| 商品管理 | `#/seller-item/goods-manage` | 商品筛选、商品表格、复制/编辑/改价/粉丝价/下架/批量下架 |
| 运费模版 | `#/seller-item/post-temple` | 模版名称/ID筛选、发货地、计费方式、最后编辑时间、新建模版 |
| 订单管理 | `#/seller-trade/order-manage` | 订单编号/物流单号/商品 ID/买家昵称搜索，订单状态/退款状态筛选，发货/联系/详情/钱款/备注/提醒收货/修改物流 |
| 退款管理 | `#/seller-trade/refund-manage` | 退款类型筛选、退款状态/原因/客服介入/物流信息、查看详情/钱款、确认/拒绝收货 |
| 评价管理 | `#/seller-trade/evaluation-manage` | 商品 ID、订单编号、买家昵称、日期筛选，评价等级/内容/商品信息/操作表 |
| 投诉管理 | `#/seller-trade/complaint-manage` | 完整订单编号搜索、投诉状态、投诉订单、纠纷金额、投诉详情/违规详情 |
| 退货地址 | `#/seller-trade/refund-address` | 默认退货地址、具体退货地址、编辑/删除/新增退货地址 |
| 收入账单 | `#/seller-finance/income-bill` | 月汇总/日汇总/收入明细，业务大类、收入金额合计、退款金额合计，导出 Excel |
| 支出账单 | `#/seller-finance/expense-bill` | 月汇总/日汇总/支出明细，业务大类、实收服务费、服务费返还、本月付款 |
| 申请发票 | `#/seller-finance/invoice-apply` | 待申请/已申请、业务类型、可开票金额、旧版申请入口、导出 Excel |
| 开票信息 | `#/seller-finance/basic-info` | 发票抬头、统一社会信用代码、纳税类型、公司/银行/地址/电话信息 |
| 子账号管理 | `#/seller-account/sub-account` | 账号、手机号、子账号姓名、岗位、账号状态、分流配置，新建子账号 |
| 客服分流 | `#/im-cs-dispatch/customer-routing-service` | 规则配置、分组名称、接待范围、参与客服、新建分组 |
| 安全中心 | `#/seller-sc/home` | 违规名称、违规编号、违规原因、违规影响、扣分、处罚状态、申诉状态 |
| 超级擦亮 | `#/seller-ad/home` | 擦亮计划首页，含时间筛选、轮播切换、新建擦亮计划 |

本轮纠正：

- `运费模版` 的真实路由是 `#/seller-item/post-temple`，不是常见英文 `freight-template`。
- `开票信息` 的真实路由是 `#/seller-finance/basic-info`，不是 `invoice-info`。
- `客服分流` 的真实路由是 `#/im-cs-dispatch/customer-routing-service`，不在 `seller-account` 下面。
- `安全中心` 对应 `#/seller-sc/home`，页面标题显示为安全中心。

工作台高风险按钮清单：

- 商品：`复制`、`编辑`、`改价`、`设置粉丝价`、`下架`、`批量下架`、`+ 商品发布`
- 订单：`批量导入发货`、`联系ta`、`查看钱款`、`添加备注`、`提醒收货`、`修改物流`、`去评价`、`批量延长收货`
- 退货地址：`新增退货地址`、`编辑`、`删除`
- 财务：`导出Excel`、`历史下载记录`、`下载全量明细`、`申请发票`
- 子账号/安全：`新建子账号`、违规详情/申诉相关操作
- 推广：`新建擦亮计划`

这些按钮都会改变经营状态、导出数据或触达客户/订单，执行前必须明确确认。

## 第五轮补充：卖家后台路由二次校准

这一轮验证方式：

- 先从工作台脚本确认菜单接口：`mtop.alibaba.idle.seller.platform.sys.menu.query`。
- 再用已登录浏览器直接打开候选 hash。
- 对菜单点击不稳定的项，先展开父级菜单，再点击子项。
- 只记录字段、表头、按钮名和路由，不记录订单号、买家昵称、商品名、地址、金额和经营数字。

### 数据模块

`#/seller-data/data` 数据总览：

- 日期：开始日期、结束日期、近 1 天、近 7 天、近 30 天。
- 区块：商品数据、交易数据、复购情况、浏览分布、售后数据。
- 分布：来源分布、商品分布、时间分布、地域分布。

`#/seller-data/commodity` 商品数据：

- 搜索：商品名称。
- 表头：商品信息、商品曝光次数、商品曝光人数、商品浏览次数、商品浏览人数、询单人数、支付人数、支付订单数、支付金额、浏览支付转化率、发起退款人数、发起退款订单数、发起退款金额、成功退款人数、成功退款订单数、成功退款金额。
- 按钮：搜索、重置、下载。

`#/seller-data/fanData` 粉丝数据：

- 日期：开始日期、结束日期、请选择日期。
- 区块：粉丝数据、粉丝洞察、性别分布、属性分布、地域分布、人群分布。

`#/seller-data/customerService` 客服数据：

- Tab/区块：核心监控、实时咨询。
- 表头：账号名称、咨询人数、接待人数、咨询商品数、平均响应时长、3 分钟响应率、客户服务满意度、客户服务满意率、有效评价数、有效好评数、有效差评数、客户名称、客户 nick、被评价的客服、评价时间、评分、不满意原因。
- 按钮：导出数据。

### 商品模块

`#/seller-item/publish` 商品发布：

- 区块：发闲置、基础信息、商品规格、价格、服务、发货设置。
- 字段：宝贝图片、宝贝视频、宝贝描述、价格、原价、库存、包邮、按距离计费、一口价、运费模版、无需邮寄、邮费、宝贝所在地。
- 按钮：添加规格类型、刷新、新建模版、发布。
- 空草稿状态：
  - `发布` 按钮保持禁用。
  - `添加规格类型（0/2）` 入口存在，但未填图片/描述/类目识别信息时，本轮点击没有打开规格弹层。
  - `宝贝所在地` 会预填当前/常用地点；只记录字段，不记录具体地点。
- 发货方式：
  - 默认选中 `包邮`。
  - 切到 `运费模版` 后出现 `请选择运费模版`、`刷新`、`新建模版`。
  - 发布页里的 `新建模版` 在空草稿下没有跳出可见表单；稳定查看和创建运费模版应走 `#/seller-item/post-temple`。
- 安全规则：可以打开和填草稿，但 `发布` 前必须确认。

`#/seller-item/goods-manage` 商品管理：

- 筛选：商品 ID、价格区间、日期区间、在卖/下架状态。
- 表头：商品信息、价格、库存、累计销量、创建时间、操作。
- 按钮：商品发布、重置、确认筛选、批量下架。
- 安全规则：复制、编辑、改价、粉丝价、下架、批量下架都必须确认。

`#/seller-item/post-temple` 运费模版：

- 筛选：模版名称、模版 ID。
- 表头：模版名称、发货地、计费方式、最后编辑时间、操作。
- 按钮：重置、确认筛选、创建模版、确定。
- 空列表状态：显示 `暂无模版`。
- 创建入口：`#/seller-item/post-temple/create`。
- 创建模版字段：
  - 模版名称，计数 `0 / 30`。
  - 发货地址，选择 `省份/地区`。
  - 计费方式，本轮实测默认只有 `按件数` 选中。
  - `设置为默认模版`。
  - 默认运费：数量、价格、每增加数量、增加运费价格。
  - `+ 设置指定区域运费` 会先打开 `选择区域` 弹窗。
- `选择区域` 弹窗：
  - 标题：选择区域。
  - 结构：地区分组，示例分组有东北、华北、华南、华东等。
  - 按钮：确认、取消、关闭。
- 安全规则：新建、编辑、删除模版会影响发货设置，必须确认。

### 交易模块

`#/seller-trade/order-manage` 订单管理：

- 状态：全部、待付款、待发货、发货即将超时、发货已超时、已发货、售后中、交易成功、交易关闭。
- 表头：商品信息、发货/退款状态、单价/数量、成交价、操作。
- 按钮：查询、重置、确认筛选、批量导入发货、批量延长收货。

`#/seller-trade/refund-manage` 退款管理：

- 状态：全部订单、未发货退款、已发货退款、退货退款、退运费。
- 筛选：金额区间、日期区间。
- 表头：商品信息、件数、金额、退款状态、原因、客服介入、物流信息、操作。
- 高风险按钮：查看详情、查看钱款、确认收货、拒绝收货、管理地址模版。

`#/seller-trade/evaluation-manage` 评价管理：

- 筛选：日期区间。
- 表头：评价等级、评价内容、商品信息、操作。
- 按钮：联系 ta、评价、举报、批量评价。
- 安全规则：评价、举报、联系客户都必须确认。

`#/seller-trade/complaint-manage` 投诉管理：

- 搜索：完整订单编号。
- 状态：全部、待客服处理、投诉撤销、投诉成立、投诉不成立。
- 表头：投诉信息、投诉状态、投诉订单、纠纷金额、操作。
- 按钮：查询、联系 ta、投诉详情、违规详情。

`#/seller-trade/refund-address` 退货地址：

- 表头：设为默认退货地址、具体退货地址、操作。
- 按钮：新增退货地址、编辑、删除。
- 安全规则：地址新增、编辑、删除必须确认。

### 第七轮补充：商品/交易高频页控件校准

这一轮只读表单结构、按钮和表头；真实商品、订单、买家、地址和状态数量不写入文档。

`#/seller-item/goods-manage` 商品管理：

- 状态：在卖、下架。
- 搜索/筛选：
  - 商品 ID，支持多个 ID 以逗号分隔。
  - 价格最小值、最大值。
  - 日期开始、结束。
  - 商品类目、品牌、成色、服务保障、创建时间。
- 表头：商品信息、价格、库存、累计销量、创建时间、操作。
- 按钮：`+ 商品发布`、重置、确认筛选、批量下架。
- 空态：暂无商品。
- 自动化建议：可以做只读筛选和读取表头；复制、编辑、改价、粉丝价、下架、批量下架前必须确认。

`#/seller-trade/order-manage` 订单管理：

- 状态：全部、待付款、待发货、发货即将超时、发货已超时、已发货、售后中、交易成功、交易关闭。
- 搜索：完整订单编号、物流单号、商品 ID、买家昵称共用一个搜索框。
- 筛选：订单状态、催发货订单、下单时间、品类、品牌、型号。
- 表头：商品信息、发货/退款状态、单价/数量、成交价、买家/收货信息、操作。
- 按钮：查询、重置、确认筛选、批量导入发货、批量延长收货。
- 自动化建议：订单页可以做只读搜索/筛选；导入发货、延长收货、改物流、联系买家、查看钱款、备注等必须确认。

`#/seller-trade/refund-manage` 退款管理：

- 状态：全部订单、未发货退款、已发货退款、退货退款、退运费。
- 筛选：退款状态、退款类型、退款原因、客服介入、申请时间、退款物流状态、金额最小值/最大值。
- 表头：商品信息、件数、金额、退款状态、原因、客服介入、物流信息、操作。
- 按钮：重置、确认筛选、管理地址模版。
- 自动化建议：退款页可以汇总状态和字段；确认收货、拒绝收货、管理地址模版等必须确认。

`#/seller-trade/evaluation-manage` 评价管理：

- 状态：全部、待卖家评价。
- 筛选：订单评价、订单编号、商品名称、商品 ID、买家昵称、交易成功时间、评价等级、买家评价时间。
- 表头：评价等级、评价内容、商品信息、操作。
- 按钮：重置、确认筛选、批量评价。
- 自动化建议：可以读取评价字段和筛选结果结构；评价、批量评价、举报、联系买家前必须确认。

`#/seller-trade/complaint-manage` 投诉管理：

- 状态：全部、待卖家处理、待客服处理、待买家处理、投诉撤销、投诉成立、投诉不成立。
- 搜索：完整订单编号。
- 表头：投诉信息、投诉状态、投诉订单、纠纷金额、买家信息、操作。
- 按钮：查询、联系 ta、投诉详情、违规详情。
- 自动化建议：投诉页属于高敏经营区；只读查看可以做，联系、申诉、提交材料或处理投诉前必须确认。

### 财务模块

`#/seller-finance/income-bill` 收入账单：

- Tab：月汇总、日汇总、收入明细。
- 表头：月份、业务大类、收入金额合计、退款金额合计、操作。
- 按钮：重置、查询、导出 Excel、历史下载记录、下载全量明细。

`#/seller-finance/expense-bill` 支出账单：

- Tab：月汇总、日汇总、支出明细。
- 表头：月份、业务大类、实收服务费合计、服务费返还合计、本月付款、操作。
- 按钮：重置、查询、导出 Excel、历史下载记录。

`#/seller-finance/invoice-apply` 申请发票：

- Tab：待申请发票、已申请发票、旧版申请发票。
- 表头：业务类型、可开票金额。
- 按钮：重置、查询、导出 Excel、历史下载记录、申请发票。

`#/seller-finance/basic-info` 开票信息：

- 字段：发票抬头、统一社会信用代码、纳税类型、公司名称、开户银行、开户银行账号、营业地址、营业电话。
- 安全规则：这是发票主体资料，只读可看，新增或修改必须确认。

### 小铺 / 账号 / 推广模块

`#/seller-account/sub-account` 子账号管理：

- 表头：账号、子账号姓名、岗位、账号状态、分流配置、操作。
- 按钮：新建子账号。
- 安全规则：新建、停用、改权限、改分流配置必须确认。

`#/im-cs-dispatch/customer-routing-service` 客服分流：

- 区块：规则配置。
- 表头：分组名称、接待范围、参与客服、操作。
- 按钮：新建分组。
- 安全规则：客服分流规则会影响实际接待，任何保存/启停都必须确认。

`#/seller-sc/home` 安全中心：

- 表头：违规名称、违规编号、违规原因、违规影响、闲气值扣分、违规时间、处罚状态、是否申诉、操作。
- 按钮：闲气值明细、查看详情。
- 安全规则：申诉、处理违规、跳转详情前需要说明上下文。

`#/seller-ad/home` 超级擦亮：

- 日期：今日、昨日、近 7 日、近 30 日、近 90 日。
- 指标：单次点击成本、单次询单成本、单次下单成本、单次咨询成本、擦亮花费、曝光数、点击数、询单量、下单笔数、交易额、投产比。
- 按钮：新建擦亮计划。
- 安全规则：推广投放和新建计划属于付费/经营动作，必须确认。

### 第八轮补充：数据/财务/账号安全页骨架校准

这一轮只读页面骨架，不写任何指标数字、金额、账号、手机号、公司信息或违规详情。

数据页：

- `#/seller-data/data`：页面标题为数据总览；稳定日期控件是开始日期、结束日期。
- `#/seller-data/commodity`：页面标题为商品数据；搜索框 placeholder 是请输入商品名称；按钮有搜索、重置、下载；表头覆盖曝光、浏览、询单、支付、退款等商品维度指标。
- `#/seller-data/fanData`：页面标题仍显示商品数据；日期控件包含开始日期、结束日期、请选择日期。
- `#/seller-data/customerService`：页面标题仍显示商品数据；按钮为导出数据；表头覆盖客服账号、咨询、接待、响应、满意度、客户评价等字段。

财务页：

- `#/seller-finance/income-bill`：页面标题为收入账单；tab 为月汇总、日汇总、收入明细；按钮为重置、查询、导出 Excel、历史下载记录。
- `#/seller-finance/expense-bill`：页面标题为支出账单；tab 为月汇总、日汇总、支出明细；按钮为重置、查询、导出 Excel、历史下载记录。
- `#/seller-finance/invoice-apply`：页面标题为申请发票；tab 为待申请发票、已申请发票、旧版申请发票；按钮包括导出 Excel、历史下载记录、申请发票。
- `#/seller-finance/basic-info`：真实标题显示为基本信息；这里是发票/主体资料区，只读字段名可以记录，具体主体信息不写入文档。

账号/规则/安全/推广页：

- `#/seller-account/sub-account`：页面标题为子账号管理；表头为账号、手机号、子账号姓名、岗位、账号状态、分流配置、操作；按钮为新建子账号。
- `#/im-cs-dispatch/customer-routing-service`：页面标题为客服分流服务；表头为分组名称、接待范围、参与客服、操作；按钮为规则配置、新建分组。
- `#/seller-sc/home`：页面标题为安全中心；表头为违规名称、违规编号、违规原因、违规影响、闲气值扣分、违规时间、处罚状态、是否申诉、操作；按钮为闲气值明细。
- `#/seller-ad/home`：页面标题为首页 - 超级擦亮；日期控件为开始日期、结束日期；按钮为新建擦亮计划，轮播控件表现为 prev/next。

安全规则：

- 数据下载、财务导出、申请发票、子账号新增、客服分流规则保存、安全中心申诉/处理、推广计划新建都需要确认。
- 这些页面可以先做只读巡检和字段映射，不能直接点击会导出、保存、启停、申诉、投放或修改权限的动作。

### 工作台外壳辅助路由

这些路由来自 `seller-workbench` 外壳包，不属于左侧经营菜单：

| 路由 | 类型 | 说明 | 自动化建议 |
| --- | --- | --- | --- |
| `#/notification-center` | 页面 | 通知中心 | 可只读查看通知列表；标记已读前确认 |
| `#/im` | 页面 | 工作台消息入口 | 可打开；发送消息前确认 |
| `#/im-desktop` | 页面 | 桌面版 IM 容器 | 可打开；下载/安装/发消息前确认 |
| `#/select-site` | 页面 | 站点/身份选择 | 只读；切换站点前确认 |
| `#/account-check` | 页面 | 账号检查/跳转前校验 | 涉及账号身份，不主动操作 |
| `#/login` | 页面 | 工作台登录页 | 扫码/验证码由用户完成 |
| `#/no-permission` | 页面 | 无权限页 | 只作为路由失败/无权限判断 |
| `#/iframe?url=...` | 容器 | 外部页面 iframe 承载 | 只在来源明确时使用 |
| `#/playground` | 调试 | 内部实验页 | 不主动访问 |
| `#/notification-center/api` | 内部 API 模块 | 通知中心接口封装 | 不是业务页面 |
| `#/notification-center/api/clean_unread_notifications` | 内部 API 模块 | 清理未读通知 | 不主动调用 |
| `#/notification-center/api/read_notify_status_sync` | 内部 API 模块 | 同步通知已读状态 | 不主动调用 |
| `#/notification-center/interface` | 内部接口定义 | 通知中心类型/接口 | 不是业务页面 |

下载弹层：

- 顶部 `下载` 是工作台外壳功能，不是左侧菜单路由。
- COMMONPRO 站点脚本里包含 Windows 和 Mac 版闲鱼卖家 IM 客户端下载入口。
- 实测弹层提供两个安装包：
  - Windows：`https://mtl.cn-hangzhou.oss.aliyun-inc.com/xianyu/seller/commonpro/xianyu-seller-im-1.0.4-win.exe`
  - Mac：`https://mtl.cn-hangzhou.oss.aliyun-inc.com/xianyu/seller/commonpro/xianyu-seller-im-1.0.4-mac.dmg`
- 下载、安装或打开本机客户端前必须确认。

工作台外壳实测补充：

- `#/notification-center`：通知中心会展示通知卡片/详情。通知标题可能涉及违规、交易或账号状态，记录时只写字段结构，不写具体通知内容；清理未读、标记已读前必须确认。
- `#/im`：工作台消息页，页面标题为聊天，支持按用户昵称查找；真正发消息前必须确认。
- `#/im-desktop`：桌面版消息容器，页面标题为消息，仍按 IM 风险处理。
- `#/select-site`：站点选择页，核心文案是选择要访问的站点；切换站点前确认。
- `#/account-check`：账号验证/检查页，包含 `登录其他账号`、`继续前往`；这是账号身份门禁，不自动点击。
- `#/no-permission`：无权限页，文案为当前账号没有访问权限；可用来判断路由无权限。

## 第二轮补充：搜索筛选细节

搜索页路径：

- `/search?q=关键词`

稳定控件：

- 搜索框：页面第一个文本输入框，值为当前关键词。
- 价格区间：两个 placeholder 为 `¥` 的输入框。
- 页码跳转：结果区右侧页码输入框。
- 顶部排序：`综合`、`新降价`、`新发布`。
- 价格提交：价格区间旁边的 `确定`。
- 区域/距离：
  - 页面脚本包含地区筛选面板结构，关键结构名包括 `locationWrap`、`addressList`、`distanceList`、`provItem`、`gpsWrap`。
  - 脚本中的 tab 为 `选地区`、`搜附近`、`常用地址`。
  - 距离选项包括 `1km`、`5km`、`10km`、`15km`、`50km`，对应半径 1000、5000、10000、15000、50000。
  - 实测 PC 搜索页顶部的 `区域` 文案和小分页 `1/50` 很近，误点会翻结果页；不要把 `1/50` 当作地区筛选值。
  - 当前登录态下，本轮没有稳定展开完整地区面板；地区筛选自动化需先确认可见弹层再继续。
- 标签筛选：`个人闲置`、`验货宝`、`验号担保`、`包邮`、`超赞鱼小铺`、`全新`、`严选`、`转卖`。

搜索页自动化建议：

- 进入搜索页后等待 2-5 秒，再滚动一次，瀑布流才稳定出现商品卡。
- 不要只靠 URL 判断排序/筛选状态；点击 `新降价`、`新发布`、标签筛选时，URL 可能不变。
- 商品卡片链接仍然是 `/item?id=...&categoryId=...`。
- 公开商品信息可以读取：标题、价格、想要人数、地区、卖家信用/回复速度、保障标签。
- 不要把搜索页整页文本当商品结构；底部 SEO 链接和页脚会污染结果。应以商品卡链接和卡片容器为锚点。

## 第三轮补充：个人工作台入口

个人工作台左侧菜单并不全是独立 URL：

| 入口 | 路由/行为 | 说明 |
| --- | --- | --- |
| 我的闲鱼 | `/personal` | 当前账号主页/店铺页 |
| 我发布的 | `/personal` 页内状态 | 仍停留个人主页，主体展示已发布宝贝列表和筛选 |
| 我卖出的 | `/personal` 页内状态 | 仍停留个人主页，和已发布/已售出标签联动 |
| 我买到的 | `/bought` | 买家订单列表 |
| 我的收藏 | `/collection` | 收藏商品列表 |
| 个人资料 | `/personal` 页内入口 | 资料编辑入口在个人资料卡上的 `编辑资料`，不是稳定独立路由 |
| 账号与安全 | `/account` | 账号安全页，含认证和安全中心 |

`/personal` 内部可用标签：

- `宝贝`
- `信用及评价`
- `宝贝管理`
- `综合`
- 自定义分组
- `在售`
- `已售出`
- `筛选`

个人工作台风险：

- `编辑资料` 会修改公开资料。
- `宝贝管理`、`在售`、`已售出` 可能涉及商品编辑、上下架、删除。
- `/account` 中的认证、登录、安全中心属于账号安全区。

## 第九轮补充：主站个人/交易页二次校准

这一轮只记录页面控件和动作类型；真实收藏商品、真实订单、店铺名、账号名、地址和金额不写入文档。

### `/personal` 个人主页

结构：

- 左侧账号导航：我的闲鱼、我发布的、我卖出的、我买到的、我的收藏、个人资料、账号与安全。
- 主页区块：头像/昵称资料卡、编辑资料、宝贝、信用及评价、宝贝管理。
- 商品区 tab/筛选：综合、自定义分组、在售、已售出、筛选。

安全边界：

- 只读浏览主页和商品列表可以做。
- 编辑资料、宝贝管理、在售/已售出的编辑、上下架、删除都必须确认。

### `/collection` 我的收藏

结构：

- Tab：全部、降价宝贝、有效宝贝、失效宝贝。
- 收藏卡片：商品链接、价格/降价提示、`取消收藏`、`我想要`。
- 商品链接仍走 `/item?id=商品ID&categoryId=类目ID`。

安全边界：

- 读取收藏列表结构可以做。
- `取消收藏` 会改变账号收藏状态，必须确认。
- `我想要` 可能进入沟通/表达购买意向，发送前必须确认。

### `/bought` 我买到的

结构：

- Tab：全部、待付款、待发货、待收货、待评价、退款中。
- 订单卡片：店铺/商品区、订单状态、价格、更多菜单、物流记录、宝贝快照。
- 常见动作：联系卖家、再次购买、确认收货、去评价、我要退款、查看钱款、退款详情、删除订单、投诉卖家。
- 订单详情链接走 `/order-detail?orderId=订单ID`。
- 联系卖家链接可带 `itemId` 和 `peerUserId`。

安全边界：

- 只读筛选和查看订单卡片结构可以做。
- 确认收货、评价、退款、删除订单、投诉、查看钱款、再次购买、联系卖家前必须确认。

### `/order-detail?orderId=...` 订单详情

稳定字段：

- 订单详情、订单编号、订单状态。
- 物流信息/物流记录。
- 收货地址。
- 商品信息、运费。
- 付款时间、发货时间等时间节点。

常见动作：

- 确认收货。
- 再次购买。
- 我要退款。
- 物流记录。
- 联系卖家。
- 客服。

安全边界：

- 订单详情可只读查看。
- 涉及收货、退款、评价、联系卖家、客服介入的动作必须确认。
- 记录时只写字段名，不写订单编号、地址、物流轨迹或商品内容。

### `/create-order?itemId=...` 确认订单

稳定字段：

- 收货地址。
- 商品/运费。
- 支付方式，实测可见支付宝。
- 闲鱼币/优惠类区域。

安全边界：

- 只能作为确认页只读查看。
- 不自动提交订单、不自动支付、不自动改地址。
- 收货地址和支付信息属于高敏信息，只记录字段类型。

### `/account` 账号与安全

结构：

- 基本信息。
- 保持登录。
- 接收手机通知。
- 认证信息。
- 用户身份信息。
- 实人认证。
- 支付宝实名认证。
- 安全中心。

安全边界：

- 可以只读判断是否存在这些模块。
- 不记录会员名、手机号、证件、支付宝账号或认证细节。
- 保持登录、通知开关、认证、安全中心跳转或任何修改动作都必须确认。

### `/feedback?from=...` 用户反馈

结构：

- 标题：闲鱼用户反馈中心。
- 类型：我要提功能/体验建议、我要反馈故障。
- 问题页面：首页、搜索、商品详情、交易、闲鱼号、其它。
- 文本框：描述闲鱼使用过程中遇到的问题。
- 截图上传：最多 5 张截图。
- 按钮：提交。

安全边界：

- 可以帮用户拟反馈草稿。
- 上传截图、提交反馈前必须确认内容和图片。

### `/publish` 主站发闲置

结构：

- 基础信息：宝贝图片、添加首图、宝贝描述。
- 属性识别：上传主图/填写内容后智能识别属性。
- 价格：价格、原价、鱼小铺软件服务费提示。
- 发货设置：包邮、按距离计费、一口价、无需邮寄、支持自提。
- 宝贝所在地：会带当前/常用位置，只记录字段名。
- 按钮：发布。

安全边界：

- 可以打开并帮填草稿。
- 上传图片、使用具体位置、发布前必须确认。

### `/im` 消息页

结构：

- 未选中会话时显示消息空态，例如暂无会话/尚未选择联系人。
- 选中具体会话后会进入私聊上下文，可能带商品、订单、用户信息。

安全边界：

- 可以打开页面和读取空态结构。
- 不读取或记录具体联系人、聊天内容。
- 发送任何消息前必须确认对象和文本。

### `/changelog` 更新日志

结构：

- 公共更新日志页。
- 常见内容包括网页版发闲置、多规格/深库存等产品更新。

安全边界：

- 公共只读页，低风险。

## 第十轮补充：主站静态包/API 反查

这一轮从主站前端包静态反查，不访问账号数据。结论用于补全“页面能力图”，不代表这些接口可以直接调用。

### 额外页面包

主站资产清单里除常规页面外，还存在这些页面包：

- `create-order-yhb-index`：验货宝确认订单页。
- `order-detail-yhb-index`：验货宝订单详情页。
- `login-validation-index`：登录校验页。
- `upgrade-browser-index`：浏览器升级提示页。
- `select-account-index`：账号选择页。
- `find-account-index`：找回/查找账号页。
- `pay-success-index`：支付成功页。
- `common-video-layout` / `common-video-index`：公共视频落地页。
- `playground-index`：内部实验页。

处理方式：

- 常规自动化只把它们当路由/能力线索。
- `find-account`、`select-account`、`login-validation` 涉及账号安全或登录校验，不自动操作。
- `pay-success` 只作为支付完成后的结果页，不为了测试触发支付。
- `common-video` 是活动/内容落地页，低风险，只读。
- `upgrade-browser` 是兼容性提示页，低风险，只读。

### 主站 API 能力分组

以下为前端包暴露的 API 名称分组，只做能力边界记录，不直接调用：

个人/收藏/主页：

- `mtop.idle.web.user.page.nav`
- `mtop.idle.web.user.page.head`
- `mtop.idle.web.user.page.account`
- `mtop.idle.web.xyh.item.list`
- `mtop.taobao.idle.web.favor.item.list`
- `mtop.taobao.idle.web.attention.relation`
- `mtop.idle.web.trade.rate.list`
- `mtop.taobao.idle.collect.item`

商品详情：

- `mtop.taobao.idle.pc.detail`
- `mtop.taobao.idle.item.web.recommend.list`
- `mtop.taobao.idle.trade.common.sku.selector`
- `mtop.taobao.idle.collect.item`
- `mtop.taobao.idle.item.downshelf`
- `mtop.idle.cloud.video.query`
- `mtop.taobao.idle.cat.configs`

发布：

- `mtop.idle.pc.idleitem.preget`
- `mtop.idle.pc.idleitem.prepublish.check`
- `mtop.idle.pc.idleitem.publish`
- `mtop.idle.pc.idleitem.edit`
- `mtop.idle.pc.idleitem.editDetail`
- `mtop.idle.idleitem.draft.edit`
- `mtop.idle.idleitem.draft.publish`
- `mtop.taobao.idleitem.badwords.prepubcheck`
- `mtop.taobao.idle.kgraph.property.search`
- `mtop.taobao.idle.kgraph.property.recommend`
- `mtop.taobao.idle.local.poi.get`
- `mtop.idle.item.publish.service.cards.list`

交易/订单：

- `mtop.idle.web.trade.bought.list`
- `mtop.idle.web.trade.order.detail`
- `mtop.taobao.idle.trade.order.render`
- `mtop.taobao.idle.trade.order.create`
- `mtop.idle.trade.pay.info.query`
- `mtop.order.doPay`
- `mtop.order.dopay`
- `mtop.order.doop`
- `mtop.taobao.idle.logistic.address.list.query`
- `mtop.cainiao.ld.detail.tradeid.ordercode.mailno.rescode.get.xy`
- `mtop.taobao.idle.trade.order.cancel`
- `mtop.taobao.idle.trade.order.close.reason.get`
- `mtop.taobao.idle.trade.seller.delay.confirm`
- `mtop.taobao.idle.trade.user.adjust.price`
- `mtop.taobao.idle.trade.order.modify.price.render`
- `mtop.alibaba.idle.autotrade.trade.data.update`
- `mtop.taobao.idle.unconsign.detail`
- `mtop.taobao.idle.mtee.risk.get`

验货宝：

- `mtop.alibaba.idle.pc.yhb.order.create.render`
- `mtop.alibaba.idle.pc.yhb.order.create`
- `mtop.taobao.idle.pc.trade.full.info`
- `mtop.taobao.idle.pc.yhb.dispute.apply.list`
- `mtop.alibaba.idle.pc.galaxy.report.detail`
- `mtop.taobao.idle.pc.trade.appraise.order.perform`

IM/消息：

- `mtop.taobao.idlemessage.pc.session.sync`
- `mtop.taobao.idlemessage.pc.message.sync`
- `mtop.taobao.idlemessage.message.card.send`
- `mtop.taobao.idlemessage.relation.message.read`
- `mtop.taobao.idlemessage.pc.session.unread.clean`
- `mtop.taobao.idlemessage.pc.systems.unread.clean`
- `mtop.taobao.idlemessage.pc.redpoint.query`
- `mtop.taobao.idlemessage.pc.user.query`
- `mtop.taobao.idlemessage.user.query`
- `mtop.taobao.idlemessage.face.emoji.load`
- `mtop.taobao.idlemessage.quickreply.list.get.v1`
- `mtop.taobao.idlemessage.pc.tool.item.search`
- `mtop.taobao.idlemessage.tool.item.query`
- `mtop.idle.trade.message.chat.tradeinfo`
- `mtop.idle.trade.pc.message.headinfo`
- `mtop.taobao.idlemessage.pc.blacklist.query`
- `mtop.taobao.idlemessage.pc.blacklist.add`
- `mtop.taobao.idlemessage.pc.blacklist.remove`

搜索/位置：

- `mtop.taobao.idlemtopsearch.pc.search`
- `mtop.taobao.idlemtopsearch.pc.search.suggest`
- `mtop.taobao.idlemtopsearch.pc.search.shade`
- `mtop.taobao.idlemtopsearch.pc.item.search.activate`
- `mtop.taobao.idle.filter.hitnum.pc.get`
- `mtop.taobao.idle.division.all.get`
- `mtop.taobao.idle.local.poi.get`

内容落地页：

- `mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get`

### App Deep Link 线索

PC 包里还包含若干 `fleamarket://` deep link：

- `publishentry`：App 发布入口。
- `simple_post?draftId=`：App 简易发布草稿。
- `BoughtItems` / `SoldItems`：App 买到/卖出列表。
- `order_detail_new?flutter=true` / `order_detail`：App 订单详情。
- `account` / `identity_auth?flutter=true`：账号/认证入口。
- `sku_layer`：规格选择层。
- `x_chat?sid=` / `custom_chat?sid=`：App 聊天入口。

这些 deep link 说明 PC 页会桥接到 App 能力，但在网页自动化里只作为边界提示，不主动唤起 App。

### API 安全边界

- 所有 `publish`、`order.create`、`doPay`、`doop`、`cancel`、`delay.confirm`、`adjust.price`、`message.card.send`、`blacklist.add/remove`、`collect.item` 都可能改变状态，不能直接调用。
- `address.list.query`、`order.detail`、`message.sync`、`trade.full.info` 等会返回隐私数据，只能在用户明确授权下做只读摘要。
- 优先使用页面可见状态，而不是绕过页面直接调接口。

## 第十一轮补充：覆盖矩阵和卖家 API 风险层

这一轮对本地前端资产做覆盖审计：

- 主站/普通网页版 JS 包：28 个，包括 `main.js`、`p_layout.js`、`p_search-index.js` 和 `work/www-assets/full` 下 25 个页面/能力包。
- 卖家工作台静态包：3 个大包，分别是 `idle-seller-data-main.js`、`seller-workbench-main.js`、`seller-workbench-vendors.js`。
- 总计扫描 JS 包：31 个。
- 结论：主站常规页面、边缘页面包、卖家工作台核心模块都已形成页面级地图；交易/支付/验货宝/投诉/发货等只做静态和只读边界，不触发真实流程。

### 主站静态包覆盖

已下载并纳入静态审计的主站包：

| 包名 | 页面/能力 | 覆盖状态 |
| --- | --- | --- |
| `main.js` | 主入口/运行时 | 已纳入接口和路由审计 |
| `p_layout.js` | 主站公共布局 | 已记录导航、搜索建议、登录跳转、IM 红点等公共能力 |
| `p_index.js` | 首页 | 已结合 live 页面和静态 API |
| `p_search-index.js` | 搜索页 | 已结合 live 页面和筛选脚本 |
| `p_mach-feeds-index.js` | 频道流 | 已记录 machId/publishTimes 结构 |
| `p_item-index.js` | 商品详情 | 已记录字段、按钮、推荐和收藏边界 |
| `p_personal-index.js` | 个人主页 | 已记录主页/宝贝/信用/管理入口 |
| `p_collection-index.js` | 收藏页 | 已记录收藏 tab 和卡片动作 |
| `p_bought-index.js` | 买到的 | 已记录订单 tab 和买家动作 |
| `p_order-detail-index.js` | 普通订单详情 | 已记录订单/物流/售后边界 |
| `p_create-order-index.js` | 普通确认订单 | 已记录确认页字段和支付边界 |
| `p_pay-success-index.js` | 支付成功页 | 只做结果页/静态包记录 |
| `p_publish-index.js` | 主站发闲置 | 已记录草稿字段、发布边界和 API |
| `p_im-index.js` | 主站消息 | 已记录空态、会话和发送边界 |
| `p_account-index.js` | 账号与安全 | 已记录账号安全模块和通知开关 |
| `p_account-api.js` | 账号通知 API | 静态记录 query/update，修改前确认 |
| `p_feedback-index.js` | 用户反馈 | 已记录反馈类型、截图、提交边界 |
| `p_login-index.js` | 登录页 | 已记录扫码/验证码由用户完成 |
| `p_login-validation-index.js` | 登录校验 | 静态包很小，只作为账号安全页记录 |
| `p_find-account-index.js` | 找回/查找账号 | 静态包很小，不主动访问 |
| `p_select-account-index.js` | 账号选择 | 静态包很小，不主动切换 |
| `p_upgrade-browser-index.js` | 浏览器升级提示 | 已记录推荐升级浏览器，低风险 |
| `p_common-video-layout.js` | 公共视频布局 | 静态记录活动/内容落地页 |
| `p_common-video-index.js` | 公共视频页 | 静态记录活动/内容落地页 |
| `p_create-order-yhb-index.js` | 验货宝确认订单 | 静态记录，不触发下单 |
| `p_order-detail-yhb-index.js` | 验货宝订单详情 | 静态记录，不触发售后/评价 |
| `p_playground-index.js` | 内部实验页 | 不主动访问，发现 `account.sub.test` / 支付测试类 API |
| `p_$.js` | 极小运行占位包 | 无业务页面 |

更新日志 `/changelog` 已做 live 只读记录；当前本地资产没有捕获到独立的更新日志 JS 包，因此不把它计入静态包覆盖表。

### 主站边缘能力补充

- 账号通知：`mtop.taobao.idlemessage.pc.profile.notice.query` / `update`，对应网页版通知开关；更新前必须确认。
- 验货宝确认订单：`mtop.alibaba.idle.pc.yhb.order.create.render` / `create`，属于下单高风险。
- 验货宝详情：`mtop.taobao.idle.pc.trade.full.info`、`mtop.taobao.idle.pc.yhb.dispute.apply.list`、`mtop.alibaba.idle.pc.galaxy.report.detail`、`mtop.taobao.idle.pc.trade.appraise.order.perform`，可能涉及报告、纠纷、评价。
- 发布草稿：`mtop.idle.idleitem.draft.edit` / `draft.publish`，即使是草稿也可能保存账号状态。
- 发布审核：`mtop.taobao.idleitem.badwords.prepubcheck`、`prepublish.check`，可用于发布前校验，但不能替代人工确认。
- IM 风控和消息：`blacklist.add/remove`、`quickreply`、`voice.change`、`message.card.send` 都属于会影响沟通或账号关系的操作。
- `playground` 中出现 `mtop.idle.user.account.sub.test` 和支付类 API，明确归为内部实验/测试，不进入常规自动化。

### 卖家后台 API 风险层

卖家工作台静态包除了左侧菜单路由，还暴露更深的业务能力。自动化应先按页面层做，只在用户明确授权时才进入 API 层。

物流/发货：

- `mtop.taobao.idle.logistics.guess.mailno`
- `mtop.taobao.idle.logistics.merchant.consign.page.render`
- `mtop.taobao.idle.logistics.merchant.consign.offline`
- `mtop.taobao.idle.logistics.merchant.consign.dummy`
- `mtop.taobao.idle.logistics.merchant.consign.resend`
- `mtop.taobao.idle.logistics.merchant.excel.consign.offline`
- `mtop.taobao.idle.logistics.merchant.oss.sts.get`
- `mtop.taobao.idle.logistics.merchant.oss.url.get`

边界：导入发货、填写物流、重新发货、上传 Excel 都会影响订单履约，必须确认。

退款/退运费/赔付：

- `mtop.taobao.idle.merchant.refund.agree.refund`
- `mtop.taobao.idle.merchant.refund.refuse`
- `mtop.taobao.idle.merchant.refund.refuse.render`
- `mtop.taobao.idle.merchant.postage.refund.detail.query`
- `mtop.taobao.idle.merchant.postage.refund.refuse`
- `mtop.taobao.idle.merchant.postage.refund.refuse.reason.query`
- `mtop.taobao.idle.merchant.compensate.service.detail.query`
- `mtop.taobao.idle.merchant.compensate.service.pay`
- `mtop.taobao.idle.merchant.compensate.service.refuse`
- `mtop.taobao.idle.merchant.compensate.service.refuse.render`

边界：同意退款、拒绝退款、赔付支付、拒绝赔付都是高风险经营动作。

投诉/纠纷/举证：

- `mtop.taobao.idle.cco.shop.complain.detail`
- `mtop.taobao.idle.cco.shop.complain.refuse`
- `mtop.taobao.idle.cco.shop.complain.apply.revoke`
- `mtop.taobao.idle.cco.shop.complain.return.money.page`
- `mtop.taobao.idle.cco.shop.complain.submit.proof`
- `mtop.taobao.idle.cco.shop.complain.submit.active.proof`
- `mtop.taobao.idle.cco.shop.complain.submit.passive.proof`
- `mtop.taobao.idle.merchant.dispute.create`
- `mtop.taobao.idle.merchant.dispute.create.page`

边界：投诉、撤销、拒绝、举证、创建纠纷必须由用户确认材料和动作。

纠纷消息：

- `mtop.taobao.idle.shop.dispute.message.get.conversation`
- `mtop.taobao.idle.shop.dispute.message.query.history`
- `mtop.taobao.idle.shop.dispute.message.query.unread.list`
- `mtop.taobao.idle.shop.dispute.message.mark.read`
- `mtop.taobao.idle.shop.dispute.message.send`

边界：可只读汇总字段；发送纠纷消息、标记已读前确认。

订单地址修改：

- `mtop.idle.merchant.order.get.modify.address.info`
- `mtop.idle.merchant.order.address.modify.agree`
- `mtop.idle.merchant.order.address.modify.refuse`
- `mtop.alibaba.idle.seller.platform.merchant.delivery.address.list.query`

边界：地址是隐私信息；同意/拒绝改地址会影响履约，必须确认。

评价/备注/改价：

- `mtop.taobao.idle.merchant.rate.create`
- `mtop.taobao.idle.merchant.add.memo`
- `mtop.taobao.idle.trade.merchant.user.adjust.price`
- `mtop.taobao.idle.trade.user.adjust.price`
- `mtop.taobao.idle.trade.order.modify.price.render`

边界：评价、备注、改价都属于真实经营动作。

卖家 IM/客服：

- `mtop.taobao.idlemessage.customer.deliver.session`
- `mtop.taobao.idlemessage.customer.leave.session`
- `mtop.taobao.idlemessage.customer.rejoin.session`
- `mtop.taobao.idlemessage.customers.info.get`
- `mtop.taobao.idlemessage.message.card.send`
- `mtop.taobao.idlemessage.quickreply.list.get.v1`
- `mtop.taobao.idlemessage.quickreply.content.operate`
- `mtop.taobao.idlemessage.quickreply.group.operate`
- `mtop.taobao.idlemessage.pc.blacklist.add`
- `mtop.taobao.idlemessage.pc.blacklist.remove`
- `mtop.taobao.idlemessage.pc.file.entry.auth`
- `mtop.taobao.idlemessage.file.token.v1`
- `mtop.taobao.idlemessage.pc.tool.remark`

边界：发送卡片、快捷回复维护、黑名单、文件上传、客服接待转移都必须确认。

数据/报表：

- `mtop.alibaba.idle.seller.pc.datacompass.*`
- `mtop.alibaba.idle.seller.platform.datacompass.*`
- `mtop.alibaba.idle.seller.pc.datacompass.*.export`
- `mtop.alibaba.idle.seller.pc.datacompass.*.excel.url`

边界：只读指标可汇总；导出和下载报表前确认。

### 当前覆盖判断

- 页面层：主站常规页、主站边缘包、卖家工作台菜单页已基本覆盖。
- 操作层：已建立“可只读 / 需确认 / 禁止主动触发”边界。
- 未触发层：支付成功、验货宝真实下单、售后举证、退款/赔付、发货导入、账号找回/切换、登录校验等只能静态记录，不做实测触发。
- 后续如果要自动化多账号，应先按浏览器 Profile 隔离，再按这份页面地图给每个动作分级。

## 第十四轮补充：静态接口审计二次补齐

这一轮从当前工作区 31 个 JS 文件重新抽取 `mtop.*` 名称，并生成独立接口审计表 `goofish-static-api-audit.md`。

抽取结果：

- 原始 `mtop` 名称：225 个。
- 排除运行时、配置、确认弹窗和请求器字段后，业务接口：200 个。
- 分组数量：搜索/首页 5 个，个人/收藏 5 个，商品/发布/服务 22 个，交易/售后/物流/支付 71 个，IM/消息 46 个，数据/财务/经营分析 26 个，账号/权限/风控 10 个，其他/基础能力 15 个。

这次补齐的重点：

- `p_layout.js` 不是业务页，但承担公共搜索建议、登录跳转、用户导航、IM 红点、消息登录态等能力，应纳入主站覆盖。
- 数据罗盘接口比页面表头更多，包含粉丝洞察、首购/复购、单用户浏览/商品/卖家摘要、客服明细/分流/评价和 Excel URL；这些都是经营数据，只能脱敏只读，导出前确认。
- IM 接口不只包含发送消息，还包含会话同步、未读清理、系统未读清理、登录 token、黑名单、快捷回复、文件权限、客服接待转移和纠纷消息；默认只看页面框架，发送、标记已读、拉黑、快捷回复维护、文件上传前确认。
- 交易/售后层新增关注卖家侧关单、批量延长收货、批量提醒收货、改价渲染、地址修改同意/拒绝、赔付、退运费拒绝、投诉撤销/举证等接口；全部归为高风险门禁。
- 账号/权限层新增子账号导航、用户组成员、商家身份、备注修改、账号 mock apply/cancel 等接口；只读判断可以，权限、身份、备注或账号状态变更前确认。
- 静态路由里还出现 `#/seller-trade/order-manage/order-detail?orderId=` 和 `#/account-check?userNick=` 这类深层/带参路由；它们用于识别页面状态，不主动拼真实订单号或账号名访问。

执行规则补充：

- 自动化优先走页面，不绕过页面直接调用 `mtop`。
- 如果页面和接口风险不同，按更高风险处理。
- 如果接口名包含 `create`、`publish`、`pay`、`refund`、`refuse`、`agree`、`send`、`update`、`delete`、`clean`、`export`、`download`、`consign`、`blacklist`、`remark`、`proof`、`dispute`，默认必须确认。
- 接口审计表只保留接口名和来源包，不保留真实数据。

## 第十二轮补充：边缘包实锤行为和证据等级

这一轮重点核对几个极小或高风险边缘包的实际行为，仍然只做静态确认，不触发账号/交易动作。

### 极小边缘包

`p_find-account-index.js`：

- 页面标题：找回账号_闲鱼。
- 页面配置：`Page_xyPCFindAccount`。
- 实际行为：组件加载后执行跳转到 `/`，不渲染可操作表单。
- 结论：PC 侧只是找回账号占位/兜底，不作为常规账号找回自动化入口。

`p_select-account-index.js`：

- 页面标题：选择登录账号_闲鱼。
- 页面配置：`Page_xyPCSelectAccount`。
- 实际行为：组件加载后执行跳转到 `/`，不渲染可操作账号列表。
- 结论：PC 侧只是账号选择占位/兜底，多账号不能依赖这个页自动切换。

`p_login-validation-index.js`：

- 实际行为：只渲染空片段。
- 结论：登录校验页不是常规可操作 UI；扫码、验证码、风控校验仍由用户本人完成。

`p_$.js`：

- 极小运行占位包，无业务页面。

### 浏览器升级页

`p_upgrade-browser-index.js`：

- 页面标题：建议您升级浏览器_闲鱼。
- 核心文案：为了更好使用闲鱼网页版，建议升级浏览器。
- 推荐浏览器：Google Chrome、Mozilla Firefox、Microsoft Edge、QQ Browser、360 Browser、360 X Browser、Sogou Browser。
- 自动化边界：这是低风险只读页；不自动打开外部下载链接。

### 公共视频页

`p_common-video-layout.js` / `p_common-video-index.js`：

- 页面标题：闲鱼 - 闲不住？上闲鱼！
- 页面配置：`Page_xyPCCommonVideo`。
- 数据来源：`mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get`。
- 配置路径：`xy-site/pages/common-video`。
- 渲染内容：背景色、内容宽高、背景图、标题图、视频地址、自动播放/静音、视频尺寸和位置。
- 自动化边界：活动/内容落地页，只读；不主动播放、下载或上传视频。

### Playground 内部实验页

`p_playground-index.js`：

- 页面配置显示它是内部实验/调试页。
- 包含埋点测试：发送自定义事件。
- 包含页面事件订阅/发布测试：例如刷新 IM 头部事件。
- 包含通用二维码弹框测试：示例为闲鱼实人认证二维码。
- 包含登录状态测试：调用 `mtop.idle.user.account.sub.test`。
- 包含支付测试：输入订单 ID 后调用支付类 API，例如 `mtop.order.dopay`，并可能打开支付宝链接。
- 包含图片加载错误兜底测试。
- 自动化边界：禁止主动访问、禁止调用测试支付、禁止提交订单 ID。

### 证据等级表

| 证据等级 | 含义 | 当前覆盖 |
| --- | --- | --- |
| Live + Static | 浏览器实测页面骨架，并用前端包/API 反查校准 | 首页、搜索、商品详情、个人页、收藏、买到的、订单详情、确认订单、发布、消息、账号、反馈、更新日志、卖家工作台主菜单页 |
| Live Only | 已在浏览器看过，但静态包信息价值较低 | 客服外链入口、APP/商品码弹层、部分右侧工具条行为 |
| Static Only | 只静态确认包/路由/API，不触发页面业务 | 找回账号、选择账号、登录校验、公共视频、浏览器升级、支付成功、验货宝确认订单、验货宝订单详情、playground |
| Boundary Only | 只记录能力和风险，明确不实测 | 真实支付、验货宝下单、确认收货、退款/拒绝退款、赔付、发货导入、投诉举证、纠纷消息、账号找回/切换、认证、黑名单、IM 发消息 |

### 当前熟悉程度判断

- 常规浏览/搜索/详情/个人/订单/发布/消息/卖家后台页面：已达到可画路径、可识别字段、可判定风险的程度。
- 高风险交易/售后/账号安全页面：已达到知道入口、字段类型、API 能力和不可自动触发边界的程度。
- 不应继续“为了实测而实测”的部分：支付、确认收货、退款赔付、投诉举证、账号找回、账号切换、认证、发消息、导出/上传。
- 后续如果要写自动化脚本，应以这份证据等级表作为准入规则：Static Only 和 Boundary Only 只能打开/说明/等待用户确认，不能直接提交。

## 第十三轮补充：动作准入矩阵和多账号规则

这一轮把页面地图转成可执行准入规则，方便以后真正做自动化时判断“能不能点、能不能填、要不要停下来问用户”。

### 动作准入矩阵

| 动作类型 | 代表页面/入口 | 允许程度 | 执行规则 |
| --- | --- | --- | --- |
| 打开公共页面 | 首页、搜索、频道、商品详情、更新日志、公共视频、浏览器升级 | 可直接做 | 可打开、滚动、截图、读取公开字段 |
| 搜索和筛选 | `/search` 关键词、价格、排序、标签筛选、频道流 | 可直接做 | 可改关键词和筛选；地区筛选需确认弹层已打开，不误点分页 |
| 读取公开商品信息 | 商品卡、商品详情、推荐流 | 可直接做 | 可读标题、价格、地区、想要人数、保障标签；不自动收藏/购买/联系 |
| 读取账号内列表 | 个人页、收藏、买到的、订单列表、卖家订单/退款/评价/投诉列表 | 可只读 | 可汇总字段和状态；总结时去掉商品名、买家名、订单号、地址、金额细节 |
| 查看详情页 | 商品详情、订单详情、退款详情、投诉详情、安全中心详情 | 只读优先 | 可打开和说明字段；涉及隐私的内容不写入文档或外发 |
| 填草稿 | 发布闲置、反馈、投诉/举证材料草稿、IM 草稿 | 可辅助但不提交 | 可以帮写内容或填入草稿；提交/发送/发布前必须停下确认 |
| 上传文件/图片 | 发布图片、反馈截图、售后举证、发货 Excel、IM 文件 | 必须确认 | 上传前说明文件和目标页面；用户确认后才操作 |
| 导出/下载数据 | 数据下载、财务导出、历史下载记录、全量明细、客服数据导出 | 必须确认 | 说明导出的数据范围和文件类型；确认后才点击 |
| 账号设置 | 保持登录、手机通知、认证、支付宝实名、安全中心、子账号 | 必须确认 | 只读状态可看；任何修改/认证/开关都停下确认 |
| 沟通动作 | IM 发消息、我想要、联系卖家、客服分流、快捷回复、纠纷消息 | 必须确认 | 确认对象、文本、是否带商品/订单卡片后才发送 |
| 交易动作 | 提交订单、支付、再次购买、确认收货、取消订单、延长收货、修改物流 | 禁止主动触发 | 只能打开页面并说明风险；用户明确逐项授权才可继续 |
| 售后/纠纷动作 | 退款、拒绝退款、赔付、投诉、撤销投诉、举证、申诉、仲裁消息 | 禁止主动触发 | 只做只读和草稿；提交/同意/拒绝/赔付前必须确认 |
| 商品经营动作 | 发布、编辑、改价、粉丝价、上架、下架、删除、批量下架、擦亮计划 | 禁止主动触发 | 可以准备方案和草稿；保存、投放、上下架前确认 |
| 内部/测试页 | playground、支付测试、账号测试、登录校验占位 | 禁止主动访问/触发 | 仅静态记录，不进入真实自动化流程 |

### 页面自动化默认策略

默认策略按页面分四类：

| 页面类 | 页面 | 默认策略 |
| --- | --- | --- |
| 公开浏览 | `/`、`/search`、`/mach-feeds`、`/item`、`/changelog`、`/common-video`、`/upgrade-browser` | 可浏览、读取、截图、比较 |
| 登录只读 | `/personal`、`/collection`、`/bought`、`/order-detail`、卖家数据/订单/财务列表 | 可打开和摘要，但隐私字段脱敏 |
| 草稿辅助 | `/publish`、`/feedback`、IM 输入框、售后/投诉文本框 | 可拟稿和填草稿，不提交 |
| 高风险门禁 | `/create-order`、`/pay-success`、验货宝订单、账号认证、退款/投诉/赔付/发货/导出/投放 | 只说明结构和风险，停在确认前 |

### 多账号会话规则

结论：不要把多账号理解成“给密钥就能切账号”。闲鱼 PC 登录态主要是浏览器 Profile 里的 cookie/session 和风控状态。

推荐模型：

- 一个账号对应一个独立浏览器 Profile。
- Profile 名称和账号备注单独维护，例如 `goofish-profile-main`、`goofish-profile-store-a`。
- 不复制 cookie，不混用 localStorage/sessionStorage，不把一个账号的登录态注入另一个 Profile。
- 每次执行前先打开 `/account` 或卖家工作台首页确认当前账号身份，但记录时只写“账号 A/B 已登录”，不写会员名。
- 如果出现登录校验、扫码、实人认证、选择账号、找回账号，立即交给用户本人处理。
- 不使用账号密码、短信验证码、支付密码、支付宝信息作为自动化“密钥”。
- 如果需要服务器/脚本长期运行，应让脚本只保存 Profile 路径和账号别名，不保存敏感凭证。

多账号执行顺序：

1. 选择账号别名。
2. 启动对应独立 Profile。
3. 打开 `/account` 或 `seller.goofish.com` 只读确认登录态。
4. 执行低风险或只读任务。
5. 遇到草稿提交、发消息、交易、售后、账号设置、导出下载，停下要求用户确认。
6. 任务结束后记录本次用的是哪个账号别名和页面路径，不记录 cookie、订单号、地址或联系人。

### 自动化日志脱敏规则

允许记录：

- 页面路径和 hash。
- 页面标题。
- 字段名、按钮名、tab 名、表头名。
- 商品/订单/售后的状态类别。
- 是否成功打开、是否需要登录、是否被权限拦截。
- 风险等级和下一步是否需要用户确认。

不允许记录：

- 会员名、昵称、手机号、身份证、支付宝账号。
- 订单号、物流单号、商品 ID、买家/卖家昵称。
- 收货/退货/发货地址。
- 真实商品标题、聊天内容、投诉内容、评价内容。
- 金额明细、可开票金额、收入/支出/退款/赔付具体数值。
- cookie、token、localStorage、sessionStorage、二维码内容。

### 自动化前置检查清单

任何脚本开始前先检查：

- 当前 Profile 是否和目标账号别名一致。
- 当前页面是否在 `www.goofish.com` 或 `seller.goofish.com`。
- 当前动作是否属于动作准入矩阵里的可直接做、只读、草稿辅助或高风险门禁。
- 是否会触发提交、发送、支付、保存、导出、上传、上下架、退款、投诉、认证、拉黑。
- 是否会读取或保存隐私字段。

如果任一项不确定，默认按高风险处理，停下让用户确认。

## 任务路径手册

### 搜商品 / 比价

入口：

1. `/search?q=关键词`
2. 等待瀑布流加载。
3. 必要时滚动一次。
4. 读取商品卡片。
5. 点击 `/item?id=...&categoryId=...` 进入详情。

可读字段：

- 标题/描述摘要
- 价格
- 想要人数
- 地区
- 卖家信用/回复速度
- 保障标签
- 商品详情中的品牌、成色、描述、浏览数、想要数

注意：

- 筛选不一定改变 URL。
- 适合自动化的筛选有关键词、价格区间、排序、包邮、全新、验货宝等。

### 看商品详情

入口：

- `/item?id=...&categoryId=...`

读取顺序：

1. 卖家卡：地区、活跃时间、历史成交/好评率、信用标签。
2. 商品图集。
3. 价格和保障标签。
4. 标题、描述、属性。
5. 想要人数和浏览数。
6. 推荐商品。

不能自动执行：

- `聊一聊`
- `立即购买`
- `收藏`

这些都会改变账号状态或触达交易流程。

### 联系卖家

入口：

- 商品详情页 `聊一聊`
- `/im?itemId=...&peerUserId=...`
- 收藏页商品卡 `我想要`

安全规则：

- 可以打开会话。
- 可以根据用户给的内容帮拟草稿。
- 真正发送消息前必须确认对象和文本。

### 买东西 / 下单

入口：

- 商品详情页 `立即购买`
- `/create-order?itemId=...`

确认页字段：

- 收货地址
- 商品信息
- 运费/配送
- 支付方式，如支付宝
- 实付金额

安全规则：

- 可以只读检查。
- 不自动提交订单。
- 不自动支付。
- 不自动修改收货地址或支付方式。

### 查买家订单

入口：

- `/bought`

订单列表状态：

- 全部
- 待付款
- 待发货
- 待收货
- 待评价
- 退款/售后

常见按钮：

- 联系卖家
- 再次购买
- 确认收货
- 物流记录
- 去评价
- 查看钱款

安全规则：

- 查订单、查物流可以辅助。
- `确认收货`、`退款/售后`、`去评价`、`再次购买` 都需要确认。

### 查订单详情 / 物流

入口：

- `/order-detail?orderId=...`

字段：

- 订单编号
- 收货地址
- 物流/快递
- 卖家/买家
- 退款/售后状态

安全规则：

- 此页含地址和物流隐私。
- 不把地址、电话、订单号写入总结。
- 不自动退款、确认收货、延长收货、评价。

### 发闲置

入口：

- `/publish`
- 右侧工具条 `发闲置`
- 更新日志页的发闲置入口

填写结构：

1. 图片
2. 描述
3. 属性规格
4. 价格/原价
5. 发货设置
6. 所在地
7. 发布

可辅助：

- 帮写标题/描述。
- 帮整理图片顺序。
- 帮填价格、规格、运费设置草稿。

必须确认：

- 上传图片。
- 最终点击 `发布`。

### 管自己的商品

普通网页版入口：

- `/personal`
- `宝贝`
- `宝贝管理`
- `在售`
- `已售出`

卖家工作台入口：

- `seller.goofish.com`
- `商品 -> 商品管理`
- `#/seller-item/goods-manage`

工作台商品管理字段：

- 商品信息
- 价格
- 库存
- 累计销量
- 创建时间
- 操作

常见操作：

- 商品发布
- 复制
- 编辑
- 改价
- 设置粉丝价
- 下架
- 批量下架

安全规则：

- 只读列表可以做。
- 编辑、改价、下架、批量操作必须确认。

### 卖家处理订单

入口：

- `seller.goofish.com`
- `交易 -> 订单管理`
- `#/seller-trade/order-manage`

筛选字段：

- 完整订单编号
- 物流单号
- 商品 ID
- 买家昵称
- 订单状态
- 退款状态
- 日期区间

表头：

- 商品信息
- 发货/退款状态
- 单价/数量
- 成交价
- 买家/收货信息
- 操作

常见操作：

- 联系买家
- 查看详情
- 查看钱款
- 添加备注
- 提醒收货
- 修改物流
- 去评价
- 批量延长收货
- 批量导入发货

安全规则：

- 查询和筛选可做。
- 发货、修改物流、备注、评价、钱款、导入发货均需确认。

### 卖家看数据

入口：

- `seller.goofish.com`
- `数据 -> 数据总览`
- `数据 -> 商品数据`
- `数据 -> 粉丝数据`
- `数据 -> 客服数据`

数据总览：

- 商品访问/曝光/浏览
- 在线商品数
- 动销商品数
- 交易转化
- 复购情况
- 客服数据

商品数据：

- 商品曝光次数/人数
- 浏览次数/人数
- 询单人数
- 支付人数/订单数/金额
- 浏览支付转化率
- 发起退款/成功退款人数、订单数、金额

客服数据：

- 咨询人数
- 接待人数
- 平均响应时长
- 3 分钟响应率
- 客户服务满意度
- 有效评价数/好评数/差评数

粉丝数据：

- 粉丝数据
- 粉丝洞察
- 性别分布
- 属性分布
- 地域分布
- 人群分布

安全规则：

- 可以汇总趋势和字段。
- 导出数据、下载明细前必须确认。

### 卖家财务 / 发票

入口：

- `财务 -> 收入账单`
- `财务 -> 支出账单`
- `财务 -> 申请发票`
- `财务 -> 开票信息`

收入账单：

- 月汇总
- 日汇总
- 收入明细
- 业务大类
- 收入金额合计
- 退款金额合计

申请发票：

- 待申请发票
- 已申请发票
- 业务类型
- 可开票金额

支出账单：

- 月汇总
- 日汇总
- 支出明细
- 业务大类
- 实收服务费合计
- 服务费返还合计
- 本月付款

开票信息：

- 发票抬头
- 统一社会信用代码
- 纳税类型
- 公司名称
- 开户银行
- 开户银行账号
- 营业地址
- 营业电话

安全规则：

- 财务页面可只读。
- 导出、下载、申请发票、修改开票信息必须确认。

### 账号与安全

入口：

- `/account`

结构：

- 基本信息
- 保持登录
- 接收手机通知
- 用户身份信息
- 实人认证
- 支付宝实名认证
- 安全中心

安全规则：

- 可只读判断状态。
- 不自动修改登录、安全、认证、支付绑定。

### 反馈

入口：

- `/feedback?from=...`

结构：

- 反馈类型
- 问题页面
- 反馈文本
- 截图上传
- 提交

安全规则：

- 可以代写反馈草稿。
- 上传截图、提交反馈必须确认。

### 多账号

推荐方式：

- 一个闲鱼账号一个独立浏览器 Profile。
- 每个 Profile 首次由用户扫码登录。
- 后续用账号名切换 Profile。

不推荐：

- 同一个 Profile 硬切 cookie。
- 把密码、cookie、token 明文交给自动化。

## 第四轮补充：主站路由清单

这一轮来源：

- 首页 HTML 里的站点地图和 SEO 链接。
- `robots.txt` 暴露的受限路径。
- 主站前端脚本里的路由关键字和跳转方法。
- 已登录浏览器中的只读访问结果。

可信度分层：

- `已实测`：已经在当前登录态浏览器里打开过，并观察了页面结构。
- `已发现`：从 HTML、脚本或 robots 里确认存在，但未完整进入页面。
- `不建议测`：与支付、找回账号、选择账号、实验页面或风控相关，只记录入口，不做自动操作。

### `www.goofish.com` 路由总表

| 路由 | 状态 | 作用 | 自动化建议 |
| --- | --- | --- | --- |
| `/` | 已实测 | 首页、搜索入口、频道入口、推荐流 | 可只读浏览和搜索 |
| `/login` | 已实测 | 登录页/登录弹层承载页 | 只辅助打开，扫码/验证码由用户完成 |
| `/search?q=...` | 已实测 | 搜索结果页 | 可读列表、筛选、翻页；不要提交敏感操作 |
| `/mach-feeds?machId=...&publishTimes=...` | 已实测 | 频道/活动/主题流 | 可只读采集可见商品卡片 |
| `/item?id=...&categoryId=...` | 已实测 | 商品详情页 | 可读商品信息；沟通/下单需确认 |
| `/personal` | 已实测 | 我的闲鱼、我的发布、我卖出的 | 可只读；编辑资料/上下架需确认 |
| `/bought` | 已实测 | 我买到的订单列表 | 可只读；售后/确认收货/评价需确认 |
| `/collection` | 已实测 | 我的收藏 | 可只读；取消收藏需确认 |
| `/publish` | 已实测 | 发布闲置 | 可进入和填草稿；发布前必须确认 |
| `/im` | 已实测 | 消息页 | 可读页面结构；发送消息必须确认 |
| `/account` | 已实测 | 账号与安全 | 只读状态；不改认证、手机号、通知、安全设置 |
| `/feedback?from=...` | 已实测 | 反馈页 | 可代写草稿；提交前必须确认 |
| `/changelog` | 已实测 | 更新日志/版本说明 | 可只读 |
| `/create-order?itemId=...` | 已实测 | 创建订单/确认购买 | 高风险页，只读，不自动提交 |
| `/order-detail?orderId=...` | 已实测 | 订单详情 | 只读；不做售后、确认收货、评价 |
| `/pay-success?orderId=...&itemId=...` | 已发现 | 支付成功结果页 | 支付后结果页，不主动触发 |
| `/find-account` | 已发现 | 找回/查找账号相关 | robots 禁止抓取，不建议自动访问 |
| `/select-account` | 已发现 | 多账号选择相关 | robots 禁止抓取，不建议自动访问 |
| `/playground` | 已发现 | 内部实验/调试页 | robots 禁止抓取，不建议自动访问 |

### 路由参数形态

搜索：

- 形态：`/search?q=关键词`
- 脚本形态：`search?q=` + `encodeURIComponent(keyword)`
- 注意：点击筛选后 URL 不一定完整反映筛选状态，要结合页面状态读取。

商品详情：

- 形态：`/item?id=商品ID&categoryId=类目ID`
- 商品卡片通常直接带完整详情链接。
- 商品详情页右侧可能出现 `商品码`，用于 App 扫码打开。

频道页：

- 形态：`/mach-feeds?machId=频道ID&publishTimes=次数`
- 首页频道卡片会跳到这一类页面。
- 页面本质类似主题商品流，需要等待瀑布流加载。

消息页：

- 基础形态：`/im`
- 带商品上下文形态：`/im?itemId=商品ID&peerUserId=对方用户ID`
- 进入会话或发送消息属于高风险动作，必须由用户确认。

订单与支付：

- 创建订单：`/create-order?itemId=商品ID`
- 订单详情：`/order-detail?orderId=订单ID`
- 支付成功：`/pay-success?orderId=订单ID&itemId=商品ID`
- `pay-success` 只作为支付完成后的结果页记录，不应为了测试去触发付款链路。

反馈：

- 形态：`/feedback?from=当前页面路径`
- 右侧工具条点击反馈时会带上当前页面来源。

### 首页 HTML 站点地图

首页公开 HTML 暴露了站点地图入口：

- `/login`
- `/search`
- `/im`

这些链接更像 SEO/导航兜底，不等同于完整业务菜单。真实操作仍以页面可见入口和登录态后的菜单为准。

### 首页 SEO 大类

首页 HTML 暴露的 30 个大类搜索入口：

| 分组 | 大类 |
| --- | --- |
| 手机数码 | 手机、数码、电脑 |
| 服饰运动 | 服饰、箱包、运动 |
| 虚拟潮玩 | 技能、卡券、潮玩 |
| 母婴美护 | 母婴、美妆、个护 |
| 家居家装 | 家具、家电、家装 |
| 文玩礼品 | 文玩、珠宝、礼品 |
| 生活兴趣 | 食品、宠物、花卉 |
| 文娱内容 | 图书、游戏、音像 |
| 出行住房 | 汽车、电动车、租房 |
| 生产资料 | 五金、设备、农牧 |

入口形态：

- `/search?spm=...&q=手机`
- `/search?spm=...&q=数码`
- `/search?spm=...&q=电脑`
- 其他大类同样走 `/search`，核心参数是 `q`。

自动化时可以把这些大类视为“预置搜索词”，不是独立页面类型。

### 首页频道和活动入口

HTML 中确认的频道入口：

| 名称 | 链接形态 | 说明 |
| --- | --- | --- |
| 活动 banner | `/mach-feeds?machId=166630&publishTimes=2` | 首页 banner/活动流 |
| 衣橱捡漏 | `/mach-feeds?machId=163873&publishTimes=1` | 频道流 |
| 二次元 | `/mach-feeds?machId=165202&publishTimes=1` | 频道流 |
| 手机数码 | `/mach-feeds?machId=163816&publishTimes=1` | 频道流 |
| 省钱卡券 | `/mach-feeds?machId=165364&publishTimes=1` | 频道流 |

这些频道页面的共同点：

- 主内容仍是商品卡片流。
- URL 的 `machId` 决定频道内容。
- `publishTimes` 是频道链接附带参数，不应随意改写。

### 首页推荐 Tab

首页 HTML 暴露的推荐 tab/主题词：

- 猜你喜欢
- BJD娃娃
- 垂钓
- 吉他乐器
- 台球
- 摄影摄像
- 钱币收藏
- 女装穿搭
- 居家好物
- 大牌美妆
- 机车

处理方式：

- 可以当成首页推荐流的主题切换。
- 不要把它们当成独立稳定路由。
- 如果点击后 URL 没变，应以页面选中态和新加载商品卡片判断结果。

### 右侧工具条跳转

主站公共布局脚本中确认的工具条行为：

| 工具条项 | 跳转/动作 | 风险 |
| --- | --- | --- |
| 发闲置 | `/publish` | 中风险，发布前确认 |
| 消息 | `/im` | 高风险，发消息前确认 |
| APP | 展示 App 下载/打开二维码 | 低风险 |
| 反馈 | `/feedback?from=当前路径` | 中风险，提交前确认 |
| 客服 | 跳外部客服页 | 中风险，可能涉及账号问题 |
| 回顶部 | 当前页滚动回顶部 | 低风险 |
| 商品码 | 商品页展示商品二维码 | 低风险 |
| 个人码 | 个人页展示个人二维码 | 低风险 |

客服外链：

- `https://alimebot.goofish.com/intl/index.htm?from=wkbRssQuvW`
- 未登录时可能先要求登录。
- 涉及账号、售后、纠纷时，不自动提交任何内容。

### robots.txt 受限路径

当前 `robots.txt` 明确列出：

- `Disallow: /find-account`
- `Disallow: /select-account`
- `Disallow: /playground`

结论：

- 这些不是常规业务探索目标。
- 只记录它们存在，不做深度访问和自动化。
- 如果未来业务确实需要账号找回或账号选择，应让用户本人在前台完成。

### 路由发现结论

主站目前可以先按四类理解：

1. 公开浏览链路：`/`、`/search`、`/mach-feeds`、`/item`、`/changelog`。
2. 登录后个人链路：`/personal`、`/collection`、`/bought`、`/order-detail`、`/account`。
3. 交易/沟通链路：`/im`、`/publish`、`/create-order`、`/pay-success`、`/feedback`。
4. 内部/受限链路：`/find-account`、`/select-account`、`/playground`。

自动化优先级：

- 第一优先：公开浏览链路和只读个人链路。
- 第二优先：发布草稿、反馈草稿、消息草稿。
- 第三优先：交易、支付、售后、安全设置，只能做到打开和提醒，不能自动确认。
