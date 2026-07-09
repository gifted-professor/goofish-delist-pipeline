#!/usr/bin/env python3
"""Prepare a Goofish publish draft from a local SZWego item package.

This is intentionally a dry-run helper: it fills/uploads into the publish form
and stops before the final publish button. It uses the user's already logged-in
Chrome window plus macOS UI scripting for the native file picker.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from websockets.sync.client import connect as websocket_connect


PUBLISH_URL = "https://www.goofish.com/publish"
DEFAULT_CPA_BASE_URL = "http://100.84.194.46:8317"
DEFAULT_CPA_MODEL = "claude-sonnet-4-6"
DEFAULT_CPA_API_KEY = "cliproxyapi-local"
DEFAULT_SKU_STOCK = "20"
MAX_LISTING_TITLE_CHARS = 15
CHROME_JS_DISABLED_HINT = (
    "Chrome has disabled JavaScript from Apple Events. In Chrome, enable: "
    "View > Developer > Allow JavaScript from Apple Events, then run --doctor again."
)
MEASUREMENT_LABELS = {
    "胸围",
    "肩宽",
    "衣长",
    "袖长",
    "腰围",
    "臀围",
    "裤长",
    "腿围",
    "脚口",
    "建议",
    "体重",
    "身高",
}
SIZE_ORDER = ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "2XL", "3XL", "4XL", "5XL", "6XL", "7XL", "8XL", "9XL"]
DISPLAY_SIZE_ORDER = ["XXS", "XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL", "5XL", "6XL", "7XL", "8XL", "9XL"]
BRAND_RULES = [
    {
        "patterns": [r"chrome\s*hearts", r"克罗心", r"\bCH\b"],
        "query": "Chrome Hearts",
        "preferred": ["CHROME HEARTS", "Chrome Hearts", "克罗心"],
    },
    {
        "patterns": [r"adidas", r"阿迪达斯", r"三叶草"],
        "query": "Adidas",
        "preferred": ["ADIDAS", "Adidas", "阿迪达斯"],
    },
    {
        "patterns": [r"descente", r"迪桑特", r"D家"],
        "query": "Descente",
        "preferred": ["DESCENTE", "Descente", "迪桑特"],
    },
    {
        "patterns": [r"\bfila\b", r"斐乐", r"F家"],
        "query": "FILA",
        "preferred": ["FILA", "Fila", "斐乐"],
    },
    {
        "patterns": [r"kolon", r"可隆", r"K家"],
        "query": "KOLON SPORT",
        "preferred": ["KOLON SPORT", "KOLON", "可隆"],
    },
    {
        "patterns": [r"arc'?teryx", r"arcteryx", r"始祖鸟"],
        "query": "Arc'teryx",
        "preferred": ["ARC'TERYX", "Arc'teryx", "始祖鸟"],
    },
    {
        "patterns": [r"\bnike\b", r"耐克"],
        "query": "Nike",
        "preferred": ["NIKE", "Nike", "耐克"],
    },
    {
        "patterns": [r"lululemon", r"露露乐蒙"],
        "query": "lululemon",
        "preferred": ["LULULEMON", "lululemon", "露露乐蒙"],
    },
]


class ChromeJavaScriptDisabled(RuntimeError):
    pass


CDP_PORT: int | None = None
CDP_TAB_ID: str | None = None


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def run(cmd: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def osascript(script: str, *, check: bool = True) -> str:
    proc = run(["osascript"], input_text=script, check=check)
    return proc.stdout.strip()


def set_clipboard(text: str) -> None:
    run(["pbcopy"], input_text=text)


def paste() -> None:
    osascript(
        '''
        tell application "System Events"
          keystroke "v" using {command down}
        end tell
        '''
    )


def cdp_request(path: str, *, method: str = "GET") -> object:
    assert CDP_PORT is not None
    req = urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}{path}", method=method)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read())


def cdp_tabs() -> list[dict[str, object]]:
    data = cdp_request("/json/list")
    return data if isinstance(data, list) else []


def cdp_tab_by_id(tab_id: str | None) -> dict[str, object] | None:
    if not tab_id:
        return None
    for tab in cdp_tabs():
        if tab.get("id") == tab_id and tab.get("type") == "page":
            return tab
    return None


def cdp_current_tab() -> dict[str, object]:
    tab = cdp_tab_by_id(CDP_TAB_ID)
    if tab:
        return tab
    publish_tab = next((t for t in cdp_tabs() if t.get("type") == "page" and "goofish.com/publish" in str(t.get("url") or "")), None)
    if publish_tab:
        return publish_tab
    page_tab = next((t for t in cdp_tabs() if t.get("type") == "page"), None)
    if not page_tab:
        raise RuntimeError(f"no page tab on CDP port {CDP_PORT}")
    return page_tab


def cdp_open_url(url: str, *, new_tab: bool) -> None:
    global CDP_TAB_ID
    if new_tab or not cdp_tab_by_id(CDP_TAB_ID):
        encoded = urllib.parse.quote(url, safe=":/?=&%#")
        tab = cdp_request(f"/json/new?{encoded}", method="PUT")
        if isinstance(tab, dict):
            CDP_TAB_ID = str(tab.get("id") or "")
        return
    tab = cdp_current_tab()
    ws_url = str(tab["webSocketDebuggerUrl"])
    with websocket_connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        ws.send(json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                return


def cdp_eval(js: str, *, check: bool = True) -> str:
    tab = cdp_current_tab()
    ws_url = str(tab["webSocketDebuggerUrl"])
    with websocket_connect(ws_url, max_size=50 * 1024 * 1024) as ws:
        ws.send(json.dumps({
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": js,
                "returnByValue": True,
                "awaitPromise": True,
            },
        }))
        while True:
            msg = json.loads(ws.recv())
            if msg.get("id") != 1:
                continue
            if check and msg.get("error"):
                raise RuntimeError(json.dumps(msg["error"], ensure_ascii=False))
            result = msg.get("result", {})
            if check and result.get("exceptionDetails"):
                raise RuntimeError(json.dumps(result["exceptionDetails"], ensure_ascii=False)[:1000])
            value = result.get("result", {}).get("value")
            if value is None:
                value = result.get("result", {}).get("description", "")
            return "" if value is None else str(value)


def chrome_js(js: str, *, check: bool = True) -> str:
    if CDP_PORT is not None:
        return cdp_eval(js, check=check)
    # Avoid embedding JS directly in AppleScript strings: non-ASCII text,
    # regular expressions, and backslashes are easy to misquote there.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as temp:
        temp.write(js)
        temp_path = Path(temp.name)
    script = f'''
    set jsSource to read POSIX file {json.dumps(str(temp_path))} as «class utf8»
    tell application "Google Chrome"
      activate
      execute active tab of front window javascript jsSource
    end tell
    '''
    proc = run(["osascript"], input_text=script, check=False)
    temp_path.unlink(missing_ok=True)
    output = (proc.stdout or "").strip()
    error = (proc.stderr or "").strip()
    if proc.returncode != 0:
        if "JavaScript" in error and ("Apple" in error or "AppleScript" in error):
            if check:
                raise ChromeJavaScriptDisabled(CHROME_JS_DISABLED_HINT)
            return ""
        if check:
            raise subprocess.CalledProcessError(proc.returncode, proc.args, output=proc.stdout, stderr=proc.stderr)
    return output


def open_publish_page(*, new_tab: bool = False) -> None:
    if CDP_PORT is not None:
        cdp_open_url(PUBLISH_URL, new_tab=new_tab)
        return
    if new_tab:
        osascript(
            f'''
            tell application "Google Chrome"
              activate
              if (count of windows) = 0 then make new window
              set newTab to make new tab at end of tabs of front window with properties {{URL:"about:blank"}}
              set active tab index of front window to (count of tabs of front window)
              delay 0.8
              set URL of newTab to {json.dumps(PUBLISH_URL)}
            end tell
            '''
        )
        return
    osascript(
        f'''
        tell application "Google Chrome"
          activate
          if (count of windows) = 0 then make new window
          set URL of active tab of front window to "about:blank"
          delay 0.8
          set URL of active tab of front window to {json.dumps(PUBLISH_URL)}
        end tell
        '''
    )


def press_escape() -> None:
    if CDP_PORT is not None:
        try:
            tab = cdp_current_tab()
            with websocket_connect(str(tab["webSocketDebuggerUrl"]), max_size=50 * 1024 * 1024) as ws:
                for idx, event_type in enumerate(["keyDown", "keyUp"], start=1):
                    ws.send(json.dumps({
                        "id": idx,
                        "method": "Input.dispatchKeyEvent",
                        "params": {
                            "type": event_type,
                            "key": "Escape",
                            "code": "Escape",
                            "windowsVirtualKeyCode": 27,
                        },
                    }))
                    while True:
                        msg = json.loads(ws.recv())
                        if msg.get("id") == idx:
                            break
        except Exception:
            pass
        return
    osascript(
        '''
        tell application "System Events"
          key code 53
        end tell
        ''',
        check=False,
    )


def wait_for_page_ready(timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    last = ""
    while time.monotonic() < deadline:
        last = chrome_js("document.body && document.body.innerText.includes('发闲置') ? 'ready' : document.title")
        if "ready" in last:
            return
        time.sleep(0.5)
    raise RuntimeError(f"Goofish publish page did not become ready: {last}")


def strip_emoji(text: str) -> str:
    kept: list[str] = []
    for ch in text:
        category = unicodedata.category(ch)
        if category == "So" or ord(ch) > 0xFFFF:
            continue
        kept.append(ch)
    return "".join(kept).strip()


def normalize_price(raw: str) -> str:
    match = re.search(r"\d+(?:\.\d+)?", raw)
    if not match:
        raise ValueError(f"could not parse price from {raw!r}")
    return f"{float(match.group(0)):.2f}"


def listing_price_from_supplier_price(raw: str) -> str:
    supplier_price = float(normalize_price(raw))
    target = supplier_price / 0.7
    rounded_to_ending_9 = int(((target + 1) / 10) + 0.5) * 10 - 1
    return f"{max(rounded_to_ending_9, 9):.2f}"


def same_price(left: str, right: str) -> bool:
    try:
        return normalize_price(left) == normalize_price(right)
    except ValueError:
        return False


def split_spec_values(raw: str) -> list[str]:
    values: list[str] = []
    for token in re.split(r"[\s,，、/]+", raw.strip()):
        token = token.strip("：:;；")
        if token and token not in values:
            values.append(token)
    return values


def normalize_size_token(value: str) -> str:
    text = value.strip().upper()
    replacements = {
        "2XXL": "XXL",
        "3XXL": "XXXL",
    }
    return replacements.get(text, text)


def expand_size_values(values: list[str]) -> list[str]:
    expanded: list[str] = []
    for value in values:
        token = value.strip()
        range_match = re.match(r"^(XXS|XS|S|M|L|XL|XXL|XXXL|[2-9]XL)\s*[-~至到]\s*(XXS|XS|S|M|L|XL|XXL|XXXL|[2-9]XL)$", token, re.IGNORECASE)
        if range_match:
            start = normalize_size_token(range_match.group(1))
            end = normalize_size_token(range_match.group(2))
            if start in SIZE_ORDER and end in SIZE_ORDER:
                left = SIZE_ORDER.index(start)
                right = SIZE_ORDER.index(end)
                if left <= right:
                    for size in SIZE_ORDER[left : right + 1]:
                        if size not in expanded:
                            expanded.append(size)
                    continue
        normalized = normalize_size_token(token)
        if normalized and normalized not in expanded:
            expanded.append(normalized)
    return expanded


def parse_colors(description: str) -> list[str]:
    for line in description.splitlines():
        match = re.search(r"颜色\s*[:：]\s*(.+)", line)
        if match:
            return split_spec_values(match.group(1))
    return []


def parse_sizes(description: str) -> list[str]:
    size_pattern = re.compile(r"^(?:均码|XXS|XS|S|M|L|XL|XXL|XXXL|[2-9]XL)$", re.IGNORECASE)
    for line in description.splitlines():
        label_match = re.search(r"尺码\s*[:：]\s*(.+)", line)
        if label_match:
            values = expand_size_values(split_spec_values(label_match.group(1)))
            if values and all(size_pattern.match(value) for value in values):
                return values
        values = expand_size_values(split_spec_values(line))
        if len(values) >= 2 and all(size_pattern.match(value) for value in values):
            return values
    return []


def parse_specs(description: str) -> dict[str, list[str]]:
    specs: dict[str, list[str]] = {}
    colors = parse_colors(description)
    sizes = parse_sizes(description)
    if colors:
        specs["颜色"] = colors
    if sizes:
        specs["尺码"] = sizes
    return specs


def is_size_list_line(line: str) -> bool:
    size_pattern = re.compile(r"^(?:均码|XXS|XS|S|M|L|XL|XXL|XXXL|[2-9]XL)$", re.IGNORECASE)
    label_match = re.search(r"尺码\s*[:：]\s*(.+)", line)
    values = expand_size_values(split_spec_values(label_match.group(1) if label_match else line))
    return len(values) >= 2 and all(size_pattern.match(value) for value in values)


def is_measurement_header_line(line: str) -> bool:
    values = split_spec_values(line)
    return len(values) >= 2 and all(value in MEASUREMENT_LABELS for value in values)


def is_measurement_line(line: str) -> bool:
    values = split_spec_values(line)
    if len(values) < 2:
        return False
    label = values[0].strip()
    return label in MEASUREMENT_LABELS and any(re.search(r"\d", value) for value in values[1:])


def is_size_measurement_line(line: str) -> bool:
    values = split_spec_values(line)
    if len(values) < 2:
        return False
    first = normalize_size_token(values[0])
    return first in SIZE_ORDER and any(re.search(r"\d", value) for value in values[1:])


def strip_leading_price_from_title(line: str, price: str) -> tuple[str, str | None]:
    match = re.match(r"^\s*(?:[¥￥]\s*)?(\d+(?:\.\d+)?)(?:\s*发)?\s*[，,、]?\s*(.*)$", line)
    if not match or not same_price(match.group(1), price):
        return line, None
    rest = match.group(2).strip()
    removed = f"leading price: {match.group(1)}"
    if not rest:
        return "", removed
    return rest, removed


def is_price_intro_line(line: str, price: str) -> bool:
    match = re.search(r"\d+(?:\.\d+)?", line)
    if not match or not same_price(match.group(0), price):
        return False
    without_price = (line[: match.start()] + line[match.end() :]).strip()
    without_price = re.sub(r"[\s:：,，.。!！~-]+", "", without_price)
    return without_price in {"", "发", "上新", "新款", "现货", "到货", "补货", "特价", "推荐"}


def clean_listing_description(raw_description: str, price: str) -> tuple[str, list[str]]:
    """Remove supplier-only structure from the buyer-facing listing copy."""
    cleaned = strip_emoji(raw_description)
    kept: list[str] = []
    removed: list[str] = []
    saw_content = False

    for raw_line in cleaned.splitlines():
        line = raw_line.strip()
        if not line:
            if kept and kept[-1] != "":
                kept.append("")
            continue

        if is_price_intro_line(line, price):
            removed.append(line)
            continue

        if not saw_content:
            line, removed_price_line = strip_leading_price_from_title(line, price)
            saw_content = True
            if removed_price_line:
                removed.append(removed_price_line)
            if not line:
                continue

        if re.match(r"^颜色\s*[:：]", line):
            removed.append(line)
            continue
        if is_size_list_line(line):
            removed.append(line)
            continue
        if is_measurement_header_line(line) or is_measurement_line(line) or is_size_measurement_line(line):
            removed.append(line)
            continue

        kept.append(line)

    while kept and kept[-1] == "":
        kept.pop()
    return "\n".join(kept).strip(), removed


def rule_extract_copy(raw_description: str, price: str) -> dict[str, object]:
    listing_description, removed_lines = clean_listing_description(raw_description, price)
    return {
        "source": "rule",
        "listing_description": listing_description,
        "price": price,
        "sku_specs": parse_specs(raw_description),
        "removed_description_lines": removed_lines,
        "notes": [],
    }


def normalize_listing_brand_aliases(description: str) -> str:
    """Use public-facing brand hints while keeping brand selection separate."""
    replacements = [
        (r"(?<![A-Za-z0-9])D家", "D家"),
        (r"descente|迪桑特", "D家"),
        (r"(?<![A-Za-z0-9])F家", "F家"),
        (r"\bfila\b|斐乐", "F家"),
        (r"(?<![A-Za-z0-9])K家", "K家"),
        (r"kolon\s*sport|kolon|可隆", "K家"),
    ]
    text = description
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def compact_title_length(description: str) -> int:
    return len(re.sub(r"\s+", "", description))


def trim_listing_title(description: str) -> str:
    text = normalize_listing_brand_aliases(description).strip()
    text = re.sub(r"^\s*(?:[¥￥]\s*)?\d+(?:\.\d+)?\s*发\s*[，,、]?\s*", "", text)
    text = re.sub(r"^\s*发\s*[，,、]?\s*", "", text)
    text = re.split(r"[\n，,。；;！!]", text, maxsplit=1)[0].strip()
    text = re.sub(r"\s+", "", text).strip("，,。；;！!")
    if compact_title_length(text) <= MAX_LISTING_TITLE_CHARS:
        return text

    replacements = [
        (r"男士|女士|男女同款|男女|男款|女款|情侣款", ""),
        (r"26款|新款", ""),
        (r"TRAINING综训系列|TRAINING系列|综训系列|RUNNING系列", ""),
        (r"短袖T恤", "短袖"),
    ]
    candidate = text
    for pattern, replacement in replacements:
        candidate = re.sub(pattern, replacement, candidate, flags=re.IGNORECASE)
    if compact_title_length(candidate) <= MAX_LISTING_TITLE_CHARS:
        return candidate

    lower = text.lower()
    if "D家" in text and "防晒" in text and "polo" in lower:
        return "D家凉感防晒POLO"
    if "萨洛蒙" in text and "三座山" in text and "短袖" in text:
        return "萨洛蒙三座山印花短袖"
    if "阿迪达斯" in text and ("外套" in text or "夹克" in text):
        return "阿迪达斯复古立领外套"

    return text[:MAX_LISTING_TITLE_CHARS]


def display_size_range(sizes: list[str]) -> str:
    normalized = [normalize_size_token(str(size)) for size in sizes if str(size).strip()]
    if not normalized:
        return ""
    unique: list[str] = []
    for size in normalized:
        if size not in unique:
            unique.append(size)
    if len(unique) == 1:
        return unique[0]
    if all(size in DISPLAY_SIZE_ORDER for size in unique):
        indexes = [DISPLAY_SIZE_ORDER.index(size) for size in unique]
        ordered = [size for _, size in sorted(zip(indexes, unique))]
        if indexes == list(range(min(indexes), max(indexes) + 1)):
            return f"{ordered[0]}-{ordered[-1]}"
    return "/".join(unique)


def build_goofish_description(title: str, specs: dict[str, object]) -> str:
    lines = [f"【奥莱折扣】2折+ {trim_listing_title(title)}"]
    raw_sizes = specs.get("尺码") if isinstance(specs, dict) else None
    sizes = [str(value) for value in raw_sizes] if isinstance(raw_sizes, list) else []
    size_text = display_size_range(sizes)
    if size_text:
        lines.append(f"尺码 {size_text}")
    lines.extend(
        [
            "部分 断码 数量有限",
            "主页均为实拍 需要的点击我想要咨询",
        ]
    )
    return "\n".join(line for line in lines if line.strip())


def json_from_model_text(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", stripped, re.DOTALL)
        if not match:
            raise
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("model response JSON must be an object")
    return parsed


def normalize_model_specs(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    specs: dict[str, list[str]] = {}
    for raw_key, raw_values in value.items():
        key = str(raw_key).strip()
        if not key:
            continue
        values: list[str] = []
        if isinstance(raw_values, list):
            candidates = raw_values
        else:
            candidates = split_spec_values(str(raw_values))
        for candidate in candidates:
            text = str(candidate).strip()
            if text and text not in values:
                values.append(text)
        if values:
            specs[key] = values
    return specs


def validate_copy_extraction(result: dict[str, object], fallback: dict[str, object], price: str) -> dict[str, object]:
    listing_description = strip_emoji(str(result.get("listing_description") or "")).strip()
    if not listing_description:
        listing_description = str(fallback["listing_description"])
    if len(listing_description) > 1500:
        listing_description = listing_description[:1500].rstrip()
    listing_description = trim_listing_title(listing_description)
    notes = result.get("notes")
    if isinstance(notes, list):
        normalized_notes = [str(note).strip() for note in notes if str(note).strip()]
    elif notes:
        normalized_notes = [str(notes).strip()]
    else:
        normalized_notes = []

    fallback_description = str(fallback.get("listing_description") or "").strip()
    fallback_first_line = next((line.strip() for line in fallback_description.splitlines() if line.strip()), "")
    title_candidate_lines = [fallback_first_line]
    removed_candidates = fallback.get("removed_description_lines", [])
    if isinstance(removed_candidates, list):
        title_candidate_lines.extend(str(line) for line in removed_candidates)
    fallback_titles = [
        trim_listing_title(line)
        for line in title_candidate_lines
        if str(line).strip()
    ]
    fallback_titles = [
        title
        for title in fallback_titles
        if title and compact_title_length(title) <= MAX_LISTING_TITLE_CHARS
        and re.search(r"[\u4e00-\u9fff]", title)
        and not title.lower().startswith("leading")
    ]
    fallback_title = max(
        fallback_titles,
        key=lambda title: (
            "短袖" in title,
            "POLO" in title.upper(),
            "衫" in title,
            compact_title_length(title),
        ),
        default="",
    )
    title_tokens = [
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}|[\u4e00-\u9fff]{2,}", fallback_first_line)
        if token not in {"潮牌", "情侣款", "短袖", "恤"}
    ]
    if fallback_first_line and fallback_first_line not in listing_description:
        has_title_signal = any(token.lower() in listing_description.lower() for token in title_tokens)
        if not has_title_signal:
            listing_description = fallback_title
            normalized_notes.append("model output omitted title/brand line; restored fallback title")
    if (
        fallback_title
        and compact_title_length(fallback_title) <= MAX_LISTING_TITLE_CHARS
        and (
            ("短袖" in fallback_title and "短袖" not in listing_description)
            or ("POLO" in fallback_title.upper() and "POLO" not in listing_description.upper())
            or ("POLO衫" in fallback_title.upper() and "衫" not in listing_description)
        )
        and any(token in fallback_title.upper() for token in ("POLO", "T恤", "短袖"))
    ):
        listing_description = fallback_title
        normalized_notes.append("restored richer short-sleeve product title from source")

    raw_price = str(result.get("price") or price).strip()
    try:
        extracted_price = normalize_price(raw_price)
    except ValueError:
        extracted_price = price

    model_specs = normalize_model_specs(result.get("sku_specs"))
    fallback_specs = fallback.get("sku_specs")
    specs = model_specs if model_specs else fallback_specs
    if not isinstance(specs, dict):
        specs = {}

    removed = result.get("removed_description_lines")
    if isinstance(removed, list):
        removed_lines = [str(line).strip() for line in removed if str(line).strip()]
    else:
        removed_lines = list(fallback.get("removed_description_lines", []))  # type: ignore[arg-type]

    return {
        "source": str(result.get("source") or "cpa"),
        "listing_description": listing_description,
        "price": extracted_price,
        "sku_specs": specs,
        "removed_description_lines": removed_lines,
        "notes": normalized_notes,
    }


def cpa_extract_copy(
    raw_description: str,
    price: str,
    *,
    base_url: str,
    model: str,
    api_key: str,
    timeout: float,
    fallback: dict[str, object],
) -> dict[str, object]:
    system_prompt = (
        "你是闲鱼上架文案结构化助手。只输出 JSON，不要输出 markdown。"
        "目标是把供货商原始文案拆成买家可见短标题、价格、SKU 规格和被丢弃的供货字段。"
    )
    user_prompt = f"""
