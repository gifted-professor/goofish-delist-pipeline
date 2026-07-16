#!/usr/bin/env python3
"""闲鱼商品增量对比 + 下架建议台账 + 清单（Phase 1，纯本地，不碰飞书）

数据流：
    每日采集 JSON ──► 本地台账 goofish-item-state.json ──► 下架建议 CSV

台账 goofish-item-state.json 是商品状态和下架规则命中的唯一真相。每次跑：
  1. 读今日采集 JSON（默认取 data/ 里最新一份）
  2. 跟台账逐商品对比浏览数 / 想要数
  3. 更新无增长天数：今天涨了→归 0；今天没涨→ +1
  4. 输出 data/goofish-delist-suggestions-{date}.csv

关键规则（避免误判）：
  - 采集失败那天（collectError）不计数，沿用旧值。漏采 != 无增长。
  - wantCount=null 时只用 viewCount 判断，不把 null 当 0。
  - 已售出 / 今日列表里消失的商品：标状态、踢出建议清单、不计数。
  - 只有浏览数或想要数「上涨」算增长；持平或下降都按无增长 +1。
  - 低浏览量建议：首次发现满 5 天且浏览 < 50，或满 10 天且浏览 < 100。
  - 首次采集到的新商品默认视为当天发布；已有商品不会因重复采集而重置首次发现日。
  - 建议清单只供确认，不自动下架。

用法：
    python3 goofish-diff-state.py                 # 取最新一天，阈值默认 20
    python3 goofish-diff-state.py --no-growth-days 7
    python3 goofish-diff-state.py --date 2026-06-22
    python3 goofish-diff-state.py --dry-run       # 不写台账，只看清单
"""

import argparse
import csv
from datetime import date
import glob
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根（scripts/ 上一级），随目录搬动自适应
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_FILE = os.path.join(DATA_DIR, "goofish-item-state.json")

ONSALE = "在售"
SOLD = "已售出"
MISSING = "missing"  # 今日列表里没出现，可能已售出 / 已下架


def item_url(item_id):
    return f"https://www.goofish.com/item?id={item_id}"


FILE_RE = re.compile(r"goofish-account-item-metrics-(account-\d+)-(\d{4}-\d{2}-\d{2})\.json$")


def gather_inputs(date):
    """收集某一天所有账号的采集 JSON。

    返回 (run_date, items, ran_accounts, files)。items 每条带 _account；
    date 为 None 时取最新日期。某天可能只有部分账号跑过，ran_accounts 记录实际跑过的账号，
    用于「消失」判定——只有商品所属账号当天跑过，才可能把它标成 missing。
    """
    parsed = []  # (account, date, path)
    for p in glob.glob(os.path.join(DATA_DIR, "goofish-account-item-metrics-account-*-*.json")):
        m = FILE_RE.search(os.path.basename(p))
        if m:
            parsed.append((m.group(1), m.group(2), p))
    if not parsed:
        sys.exit(f"{DATA_DIR} 下没有采集 JSON")
    if not date:
        date = max(d for _, d, _ in parsed)
    day = [(acc, p) for acc, d, p in parsed if d == date]
    if not day:
        sys.exit(f"没有 {date} 的采集文件")

    items, ran_accounts, files = [], set(), []
    for acc, p in sorted(day):
        ran_accounts.add(acc)
        files.append(os.path.basename(p))
        with open(p, encoding="utf-8") as f:
            for it in json.load(f).get("items", []):
                it = dict(it)
                it["_account"] = it.get("accountSlot") or acc
                items.append(it)
    return date, items, sorted(ran_accounts), files


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


# 我们采集时打开商品详情页，闲鱼会把「浏览」+1（实测店主身份也照计）。正常每天采一次、
# collect 有断点同一天不重复访问，所以稳态下每个商品每天被我们自己 +1。判断「真涨」时要扣掉。
SELF_VIEW_PER_RUN = 1


def grew(today_view, today_want, prev_view, prev_want, self_view=SELF_VIEW_PER_RUN):
    """浏览数或想要数是否较上次「真实」上涨。null 一律跳过比较。
    浏览要涨过我们自己贡献的 self_view 才算真涨（扣除采集自身 +1 污染）；
    想要数打开详情页不会增加、是干净信号，照常 >0 即算涨。"""
    if (today_view is not None and prev_view is not None
            and today_view - prev_view > self_view):
        return True
    if today_want is not None and prev_want is not None and today_want > prev_want:
        return True
    return False


def days_since(first_seen, run_date):
    """按首次进入台账日期估算商品存续天数。"""
    try:
        start = date.fromisoformat(str(first_seen)[:10])
        end = date.fromisoformat(str(run_date)[:10])
    except (TypeError, ValueError):
        return None
    return max(0, (end - start).days)


