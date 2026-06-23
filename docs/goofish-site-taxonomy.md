# 闲鱼站点层级与页面家族

日期：2026-06-22  
用途：把闲鱼 PC 主站和卖家工作台按“站点层级、页面家族、父子关系、参数深度、风险边界”整理成一张总地图。  
边界：只记录页面类型、路由形态、入口关系、控件类别和风险；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接或登录材料。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于按页面 id、站点面、家族和层级读取站点树。
配套主地图：`goofish-page-map.md`  
配套主站操作图谱：`goofish-www-operational-map.md`  
配套卖家工作台操作图谱：`goofish-seller-workbench-operational-map.md`  
配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`  
配套路由索引：`goofish-route-inventory.md`  
配套导航定位：`goofish-navigation-selector-guide.md`  
配套控件清单：`goofish-ui-control-inventory.md`  
配套任务流手册：`goofish-task-workflow-runbook.md`  
配套状态清单：`goofish-page-state-modal-inventory.md`  
配套页面接口对照：`goofish-page-api-crosswalk.md`

## 总分层

| 层级 | 范围 | 代表页面 | 默认处理 |
| --- | --- | --- | --- |
| M0 公开发现层 | 不依赖账号的浏览、搜索、频道、商品公开详情 | `/`、`/search`、`/mach-feeds`、`/item`、`/common-video`、`/changelog`、`/upgrade-browser` | 可只读、搜索、筛选 |
| M1 登录买家层 | 当前账号相关列表、订单、收藏、账号、消息 | `/personal`、`/collection`、`/bought`、`/order-detail`、`/account`、`/im` | 只读脱敏 |
| M2 草稿/输入层 | 发布、反馈、IM 草稿、售后/申诉文本 | `/publish`、`/feedback`、`/im`、卖家发布/售后页 | 可写草稿，不提交 |
| M3 交易/资金层 | 下单、支付、订单状态、售后、物流、评价、投诉 | `/create-order`、`/pay-success`、`/order-detail`、卖家交易组 | 默认只读，动作前确认 |
| M4 卖家经营层 | 数据、商品、订单、财务、子账号、客服分流、安全、推广 | `seller.goofish.com` hash 页面 | 只读字段；导出/保存/投放前确认 |
| M5 身份/门禁层 | 登录、账号选择、找回、站点选择、账号检查、无权限、认证 | `/login`、`/find-account`、`#/select-site`、`#/account-check`、`#/no-permission` | 用户本人处理 |
| M6 容器/内部层 | iframe、下载、内部实验、API 模块、资源包 | `#/iframe`、`#/download`、`/playground`、`#/playground`、`/account/api` | 只识别，不主动触发 |

## 顶层站点树

```text
Goofish PC
├─ www.goofish.com
│  ├─ 公开发现
│  │  ├─ / 首页
│  │  ├─ /search 搜索结果
│  │  ├─ /mach-feeds 频道/活动商品流
│  │  ├─ /item 商品详情
│  │  ├─ /personal?userId=... 他人主页
│  │  ├─ /common-video 公共视频/活动页
│  │  ├─ /changelog 更新日志
│  │  └─ /upgrade-browser 浏览器升级提示
│  ├─ 登录买家
│  │  ├─ /personal 当前账号主页
│  │  ├─ /collection 收藏
│  │  ├─ /bought 买到的
│  │  ├─ /order-detail 买家订单详情
│  │  ├─ /create-order 确认订单
│  │  ├─ /pay-success 支付结果
│  │  ├─ /account 账号与安全
│  │  └─ /im 消息
│  ├─ 输入/草稿
│  │  ├─ /publish 发布/编辑闲置
│  │  └─ /feedback 用户反馈
│  ├─ 身份流程
│  │  ├─ /login 登录
│  │  ├─ /find-account 找回账号占位
│  │  ├─ /select-account 选择账号占位
│  │  └─ /login-validation 登录校验
│  └─ 内部/边界
│     ├─ /playground 内部实验
│     ├─ /account/api 账号 API 模块路径
│     └─ /common-video/layout 公共视频布局包路径
└─ seller.goofish.com
   ├─ 工作台外壳
   │  ├─ 左侧菜单
   │  ├─ 顶部下载/消息/通知/账号区
   │  └─ 站点/登录/权限门禁
   ├─ 数据组 seller-data
   ├─ 商品组 seller-item
   ├─ 交易组 seller-trade
   ├─ 财务组 seller-finance
   ├─ 账号/客服组 seller-account / im-cs-dispatch
   ├─ 安全/推广 seller-sc / seller-ad
   └─ 外壳容器 notification / im / iframe / download / playground
```

