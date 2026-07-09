#!/usr/bin/env python3
"""Maintain SZWego-to-Goofish de-duplication fingerprints.

SZWego exposes per-post IDs, but those IDs can change if a supplier copies or
reposts the same item. The stable business key for our workflow is the
normalized full source copy, with platform IDs and media fingerprints kept as
secondary evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import urllib.parse
from pathlib import Path


def strip_emoji(text: str) -> str:
    kept: list[str] = []
    for ch in text:
        category = unicodedata.category(ch)
        if category == "So" or ord(ch) > 0xFFFF:
            continue
        kept.append(ch)
    return "".join(kept)


def digest_text(text: str, length: int = 16) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def normalize_source_copy(text: str) -> str:
    text = unicodedata.normalize("NFKC", strip_emoji(text))
    text = re.sub(r"(?<![A-Za-z0-9])D家", "迪桑特", text)
    text = re.sub(r"^\s*(?:[¥￥]\s*)?\d+(?:\.\d+)?\s*发\s*[，,、]?\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[，,。；;：:、\s]+$", "", text)
    return text.strip().lower()


def normalize_media_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def media_fingerprint_from_urls(urls: list[str]) -> str:
    normalized = [normalize_media_url(url) for url in urls if url]
    return digest_text("\n".join(normalized)) if normalized else ""


def package_media_fingerprint(package_dir: Path) -> str:
    image_dir = package_dir / "images"
    if not image_dir.exists():
        return ""
    image_hashes: list[str] = []
    for path in sorted(image_dir.iterdir())[:12]:
        if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        image_hashes.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return digest_text("\n".join(image_hashes)) if image_hashes else ""


def package_fingerprints(package_dir: Path) -> dict[str, str]:
    package_json = package_dir / "package.json"
    copy_path = package_dir / "copy.goofish.txt"
    meta = json.loads(package_json.read_text(encoding="utf-8")) if package_json.exists() else {}
    copy = copy_path.read_text(encoding="utf-8") if copy_path.exists() else ""
    normalized = normalize_source_copy(copy)
    return {
        "source_goods_id": str(meta.get("source_goods_id") or ""),
        "business_dedupe_id": f"copy:{digest_text(normalized)}" if normalized else "",
        "normalized_copy_fingerprint": digest_text(normalized) if normalized else "",
        "media_fingerprint": package_media_fingerprint(package_dir),
    }


def selected_group_fingerprints(group: dict[str, object]) -> dict[str, str]:
    title = str(group.get("title") or "")
    normalized = normalize_source_copy(title)
    imgs_raw = group.get("imgs") or group.get("imgsSrc") or []
    imgs = [str(url) for url in imgs_raw] if isinstance(imgs_raw, list) else []
    return {
        "source_goods_id": str(group.get("source_goods_id") or ""),
        "business_dedupe_id": f"copy:{digest_text(normalized)}" if normalized else "",
        "normalized_copy_fingerprint": digest_text(normalized) if normalized else "",
        "media_fingerprint": media_fingerprint_from_urls(imgs),
    }


def load_selected_groups(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [group for group in data if isinstance(group, dict)]
    for key in ("groups", "selected", "records"):
        value = data.get(key) if isinstance(data, dict) else None
        if isinstance(value, list):
            return [group for group in value if isinstance(group, dict)]
    return []


def enrich_ledger(ledger_path: Path, selected_path: Path | None, package_dirs: list[Path]) -> dict[str, object]:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    fingerprints_by_source: dict[str, dict[str, str]] = {}
    if selected_path:
        for group in load_selected_groups(selected_path):
            fingerprints = selected_group_fingerprints(group)
            source_id = fingerprints.get("source_goods_id")
            if source_id:
                fingerprints_by_source[source_id] = fingerprints
    for package_dir in package_dirs:
        fingerprints = package_fingerprints(package_dir)
        source_id = fingerprints.get("source_goods_id")
        if source_id:
            fingerprints_by_source.setdefault(source_id, {}).update({k: v for k, v in fingerprints.items() if v})

    for record in ledger.get("records", []):
        if not isinstance(record, dict):
            continue
        source_id = str(record.get("source_goods_id") or "")
        fingerprints = fingerprints_by_source.get(source_id)
        if not fingerprints:
            preview = str(record.get("title_preview") or "")
            normalized = normalize_source_copy(preview)
            if normalized:
                fingerprints = {
                    "business_dedupe_id": f"copy:{digest_text(normalized)}",
                    "normalized_copy_fingerprint": digest_text(normalized),
                }
        if fingerprints:
            for key, value in fingerprints.items():
                if key != "source_goods_id" and value:
                    record[key] = value
    ledger["dedupe_key"] = (
        "business_dedupe_id (normalized full source copy) first; "
        "source_goods_id second; media_fingerprint fallback"
    )
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ledger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--selected", type=Path)
    parser.add_argument("package_dirs", type=Path, nargs="*")
    args = parser.parse_args()
    ledger = enrich_ledger(args.ledger, args.selected, args.package_dirs)
    records = ledger.get("records", [])
    print(f"[ok] records={len(records) if isinstance(records, list) else 0} ledger={args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