请分析下面的供货商原始文案，返回严格 JSON：
{{
  "listing_description": "适合直接粘贴到闲鱼宝贝描述的商品短标题，15个字以内，不要包含价格、颜色行、尺码列表、胸围肩宽衣长等尺码表",
  "price": "数字价格，保留两位小数",
  "sku_specs": {{"颜色": ["..."], "尺码": ["..."]}},
  "removed_description_lines": ["从描述中移除但用于价格/SKU/尺码表的原文行"],
  "notes": ["可选，简短说明"]
}}

规则：
- 若开头出现类似“85💰标题”，且 85 与给定价格一致，则 85 是价格，不应进入 listing_description。
- 颜色、尺码、胸围、肩宽、衣长、袖长、腰围、裤长等结构化信息不要进入 listing_description。
- listing_description 必须是商品短标题，不是长段落；控制在 15 个字以内，例如“萨洛蒙三座山印花短袖”。
- 公开买家标题里保留可识别但不直写全称的品牌提示：迪桑特/Descente/D家写作“D家”，斐乐/FILA/F家写作“F家”，可隆/KOLON/K家写作“K家”。
- 品牌字段会另外结构化选择真实品牌，listing_description 只负责公开文案短标题。
- 不要虚构商品卖点，不要改写品牌/型号事实。
- 如果不确定某个字段，优先保守输出品牌 + 品类 + 最核心卖点。

