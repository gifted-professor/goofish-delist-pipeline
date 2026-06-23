# 闲鱼页面理解总索引

日期：2026-06-22  
用途：作为当前所有闲鱼页面理解文档的总入口。先从这里判断该看哪份文档，再进入页面地图、路由、层级、控件、状态、接口、任务流或动作门禁。  
边界：本索引只组织结构和查阅路径；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

## 当前文档组

| 文档 | 作用 | 最适合回答的问题 |
| --- | --- | --- |
| `goofish-readme-first.md` | 最短入口 | “这么多文档我先看哪几个？” |
| `goofish-page-map.md` | 完整长笔记 | “这个站到底有哪些页面和发现过程？” |
| `goofish-closeout-summary.md` | 本轮收尾摘要 | “现在已经懂到什么程度，下一步怎么继续，商品想要/浏览数怎么看？” |
| `goofish-completion-audit.md` | 完成度审计 | “哪些已经证明，哪些不能证明，为什么不能标全站全状态完成？” |
| `goofish-item-metrics-readiness.md` | 自发布商品指标读取说明 | “自己发布商品的想要/浏览数从哪里看，怎么安全记录？” |
| `goofish-route-risk-cheatsheet.md` | 最短速查表 | “我要快速判断这个页面能不能操作。” |
| `goofish-page-ontology.json` | 机器可读统一页面画像 | “我要一次拿到每页的覆盖、流转、动作门禁、状态预期和停止点。” |
| `goofish-page-ontology-guide.md` | 人工统一页面画像读法 | “我该怎么读页面画像，按什么顺序判断风险？” |
| `goofish-page-dossiers.md` | 人工逐页档案 | “每个页面到底是什么、打开看什么、怎么判定看懂、哪里必须停？” |
| `goofish-page-dossier-index.json` | 机器可读逐页档案索引 | “我要让脚本定位逐页档案锚点和档案摘要。” |
| `goofish-page-classifier-rules.json` | 机器可读页面分类器 | “遇到陌生 URL/hash/灰度页时，如何归类到页面族和风险动作？” |
| `goofish-route-context-catalog.json` | 机器可读路由参数与上下文目录 | “这个 URL/hash 能不能直接打开，参数值该怎么处理？” |
| `goofish-route-context-catalog.md` | 路由参数与上下文手册 | “带订单、商品、用户、会话、站点、跳转参数时怎么判断？” |
| `goofish-page-change-sentinel.json` | 机器可读页面变更哨兵 | “页面改版、灰度、权限变化时，哪些变化可接受，哪些必须停？” |
| `goofish-page-change-sentinel.md` | 页面变更哨兵手册 | “页面锚点、参数、控件、弹窗变了以后怎么判断风险？” |
| `goofish-visible-label-lexicon.json` | 机器可读可见文案词典 | “看到中文按钮、字段、tab 或状态词时怎么归类风险？” |
| `goofish-visible-label-lexicon.md` | 可见文案词典手册 | “发布、保存、导出、退款、验证码、无权限等词该怎么处理？” |
| `goofish-unknown-page-triage.md` | 未知页面分类手册 | “不在 66 个已知页面里的页面，怎样安全观察和收口？” |
| `goofish-safe-dom-observation-schema.json` | 机器可读 DOM 观察规范 | “浏览器实际打开页面后，脚本能采哪些 DOM 结构、哪些必须丢弃？” |
| `goofish-safe-dom-observation-guide.md` | 人工 DOM 观察手册 | “人工巡检页面时，字段名、按钮名、表头、状态类别怎么采才安全？” |
| `goofish-probe-batch-matrix.json` | 机器可读巡检批次矩阵 | “一个登录 Profile 下，页面按什么批次和顺序安全巡检？” |
| `goofish-probe-batch-runbook.md` | 人工巡检批次手册 | “B0-B7 每批看哪些页面、采什么、哪里停？” |
| `goofish-page-verification-checklist.json` | 机器可读逐页验证清单 | “下一次巡检 66 个页面时，每页怎样算验证通过？” |
| `goofish-page-verification-checklist.md` | 人工逐页验证清单 | “按 D1-D6 分组，每页要等什么、记什么、停什么？” |
| `goofish-account-profile-probe-template.json` | 账号/Profile 巡检模板 | “换一个账号或浏览器 Profile 后，按什么任务批次重新只读检查？” |
| `goofish-account-profile-probe-runbook.md` | 多账号/Profile 巡检说明 | “多个账号怎样轮换，又不交出密钥、cookie 或验证码？” |
| `goofish-cross-profile-coverage-ledger.json` | 机器可读跨 Profile 覆盖台账 | “多个账号/Profile 的页面覆盖、权限和状态差异怎么统一记录？” |
| `goofish-cross-profile-coverage-runbook.md` | 跨 Profile 覆盖对比手册 | “不同账号看到的页面菜单、空态、权限和停止原因怎么比较？” |
| `goofish-observation-result-ledger.json` | 机器可读观察结果台账 | “每次跑页面后，怎么只保存类别化结果、停止原因和隐私检查？” |
| `goofish-observation-result-runbook.md` | 观察结果登记手册 | “登录一个 Profile 后，页面跑没跑、为什么停、能不能算覆盖怎么记？” |
| `goofish-page-manifest.json` | 机器可读页面清单 | “我要让脚本读取所有已识别页面、锚点和停止点。” |
| `goofish-probe-policy.json` | 机器可读探测策略 | “我要让脚本按页面族、证据和状态自动套安全规则。” |
| `goofish-login-session-smoke-test.md` | 登录会话冒烟观察 | “先登录一个账号后，主站/订单/卖家工作台能看到什么状态？” |
| `goofish-live-coverage-matrix.md` | 登录后 Live 覆盖矩阵 | “当前 Profile 下哪些主站/卖家页面实测可进入，控件密度和停止点是什么？” |
| `goofish-live-coverage-status.json` | 机器可读 Live 覆盖状态 | “manifest 里的 66 个页面分别是已实测、需上下文、静态还是容器边界？” |
| `goofish-coverage-gap-register.md` | 覆盖缺口登记 | “哪些页面不能为了补覆盖而强行打开，下一步该怎么处理？” |
| `goofish-page-deepening-queue.json` | 机器可读页面深化队列 | “66 个页面下一步分别该按 D1-D6 哪种方式继续观察？” |
| `goofish-page-deepening-queue.md` | 人工页面深化队列 | “下一轮先看高风险页、表单页、公开页，还是等用户上下文？” |
| `goofish-page-transition-graph.json` | 机器可读页面流转图 | “页面之间哪些跳转能只读、哪些需要上下文、哪些必须停？” |
| `goofish-page-transition-graph.md` | 人工页面流转图 | “主站/卖家工作台从一个页面到另一个页面时该怎么判断风险？” |
| `goofish-action-gate-rules.json` | 机器可读动作门禁规则 | “脚本看到按钮、控件或接口词时怎么判 G0-G4？” |
| `goofish-action-execution-guard.md` | 动作执行防护说明 | “人看到保存、发送、导出、支付、退款等动作时怎么判断能不能点？” |
| `goofish-state-modal-rules.json` | 机器可读状态弹窗规则 | “脚本看到 loading、空态、登录、二维码、确认弹窗时怎么判 S0-S10？” |
| `goofish-state-modal-handling.md` | 状态弹窗处理手册 | “人看到页面状态或弹窗时，下一步该等、读、关还是停？” |
| `goofish-page-readiness-matrix.md` | 逐页统一矩阵 | “这个页面现在理解到什么程度，首要停止点是什么？” |
| `goofish-site-taxonomy.md` | 站点层级和页面家族 | “这个页面属于主站、卖家工作台、门禁还是容器？” |
| `goofish-www-operational-map.md` | 主站操作图谱 | “主站每个页面能读什么、哪里必须停？” |
| `goofish-seller-workbench-operational-map.md` | 卖家工作台操作图谱 | “卖家后台每个菜单能读什么、哪里必须停？” |
| `goofish-route-inventory.md` | URL/hash 路由索引 | “看到一个 URL 或 hash，它是哪类页面？” |
| `goofish-navigation-selector-guide.md` | 导航和定位指南 | “从哪里进、页面加载好了看什么锚点？” |
| `goofish-safe-probe-protocol.md` | 安全页面探测规程 | “脚本逐页巡检时每一步该等什么、读什么、停什么？” |
| `goofish-ui-control-inventory.md` | 控件清单 | “这个页面有哪些 tab、筛选、输入框、表格、弹窗？” |
| `goofish-page-state-modal-inventory.md` | 状态和弹窗清单 | “加载、空态、无权限、二维码、确认弹窗怎么处理？” |
| `goofish-page-field-inventory.md` | 字段敏感度 | “哪些字段能记录，哪些只能脱敏，哪些不能写？” |
| `goofish-page-api-crosswalk.md` | 页面到接口能力对照 | “页面背后牵到哪些读取/写入/高风险接口？” |
| `goofish-static-api-audit.md` | 静态接口审计 | “本地前端包里暴露了哪些 mtop 接口和风险组？” |
| `goofish-static-signal-matrix.md` | 静态页面信号矩阵 | “看到 Page 名、失败码、H5 或 deep link 是什么意思？” |
| `goofish-action-gate-matrix.md` | 动作门禁矩阵 | “这个按钮/动作词能不能点？” |
| `goofish-task-workflow-runbook.md` | 任务流与停止点 | “搜索、下单前确认、发布、售后、财务这些任务怎么拆？” |
| `goofish-evidence-coverage.md` | 证据覆盖清单 | “哪些是实测，哪些只是静态确认，哪些不应该触发？” |

