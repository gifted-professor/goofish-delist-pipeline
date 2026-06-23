# 闲鱼静态接口审计

日期：2026-06-22  
来源：当前工作区本地前端包静态抽取。只记录接口名和来源包，不调用接口，不记录账号、订单、地址、聊天、经营数据。

总索引：`goofish-master-index.md`，用于从当前所有页面理解文档中选择查阅路径。

配套机器可读清单：`goofish-page-manifest.json`，用于把静态接口风险回填到页面级条目。

配套逐页就绪矩阵：`goofish-page-readiness-matrix.md`，用于把接口风险放回每个页面的证据、层级和停止点中。

配套任务流手册：`goofish-task-workflow-runbook.md`，用于把接口风险放回具体买家/卖家任务路径和停止点中。

配套页面接口对照：`goofish-page-api-crosswalk.md`，用于把本审计中的接口按页面/路由归并，判断页面背后的读取和高风险能力。

配套静态信号矩阵：`goofish-static-signal-matrix.md`，用于查看页面埋点名、失败码、H5 承接页和 App deep link。

## 审计范围

- 扫描 JS 文件：31 个。
- 抽取到 mtop 名称：225 个。
- 排除运行时/配置类名称后，业务接口：200 个。
- 来源包包括 `main.js`、`p_layout.js`、`p_search-index.js`、`work/www-assets/full/*.js`、`work/seller-assets/*.js`。

## 总原则

- 这份表只说明页面包暴露的能力，不代表可以绕过页面直接调接口。
- 优先读页面可见状态；接口层只作为理解页面、识别风险和写自动化防线的依据。
- 任何会改变账号、交易、商品、消息、财务、权限、物流、售后状态的接口，都必须停下让用户确认。

## 搜索/首页（5）

公开浏览和搜索相关，默认只读；搜索关键词可执行，关注/收藏/联系前确认。

- `mtop.taobao.idlehome.home.webpc.feed`：p_index.js、p_mach-feeds-index.js、p_search-index.js
- `mtop.taobao.idlemtopsearch.pc.item.search.activate`：p_layout.js
- `mtop.taobao.idlemtopsearch.pc.search`：p_search-index.js
- `mtop.taobao.idlemtopsearch.pc.search.shade`：p_layout.js
- `mtop.taobao.idlemtopsearch.pc.search.suggest`：p_layout.js

## 个人/收藏（5）

包含个人主页、收藏、关注关系，读取结构可做；收藏/取消收藏/关注关系变更前确认。

- `mtop.idle.web.user.page.head`：p_account-index.js、p_collection-index.js、p_personal-index.js
- `mtop.idle.web.user.page.nav`：p_account-index.js、p_bought-index.js、p_collection-index.js、p_create-order-index.js、p_feedback-index.js、p_item-index.js、p_layout.js、p_pay-success-index.js、p_personal-index.js、p_playground-index.js、p_publish-index.js、p_search-index.js、seller-workbench-vendors.js
- `mtop.idle.web.user.panel.customer`：seller-workbench-vendors.js
- `mtop.taobao.idle.collect.item`：p_collection-index.js、p_item-index.js、p_order-detail-index.js、p_order-detail-yhb-index.js
- `mtop.taobao.idle.web.attention.relation`：p_account-index.js、p_collection-index.js、p_personal-index.js

## 商品/发布/服务（22）

包含发布、编辑、草稿、属性识别和服务卡；草稿可辅助，发布/编辑/下架/保存账号状态前确认。

