#!/usr/bin/env python3
"""轻量登录态探针：给每个账号端口开临时标签页导航到 /personal，
读 document.title + 查登录墙标记，确认后关掉标签页（不动现有页面）。
用法: /usr/bin/python3 scripts/goofish-login-check.py
"""
import asyncio, json, urllib.request, sys
import websockets  # /usr/bin/python3 已装 13.1

ACCOUNTS = [("account-01", 9224), ("account-04", 9233),
            ("account-05", 9225)]
PERSONAL = "https://www.goofish.com/personal"


def http_json(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=4) as r:
        return json.loads(r.read())


async def check(account, port):
    try:
        ver = http_json(port, "/json/version")
    except Exception as e:
        return (account, port, "❌ CDP 不在线", "")
    bws = ver["webSocketDebuggerUrl"]
    _id = [0]
    def nx(): _id[0] += 1; return _id[0]
    try:
        async with websockets.connect(bws, max_size=None) as ws:
            async def cmd(method, params=None, sid=None):
                mid = nx()
                msg = {"id": mid, "method": method, "params": params or {}}
                if sid: msg["sessionId"] = sid
                await ws.send(json.dumps(msg))
                while True:
                    r = json.loads(await asyncio.wait_for(ws.recv(), timeout=20))
                    if r.get("id") == mid:
                        return r
            # 新建临时标签页
            t = await cmd("Target.createTarget", {"url": PERSONAL})
            tgt = t["result"]["targetId"]
            a = await cmd("Target.attachToTarget", {"targetId": tgt, "flatten": True})
            sid = a["result"]["sessionId"]
            await cmd("Page.enable", {}, sid)
            await asyncio.sleep(6)  # 等闲鱼页面/登录墙渲染
            ev = await cmd("Runtime.evaluate", {
                "expression": "JSON.stringify({t:document.title,b:(document.body?document.body.innerText:'').slice(0,3000)})",
                "returnByValue": True}, sid)
            val = json.loads(ev["result"]["result"]["value"])
            title, body = val["t"], val["b"]
            await cmd("Target.closeTarget", {"targetId": tgt})
            logged_in = not ("请登录" in body or "扫码登录" in body or "亲，请登录" in title)
            status = "✅ 已登录" if logged_in else "⚠ 登录态已掉（出现登录墙）"
            return (account, port, status, title)
    except Exception as e:
        return (account, port, f"⚠ 探测异常: {type(e).__name__}: {e}", "")


async def main():
    only = sys.argv[1:] or None
    targets = [(a, p) for a, p in ACCOUNTS if not only or a in only]
    res = await asyncio.gather(*(check(a, p) for a, p in targets))
    print(f"{'账号':<12}{'端口':<7}{'状态':<24}标题")
    for a, p, s, t in res:
        print(f"{a:<12}{p:<7}{s:<24}{t}")


if __name__ == "__main__":
    asyncio.run(main())