给定价格：{price}
原始文案：
{raw_description}
""".strip()
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": 1200,
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        method="POST",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"CPA extractor failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"CPA extractor connection failed: {exc.reason}") from exc

    choices = data.get("choices") if isinstance(data, dict) else None
    if not choices:
        raise RuntimeError("CPA extractor returned no choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("CPA extractor returned empty content")
    parsed = json_from_model_text(content)
    parsed["source"] = f"cpa:{model}"
    return validate_copy_extraction(parsed, fallback, price)


def extract_copy(
    raw_description: str,
    price: str,
    *,
    extractor: str,
    cpa_base_url: str,
    cpa_model: str,
    cpa_api_key: str,
    cpa_timeout: float,
) -> dict[str, object]:
    fallback = rule_extract_copy(raw_description, price)
    if extractor == "rule":
        return fallback
    try:
        return cpa_extract_copy(
            raw_description,
            price,
            base_url=cpa_base_url,
            model=cpa_model,
            api_key=cpa_api_key,
            timeout=cpa_timeout,
            fallback=fallback,
        )
    except Exception as exc:
        if extractor == "cpa":
            raise
        result = dict(fallback)
        result["source"] = "rule-fallback"
        result["notes"] = [f"CPA extractor failed: {exc}"]
        return result


def spec_combination_count(specs: dict[str, list[str]]) -> int:
    count = 1
    used = False
    for values in specs.values():
        if values:
            used = True
            count *= len(values)
    return count if used else 0


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def infer_category_preferences(description: str) -> list[str]:
    text = description.lower()
    prefs: list[str] = []

    def category_flags(scope: str) -> dict[str, bool]:
        return {
            "tshirt": bool(re.search(r"T恤|t恤|tee|短袖", scope, re.IGNORECASE)),
            "outer": bool(re.search(r"外套|夹克|冲锋衣|防晒衣|开衫|棒球服|风衣", scope)),
            "shorts": bool(re.search(r"短裤|五分裤|训练裤", scope)),
            "pants": bool(re.search(r"长裤|休闲裤|运动裤|梭织裤|直筒裤|速干裤", scope)),
            "polo": bool(re.search(r"polo|POLO|polo衫", scope)),
        }

    primary_lines = [line.strip() for line in description.splitlines() if line.strip()][:4]
    primary = "\n".join(primary_lines)
    primary_flags = category_flags(primary)
    full_flags = category_flags(description)

    has_tshirt = primary_flags["tshirt"] or (not prefs and full_flags["tshirt"])
    has_outer = primary_flags["outer"] or (not prefs and full_flags["outer"])
    has_shorts = primary_flags["shorts"] or (not prefs and full_flags["shorts"])
    has_pants = primary_flags["pants"] or (not prefs and full_flags["pants"] and not primary_flags["tshirt"] and not primary_flags["polo"])
    has_polo = primary_flags["polo"] or (not prefs and full_flags["polo"])

    if has_shorts:
        prefs.extend(["运动短裤", "短裤", "速干裤"])
    elif has_pants:
        prefs.extend(["运动长裤", "休闲裤", "速干裤"])
    if has_polo:
        prefs.extend(["运动POLO衫", "运动polo衫", "运动T恤"])
    if has_tshirt:
        prefs.extend(["运动T恤", "速干衣", "文化衫"])
    elif has_outer:
        prefs.extend(["运动外套", "防晒衣", "速干衣"])
    if re.search(r"卫衣|帽衫", description):
        prefs.extend(["运动卫衣", "运动外套"])
    if re.search(r"衬衫", description):
        prefs.extend(["运动衬衫", "速干衣", "运动外套"])
    if not prefs and "chrome hearts" in text:
        prefs.extend(["运动T恤", "运动外套", "速干衣", "文化衫"])
    prefs.extend(["运动T恤", "运动外套", "速干衣", "文化衫"])
    return unique(prefs)


def infer_brand_preference(description: str) -> dict[str, object]:
    for rule in BRAND_RULES:
        patterns = rule["patterns"]
        assert isinstance(patterns, list)
        if any(re.search(str(pattern), description, re.IGNORECASE) for pattern in patterns):
            return {
                "query": rule["query"],
                "preferred": rule["preferred"],
            }
    return {}


def resolve_package_file(package_dir: Path, raw_path: str | None, fallback_name: str) -> Path:
    if raw_path:
        path = Path(raw_path)
        return path if path.is_absolute() else package_dir / path
    return package_dir / fallback_name


def image_files(image_dir: Path) -> list[Path]:
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted(path for path in image_dir.iterdir() if path.is_file() and path.suffix.lower() in allowed)


def image_dimensions(path: Path) -> tuple[int, int] | None:
    proc = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)], check=False)
    if proc.returncode != 0:
        return None
    width_match = re.search(r"pixelWidth:\s*(\d+)", proc.stdout)
    height_match = re.search(r"pixelHeight:\s*(\d+)", proc.stdout)
    if not width_match or not height_match:
        return None
    return int(width_match.group(1)), int(height_match.group(1))


def image_aspect(path: Path) -> float | None:
    dimensions = image_dimensions(path)
    if not dimensions:
        return None
    width, height = dimensions
    return width / height if height else None


def image_sequence_number(path: Path) -> int:
    match = re.search(r"\d+", path.stem)
    return int(match.group(0)) if match else 9999


def classify_image_for_listing(path: Path) -> str:
    """Classify SZWego feed images for Goofish ordering."""
    dimensions = image_dimensions(path)
    if not dimensions:
        return "detail"
    width, height = dimensions
    if height <= 0:
        return "detail"
    aspect = width / height
    if aspect >= 1.8:
        return "size_chart"
    if aspect >= 1.05:
        return "overview"
    sequence = image_sequence_number(path)
    if sequence >= 11 and aspect >= 0.58:
        return "overview_vertical"
    return "detail"


def ranked_image_files(image_dir: Path) -> list[Path]:
    """Prefer product overview images as cover and keep size charts last."""
    files = image_files(image_dir)

    def rank(path: Path) -> tuple[int, int, str]:
        image_type = classify_image_for_listing(path)
        buckets = {
            "overview": 0,
            "overview_vertical": 1,
            "detail": 2,
            "size_chart": 3,
        }
        return (buckets.get(image_type, 2), image_sequence_number(path), path.name)

    return sorted(files, key=rank)


def selected_image_files(image_dir: Path, max_images: int) -> list[Path]:
    ranked = ranked_image_files(image_dir)
    size_charts = [path for path in ranked if classify_image_for_listing(path) == "size_chart"]
    non_size_charts = [path for path in ranked if path not in size_charts]
    if size_charts and max_images >= 2:
        return non_size_charts[: max_images - 1] + [size_charts[0]]
    return ranked[:max_images]


def image_order_check(images: list[Path]) -> dict[str, object]:
    if not images:
        return {"passed": False, "reason": "no images"}
    first_aspect = image_aspect(images[0])
    last_aspect = image_aspect(images[-1]) if images else None
    first_type = classify_image_for_listing(images[0])
    last_type = classify_image_for_listing(images[-1])
    return {
        "passed": first_type in {"overview", "overview_vertical"} and (last_type == "size_chart" or last_aspect is None),
        "expected_cover": str(images[0]),
        "expected_cover_name": images[0].name,
        "expected_cover_aspect": first_aspect,
        "expected_cover_type": first_type,
        "last_image": str(images[-1]),
        "last_image_name": images[-1].name,
        "last_image_aspect": last_aspect,
        "last_image_type": last_type,
        "selected_order": [path.name for path in images],
    }


def bmp_grays_from_image(path: Path, size: int = 16) -> list[int]:
    with tempfile.TemporaryDirectory(prefix="goofish-img-hash-") as tmp:
        bmp_path = Path(tmp) / "image.bmp"
        proc = run(["sips", "-z", str(size), str(size), "-s", "format", "bmp", str(path), "--out", str(bmp_path)], check=False)
        if proc.returncode != 0 or not bmp_path.exists():
            raise RuntimeError(f"could not convert image for hashing: {path}: {proc.stderr.strip()}")
        data = bmp_path.read_bytes()

    if data[:2] != b"BM" or len(data) < 54:
        raise RuntimeError(f"unsupported BMP output for hashing: {path}")
    pixel_offset = int.from_bytes(data[10:14], "little")
    dib_size = int.from_bytes(data[14:18], "little")
    if dib_size < 40:
        raise RuntimeError(f"unsupported BMP DIB header for hashing: {path}")
    width = int.from_bytes(data[18:22], "little", signed=True)
    height = int.from_bytes(data[22:26], "little", signed=True)
    bits = int.from_bytes(data[28:30], "little")
    compression = int.from_bytes(data[30:34], "little")
    if width == 0 or height == 0 or bits != 24 or compression != 0:
        raise RuntimeError(f"unsupported BMP format for hashing: {path}")

    abs_width = abs(width)
    abs_height = abs(height)
    stride = ((abs_width * 3 + 3) // 4) * 4
    top_down = height < 0
    grays: list[int] = []
    for y in range(abs_height):
        source_y = y if top_down else abs_height - 1 - y
        row_start = pixel_offset + source_y * stride
        for x in range(abs_width):
            offset = row_start + x * 3
            if offset + 2 >= len(data):
                raise RuntimeError(f"truncated BMP pixel data for hashing: {path}")
            blue, green, red = data[offset], data[offset + 1], data[offset + 2]
            grays.append((red * 299 + green * 587 + blue * 114) // 1000)
    return grays


def image_average_hash(path: Path, size: int = 16) -> str:
    grays = bmp_grays_from_image(path, size)
    if not grays:
        raise RuntimeError(f"empty image hash input: {path}")
    avg = sum(grays) / len(grays)
    bits = "".join("1" if value >= avg else "0" for value in grays)
    return f"{int(bits, 2):0{len(bits) // 4}x}"


def hamming_distance_hex(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("hashes have different lengths")
    return bin(int(left, 16) ^ int(right, 16)).count("1")


def download_image_to_temp(url: str) -> Path:
    suffix = Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
    temp = tempfile.NamedTemporaryFile(prefix="goofish-remote-cover-", suffix=suffix, delete=False)
    temp_path = Path(temp.name)
    temp.close()
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            temp_path.write_bytes(response.read())
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
    return temp_path


def load_item_details(
    package_dir: Path,
    max_images: int,
    *,
    copy_extractor: str = "rule",
    cpa_base_url: str = DEFAULT_CPA_BASE_URL,
    cpa_model: str = DEFAULT_CPA_MODEL,
    cpa_api_key: str = DEFAULT_CPA_API_KEY,
    cpa_timeout: float = 45.0,
) -> dict[str, object]:
    package_json = package_dir / "package.json"
    if not package_json.exists():
        raise FileNotFoundError(f"missing package.json: {package_json}")
    meta = json.loads(package_json.read_text(encoding="utf-8"))

    copy_path = resolve_package_file(package_dir, meta.get("copy_goofish"), "copy.goofish.txt")
    if not copy_path.exists():
        raise FileNotFoundError(f"missing copy text: {copy_path}")
    raw_description = copy_path.read_text(encoding="utf-8").strip()
    raw_price = str(meta.get("price") or "").strip()
    if not raw_price:
        raise ValueError("package.json has no price")
    price = normalize_price(raw_price)
    extraction = extract_copy(
        raw_description,
        price,
        extractor=copy_extractor,
        cpa_base_url=cpa_base_url,
        cpa_model=cpa_model,
        cpa_api_key=cpa_api_key,
        cpa_timeout=cpa_timeout,
    )
    listing_description = str(extraction["listing_description"])
    extracted_price = str(extraction["price"])
    if not listing_description:
        raise ValueError("cleaned listing description is empty")

    image_dir = package_dir / "images"
    if not image_dir.exists():
        raise FileNotFoundError(f"missing image directory: {image_dir}")
    images = selected_image_files(image_dir, max_images)
    if not images:
        raise FileNotFoundError(f"no supported images found in {image_dir}")
    return {
        "raw_description": strip_emoji(raw_description),
        "listing_description": listing_description,
        "removed_description_lines": extraction["removed_description_lines"],
        "price": extracted_price,
        "copy_extraction": extraction,
        "images": images,
    }


def load_item(package_dir: Path, max_images: int) -> tuple[str, str, list[Path]]:
    item = load_item_details(package_dir, max_images)
    return item["listing_description"], item["price"], item["images"]  # type: ignore[return-value]


def package_plan_from_item(package_dir: Path, max_images: int, item: dict[str, object], copy_extractor: str) -> dict[str, object]:
    listing_title = str(item["listing_description"])
    raw_description = str(item["raw_description"])
    supplier_price = str(item["price"])
    price = listing_price_from_supplier_price(supplier_price)
    images = item["images"]
    assert isinstance(images, list)
    extraction = item["copy_extraction"]
    assert isinstance(extraction, dict)
    specs = extraction.get("sku_specs")
    if not isinstance(specs, dict):
        specs = parse_specs(raw_description)
    description = build_goofish_description(listing_title, specs)
    return {
        "package_dir": str(package_dir),
        "dry_run": True,
        "publish_url": PUBLISH_URL,
        "price": price,
        "listing_price": price,
        "supplier_price": supplier_price,
        "price_rule": "supplier_price / 0.7, rounded to nearest price ending in 9",
        "copy_extractor": copy_extractor,
        "copy_extraction_source": extraction.get("source"),
        "copy_extraction_notes": extraction.get("notes", []),
        "sku_specs": specs,
        "sku_count": spec_combination_count(specs),
        "raw_description_chars": len(raw_description),
        "listing_title": listing_title,
        "listing_title_chars": compact_title_length(listing_title),
        "description_chars": len(description),
        "description_preview": description[:80],
        "removed_description_lines": item["removed_description_lines"],
        "category_preferences": infer_category_preferences(raw_description + "\n" + listing_title),
        "brand_preference": infer_brand_preference(raw_description + "\n" + listing_title),
        "max_images": max_images,
        "selected_image_count": len(images),
        "selected_images": [str(path) for path in images],
        "image_order_check": image_order_check(images),
        "will_click_publish": False,
    }


def package_plan(
    package_dir: Path,
    max_images: int,
    *,
    copy_extractor: str = "rule",
    cpa_base_url: str = DEFAULT_CPA_BASE_URL,
    cpa_model: str = DEFAULT_CPA_MODEL,
    cpa_api_key: str = DEFAULT_CPA_API_KEY,
    cpa_timeout: float = 45.0,
) -> dict[str, object]:
    item = load_item_details(
        package_dir,
        max_images,
        copy_extractor=copy_extractor,
        cpa_base_url=cpa_base_url,
        cpa_model=cpa_model,
        cpa_api_key=cpa_api_key,
        cpa_timeout=cpa_timeout,
    )
    return package_plan_from_item(package_dir, max_images, item, copy_extractor)


def fill_text_and_price(description: str, price: str, original_price: str | None = None) -> None:
    js = f"""
    (() => {{
      const description = {json.dumps(description)};
      const price = {json.dumps(price)};
      const originalPrice = {json.dumps(original_price)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const setNativeValue = (el, value) => {{
        const proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(el, value);
        el.dispatchEvent(new Event('input', {{ bubbles: true }}));
        el.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }};
      const textBox = Array.from(document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"]')).find(visible);
      if (!textBox) return 'missing description box';
      if (textBox.tagName === 'TEXTAREA' || textBox.tagName === 'INPUT') {{
        setNativeValue(textBox, description);
      }} else {{
        textBox.focus();
        textBox.textContent = description;
        textBox.dispatchEvent(new InputEvent('input', {{ bubbles: true, inputType: 'insertText', data: description }}));
        textBox.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }}

      const inputs = Array.from(document.querySelectorAll('input')).filter(visible);
      const priceInput = inputs.find((el) => el.value === '0.00')
        || inputs.find((el) => (el.getAttribute('placeholder') || '') === '0.00')
        || inputs.find((el) => /0\\.00/.test((el.value || '') + ' ' + (el.getAttribute('placeholder') || '')));
      if (!priceInput) return 'missing price input';
      setNativeValue(priceInput, price);
      if (originalPrice) {{
        const originalPriceInput = inputs
          .filter((el) => el !== priceInput)
          .find((el) => (el.getAttribute('placeholder') || '') === '0.00' || /0\\.00/.test(el.value || ''));
        if (!originalPriceInput) return 'missing original price input';
        setNativeValue(originalPriceInput, originalPrice);
      }}
      return 'filled';
    }})()
    """
    result = chrome_js(js)
    if "filled" not in result:
        raise RuntimeError(f"could not fill text/price: {result}")


def click_upload_button() -> None:
    js = """
    (() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      };
      const labels = ['添加首图', '添加细节图'];
      const candidates = Array.from(document.querySelectorAll('.ant-upload-select, .ant-upload, button, [role="button"], div'))
        .filter((el) => visible(el) && labels.some((label) => (el.innerText || '').includes(label)))
        .sort((a, b) => {
          const ar = a.getBoundingClientRect();
          const br = b.getBoundingClientRect();
          return (ar.width * ar.height) - (br.width * br.height);
        });
      const target = candidates.find((el) => el.closest('.ant-upload-select') || el.className.includes('ant-upload'))
        || candidates[0];
      if (!target) return JSON.stringify({ error: 'missing upload button' });
      const upload = target.closest('.ant-upload-select') || target.closest('.ant-upload') || target;
      const r = upload.getBoundingClientRect();
      return JSON.stringify({
        x: Math.round(window.screenX + r.left + (r.width / 2)),
        y: Math.round(window.screenY + (window.outerHeight - window.innerHeight) + r.top + (r.height / 2)),
        text: (upload.innerText || '').trim(),
        width: Math.round(r.width),
        height: Math.round(r.height)
      });
    })()
    """
    result = parse_json_result(chrome_js(js))
    if "error" in result:
        raise RuntimeError(f"could not find upload button: {result['error']}")
    try:
        x = int(result["x"])
        y = int(result["y"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"could not parse upload button coordinates: {result}") from exc

    press_escape()
    osascript(
        f'''
        tell application "Google Chrome" to activate
        delay 0.1
        tell application "System Events"
          click at {{{x}, {y}}}
        end tell
        '''
    )


def choose_file_in_open_panel(path: Path) -> None:
    # The "Go to the folder" field accepts a full POSIX path in macOS open panels.
    set_clipboard(str(path))
    osascript(
        '''
        tell application "System Events"
          keystroke "g" using {command down, shift down}
          delay 0.2
          keystroke "v" using {command down}
          delay 0.2
          key code 36
          delay 0.5
          key code 36
        end tell
        '''
    )


def uploaded_image_count() -> int:
    out = chrome_js(
        """
        (() => new Set(Array.from(document.images)
          .map((img) => img.src || '')
          .filter((src) => /-fleamarket\\.jpg_170x10000Q90\\.jpg_\\.webp/.test(src))).size)()
        """,
    )
    try:
        return int(out.strip())
    except ValueError:
        return 0


def wait_for_upload_count(expected: int, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if uploaded_image_count() >= expected:
            return
        time.sleep(1)
    raise RuntimeError(f"timed out waiting for {expected} uploaded images; saw {uploaded_image_count()}")


def upload_image_via_file_input(image: Path) -> None:
    mime = mimetypes.guess_type(str(image))[0] or "image/jpeg"
    b64 = base64.b64encode(image.read_bytes()).decode("ascii")
    js = f"""
    (() => {{
      const b64 = {json.dumps(b64)};
      const name = {json.dumps(image.name)};
      const mime = {json.dumps(mime)};
      const binary = atob(b64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) {{
        bytes[i] = binary.charCodeAt(i);
      }}
      const file = new File([bytes], name, {{ type: mime, lastModified: Date.now() }});
      const input = document.querySelector('input[type="file"]');
      if (!input) return 'missing file input';
      const transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
      input.dispatchEvent(new Event('input', {{ bubbles: true }}));
      input.dispatchEvent(new Event('change', {{ bubbles: true }}));
      return 'dispatched ' + name;
    }})()
    """
    result = chrome_js(js)
    if "missing file input" in result:
        raise RuntimeError(result)


def upload_images_via_file_input(images: list[Path], per_image_timeout: float) -> None:
    existing = uploaded_image_count()
    if existing + len(images) > 9:
        raise RuntimeError(f"page already has {existing} images; cannot add {len(images)} more without exceeding 9")
    for index, image in enumerate(images, start=1):
        print(f"[upload:file-input] {index}/{len(images)} {image.name}", flush=True)
        upload_image_via_file_input(image)
        wait_for_upload_count(existing + index, per_image_timeout)


def upload_images_via_file_picker(images: list[Path], per_image_timeout: float) -> None:
    existing = uploaded_image_count()
    if existing + len(images) > 9:
        raise RuntimeError(f"page already has {existing} images; cannot add {len(images)} more without exceeding 9")
    for index, image in enumerate(images, start=1):
        print(f"[upload:file-picker] {index}/{len(images)} {image.name}", flush=True)
        click_upload_button()
        time.sleep(0.7)
        choose_file_in_open_panel(image)
        wait_for_upload_count(existing + index, per_image_timeout)


def upload_images(images: list[Path], per_image_timeout: float, mode: str) -> None:
    if mode == "file-input":
        upload_images_via_file_input(images, per_image_timeout)
    elif mode == "file-picker":
        upload_images_via_file_picker(images, per_image_timeout)
    else:
        raise ValueError(f"unknown upload mode: {mode}")


def select_condition_new() -> None:
    js_open = """
    (() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      };
      const selected = Array.from(document.querySelectorAll('.ant-form-item'))
        .find((item) => visible(item) && /^成色\\s*全新/.test((item.innerText || '').trim()));
      if (selected) return 'already-selected';

      const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
        .find((item) => visible(item) && (item.innerText || '').trim().startsWith('成色'));
      const placeholder = formItem
        ? Array.from(formItem.querySelectorAll('div, span')).find((el) => (el.innerText || '').trim() === '请选择成色')
        : Array.from(document.querySelectorAll('div, span')).find((el) => (el.innerText || '').trim() === '请选择成色');
      const target = (formItem && (formItem.querySelector('.ant-select-selector') || formItem.querySelector('.ant-select')))
        || (placeholder && (placeholder.closest('.ant-select-selector') || placeholder.closest('.ant-select')))
        || placeholder;
      if (!target) return 'missing selector';
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
      target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
      target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return 'opened';
    })()
    """
    open_result = ""
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        open_result = chrome_js(js_open)
        if "missing" not in open_result:
            break
        time.sleep(0.5)
    if "missing" in open_result:
        raise RuntimeError(f"could not open condition selector: {open_result}")
    time.sleep(0.7)
    js_select = """
    (() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      };
      const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
        .find((item) => visible(item) && /^成色\\s*全新/.test((item.innerText || '').trim()));
      if (formItem) return 'already-selected';
      const option = Array.from(document.querySelectorAll('.ant-select-item-option-content, .ant-select-item, div, span'))
        .filter((el) => visible(el) && (el.innerText || '').trim() === '全新')
        .sort((a, b) => {
          const ar = a.getBoundingClientRect();
          const br = b.getBoundingClientRect();
          return (ar.width * ar.height) - (br.width * br.height);
        })[0];
      if (!option) return 'missing option';
      const target = option.closest('.ant-select-item-option') || option;
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
      target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
      target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
      return 'selected';
    })()
    """
    select_result = chrome_js(js_select)
    if not any(token in select_result for token in ("selected", "already-selected")):
        raise RuntimeError(f"could not select condition: {select_result}")
    time.sleep(0.5)
    verify = chrome_js(
        """
        (() => {
          const text = document.body.innerText || '';
          return text.includes('成色\\n全新') || text.includes('全新\\n尺码') ? 'ok' : text.slice(0, 300);
        })()
        """,
    )
    if "ok" not in verify:
        raise RuntimeError(f"condition selection did not stick: {verify}")


def select_preferred_category(preferences: list[str]) -> dict[str, object]:
    if not preferences:
        return {"enabled": False, "reason": "no inferred category preferences"}
    js_open = f"""
    (() => {{
      const preferences = {json.dumps(preferences, ensure_ascii=False)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const cleanLines = (text) => (text || '').split('\\n').map((line) => line.trim()).filter(Boolean);
      const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
        .find((item) => visible(item) && cleanLines(item.innerText)[0] === '分类');
      if (!formItem) return JSON.stringify({{ error: 'missing category form item' }});
      const current = cleanLines(formItem.innerText).filter((line) => line !== '分类' && line !== '*').slice(-1)[0] || '';
      if (current === preferences[0]) return JSON.stringify({{ selected: current, previous: current, reason: 'already top preference' }});
      const select = formItem.querySelector('.ant-select');
      const target = formItem.querySelector('.ant-select-selector') || select;
      if (!target) return JSON.stringify({{ error: 'missing category select', current }});
      target.scrollIntoView({{ block: 'center' }});
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
      return JSON.stringify({{ opened: true, current, preferences }});
    }})()
    """
    open_result = parse_json_result(chrome_js(js_open))
    if "selected" in open_result:
        return {
            "enabled": True,
            "selected": open_result.get("selected"),
            "previous": open_result.get("previous"),
            "reason": open_result.get("reason"),
            "preferences": preferences,
        }
    if "error" in open_result:
        return {
            "enabled": False,
            "reason": open_result.get("error"),
            "current": open_result.get("current"),
            "preferences": preferences,
        }
    time.sleep(0.7)

    js_select = f"""
    (() => {{
      const preferences = {json.dumps(preferences, ensure_ascii=False)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const optionNodes = Array.from(document.querySelectorAll(
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content, ' +
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item'
      )).filter(visible);
      const options = optionNodes
        .map((el) => (el.innerText || '').trim())
        .filter((text, index, arr) => text && arr.indexOf(text) === index);
      const chosen = preferences.find((pref) => options.includes(pref));
      if (!chosen) return JSON.stringify({{ selected: null, reason: 'no preferred option visible', options, preferences }});
      const option = optionNodes.find((el) => (el.innerText || '').trim() === chosen);
      const target = option.closest('.ant-select-item-option') || option;
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
      return JSON.stringify({{ selected: chosen, options, preferences }});
    }})()
    """
    select_result = parse_json_result(chrome_js(js_select))
    selected = select_result.get("selected")
    if not selected:
        press_escape()
        return {
            "enabled": False,
            "reason": select_result.get("reason", "no preferred option selected"),
            "current": open_result.get("current"),
            "visible_options": select_result.get("options", []),
            "preferences": preferences,
        }
    time.sleep(0.6)
    verify = parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const cleanLines = (text) => (text || '').split('\\n').map((line) => line.trim()).filter(Boolean);
              const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
                .find((item) => visible(item) && cleanLines(item.innerText)[0] === '分类');
              const current = formItem ? cleanLines(formItem.innerText).filter((line) => line !== '分类' && line !== '*').slice(-1)[0] || '' : '';
              return JSON.stringify({ current });
            })()
            """
        )
    )
    return {
        "enabled": True,
        "selected": verify.get("current") or selected,
        "previous": open_result.get("current"),
        "preferences": preferences,
    }


