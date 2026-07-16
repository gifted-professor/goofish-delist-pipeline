# 闲鱼账号 Profile 采集 Runbook（多账号）

日期：2026-06-22（2026-06-23 更新为多账号 + 接入下架建议流水线）

用途：让 Hermes、Codex 或其他本机执行器复用一个或多个已登录的 Chrome Profile，只读采集闲鱼账号商品数据，并喂给「连续无增长 → 下架建议」流水线。

## 账号 / Profile 约定

每个账号 = 一个独立的 Chrome user-data-dir + 一个独立调试端口；登录由用户本人手动完成，脚本不碰凭据。

| 账号槽位 | Profile 目录（`.goofish-browser-profiles/<slot>`） | 调试端口 | 状态 |
| --- | --- | --- | --- |
| account-01 | `.../goofish/.goofish-browser-profiles/account-04` | 9224 | 当前绑定奥莱 |
| account-02 | `.../goofish/.goofish-browser-profiles/account-02` | 9222 | 管道已就绪，**待用户登录** |
| account-03 | 暂未绑定 | - | 小华待重新绑定 |
| account-04 | `.../goofish/.goofish-browser-profiles/account-03` | 9233 | 当前绑定小佳 |
| account-05 | `.../goofish/.goofish-browser-profiles/account-05` | 9225 | 当前绑定皮皮 |

端口以 `runtime/account-bindings.json` 为准，不再按 `account-NN → 9220+NN` 猜测。采集脚本未显式传 `--port` 时使用当前已绑定账号的端口。

Profile 根目录：

```text
/Volumes/GPFS/Users/a1234/Desktop/Coding/goofish/.goofish-browser-profiles/
```

account-01 基线验证状态：

```text
已登录
可打开 https://www.goofish.com/personal
可见宝贝总数 631（在售 470 / 已售出 161）
首屏可见商品详情链接
```

## 启动浏览器（任意账号）

把 `<SLOT>` 换成账号槽位、`<PORT>` 换成对应端口（见上表）。

先检查端口是否已在监听，已开着就不要重复启动：

```bash
lsof -nP -iTCP:<PORT> -sTCP:LISTEN
```

没监听再启动（不同 user-data-dir + 不同端口可同时开多个账号，互不影响）：

```bash
open -na "Google Chrome" --args \
  --user-data-dir="/Volumes/GPFS/Users/a1234/Desktop/Coding/goofish/.goofish-browser-profiles/<SLOT>" \
  --remote-debugging-port=<PORT> \
  --no-first-run \
  --no-default-browser-check \
  "https://www.goofish.com/personal"
```

例：登录第二个账号 account-02（端口 9222）：

```bash
open -na "Google Chrome" --args \
  --user-data-dir="/Volumes/GPFS/Users/a1234/Desktop/Coding/goofish/.goofish-browser-profiles/account-02" \
  --remote-debugging-port=9222 \
  --no-first-run --no-default-browser-check \
  "https://www.goofish.com/personal"
```

检查 Chrome 调试接口：

```bash
curl -s http://127.0.0.1:<PORT>/json/version
curl -s http://127.0.0.1:<PORT>/json/list
```

## 登录态处理

- 如果打开后仍是登录状态，直接采集。
- 如果出现登录、扫码、验证码或安全验证，由用户本人在浏览器窗口里处理。
- 不复制、不读取、不保存 `cookie`、`token`、`localStorage`、`sessionStorage`、密码、验证码或二维码内容。
- 采集完成后可以关闭 Chrome 窗口，登录态会保留在 Profile 目录里。
- 不要删除 Profile 目录，不要清理浏览器站点数据。
- 每个账号用各自独立的 Profile 目录，绝不共用，避免登录态串号。

## 采集（脚本流程）

脚本都在 `scripts/`，输出都落在 `data/`。

### 1. 采集某账号商品指标

```bash
# account-01（默认，端口 9221）
python3 scripts/goofish-collect-v3.py

# account-02（端口不填自动推 9222）
python3 scripts/goofish-collect-v3.py --account account-02
# 或显式指定端口
python3 scripts/goofish-collect-v3.py --account account-02 --port 9222
```

输出（按账号 + 日期命名）：

```text
data/goofish-account-item-metrics-<slot>-YYYY-MM-DD.json
data/goofish-account-item-metrics-<slot>-YYYY-MM-DD.csv
```

脚本只读流程：连接 `127.0.0.1:<port>` → 打开/复用 `https://www.goofish.com/personal` → 确认非登录页 → 切「在售」「已售出」页签滚动收集本账号商品详情链接 → 合并去重 → 逐个打开详情页只读解析「为你推荐」之前的主商品正文 → 每 10 条写一次 JSON/CSV。