- `mtop.alibaba.idle.seller.pc.datacompass.item.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.item.list.export`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.user.market.item.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.item.stats.query`：seller-workbench-vendors.js
- `mtop.alibaba.idle.seller.platform.datacompass.export.item.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.idle.category.query`：idle-seller-data-main.js
- `mtop.alibaba.idle.service.open`：p_publish-index.js、p_search-index.js
- `mtop.alibaba.idle.service.status.query`：p_publish-index.js、p_search-index.js
- `mtop.idle.idleitem.draft.edit`：p_publish-index.js、p_search-index.js
- `mtop.idle.idleitem.draft.publish`：p_publish-index.js、p_search-index.js
- `mtop.idle.item.publish.service.cards.list`：p_publish-index.js、p_search-index.js
- `mtop.idle.pc.idleitem.edit`：p_publish-index.js、p_search-index.js
- `mtop.idle.pc.idleitem.editDetail`：p_publish-index.js、p_search-index.js
- `mtop.idle.pc.idleitem.preget`：p_publish-index.js、p_search-index.js
- `mtop.idle.pc.idleitem.prepublish.check`：p_publish-index.js、p_search-index.js
- `mtop.idle.pc.idleitem.publish`：p_publish-index.js、p_search-index.js
- `mtop.idle.web.xyh.item.list`：p_account-index.js、p_collection-index.js、p_personal-index.js
- `mtop.taobao.idle.item.downshelf`：p_item-index.js
- `mtop.taobao.idle.kgraph.property.recommend`：p_publish-index.js、p_search-index.js
- `mtop.taobao.idle.kgraph.property.search`：p_publish-index.js、p_search-index.js
- `mtop.taobao.idle.web.favor.item.list`：p_account-index.js、p_collection-index.js、p_personal-index.js
- `mtop.taobao.idleitem.badwords.prepubcheck`：p_publish-index.js

## 交易/售后/物流/支付（71）

最高风险层，订单、支付、退款、投诉、发货、地址、赔付、评价都必须用户逐项确认。

- `mtop.alibaba.idle.autotrade.trade.data.update`：p_order-detail-index.js
- `mtop.alibaba.idle.merchant.autotrade.data.update`：seller-workbench-vendors.js
- `mtop.alibaba.idle.merchant.autotrade.trade.api`：seller-workbench-vendors.js
- `mtop.alibaba.idle.pc.yhb.order.create`：p_create-order-yhb-index.js
- `mtop.alibaba.idle.pc.yhb.order.create.render`：p_create-order-yhb-index.js
- `mtop.alibaba.idle.seller.pc.datacompass.refund.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.datacompass.refund.item.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.datacompass.refund.item.reason.detail`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.datacompass.refund.reason.detail`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.datacompass.refund.reason.item.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.datacompass.refund.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.merchant.delivery.address.list.query`：seller-workbench-vendors.js
- `mtop.cainiao.ld.detail.tradeid.ordercode.mailno.rescode.get.xy`：p_order-detail-index.js、seller-workbench-vendors.js
- `mtop.idle.alipay.verify.url.query`：seller-workbench-vendors.js
- `mtop.idle.merchant.order.address.modify.agree`：seller-workbench-vendors.js
- `mtop.idle.merchant.order.address.modify.refuse`：seller-workbench-vendors.js
- `mtop.idle.merchant.order.get.modify.address.info`：seller-workbench-vendors.js
- `mtop.idle.trade.pay.info.query`：p_create-order-index.js、p_create-order-yhb-index.js、p_pay-success-index.js
- `mtop.idle.web.trade.bought.list`：p_bought-index.js
- `mtop.idle.web.trade.order.detail`：p_order-detail-index.js
- `mtop.idle.web.trade.rate.list`：p_account-index.js、p_collection-index.js、p_personal-index.js
- `mtop.taobao.idle.cco.shop.complain.apply.revoke`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.detail`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.refuse`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.return.money.page`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.submit.active.proof`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.submit.passive.proof`：seller-workbench-vendors.js
- `mtop.taobao.idle.cco.shop.complain.submit.proof`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistic.address.list.query`：p_bought-index.js、p_create-order-index.js、p_create-order-yhb-index.js、p_order-detail-index.js、p_pay-success-index.js
- `mtop.taobao.idle.logistics.guess.mailno`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.consign.dummy`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.consign.offline`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.consign.page.render`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.consign.resend`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.excel.consign.offline`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.oss.sts.get`：seller-workbench-vendors.js
- `mtop.taobao.idle.logistics.merchant.oss.url.get`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.add.memo`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.compensate.service.detail.query`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.compensate.service.pay`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.compensate.service.refuse`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.compensate.service.refuse.render`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.dispute.create`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.dispute.create.page`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.postage.refund.detail.query`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.postage.refund.refuse`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.postage.refund.refuse.reason.query`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.rate.create`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.refund.agree.refund`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.refund.refuse`：seller-workbench-vendors.js
- `mtop.taobao.idle.merchant.refund.refuse.render`：seller-workbench-vendors.js
- `mtop.taobao.idle.pc.trade.appraise.order.perform`：p_order-detail-yhb-index.js
- `mtop.taobao.idle.pc.trade.full.info`：p_order-detail-yhb-index.js
- `mtop.taobao.idle.pc.yhb.dispute.apply.list`：p_order-detail-yhb-index.js
- `mtop.taobao.idle.trade.close.by.seller`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.common.sku.selector`：p_bought-index.js、p_im-index.js、p_item-index.js、p_order-detail-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.adjust.price.render`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.batch.delay.confirm`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.batch.remind.confirm`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.close.by.seller`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.order.close.reason.get`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.sold.get`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.merchant.user.adjust.price`：seller-workbench-vendors.js
- `mtop.taobao.idle.trade.order.cancel`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.order.close.reason.get`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.order.create`：p_bought-index.js、p_create-order-index.js、p_order-detail-index.js、p_pay-success-index.js
- `mtop.taobao.idle.trade.order.modify.price.render`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.order.render`：p_bought-index.js、p_create-order-index.js、p_order-detail-index.js、p_pay-success-index.js
- `mtop.taobao.idle.trade.seller.delay.confirm`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.trade.user.adjust.price`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.unconsign.detail`：p_order-detail-index.js

## IM/消息（46）

涉及会话、未读、黑名单、快捷回复、文件和消息发送；只读框架可以，发送/标记/关系变更前确认。

- `mtop.idle.trade.message.chat.tradeinfo`：p_im-index.js、seller-workbench-vendors.js
- `mtop.idle.trade.pc.message.headinfo`：p_im-index.js、seller-workbench-vendors.js
- `mtop.idle.trade.pc.message.headinfo.query`：seller-workbench-vendors.js
- `mtop.taobao.idle.shop.dispute.message.get.conversation`：seller-workbench-vendors.js
- `mtop.taobao.idle.shop.dispute.message.mark.read`：seller-workbench-vendors.js
- `mtop.taobao.idle.shop.dispute.message.query.history`：seller-workbench-vendors.js
- `mtop.taobao.idle.shop.dispute.message.query.unread.list`：seller-workbench-vendors.js
- `mtop.taobao.idle.shop.dispute.message.send`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.customer.deliver.session`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.customer.leave.session`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.customer.rejoin.session`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.customers.data.query`：idle-seller-data-main.js
- `mtop.taobao.idlemessage.customers.info.get`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.face.emoji.load`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.file.token.v1`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.instant.log`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.message.card.send`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.accs.token`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.blacklist.add`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.blacklist.query`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.blacklist.remove`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.file.entry.auth`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.login.query`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.login.token`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.loginuser.get`：p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.message.sync`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.profile.notice.query`：p_account-api.js、p_account-index.js
- `mtop.taobao.idlemessage.pc.profile.notice.update`：p_account-api.js、p_account-index.js
- `mtop.taobao.idlemessage.pc.redpoint.query`：p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.repect.status.edit`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.session.search`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.session.sync`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.session.unread.clean`：p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.systems.unread.clean`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.tool.item.search`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.tool.remark`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.pc.user.query`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.quickreply.content.operate`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.quickreply.group.operate`：seller-workbench-vendors.js
- `mtop.taobao.idlemessage.quickreply.list.get.v1`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.relation.message.read`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.tool.item.query`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.user.query`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.idlemessage.wx.login.token`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.wx.idlemessage.message.sync`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js
- `mtop.taobao.wx.idlemessage.session.sync`：p_account-index.js、p_im-index.js、p_layout.js、seller-workbench-vendors.js

