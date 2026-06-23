# 闲鱼可见文案词典

日期：2026-06-22  
用途：把页面上看到的中文按钮、tab、字段名、状态词、弹窗词和任务词，映射到控件风险、动作门禁、字段敏感和页面状态。后续巡检时，先读文案，再按词典决定能否继续。  
边界：本词典只保存通用可见文案和类别；不保存真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容、cookie、token、localStorage 或 sessionStorage。

总索引：`goofish-master-index.md`  
配套机器词典：`goofish-visible-label-lexicon.json`  
配套动作规则：`goofish-action-gate-rules.json`  
配套状态规则：`goofish-state-modal-rules.json`  
配套控件清单：`goofish-ui-control-inventory.md`  
配套字段清单：`goofish-page-field-inventory.md`

## 总账

| 指标 | 数量 |
| --- | ---: |
| 文案组 | 12 |
| 唯一文案词条 | 258 |
| 原始组内词槽 | 269 |
| 歧义文案 | 11 |
| 上下文升级规则 | 6 |
| 页面族覆盖 | 21 |
| 默认停止组 | 6 |

## 判定顺序

1. read visible label only, not nearby private value
2. match exact label or substring to unique labelIndex
3. if ambiguous=true, keep candidateGroups and apply page family, DOM role, modal context and aliasRules
4. take the highest resulting controlRisk/actionGate/fieldRisk until context safely lowers it
5. persist only label and category when privacy check passes
6. unknown or unresolved labels use UNKNOWN_STOP and page-change/unknown-page triage

## 文案组

