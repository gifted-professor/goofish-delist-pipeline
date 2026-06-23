# 闲鱼统一页面画像读法

日期：2026-06-22  
用途：解释 `goofish-page-ontology.json` 的使用方式。它把页面清单、登录后覆盖、深化队列、页面流转、动作门禁和状态弹窗合成一个逐页画像，方便人工判断，也方便后续脚本读取。  
边界：只记录页面结构、路由形状、页面族、风险等级、状态类别、控件类别和停止点；不记录真实账号、订单、地址、聊天、商品标题、金额、经营数据、图片链接、二维码内容或登录材料。

## 一句话结论

遇到任意闲鱼页面，先在 `goofish-page-ontology.json` 里按 `id` 或 `routePattern` 找到画像，再按 `liveCoverage`、`transitionClass`、`defaultActionGate`、`expectedStates` 和 `stopPoints` 决定下一步。这样可以避免只看 URL 就误判页面风险。

## 画像字段怎么读

| 字段 | 含义 | 使用方式 |
| --- | --- | --- |
| `id` | 稳定页面编号 | 脚本和人工都优先用它定位页面。 |
| `surface` | 主站或卖家工作台 | 区分 `www` 与 `seller` 两套导航。 |
| `routePattern` | 路由形状 | 只代表形状，不代表真实私有参数。 |
| `family` | 页面族 | 决定默认探测方式、动作门禁和状态预期。 |
| `layer` | M0-M6 风险层级 | 越靠后越靠近交易、经营、身份、容器边界。 |
| `evidence` | 证据来源 | 判断是 Live、Static、Deep/Param 还是 Shell。 |
| `readiness` | R0-R5 就绪等级 | 判断页面理解是否可用于只读巡检或只能做边界描述。 |
| `liveCoverage` | 当前登录 Profile 下的覆盖状态 | 判断能不能打开、是否必须等用户上下文。 |
| `deepeningQueue` | D1-D6 深化队列 | 决定下一轮观察优先级和观察粒度。 |
| `transitionClass` | 页面流转类别 | 判断从当前页跳转到该页是否安全。 |
| `defaultActionGate` | G0-G4 默认动作门禁 | 任何具体按钮都要在这个基础上再判一次。 |
| `expectedStates` | S0-S10 状态/弹窗预期 | 用来处理 loading、空态、登录、门禁、确认弹窗等。 |
| `probeMode` | 默认只读探测模式 | 脚本可用它选择等待锚点和输出口径。 |
| `allowedRead` | 页面级可读内容 | 只读这些结构，不读真实私有值。 |
| `defaultObservationTargets` | 深化队列建议观察项 | 决定观察 tab、表头、字段、按钮类别还是容器边界。 |
| `anchors` | 页面加载锚点 | 判断页面是否已稳定，不用真实业务内容作锚点。 |
| `stopPoints` | 停止点 | 命中后停止，不继续点击或触发。 |
| `stopPolicy` | 覆盖状态对应的停止策略 | 给人工和脚本的简短处置说明。 |

## 判断顺序

1. 先看 `liveCoverage`：`observed-live` 可只读观察；`requires-user-context` 要等用户给真实上下文；`static-only` 只解释静态证据；`shell-boundary` 只认外壳。
2. 再看 `transitionClass`：`SAFE_READ` 可结构化读取；`READ_WITH_REDACTION` 只能脱敏读；`REQUIRES_USER_CONTEXT` 不猜参数；`STATIC_ONLY` 不为了补覆盖强开；`SHELL_ONLY` 停在容器边界。
3. 再看 `defaultActionGate`：G0/G1 可只读；G2 只做草稿辅助；G3 必须明确确认；G4 不主动触发。
4. 再看 `expectedStates`：遇到登录、无权限、二维码、确认弹窗、上传下载、高风险业务态时，用 S0-S10 规则升级处理。
5. 最后看 `stopPoints`：任何提交、发送、支付、退款、发货、导出、上传、权限、认证、下载、安装、账号切换都停。

## 页面覆盖概览

| 类别 | 数量 | 说明 |
| --- | ---: | --- |
| 总页面 | 66 | 来自 manifest 的主站和卖家工作台页面。 |
| 主站页面 | 31 | 公开发现、商品、个人、订单、发布、消息、账号、登录和静态承接页。 |
| 卖家页面 | 35 | 数据、商品、订单、售后、财务、账号、安全、推广、消息、外壳和门禁页。 |
| 已 Live 观察 | 40 | 当前登录 Profile 下可进入并只读观察结构。 |
| 需用户上下文 | 8 | 商品、订单详情、聊天商品页等，不猜真实参数。 |
| 静态页 | 16 | 静态包或模块证据，只解释不强行打开。 |
| 外壳边界 | 2 | 登录或 iframe 容器，只识别边界。 |

## 自动化使用口径

脚本读取时建议把 `goofish-page-ontology.json` 当第一入口：

```text
route/hash -> ontology page -> liveCoverage -> transitionClass -> defaultActionGate -> expectedStates -> stopPoints
```

输出时只允许写：

```text
页面 id、路由形状、页面族、层级、证据、就绪等级、覆盖状态、流转类别、动作门禁、状态类别、字段名、tab 名、表头、按钮名、停止点
```

不能写：

```text
真实账号、订单号、地址、聊天正文、商品标题、金额、经营指标、图片链接、二维码内容、密码、验证码、cookie、token、localStorage、sessionStorage
```

## 和其他文件的关系

| 需要更细内容 | 去看 |
| --- | --- |
| 页面发现过程和长笔记 | `goofish-page-map.md` |
| URL/hash 归类 | `goofish-route-inventory.md` |
| 页面层级 | `goofish-site-taxonomy.md` |
| 只读探测步骤 | `goofish-safe-probe-protocol.md` |
| 登录后覆盖 | `goofish-live-coverage-matrix.md` |
| 下一轮深化 | `goofish-page-deepening-queue.md` |
| 页面间跳转 | `goofish-page-transition-graph.md` |
| 状态和弹窗 | `goofish-state-modal-handling.md` |
| 动作能不能点 | `goofish-action-execution-guard.md` |
| 字段能不能记录 | `goofish-page-field-inventory.md` |
| 背后接口风险 | `goofish-page-api-crosswalk.md` |

## 最小人工判断模板

```text
页面：<id 或 routePattern>
覆盖：observed-live / requires-user-context / static-only / shell-boundary
流转：SAFE_READ / READ_WITH_REDACTION / REQUIRES_USER_CONTEXT / STATIC_ONLY / SHELL_ONLY
动作：G0 / G1 / G2 / G3 / G4
状态：S0-S10 中当前命中的类别
可读：结构、字段名、tab、表头、按钮名、状态类别
停止：命中的 stopPoints
下一步：只读继续 / 脱敏读取 / 等用户上下文 / 静态解释 / 停在外壳
```

结论：`goofish-page-ontology.json` 是当前最集中的页面理解入口；人工要读它，脚本也优先读它，再按具体问题跳到其它文档深挖。