def select_preferred_category_with_retry(preferences: list[str], timeout: float = 12.0) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    last: dict[str, object] = {"enabled": False, "reason": "not attempted", "preferences": preferences}
    while time.monotonic() < deadline:
        last = select_preferred_category(preferences)
        reason = str(last.get("reason", ""))
        if last.get("enabled") or reason not in {"missing category form item", "missing category select"}:
            return last
        time.sleep(1)
    return last


def select_preferred_brand(brand_preference: dict[str, object]) -> dict[str, object]:
    query = str(brand_preference.get("query") or "").strip()
    preferred_raw = brand_preference.get("preferred") or []
    preferred = [str(value).strip() for value in preferred_raw if str(value).strip()] if isinstance(preferred_raw, list) else []
    if not query:
        return {"enabled": False, "reason": "no inferred brand"}
    js_open = f"""
    (() => {{
      const query = {json.dumps(query, ensure_ascii=False)};
      const preferred = {json.dumps(preferred, ensure_ascii=False)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const cleanLines = (text) => (text || '').split('\\n').map((line) => line.trim()).filter(Boolean);
      const normalized = (text) => (text || '').replace(/\\s+/g, '').toLowerCase();
      const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
        .find((item) => visible(item) && cleanLines(item.innerText)[0] === '品牌');
      if (!formItem) return JSON.stringify({{ error: 'missing brand form item' }});
      const lines = cleanLines(formItem.innerText).filter((line) => line !== '品牌' && line !== '*' && line !== '请输入宝贝的品牌');
      const current = lines.slice(-1)[0] || '';
      if (current && preferred.some((name) => normalized(name) === normalized(current))) {{
        return JSON.stringify({{ selected: current, previous: current, reason: 'already preferred' }});
      }}
      const select = formItem.querySelector('.ant-select');
      const target = formItem.querySelector('.ant-select-selector') || select;
      if (!target) return JSON.stringify({{ error: 'missing brand select', current }});
      target.scrollIntoView({{ block: 'center' }});
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
      const input = formItem.querySelector('input[role="combobox"], input');
      if (!input) return JSON.stringify({{ error: 'missing brand input', current }});
      const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
      input.focus();
      setter.call(input, query);
      input.dispatchEvent(new Event('input', {{ bubbles: true }}));
      input.dispatchEvent(new Event('change', {{ bubbles: true }}));
      input.dispatchEvent(new KeyboardEvent('keydown', {{ key: query.slice(-1) || 's', bubbles: true }}));
      input.dispatchEvent(new KeyboardEvent('keyup', {{ key: query.slice(-1) || 's', bubbles: true }}));
      return JSON.stringify({{ opened: true, query, current, preferred }});
    }})()
    """
    open_result = parse_json_result(chrome_js(js_open))
    if "selected" in open_result:
        return {
            "enabled": True,
            "selected": open_result.get("selected"),
            "previous": open_result.get("previous"),
            "reason": open_result.get("reason"),
            "query": query,
            "preferred": preferred,
        }
    if "error" in open_result:
        return {
            "enabled": False,
            "reason": open_result.get("error"),
            "current": open_result.get("current"),
            "query": query,
            "preferred": preferred,
        }
    time.sleep(1.2)

    js_select = f"""
    (() => {{
      const query = {json.dumps(query, ensure_ascii=False)};
      const preferred = {json.dumps(preferred, ensure_ascii=False)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const normalized = (text) => (text || '').replace(/\\s+/g, '').toLowerCase();
      const optionNodes = Array.from(document.querySelectorAll(
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content, ' +
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item'
      )).filter(visible);
      const options = optionNodes
        .map((el) => (el.innerText || '').trim())
        .filter((text, index, arr) => text && !/暂无数据|无匹配|Not Found/i.test(text) && arr.indexOf(text) === index);
      let chosen = preferred.find((name) => options.some((option) => normalized(option) === normalized(name)));
      if (chosen) chosen = options.find((option) => normalized(option) === normalized(chosen));
      if (!chosen) chosen = options.find((option) => normalized(option).includes(normalized(query)) || normalized(query).includes(normalized(option)));
      if (!chosen) chosen = options[0] || '';
      if (!chosen) return JSON.stringify({{ selected: null, reason: 'no brand option visible', options, query, preferred }});
      const option = optionNodes.find((el) => (el.innerText || '').trim() === chosen);
      const target = option.closest('.ant-select-item-option') || option;
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
      return JSON.stringify({{ selected: chosen, options, query, preferred }});
    }})()
    """
    select_result = parse_json_result(chrome_js(js_select))
    selected = select_result.get("selected")
    if not selected:
        press_escape()
        return {
            "enabled": False,
            "reason": select_result.get("reason", "no brand option selected"),
            "visible_options": select_result.get("options", []),
            "query": query,
            "preferred": preferred,
        }
    time.sleep(0.7)
    verify = parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const cleanLines = (text) => (text || '').split('\\n').map((line) => line.trim()).filter(Boolean);
              const formItem = Array.from(document.querySelectorAll('.ant-form-item'))
                .find((item) => visible(item) && cleanLines(item.innerText)[0] === '品牌');
              const current = formItem
                ? cleanLines(formItem.innerText).filter((line) => line !== '品牌' && line !== '*' && line !== '请输入宝贝的品牌').slice(-1)[0] || ''
                : '';
              return JSON.stringify({ current });
            })()
            """
        )
    )
    return {
        "enabled": True,
        "selected": verify.get("current") or selected,
        "previous": open_result.get("current"),
        "query": query,
        "preferred": preferred,
    }


def select_preferred_brand_with_retry(brand_preference: dict[str, object], timeout: float = 12.0) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    last: dict[str, object] = {"enabled": False, "reason": "not attempted", "brand_preference": brand_preference}
    while time.monotonic() < deadline:
        last = select_preferred_brand(brand_preference)
        reason = str(last.get("reason", ""))
        if last.get("enabled") or reason not in {"missing brand form item", "missing brand select", "missing brand input"}:
            return last
        time.sleep(1)
    return last


def add_sku_spec_type(spec_name: str) -> None:
    js_add = """
    (() => {
      const btn = Array.from(document.querySelectorAll('button'))
        .find((el) => (el.innerText || '').trim().startsWith('添加规格类型'));
      if (!btn) return 'missing add button';
      btn.scrollIntoView({ block: 'center' });
      btn.click();
      return 'clicked add';
    })()
    """
    add_result = chrome_js(js_add)
    if "clicked add" not in add_result:
        raise RuntimeError(f"could not add SKU spec type row: {add_result}")
    time.sleep(0.5)

    js_open = """
    (() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      };
      const select = Array.from(document.querySelectorAll('.ant-select'))
        .filter(visible)
        .find((el) => (el.innerText || '').includes('请选择规格类型'));
      if (!select) return 'missing spec select';
      const target = select.querySelector('.ant-select-selector') || select;
      target.scrollIntoView({ block: 'center' });
      const fire = (type) => target.dispatchEvent(new MouseEvent(type, {
        bubbles: true,
        cancelable: true,
        view: window,
        button: 0,
        buttons: 1
      }));
      target.focus && target.focus();
      fire('pointerdown');
      fire('mousedown');
      fire('mouseup');
      fire('click');
      return 'opened';
    })()
    """
    open_result = chrome_js(js_open)
    if "opened" not in open_result:
        raise RuntimeError(f"could not open SKU spec type dropdown: {open_result}")
    time.sleep(0.5)

    js_select = f"""
    (() => {{
      const specName = {json.dumps(spec_name)};
      const visible = (el) => {{
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
      }};
      const option = Array.from(document.querySelectorAll(
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option-content, ' +
        '.ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item'
      )).find((el) => visible(el) && (el.innerText || '').trim() === specName);
      if (!option) return 'missing option ' + specName;
      const target = option.closest('.ant-select-item-option') || option;
      target.click();
      target.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
      target.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
      return 'selected ' + specName;
    }})()
    """
    select_result = chrome_js(js_select)
    if f"selected {spec_name}" not in select_result:
        raise RuntimeError(f"could not select SKU spec type {spec_name}: {select_result}")
    time.sleep(0.8)


def fill_sku_spec_values(spec_name: str, values: list[str]) -> None:
    for value in values:
        js = f"""
        (() => {{
          const specName = {json.dumps(spec_name)};
          const value = {json.dumps(value)};
          const placeholder = '请输入具体的' + specName;
          const setValue = (input, nextValue) => {{
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            input.focus();
            setter.call(input, nextValue);
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
            input.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', bubbles: true, cancelable: true }}));
            input.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', code: 'Enter', bubbles: true, cancelable: true }}));
          }};
          const inputs = Array.from(document.querySelectorAll('input'))
            .filter((el) => el.placeholder === placeholder);
          if (inputs.some((el) => el.value === value)) return 'exists ' + value;
          const empty = inputs.find((el) => !el.value);
          if (!empty) return 'missing empty input for ' + value;
          setValue(empty, value);
          return 'entered ' + value;
        }})()
        """
        result = chrome_js(js)
        if not any(token in result for token in (f"entered {value}", f"exists {value}")):
            raise RuntimeError(f"could not enter SKU spec value {spec_name}={value}: {result}")
        time.sleep(0.2)


def fill_sku_table(price: str, stock: str) -> dict[str, int]:
    js = f"""
    (() => {{
      const price = {json.dumps(price)};
      const stock = {json.dumps(stock)};
      const table = document.querySelector('.skuTableContainer--aPU8qInw') || document.querySelector('.ant-table-wrapper');
      if (!table) return JSON.stringify({{ error: 'missing SKU table' }});
      const setValue = (input, nextValue) => {{
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
        input.focus();
        setter.call(input, nextValue);
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
      }};
      let prices = 0;
      let stocks = 0;
      for (const input of Array.from(table.querySelectorAll('input')).filter((el) => el.type === 'text')) {{
        if (input.placeholder === '0.00') {{
          setValue(input, price);
          prices += 1;
        }} else if (input.placeholder === '0') {{
          setValue(input, stock);
          stocks += 1;
        }}
      }}
      return JSON.stringify({{ prices, stocks }});
    }})()
    """
    result = parse_json_result(chrome_js(js))
    if "error" in result:
        raise RuntimeError(f"could not fill SKU table: {result['error']}")
    return {
        "prices": int(result.get("prices", 0)),
        "stocks": int(result.get("stocks", 0)),
    }


def fill_sku_specs(specs: dict[str, list[str]], price: str, stock: str) -> dict[str, object]:
    if not specs:
        return {"enabled": False, "reason": "no parsed specs"}
    for spec_name, values in specs.items():
        if not values:
            continue
        add_sku_spec_type(spec_name)
        fill_sku_spec_values(spec_name, values)
    counts = fill_sku_table(price, stock)
    return {
        "enabled": True,
        "specs": specs,
        "sku_count": spec_combination_count(specs),
        "filled_prices": counts["prices"],
        "filled_stocks": counts["stocks"],
        "stock": stock,
    }


def final_state(expected_description: str) -> str:
    description_lines = [line.strip() for line in expected_description.splitlines() if line.strip()]
    description_anchor = description_lines[0][:24] if description_lines else expected_description[:24]
    return chrome_js(
        """
        (() => {
          const descriptionAnchor = __DESCRIPTION_ANCHOR__;
          const text = document.body.innerText || '';
          const uploaded = new Set(Array.from(document.images)
            .map((img) => img.src || '')
            .filter((src) => /-fleamarket\\.jpg_170x10000Q90\\.jpg_\\.webp/.test(src))).size;
          const skuPriceInputsFilled = Array.from(document.querySelectorAll('.skuTableContainer--aPU8qInw input[placeholder="0.00"]')).filter((el) => el.value).length;
          const skuStockInputsFilled = Array.from(document.querySelectorAll('.skuTableContainer--aPU8qInw input[placeholder="0"]')).filter((el) => el.value).length;
          const visible = (el) => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
          };
          const cleanLines = (value) => (value || '').split('\\n').map((line) => line.trim()).filter(Boolean);
          const categoryItem = Array.from(document.querySelectorAll('.ant-form-item'))
            .find((item) => visible(item) && cleanLines(item.innerText)[0] === '分类');
          const category = categoryItem
            ? cleanLines(categoryItem.innerText).filter((line) => line !== '分类' && line !== '*').slice(-1)[0] || ''
            : '';
          const brandItem = Array.from(document.querySelectorAll('.ant-form-item'))
            .find((item) => visible(item) && cleanLines(item.innerText)[0] === '品牌');
          const brand = brandItem
            ? cleanLines(brandItem.innerText).filter((line) => line !== '品牌' && line !== '*' && line !== '请输入宝贝的品牌').slice(-1)[0] || ''
            : '';
          return JSON.stringify({
            url: location.href,
            uploaded,
            hasDescription: descriptionAnchor ? text.includes(descriptionAnchor) : false,
            category,
            brand,
            hasConditionNew: text.includes('成色\\n全新') || text.includes('全新\\n尺码'),
            hasPriceSignal: text.includes('¥83.64') || text.includes('85.00') || skuPriceInputsFilled > 0,
            hasSkuSpecs: text.includes('颜色\\t尺码\\t价格\\t库存') || (text.includes('颜色') && text.includes('尺码') && text.includes('库存')),
            skuPriceInputsFilled,
            skuStockInputsFilled,
            hasPublishButton: text.includes('发布'),
            locationShanghai: text.includes('上海 黄浦区')
          });
        })()
        """.replace("__DESCRIPTION_ANCHOR__", json.dumps(description_anchor)),
    )


def click_publish_button() -> dict[str, object]:
    result = parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const candidates = Array.from(document.querySelectorAll('button'))
                .filter(visible)
                .map((button) => ({ button, text: clean(button.innerText), rect: button.getBoundingClientRect() }))
                .filter((item) => item.text === '发布' || item.text === '立即发布' || item.text === '确认发布');
              candidates.sort((a, b) => (b.rect.width * b.rect.height) - (a.rect.width * a.rect.height));
              const target = candidates[0];
              if (!target) {
                const buttons = Array.from(document.querySelectorAll('button')).filter(visible).map((button) => clean(button.innerText)).filter(Boolean);
                return JSON.stringify({ clicked: false, reason: 'missing publish button', buttons });
              }
              target.button.scrollIntoView({ block: 'center' });
              target.button.click();
              target.button.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
              target.button.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
              target.button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
              return JSON.stringify({ clicked: true, text: target.text, url: location.href });
            })()
            """
        )
    )
    if not result.get("clicked"):
        raise RuntimeError(f"could not click publish button: {result}")
    return result


