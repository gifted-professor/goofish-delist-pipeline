#!/bin/bash
# 快速采集：用已登录的浏览器访问其他店铺主页
# 用法：bash scripts/goofish-quick-collect.sh --port 9221 --userId 2219882422701 --name account-05

cd "$(cd "$(dirname "$0")" && pwd)/.." || exit 1
PY="${GOOFISH_PY:-/usr/bin/python3}"

PORT=""
USERID=""
NAME=""

while [ $# -gt 0 ]; do
  case "$1" in
    --port) PORT="$2"; shift 2 ;;
    --userId) USERID="$2"; shift 2 ;;
    --name) NAME="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

[ -z "$PORT" ] && echo "需要 --port" && exit 1
[ -z "$USERID" ] && echo "需要 --userId" && exit 1
[ -z "$NAME" ] && NAME="borrowed"

echo "==== 用端口 $PORT 的浏览器采集 $NAME (userId=$USERID) ===="
"$PY" scripts/goofish-collect-v3.py --account "$NAME" --port "$PORT" --userId "$USERID"
