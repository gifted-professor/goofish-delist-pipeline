# 闲鱼静态页面信号矩阵

日期：2026-06-22  
用途：把前端包里不是常规页面、但会影响页面理解的信号单独成册：页面埋点名、SPM 页面名、登录/风控失败码、H5 承接页、App deep link 和工作台深层 hash。  
边界：只记录信号类型、来源包、页面族和处理规则；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

总索引：`goofish-master-index.md`  
配套机器可读清单：`goofish-page-manifest.json`  
配套接口审计：`goofish-static-api-audit.md`  
配套状态弹窗：`goofish-page-state-modal-inventory.md`  
配套导航定位：`goofish-navigation-selector-guide.md`

## 抽取范围

- JS 文件：31 个。
- 页面埋点名：26 个 `Page_*`。
- SPM 页面名：24 个 `spmB`。
- 失败码：15 个 `FAIL_*`。
- H5 承接页：按页面族归并，不记录具体业务参数。
- App deep link：按能力归并，不拼参数、不主动打开。

## 页面埋点名到页面族

| 信号 | 来源包 | 页面族 | 处理 |
| --- | --- | --- | --- |
| `Page_xyPCHome` | `p_index.js` | 首页/推荐流 | 公开只读 |
| `Page_xyPCSearch` | `p_search-index.js` | 搜索结果 | 可改关键词、价格、排序 |
| `Page_xyPCMachFeeds` | `p_mach-feeds-index.js` | 频道/活动商品流 | 公开只读 |
| `Page_xyPCItem` | `p_item-index.js` | 商品详情 | 只读；收藏、联系、购买前停 |
| `Page_xyPCPersonal` | `p_personal-index.js` | 个人主页/当前账号主页 | 公开页只读；账号内页脱敏 |
| `Page_xyPCCollection` | `p_collection-index.js` | 收藏 | 登录只读；取消收藏/联系前停 |
| `Page_xyPCBought` | `p_bought-index.js` | 买家订单列表 | 登录只读；订单动作前停 |
| `Page_xyPCOrderDetail` | `p_order-detail-index.js` | 买家订单详情 | 只读字段名和状态类别 |
| `Page_xyPCCreateOrder` | `p_create-order-index.js` | 确认订单 | 下单前核对；提交/支付前停 |
| `Page_xyPCPaySuccess` | `p_pay-success-index.js` | 支付结果 | 只作为静态结果页理解 |
| `Page_xyPCPublish` | `p_publish-index.js` | 发布/编辑闲置 | 可写草稿；上传、保存、发布前停 |
| `Page_xyPCIM` | `p_im-index.js` | 消息 | 可看框架/拟草稿；读取私聊和发送前停 |
| `Page_xyPCAccount` | `p_account-index.js` | 账号与安全 | 只读模块；认证、切换、退出前停 |
| `Page_xyPCFeedback` | `p_feedback-index.js` | 用户反馈 | 可写草稿；上传/提交前停 |
| `Page_xyPCLogin` | `p_login-index.js` | 登录 | 用户本人扫码/验证码 |
| `Page_xyPCFindAccount` | `p_find-account-index.js` | 找回账号 | 只识别，不自动找回 |
| `Page_xyPCSelectAccount` | `p_select-account-index.js` | 选择账号 | 不自动切号；多账号走独立 Profile |
| `Page_xyPCCommonVideo` | `p_common-video-index.js` | 公共视频/活动页 | 只读；不主动播放、下载或抓视频 |
| `Page_xyPCUpgradeBrowser` | `p_upgrade-browser-index.js` | 浏览器升级提示 | 只读；不打开下载 |
| `Page_createOrderYhb` | `p_create-order-yhb-index.js` | 验货宝确认订单 | 只记录结构和风险；不触发下单 |
| `Page_xyPCYHBOrderDetail` | `p_order-detail-yhb-index.js` | 验货宝订单详情 | 只读报告/纠纷/评价能力；不触发售后 |
| `Page_xyPCSellerData` | `idle-seller-data-main.js` | 卖家数据总览 | 只读指标字段名；不记录真实数字 |
| `Page_xyPCSellerCommodity` | `idle-seller-data-main.js` | 卖家商品数据 | 只读筛选/表头；导出前停 |
| `Page_xyPCSellerCustomerService` | `idle-seller-data-main.js` | 卖家客服数据 | 只读表头/指标名；导出前停 |
| `Page_xyPCSellerMarketing` | `idle-seller-data-main.js` | 卖家营销/活动数据 | 只读结构；投放/活动动作前停 |
| `Page_xyPCSellerUser` | `idle-seller-data-main.js` | 卖家用户/粉丝画像 | 只读模块名；不记录真实画像数字 |