def click_publish_confirmation_if_present() -> dict[str, object]:
    return parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const overlayText = Array.from(document.querySelectorAll('.ant-modal, .ant-popover, .ant-message, .ant-notification'))
                .filter(visible)
                .map((node) => clean(node.innerText))
                .filter(Boolean)
                .join(' | ');
              const buttons = Array.from(document.querySelectorAll('button'))
                .filter(visible)
                .map((button) => ({ button, text: clean(button.innerText), rect: button.getBoundingClientRect() }))
                .filter((item) => item.text);
              const target = buttons.find((item) => ['确认发布', '继续发布', '确定', '确认', '我知道了'].includes(item.text));
              if (!target) {
                return JSON.stringify({ clicked: false, overlayText, buttons: buttons.map((item) => item.text).slice(0, 20), url: location.href });
              }
              target.button.click();
              target.button.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
              target.button.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
              target.button.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
              return JSON.stringify({ clicked: true, text: target.text, overlayText, url: location.href });
            })()
            """
        )
    )


def publish_observation() -> dict[str, object]:
    return parse_json_result(
        chrome_js(
            """
            (() => {
              const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const text = clean(document.body.innerText);
              const buttons = Array.from(document.querySelectorAll('button')).map((button) => clean(button.innerText)).filter(Boolean).slice(0, 30);
              return JSON.stringify({
                url: location.href,
                title: document.title,
                textSample: text.slice(0, 1200),
                buttons,
                successSignal: /发布成功|提交成功|上架成功|已发布|审核/.test(text) || /\\/item\\?id=/.test(location.href),
                validationSignal: /不能为空|请选择|不能包含|错误|失败/.test(text)
              });
            })()
            """
        )
    )


def publish_current_page(timeout: float = 25.0) -> dict[str, object]:
    click_result = click_publish_button()
    confirmations: list[dict[str, object]] = []
    deadline = time.monotonic() + timeout
    time.sleep(1.5)
    while time.monotonic() < deadline:
        confirmation = click_publish_confirmation_if_present()
        confirmations.append(confirmation)
        if confirmation.get("clicked"):
            time.sleep(1.5)
            continue
        break

    observations: list[dict[str, object]] = []
    while time.monotonic() < deadline:
        observation = publish_observation()
        observations.append(observation)
        if observation.get("successSignal"):
            break
        if observation.get("validationSignal") and len(observations) >= 2:
            break
        time.sleep(2)
    return {
        "clicked": click_result,
        "confirmations": confirmations,
        "observations": observations,
        "final": observations[-1] if observations else publish_observation(),
    }


def detail_primary_image() -> dict[str, object]:
    return parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const candidates = Array.from(document.images)
                .filter(visible)
                .map((img) => {
                  const rect = img.getBoundingClientRect();
                  return {
                    src: img.currentSrc || img.src || '',
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight,
                    renderedWidth: rect.width,
                    renderedHeight: rect.height,
                    area: rect.width * rect.height,
                    className: String(img.className || ''),
                    alt: img.alt || ''
                  };
                })
                .filter((item) => item.src && !item.src.startsWith('data:'))
                .filter((item) => !/avatar|static|icon|logo|head/i.test(item.src))
                .filter((item) => item.renderedWidth >= 120 && item.renderedHeight >= 120)
                .sort((a, b) => b.area - a.area);
              return JSON.stringify({
                url: location.href,
                title: document.title,
                primary: candidates[0] || null,
                candidates: candidates.slice(0, 6)
              });
            })()
            """
        )
    )


