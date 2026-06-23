#!/usr/bin/env python3
"""
闲鱼商品指标只读采集 v2
通过 Chrome CDP (port 9221) 连接已登录的 Profile，采集商品详情页指标。

数据源：
- 列表页 API (mtop.idle.web.xyh.item.list) → itemId, title, price, categoryId, status
- 详情页 DOM → 浏览数, 小刀价, 直接买价格, 品牌/成色等属性
"""

import asyncio
import json
import re
import csv
import os
import sys
import time
from datetime import datetime

try:
    import websockets
except ImportError:
    print("ERROR: pip install websockets")
    sys.exit(1)

# ─── Config ──────────────────────────────────────────────────────────
CDP_PORT = 9221
BASE_DIR = "/Volumes/GPFS/Users/a1234/Desktop/Coding/goofish"
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_JSON = os.path.join(DATA_DIR, f"goofish-account-item-metrics-account-01-{TODAY}.json")
OUTPUT_CSV = os.path.join(DATA_DIR, f"goofish-account-item-metrics-account-01-{TODAY}.csv")
CHECKPOINT_FILE = os.path.join(BASE_DIR, f".goofish-collect-checkpoint-{TODAY}.json")

# Timing
DETAIL_WAIT = 4        # seconds to wait for detail page to render
SCROLL_WAIT = 1.5      # seconds between scrolls on list page
SAVE_EVERY = 10        # checkpoint every N items

# ─── CDP Helpers ─────────────────────────────────────────────────────
_msg_id = 0

async def send_cmd(ws, method, params=None):
    global _msg_id
    _msg_id += 1
    cmd = {"id": _msg_id, "method": method}
    if params:
        cmd["params"] = params
    await ws.send(json.dumps(cmd))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == cmd["id"]:
            return resp
        # skip events

async def evaluate(ws, expression, await_promise=False):
    params = {"expression": expression, "returnByValue": True}
    if await_promise:
        params["awaitPromise"] = True
    result = await send_cmd(ws, "Runtime.evaluate", params)
    return result.get("result", {}).get("result", {}).get("value")

