# 闲鱼 IM 批量采集 runbook

用途：让 Hermes 或人工操作员按批次从已登录的本机 Chrome 采集闲鱼 IM 会话，支持左侧会话列表 cursor 恢复、已采会话跳过、SQLite 增量落库和脱敏输出。

## 安全边界

- 只连接用户已经登录好的本机 Chrome CDP 端口。
- 脚本只读渲染后的 DOM，不调用发送、清理未读、拉黑、快捷回复、文件上传或平台导出接口。
- 打开具体会话可能会让网页端把会话标为已读；运行前需要接受这个副作用。
- 默认脱敏手机号、邮箱和长数字；`out/` 已在 `.gitignore` 中，不进仓库。
- 不在终端展示聊天正文。进度日志只显示计数和哈希前缀。

## 预检

```bash
cd /Volumes/GPFS/Users/a1234/Desktop/Coding/goofish
/usr/bin/python3 scripts/goofish-login-check.py account-01
```

确认 `account-01` 的 `/personal` 是已登录状态，再手动打开一次：

```text
https://www.goofish.com/im
```

左侧能看到会话列表后再跑批量采集。

## 首批采集

```bash
/usr/bin/python3 scripts/goofish-im-export.py \
  --account account-01 \
  --max-conversations 100 \
  --max-conversation-scrolls 100 \
  --max-message-scrolls 12 \
  --progress-every 10
```

## 后续继续采集

```bash
/usr/bin/python3 scripts/goofish-im-export.py \
  --account account-01 \
  --resume-conversation-cursor \
  --max-conversations 100 \
  --max-conversation-scrolls 100 \
  --max-message-scrolls 12 \
  --progress-every 10
```

`--resume-conversation-cursor` 会从 SQLite 保存的左侧列表位置附近继续。边界附近重复看到的会话会用 `latestMessageToken` / SQLite 主键跳过或 upsert，不会重复插入。

## 成功口径

最终 JSON 中重点看这些字段：

```text
conversationCursorRestored=true   # 恢复左侧列表位置
scannedConversationCount          # 本轮页面扫到多少会话
skippedExistingConversationCount  # 已采且最新消息没变，被跳过多少
conversationCount                 # 本轮实际处理多少会话
insertedConversationCount         # 本轮新增入库多少会话
updatedMessageCount               # 已有消息被刷新多少
totalConversationCount            # SQLite 当前总会话数
totalMessageCount                 # SQLite 当前总消息数
errorCount=0                      # 本轮无会话级错误
```

注意：`conversationCount=100` 不等于总数一定增加 100。总数增加看 `insertedConversationCount`。

## 当前实测

2026-07-09 在 `account-01` 上验证：

- 第一批：新增 100 个会话、2148 条消息。
- 第二批：扫到 134 个、跳过 34 个、处理 100 个，其中新增 97 个会话。
- 两批后主库总计：199 个会话、4569 条消息。
- 新版 smoke DB 验证：进度日志正常；第二轮先跳过已采 2 个，再继续采后续 2 个；SQLite 每个会话处理完即落库。

## 中途异常处理

- 如果脚本中途断掉，已处理完的会话已经写入 SQLite；重新运行 `--resume-conversation-cursor` 即可。
- 如果 `/im` 页面没有左侧会话，先在 Chrome 里确认 IM 侧已登录并能看到会话列表。
- 如果连续很多轮 `skippedExistingConversationCount` 很高但 `insertedConversationCount` 很低，说明 cursor 附近重复区较大，可继续跑；SQLite upsert 会保护去重。
- 如果 `errorCount > 0`，先保留本轮输出 JSON，不要删库；下一轮可以继续跑，单个坏会话不会影响已落库数据。