## 推荐查阅顺序

### 看到一个 URL/hash

1. 查 `goofish-route-inventory.md` 判断它是哪类页面。
2. 查 `goofish-route-context-catalog.md` 判断是否带参数、能否直接开、是否需要用户上下文。
3. 若页面结构、参数、控件或弹窗和旧理解不同，查 `goofish-page-change-sentinel.md` 判断是可接受漂移、需复核还是必须停。
4. 若页面上出现按钮、字段、tab、弹窗或状态词，查 `goofish-visible-label-lexicon.md` 判断控件、动作、字段和状态风险。
5. 若没有命中已知页面，查 `goofish-unknown-page-triage.md` 和 `goofish-page-classifier-rules.json` 先分类再决定是否继续。
6. 查 `goofish-page-ontology.json` 一次拿到覆盖、流转、动作门禁、状态预期和停止点。
7. 查 `goofish-page-dossiers.md` 看该页面的人工逐页说明。
8. 查 `goofish-site-taxonomy.md` 放回主站/卖家/门禁/容器层。
9. 查 `goofish-page-transition-graph.md` 判断从当前页到下一页属于安全只读、需上下文还是必须停。
10. 查 `goofish-page-readiness-matrix.md` 看证据、锚点、可读内容和停止点。
11. 查 `goofish-action-gate-matrix.md` 决定能否继续。