## 主站页面家族

| 家族 | 页面 | 父级/入口 | 子页面或下一跳 | 风险 |
| --- | --- | --- | --- | --- |
| 首页发现 | `/` | 直接打开 | `/search`、`/mach-feeds`、`/item`、工具条入口 | M0 |
| 搜索发现 | `/search?q=...` | 首页搜索框、搜索建议 | `/item`、地区/价格/标签筛选、分页 | M0，联系/收藏/购买前确认 |
| 频道流 | `/mach-feeds?machId=...` | 首页频道或主题入口 | `/item` | M0 |
| 商品详情 | `/item?id=...&categoryId=...` | 搜索/频道/推荐/收藏/订单推荐 | `/personal?userId=...`、`/im?itemId=...`、`/create-order?itemId=...` | 读详情 M0/M1，动作 M3 |
| 他人主页 | `/personal?userId=...` | 商品详情卖家卡、公开主页入口 | 公开商品列表、联系/关注 | M0/M1 |
| 当前主页 | `/personal` | 账号入口、我的闲鱼 | 发布宝贝列表、宝贝管理、编辑资料 | M1/M2 |
| 收藏 | `/collection` | 账号入口、侧边入口 | 商品详情、取消收藏、我想要 | M1/M3 |
| 买到的 | `/bought` | 账号/订单入口 | `/order-detail?orderId=...`、订单按钮 | M1/M3 |
| 买家订单详情 | `/order-detail?orderId=...` | 买到的订单卡 | 售后、物流、客服、评价、确认收货 | M3 |
| 确认订单 | `/create-order?itemId=...` | 商品详情立即购买 | 支付、地址管理、认证、支付结果 | M3/M5 |
| 支付结果 | `/pay-success?orderId=...&itemId=...` | 支付后结果 | 订单详情、推荐 | M3，只静态记录 |
| 发布 | `/publish`、`/publish?scene=...` | 侧边发闲置、个人页管理入口 | 图片/描述/价格/发货草稿、发布 | M2/M3 |
| 消息 | `/im`、`/im?itemId=...&peerUserId=...` | 商品详情、侧边消息、订单联系 | 会话、输入区、卡片/文件发送 | M1/M2/M3 |
| 账号与安全 | `/account` | 账号入口 | 通知、认证、安全中心、退出/切号 | M1/M5 |
| 反馈 | `/feedback?from=...` | 侧边反馈 | 文本草稿、截图上传、提交 | M2/M3 |
| 身份流程 | `/login`、`/find-account`、`/select-account`、`/login-validation` | 登录态失效、账号入口 | 扫码、验证码、找回、选择 | M5 |
| 内容边缘 | `/common-video`、`/changelog`、`/upgrade-browser` | 站内入口或静态路由 | 视频/日志/下载提示 | M0/M6 |
| 内部实验 | `/playground` | 静态发现 | 登录/认证/上传/支付测试 | M6，不访问 |

## 主站父子关系

| 父页面 | 子页面/动作 | 关系 | 停止点 |
| --- | --- | --- | --- |
| `/` | `/search` | 搜索框进入搜索结果 | 无 |
| `/` | `/mach-feeds` | 频道/主题进入商品流 | 无 |
| `/search`、`/mach-feeds` | `/item` | 商品卡进入详情 | 收藏/联系/购买前停 |
| `/item` | `/personal?userId=...` | 卖家卡进入他人主页 | 关注/联系前停 |
| `/item` | `/im?itemId=...` | 聊一聊进入商品关联会话 | 发送前停 |
| `/item` | `/create-order?itemId=...` | 购买进入确认订单 | 提交订单/支付前停 |
| `/bought` | `/order-detail?orderId=...` | 订单卡进入买家订单详情 | 订单状态动作前停 |
| `/create-order` | `/pay-success` | 支付完成后的结果页 | 不为测试触发 |
| `/personal` | `/publish?scene=...&itemId=...` | 当前账号宝贝管理/编辑线索 | 保存/发布前停 |
| `/feedback` | 截图上传/提交 | 草稿页进入提交动作 | 上传/提交前停 |
| `/account` | 登录/认证/安全相关流程 | 账号设置进入身份流程 | 用户本人处理 |