| 组 | 默认控件 | 默认动作 | 字段风险 | 状态 | 处理 | 示例文案 |
| --- | --- | --- | --- | --- | --- | --- |
| `navigation-display` | `C0_DISPLAY_NAV` | `G0` | `F0` | 无 | 可记录按钮名、tab 名、入口类别和选中态；不读取入口后面的真实私有值。 | `首页`、`搜索`、`分类`、`频道`、`推荐`、`返回`、`关闭`、`取消`、`展开`、`收起`、`查看更多`、`上一页` 等 |
| `public-search-filter` | `C1_FILTER_READ` | `G0` | `F0` | 无 | 可读筛选字段名和选中态；搜索词、地区和价格只写类别，不保存具体值。 | `关键词`、`搜索框`、`搜索建议`、`筛选`、`排序`、`综合`、`最新`、`价格`、`价格区间`、`最低价`、`最高价`、`地区` 等 |
| `read-only-detail` | `C0_DISPLAY_NAV` | `G1` | `F2` | 无 | 只记录字段名、状态类别、表头、模块名和按钮名；不记录行值、卡片值或身份值。 | `状态`、`详情`、`订单详情`、`物流记录`、`宝贝快照`、`商品详情`、`卖家信息`、`买家信息`、`保障`、`浏览`、`想要`、`收藏数` 等 |
| `draft-input` | `C2_DRAFT_INPUT` | `G2` | `F2` | 无 | 可以整理草稿、字段结构和校验类别；保存、提交、发送、发布前必须停。 | `标题`、`描述`、`正文`、`留言`、`备注`、`反馈内容`、`问题描述`、`模板名称`、`运费模板`、`规格`、`库存`、`数量` 等 |
| `file-external-bridge` | `C3_FILE_EXTERNAL` | `G3` | `F3` | 无 | 只记录文件/外部动作类别；上传、下载、导出、安装、打开客户端、扫码都要停。 | `上传`、`上传图片`、`上传视频`、`添加图片`、`添加附件`、`截图上传`、`下载`、`导出`、`历史下载`、`下载明细`、`下载报表`、`打开客户端` 等 |
| `account-login-gate` | `C4_BUSINESS_COMMIT` | `G4` | `F4` | `S4_LOGIN_EXPIRED/S5_PERMISSION_OR_IDENTITY_GATE` | 只记录门禁类型和按钮名；登录、验证码、切号、站点选择、账号检查由用户本人处理。 | `登录`、`扫码登录`、`短信登录`、`密码登录`、`验证码`、`安全验证`、`验证身份`、`实名认证`、`账号检查`、`继续前往`、`重新登录`、`登录其他账号` 等 |
| `confirm-modal` | `C4_BUSINESS_COMMIT` | `G3` | `F2` | `S7_CONFIRM_DIALOG` | 只读弹窗类别、取消按钮和确认动作类别；不点确认。 | `确定`、`确认`、`取消`、`关闭`、`我知道了`、`确认删除`、`确认保存`、`确认提交`、`确认发布`、`确认下架`、`确认取消`、`确认清空` 等 |
| `business-commit` | `C4_BUSINESS_COMMIT` | `G3` | `F3` | 无 | 可能改变账号、商品、消息、通知、规则或列表状态；需要动作级确认。 | `收藏`、`取消收藏`、`关注`、`取消关注`、`我想要`、`联系`、`聊一聊`、`发送`、`发消息`、`发送卡片`、`保存`、`提交` 等 |
| `high-risk-trade-finance` | `C4_BUSINESS_COMMIT` | `G4` | `F3/F4` | `S10_HIGH_RISK_BUSINESS_STATE` | 只解释字段和风险，不主动触发；涉及资金、履约、退款、申诉、权限、投放和主体资料。 | `立即购买`、`提交订单`、`立即支付`、`去支付`、`确认收货`、`延长收货`、`取消订单`、`关闭订单`、`申请退款`、`我要退款`、`同意退款`、`拒绝退款` 等 |
| `state-loading-empty-error` | `C0_DISPLAY_NAV` | `G1` | `F0` | `S1_LOADING/S2_EMPTY_STATE/S3_NETWORK_OR_API_FAILURE` | 记录状态类别和可见锚点；不为了补数据而创建订单、商品、会话或经营状态。 | `加载中`、`正在加载`、`刷新`、`重试`、`网络错误`、`请求失败`、`页面走丢了`、`暂无数据`、`暂无订单`、`暂无商品`、`暂无评价`、`暂无退款` 等 |
| `finance-data-metric` | `C0_DISPLAY_NAV` | `G1` | `F3` | 无 | 只记录指标字段名、图表模块名、表头和筛选项；不记录真实数值、金额或经营表现。 | `数据总览`、`商品数据`、`粉丝数据`、`客服数据`、`曝光`、`点击`、`浏览`、`成交`、`退款`、`转化`、`询单`、`下单` 等 |
| `unknown-label` | `UNKNOWN_CONTROL` | `UNKNOWN_STOP` | `UNKNOWN_FIELD` | 无 | 只记录文案类别和所在页面，不点击；先走未知页分类和页面变更哨兵。 | 无 |

## 歧义文案

| 文案 | 默认候选 | 其他候选 | 处理 |
| --- | --- | --- | --- |
| `备注` | `business-commit` | `draft-input` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `关闭` | `confirm-modal` | `navigation-display` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `浏览` | `finance-data-metric` | `read-only-detail` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `评价` | `high-risk-trade-finance` | `read-only-detail` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `取消` | `confirm-modal` | `navigation-display` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `详情` | `read-only-detail` | `navigation-display` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `信用` | `read-only-detail` | `public-search-filter` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `暂无订单` | `read-only-detail` | `state-loading-empty-error` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `暂无商品` | `read-only-detail` | `state-loading-empty-error` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `暂无数据` | `read-only-detail` | `state-loading-empty-error` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |
| `暂无消息` | `read-only-detail` | `state-loading-empty-error` | 未确认上下文前按更高风险候选处理；结合页面族、弹窗、操作列和 DOM role 再降级。 |

## 上下文升级规则

