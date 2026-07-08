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
import re
import subprocess
import sys
import tempfile
import time
import unicodedata
from pathlib import Path


PUBLISH_URL = "https://www.goofish.com/publish"
CHROME_JS_DISABLED_HINT = (
    "Chrome has disabled JavaScript from Apple Events. In Chrome, enable: "
    "View > Developer > Allow JavaScript from Apple Events, then run --doctor again."
)


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


def split_spec_values(raw: str) -> list[str]:
    values: list[str] = []
    for token in re.split(r"[\s,，、/]+", raw.strip()):
        token = token.strip("：:;；")
        if token and token not in values:
            values.append(token)
    return values


def parse_colors(description: str) -> list[str]:
    for line in description.splitlines():
        match = re.search(r"颜色\s*[:：]\s*(.+)", line)
        if match:
            return split_spec_values(match.group(1))
    return []


def parse_sizes(description: str) -> list[str]:
    size_pattern = re.compile(r"^(?:均码|XXS|XS|S|M|L|XL|XXL|XXXL|[2-9]XL)$", re.IGNORECASE)
    for line in description.splitlines():
        values = split_spec_values(line)
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


def spec_combination_count(specs: dict[str, list[str]]) -> int:
    count = 1
    used = False
    for values in specs.values():
        if values:
            used = True
            count *= len(values)
    return count if used else 0


def resolve_package_file(package_dir: Path, raw_path: str | None, fallback_name: str) -> Path:
    if raw_path:
        path = Path(raw_path)
        return path if path.is_absolute() else package_dir / path
    return package_dir / fallback_name


def image_files(image_dir: Path) -> list[Path]:
    allowed = {".jpg", ".jpeg", ".png", ".webp"}
    return sorted(path for path in image_dir.iterdir() if path.is_file() and path.suffix.lower() in allowed)


def load_item(package_dir: Path, max_images: int) -> tuple[str, str, list[Path]]:
    package_json = package_dir / "package.json"
    if not package_json.exists():
        raise FileNotFoundError(f"missing package.json: {package_json}")
    meta = json.loads(package_json.read_text(encoding="utf-8"))

    copy_path = resolve_package_file(package_dir, meta.get("copy_goofish"), "copy.goofish.txt")
    if not copy_path.exists():
        raise FileNotFoundError(f"missing copy text: {copy_path}")
    description = strip_emoji(copy_path.read_text(encoding="utf-8"))
    raw_price = str(meta.get("price") or "").strip()
    if not raw_price:
        raise ValueError("package.json has no price")
    price = normalize_price(raw_price)

    image_dir = package_dir / "images"
    if not image_dir.exists():
        raise FileNotFoundError(f"missing image directory: {image_dir}")
    images = image_files(image_dir)[:max_images]
    if not images:
        raise FileNotFoundError(f"no supported images found in {image_dir}")
    return description, price, images


def package_plan(package_dir: Path, max_images: int) -> dict[str, object]:
    description, price, images = load_item(package_dir, max_images)
    specs = parse_specs(description)
    return {
        "package_dir": str(package_dir),
        "dry_run": True,
        "publish_url": PUBLISH_URL,
        "price": price,
        "sku_specs": specs,
        "sku_count": spec_combination_count(specs),
        "description_chars": len(description),
        "description_preview": description[:80],
        "max_images": max_images,
        "selected_image_count": len(images),
        "selected_images": [str(path) for path in images],
        "will_click_publish": False,
    }


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


def final_state() -> str:
    return chrome_js(
        """
        (() => {
          const text = document.body.innerText || '';
          const uploaded = new Set(Array.from(document.images)
            .map((img) => img.src || '')
            .filter((src) => /-fleamarket\\.jpg_170x10000Q90\\.jpg_\\.webp/.test(src))).size;
          const skuPriceInputsFilled = Array.from(document.querySelectorAll('.skuTableContainer--aPU8qInw input[placeholder="0.00"]')).filter((el) => el.value).length;
          const skuStockInputsFilled = Array.from(document.querySelectorAll('.skuTableContainer--aPU8qInw input[placeholder="0"]')).filter((el) => el.value).length;
          return JSON.stringify({
            url: location.href,
            uploaded,
            hasDescription: text.includes('克罗心chromehearts'),
            hasConditionNew: text.includes('成色\\n全新') || text.includes('全新\\n尺码'),
            hasPriceSignal: text.includes('¥83.64') || text.includes('85.00') || skuPriceInputsFilled > 0,
            hasSkuSpecs: text.includes('颜色\\t尺码\\t价格\\t库存') || (text.includes('颜色') && text.includes('尺码') && text.includes('库存')),
            skuPriceInputsFilled,
            skuStockInputsFilled,
            hasPublishButton: text.includes('发布'),
            locationShanghai: text.includes('上海 黄浦区')
          });
        })()
        """,
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


def doctor(package_dir: Path | None, max_images: int) -> int:
    ok = True
    print("[doctor] checking local package")
    if package_dir:
        try:
            description, price, images = load_item(package_dir, max_images)
            print(f"[ok] package={package_dir}")
            print(f"[ok] price={price} description_chars={len(description)} images_selected={len(images)}")
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

    with tempfile.TemporaryDirectory(prefix="goofish-publish-selftest-") as tmp:
        package_dir = Path(tmp)
        image_dir = package_dir / "images"
        image_dir.mkdir()
        (package_dir / "copy.goofish.txt").write_text("标题💰\n正文", encoding="utf-8")
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
    parser.add_argument("--skip-sku-specs", action="store_true", help="do not parse/fill color and size SKU specs from the copy")
    parser.add_argument("--sku-stock", default="1", help="stock value to fill for each generated SKU; default 1")
    parser.add_argument("--original-price", help="optional original price to fill; omitted by default")
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

    if args.plan_json:
        print(json.dumps(package_plan(args.package_dir, args.max_images), ensure_ascii=False, indent=2))
        return 0

    if args.enable_chrome_js_menu:
        enable_chrome_js_from_menu()

    if args.doctor:
        return doctor(args.package_dir, args.max_images)

    start = time.monotonic()
    plan = package_plan(args.package_dir, args.max_images)
    description, price, images = load_item(args.package_dir, args.max_images)
    original_price = normalize_price(args.original_price) if args.original_price else None
    specs = parse_specs(description)
    plan["skip_sku_specs"] = args.skip_sku_specs
    plan["sku_stock"] = args.sku_stock
    plan["original_price"] = original_price
    plan["upload_mode"] = args.upload_mode
    print(f"[item] {args.package_dir}")
    print(f"[item] price={price} images={len(images)} dry_run=true")
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
    if args.no_upload:
        print("[upload] skipped by --no-upload")
    else:
        upload_images(images, args.per_image_timeout, args.upload_mode)
    select_condition_new()
    sku_result = {"enabled": False, "reason": "skipped"}
    if not args.skip_sku_specs:
        sku_result = fill_sku_specs(specs, price, args.sku_stock)
        if sku_result.get("enabled"):
            print(f"[sku] filled {sku_result['sku_count']} combinations prices={sku_result['filled_prices']} stocks={sku_result['filled_stocks']}")

    state = final_state()
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
