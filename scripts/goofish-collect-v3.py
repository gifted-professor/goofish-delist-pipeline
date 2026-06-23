#!/usr/bin/env python3
"""闲鱼商品指标采集 v3 — 修正 wantCount 污染 + 文件日志"""

import argparse
import asyncio
import json
import csv
import os
import re
import sys
import urllib.request
from datetime import datetime

import websockets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 项目根（scripts/ 上一级），随目录搬动自适应
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")

# 这些在 __main__ 里按 --account / --port 赋值；默认 account-01 / 9221（向后兼容）
ACCOUNT = "account-01"
CDP_PORT = 9221
INCLUDE_SOLD = False   # 默认只采在售；--include-sold 才连已售出一起采
OUTPUT_JSON = OUTPUT_CSV = CHECKPOINT = LOG_FILE = None


def derive_port(account, port):
    """没显式给端口时，按 account-NN 推 9220+NN（account-01→9221）。"""
    if port is not None:
        return port
    m = re.match(r"account-(\d+)$", account)
    return 9220 + int(m.group(1)) if m else 9221


def configure(account, port):
    global ACCOUNT, CDP_PORT, OUTPUT_JSON, OUTPUT_CSV, CHECKPOINT, LOG_FILE
    ACCOUNT = account
    CDP_PORT = port
    OUTPUT_JSON = os.path.join(DATA_DIR, f"goofish-account-item-metrics-{account}-{TODAY}.json")
    OUTPUT_CSV  = os.path.join(DATA_DIR, f"goofish-account-item-metrics-{account}-{TODAY}.csv")
    CHECKPOINT  = os.path.join(BASE_DIR, f".goofish-checkpoint-{account}-{TODAY}.json")
    LOG_FILE    = os.path.join(BASE_DIR, f".goofish-collect-{account}.log")

DETAIL_WAIT = 4
SCROLL_WAIT = 2.0      # 店铺页懒加载慢，给足时间
STALL_LIMIT = 7        # 连续多少次无新增才判定到底（原 3 太急，店铺页会误停在第一屏）
SAVE_EVERY  = 10

# 统计当前已加载的唯一商品数（按详情链接 id 去重），比 cardWarp 类名更稳
COUNT_UNIQUE_JS = (
    'new Set(Array.from(document.querySelectorAll(\'a[href*="goofish.com/item"]\'))'
    '.map(function(a){var m=a.href.match(/id=(\\d+)/);return m?m[1]:null;})'
    '.filter(Boolean)).size'
)

# 读店铺自己的「在售N / 已售出M」筛选 chip 数字 —— 这是闲鱼后台权威数，拿来当滚动加载目标，
# 根治"懒加载滚不到底、第一屏 20 个就判到底"的少采问题。
CHIP_TARGETS_JS = (
    '(function(){var on=null,sold=null;'
    'document.querySelectorAll("*").forEach(function(e){'
    'if(e.children.length!==0)return;'
    'var t=(e.innerText||"").trim();'
    'var m1=t.match(/^在售(\\d+)$/);if(m1)on=parseInt(m1[1]);'
    'var m2=t.match(/^已售出(\\d+)$/);if(m2)sold=parseInt(m2[1]);});'
    'return JSON.stringify({onsale:on,sold:sold});})()'
)

# 点「已售出」筛选 chip（叶子节点、文本以"已售出"开头）
CLICK_SOLD_JS = (
    '(function(){var a=document.querySelectorAll("*");for(var e of a){'
    'var t=(e.innerText||"").trim();'
    'if(e.children.length===0&&t.indexOf("已售出")===0){e.click();return t}}return "nf"})()'
)


def collect_items_js():
    """枚举当前视图所有商品卡片（id/标题/价格/小刀价）。status 在 collect_list 里按是否已售出统一打标。"""
    return (
        '(function(){'
        'var links=document.querySelectorAll(\'a[href*="goofish.com/item"]\');'
        'var items=[],seen=new Set();'
        'for(var l of links){'
        'var m=l.href.match(/id=(\\d+)/);'
        'if(m&&!seen.has(m[1])){'
        'seen.add(m[1]);'
        'var c=l.closest(\'[class*="cardWarp"]\');'
        'var t=c?c.innerText:l.innerText;'
        'var pm=t.match(/¥\\s*(\\d+\\.?\\d*)/);'
        'var km=t.match(/(\\d+)人小刀价/);'
        'var te=c?c.querySelector(\'[class*="main-title"],[class*="row1"]\'):null;'
        'var ti=te?te.innerText.trim():t.split("\\n")[0].trim();'
        'items.push({i:m[1],t:ti.substring(0,100),p:pm?pm[1]:null,k:km?parseInt(km[1]):0,s:"在售"});}}'
        'return JSON.stringify(items);})()'
    )