### 要做一个任务

1. 查 `goofish-task-workflow-runbook.md` 找任务路径。
2. 查 `goofish-ui-control-inventory.md` 判断页面上会遇到哪些控件。
3. 查 `goofish-state-modal-rules.json` 和 `goofish-page-state-modal-inventory.md` 判断当前是否加载、空态、登录失效、无权限或弹窗。
4. 查 `goofish-page-field-inventory.md` 确认输出时能写什么。
5. 若出现接口、按钮、失败码、H5 承接页、deep link 或高风险词，再查 `goofish-page-api-crosswalk.md`、`goofish-static-signal-matrix.md` 和 `goofish-action-gate-matrix.md`。

### 要写自动化规则

1. 先读 `goofish-page-ontology.json`，获得每页的统一画像。
2. 再读 `goofish-page-classifier-rules.json`，处理未知 URL/hash、参数风险和 DOM 锚点分类。
3. 再读 `goofish-route-context-catalog.json`，确定每页入口方式、参数风险、上下文来源和缺上下文处理。
4. 再读 `goofish-page-change-sentinel.json`，确定页面结构变化、灰度变化、参数变化和控件变化的收口规则。
5. 再读 `goofish-visible-label-lexicon.json`，把中文按钮、字段、tab、状态词映射到控件、动作、字段和状态风险。
6. 再读 `goofish-safe-dom-observation-schema.json`，确定 DOM 观察输出字段、脱敏规则和停止触发器。
7. 再读 `goofish-probe-batch-matrix.json`，确定 B0-B7 的执行顺序、进入条件和停止边界。
8. 再读 `goofish-page-dossier-index.json`，获得逐页档案锚点、摘要和快速定位信息。
9. 再读 `goofish-page-verification-checklist.json`，确定每页怎样算本轮验证通过。
10. 若是账号/Profile 轮换，读 `goofish-account-profile-probe-template.json`，按 D3、D2、D1、D4、D5、D6 批次执行。
11. 若要比较多个账号/Profile 的覆盖差异，读 `goofish-cross-profile-coverage-ledger.json` 和 `goofish-cross-profile-coverage-runbook.md`，只记录槽位、Profile 别名、页面状态类别和差异类别。
12. 再读 `goofish-probe-policy.json`，按页面族、证据等级和状态套安全策略。
13. 必要时读 `goofish-page-manifest.json` 获得更原始的页面 id、路由、层级、锚点和停止点。
14. 再读 `goofish-page-deepening-queue.json`，确定每页属于 D1-D6 哪个下一步队列。
15. 再读 `goofish-page-transition-graph.json`，确定页面间流转属于 `SAFE_READ`、`READ_WITH_REDACTION`、`REQUIRES_USER_CONTEXT`、`STOP_BEFORE_ACTION`、`STATIC_ONLY` 还是 `SHELL_ONLY`。
16. 用 `goofish-safe-probe-protocol.md` 确定 P0-P8 探测顺序。
17. 再用 `goofish-page-readiness-matrix.md` 确定页面是否 R0/R1/R2/R3/R4/R5。
18. 用 `goofish-navigation-selector-guide.md` 找稳定锚点和等待方式。
19. 用 `goofish-ui-control-inventory.md` 识别控件类别 C0/C1/C2/C3/C4。
20. 用 `goofish-page-api-crosswalk.md` 确认背后接口是否牵到写入、交易、消息、财务或权限。
21. 用 `goofish-static-signal-matrix.md` 处理 `Page_*`、SPM、失败码、H5 承接和 deep link。
22. 用 `goofish-evidence-coverage.md` 排除 Static Only、Deep/Param、Boundary Only 的危险触发。

