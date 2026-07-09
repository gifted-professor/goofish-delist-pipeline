# START_HERE for Codex

用途：闲鱼页面理解、只读商品指标采集、日常在售/下架同步。

## 先读

1. `README.md`
2. `docs/goofish-readme-first.md`
3. 日常同步或下架相关任务再读 `docs/goofish-delist-pipeline-runbook.md`
4. 如果任务是从 SZWego/微购相册按关键词抓商品素材，再接到闲鱼选品或上架准备，读 `docs/szwego-keyword-gallery-to-goofish-runbook.md`

## 先做只读检查

```bash
/usr/bin/python3 scripts/goofish-login-check.py
```

如果只是日常轻量同步，默认命令是：

```bash
bash scripts/goofish-daily.sh --push
```

只有周一、差异很大、或用户明确要求深度清理时，才考虑 `--prune` / full sync 路径。

## 边界

- 这是本机浏览器登录态任务，不要默认搬到 CI 或远端服务器。
- `data/goofish-item-state.json` / 本地 ledger 是历史真相；飞书 Base 更像当前状态输出。
- 只读采集优先，任何支付、发货、退款、发布、发送、删除、导出、切号都要停。
- 不记录 token、cookie、验证码、真实账号、订单、地址、聊天、商品标题、金额、图片链接。

## 不要扫

- `.goofish-browser-profile*`
- `.goofish-checkpoint-*.json`
- `.goofish-collect.log`
- 大量历史输出，除非用户问具体 run

## 成功口径

- 登录预检通过。
- dry-run 或 daily summary 能说明新增、消失、写入、跳过数量。
- 写入任务要能指向日志、summary 或 ledger，不只说“跑过了”。