## 卖家工作台页面家族

| 家族 | Hash 页面 | 父级菜单 | 子页面或下一跳 | 风险 |
| --- | --- | --- | --- | --- |
| 数据组 | `#/seller-data/data` | 数据 | 商品数据、粉丝数据、客服数据 | M4，导出前确认 |
| 数据组 | `#/seller-data/commodity` | 数据 | 商品列表、下载、类目/指标 | M4 |
| 数据组 | `#/seller-data/fanData` | 数据 | 粉丝画像、地域/人群分布 | M4 |
| 数据组 | `#/seller-data/customerService` | 数据 | 咨询/满意度、客服明细、导出 | M4 |
| 商品组 | `#/seller-item/publish` | 商品 | 发布草稿、上传、保存/发布 | M2/M4 |
| 商品组 | `#/seller-item/goods-manage` | 商品 | 编辑、复制、改价、上下架、删除 | M4 |
| 商品组 | `#/seller-item/post-temple` | 商品 | 运费模板列表、创建 | M4 |
| 商品组 | `#/seller-item/post-temple/create` | 商品/运费模板 | 模板表单、区域弹窗、保存 | M4 |
| 交易组 | `#/seller-trade/order-manage` | 交易 | 卖家订单详情、发货、备注、联系 | M3/M4 |
| 交易组 | `#/seller-trade/order-manage/order-detail?orderId=...` | 订单管理 | 订单详情、物流、地址修改、售后 | M3/M4 |
| 交易组 | `#/seller-trade/refund-manage` | 交易 | 同意/拒绝退款、赔付、确认收货 | M3/M4 |
| 交易组 | `#/seller-trade/evaluation-manage` | 交易 | 评价、举报、联系 | M3/M4 |
| 交易组 | `#/seller-trade/complaint-manage` | 交易 | 投诉详情、举证、撤销、处理 | M3/M4 |
| 交易组 | `#/seller-trade/refund-address` | 交易 | 退货地址新增/编辑/删除 | M4 |
| 财务组 | `#/seller-finance/income-bill` | 财务 | 收入账单、导出/下载 | M4 |
| 财务组 | `#/seller-finance/expense-bill` | 财务 | 支出账单、导出/下载 | M4 |
| 财务组 | `#/seller-finance/invoice-apply` | 财务 | 申请发票、导出 | M4 |
| 财务组 | `#/seller-finance/basic-info` | 财务 | 主体资料编辑/保存 | M4/M5 |
| 账号/客服 | `#/seller-account/sub-account` | 小铺/账号 | 子账号、岗位、权限、分流 | M4/M5 |
| 账号/客服 | `#/im-cs-dispatch/customer-routing-service` | 客服分流 | 分组、规则、保存/启停 | M4/M5 |
| 安全/推广 | `#/seller-sc/home` | 安全中心 | 违规详情、申诉、处理 | M4 |
| 安全/推广 | `#/seller-ad/home` | 超级擦亮 | 投放指标、新建计划 | M4 |
| 通知消息 | `#/notification-center` | 顶部通知 | 通知详情、标已读/清未读 | M4 |
| 通知消息 | `#/im`、`#/im-desktop` | 顶部消息 | 会话、发送、下载客户端 | M3/M4/M6 |
| 外壳门禁 | `#/select-site`、`#/account-check`、`#/login`、`#/no-permission` | 顶部/门禁 | 站点切换、账号检查、登录、权限失败 | M5 |
| 容器内部 | `#/iframe`、`#/download`、`#/playground` | 外壳容器 | 外部页、下载、测试入口 | M6 |

## 卖家菜单树

