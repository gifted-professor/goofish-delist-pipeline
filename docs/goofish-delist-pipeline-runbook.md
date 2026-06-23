# 闲鱼「连续无增长 → 建议下架」流水线 · 运行手册

> 给 Hermes / 任何接手的人：照这份就能跑。最后更新 2026-06-23（含当日修复的几个关键坑）。
> 当前阶段 = **Phase 1（只产出"建议下架清单"，不自动下架）**。任何下架/发布/支付类写操作都不在本流水线内。

---

## 0. 一句话数据流

```
每个闲鱼号（已登录的 Chrome，CDP 端口）
   → collect-v3 只读采「在售」商品的浏览/想要/小刀价   （data/goofish-account-item-metrics-<slot>-<date>.json）
   → diff-state 对比昨天、记台账、判"连续 N 天无增长"     （data/goofish-item-state.json = 唯一真相）
   → 建议清单 CSV（连续 ≥N 天零增长的在售品）            （data/goofish-delist-suggestions-<date>.csv）
   → push-feishu 同步「在售」到飞书 Base 表（展示+确认层），并剪掉卖掉/下架的
```

**台账 `data/goofish-item-state.json` 是无增长天数的唯一真相，不是飞书。** 飞书只做展示和人工确认。

---

## 1. 账号清单（slot ↔ 端口 ↔ 店铺）

| slot | CDP 端口 | 店铺名 | 在售件数（2026-06-23）|
|---|---|---|---|
| account-01 | 9221 | 奥莱运动折扣捡漏 | 459 |
| account-03 | 9223 | 小华潮牌店 | 298 |
| account-04 | 9224 | 小佳运动 | 11 |
| account-05 | 9225 | 皮皮运动 | 153 |

- 端口约定 **9220 + NN**（account-01→9221，account-03→9223…）。
- 每个号一个独立 Chrome user-data-dir：`.goofish-browser-profiles/<slot>`。
- `account-NN` 是**内部连接键**（串采集文件名、台账主键、daily.sh、飞书「闲鱼账号」列）。**别改 slot 名**；改展示名只改飞书「店铺名」列 / `push-feishu.py` 的 `STORE_NAMES`。
- account-02（Bape77777）已整体移除，不在清单内。

---

## 2. 环境前提（只需确认一次）

1. **Python**：脚本默认用 `/usr/bin/python3`（装了 `websockets 13.1`；Homebrew python 没装，会跑挂）。换解释器可设环境变量 `GOOFISH_PY=/path/to/python3`。
2. **lark-cli 登录**（推飞书才需要）：`lark-cli auth login --domain base`，身份 `--as user`。环境有代理，脚本已统一 `export LARK_CLI_NO_PROXY=1`。
3. **各账号浏览器已登录**：daily 不会自动登录；端口没监听就跳过该号。登录态掉了要本人重扫码（见 §3 第 1 步）。
4. **路径自适应**：脚本的项目根目录按脚本自身位置推导（不再写死路径），整个目录搬到哪、从哪个 cwd 调用都不用改代码。

### 换一台机器跑（portability 清单）
本流水线非「拷过去就能跑」，换机器需要：
- ✅ **路径**：已自适应，无需改（前提：整个项目目录一起搬过去）。
- **Python**：新机器装 `python3 + websockets`，或设 `GOOFISH_PY`。
- **lark-cli**：新机器装 lark-cli 并重做 `lark-cli auth login --domain base`（认证 token 是每台机器本地的）。
- **⚠ 4 个登录好的 Chrome（CDP 端口 9221/9223/9224/9225）= 本质绑机器**：登录态在 `.goofish-browser-profiles/<slot>`（随目录搬走），但 CDP 端口必须由**跑在该机器上的 Chrome** 打开；**同一 profile 不能两机同时开**（profile 锁），两台机器只能轮流当采集机；换机器/IP 后闲鱼登录态可能失效要重扫码。
- 若两机挂的是**同一网络盘(GPFS)同路径** → 文件/台账/profile 共享，但浏览器仍只能在其中一台跑。

---

## 3. 每日操作（Hermes 照这三步走）