def post_publish_cover_check(expected_cover: Path, threshold: int) -> dict[str, object]:
    detail = detail_primary_image()
    primary = detail.get("primary")
    if not isinstance(primary, dict) or not primary.get("src"):
        return {
            "enabled": True,
            "passed": False,
            "reason": "missing primary image on detail page",
            "detail": detail,
            "expected_cover": str(expected_cover),
            "threshold": threshold,
        }

    remote_path: Path | None = None
    try:
        expected_hash = image_average_hash(expected_cover)
        remote_path = download_image_to_temp(str(primary["src"]))
        published_hash = image_average_hash(remote_path)
        distance = hamming_distance_hex(expected_hash, published_hash)
        return {
            "enabled": True,
            "passed": distance <= threshold,
            "reason": "cover hash within threshold" if distance <= threshold else "published cover does not match expected cover",
            "expected_cover": str(expected_cover),
            "expected_cover_name": expected_cover.name,
            "published_cover_url": primary["src"],
            "distance": distance,
            "threshold": threshold,
            "detail_url": detail.get("url"),
            "detail_title": detail.get("title"),
            "primary_image": primary,
        }
    except Exception as exc:
        return {
            "enabled": True,
            "passed": False,
            "reason": f"cover check failed: {exc}",
            "expected_cover": str(expected_cover),
            "published_cover_url": primary.get("src"),
            "threshold": threshold,
            "detail_url": detail.get("url"),
            "detail_title": detail.get("title"),
            "primary_image": primary,
        }
    finally:
        if remote_path is not None:
            remote_path.unlink(missing_ok=True)


def click_seller_action(text: str) -> dict[str, object]:
    return parse_json_result(
        chrome_js(
            """
            (() => {
              const actionText = __ACTION_TEXT__;
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const candidates = Array.from(document.querySelectorAll('button, [role="button"], div, span'))
                .filter(visible)
                .map((el) => ({ el, text: clean(el.innerText || el.textContent), rect: el.getBoundingClientRect(), cursor: getComputedStyle(el).cursor }))
                .filter((item) => item.text === actionText);
              candidates.sort((a, b) => {
                const ac = a.cursor === 'pointer' ? 0 : 1;
                const bc = b.cursor === 'pointer' ? 0 : 1;
                if (ac !== bc) return ac - bc;
                return (a.rect.width * a.rect.height) - (b.rect.width * b.rect.height);
              });
              const candidate = candidates[0];
              if (!candidate) return JSON.stringify({ clicked: false, reason: 'missing action', actionText });
              const target = candidate.el.closest('button') || candidate.el;
              target.scrollIntoView({ block: 'center' });
              const r = target.getBoundingClientRect();
              for (const type of ['pointerover', 'mouseover', 'pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
                const event = type.startsWith('pointer')
                  ? new PointerEvent(type, { bubbles: true, cancelable: true, view: window, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type.includes('down') ? 1 : 0, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2 })
                  : new MouseEvent(type, { bubbles: true, cancelable: true, view: window, button: 0, buttons: type.includes('down') ? 1 : 0, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2 });
                target.dispatchEvent(event);
              }
              return JSON.stringify({ clicked: true, actionText, url: location.href });
            })()
            """.replace("__ACTION_TEXT__", json.dumps(text, ensure_ascii=False))
        )
    )


