#!/usr/bin/env python3
"""把本地台账 goofish-item-state.json 按「商品ID」upsert 进飞书 Base 表。

lark-cli 没有「按业务键 upsert」也没有「逐行不同值的批量更新」，所以这里：
  1. 翻页拉现有记录，建 {商品ID -> record_id} 映射
  2. 台账里已存在的 -> 逐条 +record-upsert --record-id 更新
  3. 台账里新出现的 -> +record-batch-create 批量新建（200/批）

两种模式：
  --mode full         全表镜像：把台账所有商品同步进飞书（重，约几百次写）
  --mode suggestions  只推「在售 且命中下架建议规则」的商品（轻，默认）

安全：默认 --dry-run，只打印将要做什么，不写飞书。确认无误后加 --apply 才真正写。

表坐标见 memory/feishu-delist-table.md：
  base_token PYtZbqyPyafc4sscwdjcQNLNnEh / table tbl6lyatj4o6yXOu
"""

import argparse
import json
import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根（scripts/ 上一级），随目录搬动自适应
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_FILE = os.path.join(DATA_DIR, "goofish-item-state.json")

BASE_TOKEN = "PYtZbqyPyafc4sscwdjcQNLNnEh"
TABLE_ID = "tbl6lyatj4o6yXOu"

# 台账状态 -> 飞书「在售状态」单选值
STATUS_MAP = {"在售": "在售", "已售出": "已售出", "missing": "已下架/已售"}

# account 槽位 -> 飞书「店铺名」展示值（闲鱼页面原名；account-NN 仍是内部连接键）
STORE_NAMES = {
    "account-01": "奥莱运动折扣捡漏",
    "account-02": "Bape77777",
    "account-03": "小华潮牌店",
    "account-04": "小佳运动",
    "account-05": "皮皮运动",
}

ENV = {**os.environ, "LARK_CLI_NO_PROXY": "1"}
IDENTITY = "user"


def lark(args, json_body=None):
    """跑一条 lark-cli base 命令，返回解析后的 JSON envelope（失败抛异常）。"""
    cmd = ["lark-cli", "base", *args, "--as", IDENTITY,
           "--base-token", BASE_TOKEN, "--table-id", TABLE_ID]
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body, ensure_ascii=False)]
    r = subprocess.run(cmd, capture_output=True, text=True, env=ENV)
    out = r.stdout.strip()
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(f"非 JSON 输出: {out[:300]} | stderr: {r.stderr[:200]}")
    if not data.get("ok"):
        raise RuntimeError(f"lark-cli 失败: {json.dumps(data.get('error'), ensure_ascii=False)}")
    return data["data"]


def fetch_id_map():
    """翻页拉全表，返回 {商品ID: record_id}。投影只取 商品ID 降低体积。"""
    id_map = {}
    for iid, (rid, _acc) in fetch_full_map().items():
        id_map[iid] = rid
    return id_map


def fetch_full_map():
    """翻页拉全表，返回 {商品ID: (record_id, 闲鱼账号)}。prune 时需要账号判断归属。"""
    full = {}
    offset = 0
    while True:
        d = lark(["+record-list", "--field-id", "商品ID", "--field-id", "闲鱼账号",
                  "--limit", "200", "--offset", str(offset), "--format", "json"])
        rids = d.get("record_id_list", [])
        rows = d.get("data", [])  # [[商品ID,[闲鱼账号]], ...] 与 rids 同序
        for rid, row in zip(rids, rows):
            if row and row[0] is not None:
                acc = row[1][0] if len(row) > 1 and isinstance(row[1], list) and row[1] else None
                full[str(row[0])] = (rid, acc)
        if not d.get("has_more"):
            break
        offset += len(rids) or 200
    return full


def to_num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def field_payload(e, *, for_create):
    """台账 entry -> 飞书字段 map。for_create=True 时 null 显式保留；更新时省略 null（不清空旧值）。"""
    date = (e.get("lastUpdated") or "")[:10]
    acct = e.get("account") or "account-01"
    store_name = e.get("sellerName") or STORE_NAMES.get(acct)
    fields = {
        "商品ID": e["itemId"],
        "闲鱼账号": acct,
        "店铺名": store_name,
        "商品标题": e.get("title"),
        "商品链接": e.get("url"),
        "价格": to_num(e.get("price")),
        "直购价": to_num(e.get("directBuyPrice")),
        "浏览数": e.get("lastView"),
        "想要数": e.get("lastWant"),
        "小刀价数量": e.get("lastKnife"),
        "无增长天数": e.get("noGrowthDays"),
        "下架权重": e.get("delistScore"),
        "在售状态": STATUS_MAP.get(e.get("status"), "在售"),
        "采集错误": e.get("lastError") or None,
        "采集时间": f"{date} 00:00:00" if date else None,
    }
    if for_create:
        return fields
    return {k: v for k, v in fields.items() if v is not None}


def select_items(state, mode, N, account=None):
    items = list(state.values())
    if account:
        items = [e for e in items if (e.get("account") or "account-01") == account]
    if mode == "suggestions":
        return [e for e in items
                if e.get("status") == "在售" and not e.get("lastError")
                and (e.get("delistReasons") or e.get("noGrowthDays", 0) >= N)]
    # full 模式也只推「在售」——已售出/已下架不进飞书（策略：只走在售）。
    return [e for e in items if e.get("status") == "在售"]