### 要判断能不能记录内容

1. 查 `goofish-page-field-inventory.md` 的 F0-F4。
2. 查 `goofish-page-state-modal-inventory.md` 判断是正常内容、空态、弹窗还是高风险业务态。
3. 查 `goofish-task-workflow-runbook.md` 看该字段属于哪个任务。
4. 默认只写字段名、按钮名、tab、表头、状态类别和风险等级。

## 快速路径

| 需求 | 先看 | 再看 | 最后看 |
| --- | --- | --- | --- |
| 统一页面画像 | `goofish-page-ontology-guide.md` | `goofish-page-ontology.json` | `goofish-probe-policy.json` |
| 逐页人工理解 | `goofish-page-dossiers.md` | `goofish-page-dossier-index.json` | `goofish-page-verification-checklist.md` |
| 未知/灰度页面 | `goofish-unknown-page-triage.md` | `goofish-page-classifier-rules.json` | `goofish-coverage-gap-register.md` |
| 路由参数/上下文判断 | `goofish-route-context-catalog.md` | `goofish-route-context-catalog.json` | `goofish-page-classifier-rules.json` |
| 页面改版/灰度变化 | `goofish-page-change-sentinel.md` | `goofish-page-change-sentinel.json` | `goofish-unknown-page-triage.md` |
| 中文文案/按钮判断 | `goofish-visible-label-lexicon.md` | `goofish-visible-label-lexicon.json` | `goofish-action-gate-rules.json` |
| DOM 结构观察 | `goofish-safe-dom-observation-guide.md` | `goofish-safe-dom-observation-schema.json` | `goofish-ui-control-inventory.md` |
| Profile 巡检批次 | `goofish-probe-batch-runbook.md` | `goofish-probe-batch-matrix.json` | `goofish-account-profile-probe-template.json` |
| 逐页验证通过 | `goofish-page-verification-checklist.md` | `goofish-page-verification-checklist.json` | `goofish-safe-probe-protocol.md` |
| 多账号/Profile 轮换 | `goofish-account-profile-probe-runbook.md` | `goofish-account-profile-probe-template.json` | `goofish-page-verification-checklist.json` |
| 多 Profile 覆盖对比 | `goofish-cross-profile-coverage-runbook.md` | `goofish-cross-profile-coverage-ledger.json` | `goofish-probe-batch-matrix.json` |
| 观察结果落账 | `goofish-observation-result-runbook.md` | `goofish-observation-result-ledger.json` | `goofish-probe-policy.json` |
| 自发布商品指标 | `goofish-item-metrics-readiness.md` | `goofish-closeout-summary.md` | `goofish-action-gate-rules.json` |
| 搜索/找货 | `goofish-task-workflow-runbook.md` | `goofish-ui-control-inventory.md` | `goofish-action-gate-matrix.md` |
| 只读页面巡检 | `goofish-safe-probe-protocol.md` | `goofish-navigation-selector-guide.md` | `goofish-page-state-modal-inventory.md` |
| 页面状态/弹窗判断 | `goofish-state-modal-rules.json` | `goofish-state-modal-handling.md` | `goofish-page-state-modal-inventory.md` |
| 主站巡检 | `goofish-www-operational-map.md` | `goofish-page-api-crosswalk.md` | `goofish-action-gate-matrix.md` |
| 登录后覆盖检查 | `goofish-live-coverage-matrix.md` | `goofish-login-session-smoke-test.md` | `goofish-action-gate-matrix.md` |
| 看商品详情 | `goofish-page-readiness-matrix.md` | `goofish-page-field-inventory.md` | `goofish-action-gate-matrix.md` |
| 收藏/联系 | `goofish-task-workflow-runbook.md` | `goofish-page-api-crosswalk.md` | `goofish-action-gate-matrix.md` |
| 下单前核对 | `goofish-page-readiness-matrix.md` | `goofish-page-state-modal-inventory.md` | `goofish-action-gate-matrix.md` |
| 发布草稿 | `goofish-task-workflow-runbook.md` | `goofish-ui-control-inventory.md` | `goofish-page-field-inventory.md` |
| 看买家订单 | `goofish-route-inventory.md` | `goofish-page-field-inventory.md` | `goofish-action-gate-matrix.md` |
| 卖家订单/售后 | `goofish-site-taxonomy.md` | `goofish-page-readiness-matrix.md` | `goofish-action-gate-matrix.md` |
| 财务/发票 | `goofish-page-field-inventory.md` | `goofish-page-api-crosswalk.md` | `goofish-action-gate-matrix.md` |
| 子账号/客服分流 | `goofish-site-taxonomy.md` | `goofish-ui-control-inventory.md` | `goofish-action-gate-matrix.md` |
| 卖家工作台巡检 | `goofish-seller-workbench-operational-map.md` | `goofish-page-api-crosswalk.md` | `goofish-action-gate-matrix.md` |
| 登录/多账号 | `goofish-login-session-smoke-test.md` | `goofish-task-workflow-runbook.md` | `goofish-page-state-modal-inventory.md` |
| 覆盖缺口判断 | `goofish-live-coverage-status.json` | `goofish-coverage-gap-register.md` | `goofish-evidence-coverage.md` |
| 完成度审计 | `goofish-completion-audit.md` | `goofish-closeout-summary.md` | `goofish-coverage-gap-register.md` |
| 下一轮页面深化 | `goofish-page-deepening-queue.md` | `goofish-page-deepening-queue.json` | `goofish-action-gate-matrix.md` |
| 页面间流转判断 | `goofish-page-transition-graph.md` | `goofish-page-transition-graph.json` | `goofish-action-gate-matrix.md` |
| 按钮/动作判定 | `goofish-action-gate-rules.json` | `goofish-action-execution-guard.md` | `goofish-action-gate-matrix.md` |