## SPM 页面名提示

| SPM | 对应页面 |
| --- | --- |
| `home` | 首页 |
| `search` | 搜索 |
| `mach-feeds` | 频道/活动商品流 |
| `item` | 商品详情 |
| `personal` | 个人主页 |
| `collection` | 收藏 |
| `bought` | 买家订单列表 |
| `order-detail` | 买家订单详情/验货宝订单详情 |
| `create-order` | 确认订单 |
| `createOrderYhb` | 验货宝确认订单 |
| `pay-success` | 支付结果 |
| `publish` | 发布/编辑 |
| `im` | 消息 |
| `account` | 账号与安全 |
| `feedback` | 反馈 |
| `login` | 登录 |
| `findAccount` | 找回账号 |
| `selectAccount` | 选择账号 |
| `common-video` | 公共视频 |
| `upgrade-browser` | 浏览器升级 |
| `pc_seller_data` | 卖家数据 |
| 数字型卖家 SPM | 卖家数据/商品/客服/营销子页，只作静态分组 |

## 失败码和页面含义

| 失败码 | 出现位置 | 页面含义 | 处理 |
| --- | --- | --- | --- |
| `FAIL_SYS_SESSION_EXPIRED` | 主站和工作台公共请求 | 登录态过期或续登失败 | 停下让用户本人登录 |
| `FAIL_SYS_ILLEGAL_ACCESS` | 主站和工作台公共请求 | 风控、权限或非法访问 | 停下，不重试撞风控 |
| `FAIL_SYS_TOKEN_EMPTY` | 主入口/工作台入口 | 登录或请求凭证缺失 | 停下，不构造凭证 |
| `FAIL_SYS_TOKEN_ILLEGAL` | 主入口/工作台入口 | 登录或请求凭证异常 | 停下，不替换凭证 |
| `FAIL_SYS_TRAFFIC_LIMIT` | 工作台 vendor | 访问频率/流量限制 | 降速或暂停 |
| `FAIL_SYS_HSF_ASYNC_TIMEOUT` | 工作台 vendor | 后端超时 | 可刷新一次，仍失败就记录异常 |
| `FAIL_BIZ_CAN_NOT_COLLECT_SELF_ITEM` | 商品/订单详情 | 不能收藏自己的商品 | 不作为错误重试 |
| `FAIL_BIZ_CROSS_BORDER_PC_CAN_NOT_SEE` | 商品详情 | PC 不可见/跨端限制 | 记录不可见，不绕端访问 |
| `FAIL_BIZ_ITEM_DEL_NOT_FOUND` | 商品详情 | 商品不存在或已删除 | 记录下架/不存在 |
| `FAIL_BIZ_ITEM_NOT_MULTI_SKU_ERROR` | 商品/订单/消息 | SKU 形态不匹配 | 不强开规格层 |
| `FAIL_BIZ_ZFB_NOT_BIND` | 确认订单/验货宝订单 | 支付账户未绑定 | 用户本人处理 |
| `FAIL_BIZ_YHB_ZFB_NOT_BIND` | 验货宝确认订单 | 验货宝支付账户未绑定 | 用户本人处理 |
| `FAIL_BIZ_STRONG_VALID_VERIFY_INFO` | 发布 | 强校验/认证信息不足 | 用户本人认证 |
| `FAIL_BIZ_USER_NOT_AUTH` | 发布 | 用户未认证 | 用户本人认证 |
| `FAIL_CODE` | 工作台 vendor | 泛化业务失败 | 按页面状态记录，不自动重放 |

## H5 承接页

