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
import urllib.request
from pathlib import Path


PUBLISH_URL = "https://www.goofish.com/publish"
DEFAULT_CPA_BASE_URL = "http://100.84.194.46:8317"
DEFAULT_CPA_MODEL = "claude-sonnet-4-6"
DEFAULT_CPA_API_KEY = "cliproxyapi-local"
DEFAULT_SKU_STOCK = "20"
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


def chrome_js(js: str, *, check: bool = True) -> str:
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


def open_publish_page() -> None:
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
    match = re.match(r"^\s*(?:[¥￥]\s*)?(\d+(?:\.\d+)?)\s*(.*)$", line)
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
    return without_price in {"", "上新", "新款", "现货", "到货", "补货", "特价", "推荐"}


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
    notes = result.get("notes")
    if isinstance(notes, list):
        normalized_notes = [str(note).strip() for note in notes if str(note).strip()]
    elif notes:
        normalized_notes = [str(notes).strip()]
    else:
        normalized_notes = []

    fallback_description = str(fallback.get("listing_description") or "").strip()
    fallback_first_line = next((line.strip() for line in fallback_description.splitlines() if line.strip()), "")
    title_tokens = [
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9-]{2,}|[\u4e00-\u9fff]{2,}", fallback_first_line)
        if token not in {"潮牌", "情侣款", "短袖", "恤"}
    ]
    if fallback_first_line and fallback_first_line not in listing_description:
        has_title_signal = any(token.lower() in listing_description.lower() for token in title_tokens)
        if not has_title_signal:
            listing_description = f"{fallback_first_line}\n{listing_description}".strip()
            normalized_notes.append("model output omitted title/brand line; restored fallback title")

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
        "目标是把供货商原始文案拆成买家可见描述、价格、SKU 规格和被丢弃的供货字段。"
    )
    user_prompt = f"""
请分析下面的供货商原始文案，返回严格 JSON：
{{
  "listing_description": "适合直接粘贴到闲鱼宝贝描述的中文文案，不要包含价格、颜色行、尺码列表、胸围肩宽衣长等尺码表",
  "price": "数字价格，保留两位小数",
  "sku_specs": {{"颜色": ["..."], "尺码": ["..."]}},
  "removed_description_lines": ["从描述中移除但用于价格/SKU/尺码表的原文行"],
  "notes": ["可选，简短说明"]
}}

规则：
- 若开头出现类似“85💰标题”，且 85 与给定价格一致，则 85 是价格，不应进入 listing_description。
- 颜色、尺码、胸围、肩宽、衣长、袖长、腰围、裤长等结构化信息不要进入 listing_description。
- 不要虚构商品卖点，不要改写品牌/型号事实。
- 如果不确定某个字段，优先保守保留在 listing_description。

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
    has_tshirt = bool(re.search(r"T恤|t恤|tee|短袖", description, re.IGNORECASE))
    has_outer = bool(re.search(r"外套|夹克|冲锋衣|防晒衣|开衫|棒球服|风衣", description))
    if has_tshirt:
        prefs.extend(["运动T恤", "速干衣", "文化衫"])
    elif has_outer:
        prefs.extend(["运动外套", "防晒衣", "速干衣"])
    if re.search(r"卫衣|帽衫", description):
        prefs.extend(["运动卫衣", "运动外套"])
    if re.search(r"polo|POLO|polo衫", description):
        prefs.extend(["运动polo衫", "运动T恤"])
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
    images = image_files(image_dir)[:max_images]
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
    description = str(item["listing_description"])
    raw_description = str(item["raw_description"])
    price = str(item["price"])
    images = item["images"]
    assert isinstance(images, list)
    extraction = item["copy_extraction"]
    assert isinstance(extraction, dict)
    specs = extraction.get("sku_specs")
    if not isinstance(specs, dict):
        specs = parse_specs(raw_description)
    return {
        "package_dir": str(package_dir),
        "dry_run": True,
        "publish_url": PUBLISH_URL,
        "price": price,
        "copy_extractor": copy_extractor,
        "copy_extraction_source": extraction.get("source"),
        "copy_extraction_notes": extraction.get("notes", []),
        "sku_specs": specs,
        "sku_count": spec_combination_count(specs),
        "raw_description_chars": len(raw_description),
        "description_chars": len(description),
        "description_preview": description[:80],
        "removed_description_lines": item["removed_description_lines"],
        "category_preferences": infer_category_preferences(description),
        "brand_preference": infer_brand_preference(raw_description + "\n" + description),
        "max_images": max_images,
        "selected_image_count": len(images),
        "selected_images": [str(path) for path in images],
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
      if (preferences.includes(current)) return JSON.stringify({{ selected: current, previous: current, reason: 'already preferred' }});
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
    assert str(validated["listing_description"]).startswith("潮牌 克罗心chromehearts")
    assert "restored fallback title" in " ".join(validated["notes"])  # type: ignore[arg-type]

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
    args = parser.parse_args()

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
    description = raw_description if args.keep_raw_description else str(item["listing_description"])
    price = str(item["price"])
    images = item["images"]
    assert isinstance(images, list)
    original_price = normalize_price(args.original_price) if args.original_price else None
    extraction = item["copy_extraction"]
    assert isinstance(extraction, dict)
    specs = extraction.get("sku_specs")
    if not isinstance(specs, dict):
        specs = parse_specs(raw_description)
    plan["skip_sku_specs"] = args.skip_sku_specs
    plan["skip_category"] = args.skip_category
    plan["skip_brand"] = args.skip_brand
    plan["sku_stock"] = args.sku_stock
    plan["original_price"] = original_price
    plan["upload_mode"] = args.upload_mode
    plan["description_mode"] = "raw" if args.keep_raw_description else "clean"
    print(f"[item] {args.package_dir}")
    print(f"[item] price={price} images={len(images)} description_mode={plan['description_mode']} dry_run=true")
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
        open_publish_page()
    wait_for_page_ready()
    fill_text_and_price(description, price, original_price)
    category_result = {"enabled": False, "reason": "skipped"}
    brand_result = {"enabled": False, "reason": "skipped"}
    if args.no_upload:
        print("[upload] skipped by --no-upload")
    else:
        upload_images(images, args.per_image_timeout, args.upload_mode)
    if not args.skip_category:
        category_preferences = infer_category_preferences(description)
        category_result = select_preferred_category_with_retry(category_preferences)
        if category_result.get("enabled"):
            print(f"[category] selected={category_result.get('selected')} previous={category_result.get('previous')}")
        else:
            print(f"[category] unchanged reason={category_result.get('reason')}")
    if not args.skip_brand:
        brand_preference = infer_brand_preference(raw_description + "\n" + description)
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
    elapsed = time.monotonic() - start
    print(f"[state] {state}")
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
            },
        )
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
