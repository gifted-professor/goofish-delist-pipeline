#!/usr/bin/env python3
"""Probe whether Goofish IM can be traversed to list/message boundaries.

The report intentionally avoids chat text. It stores hashes, counts, scroll
positions, and boundary flags so we can decide whether a full CRM sync is
technically reachable through the logged-in web UI.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import websockets


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out"
IM_URL = "https://www.goofish.com/im"


def port_for_account(account: str) -> int:
    m = re.search(r"(\d+)$", account)
    return 9220 + int(m.group(1)) if m else 9221


def http_json(port: int, path: str) -> dict[str, Any]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=4) as r:
        return json.loads(r.read())


def digest(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:length]


class CDP:
    def __init__(self, browser_ws: str):
        self.browser_ws = browser_ws
        self.ws = None
        self._id = 0

    async def __aenter__(self) -> "CDP":
        self.ws = await websockets.connect(self.browser_ws, max_size=None)
        return self

    async def __aexit__(self, *_exc: object) -> None:
        if self.ws:
            await self.ws.close()

    async def cmd(self, method: str, params: dict[str, Any] | None = None, sid: str | None = None, timeout: int = 30) -> dict[str, Any]:
        if not self.ws:
            raise RuntimeError("CDP websocket not connected")
        self._id += 1
        mid = self._id
        msg: dict[str, Any] = {"id": mid, "method": method, "params": params or {}}
        if sid:
            msg["sessionId"] = sid
        await self.ws.send(json.dumps(msg))
        while True:
            data = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=timeout))
            if data.get("id") == mid:
                if "error" in data:
                    raise RuntimeError(f"CDP {method} failed: {data['error']}")
                return data


async def page_eval(cdp: CDP, sid: str, expression: str, timeout: int = 30) -> Any:
    res = await cdp.cmd(
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
        sid,
        timeout=timeout,
    )
    payload = res.get("result", {})
    if "exceptionDetails" in payload:
        raise RuntimeError(f"page eval failed: {payload['exceptionDetails']}")
    return payload.get("result", {}).get("value")


CONVERSATION_SNAPSHOT_JS = r"""
(() => {
  const holder = document.querySelector('.rc-virtual-list-holder')
    || [...document.querySelectorAll('*')].find(el => el.scrollHeight > el.clientHeight && /conversation|virtual-list/i.test(String(el.className || '')));
  const items = [...document.querySelectorAll('[class*=conversation-item]')];
  return {
    holder: holder ? {
      scrollTop: holder.scrollTop,
      scrollHeight: holder.scrollHeight,
      clientHeight: holder.clientHeight,
      atBottom: Math.ceil(holder.scrollTop + holder.clientHeight) >= holder.scrollHeight - 2
    } : null,
    visibleCount: items.length,
    items: items.map((el, visibleIndex) => {
      const raw = (el.innerText || '').trim().replace(/\s+/g, '\n');
      const titleEl = el.querySelector('[class*=title]');
      const summaryEl = el.querySelector('[class*=summary]');
      const rect = el.getBoundingClientRect();
      return {
        visibleIndex,
        rawHash: raw,
        isNotification: /通知消息|通知中心|系统通知/.test(raw),
        titleLen: titleEl ? titleEl.innerText.trim().length : 0,
        summaryLen: summaryEl ? summaryEl.innerText.trim().length : 0,
        top: Math.round(rect.top),
        height: Math.round(rect.height)
      };
    }).filter(x => x.rawHash)
  };
})()
"""


CONVERSATION_SCROLL_DOWN_JS = r"""
(() => {
  const holder = document.querySelector('.rc-virtual-list-holder')
    || [...document.querySelectorAll('*')].find(el => el.scrollHeight > el.clientHeight && /conversation|virtual-list/i.test(String(el.className || '')));
  if (!holder) return { ok: false };
  const before = holder.scrollTop;
  const delta = Math.max(220, holder.clientHeight - 68);
  holder.scrollTop = Math.min(holder.scrollHeight, before + delta);
  holder.dispatchEvent(new Event('scroll', { bubbles: true }));
  return {
    ok: true,
    before,
    after: holder.scrollTop,
    scrollHeight: holder.scrollHeight,
    clientHeight: holder.clientHeight,
    atBottom: Math.ceil(holder.scrollTop + holder.clientHeight) >= holder.scrollHeight - 2
  };
})()
"""


CLICK_VISIBLE_CONVERSATION_JS = r"""
(visibleIndex => {
  const items = [...document.querySelectorAll('[class*=conversation-item]')];
  const item = items[visibleIndex];
  if (!item) return { clicked: false, visibleIndex };
  item.scrollIntoView({ block: 'nearest' });
  item.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  item.click();
  return { clicked: true, visibleIndex };
})
"""


MESSAGE_SNAPSHOT_JS = r"""
(() => {
  const main = document.querySelector('main[class*=chat-main]') || document.querySelector('main');
  const target = document.querySelector('#message-list-scrollable')
    || [...(main || document).querySelectorAll('*')]
      .filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 100)
      .sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight))[0]
    || null;
  const targetRect = target ? target.getBoundingClientRect() : null;
  const centerX = targetRect ? Math.max(targetRect.left + 8, Math.min(targetRect.right - 8, targetRect.left + targetRect.width / 2)) : null;
  const centerY = targetRect ? Math.max(targetRect.top + 8, Math.min(targetRect.bottom - 8, targetRect.top + targetRect.height / 2)) : null;
  const hitStack = targetRect ? document.elementsFromPoint(centerX, centerY).slice(0, 8).map(el => ({
    tag: el.tagName,
    id: el.id || '',
    className: String(el.className || '').slice(0, 180),
    role: el.getAttribute('role') || ''
  })) : [];
  const scrollers = [...(main || document).querySelectorAll('*')]
    .filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 100)
    .map((el, i) => ({ i, className: String(el.className || ''), scrollTop: el.scrollTop, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight }))
    .sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight));
  const list = main ? main.querySelector('.ant-list-items') : document.querySelector('.ant-list-items');
  const items = list ? [...list.querySelectorAll('li.ant-list-item')] : [];
  const rows = items.map((li, index) => {
    const row = li.querySelector('[class*=message-row]');
    const textEl = li.querySelector('[class*=message-text], [class*=msg-dx-content], [class*=msg-text-card], [class*=transaction-card], [class*=voice-container], [class*=image-container], [class*=video-container]');
    const raw = (li.innerText || '').trim().replace(/\s+/g, '\n');
    const text = textEl ? (textEl.innerText || '').trim() : raw;
    const cls = [row && row.className || '', textEl && textEl.className || ''].join(' ');
    let role = 'system';
    if (/right|mine/i.test(cls)) role = 'seller';
    else if (/left|other/i.test(cls)) role = 'customer';
    let kind = 'text';
    if (/image/i.test(cls)) kind = 'image';
    if (/voice/i.test(cls)) kind = 'voice';
    if (/video/i.test(cls)) kind = 'video';
    if (/card|transaction|dx-content/i.test(cls)) kind = 'card';
    return { index, role, kind, textLen: text.length, rawHash: raw };
  }).filter(x => x.rawHash || x.textLen);
  const primary = scrollers[0] || null;
  const targetClass = target ? String(target.className || '') : '';
  const isReverse = /reverse/i.test(targetClass);
  const minScrollTop = target ? Math.min(0, target.clientHeight - target.scrollHeight) : 0;
  const reachedOlderBoundary = target ? (isReverse ? target.scrollTop <= minScrollTop + 2 : target.scrollTop <= 2) : null;
  const targetInfo = target ? {
    id: target.id || '',
    tag: target.tagName,
    className: targetClass,
    isReverse,
    minScrollTop,
    scrollTop: target.scrollTop,
    scrollHeight: target.scrollHeight,
    clientHeight: target.clientHeight,
    reachedOlderBoundary,
    atTop: reachedOlderBoundary,
    atBottom: Math.ceil(target.scrollTop + target.clientHeight) >= target.scrollHeight - 2,
    rect: targetRect ? {
      left: Math.round(targetRect.left),
      top: Math.round(targetRect.top),
      right: Math.round(targetRect.right),
      bottom: Math.round(targetRect.bottom),
      width: Math.round(targetRect.width),
      height: Math.round(targetRect.height),
      centerX: Math.round(centerX),
      centerY: Math.round(centerY)
    } : null
  } : null;
  return {
    rows,
    scrollers,
    primary,
    target: targetInfo,
    hitStack,
    atTop: targetInfo ? targetInfo.reachedOlderBoundary : (primary ? primary.scrollTop <= 2 : null)
  };
})()
"""


MESSAGE_TARGET_JS = r"""
(() => {
  const main = document.querySelector('main[class*=chat-main]') || document.querySelector('main');
  const target = document.querySelector('#message-list-scrollable')
    || [...(main || document).querySelectorAll('*')]
      .filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 100)
      .sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight))[0]
    || null;
  if (!target) return { ok: false };
  const rect = target.getBoundingClientRect();
  const x = Math.max(rect.left + 8, Math.min(rect.right - 8, rect.left + rect.width / 2));
  const y = Math.max(rect.top + 8, Math.min(rect.bottom - 8, rect.top + rect.height / 2));
  const hitStack = document.elementsFromPoint(x, y).slice(0, 8).map(el => ({
    tag: el.tagName,
    id: el.id || '',
    className: String(el.className || '').slice(0, 180),
    role: el.getAttribute('role') || ''
  }));
  const targetClass = String(target.className || '');
  const isReverse = /reverse/i.test(targetClass);
  const minScrollTop = Math.min(0, target.clientHeight - target.scrollHeight);
  const reachedOlderBoundary = isReverse ? target.scrollTop <= minScrollTop + 2 : target.scrollTop <= 2;
  return {
    ok: true,
    id: target.id || '',
    tag: target.tagName,
    className: targetClass,
    isReverse,
    minScrollTop,
    x,
    y,
    scrollTop: target.scrollTop,
    scrollHeight: target.scrollHeight,
    clientHeight: target.clientHeight,
    reachedOlderBoundary,
    atTop: reachedOlderBoundary,
    atBottom: Math.ceil(target.scrollTop + target.clientHeight) >= target.scrollHeight - 2,
    rect: {
      left: Math.round(rect.left),
      top: Math.round(rect.top),
      right: Math.round(rect.right),
      bottom: Math.round(rect.bottom),
      width: Math.round(rect.width),
      height: Math.round(rect.height)
    },
    hitStack
  };
})()
"""


async def probe_conversation_list(cdp: CDP, sid: str, max_scrolls: int, wait_s: float) -> dict[str, Any]:
    seen: dict[str, dict[str, Any]] = {}
    steps = []
    stagnant = 0
    for step in range(max_scrolls + 1):
        snap = await page_eval(cdp, sid, CONVERSATION_SNAPSHOT_JS)
        before_count = len(seen)
        for item in (snap or {}).get("items", []):
            key = digest(item.pop("rawHash", ""))
            seen.setdefault(key, {"key": key, **item})
        new_count = len(seen) - before_count
        holder = (snap or {}).get("holder")
        step_row: dict[str, Any] = {
            "step": step,
            "uniqueCount": len(seen),
            "newCount": new_count,
            "visibleCount": (snap or {}).get("visibleCount"),
            "holder": holder,
        }
        if holder and holder.get("atBottom"):
            step_row["stopReason"] = "at-bottom-before-scroll"
            steps.append(step_row)
            break
        scroll = await page_eval(cdp, sid, CONVERSATION_SCROLL_DOWN_JS)
        step_row["scroll"] = scroll
        steps.append(step_row)
        await asyncio.sleep(wait_s)
        if not scroll or not scroll.get("ok") or scroll.get("before") == scroll.get("after"):
            stagnant += 1
        else:
            stagnant = 0
        if stagnant >= 2:
            break
    last_holder = steps[-1].get("holder") if steps else None
    return {
        "uniqueConversationCount": len(seen),
        "visibleConversationCount": steps[-1].get("visibleCount") if steps else None,
        "reachedBottom": bool(last_holder and last_holder.get("atBottom")) or bool(steps and (steps[-1].get("scroll") or {}).get("atBottom")),
        "steps": steps,
        "sampleKeys": list(seen.keys())[:12],
    }


async def choose_conversation_for_message_probe(cdp: CDP, sid: str, index: int) -> dict[str, Any]:
    snap = await page_eval(cdp, sid, CONVERSATION_SNAPSHOT_JS)
    items = (snap or {}).get("items", [])
    if not items:
        raise RuntimeError("no visible conversation items")
    selectable = [item for item in items if not item.get("isNotification")]
    if not selectable:
        raise RuntimeError("no visible customer conversation items; notification center is intentionally skipped")
    selected = selectable[min(index, len(selectable) - 1)]
    visible_index = int(selected["visibleIndex"])
    key = digest(selected.get("rawHash", ""))
    clicked = await page_eval(cdp, sid, f"{CLICK_VISIBLE_CONVERSATION_JS}({visible_index})")
    if not clicked or not clicked.get("clicked"):
        raise RuntimeError(f"failed to click visible conversation {visible_index}: {clicked}")
    await asyncio.sleep(3)
    return {
        "requestedSelectableIndex": index,
        "visibleIndex": visible_index,
        "conversationKey": key,
        "skippedNotifications": len(items) - len(selectable),
    }


async def dispatch_message_wheel(cdp: CDP, sid: str, delta_y: float) -> dict[str, Any]:
    target = await page_eval(cdp, sid, MESSAGE_TARGET_JS)
    if not target or not target.get("ok"):
        return {"ok": False, "target": target}
    x = float(target["x"])
    y = float(target["y"])
    await cdp.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseMoved", "x": x, "y": y, "button": "none"},
        sid,
    )
    await cdp.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseWheel", "x": x, "y": y, "deltaX": 0, "deltaY": delta_y},
        sid,
    )
    return {"ok": True, "deltaY": delta_y, "targetBeforeWheel": target}


async def probe_message_history(cdp: CDP, sid: str, max_scrolls: int, wait_s: float, wheel_delta_y: float) -> dict[str, Any]:
    seen: dict[str, dict[str, Any]] = {}
    steps = []
    stagnant = 0
    reached_top = False
    for step in range(max_scrolls + 1):
        snap = await page_eval(cdp, sid, MESSAGE_SNAPSHOT_JS)
        before_count = len(seen)
        for row in (snap or {}).get("rows", []):
            raw_hash = row.pop("rawHash", "")
            key = digest(json.dumps([row.get("role"), row.get("kind"), row.get("textLen"), raw_hash], ensure_ascii=False))
            seen.setdefault(key, {"key": key, **row})
        new_count = len(seen) - before_count
        primary = (snap or {}).get("target") or (snap or {}).get("primary")
        if snap and snap.get("atTop"):
            reached_top = True
        step_row: dict[str, Any] = {
            "step": step,
            "uniqueMessageCount": len(seen),
            "newCount": new_count,
            "renderedRows": len((snap or {}).get("rows", [])),
            "messageScroller": primary,
            "hitStack": (snap or {}).get("hitStack", []),
            "atTopBeforeScroll": (snap or {}).get("atTop"),
        }
        if reached_top and step > 0 and new_count == 0:
            step_row["stopReason"] = "at-top-stable"
            steps.append(step_row)
            break
        scroll = await dispatch_message_wheel(cdp, sid, wheel_delta_y)
        step_row["scroll"] = scroll
        steps.append(step_row)
        await asyncio.sleep(wait_s)
        after = await page_eval(cdp, sid, MESSAGE_TARGET_JS)
        step_row["targetAfterWait"] = after
        if after and after.get("atTop"):
            reached_top = True
        before_target = (scroll or {}).get("targetBeforeWheel") or {}
        if not scroll or not scroll.get("ok") or (after and before_target.get("scrollTop") == after.get("scrollTop")):
            stagnant += 1
        else:
            stagnant = 0
        if stagnant >= 3:
            break
    roles: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for row in seen.values():
        roles[row.get("role", "unknown")] = roles.get(row.get("role", "unknown"), 0) + 1
        kinds[row.get("kind", "unknown")] = kinds.get(row.get("kind", "unknown"), 0) + 1
    return {
        "uniqueMessageCount": len(seen),
        "reachedTop": reached_top,
        "roleCounts": roles,
        "kindCounts": kinds,
        "steps": steps,
        "sampleKeys": list(seen.keys())[:12],
    }


async def probe_message_histories(cdp: CDP, sid: str, indices: list[int], max_scrolls: int, wait_s: float, wheel_delta_y: float) -> list[dict[str, Any]]:
    results = []
    for index in indices:
        await page_eval(cdp, sid, "(() => { const h=document.querySelector('.rc-virtual-list-holder'); if (h) { h.scrollTop=0; h.dispatchEvent(new Event('scroll',{bubbles:true})); } return true; })()")
        await asyncio.sleep(wait_s)
        chosen = await choose_conversation_for_message_probe(cdp, sid, index)
        probe = await probe_message_history(cdp, sid, max_scrolls, wait_s, wheel_delta_y)
        results.append({"chosenConversation": chosen, **probe})
    return results


async def run(args: argparse.Namespace) -> dict[str, Any]:
    port = args.port or port_for_account(args.account)
    browser_ws = http_json(port, "/json/version")["webSocketDebuggerUrl"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = OUT_DIR / f"goofish-im-fullness-probe-{args.account}-{stamp}.json"

    async with CDP(browser_ws) as cdp:
        target_id = (await cdp.cmd("Target.createTarget", {"url": IM_URL}))["result"]["targetId"]
        sid = (await cdp.cmd("Target.attachToTarget", {"targetId": target_id, "flatten": True}))["result"]["sessionId"]
        await cdp.cmd("Page.enable", {}, sid)
        await cdp.cmd("Runtime.enable", {}, sid)
        await asyncio.sleep(args.initial_wait)
        state = await page_eval(cdp, sid, "(() => ({url: location.href, title: document.title, bodyChars: document.body ? document.body.innerText.length : 0}))()")
        if not state or "聊天" not in state.get("title", ""):
            raise RuntimeError(f"unexpected IM page state: {state}")

        if args.skip_conversation_list:
            conversation_probe = None
        else:
            conversation_probe = await probe_conversation_list(cdp, sid, args.max_conversation_scrolls, args.wait)

        indices = [int(x) for x in args.message_conversation_indices.split(",") if x.strip()]
        message_probes = await probe_message_histories(cdp, sid, indices, args.max_message_scrolls, args.wait, args.message_wheel_delta_y)

        await cdp.cmd("Target.closeTarget", {"targetId": target_id})

    report = {
        "schema": "goofish-im-fullness-probe/v1",
        "account": args.account,
        "port": port,
        "collectedAt": datetime.now().isoformat(),
        "pageState": state,
        "conversationListProbe": conversation_probe,
        "messageHistoryProbes": message_probes,
        "notes": [
            "No chat text is stored in this report, only hashes/counts/scroll positions.",
            "Opening a conversation in the web UI may mark it read.",
        ],
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    total_messages = sum(p["uniqueMessageCount"] for p in message_probes)
    reached_tops = sum(1 for p in message_probes if p["reachedTop"])
    return {
        "report": str(path),
        "uniqueConversationCount": conversation_probe["uniqueConversationCount"] if conversation_probe else None,
        "reachedConversationBottom": conversation_probe["reachedBottom"] if conversation_probe else None,
        "messageProbeCount": len(message_probes),
        "reachedMessageTopCount": reached_tops,
        "totalUniqueMessagesAcrossProbes": total_messages,
        "messageProbes": [
            {
                "visibleIndex": p["chosenConversation"]["visibleIndex"],
                "conversationKey": p["chosenConversation"]["conversationKey"],
                "uniqueMessageCount": p["uniqueMessageCount"],
                "reachedTop": p["reachedTop"],
                "roleCounts": p["roleCounts"],
                "kindCounts": p["kindCounts"],
            }
            for p in message_probes
        ],
    }


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Probe Goofish IM list/history traversal boundaries.")
    ap.add_argument("--account", default="account-01")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--initial-wait", type=float, default=14)
    ap.add_argument("--wait", type=float, default=1.5)
    ap.add_argument("--max-conversation-scrolls", type=int, default=80)
    ap.add_argument("--skip-conversation-list", action="store_true")
    ap.add_argument("--message-conversation-indices", default="0", help="Comma-separated visible conversation indices to probe.")
    ap.add_argument("--max-message-scrolls", type=int, default=80)
    ap.add_argument("--message-wheel-delta-y", type=float, default=-900, help="Mouse wheel deltaY sent at the center of #message-list-scrollable. Negative is visual upward scrolling.")
    return ap.parse_args()


def main() -> int:
    try:
        result = asyncio.run(run(parse_args()))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