```text
seller.goofish.com/?site=COMMONPRO
├─ 数据
│  ├─ #/seller-data/data 数据总览
│  ├─ #/seller-data/commodity 商品数据
│  ├─ #/seller-data/fanData 粉丝数据
│  └─ #/seller-data/customerService 客服数据
├─ 商品
│  ├─ #/seller-item/publish 商品发布
│  ├─ #/seller-item/goods-manage 商品管理
│  ├─ #/seller-item/post-temple 运费模板
│  └─ #/seller-item/post-temple/create 创建运费模板
├─ 交易
│  ├─ #/seller-trade/order-manage 订单管理
│  │  └─ #/seller-trade/order-manage/order-detail?orderId=... 卖家订单详情
│  ├─ #/seller-trade/refund-manage 退款管理
│  ├─ #/seller-trade/evaluation-manage 评价管理
│  ├─ #/seller-trade/complaint-manage 投诉管理
│  └─ #/seller-trade/refund-address 退货地址
├─ 财务
│  ├─ #/seller-finance/income-bill 收入账单
│  ├─ #/seller-finance/expense-bill 支出账单
│  ├─ #/seller-finance/invoice-apply 申请发票
│  └─ #/seller-finance/basic-info 基本/开票信息
├─ 账号/客服
│  ├─ #/seller-account/sub-account 子账号管理
│  └─ #/im-cs-dispatch/customer-routing-service 客服分流
├─ 安全/推广
│  ├─ #/seller-sc/home 安全中心
│  └─ #/seller-ad/home 超级擦亮
└─ 外壳
   ├─ #/notification-center 通知中心
   ├─ #/im 工作台消息
   ├─ #/im-desktop 桌面消息容器
   ├─ #/download 下载入口
   ├─ #/select-site 站点选择
   ├─ #/account-check 账号检查
   ├─ #/login 工作台登录
   ├─ #/no-permission 无权限
   ├─ #/iframe 外部 iframe 容器
   └─ #/playground 内部实验
```

## 参数深度分类

| 参数形态 | 页面 | 含义 | 处理 |
| --- | --- | --- | --- |
| `q=...` | `/search` | 搜索关键词 | 可改关键词，输出不写敏感词 |
| `machId=...&publishTimes=...` | `/mach-feeds` | 频道/活动流标识 | 只读商品流 |
| `id=...&categoryId=...` | `/item` | 商品详情 | 不记录商品 ID |
| `userId=...` | `/personal` | 他人主页 | 不记录用户 ID |
| `itemId=...` | `/create-order`、`/publish?...itemId=...` | 下单或编辑商品上下文 | 高风险，只读/确认 |
| `orderId=...` | `/order-detail`、`/pay-success`、卖家订单详情 | 订单上下文 | 不拼真实参数，不记录订单号 |
| `peerUserId=...` | `/im` | 会话对象 | 不主动读取或发送 |
| `from=...` | `/feedback` | 反馈来源页面 | 可用作路径线索 |
| `redirectURL=...` | `/login` | 登录回跳 | 不改登录参数 |
| `url=...` | `#/iframe` | 外部容器来源 | 来源明确后再判断 |
| `userNick=...` | `#/account-check` | 账号检查上下文 | 不拼真实账号名 |

## 不应当作页面的对象

| 对象 | 例子 | 原因 |
| --- | --- | --- |
| API 模块路径 | `/account/api`、`#/notification-center/api*` | 是模块或接口，不是业务页面 |
| 静态资源 | JS、CSS、字体、图片、安装包、remoteEntry | 只作为证据，不作为页面 |
| 埋点/事件字符串 | `xianyu.pc_*`、事件名、SPM 字符串 | 会污染路由抽取 |
| 第三方库字符串 | URL ponyfill、polyfill、组件库文案 | 不是业务入口 |
| 内部实验 | `/playground`、`#/playground` | 只静态识别，不进入测试 |
| 二维码内容 | 登录、认证、付款、APP 查看二维码 | 敏感且会变，只记录用途 |

## 查图顺序

1. 先看域名：主站 `www.goofish.com`，卖家工作台 `seller.goofish.com`。
2. 再看 path/hash 属于哪个页面家族。
3. 再看是否带商品、订单、用户、账号、地址、支付、物流、发票、iframe 参数。
4. 查 `goofish-ui-control-inventory.md` 判断页面控件。
5. 查 `goofish-page-state-modal-inventory.md` 判断加载、空态、登录、权限、弹窗。
6. 查 `goofish-page-api-crosswalk.md` 判断背后接口家族。
7. 查 `goofish-action-gate-matrix.md` 判断最终动作门禁。

结论：闲鱼 PC 页面不是一个平面列表，而是“公开发现 -> 详情 -> 登录买家/交易 -> 卖家经营 -> 身份门禁/容器内部”的层级结构。越靠近交易、售后、财务、消息、权限、认证和内部实验，越只能只读或停下确认。