def main():
    global IDENTITY
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "suggestions"], default="suggestions",
                    help="full=全表镜像；suggestions=只推建议下架商品（默认）")
    ap.add_argument("--no-growth-days", type=int, default=20,
                    help="兼容旧台账的无增长阈值（默认 20）")
    ap.add_argument("--apply", action="store_true", help="真正写飞书；不加则只 dry-run 预览")
    ap.add_argument("--max", type=int, default=0, help="最多写多少条（0=不限），用于首次小批测试")
    ap.add_argument("--delay", type=float, default=0.3, help="逐条更新间隔秒（默认 0.3）")
    ap.add_argument("--account", default=None, help="只推某个账号（如 account-02）；默认全部")
    ap.add_argument("--as", dest="identity", choices=["user", "bot"], default="user",
                    help="飞书身份，默认 user；用户授权缺失但 bot 有表权限时可用 bot")
    ap.add_argument("--prune", action="store_true",
                    help="推完后删除同账号里不在「在售」集合的飞书行（卖掉/下架的）——固化只走在售")
    args = ap.parse_args()
    IDENTITY = args.identity

    if not os.path.exists(STATE_FILE):
        sys.exit(f"找不到台账 {STATE_FILE}，请先跑 goofish-diff-state.py")
    with open(STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)

    targets = select_items(state, args.mode, args.no_growth_days, args.account)
    if args.max:
        targets = targets[:args.max]
    target_ids = {e["itemId"] for e in targets}
    # prune 作用域：指定 --account 就只剪那个号，否则剪本次在售涉及的所有账号
    scope_accounts = ({args.account} if args.account
                      else {(e.get("account") or "account-01") for e in targets})

    print(f"模式: {args.mode}" + (f"（阈值 {args.no_growth_days}）" if args.mode == "suggestions" else ""))
    print(f"台账商品: {len(state)}  本次待同步: {len(targets)}")
    print("拉取现有记录建 商品ID->record_id 映射 ...")
    full_map = fetch_full_map()
    id_map = {iid: rid for iid, (rid, _a) in full_map.items()}
    print(f"飞书现有记录: {len(id_map)}")

    # 计算待剪枝的孤儿行：账号在作用域内、但商品ID 不在本次在售集合 → 卖掉/下架的
    to_prune = [(iid, rid) for iid, (rid, acc) in full_map.items()
                if acc in scope_accounts and iid not in target_ids]
    if args.prune:
        print(f"将剪枝(删): {len(to_prune)}  （作用域账号: {', '.join(sorted(scope_accounts))}）")

    to_update = [(e, id_map[e["itemId"]]) for e in targets if e["itemId"] in id_map]
    to_create = [e for e in targets if e["itemId"] not in id_map]
    print(f"将更新: {len(to_update)}  将新建: {len(to_create)}")

    if not args.apply:
        print("\n[dry-run] 未写飞书。确认后加 --apply 执行。示例预览：")
        for e, rid in to_update[:3]:
            print(f"  更新 {rid} <- {json.dumps(field_payload(e, for_create=False), ensure_ascii=False)}")
        for e in to_create[:3]:
            print(f"  新建    <- {json.dumps(field_payload(e, for_create=True), ensure_ascii=False)}")
        if args.prune:
            for iid, rid in to_prune[:5]:
                print(f"  剪枝删  {rid} <- 商品ID {iid}")
        return

    # 更新（逐条，串行 + 间隔）
    ok_u = err_u = 0
    for i, (e, rid) in enumerate(to_update, 1):
        try:
            lark(["+record-upsert", "--record-id", rid], field_payload(e, for_create=False))
            ok_u += 1
        except RuntimeError as ex:
            err_u += 1
            print(f"  ⚠ 更新失败 {e['itemId']}: {ex}")
        if i % 50 == 0:
            print(f"  更新进度 {i}/{len(to_update)}")
        time.sleep(args.delay)

    # 新建（batch-create，200/批）
    ok_c = err_c = 0
    FIELDS = ["商品ID", "闲鱼账号", "店铺名", "商品标题", "商品链接", "价格", "直购价", "浏览数", "想要数",
              "小刀价数量", "无增长天数", "下架权重", "在售状态", "采集错误", "采集时间"]
    for b in range(0, len(to_create), 200):
        batch = to_create[b:b + 200]
        rows = [[field_payload(e, for_create=True)[k] for k in FIELDS] for e in batch]
        try:
            lark(["+record-batch-create"], {"fields": FIELDS, "rows": rows})
            ok_c += len(batch)
        except RuntimeError as ex:
            err_c += len(batch)
            print(f"  ⚠ 批量新建失败（{b}-{b+len(batch)}）: {ex}")
        time.sleep(max(args.delay, 0.5))

    # 剪枝：删除同账号里不在在售集合的孤儿行（卖掉/下架的）
    ok_p = err_p = 0
    if args.prune and to_prune:
        for b in range(0, len(to_prune), 100):
            batch = to_prune[b:b + 100]
            cmd = ["+record-delete", "--yes"]
            for _iid, rid in batch:
                cmd += ["--record-id", rid]
            try:
                lark(cmd)
                ok_p += len(batch)
            except RuntimeError as ex:
                err_p += len(batch)
                print(f"  ⚠ 批量删除失败（{b}-{b+len(batch)}）: {ex}")
            time.sleep(max(args.delay, 0.5))

    print(f"\n完成。更新成功 {ok_u} 失败 {err_u} | 新建成功 {ok_c} 失败 {err_c}"
          + (f" | 剪枝删 {ok_p} 失败 {err_p}" if args.prune else ""))


if __name__ == "__main__":
    main()