## 统一风险口径

| 维度 | 低风险 | 中间态 | 高风险 |
| --- | --- | --- | --- |
| 站点层级 | M0 公开发现 | M1/M2 登录只读或草稿 | M3/M4/M5/M6 交易、经营、门禁、容器 |
| 就绪等级 | R0/R1 只读 | R2 草稿辅助 | R3/R4/R5 确认、边界、外壳 |
| 控件层 | C0/C1 展示/筛选 | C2 草稿输入 | C3/C4 文件/提交/业务动作 |
| 字段层 | F0/F1 公共结构/公开商品 | F2 账号内列表 | F3/F4 交易经营/身份安全 |
| 动作层 | G0/G1 公开或登录只读 | G2 草稿辅助 | G3/G4 明确确认或禁止主动触发 |

## 当前强结论

- 主站公开浏览、搜索、频道、商品详情已能稳定按只读方式理解。
- 登录买家页、收藏、订单、账号、消息已能判断字段、控件、状态和停止点，但输出必须脱敏。
- 主站已按入口、页面族、接口能力、可记录字段和停止动作整理成操作图谱。
- 发布、反馈、IM、售后/申诉文本可以作为草稿辅助，不提交。
- 卖家工作台的数据、商品、交易、财务、账号、客服、安全、推广页面已能按菜单、hash、控件、表头和接口风险理解。
- 卖家工作台已按菜单入口、权限门禁、接口能力族和停止动作整理成操作图谱。
- 已登录会话冒烟观察确认：当前浏览器 Profile 可进入主站个人页、买家订单页和卖家工作台外壳，适合继续只读熟悉页面。
- 登录后 Live 覆盖矩阵已覆盖 12 个主站入口和 28 个卖家工作台入口，记录了页面态、控件密度和停止点。
- 66 个 manifest 页面已全部归类：40 个已 Live 只读观察，8 个需要用户上下文，16 个只能静态解释，2 个是 shell/container 边界。
- 66 个页面已全部进入 D1-D6 深化队列：18 个高风险 Live 页、14 个表单/外壳 Live 页、8 个低风险 Live 页、8 个需上下文页、16 个静态页、2 个容器边界页。
- 页面之间已整理成 7 张流转子图，统一标记 `SAFE_READ`、`READ_WITH_REDACTION`、`REQUIRES_USER_CONTEXT`、`STOP_BEFORE_ACTION`、`STATIC_ONLY` 和 `SHELL_ONLY`。
- 动作执行已整理成机器可读 G0-G4 规则，覆盖 21 个页面族、按钮文案、控件类型、接口词和页面状态升级条件。
- 页面状态已整理成机器可读 S0-S10 规则，覆盖 21 个页面族的 loading、空态、登录、门禁、二维码、确认弹窗、上传下载和高风险业务态。
- 66 个页面已合成统一页面画像，每页都能直接读到覆盖状态、深化队列、流转类别、动作门禁、状态预期、锚点和停止策略。
- 66 个页面已展开成人工逐页档案，每页都有“这页是什么、打开方式、等待锚点、可读结构、停止状态、停止点、通过证据和下一步熟悉方式”。
- 已生成未知页面分类器：66 个精确页面规则、22 个路由族规则、8 个参数风险规则、9 个 DOM 信号规则和 UNKNOWN_PAGE 兜底。
- 已生成路由参数与上下文目录：66 个页面全部标注入口方式、参数名、参数风险、可否直接打开、上下文来源和缺上下文处理。
- 已生成页面变更哨兵：66 个页面都有基线签名、监控层级、观察锚点、停止控件、停止状态和变更收口规则。
- 已生成可见文案词典：258 个唯一中文文案词条、11 个歧义词、6 条上下文升级规则和 21 个页面族匹配入口。
- 已生成安全 DOM 观察规范：66 个页面观察计划、5 层控件风险、7 条脱敏规则和 5 类停止触发器。
- 已生成 B0-B7 巡检批次矩阵：预检、低风险 Live、表单/外壳 Live、高风险脱敏 Live、需上下文、静态证据、外壳边界、未知页收口。
- 66 个页面已生成逐页验证清单，每页都有等待锚点、通过证据、可记录结构、停止状态和动作停止点。
- 已生成账号/Profile 巡检模板，可用于不同登录账号下重复只读验证；模板只放账号槽位和 Profile 别名，不保存登录材料。
- 已生成跨 Profile 覆盖台账：可比较多个账号/Profile 的页面覆盖、菜单可见性、权限状态、空态/有内容差异和停止原因；只记录槽位、Profile 别名和类别差异。
- 已生成观察结果台账：每页只登记运行状态、停止原因、控件/字段/动作类别和隐私检查，不保存真实页面值。
- 自己发布商品的“我发布的”列表卡片层未稳定暴露“想要/浏览数”；商品详情页只读状态下能看到相关信号，但详情页同时有编辑、下架、删除等管理入口，必须停在只读。
- 页面巡检已整理成 P0-P8 安全探测规程，可用于人工或脚本逐页只读检查。
- 脚本可优先用 `goofish-page-ontology.json` + `goofish-page-classifier-rules.json` + `goofish-route-context-catalog.json` + `goofish-page-change-sentinel.json` + `goofish-visible-label-lexicon.json` + `goofish-safe-dom-observation-schema.json` + `goofish-probe-batch-matrix.json` + `goofish-page-dossier-index.json` + `goofish-page-verification-checklist.json` + `goofish-cross-profile-coverage-ledger.json` + `goofish-probe-policy.json` 组合出每页探测计划。
- 工作台外壳、登录、站点选择、账号检查、无权限、iframe、下载、内部实验页已按容器/门禁处理。
- 页面背后的 200 个业务接口已经按搜索/首页、个人/收藏、商品/发布、交易/售后/物流/支付、IM/消息、数据/财务、账号/权限等风险组整理。
- 静态包中的 `Page_*`、SPM、失败码、H5 承接和 App deep link 已按页面族和停止点整理。