# ─── Step 1: Collect item URLs from personal page ────────────────────
async def collect_item_urls(ws):
    """Navigate to personal page, scroll through 在售 and 已售出, collect all item URLs."""
    print("[1/4] Navigating to personal page...")
    await evaluate(ws, "window.location.href = 'https://www.goofish.com/personal'")
    await asyncio.sleep(5)
    
    # Verify we're logged in
    title = await evaluate(ws, "document.title")
    print(f"  Page title: {title}")
    
    # Get stats from page
    stats = await evaluate(ws, """
    (function() {
        var text = document.body.innerText;
        var total = text.match(/宝贝\\n(\\d+)/);
        var onsale = text.match(/在售(\\d+)/);
        var sold = text.match(/已售出(\\d+)/);
        return JSON.stringify({
            total: total ? total[1] : null,
            onsale: onsale ? onsale[1] : null,
            sold: sold ? sold[1] : null
        });
    })()
    """)
    if stats:
        s = json.loads(stats)
        print(f"  Stats: total={s['total']}, onsale={s['onsale']}, sold={s['sold']}")
    
    # Collect URLs from list API by scrolling
    all_items = {}
    
    for tab_name in ["在售", "已售出"]:
        print(f"\n[1/4] Collecting {tab_name} items...")
        
        # Click on the tab
        if tab_name == "已售出":
            await evaluate(ws, """
            (function() {
                var tabs = document.querySelectorAll('[class*="tabItem"], [class*="tab-item"]');
                for (var t of tabs) {
                    if (t.innerText.includes('已售出')) {
                        t.click();
                        return 'clicked 已售出';
                    }
                }
                // Try broader selector
                var all = document.querySelectorAll('*');
                for (var el of all) {
                    if (el.innerText === '已售出' && el.children.length === 0) {
                        el.click();
                        return 'clicked 已售出 (broad)';
                    }
                }
                return 'not found';
            })()
            """)
            await asyncio.sleep(3)
        
        # Intercept the item list API response
        await send_cmd(ws, "Network.enable")
        
        # Scroll to load all items
        prev_count = 0
        no_change_count = 0
        max_scrolls = 100
        
        for scroll_i in range(max_scrolls):
            # Collect any API responses that came in
            # Scroll down
            await evaluate(ws, "window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(SCROLL_WAIT)
            
            # Count visible items
            count = await evaluate(ws, """
            (function() {
                var cards = document.querySelectorAll('[class*="cardWarp"]');
                return cards.length;
            })()
            """)
            count = count or 0
            
            if count == prev_count:
                no_change_count += 1
                if no_change_count >= 3:
                    break
            else:
                no_change_count = 0
                if scroll_i % 10 == 0:
                    print(f"  Scrolled {scroll_i+1} times, {count} cards visible...")
            prev_count = count
        
        # Now collect item URLs from DOM
        items = await evaluate(ws, """
        (function() {
            var links = document.querySelectorAll('a[href*="goofish.com/item"]');
            var items = [];
            var seen = new Set();
            for (var link of links) {
                var href = link.href;
                var match = href.match(/id=(\\d+)/);
                if (match && !seen.has(match[1])) {
                    seen.add(match[1]);
                    var card = link.closest('[class*="cardWarp"]');
                    var text = card ? card.innerText : link.innerText;
                    var priceMatch = text.match(/¥\\s*(\\d+\\.?\\d*)/);
                    var knifeMatch = text.match(/(\\d+)人小刀价/);
                    var titleEl = card ? card.querySelector('[class*="main-title"], [class*="row1"]') : null;
                    var title = titleEl ? titleEl.innerText.trim() : text.split('\\n')[0].trim();
                    items.push({
                        itemId: match[1],
                        title: title.substring(0, 100),
                        price: priceMatch ? priceMatch[1] : null,
                        knifeCount: knifeMatch ? parseInt(knifeMatch[1]) : 0,
                        listStatus: '""" + tab_name + """'
                    });
                }
            }
            return JSON.stringify(items);
        })()
        """)
        
        if items:
            item_list = json.loads(items)
            for item in item_list:
                if item['itemId'] not in all_items:
                    all_items[item['itemId']] = item
            print(f"  {tab_name}: found {len(item_list)} unique items (total unique: {len(all_items)})")
    
    return all_items

# ─── Step 2: Visit detail pages ──────────────────────────────────────
async def collect_detail(ws, item_id, category_id):
    """Navigate to item detail page and extract metrics."""
    url = f"https://www.goofish.com/item?id={item_id}&categoryId={category_id}"
    
    await evaluate(ws, f"window.location.href = '{url}'")
    await asyncio.sleep(DETAIL_WAIT)
    
    # Extract detail data — ONLY from mainText (before "为你推荐")
    data = await evaluate(ws, """
    (function() {
        var text = document.body.innerText;

        // Check for error page
        if (text.includes('网络不见了') || text.includes('页面不见了')) {
            return JSON.stringify({error: 'page_error'});
        }

        // Check for login wall
        if (text.includes('请登录') || text.includes('扫码登录')) {
            return JSON.stringify({error: 'login_required'});
        }

        // ---- ONLY parse mainText: everything BEFORE "为你推荐" ----
        var recommendIdx = text.indexOf('为你推荐');
        var mainText = recommendIdx > 0 ? text.substring(0, recommendIdx) : text;

        // All regexes run against mainText ONLY — no full-page fallback
        var viewMatch      = mainText.match(/(\\d+)浏览/);
        var wantMatch      = mainText.match(/(\\d+)人想要/);
        var knifeMatch     = mainText.match(/(\\d+)人小刀价/);
        var priceMatch     = mainText.match(/¥\\s*(\\d+\\.?\\d+)/);
        var directBuyMatch = mainText.match(/直接买\\s*￥(\\d+\\.?\\d+)/);
        var brandMatch     = mainText.match(/牌[\\s\\n：:]+([^\\n]+)/);
        var conditionMatch = mainText.match(/成[\\s\\n]*色[\\s\\n：:]+([^\\n]+)/);

        return JSON.stringify({
            viewCount:      viewMatch      ? parseInt(viewMatch[1])  : null,
            wantCount:      wantMatch      ? parseInt(wantMatch[1])  : null,
            knifeCount:     knifeMatch     ? parseInt(knifeMatch[1]) : null,
            price:          priceMatch     ? priceMatch[1]           : null,
            directBuyPrice: directBuyMatch ? directBuyMatch[1]       : null,
            brand:          brandMatch     ? brandMatch[1].trim()    : null,
            condition:      conditionMatch ? conditionMatch[1].trim(): null,
            hasRemoveButton: mainText.includes('下架'),
            hasDeleteButton: mainText.includes('删除'),
            error: null
        });
    })()
    """)
    
    if data:
        return json.loads(data)
    return {"error": "eval_failed"}

# ─── Step 3: Guess categoryId ────────────────────────────────────────
# Since the list API gives categoryId, we store it. Fallback to a common one.
DEFAULT_CATEGORY = "50025445"

# ─── Main ────────────────────────────────────────────────────────────
async def main():
    import urllib.request
    
    # Check if Chrome is running
    try:
        tabs_raw = urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/list").read()
        tabs = json.loads(tabs_raw)
    except Exception as e:
        print(f"ERROR: Cannot connect to Chrome on port {CDP_PORT}: {e}")
        print("Start Chrome with:")
        print(f'  open -na "Google Chrome" --args --user-data-dir="...account-01" --remote-debugging-port={CDP_PORT}')
        return
    
    # Find the personal page tab (or any goofish tab)
    target_tab = None
    for tab in tabs:
        if tab.get("type") == "page" and "goofish.com" in tab.get("url", ""):
            target_tab = tab
            if "personal" in tab["url"]:
                break
    if not target_tab:
        target_tab = tabs[0] if tabs else None
    
    if not target_tab:
        print("ERROR: No browser tabs found")
        return
    
    ws_url = target_tab["webSocketDebuggerUrl"]
    print(f"Connecting to tab: {target_tab['url']}")
    
    async with websockets.connect(ws_url, max_size=50*1024*1024) as ws:
        # Step 1: Collect all item URLs from list page
        all_items = await collect_item_urls(ws)
        
        if not all_items:
            print("ERROR: No items found!")
            return
        
        print(f"\n[2/4] Total unique items to process: {len(all_items)}")
        
        # Load checkpoint
        done_items = {}
        if os.path.exists(CHECKPOINT_FILE):
            with open(CHECKPOINT_FILE) as f:
                done_items = json.load(f)
            print(f"  Resuming from checkpoint: {len(done_items)} items already done")
        
        # Step 2: Visit each detail page
        item_list = list(all_items.values())
        errors = 0
        success = 0
        
        for i, item in enumerate(item_list):
            item_id = item['itemId']
            
            if item_id in done_items:
                # Merge saved detail data
                item.update(done_items[item_id])
                success += 1
                continue
            
            cat_id = item.get('categoryId', DEFAULT_CATEGORY)
            print(f"[3/4] ({i+1}/{len(item_list)}) Fetching detail: {item_id} - {item['title'][:40]}...")
            
            detail = await collect_detail(ws, item_id, cat_id)
            
            if detail.get('error'):
                print(f"  ⚠ Error: {detail['error']}")
                item['collectError'] = detail['error']
                errors += 1
            else:
                item.update(detail)
                item['collectError'] = None
                success += 1
                vc = detail.get('viewCount')
                wc = detail.get('wantCount')
                kc = detail.get('knifeCount')
                print(f"  ✓ views={vc}, wants={wc}, knife={kc}, price={detail.get('price')}")
            
            # Save checkpoint
            done_items[item_id] = {k: v for k, v in item.items() if k != 'itemId'}
            if (i + 1) % SAVE_EVERY == 0:
                with open(CHECKPOINT_FILE, 'w') as f:
                    json.dump(done_items, f, ensure_ascii=False)
                print(f"  [checkpoint saved: {len(done_items)} items]")
            
            # Small delay between detail pages to be nice
            await asyncio.sleep(1)
        
        # Save final checkpoint
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(done_items, f, ensure_ascii=False)
        
        # Step 3: Write outputs
        print(f"\n[4/4] Writing output files...")
        
        # Prepare data
        results = []
        for item in item_list:
            results.append({
                "accountSlot": "account-01",
                "listStatus": item.get("listStatus", ""),
                "itemId": item["itemId"],
                "categoryId": item.get("categoryId", DEFAULT_CATEGORY),
                "detailUrl": f"https://www.goofish.com/item?id={item['itemId']}",
                "title": item.get("title", ""),
                "price": item.get("price"),
                "directBuyPrice": item.get("directBuyPrice"),
                "viewCount": item.get("viewCount"),
                "wantCount": item.get("wantCount"),
                "knifeCount": item.get("knifeCount"),
                "hasRemoveButton": item.get("hasRemoveButton", False),
                "hasDeleteButton": item.get("hasDeleteButton", False),
                "collectError": item.get("collectError"),
            })
        
        # Write JSON
        summary = {
            "collectedAt": datetime.now().isoformat(),
            "accountSlot": "account-01",
            "totalItems": len(results),
            "onsaleCount": sum(1 for r in results if r["listStatus"] == "在售"),
            "soldCount": sum(1 for r in results if r["listStatus"] == "已售出"),
            "detailSuccess": sum(1 for r in results if not r["collectError"]),
            "detailErrors": sum(1 for r in results if r["collectError"]),
            "withViewCount": sum(1 for r in results if r.get("viewCount") is not None and r["viewCount"] > 0),
            "withWantCount": sum(1 for r in results if r.get("wantCount") is not None and r["wantCount"] > 0),
            "withKnifeCount": sum(1 for r in results if r.get("knifeCount") is not None and r["knifeCount"] > 0),
            "totalViews": sum(r["viewCount"] for r in results if r.get("viewCount") is not None),
            "totalWants": sum(r["wantCount"] for r in results if r.get("wantCount") is not None),
            "totalKnife": sum(r["knifeCount"] for r in results if r.get("knifeCount") is not None),
            "items": results,
        }
        
        with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"  JSON: {OUTPUT_JSON}")
        
        # Write CSV
        csv_fields = ["accountSlot", "listStatus", "itemId", "categoryId", "title", "price",
                       "directBuyPrice", "viewCount", "wantCount", "knifeCount",
                       "hasRemoveButton", "hasDeleteButton", "collectError", "detailUrl"]
        with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(results)
        print(f"  CSV: {OUTPUT_CSV}")
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"采集完成！")
        print(f"{'='*60}")
        print(f"商品总数:       {summary['totalItems']}")
        print(f"在售:           {summary['onsaleCount']}")
        print(f"已售出:         {summary['soldCount']}")
        print(f"详情页成功:     {summary['detailSuccess']}")
        print(f"详情页失败:     {summary['detailErrors']}")
        print(f"有浏览数的商品: {summary['withViewCount']}")
        print(f"有想要数的商品: {summary['withWantCount']}")
        print(f"有小刀价的商品: {summary['withKnifeCount']}")
        print(f"浏览数合计:     {summary['totalViews']}")
        print(f"想要数合计:     {summary['totalWants']}")
        print(f"小刀价人数合计: {summary['totalKnife']}")
        print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