### 第 1 步 · 先验登录态（30 秒）
```bash
cd /Volumes/GPFS/Users/a1234/Desktop/Coding/goofish
/usr/bin/python3 scripts/goofish-login-check.py
```
逐号开临时标签页导航 `/personal`、读店铺名、查登录墙，确认后自动关掉，不动现有页面。
- `✅ 已登录` + 正确店铺名 → 能采。
- `⚠ 登录态已掉` / `❌ CDP 不在线` → 让**账号本人**在对应端口窗口重登后再跑。
- 只查某号：`... goofish-login-check.py account-03`

### 第 2 步 · 一键采集 + 更新台账
```bash
bash scripts/goofish-daily.sh            # 采所有在线账号 → 更新台账 → 出建议清单（不推飞书）
```
- 只跑某号：`--only account-05`；改阈值：`--days 7`（默认 **N=5**）。
- 端口没在线会跳过提示，不报错。
- **采完务必核对件数 = 店铺 chip 在售数**（脚本日志会打 `汇总: 在售 X … chip 在售=Y，一致✓/不一致⚠`）。不一致就重采那个号。

### 第 3 步 · 推飞书（`daily.sh --push` 自带条件触发，推荐）

**日常 scheduled 跑这一条就够**：
```bash
bash scripts/goofish-daily.sh --push
```
它会自动决定推什么（条件触发，省掉每天无脑全量的上千次写）：

| 情况 | 行为 |
|---|---|
| 平日 + 在售集合小变动（新增+消失 < 阈值，默认 15）| 只推**建议下架清单**（轻）|
| **周一** | 自动升级为**全量在售镜像 + 剪枝**（`--mode full --prune`）|
| **在售大变动**（上新/大量卖出，新增+消失 ≥ 阈值）| 自动升级为全量同步 |
| `bash scripts/goofish-daily.sh --full-sync` | 任意天**强制**全量同步 |

- 阈值可调：`--sync-threshold 20`。变动量来自 diff-state 输出的 `[SUMMARY] new=.. vanished=..`。
- 手动单跑全量：`/usr/bin/python3 scripts/goofish-push-feishu.py --mode full --prune --apply`（新号入表 / 临时对账）。
- **`push-feishu` 默认 `--dry-run`，只打印不写**；确认后加 `--apply`。`--mode full` 只推在售，`--prune` 删掉同账号里卖掉/下架的飞书行 → 「飞书 = 当前真实在售」。只推某号 `--account account-03`。

---

## 4. ⚠ 三个关键坑（都在 2026-06-23 踩过并修好，务必理解）

### 4.1 后台标签页懒加载被节流 → 少采（曾把 153 件采成 20）
被遮挡/非最前的 Chrome 标签页 `document.visibilityState=hidden`，懒加载(IntersectionObserver)被节流，**滚动加载不出新商品**，会卡在第一屏 ~20 个就判到底。
- **修复**：collect-v3 开采前调 `Emulation.setFocusEmulationEnabled{enabled:true}`，让渲染器把页面当有焦点/可见。`bringToForeground`、`setWebLifecycleState` 都无效，**只有这个管用**。
- **双保险**：用店铺「在售N」chip 数当滚动目标，滚到载满 N 才停（见日志 `载满 153/153 ✓`）。chip 数是闲鱼后台权威数，也顺带挡住滚过头进「为你推荐」的污染。

### 4.2 采集会把已售出混进来 → 必须切分在售
`/personal` 默认「宝贝」视图 = 在售 + 已售出。不处理的话已售出会被当在售采进来（曾 04 在售只有 11，却采了 30）。
- **修复**：collect-v3 先采「宝贝」全量，再点「已售出」chip 拿到已售出 id 集合，**只保留在售**（`INCLUDE_SOLD=False` 默认）。
- 判在售/已售出的权威信号（详情页）：在售有「下架」按钮；已售出显示「卖掉了」。
- **策略：只走在售。** push-feishu full 模式只推在售；`--prune` 删掉卖掉/下架的飞书行。