def confirm_delist_if_present() -> dict[str, object]:
    return parse_json_result(
        chrome_js(
            """
            (() => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
              };
              const clean = (value) => (value || '').replace(/\\s+/g, ' ').trim();
              const overlay = Array.from(document.querySelectorAll('.ant-modal, .ant-popover, [role="dialog"]'))
                .find((node) => visible(node) && clean(node.innerText).includes('确定要下架这个宝贝吗'));
              if (!overlay) return JSON.stringify({ clicked: false, reason: 'missing delist confirmation' });
              const candidates = Array.from(overlay.querySelectorAll('button, [role="button"], div, span'))
                .filter(visible)
                .map((el) => ({ el, text: clean(el.innerText || el.textContent), rect: el.getBoundingClientRect() }))
                .filter((item) => item.text === '确定');
              candidates.sort((a, b) => (a.rect.width * a.rect.height) - (b.rect.width * b.rect.height));
              const candidate = candidates[0];
              if (!candidate) return JSON.stringify({ clicked: false, reason: 'missing confirm button', overlayText: clean(overlay.innerText) });
              const target = candidate.el.closest('button') || candidate.el;
              const r = target.getBoundingClientRect();
              for (const type of ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click']) {
                const event = type.startsWith('pointer')
                  ? new PointerEvent(type, { bubbles: true, cancelable: true, view: window, pointerId: 1, pointerType: 'mouse', isPrimary: true, button: 0, buttons: type.includes('down') ? 1 : 0, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2 })
                  : new MouseEvent(type, { bubbles: true, cancelable: true, view: window, button: 0, buttons: type.includes('down') ? 1 : 0, clientX: r.x + r.width / 2, clientY: r.y + r.height / 2 });
                target.dispatchEvent(event);
              }
              return JSON.stringify({ clicked: true, overlayText: clean(overlay.innerText) });
            })()
            """
        )
    )


def delist_current_item(timeout: float = 15.0) -> dict[str, object]:
    click_result = click_seller_action("下架")
    if not click_result.get("clicked"):
        return {"enabled": True, "success": False, "reason": "could not click delist", "click_result": click_result}
    time.sleep(1)
    confirm_result = confirm_delist_if_present()
    if not confirm_result.get("clicked"):
        return {"enabled": True, "success": False, "reason": "could not confirm delist", "click_result": click_result, "confirm_result": confirm_result}

    deadline = time.monotonic() + timeout
    observations: list[dict[str, object]] = []
    while time.monotonic() < deadline:
        observation = publish_observation()
        observations.append(observation)
        sample = str(observation.get("textSample") or "")
        if "下架成功" in sample or "已下架" in sample:
            return {
                "enabled": True,
                "success": True,
                "click_result": click_result,
                "confirm_result": confirm_result,
                "final": observation,
                "observations": observations,
            }
        time.sleep(1)
    return {
        "enabled": True,
        "success": False,
        "reason": "timed out waiting for delist confirmation",
        "click_result": click_result,
        "confirm_result": confirm_result,
        "observations": observations,
    }


def parse_json_result(raw: str) -> dict[str, object]:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def chrome_url_title() -> tuple[str, str]:
    script = '''
    tell application "Google Chrome"
      activate
      set currentUrl to URL of active tab of front window
      set currentTitle to title of active tab of front window
      return currentUrl & linefeed & currentTitle
    end tell
    '''
    out = osascript(script)
    first, _, rest = out.partition("\n")
    return first.strip(), rest.strip()


def cpa_api_key_from_env() -> str:
    return os.environ.get("AI_PROXY_API_KEY") or os.environ.get("CPA_API_KEY") or DEFAULT_CPA_API_KEY


def chrome_js_enabled() -> bool:
    try:
        chrome_js("1")
        return True
    except ChromeJavaScriptDisabled:
        return False


def enable_chrome_js_from_menu() -> None:
    if chrome_js_enabled():
        print("[ok] Chrome JavaScript from Apple Events is already enabled")
        return
    script = '''
    tell application "Google Chrome" to activate
    tell application "System Events"
      tell process "Google Chrome"
        set menuClicked to false
        try
          click menu item "允许 Apple 事件中的 JavaScript" of menu 1 of menu item "开发者" of menu 1 of menu bar item "显示" of menu bar 1
          set menuClicked to true
        on error
          try
            click menu item "Allow JavaScript from Apple Events" of menu 1 of menu item "Developer" of menu 1 of menu bar item "View" of menu bar 1
            set menuClicked to true
          end try
        end try
        return menuClicked
      end tell
    end tell
    '''
    result = osascript(script)
    if "true" not in result:
        raise RuntimeError("could not find Chrome menu item for Allow JavaScript from Apple Events")
    time.sleep(0.5)
    if not chrome_js_enabled():
        raise RuntimeError("clicked Chrome menu item, but JavaScript from Apple Events is still disabled")
    print("[ok] enabled Chrome JavaScript from Apple Events")


def doctor(
    package_dir: Path | None,
    max_images: int,
    *,
    copy_extractor: str = "rule",
    cpa_base_url: str = DEFAULT_CPA_BASE_URL,
    cpa_model: str = DEFAULT_CPA_MODEL,
    cpa_api_key: str = DEFAULT_CPA_API_KEY,
    cpa_timeout: float = 45.0,
) -> int:
    ok = True
    print("[doctor] checking local package")
    if package_dir:
        try:
            item = load_item_details(
                package_dir,
                max_images,
                copy_extractor=copy_extractor,
                cpa_base_url=cpa_base_url,
                cpa_model=cpa_model,
                cpa_api_key=cpa_api_key,
                cpa_timeout=cpa_timeout,
            )
            description = str(item["listing_description"])
            price = str(item["price"])
            images = item["images"]
            assert isinstance(images, list)
            extraction = item["copy_extraction"]
            assert isinstance(extraction, dict)
            print(f"[ok] package={package_dir}")
            print(f"[ok] price={price} description_chars={len(description)} images_selected={len(images)}")
            print(f"[ok] copy_extraction_source={extraction.get('source')}")
            print(f"[ok] removed_description_lines={len(item['removed_description_lines'])}")
            if len(images) > 9:
                print("[fail] selected more than 9 images")
                ok = False
        except Exception as exc:
            print(f"[fail] package check failed: {exc}")
            ok = False

    print("[doctor] checking Chrome")
    try:
        url, title = chrome_url_title()
        print(f"[ok] chrome active tab title={title!r} url={url!r}")
    except Exception as exc:
        print(f"[fail] cannot read Chrome active tab: {exc}")
        ok = False

    print("[doctor] checking Chrome JavaScript-from-Apple-Events")
    try:
        title = chrome_js("document.title")
        print(f"[ok] chrome_js returned title={title!r}")
    except ChromeJavaScriptDisabled as exc:
        print(f"[fail] {exc}")
        ok = False
    except Exception as exc:
        print(f"[fail] chrome_js failed: {exc}")
        ok = False

    return 0 if ok else 2