## 数据/财务/经营分析（26）

可读字段和汇总结构；导出、下载、发票、经营数据明细前确认并脱敏。

- `mtop.alibaba.idle.seller.datacompass.get.begin.time`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.buyerprofile.buyer.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.buyerprofile.first.buyer.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.detail.export`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.detail.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.diversion.export`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.diversion.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.evaluation.export`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.evaluation.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.excel.url`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.overview.export`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.cs.overview.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.excel.url.get`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.fans.insights.query`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.fans.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.flow.detail`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.item.indicators`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.marketing.data.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.merchant.info.query`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.seller.activity.list`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.singleuser.browse.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.singleuser.item.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.singleuser.repurchase.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.datacompass.singleuser.seller.summary`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.pc.shop.stats.query`：seller-workbench-vendors.js
- `mtop.alibaba.idle.seller.platform.query.login.merchant.info`：idle-seller-data-main.js、seller-workbench-main.js

## 账号/权限/风控（10）

涉及登录、身份、子账号、备注、风控；只读判断可做，认证/权限/切号/备注修改前确认。

- `mtop.alibaba.idle.seller.platform.account.mock.apply`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.account.mock.cancel`：idle-seller-data-main.js
- `mtop.alibaba.idle.seller.platform.sys.usergroup.member.list`：seller-workbench-main.js
- `mtop.alibaba.idle.seller.platform.user.business.identity.get`：seller-workbench-main.js
- `mtop.alibaba.idle.seller.platform.user.remark.update`：seller-workbench-main.js
- `mtop.alibaba.idle.seller.platform.usergroup.member.list`：idle-seller-data-main.js
- `mtop.idle.user.account.sub.nav`：seller-workbench-main.js
- `mtop.idle.user.account.sub.test`：p_playground-index.js
- `mtop.idle.web.user.page.account`：p_account-index.js、p_collection-index.js、p_personal-index.js
- `mtop.taobao.idle.mtee.risk.get`：p_bought-index.js、p_im-index.js、p_order-detail-index.js、p_pay-success-index.js、seller-workbench-vendors.js