_msg_id = 0

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

async def cdp(ws, method, params=None):
    global _msg_id; _msg_id += 1
    cmd = {"id": _msg_id, "method": method}
    if params: cmd["params"] = params
    await ws.send(json.dumps(cmd))
    while True:
        r = json.loads(await ws.recv())
        if r.get("id") == cmd["id"]: return r

async def ev(ws, expr):
    r = await cdp(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("result", {}).get("value")


async def scroll_until(ws, target, tab_name):
    """滚动加载直到唯一商品数 >= target（用店铺 chip 数当目标，根治少采）。
    没拿到 target 时退回 stall 判定到底；有 target 但卡住会多撑几轮再放弃并告警。"""
    prev = 0; stall = 0
    for i in range(600):
        await ev(ws, "window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(SCROLL_WAIT)
        # 每隔几次往上顶一下再到底，重新触发懒加载（店铺页 IntersectionObserver 偶尔不补货）
        if i % 4 == 3:
            await ev(ws, "window.scrollBy(0, -800)")
            await asyncio.sleep(0.6)
            await ev(ws, "window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(SCROLL_WAIT)
        cnt = await ev(ws, COUNT_UNIQUE_JS) or 0
        if target and cnt >= target:
            log(f"  [{tab_name}] 载满 {cnt}/{target} ✓")
            return cnt
        if cnt == prev:
            stall += 1
            give_up = (STALL_LIMIT + 8) if target else STALL_LIMIT
            if stall >= give_up:
                if target and cnt < target:
                    log(f"  [{tab_name}] ⚠ 滚动卡在 {cnt}/{target}（没到目标！）")
                else:
                    log(f"  [{tab_name}] 到底 {cnt}")
                return cnt
        else:
            stall = 0
            if i % 5 == 0:
                log(f"  [{tab_name}] scroll {i}: {cnt}" + (f"/{target}" if target else ""))
        prev = cnt
    return prev


async def collect_list(ws):
    log("Navigating to personal page...")
    # 关键：被遮挡/后台的 Chrome 标签页 visibilityState=hidden，懒加载(IntersectionObserver)被节流，
    # 滚动加载不出新商品（曾把 153 件采成 20）。setFocusEmulationEnabled 让渲染器当页面有焦点/可见，
    # 懒加载恢复正常。bringToForeground / setWebLifecycleState 都无效，只有这个管用。
    try:
        await cdp(ws, "Emulation.setFocusEmulationEnabled", {"enabled": True})
    except Exception as e:
        log(f"  ⚠ setFocusEmulationEnabled 失败: {e}")
    await ev(ws, "window.location.href = 'https://www.goofish.com/personal'")
    await asyncio.sleep(6)
    title = await ev(ws, "document.title")
    vis = await ev(ws, "document.visibilityState")
    log(f"Title: {title}  visibility={vis}")

    # 读店铺自己的「在售N / 已售出M」chip 当滚动目标（权威数，根治懒加载少采）
    raw = await ev(ws, CHIP_TARGETS_JS)
    chips = json.loads(raw) if raw else {}
    n_onsale = chips.get("onsale")
    n_sold = chips.get("sold") or 0
    log(f"店铺 chip: 在售={n_onsale} 已售出={n_sold}")

    all_items = {}

    # 1) 默认「宝贝」视图 = 在售 + 已售出，滚到载满 (在售+已售出)
    baby_target = ((n_onsale or 0) + n_sold) or None
    await scroll_until(ws, baby_target, "宝贝")
    raw = await ev(ws, collect_items_js())
    for it in (json.loads(raw) if raw else []):
        all_items.setdefault(it["i"], it)
    log(f"  [宝贝] 采到 {len(all_items)}（目标 {baby_target}）")

    # 2) 点「已售出」chip，滚到载满 M，拿到已售出 id 集合
    sold_ids = set()
    if n_sold > 0:
        await ev(ws, CLICK_SOLD_JS)
        await asyncio.sleep(3)
        await scroll_until(ws, n_sold, "已售出")
        raw = await ev(ws, collect_items_js())
        for it in (json.loads(raw) if raw else []):
            sold_ids.add(it["i"])
            all_items.setdefault(it["i"], it)  # 极少数只在已售出视图出现的也收进来
        log(f"  [已售出] 采到 {len(sold_ids)}（目标 {n_sold}）")

    # 3) 统一打标：在已售出集合里的 → 已售出，其余 → 在售
    for iid, it in all_items.items():
        it["s"] = "已售出" if iid in sold_ids else "在售"

    n_on = sum(1 for it in all_items.values() if it["s"] == "在售")
    log(f"  汇总: 在售 {n_on} / 已售出 {len(sold_ids)} / 总 {len(all_items)}"
        + (f"  （chip 在售={n_onsale}，{'一致✓' if n_onsale==n_on else '不一致⚠'}）" if n_onsale is not None else ""))
    # INCLUDE_SOLD=False（默认）时只留在售，把已售出从待处理列表剔除；
    # --include-sold 时保留全部（已售出仍打标已售出，便于飞书标记）。
    if not INCLUDE_SOLD:
        all_items = {k: v for k, v in all_items.items() if v["s"] == "在售"}
        log(f"  仅在售模式：保留 {len(all_items)} 件在售")
    return all_items, n_onsale, n_on


async def collect_detail(ws, item_id):
    url = f"https://www.goofish.com/item?id={item_id}&categoryId=50025445"
    await ev(ws, f"window.location.href = '{url}'")
    await asyncio.sleep(DETAIL_WAIT)

    js_detail = (
        '(function(){'
        'var t=document.body.innerText;'
        'if(t.indexOf("网络不见了")>=0||t.indexOf("页面不见了")>=0)'
        'return JSON.stringify({e:"page_err"});'
        'if(t.indexOf("请登录")>=0||t.indexOf("扫码登录")>=0)'
        'return JSON.stringify({e:"login"});'
        'var ri=t.indexOf("为你推荐");'
        'var m=ri>0?t.substring(0,ri):t;'
        'var vm=m.match(/(\\d+)浏览/);'
        'var wm=m.match(/(\\d+)人想要/);'
        'var km=m.match(/(\\d+)人小刀价/);'
        'var pm=m.match(/¥\\s*(\\d+\\.?\\d+)/);'
        'var dm=m.match(/直接买\\s*￥(\\d+\\.?\\d+)/);'
        'return JSON.stringify({'
        'v:vm?parseInt(vm[1]):null,'
        'w:wm?parseInt(wm[1]):null,'
        'k:km?parseInt(km[1]):null,'
        'p:pm?pm[1]:null,'
        'd:dm?dm[1]:null,'
        'e:null});})()'
    )
    raw = await ev(ws, js_detail)
    if raw:
        return json.loads(raw)
    return {"e": "eval_fail"}


async def main():
    # Clear log
    with open(LOG_FILE, "w") as f:
        f.write(f"=== Goofish Collect v3 — {TODAY} ===\n")

    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list").read())
    page_tabs = [t for t in tabs if t.get("type") == "page"]
    if not page_tabs:
        # 窗口被关、没有可用标签页时，通过 CDP 新建一个（自愈，不用人工重开窗口）
        log("无可用标签页，CDP 新建一个 personal 页")
        req = urllib.request.Request(
            f"http://127.0.0.1:{CDP_PORT}/json/new?https://www.goofish.com/personal", method="PUT")
        page_tabs = [json.loads(urllib.request.urlopen(req).read())]
    tab = (next((t for t in page_tabs if "personal" in t.get("url", "")), None)
           or next((t for t in page_tabs if "goofish" in t.get("url", "")), None)
           or page_tabs[0])
    log(f"Tab: {tab.get('url', '')[:80]}")

    async with websockets.connect(tab["webSocketDebuggerUrl"], max_size=50*1024*1024) as ws:
        all_items, n_onsale, n_on = await collect_list(ws)
        total = len(all_items)
        log(f"\nTotal items to process: {total}")
        # ⚠ 完整性闸：采集残缺时绝不写文件，并以非零退出让 daily.sh 跳过该号。
        # 否则残缺结果进 diff-state → 没采到的在售被误判 MISSING → push --prune 误删飞书行（一次抖动删几百行）。
        if n_onsale is None:
            log("ERROR: 读不到店铺「在售」chip（页面异常/重定向/掉登录？），判定采集不完整，不写文件。")
            sys.exit(2)
        if total == 0:
            log("ERROR: No items found! 不写文件。")
            sys.exit(2)
        if not INCLUDE_SOLD and n_on < n_onsale:
            log(f"ERROR: 在售只采到 {n_on}/{n_onsale}（没到店铺 chip 数），判定采集不完整，"
                f"不写文件以免 diff-state 误标 MISSING / prune 误删。请重采该号。")
            sys.exit(3)

        done = {}
        if os.path.exists(CHECKPOINT):
            with open(CHECKPOINT) as f:
                done = json.load(f)
            log(f"Checkpoint: {len(done)} already done")

        items_list = list(all_items.values())
        errors = 0

        for idx, it in enumerate(items_list):
            iid = it["i"]
            if iid in done:
                continue

            log(f"[{idx+1}/{total}] {iid} — {it['t'][:45]}")
            detail = await collect_detail(ws, iid)
            done[iid] = detail

            if detail.get("e"):
                errors += 1
                log(f"  ⚠ {detail['e']}")
            else:
                log(f"  ✓ v={detail.get('v')} w={detail.get('w')} k={detail.get('k')} p={detail.get('p')} d={detail.get('d')}")

            if (idx + 1) % SAVE_EVERY == 0:
                with open(CHECKPOINT, "w") as f:
                    json.dump(done, f, ensure_ascii=False)
                log(f"  [checkpoint: {len(done)}]")

        with open(CHECKPOINT, "w") as f:
            json.dump(done, f, ensure_ascii=False)

        # Build results
        results = []
        for it in items_list:
            iid = it["i"]
            dd = done.get(iid, {})
            results.append({
                "accountSlot": ACCOUNT,
                "listStatus": it["s"],
                "itemId": iid,
                "title": it["t"],
                "url": f"https://www.goofish.com/item?id={iid}",
                "price": dd.get("p") or it.get("p"),
                "directBuyPrice": dd.get("d"),
                "viewCount": dd.get("v"),
                "wantCount": dd.get("w"),
                "knifeCount": dd.get("k") if dd.get("k") is not None else it.get("k"),
                "collectError": dd.get("e"),
                "collectedDate": TODAY,
            })

        def safe_sum(key):
            return sum(r[key] for r in results if r.get(key) is not None)

        summary = {
            "collectedAt": datetime.now().isoformat(),
            "totalItems": len(results),
            "onsaleCount": sum(1 for r in results if r["listStatus"] == "在售"),
            "soldCount": sum(1 for r in results if r["listStatus"] == "已售出"),
            "detailSuccess": sum(1 for r in results if not r["collectError"]),
            "detailErrors": sum(1 for r in results if r["collectError"]),
            "withViewCount": sum(1 for r in results if r.get("viewCount") is not None and r["viewCount"] > 0),
            "withWantCount": sum(1 for r in results if r.get("wantCount") is not None and r["wantCount"] > 0),
            "withKnifeCount": sum(1 for r in results if r.get("knifeCount") is not None and r["knifeCount"] > 0),
            "totalViews": safe_sum("viewCount"),
            "totalWants": safe_sum("wantCount"),
            "totalKnife": safe_sum("knifeCount"),
            "items": results,
        }

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        fields = ["accountSlot","listStatus","itemId","title","url","price","directBuyPrice",
                   "viewCount","wantCount","knifeCount","collectError","collectedDate"]
        with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(results)

        log("=" * 50)
        log("采集完成!")
        log(f"商品总数:       {summary['totalItems']}")
        log(f"在售:           {summary['onsaleCount']}")
        log(f"已售出:         {summary['soldCount']}")
        log(f"详情成功:       {summary['detailSuccess']}")
        log(f"详情失败:       {summary['detailErrors']}")
        log(f"有浏览数:       {summary['withViewCount']}")
        log(f"有想要数:       {summary['withWantCount']}")
        log(f"有小刀价:       {summary['withKnifeCount']}")
        log(f"浏览数合计:     {summary['totalViews']}")
        log(f"想要数合计:     {summary['totalWants']}")
        log(f"小刀价合计:     {summary['totalKnife']}")
        log(f"JSON: {OUTPUT_JSON}")
        log(f"CSV:  {OUTPUT_CSV}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="闲鱼商品指标只读采集 v3")
    ap.add_argument("--account", default="account-01", help="账号槽位，默认 account-01")
    ap.add_argument("--port", type=int, default=None,
                    help="CDP 调试端口；不填按 account-NN 推 9220+NN")
    ap.add_argument("--include-sold", action="store_true",
                    help="连「已售出」一起采；默认只采在售")
    args = ap.parse_args()
    INCLUDE_SOLD = args.include_sold
    configure(args.account, derive_port(args.account, args.port))
    print(f"[account={ACCOUNT} port={CDP_PORT}] -> {os.path.basename(OUTPUT_JSON)}")
    asyncio.run(main())