### 4.4 残缺采集会误删飞书 → 完整性闸（已加，自动保护）
某号采集残缺（页面异常/掉登录导致 chip=None，或懒加载没滚到 chip 数）时，**绝不能让残缺结果进 diff-state**——否则没采到的在售会被误判 MISSING、`push --prune` 把对应飞书好行删掉（一次抖动删几百行）。
- collect-v3 已加闸：在售采到数 < 店铺 chip 在售数、或读不到 chip → **拒写文件 + 非零退出**，daily.sh 打 `⚠ 采集异常` 并跳过该号；该号当天就当没采（其飞书行原样保留，不删）。
- 看到某号 `⚠ 采集异常` = 它那天没数据进库，**正常现象**（多半是该号窗口掉登录/被重定向）。重登该号窗口后单独重采即可：`collect-v3 --account <slot>`。

### 4.3 我们自己采集 = 浏览 +1 污染（最隐蔽，会废掉无增长判定）
打开商品详情页采指标时，闲鱼会给「浏览」**+1**（**实测店主本人身份也照计**）。每天采一次就自带 +1，"涨了就归零"会永远归零、永远出不了建议。
- **修复**：diff-state 的 `grew()` 里，**浏览要涨过 `SELF_VIEW_PER_RUN`(=1) 才算真涨**（扣掉我们自己那次）；想要数（开页面不会加，是干净信号）照常 >0 算涨。
- 成立前提：每天只采一次，且 collect 有断点（同一天重跑跳过已采项、不重复访问）。若某天人为多采，最坏只是误判"涨"→ 多等一天才进建议（安全方向，不会误删）。
- 注意：飞书里**显示的**浏览绝对值仍含我们历史访问（每天约 +1），但**判增长的逻辑已干净**，不影响下架判定。

---

## 5. 加一个新账号（如 account-06）

1. 起新 Chrome，user-data-dir=`.goofish-browser-profiles/account-06`，CDP 端口 **9226**，账号本人登录。
2. `goofish-daily.sh` 的 `ACCOUNTS=(...)` 加 `"account-06:9226"`。
3. `goofish-login-check.py` 的 `ACCOUNTS` 加 `("account-06", 9226)`。
4. `goofish-push-feishu.py` 的 `STORE_NAMES` 加 `"account-06": "<店铺名>"`。
5. 飞书「闲鱼账号」单选加 `account-06` 选项（写入时选项不存在会报错）。
6. 首次：`collect-v3 --account account-06` → `diff-state` → `push-feishu --mode full --account account-06 --prune --apply`。

---

## 6. 飞书 Base 表坐标

- wiki：https://v8mfxiqu19.feishu.cn/wiki/BsAJwGzkIiJ0J4kfp2IcUet3nSg?table=tbl6lyatj4o6yXOu
- `base_token`：`PYtZbqyPyafc4sscwdjcQNLNnEh`　`table_id`：`tbl6lyatj4o6yXOu`
- 字段：商品ID(主键) · 店铺名 · 商品标题 · 商品链接 · 价格 · 直购价 · 浏览数 · 想要数 · 小刀价数量 · 无增长天数 · 在售状态 · 闲鱼账号 · 采集错误 · 采集时间 · ID(系统)
- 现 921 行 = 4 号真实在售（01:459 / 03:298 / 04:11 / 05:153）。

---

## 7. 关键文件速查

| 路径 | 作用 |
|---|---|
| `scripts/goofish-login-check.py` | 登录态自检（跑 daily 前先跑） |
| `scripts/goofish-daily.sh` | 一键：采所有在线号 → 台账 → 建议清单 →(可选)推飞书 |
| `scripts/goofish-collect-v3.py` | 单号只读采集（CDP；含 focus 解锁、chip 目标、在售切分） |
| `scripts/goofish-diff-state.py` | 对比 + 台账 + 建议清单（含浏览 +1 扣除） |
| `scripts/goofish-push-feishu.py` | 按商品ID upsert 进飞书（`--mode full\|suggestions`，`--prune`，默认 dry-run） |
| `data/goofish-item-state.json` | **台账 = 唯一真相**（有 `.bak-*` 备份） |
| `data/goofish-delist-suggestions-<date>.csv` | 当天建议下架清单 |
</content>