| 规则 | 触发 | 升级 | 处理 |
| --- | --- | --- | --- |
| `confirm-is-high-risk-in-modal` | label is 确定/确认 inside modal | `G3_OR_G4` | 弹窗确认按钮按后果分类，不按普通展示按钮处理。 |
| `operation-column-escalates` | label appears inside 操作 column on trade/finance/account pages | `G3_OR_G4` | 操作列只记录列名，具体按钮另行确认。 |
| `download-export-is-file-risk` | label contains 下载/导出/明细/报表 | `C3_FILE_EXTERNAL` | 停止在文件边界，不主动下载。 |
| `send-submit-save-publish-commit` | label contains 发送/提交/保存/发布 | `C4_BUSINESS_COMMIT` | 草稿可辅助，提交类动作必须停。 |
| `account-security-is-never-proactive` | label contains 登录/验证码/认证/权限/切换账号/站点 | `G4` | 用户本人处理，不保存登录材料。 |
| `private-row-value-drop` | label is field header but nearby text is row value | `F3_OR_F4_VALUE_DROPPED` | 保留表头或字段名，丢弃真实值。 |

## 页面族常用文案组

| 页面族 | 优先匹配文案组 |
| --- | --- |
| `public-discovery` | `navigation-display`、`public-search-filter`、`read-only-detail`、`state-loading-empty-error` |
| `item-detail` | `read-only-detail`、`business-commit`、`high-risk-trade-finance`、`file-external-bridge`、`state-loading-empty-error` |
| `public-profile` | `read-only-detail`、`business-commit`、`state-loading-empty-error` |
| `buyer-account` | `read-only-detail`、`account-login-gate`、`business-commit`、`state-loading-empty-error` |
| `buyer-trade` | `read-only-detail`、`high-risk-trade-finance`、`confirm-modal`、`state-loading-empty-error` |
| `draft-input` | `draft-input`、`file-external-bridge`、`confirm-modal`、`business-commit`、`state-loading-empty-error` |
| `message` | `draft-input`、`business-commit`、`file-external-bridge`、`state-loading-empty-error` |
| `identity` | `account-login-gate`、`confirm-modal` |
| `public-content` | `navigation-display`、`file-external-bridge`、`state-loading-empty-error` |
| `seller-data` | `finance-data-metric`、`public-search-filter`、`file-external-bridge`、`state-loading-empty-error` |
| `seller-item` | `draft-input`、`read-only-detail`、`business-commit`、`file-external-bridge`、`confirm-modal` |
| `seller-trade` | `read-only-detail`、`high-risk-trade-finance`、`confirm-modal`、`public-search-filter`、`state-loading-empty-error` |
| `seller-finance` | `finance-data-metric`、`file-external-bridge`、`high-risk-trade-finance`、`confirm-modal` |
| `seller-account` | `account-login-gate`、`read-only-detail`、`business-commit`、`high-risk-trade-finance`、`confirm-modal` |
| `seller-security` | `read-only-detail`、`high-risk-trade-finance`、`confirm-modal` |
| `seller-ad` | `finance-data-metric`、`high-risk-trade-finance`、`confirm-modal` |
| `seller-message` | `draft-input`、`business-commit`、`file-external-bridge`、`state-loading-empty-error` |
| `seller-gate` | `account-login-gate`、`confirm-modal` |
| `seller-shell` | `navigation-display`、`file-external-bridge`、`account-login-gate`、`state-loading-empty-error` |
| `internal-module` | `unknown-label` |
| `internal-test` | `unknown-label`、`high-risk-trade-finance` |

## 最小记录格式

```text
label: <visible generic label only>
groupId: <matched label group>
candidateGroups: <all possible groups when ambiguous>
controlRisk: C0-C4 or UNKNOWN_CONTROL
actionGate: G0-G4 or UNKNOWN_STOP
fieldRisk: F0-F4 or UNKNOWN_FIELD
stateCode: S0-S10 if applicable
decision: read-label / draft-only / stop-before-action / unknown-triage
privacy: no nearby private value, no concrete row/card/chat/order/account content
```

结论：这份词典把“看见一个中文按钮或字段”变成可执行判断。能读的只留结构，能写的只作草稿，上传/下载/提交/支付/退款/权限/登录类文案一律先停；歧义文案在上下文确认前按更高风险处理。
