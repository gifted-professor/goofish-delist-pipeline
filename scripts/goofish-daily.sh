#!/bin/bash
# 闲鱼多账号一键采集流水线
#   逐个账号采集（仅对已启动+已登录的端口）→ 合并进台账+出建议清单 → 可选推飞书
#
# 用法：
#   bash scripts/goofish-daily.sh                 # 采集所有在线账号 + 更新台账（不推飞书）
#   bash scripts/goofish-daily.sh --push          # 再加：推飞书。默认推建议清单；
#                                                 #   周一 或 在售集合大变动(新增+消失>=阈值) 自动升级为全量 --prune 同步
#   bash scripts/goofish-daily.sh --full-sync     # 强制全量在售镜像 + 剪枝（任意天）
#   bash scripts/goofish-daily.sh --sync-threshold 15   # 变动触发全量的阈值（默认 15）
#   bash scripts/goofish-daily.sh --days 7        # 无增长阈值改 7
#   bash scripts/goofish-daily.sh --only account-05   # 只跑某个账号
#
# 账号没在线（端口没监听）会跳过并提示，不会自动登录——登录按 runbook 用户本人做。

set -u
# 路径自适应：cd 到脚本所在的上一级（项目根），整个目录搬到哪都不用改代码
cd "$(cd "$(dirname "$0")" && pwd)/.." || exit 1
PY="${GOOFISH_PY:-/usr/bin/python3}"   # 默认 /usr/bin/python3（装了 websockets）；换机器可用 GOOFISH_PY 覆盖

# 账号清单：slot:port（新增账号在这里加一行即可，端口约定 9220+NN）
ACCOUNTS=( "account-01:9221" "account-03:9223" "account-04:9224" "account-05:9225" )

DAYS=5
PUSH=0
FULL_SYNC=0
SYNC_THRESHOLD=15
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --push) PUSH=1; shift ;;
    --full-sync) FULL_SYNC=1; PUSH=1; shift ;;
    --sync-threshold) SYNC_THRESHOLD="$2"; shift 2 ;;
    --days) DAYS="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

ran=0
for entry in "${ACCOUNTS[@]}"; do
  slot="${entry%%:*}"; port="${entry##*:}"
  [ -n "$ONLY" ] && [ "$ONLY" != "$slot" ] && continue
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "==== 采集 $slot (端口 $port) ===="
    "$PY" scripts/goofish-collect-v3.py --account "$slot" --port "$port" || echo "⚠ $slot 采集异常（看上面日志）"
    ran=$((ran+1))
  else
    echo "⏭  跳过 $slot：端口 $port 未监听。先按 runbook 启动 Chrome 并登录。"
  fi
done

if [ "$ran" -eq 0 ]; then
  echo "没有任何账号在线，未更新台账。"
  exit 0
fi

TODAY="$(date +%F)"
echo "==== 更新台账 + 建议清单（阈值 $DAYS，日期 $TODAY）===="
# 钉死「今天」：若今日所有号采集都失败/残缺（无今日文件），diff-state 会非零退出，
# 不会去误处理昨天的旧文件；此时直接跳过推飞书，绝不在残缺数据上 prune 误删。
if DIFF_OUT="$("$PY" scripts/goofish-diff-state.py --no-growth-days "$DAYS" --date "$TODAY" 2>&1)"; then
  echo "$DIFF_OUT"
else
  echo "$DIFF_OUT"
  echo "⚠ diff-state 未处理（今日无有效采集文件？），跳过推飞书。"
  exit 1
fi

if [ "$PUSH" -ne 1 ]; then
  echo "（未推飞书。要推加 --push；强制全量加 --full-sync）"
  exit 0
fi

# 从 diff-state 的 [SUMMARY] 行读取在售集合变动量（新增 + 消失）
SUMMARY_LINE="$(printf '%s\n' "$DIFF_OUT" | grep '^\[SUMMARY\]' | tail -1)"
NEW=$(printf '%s' "$SUMMARY_LINE" | sed -nE 's/.*new=([0-9]+).*/\1/p'); NEW=${NEW:-0}
GONE=$(printf '%s' "$SUMMARY_LINE" | sed -nE 's/.*vanished=([0-9]+).*/\1/p'); GONE=${GONE:-0}
CHANGED=$((NEW + GONE))
DOW=$(date +%u)   # 1=周一

# 决定推送模式：周一 / 强制 / 在售集合大变动 → 全量 --prune；否则只推建议清单
REASON=""
[ "$FULL_SYNC" -eq 1 ] && REASON="--full-sync 强制"
[ -z "$REASON" ] && [ "$DOW" -eq 1 ] && REASON="周一全量"
[ -z "$REASON" ] && [ "$CHANGED" -ge "$SYNC_THRESHOLD" ] && REASON="在售大变动(新增$NEW+消失$GONE>=$SYNC_THRESHOLD)"

if [ -n "$REASON" ]; then
  echo "==== 全量同步飞书（在售镜像 + 剪枝，--apply）触发原因: $REASON ===="
  "$PY" scripts/goofish-push-feishu.py --mode full --prune --apply
else
  echo "==== 推飞书（建议清单，--apply）。在售变动 新增$NEW+消失$GONE < $SYNC_THRESHOLD，不全量 ===="
  "$PY" scripts/goofish-push-feishu.py --mode suggestions --no-growth-days "$DAYS" --apply
fi