## 当前边界

- 不为了补全覆盖而触发真实支付、真实下单、确认收货、退款、赔付、发货、投诉举证、认证、账号找回、账号切换、发消息、导出、上传或内部实验。
- 不把 Static Only、Deep/Param、Shell/Container、Boundary Only 当成可自由操作页面。
- 不把 API 模块、静态资源、埋点字符串、第三方库字符串、二维码内容当成业务页面。
- “所有闲鱼页面”仍受当前账号、当前站点、当前权限和平台灰度限制；隐藏页和必须真实业务状态才能出现的页面只能作为缺口记录。

## 最小安全输出格式

```text
页面：<路由或 hash>
层级：M0-M6
证据：Live + Static / Static Only / Deep/Param / Shell / Boundary
就绪：R0-R5
控件：C0-C4
字段：F0-F4
动作：G0-G4
可读：字段名、tab、表头、按钮名、状态类别
停止点：上传 / 提交 / 发送 / 支付 / 发货 / 退款 / 导出 / 权限 / 认证
隐私：不记录账号、订单、地址、聊天、金额、商品标题、图片链接或登录材料
```

## 当前输出规模

- 主站与卖家工作台文档：37 份 Markdown + 18 份 JSON。
- 当前总行数：64509 行。
- 本索引是人工查阅第一入口；`goofish-page-ontology.json`、`goofish-page-classifier-rules.json`、`goofish-route-context-catalog.json`、`goofish-page-change-sentinel.json`、`goofish-visible-label-lexicon.json`、`goofish-safe-dom-observation-schema.json`、`goofish-probe-batch-matrix.json`、`goofish-page-dossier-index.json`、`goofish-page-verification-checklist.json`、`goofish-cross-profile-coverage-ledger.json` 和 `goofish-probe-policy.json` 是脚本读取第一入口。

结论：遇到任何闲鱼页面或任务，先从本索引选查阅路径，再落到矩阵、层级、路由、控件、状态、字段、接口、动作门禁。这样可以把“看懂页面”和“安全不越界”保持在同一套口径里。