### 2. 增量对比 + 下架规则 + 建议清单

```bash
python3 scripts/goofish-diff-state.py            # 默认：无增长20天；低浏览量5天/50、10天/100
```

- 自动吃当天**所有账号**的采集文件，合并处理（商品ID 全站唯一，不撞键）。
- 更新台账 `data/goofish-item-state.json`（每条记 account、无增长天数、状态）。
- 低浏览量规则：首次发现满 5 天且浏览 < 50，或满 10 天且浏览 < 100；首次采集到的新商品默认视为当天发布，已有商品不会因重复采集而重置首次发现日。
- 当前阶段只生成建议清单，不自动下架；台账和飞书新增「下架权重」字段，范围 0～100，分数越高越建议人工确认。
- 输出建议清单 `data/goofish-delist-suggestions-YYYY-MM-DD.csv`（含「闲鱼账号」列）。
- 安全设计：采集失败那天不计数；想要数为 null 只用浏览数判断；已售出/消失商品踢出清单；**某账号当天没采，不会误标它的商品「消失」**；同一天重复跑幂等。

### 3. 推送飞书（可选）

```bash
python3 scripts/goofish-push-feishu.py --mode suggestions          # dry-run 预览
python3 scripts/goofish-push-feishu.py --mode suggestions --apply  # 真写
python3 scripts/goofish-push-feishu.py --mode full --account account-02 --apply  # 只推某账号
```

按「商品ID」upsert 进飞书 Base，写入带「闲鱼账号」列。表坐标见 memory `feishu-delist-table`。

## 可采集字段

允许采集：

```text
accountSlot
listStatus: 在售 / 已售出
itemId
url（商品详情链接，?id= 形式）
collectedDate
商品标题
价格
直接买价格
浏览数
人想要
人小刀价
是否出现下架
是否出现删除
是否出现已售/交易完成类状态
采集错误
```

不采集：

```text
cookie
token
localStorage
sessionStorage
密码
验证码
二维码内容
真实订单内容
地址
聊天正文
支付信息
物流信息
```

## 禁止动作

采集脚本只能读页面，不允许点击或触发以下动作：

```text
立即购买
我想要
聊一聊
编辑
下架
删除
发布
保存
提交
上传
下载
导出
退款
发货
评价
投诉
认证
切号
```

如果页面出现登录、扫码、验证码、安全验证、确认弹窗、支付、发货、退款、上传、下载、导出等状态，立即停止并记录停止原因。

> 注：自动「下架」属于 Phase 2，单独立项，需先补「下架」按钮选择器 + 确认弹窗状态机 SOP，本 runbook 仍保持只读。

## 可直接给 Hermes 的任务（把 <SLOT> / <PORT> 换成目标账号）

```text
在 /Volumes/GPFS/Users/a1234/Desktop/Coding/goofish 下执行闲鱼 <SLOT> 商品指标只读采集。

使用 Chrome Profile：
.../goofish/.goofish-browser-profiles/<SLOT>

使用调试端口：
127.0.0.1:<PORT>（约定 account-NN → 9220+NN）

如果端口未监听，按本 runbook「启动浏览器」启动 Chrome。
如果出现登录、扫码、验证码或安全验证，停止并提示用户处理。

采集：
1. python3 scripts/goofish-collect-v3.py --account <SLOT>（端口自动推，或 --port <PORT>）。
2. 打开 https://www.goofish.com/personal，确认已登录。
3. 从在售和已售出列表滚动收集本账号商品详情 URL，合并去重后逐个打开详情页。
4. 只读解析标题、价格、直接买价格、浏览数、人想要、人小刀价、下架/删除/已售状态信号；详情页只取"为你推荐"之前的主商品正文。
5. 不读取、不保存 cookie/token/localStorage/sessionStorage/验证码/二维码。
6. 不点击购买、我想要、聊一聊、编辑、下架、删除、发布、保存、提交、上传、下载、导出等动作。
7. 输出在 data/ 下，按账号+日期命名。
8. 采集后跑 goofish-diff-state.py 更新台账与下架建议清单。
```

## account-01 本轮基线

上一次成熟采集结果：

```text
商品总数：631
在售：470
已售出：161
详情页读取错误：0
有浏览数的商品：129
有想要计数的商品：53
有小刀价计数的商品：56
浏览数合计：9875
想要数合计：338
小刀价人数合计：112
```

参考输出（整理后已归入 data/）：

```text
data/goofish-account-item-metrics-account-01-2026-06-22.json
data/goofish-account-item-metrics-account-01-2026-06-22.csv
```