| H5 承接族 | 来源页面 | 说明 | 停止点 |
| --- | --- | --- | --- |
| 个人设置/账号资料 | 账号、个人主页、订单相关页 | PC 页面会把资料编辑承接到 H5 | 不编辑资料、不提交 |
| 粉丝/关注列表 | 个人主页 | 关注、粉丝、访客关系承接 | 不关注、不批量抓取用户 |
| 收货地址列表/地址编辑 | 确认订单、验货宝确认订单 | 地址选择/编辑承接 | 不改地址、不提交订单 |
| 验货宝报告/鉴定订单 | 订单、商品、验货宝详情 | 报告和鉴定订单承接 | 只读结构，不触发纠纷/评价 |
| 安全中心 | 账号与安全 | 账号安全承接 | 用户本人处理 |
| 实名/强认证 | 内部实验、发布相关 | 认证流程承接 | 不代填、不代过风控 |
| 退款/逆向详情 | 卖家工作台 | 售后详情承接 | 不发起/同意/拒绝退款 |
| 帮助/文档页 | 顶部或客服入口 | 公共说明页 | 可只读 |
| `moyu-project` 基础容器 | 多页面公共桥 | App/H5 容器基座 | 不把容器当业务页 |

## App deep link

| deep link 族 | 典型形态 | 页面含义 | 处理 |
| --- | --- | --- | --- |
| 账号中心 | `fleamarket://account` | 打开 App 账号中心 | 用户本人处理 |
| 账号列表/订单列表 | `fleamarket://account_list_test...`、`fleamarket://SoldItems`、`fleamarket://BoughtItems` | App 内订单/账号列表 | 只识别，不自动切端 |
| 发布 | `fleamarket://publishentry`、`fleamarket://simple_post?draftId=...` | App 发布/草稿 | 不自动打开，不发布 |
| 商品详情 | `fleamarket://awesome_detail?id=...` | App 商品详情 | 不拼真实商品参数 |
| 规格层 | `fleamarket://sku_layer` | 规格选择/下单前层 | 不强开规格层 |
| 订单详情 | `fleamarket://order_detail...` | App 订单详情 | 不拼订单参数 |
| 聊天 | `fleamarket://x_chat?sid=...`、`fleamarket://custom_chat?sid=...` | App 聊天会话 | 不读取私聊、不发送 |
| 身份认证 | `fleamarket://identity_auth?flutter=true` | App 认证 | 用户本人处理 |

## 工作台深层 hash 信号

| hash 形态 | 来源包 | 含义 | 处理 |
| --- | --- | --- | --- |
| `#/seller-item/publish` | `idle-seller-data-main.js` | 卖家发布入口 | 草稿辅助；上传/保存/发布前停 |
| `#/seller-trade/order-manage/order-detail?orderId=...` | `seller-workbench-vendors.js` | 卖家订单详情 | 不拼真实订单号；只读字段名 |
| `#/seller-trade/refund-manage` | `seller-workbench-vendors.js` | 卖家售后管理 | 只读列表/状态；退款动作前停 |
| `#/im?itemId=...` | `seller-workbench-vendors.js` | 商品关联消息 | 不拼参数、不发送 |
| `#/account-check?userNick=...` | `seller-workbench-main.js`、`seller-workbench-vendors.js` | 账号检查/门禁 | 不拼真实账号名 |
| `#/login` | `seller-workbench-main.js` | 工作台登录 | 用户本人登录 |

## 自动化使用规则

1. 看到 `Page_*` 或 SPM 名，只能作为页面识别辅助，不能当作页面已加载完成的唯一证据。
2. 看到 `FAIL_SYS_SESSION_EXPIRED`、`FAIL_SYS_ILLEGAL_ACCESS`、`FAIL_SYS_TOKEN_EMPTY`、`FAIL_SYS_TOKEN_ILLEGAL`，立即转入登录/风控停顿点。
3. 看到 H5 承接页或 `fleamarket://`，先判断是否离开 PC 页面；涉及账号、地址、订单、聊天、认证、支付、售后时停止。
4. 看到带参数的 deep link 或 hash，只保留参数形态，不拼真实值。
5. 任何“页面信号”都必须再回查 `goofish-page-readiness-matrix.md` 和 `goofish-action-gate-matrix.md`，再决定能不能继续。

结论：这份矩阵补的是页面背后的静态信号层。它能解释“为什么页面跳到 H5/App、为什么登录失效、为什么发布/支付/认证被挡住”，但不扩大可操作边界。