def delist_reasons(entry, run_date, no_growth_days, min_age_days=5,
                   low_view_count=50, extended_age_days=10,
                   extended_low_view_count=100):
    """返回当前商品命中的下架建议规则；这里只生成建议，不执行下架。"""
    reasons = []
    age = days_since(entry.get("firstSeen"), run_date)
    entry["ageDays"] = age
    view = entry.get("lastView")
    try:
        view = int(view) if view is not None else None
    except (TypeError, ValueError):
        view = None

    if age is not None and view is not None:
        if age >= min_age_days and view < low_view_count:
            reasons.append(f"发布≥{min_age_days}天且浏览<{low_view_count}")
        if age >= extended_age_days and view < extended_low_view_count:
            reasons.append(f"发布≥{extended_age_days}天且浏览<{extended_low_view_count}")

    if entry.get("noGrowthDays", 0) >= no_growth_days:
        reasons.append(f"无增长≥{no_growth_days}天")
    return reasons


def delist_score(entry):
    """计算 0-100 的下架权重；分数越高越建议人工确认下架。"""
    age = entry.get("ageDays")
    view = entry.get("lastView")
    if age is None:
        return None
    try:
        age = int(age)
    except (TypeError, ValueError):
        return None
    try:
        view = int(view) if view is not None else None
    except (TypeError, ValueError):
        view = None

    score = 0
    # 存续时间：5 天开始观察，10 天以上风险更高。
    if age >= 10:
        score += 30
    elif age >= 5:
        score += 20

    # 浏览量：低浏览量是主要信号。
    if view is not None:
        if view < 50:
            score += 35
        elif view < 100:
            score += 25
        elif view < 200:
            score += 10

    # 有明确互动时降低下架权重；null 表示未知，不按 0 处理。
    want = entry.get("lastWant")
    if want is not None:
        try:
            want = int(want)
            if want == 0:
                score += 15
            elif want <= 1:
                score += 8
        except (TypeError, ValueError):
            pass

    knife = entry.get("lastKnife")
    if knife is not None:
        try:
            knife = int(knife)
            if knife == 0:
                score += 10
            elif knife <= 1:
                score += 5
        except (TypeError, ValueError):
            pass

    no_growth = entry.get("noGrowthDays", 0)
    if no_growth >= 20:
        score += 10
    elif no_growth >= 5:
        score += 5

    # 新商品即使浏览量低，也不让评分过早变成高风险。
    if age < 5:
        score = min(score, 20)
    return min(score, 100)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-growth-days", type=int, default=20,
                    help="无增长天数 >= 该阈值进入下架建议（默认 20）")
    ap.add_argument("--date", default=None, help="指定采集日期 YYYY-MM-DD，默认取最新")
    ap.add_argument("--dry-run", action="store_true", help="不写台账，只预览建议清单")
    ap.add_argument("--min-age-days", type=int, default=5,
                    help="低浏览量规则的最低存续天数（默认 5）")
    ap.add_argument("--low-view-count", type=int, default=50,
                    help="第一档低浏览量阈值（默认 50）")
    ap.add_argument("--extended-age-days", type=int, default=10,
                    help="第二档低浏览量规则的最低存续天数（默认 10）")
    ap.add_argument("--extended-low-view-count", type=int, default=100,
                    help="第二档低浏览量阈值（默认 100）")
    args = ap.parse_args()
    N = args.no_growth_days

    run_date, items, ran_accounts, files = gather_inputs(args.date)

    state = load_state()
    today_ids = set()

    stats = {"new": 0, "grew": 0, "stalled": 0, "errored": 0, "sold": 0, "repeat": 0}

    for it in items:
        iid = it["itemId"]
        today_ids.add(iid)
        view = it.get("viewCount")
        want = it.get("wantCount")
        err = it.get("collectError")
        status = SOLD if it.get("listStatus") == SOLD else ONSALE

        is_new = iid not in state
        entry = state.get(iid, {
            "itemId": iid,
            "account": it.get("_account"),
            "noGrowthDays": 0,
            "lastView": None,
            "lastWant": None,
            "firstSeen": run_date,
            "lastError": None,
        })
        # 这条商品本运行日是否已经处理过（幂等：同一天重复跑不重复计数）
        already_today = (not is_new) and entry.get("lastUpdated") == run_date

        # 公共字段每天刷新（幂等）
        entry["account"] = it.get("_account")
        entry["title"] = it.get("title")
        if it.get("sellerName"):
            entry["sellerName"] = it.get("sellerName")
        entry["url"] = it.get("url") or item_url(iid)
        entry["price"] = it.get("price")
        entry["directBuyPrice"] = it.get("directBuyPrice")
        entry["lastKnife"] = it.get("knifeCount")
        entry["status"] = status
        entry["lastUpdated"] = run_date
        entry["lastError"] = err

        if already_today:
            # 同一天重复跑：保留已算好的 noGrowthDays / 基线，只刷新展示字段
            stats["repeat"] += 1
        elif err:
            # 采集失败：不计数，不更新基线，沿用旧值
            stats["errored"] += 1
        elif status == SOLD:
            # 已售出：不计数，仍记录最新数值
            entry["noGrowthDays"] = 0
            entry["lastView"] = view if view is not None else entry.get("lastView")
            entry["lastWant"] = want if want is not None else entry.get("lastWant")
            stats["sold"] += 1
        elif is_new:
            # 新商品：首次采集日默认视为发布日，建基线，存续天数从 0 开始。
            entry["lastView"] = view
            entry["lastWant"] = want
            stats["new"] += 1
        else:
            prev_view = entry.get("lastView")
            prev_want = entry.get("lastWant")
            if grew(view, want, prev_view, prev_want):
                entry["noGrowthDays"] = 0
                stats["grew"] += 1
            else:
                entry["noGrowthDays"] = entry.get("noGrowthDays", 0) + 1
                stats["stalled"] += 1
            # 刷新基线：want 为 null 时保留上次已知值，便于明天对比
            entry["lastView"] = view if view is not None else prev_view
            entry["lastWant"] = want if want is not None else prev_want

        state[iid] = entry

    # 台账里有、今日列表没出现的商品 → 可能已售出/已下架
    # 多账号关键点：只有商品所属账号「当天确实跑过」，缺席才算消失；
    # 否则只是那个账号今天没采，不能误标。（老台账没有 account 字段，按 account-01 处理）
    vanished = 0
    for iid, entry in state.items():
        if iid in today_ids or entry.get("status") in (MISSING, SOLD):
            continue
        if (entry.get("account") or "account-01") in ran_accounts:
            entry["status"] = MISSING
            entry["lastSeenMissing"] = run_date
            vanished += 1

    # 建议清单：在售 + 今日采集成功 + 命中任一删除规则。
    suggestions = []
    for iid in today_ids:
        e = state[iid]
        reasons = delist_reasons(
            e,
            run_date,
            N,
            min_age_days=args.min_age_days,
            low_view_count=args.low_view_count,
            extended_age_days=args.extended_age_days,
            extended_low_view_count=args.extended_low_view_count,
        )
        e["delistReasons"] = reasons
        e["delistEligible"] = bool(reasons)
        e["delistScore"] = delist_score(e)
        if e["status"] == ONSALE and not e.get("lastError") and reasons:
            suggestions.append(e)
    suggestions.sort(key=lambda e: (
        -(e.get("delistScore") or 0),
        -len(e.get("delistReasons", [])),
        -(e.get("ageDays") or 0),
        e.get("lastView") if e.get("lastView") is not None else 10**9,
    ))

    # 输出建议 CSV
    out_csv = os.path.join(DATA_DIR, f"goofish-delist-suggestions-{run_date}.csv")
    if not args.dry_run:
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["商品ID", "闲鱼账号", "标题", "链接", "浏览数", "想要数",
                        "无增长天数", "首次发现", "存续天数", "下架权重", "下架建议原因", "价格"])
            for e in suggestions:
                w.writerow([e["itemId"], e.get("account"), e.get("title"), e.get("url"),
                            e.get("lastView"), e.get("lastWant"),
                            e.get("noGrowthDays"), e.get("firstSeen"), e.get("ageDays"),
                            e.get("delistScore"),
                            "；".join(e.get("delistReasons", [])), e.get("price")])
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    # 终端汇报
    print(f"采集日期:        {run_date}")
    print(f"今日账号:        {', '.join(ran_accounts)}  ({len(files)} 个文件)")
    print(f"阈值 N:          {N} 天无增长")
    print(f"今日商品:        {len(today_ids)}")
    print(f"  新增基线:      {stats['new']}")
    print(f"  有增长:        {stats['grew']}")
    print(f"  无增长 +1:     {stats['stalled']}")
    print(f"  采集失败跳过:  {stats['errored']}")
    print(f"  同日重复跳过:  {stats['repeat']}")
    print(f"  已售出:        {stats['sold']}")
    print(f"  本次消失:      {vanished}")
    print(f"台账商品累计:    {len(state)}")
    print(f"下架建议:        {len(suggestions)} 个（分层低浏览量规则 + 无增长 >= {N} 天）")
    # 机器可读摘要（daily.sh 据此判断是否触发全量同步：新增/消失大 = 在售集合变动大）
    print(f"[SUMMARY] onsale={len(today_ids)} new={stats['new']} grew={stats['grew']} "
          f"stalled={stats['stalled']} sold={stats['sold']} vanished={vanished} "
          f"suggestions={len(suggestions)}")
    if args.dry_run:
        print("[dry-run] 未写台账/CSV")
    else:
        print(f"台账:            {STATE_FILE}")
        print(f"建议清单:        {out_csv}")
    if suggestions:
        print("\n  前 10 个建议下架：")
        for e in suggestions[:10]:
            t = (e.get("title") or "")[:30]
            print(f"    {e['itemId']}  权重{e.get('delistScore')}  存续{e.get('ageDays')}天  浏览{e.get('lastView')} "
                  f"原因：{'；'.join(e.get('delistReasons', []))}  {t}")


if __name__ == "__main__":
    main()