## 其他/基础能力（15）

多为内容、配置、视频、智能表单或基础查询；按入口页面风险继承处理。

- `mtop.alibaba.idle.pc.galaxy.report.detail`：p_order-detail-yhb-index.js
- `mtop.alibaba.idle.seller.platform.sys.menu.query`：seller-workbench-main.js
- `mtop.gaia.nodejs.gaia.idle.data.gw.v2.index.get`：p_common-video-index.js、p_common-video-layout.js、p_im-index.js、p_index.js、p_layout.js、p_mach-feeds-index.js、seller-workbench-vendors.js
- `mtop.idle.cloud.video.query`：p_item-index.js
- `mtop.taobao.heracles.inno.interactive.voice.change`：p_im-index.js、seller-workbench-vendors.js
- `mtop.taobao.idle.bpro.marketing.info.enhance.query.pc`：idle-seller-data-main.js
- `mtop.taobao.idle.cat.configs`：p_item-index.js、p_order-detail-index.js、p_order-detail-yhb-index.js
- `mtop.taobao.idle.division.all.get`：p_search-index.js
- `mtop.taobao.idle.filter.hitnum.pc.get`：p_search-index.js
- `mtop.taobao.idle.item.web.recommend.list`：p_item-index.js、p_order-detail-index.js、p_order-detail-yhb-index.js、p_pay-success-index.js
- `mtop.taobao.idle.local.poi.get`：p_publish-index.js、p_search-index.js
- `mtop.taobao.idle.merchant.biz.jfzz.transfer`：seller-workbench-vendors.js
- `mtop.taobao.idle.pc.detail`：p_item-index.js、p_order-detail-index.js、p_order-detail-yhb-index.js
- `mtop.taobao.merchant.heracles.inno.smart.form.callback`：seller-workbench-vendors.js
- `mtop.taobao.merchant.heracles.inno.smart.form.query`：seller-workbench-vendors.js