def write_summary(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[summary] wrote {path}")


def self_test() -> int:
    assert strip_emoji("85💰潮牌🎁 test").startswith("85潮牌")
    assert normalize_price("¥85") == "85.00"
    assert normalize_price("85.5 元") == "85.50"
    assert listing_price_from_supplier_price("110") == "159.00"
    assert listing_price_from_supplier_price("120") == "169.00"
    assert listing_price_from_supplier_price("145") == "209.00"
    sample_copy = "颜色：白色 黑色\nM    L    XL   XXL\n胸围  100  104  106   108"
    assert parse_specs(sample_copy) == {"颜色": ["白色", "黑色"], "尺码": ["M", "L", "XL", "XXL"]}
    assert spec_combination_count(parse_specs(sample_copy)) == 8
    ranged_copy = "颜色：黑色 白色\n尺码：S-XL\n衣长 胸围 肩宽 袖长\nS 71 112 52 22.5\nM 73 118 54 23"
    assert parse_specs(ranged_copy) == {"颜色": ["黑色", "白色"], "尺码": ["S", "M", "L", "XL"]}
    ranged_description, ranged_removed = clean_listing_description("上新💰105\n标题\n" + ranged_copy, "105.00")
    assert ranged_description == "标题"
    assert "尺码：S-XL" in ranged_removed
    assert "衣长 胸围 肩宽 袖长" in ranged_removed
    supplier_copy = "\n".join(
        [
            "85💰潮牌🎁 克罗心chromehearts贴布刺绣重工 情侣款短袖T恤！",
            "购入原版开模打造，全套定制辅料，细节决定成败。",
            "颜色：白色 黑色",
            "M    L    XL   XXL",
            "胸围  100  104  106   108",
            "肩宽  40   41   42   43",
            "衣长  67   69   71   73",
        ]
    )
    listing_description, removed_lines = clean_listing_description(supplier_copy, "85.00")
    assert listing_description.startswith("潮牌 克罗心chromehearts")
    assert "颜色" not in listing_description
    assert "胸围" not in listing_description
    assert "85潮牌" not in listing_description
    assert len(removed_lines) == 6
    intro_description, intro_removed = clean_listing_description(
        "上新💰105\n【款号：SzKlx03】顶级版本\n颜色：黑色 白色\n尺码：S-XL",
        "105.00",
    )
    assert intro_description.startswith("【款号：SzKlx03】")
    assert "上新105" not in intro_description
    assert intro_removed[0] == "上新105"
    assert infer_category_preferences("短袖T恤")[:3] == ["运动T恤", "速干衣", "文化衫"]
    assert infer_category_preferences("防晒夹克外套")[:3] == ["运动外套", "防晒衣", "速干衣"]
    assert infer_brand_preference("Chrome Hearts 克罗心短袖")["query"] == "Chrome Hearts"
    assert infer_brand_preference("Adidas 三叶草外套")["query"] == "Adidas"
    assert infer_brand_preference("始祖鸟冲锋衣")["query"] == "Arc'teryx"
    fallback = rule_extract_copy(supplier_copy, "85.00")
    validated = validate_copy_extraction(
        {
            "listing_description": "购入原版开模打造，全套定制辅料，细节决定成败。",
            "price": "85",
            "sku_specs": {"颜色": ["白色", "黑色"], "尺码": ["M", "L", "XL", "XXL"]},
        },
        fallback,
        "85.00",
    )
    validated_title = str(validated["listing_description"])
    assert "克罗心" in validated_title or "chromehearts" in validated_title.lower()
    assert compact_title_length(validated_title) <= MAX_LISTING_TITLE_CHARS
    assert "restored fallback title" in " ".join(validated["notes"])  # type: ignore[arg-type]
    djia_title = trim_listing_title("D家 男士凉感防晒短袖POLO衫，TRAINING综训系列")
    assert djia_title.startswith("D家")
    assert "，" not in djia_title
    assert compact_title_length(djia_title) <= MAX_LISTING_TITLE_CHARS
    assert trim_listing_title("迪桑特 26款Ess吸湿速干防晒短袖T恤").startswith("D家")
    assert trim_listing_title("FILA 运动夹克外套").startswith("F家")
    assert trim_listing_title("可隆 户外防晒外套").startswith("K家")
    templated = build_goofish_description(djia_title, {"尺码": ["M", "L", "XL", "2XL", "3XL"]})
    assert templated.splitlines() == [
        f"【奥莱折扣】2折+ {djia_title}",
        "尺码 M-3XL",
        "部分 断码 数量有限",
        "主页均为实拍 需要的点击我想要咨询",
    ]

    with tempfile.TemporaryDirectory(prefix="goofish-publish-selftest-") as tmp:
        package_dir = Path(tmp)
        image_dir = package_dir / "images"
        image_dir.mkdir()
        (package_dir / "copy.goofish.txt").write_text("85💰标题\n颜色：白色 黑色\nM L\n正文", encoding="utf-8")
        (package_dir / "package.json").write_text(
            json.dumps({"price": "¥85", "copy_goofish": "copy.goofish.txt"}, ensure_ascii=False),
            encoding="utf-8",
        )
        for i in range(1, 12):
            (image_dir / f"{i:02d}.jpg").write_bytes(b"")
        description, price, images = load_item(package_dir, 9)
        assert description == "标题\n正文"
        assert price == "85.00"
        assert len(images) == 9
        assert images[0].name == "01.jpg"
        assert images[-1].name == "09.jpg"
        plan = package_plan(package_dir, 9)
        assert plan["selected_image_count"] == 9
        assert plan["will_click_publish"] is False
        assert plan["supplier_price"] == "85.00"
        assert plan["listing_price"] == "119.00"
        assert plan["sku_specs"] == {"颜色": ["白色", "黑色"], "尺码": ["M", "L"]}
        assert plan["removed_description_lines"] == ["leading price: 85", "颜色：白色 黑色", "M L"]

    print("[ok] self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path, nargs="?")
    parser.add_argument("--doctor", action="store_true", help="check package, Chrome, and required local permissions; do not edit the page")
    parser.add_argument(
        "--enable-chrome-js-menu",
        action="store_true",
        help="explicitly enable Chrome's View > Developer > Allow JavaScript from Apple Events menu item",
    )
    parser.add_argument("--self-test", action="store_true", help="run local unit checks that do not touch Chrome or Goofish")
    parser.add_argument("--plan-json", action="store_true", help="print the package plan as JSON and exit without touching Chrome")
    parser.add_argument("--write-summary", type=Path, help="write a JSON summary after a successful dry run")
    parser.add_argument("--max-images", type=int, default=9, help="maximum images to upload; Goofish currently accepts 9")
    parser.add_argument("--no-upload", action="store_true", help="fill text/price/condition only; do not open file upload dialogs")
    parser.add_argument("--skip-category", action="store_true", help="do not adjust Goofish category after text/price fill")
    parser.add_argument("--skip-brand", action="store_true", help="do not search/select brand after category selection")
    parser.add_argument("--skip-sku-specs", action="store_true", help="do not parse/fill color and size SKU specs from the copy")
    parser.add_argument("--sku-stock", default=DEFAULT_SKU_STOCK, help=f"stock value to fill for each generated SKU; default {DEFAULT_SKU_STOCK}")
    parser.add_argument("--original-price", help="optional original price to fill; omitted by default")
    parser.add_argument(
        "--copy-extractor",
        choices=["auto", "cpa", "rule"],
        default="auto",
        help="copy analysis strategy; auto tries local CPA then falls back to deterministic rules",
    )
    parser.add_argument("--cpa-base-url", default=os.environ.get("CPA_BASE_URL", DEFAULT_CPA_BASE_URL))
    parser.add_argument("--cpa-model", default=os.environ.get("CPA_MODEL", DEFAULT_CPA_MODEL))
    parser.add_argument("--cpa-timeout", type=float, default=float(os.environ.get("CPA_TIMEOUT", "45")))
    parser.add_argument(
        "--keep-raw-description",
        action="store_true",
        help="fill the original supplier copy instead of the cleaned buyer-facing description",
    )
    parser.add_argument(
        "--upload-mode",
        choices=["file-input", "file-picker"],
        default="file-input",
        help="image upload strategy; file-input injects browser File objects and avoids the macOS picker",
    )
    parser.add_argument("--per-image-timeout", type=float, default=35.0)
    parser.add_argument("--skip-open", action="store_true", help="use the current Chrome tab instead of opening /publish")
    parser.add_argument("--new-tab", action="store_true", help="open /publish in a new Chrome tab instead of reusing the active tab")
    parser.add_argument("--cdp-port", type=int, default=None, help="target a Chrome remote-debugging port instead of AppleScript front-window Chrome")
    parser.add_argument("--publish", action="store_true", help="click the final Goofish publish button after filling the form")
    parser.add_argument("--skip-post-publish-check", action="store_true", help="do not verify the published detail page cover after --publish")
    parser.add_argument("--post-publish-cover-threshold", type=int, default=80, help="maximum cover-image perceptual hash distance; default 80")
    parser.add_argument("--auto-delist-on-check-fail", action="store_true", help="after --publish, automatically delist the item if post-publish cover check fails")
    args = parser.parse_args()
    global CDP_PORT
    CDP_PORT = args.cdp_port

    if args.max_images < 1 or args.max_images > 9:
        parser.error("--max-images must be between 1 and 9")

    if args.self_test:
        return self_test()

    if args.package_dir is None:
        parser.error("package_dir is required unless --self-test is used")

    cpa_api_key = cpa_api_key_from_env()

    if args.plan_json:
        print(
            json.dumps(
                package_plan(
                    args.package_dir,
                    args.max_images,
                    copy_extractor=args.copy_extractor,
                    cpa_base_url=args.cpa_base_url,
                    cpa_model=args.cpa_model,
                    cpa_api_key=cpa_api_key,
                    cpa_timeout=args.cpa_timeout,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.enable_chrome_js_menu:
        enable_chrome_js_from_menu()

    if args.doctor:
        return doctor(
            args.package_dir,
            args.max_images,
            copy_extractor=args.copy_extractor,
            cpa_base_url=args.cpa_base_url,
            cpa_model=args.cpa_model,
            cpa_api_key=cpa_api_key,
            cpa_timeout=args.cpa_timeout,
        )

    start = time.monotonic()
    item = load_item_details(
        args.package_dir,
        args.max_images,
        copy_extractor=args.copy_extractor,
        cpa_base_url=args.cpa_base_url,
        cpa_model=args.cpa_model,
        cpa_api_key=cpa_api_key,
        cpa_timeout=args.cpa_timeout,
    )
    plan = package_plan_from_item(args.package_dir, args.max_images, item, args.copy_extractor)
    raw_description = str(item["raw_description"])
    supplier_price = str(item["price"])
    price = listing_price_from_supplier_price(supplier_price)
    images = item["images"]
    assert isinstance(images, list)
    original_price = normalize_price(args.original_price) if args.original_price else None
    extraction = item["copy_extraction"]
    assert isinstance(extraction, dict)
    specs = extraction.get("sku_specs")
    if not isinstance(specs, dict):
        specs = parse_specs(raw_description)
    listing_title = str(item["listing_description"])
    description = raw_description if args.keep_raw_description else build_goofish_description(listing_title, specs)
    plan["skip_sku_specs"] = args.skip_sku_specs
    plan["skip_category"] = args.skip_category
    plan["skip_brand"] = args.skip_brand
    plan["sku_stock"] = args.sku_stock
    plan["original_price"] = original_price
    plan["upload_mode"] = args.upload_mode
    plan["description_mode"] = "raw" if args.keep_raw_description else "clean"
    plan["dry_run"] = not args.publish
    plan["will_click_publish"] = args.publish
    plan["post_publish_check_enabled"] = args.publish and not args.skip_post_publish_check
    plan["auto_delist_on_check_fail"] = args.auto_delist_on_check_fail
    print(f"[item] {args.package_dir}")
    plan["price"] = price
    plan["listing_price"] = price
    plan["supplier_price"] = supplier_price
    plan["price_rule"] = "supplier_price / 0.7, rounded to nearest price ending in 9"
    print(f"[item] supplier_price={supplier_price} listing_price={price} images={len(images)} description_mode={plan['description_mode']} dry_run={str(not args.publish).lower()}")
    print(f"[copy] extractor={extraction.get('source')}")
    for note in extraction.get("notes", []):
        print(f"[copy] note={note}")
    if item["removed_description_lines"] and not args.keep_raw_description:
        print(f"[copy] removed supplier-only lines={len(item['removed_description_lines'])}")
    if specs and not args.skip_sku_specs:
        print(f"[sku] parsed specs={json.dumps(specs, ensure_ascii=False)} stock={args.sku_stock}")
    elif args.skip_sku_specs:
        print("[sku] skipped by --skip-sku-specs")
    else:
        print("[sku] no color/size specs parsed from copy")

    press_escape()
    if not args.skip_open:
        open_publish_page(new_tab=args.new_tab)
    wait_for_page_ready()
    fill_text_and_price(description, price, original_price)
    category_result = {"enabled": False, "reason": "skipped"}
    brand_result = {"enabled": False, "reason": "skipped"}
    if args.no_upload:
        print("[upload] skipped by --no-upload")
    else:
        upload_images(images, args.per_image_timeout, args.upload_mode)
    if not args.skip_category:
        category_preferences = infer_category_preferences(raw_description + "\n" + listing_title)
        category_result = select_preferred_category_with_retry(category_preferences)
        if category_result.get("enabled"):
            print(f"[category] selected={category_result.get('selected')} previous={category_result.get('previous')}")
        else:
            print(f"[category] unchanged reason={category_result.get('reason')}")
    if not args.skip_brand:
        brand_preference = infer_brand_preference(raw_description + "\n" + listing_title)
        brand_result = select_preferred_brand_with_retry(brand_preference)
        if brand_result.get("enabled"):
            print(f"[brand] selected={brand_result.get('selected')} query={brand_result.get('query')}")
        else:
            print(f"[brand] unchanged reason={brand_result.get('reason')}")
    select_condition_new()
    sku_result = {"enabled": False, "reason": "skipped"}
    if not args.skip_sku_specs:
        sku_result = fill_sku_specs(specs, price, args.sku_stock)
        if sku_result.get("enabled"):
            print(f"[sku] filled {sku_result['sku_count']} combinations prices={sku_result['filled_prices']} stocks={sku_result['filled_stocks']}")

    state = final_state(description)
    publish_result: dict[str, object] = {"enabled": False, "reason": "dry-run"}
    post_publish_check: dict[str, object] = {"enabled": False, "reason": "dry-run"}
    auto_delist_result: dict[str, object] = {"enabled": False, "reason": "not requested"}
    if args.publish:
        print("[publish] clicking final publish button")
        publish_result = publish_current_page()
        print(f"[publish] result={json.dumps(publish_result.get('final', {}), ensure_ascii=False)}")
        if args.skip_post_publish_check:
            post_publish_check = {"enabled": False, "reason": "skipped"}
        else:
            expected_cover = images[0]
            print(f"[postcheck] expected_cover={expected_cover.name}")
            post_publish_check = post_publish_cover_check(expected_cover, args.post_publish_cover_threshold)
            print(f"[postcheck] result={json.dumps(post_publish_check, ensure_ascii=False)}")
            if not post_publish_check.get("passed") and args.auto_delist_on_check_fail:
                print("[postcheck] failed; auto-delisting current item")
                auto_delist_result = delist_current_item()
                print(f"[postcheck] delist_result={json.dumps(auto_delist_result, ensure_ascii=False)}")

    elapsed = time.monotonic() - start
    print(f"[state] {state}")
    if args.publish:
        print(f"[done] publish attempted; elapsed={elapsed:.1f}s")
    else:
        print(f"[done] stopped before publish; elapsed={elapsed:.1f}s")
    if args.write_summary:
        write_summary(
            args.write_summary,
            {
                "created_at": now_iso(),
                "elapsed_seconds": round(elapsed, 1),
                "plan": plan,
                "category_result": category_result,
                "brand_result": brand_result,
                "sku_result": sku_result,
                "final_state": parse_json_result(state),
                "publish_result": publish_result,
                "post_publish_check": post_publish_check,
                "auto_delist_result": auto_delist_result,
            },
        )
    if args.publish and post_publish_check.get("enabled") and not post_publish_check.get("passed"):
        return 3
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ChromeJavaScriptDisabled as exc:
        print(f"[fail] {exc}", file=sys.stderr)
        raise SystemExit(2)
    except subprocess.CalledProcessError as exc:
        print(exc.stdout, file=sys.stderr)
        print(exc.stderr, file=sys.stderr)
        raise
