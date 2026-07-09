#!/usr/bin/env python3
"""Export Goofish IM conversations from a logged-in local Chrome profile.

This is intentionally separate from the item metrics collectors. It uses the
user-approved, already logged-in Chrome CDP port, opens a temporary /im tab,
clicks visible conversations, scrolls the message pane upward, and extracts
rendered message text from the DOM. It never sends messages or invokes known
read/clean/export platform actions directly, but opening conversations may
still mark them read in the web app.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import websockets


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "out"
GOOFISH_IM_URL = "https://www.goofish.com/im"


def port_for_account(account: str) -> int:
    m = re.search(r"(\d+)$", account)
    if not m:
        raise ValueError(f"cannot derive port from account slot: {account}")
    return 9220 + int(m.group(1))


def http_json(port: int, path: str) -> dict[str, Any]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=4) as r:
        return json.loads(r.read())


def digest(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:length]


def message_body_for_fingerprint(msg: dict[str, Any]) -> str:
    body = msg.get("raw") or msg.get("text") or ""
    return re.sub(r"\s+", "\n", body.strip())


def conversation_key_for(conv: dict[str, Any]) -> str:
    stable_parts = [
        "conversation-v2",
        conv.get("title") or "",
        *(conv.get("imageSrcs") or []),
    ]
    if any(str(part).strip() for part in stable_parts[1:]):
        return digest(json.dumps(stable_parts, ensure_ascii=False), length=16)
    return digest(conv.get("rawText") or json.dumps(conv, ensure_ascii=False), length=16)


def add_message_fingerprints(account: str, conversation_key: str, messages: list[dict[str, Any]]) -> None:
    duplicate_counts: dict[str, int] = {}
    for msg in messages:
        content_hash = digest(
            json.dumps(
                [
                    msg.get("role") or "",
                    msg.get("kind") or "",
                    message_body_for_fingerprint(msg),
                    msg.get("classHint") or "",
                ],
                ensure_ascii=False,
            ),
            length=32,
        )
        duplicate_counts[content_hash] = duplicate_counts.get(content_hash, 0) + 1
        duplicate_ordinal = duplicate_counts[content_hash]
        msg["contentHash"] = content_hash
        msg["duplicateOrdinal"] = duplicate_ordinal
        msg["messageFingerprint"] = digest(
            json.dumps([account, conversation_key, content_hash, duplicate_ordinal], ensure_ascii=False),
            length=32,
        )


def redact_text(text: str) -> str:
    text = re.sub(r"\b1[3-9]\d{9}\b", "[PHONE]", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", text)
    text = re.sub(r"\b\d{15,19}\b", "[LONG_NUMBER]", text)
    text = re.sub(r"\b\d{5,}\b", "[NUMBER]", text)
    return text


def redact_obj(obj: Any) -> Any:
    if isinstance(obj, str):
        return redact_text(obj)
    if isinstance(obj, list):
        return [redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    return obj


def progress(args: argparse.Namespace, msg: str) -> None:
    if getattr(args, "quiet", False):
        return
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def init_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sync_runs (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          account TEXT NOT NULL,
          port INTEGER NOT NULL,
          started_at TEXT NOT NULL,
          completed_at TEXT,
          json_path TEXT,
          jsonl_path TEXT,
          conversation_count INTEGER DEFAULT 0,
          message_count INTEGER DEFAULT 0,
          inserted_conversation_count INTEGER DEFAULT 0,
          inserted_message_count INTEGER DEFAULT 0,
          updated_message_count INTEGER DEFAULT 0,
          error_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS conversations (
          account TEXT NOT NULL,
          conversation_key TEXT NOT NULL,
          first_seen_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL,
          last_sync_run_id INTEGER,
          title TEXT,
          summary TEXT,
          raw_list_text TEXT,
          session_info_json TEXT,
          last_conversation_index INTEGER,
          PRIMARY KEY (account, conversation_key)
        );

        CREATE TABLE IF NOT EXISTS messages (
          account TEXT NOT NULL,
          conversation_key TEXT NOT NULL,
          message_fingerprint TEXT NOT NULL,
          first_seen_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL,
          last_sync_run_id INTEGER,
          message_index INTEGER,
          role TEXT,
          kind TEXT,
          text TEXT,
          raw TEXT,
          class_hint TEXT,
          content_hash TEXT,
          duplicate_ordinal INTEGER,
          PRIMARY KEY (account, conversation_key, message_fingerprint),
          FOREIGN KEY (account, conversation_key)
            REFERENCES conversations(account, conversation_key)
            ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_messages_account_conversation
          ON messages(account, conversation_key, message_index);

        CREATE INDEX IF NOT EXISTS idx_messages_content_hash
          ON messages(account, content_hash);

        CREATE TABLE IF NOT EXISTS conversation_scan_cursors (
          account TEXT PRIMARY KEY,
          updated_at TEXT NOT NULL,
          scroll_top REAL,
          scroll_height REAL,
          client_height REAL,
          last_conversation_key TEXT,
          scanned_conversation_count INTEGER DEFAULT 0,
          cursor_json TEXT
        );
        """
    )
    columns = {row[1] for row in conn.execute("PRAGMA table_info(conversations)").fetchall()}
    if "session_info_json" not in columns:
        conn.execute("ALTER TABLE conversations ADD COLUMN session_info_json TEXT")
    return conn


def latest_message_id_from_session_info(session_info: dict[str, Any]) -> str:
    token = str((session_info or {}).get("latestMessageToken") or "").strip()
    if token:
        return f"token:{token}"
    latest_message_id = str((session_info or {}).get("latestMessageId") or "").strip()
    if latest_message_id and latest_message_id not in {"[NUMBER]", "[LONG_NUMBER]"}:
        return f"token:{digest(latest_message_id, length=32)}"
    return latest_message_id


def session_info_with_tokens(session_info: dict[str, Any]) -> dict[str, Any]:
    stored = dict(session_info or {})
    latest_message_id = str(stored.get("latestMessageId") or "").strip()
    if latest_message_id:
        stored["latestMessageToken"] = digest(latest_message_id, length=32)
    return stored


def load_existing_conversation_state(db_path: Path, account: str) -> dict[str, str]:
    if not db_path.exists():
        return {}
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute(
                "SELECT conversation_key, session_info_json FROM conversations WHERE account=?",
                (account,),
            ).fetchall()
        except sqlite3.Error:
            rows = [(row[0], "{}") for row in conn.execute(
                "SELECT conversation_key FROM conversations WHERE account=?",
                (account,),
            ).fetchall()]
    except sqlite3.Error:
        return {}
    finally:
        if conn:
            conn.close()
    state: dict[str, str] = {}
    for key, raw_info in rows:
        try:
            info = json.loads(raw_info or "{}")
        except json.JSONDecodeError:
            info = {}
        state[str(key)] = latest_message_id_from_session_info(info)
    return state


def load_conversation_cursor(db_path: Path, account: str) -> dict[str, Any] | None:
    if not db_path.exists():
        return None
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(db_path)
        row = conn.execute(
            """
            SELECT cursor_json
            FROM conversation_scan_cursors
            WHERE account=?
            """,
            (account,),
        ).fetchone()
    except sqlite3.Error:
        return None
    finally:
        if conn:
            conn.close()
    if not row or not row[0]:
        return None
    try:
        cursor = json.loads(row[0])
    except json.JSONDecodeError:
        return None
    return cursor if isinstance(cursor, dict) else None


def write_sqlite(
    db_path: Path,
    payload: dict[str, Any],
    started_at: str,
    json_path: Path,
    jsonl_path: Path,
) -> dict[str, Any]:
    completed_at = datetime.now().isoformat()
    conn = init_db(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sync_runs (
              account, port, started_at, completed_at, json_path, jsonl_path,
              conversation_count, message_count, error_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["account"],
                payload["port"],
                started_at,
                completed_at,
                str(json_path),
                str(jsonl_path),
                payload["conversationCount"],
                payload["messageCount"],
                len(payload.get("errors") or []),
            ),
        )
        sync_run_id = int(cur.lastrowid)
        inserted_conversations = 0
        inserted_messages = 0
        updated_messages = 0

        for conv in payload.get("conversations") or []:
            cur.execute(
                """
                INSERT OR IGNORE INTO conversations (
                  account, conversation_key, first_seen_at, last_seen_at,
                  last_sync_run_id, title, summary, raw_list_text, session_info_json, last_conversation_index
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["account"],
                    conv["conversationKey"],
                    completed_at,
                    completed_at,
                    sync_run_id,
                    conv.get("title") or "",
                    conv.get("summary") or "",
                    conv.get("rawListText") or "",
                    json.dumps(conv.get("sessionInfo") or {}, ensure_ascii=False, sort_keys=True),
                    conv.get("conversationIndex"),
                ),
            )
            if cur.rowcount == 1:
                inserted_conversations += 1
            else:
                cur.execute(
                    """
                    UPDATE conversations
                    SET last_seen_at=?,
                        last_sync_run_id=?,
                        title=?,
                        summary=?,
                        raw_list_text=?,
                        session_info_json=?,
                        last_conversation_index=?
                    WHERE account=? AND conversation_key=?
                    """,
                    (
                        completed_at,
                        sync_run_id,
                        conv.get("title") or "",
                        conv.get("summary") or "",
                        conv.get("rawListText") or "",
                        json.dumps(conv.get("sessionInfo") or {}, ensure_ascii=False, sort_keys=True),
                        conv.get("conversationIndex"),
                        payload["account"],
                        conv["conversationKey"],
                    ),
                )

            for msg_index, msg in enumerate(conv.get("messages") or []):
                cur.execute(
                    """
                    INSERT OR IGNORE INTO messages (
                      account, conversation_key, message_fingerprint,
                      first_seen_at, last_seen_at, last_sync_run_id, message_index,
                      role, kind, text, raw, class_hint, content_hash, duplicate_ordinal
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["account"],
                        conv["conversationKey"],
                        msg["messageFingerprint"],
                        completed_at,
                        completed_at,
                        sync_run_id,
                        msg_index,
                        msg.get("role") or "",
                        msg.get("kind") or "",
                        msg.get("text") or "",
                        msg.get("raw") or "",
                        msg.get("classHint") or "",
                        msg.get("contentHash") or "",
                        msg.get("duplicateOrdinal"),
                    ),
                )
                if cur.rowcount == 1:
                    inserted_messages += 1
                else:
                    cur.execute(
                        """
                        UPDATE messages
                        SET last_seen_at=?,
                            last_sync_run_id=?,
                            message_index=?,
                            role=?,
                            kind=?,
                            text=?,
                            raw=?,
                            class_hint=?,
                            content_hash=?,
                            duplicate_ordinal=?
                        WHERE account=? AND conversation_key=? AND message_fingerprint=?
                        """,
                        (
                            completed_at,
                            sync_run_id,
                            msg_index,
                            msg.get("role") or "",
                            msg.get("kind") or "",
                            msg.get("text") or "",
                            msg.get("raw") or "",
                            msg.get("classHint") or "",
                            msg.get("contentHash") or "",
                            msg.get("duplicateOrdinal"),
                            payload["account"],
                            conv["conversationKey"],
                            msg["messageFingerprint"],
                        ),
                    )
                    updated_messages += 1

        cur.execute(
            """
            UPDATE sync_runs
            SET inserted_conversation_count=?,
                inserted_message_count=?,
                updated_message_count=?
            WHERE id=?
            """,
            (inserted_conversations, inserted_messages, updated_messages, sync_run_id),
        )
        cursor_payload = payload.get("conversationCursor")
        if cursor_payload:
            holder = cursor_payload.get("holder") or {}
            cur.execute(
                """
                INSERT INTO conversation_scan_cursors (
                  account, updated_at, scroll_top, scroll_height, client_height,
                  last_conversation_key, scanned_conversation_count, cursor_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account) DO UPDATE SET
                  updated_at=excluded.updated_at,
                  scroll_top=excluded.scroll_top,
                  scroll_height=excluded.scroll_height,
                  client_height=excluded.client_height,
                  last_conversation_key=excluded.last_conversation_key,
                  scanned_conversation_count=excluded.scanned_conversation_count,
                  cursor_json=excluded.cursor_json
                """,
                (
                    payload["account"],
                    completed_at,
                    holder.get("scrollTop"),
                    holder.get("scrollHeight"),
                    holder.get("clientHeight"),
                    cursor_payload.get("lastConversationKey") or "",
                    cursor_payload.get("scannedConversationCount") or 0,
                    json.dumps(cursor_payload, ensure_ascii=False, sort_keys=True),
                ),
            )
        conn.commit()
        totals = conn.execute(
            """
            SELECT
              (SELECT count(*) FROM conversations WHERE account=?),
              (SELECT count(*) FROM messages WHERE account=?)
            """,
            (payload["account"], payload["account"]),
        ).fetchone()
        return {
            "db": str(db_path),
            "syncRunId": sync_run_id,
            "insertedConversationCount": inserted_conversations,
            "insertedMessageCount": inserted_messages,
            "updatedMessageCount": updated_messages,
            "totalConversationCount": int(totals[0]),
            "totalMessageCount": int(totals[1]),
        }
    finally:
        conn.close()


class SQLiteRunWriter:
    def __init__(
        self,
        db_path: Path,
        account: str,
        port: int,
        started_at: str,
        json_path: Path,
        jsonl_path: Path,
    ) -> None:
        self.db_path = db_path
        self.account = account
        self.conn = init_db(db_path)
        self.inserted_conversations = 0
        self.inserted_messages = 0
        self.updated_messages = 0
        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            INSERT INTO sync_runs (
              account, port, started_at, json_path, jsonl_path,
              conversation_count, message_count, error_count
            )
            VALUES (?, ?, ?, ?, ?, 0, 0, 0)
            """,
            (account, port, started_at, str(json_path), str(jsonl_path)),
        )
        self.sync_run_id = int(self.cur.lastrowid)
        self.conn.commit()

    def _refresh_run_counts(
        self,
        conversation_count: int | None = None,
        message_count: int | None = None,
        error_count: int | None = None,
        completed_at: str | None = None,
    ) -> None:
        fields = [
            "inserted_conversation_count=?",
            "inserted_message_count=?",
            "updated_message_count=?",
        ]
        values: list[Any] = [
            self.inserted_conversations,
            self.inserted_messages,
            self.updated_messages,
        ]
        if conversation_count is not None:
            fields.append("conversation_count=?")
            values.append(conversation_count)
        if message_count is not None:
            fields.append("message_count=?")
            values.append(message_count)
        if error_count is not None:
            fields.append("error_count=?")
            values.append(error_count)
        if completed_at is not None:
            fields.append("completed_at=?")
            values.append(completed_at)
        values.append(self.sync_run_id)
        self.conn.execute(
            f"UPDATE sync_runs SET {', '.join(fields)} WHERE id=?",
            values,
        )

    def save_cursor(self, cursor_payload: dict[str, Any] | None) -> None:
        if not cursor_payload:
            return
        completed_at = datetime.now().isoformat()
        holder = cursor_payload.get("holder") or {}
        self.conn.execute(
            """
            INSERT INTO conversation_scan_cursors (
              account, updated_at, scroll_top, scroll_height, client_height,
              last_conversation_key, scanned_conversation_count, cursor_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(account) DO UPDATE SET
              updated_at=excluded.updated_at,
              scroll_top=excluded.scroll_top,
              scroll_height=excluded.scroll_height,
              client_height=excluded.client_height,
              last_conversation_key=excluded.last_conversation_key,
              scanned_conversation_count=excluded.scanned_conversation_count,
              cursor_json=excluded.cursor_json
            """,
            (
                self.account,
                completed_at,
                holder.get("scrollTop"),
                holder.get("scrollHeight"),
                holder.get("clientHeight"),
                cursor_payload.get("lastConversationKey") or "",
                cursor_payload.get("scannedConversationCount") or 0,
                json.dumps(cursor_payload, ensure_ascii=False, sort_keys=True),
            ),
        )
        self.conn.commit()

    def upsert_conversation(self, conv: dict[str, Any]) -> dict[str, int | bool]:
        completed_at = datetime.now().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO conversations (
              account, conversation_key, first_seen_at, last_seen_at,
              last_sync_run_id, title, summary, raw_list_text, session_info_json, last_conversation_index
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.account,
                conv["conversationKey"],
                completed_at,
                completed_at,
                self.sync_run_id,
                conv.get("title") or "",
                conv.get("summary") or "",
                conv.get("rawListText") or "",
                json.dumps(conv.get("sessionInfo") or {}, ensure_ascii=False, sort_keys=True),
                conv.get("conversationIndex"),
            ),
        )
        inserted_conversation = cur.rowcount == 1
        if inserted_conversation:
            self.inserted_conversations += 1
        else:
            cur.execute(
                """
                UPDATE conversations
                SET last_seen_at=?,
                    last_sync_run_id=?,
                    title=?,
                    summary=?,
                    raw_list_text=?,
                    session_info_json=?,
                    last_conversation_index=?
                WHERE account=? AND conversation_key=?
                """,
                (
                    completed_at,
                    self.sync_run_id,
                    conv.get("title") or "",
                    conv.get("summary") or "",
                    conv.get("rawListText") or "",
                    json.dumps(conv.get("sessionInfo") or {}, ensure_ascii=False, sort_keys=True),
                    conv.get("conversationIndex"),
                    self.account,
                    conv["conversationKey"],
                ),
            )

        inserted_messages = 0
        updated_messages = 0
        for msg_index, msg in enumerate(conv.get("messages") or []):
            cur.execute(
                """
                INSERT OR IGNORE INTO messages (
                  account, conversation_key, message_fingerprint,
                  first_seen_at, last_seen_at, last_sync_run_id, message_index,
                  role, kind, text, raw, class_hint, content_hash, duplicate_ordinal
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.account,
                    conv["conversationKey"],
                    msg["messageFingerprint"],
                    completed_at,
                    completed_at,
                    self.sync_run_id,
                    msg_index,
                    msg.get("role") or "",
                    msg.get("kind") or "",
                    msg.get("text") or "",
                    msg.get("raw") or "",
                    msg.get("classHint") or "",
                    msg.get("contentHash") or "",
                    msg.get("duplicateOrdinal"),
                ),
            )
            if cur.rowcount == 1:
                inserted_messages += 1
                self.inserted_messages += 1
            else:
                cur.execute(
                    """
                    UPDATE messages
                    SET last_seen_at=?,
                        last_sync_run_id=?,
                        message_index=?,
                        role=?,
                        kind=?,
                        text=?,
                        raw=?,
                        class_hint=?,
                        content_hash=?,
                        duplicate_ordinal=?
                    WHERE account=? AND conversation_key=? AND message_fingerprint=?
                    """,
                    (
                        completed_at,
                        self.sync_run_id,
                        msg_index,
                        msg.get("role") or "",
                        msg.get("kind") or "",
                        msg.get("text") or "",
                        msg.get("raw") or "",
                        msg.get("classHint") or "",
                        msg.get("contentHash") or "",
                        msg.get("duplicateOrdinal"),
                        self.account,
                        conv["conversationKey"],
                        msg["messageFingerprint"],
                    ),
                )
                updated_messages += 1
                self.updated_messages += 1

        self._refresh_run_counts()
        self.conn.commit()
        return {
            "insertedConversation": inserted_conversation,
            "insertedMessages": inserted_messages,
            "updatedMessages": updated_messages,
        }

    def finish(
        self,
        conversation_count: int,
        message_count: int,
        error_count: int,
        cursor_payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if cursor_payload:
            self.save_cursor(cursor_payload)
        self._refresh_run_counts(
            conversation_count=conversation_count,
            message_count=message_count,
            error_count=error_count,
            completed_at=datetime.now().isoformat(),
        )
        self.conn.commit()
        totals = self.conn.execute(
            """
            SELECT
              (SELECT count(*) FROM conversations WHERE account=?),
              (SELECT count(*) FROM messages WHERE account=?)
            """,
            (self.account, self.account),
        ).fetchone()
        return {
            "db": str(self.db_path),
            "syncRunId": self.sync_run_id,
            "insertedConversationCount": self.inserted_conversations,
            "insertedMessageCount": self.inserted_messages,
            "updatedMessageCount": self.updated_messages,
            "totalConversationCount": int(totals[0]),
            "totalMessageCount": int(totals[1]),
        }

    def close(self) -> None:
        self.conn.close()


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

    async def cmd(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        session_id: str | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        if not self.ws:
            raise RuntimeError("CDP websocket is not connected")
        self._id += 1
        mid = self._id
        msg: dict[str, Any] = {"id": mid, "method": method, "params": params or {}}
        if session_id:
            msg["sessionId"] = session_id
        await self.ws.send(json.dumps(msg))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            data = json.loads(raw)
            if data.get("id") == mid:
                if "error" in data:
                    raise RuntimeError(f"CDP {method} failed: {data['error']}")
                return data


async def page_eval(cdp: CDP, session_id: str, expression: str, timeout: int = 30) -> Any:
    result = await cdp.cmd(
        "Runtime.evaluate",
        {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
        },
        session_id,
        timeout=timeout,
    )
    remote = result.get("result", {}).get("result", {})
    if "exceptionDetails" in result.get("result", {}):
        raise RuntimeError(f"page evaluation failed: {result['result']['exceptionDetails']}")
    return remote.get("value")


VISIBLE_CONVERSATIONS_JS = r"""
(() => {
  const getFiber = el => {
    const key = el && Object.keys(el).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactInternalInstance$'));
    return key ? el[key] : null;
  };
  const pickSessionInfo = obj => {
    if (!obj || typeof obj !== 'object') return null;
    const seen = new Set();
    const queue = [obj];
    while (queue.length && seen.size < 1200) {
      const cur = queue.shift();
      if (!cur || typeof cur !== 'object' || seen.has(cur)) continue;
      seen.add(cur);
      if (cur.sessionId && (cur.summary || cur.itemInfo || cur.userInfo || cur.lastMessage)) {
        return cur;
      }
      for (const key of Object.keys(cur).slice(0, 80)) {
        const value = cur[key];
        if (value && typeof value === 'object') queue.push(value);
      }
    }
    return null;
  };
  const sessionInfoFor = el => {
    let fiber = getFiber(el);
    for (let depth = 0; fiber && depth < 12; depth++, fiber = fiber.return) {
      const found = pickSessionInfo(fiber.memoizedProps) || pickSessionInfo(fiber.pendingProps) || pickSessionInfo(fiber.memoizedState);
      if (found) {
        const extension = found.extension || {};
        const latest = (found.summary && found.summary.latestMessage) || {};
        const itemInfo = found.itemInfo || {};
        const userInfo = found.userInfo || {};
        const ownerInfo = found.ownerInfo || {};
        return {
          sessionId: String(found.sessionId || ''),
          sessionType: String(found.sessionType || ''),
          parentSessionId: String(found.parentSessionId || ''),
          itemId: String(itemInfo.itemId || extension.itemId || ''),
          orderId: String(extension.orderId || ''),
          userId: String(userInfo.userId || ownerInfo.userId || ''),
          latestMessageId: String(latest.messageId || '')
        };
      }
    }
    return {};
  };
  const items = [...document.querySelectorAll('[class*=conversation-item]')];
  return items.map((el, visibleIndex) => {
    const rawText = (el.innerText || '').trim().replace(/\s+/g, '\n');
    const titleEl = el.querySelector('[class*=title]');
    const summaryEl = el.querySelector('[class*=summary]');
    const rect = el.getBoundingClientRect();
    return {
      visibleIndex,
      rawText,
      isNotification: /通知消息|通知中心|系统通知/.test(rawText),
      title: titleEl ? titleEl.innerText.trim() : '',
      summary: summaryEl ? summaryEl.innerText.trim() : '',
      imageSrcs: [...el.querySelectorAll('img')].map(img => img.src || '').filter(Boolean),
      sessionInfo: sessionInfoFor(el),
      top: Math.round(rect.top),
      height: Math.round(rect.height)
    };
  }).filter(x => x.rawText);
})()
"""


MESSAGE_SNAPSHOT_JS = r"""
(() => {
  const main = document.querySelector('main[class*=chat-main]') || document.querySelector('main');
  const target = document.querySelector('#message-list-scrollable')
    || [...(main || document).querySelectorAll('*')]
      .filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 100)
      .sort((a, b) => (b.scrollHeight - b.clientHeight) - (a.scrollHeight - a.clientHeight))[0]
    || null;
  const list = main ? main.querySelector('.ant-list-items') : document.querySelector('.ant-list-items');
  const items = list ? [...list.querySelectorAll('li.ant-list-item')] : [];
  const rows = items.map((li, index) => {
    const row = li.querySelector('[class*=message-row]');
    const textEl = li.querySelector('[class*=message-text], [class*=msg-dx-content], [class*=msg-text-card], [class*=transaction-card], [class*=voice-container], [class*=image-container], [class*=video-container]');
    const raw = (li.innerText || '').trim().replace(/\s+\n/g, '\n').replace(/\n\s+/g, '\n');
    const text = textEl ? (textEl.innerText || '').trim() : raw;
    const cls = [
      row && row.className || '',
      textEl && textEl.className || ''
    ].join(' ');
    let role = 'system';
    if (/right|mine/i.test(cls)) role = 'seller';
    else if (/left|other/i.test(cls)) role = 'customer';
    else if (row) {
      const r = row.getBoundingClientRect();
      const m = (main || document.body).getBoundingClientRect();
      role = r.left > m.left + m.width / 2 ? 'seller' : 'customer';
    }
    let kind = 'text';
    if (/image/i.test(cls)) kind = 'image';
    if (/voice/i.test(cls)) kind = 'voice';
    if (/video/i.test(cls)) kind = 'video';
    if (/card|transaction|dx-content/i.test(cls)) kind = 'card';
    const rect = li.getBoundingClientRect();
    return { index, role, kind, text, raw, top: Math.round(rect.top), classHint: cls.split(/\s+/).filter(Boolean).slice(0, 4).join(' ') };
  }).filter(x => x.text || x.raw);
  const scrollers = [...document.querySelectorAll('main[class*=chat-main] *')]
    .filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 100)
    .map((el, i) => {
      const r = el.getBoundingClientRect();
      return { i, className: String(el.className || ''), scrollTop: el.scrollTop, scrollHeight: el.scrollHeight, clientHeight: el.clientHeight, rect: [r.left, r.top, r.width, r.height].map(Math.round) };
    });
  const targetClass = target ? String(target.className || '') : '';
  const isReverse = /reverse/i.test(targetClass);
  const minScrollTop = target ? Math.min(0, target.clientHeight - target.scrollHeight) : 0;
  const reachedOlderBoundary = target ? (isReverse ? target.scrollTop <= minScrollTop + 2 : target.scrollTop <= 2) : null;
  const targetInfo = target ? {
    ok: true,
    id: target.id || '',
    className: targetClass,
    isReverse,
    scrollTop: target.scrollTop,
    scrollHeight: target.scrollHeight,
    clientHeight: target.clientHeight,
    minScrollTop,
    reachedOlderBoundary
  } : { ok: false };
  return { rows, scrollers, target: targetInfo };
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
  const targetClass = String(target.className || '');
  const isReverse = /reverse/i.test(targetClass);
  const minScrollTop = Math.min(0, target.clientHeight - target.scrollHeight);
  const reachedOlderBoundary = isReverse ? target.scrollTop <= minScrollTop + 2 : target.scrollTop <= 2;
  return {
    ok: true,
    id: target.id || '',
    className: targetClass,
    isReverse,
    x,
    y,
    scrollTop: target.scrollTop,
    scrollHeight: target.scrollHeight,
    clientHeight: target.clientHeight,
    minScrollTop,
    reachedOlderBoundary
  };
})()
"""


SCROLL_CONVERSATIONS_JS = r"""
(() => {
  const holder = document.querySelector('.rc-virtual-list-holder')
    || [...document.querySelectorAll('*')].find(el => el.scrollHeight > el.clientHeight && /conversation|virtual-list/i.test(String(el.className || '')));
  if (!holder) return { ok: false };
  const before = holder.scrollTop;
  holder.scrollTop = Math.min(holder.scrollHeight, before + Math.max(300, holder.clientHeight - 80));
  holder.dispatchEvent(new Event('scroll', { bubbles: true }));
  return { ok: true, before, after: holder.scrollTop, scrollHeight: holder.scrollHeight, clientHeight: holder.clientHeight };
})()
"""


CONVERSATION_HOLDER_STATE_JS = r"""
(() => {
  const holder = document.querySelector('.rc-virtual-list-holder')
    || [...document.querySelectorAll('*')].find(el => el.scrollHeight > el.clientHeight && /conversation|virtual-list/i.test(String(el.className || '')));
  if (!holder) return { ok: false };
  return {
    ok: true,
    scrollTop: holder.scrollTop,
    scrollHeight: holder.scrollHeight,
    clientHeight: holder.clientHeight,
    atBottom: Math.ceil(holder.scrollTop + holder.clientHeight) >= holder.scrollHeight - 2
  };
})()
"""


def set_conversation_scroll_js(scroll_top: float) -> str:
    return f"""
(() => {{
  const holder = document.querySelector('.rc-virtual-list-holder')
    || [...document.querySelectorAll('*')].find(el => el.scrollHeight > el.clientHeight && /conversation|virtual-list/i.test(String(el.className || '')));
  if (!holder) return {{ ok: false }};
  const before = holder.scrollTop;
  holder.scrollTop = Math.max(0, Math.min(holder.scrollHeight, {float(scroll_top)}));
  holder.dispatchEvent(new Event('scroll', {{ bubbles: true }}));
  return {{
    ok: true,
    before,
    after: holder.scrollTop,
    scrollHeight: holder.scrollHeight,
    clientHeight: holder.clientHeight
  }};
}})()
"""


async def dispatch_message_wheel(cdp: CDP, session_id: str, delta_y: float) -> dict[str, Any]:
    target = await page_eval(cdp, session_id, MESSAGE_TARGET_JS, timeout=60)
    if not target or not target.get("ok"):
        return {"ok": False, "target": target}
    await cdp.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseMoved", "x": float(target["x"]), "y": float(target["y"]), "button": "none"},
        session_id,
        timeout=60,
    )
    await cdp.cmd(
        "Input.dispatchMouseEvent",
        {"type": "mouseWheel", "x": float(target["x"]), "y": float(target["y"]), "deltaX": 0, "deltaY": delta_y},
        session_id,
        timeout=60,
    )
    return {"ok": True, "targetBeforeWheel": target, "deltaY": delta_y}


async def collect_messages(cdp: CDP, session_id: str, max_scrolls: int, wait_s: float, wheel_delta_y: float) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    first_seen_order: dict[str, int] = {}
    stable = 0
    reached_older_boundary = False
    for step in range(max_scrolls + 1):
        snap = await page_eval(cdp, session_id, MESSAGE_SNAPSHOT_JS, timeout=60)
        target = (snap or {}).get("target") or {}
        if target.get("reachedOlderBoundary"):
            reached_older_boundary = True
        before_count = len(seen)
        for row in (snap or {}).get("rows", []):
            key = digest(json.dumps([row.get("role"), row.get("kind"), row.get("text"), row.get("raw")], ensure_ascii=False))
            if key not in seen:
                first_seen_order[key] = step
                seen[key] = row
        new_count = len(seen) - before_count
        if reached_older_boundary and step > 0 and new_count == 0:
            break
        scroll = await dispatch_message_wheel(cdp, session_id, wheel_delta_y)
        await asyncio.sleep(wait_s)
        after = await page_eval(cdp, session_id, MESSAGE_TARGET_JS, timeout=60)
        if after and after.get("reachedOlderBoundary"):
            reached_older_boundary = True
        before_target = (scroll or {}).get("targetBeforeWheel") or {}
        if new_count == 0 and (not scroll or not scroll.get("ok") or (after and before_target.get("scrollTop") == after.get("scrollTop"))):
            stable += 1
        else:
            stable = 0
        if stable >= 5:
            break
    rows = list(seen.values())
    rows.sort(key=lambda x: (first_seen_order.get(digest(json.dumps([x.get("role"), x.get("kind"), x.get("text"), x.get("raw")], ensure_ascii=False)), 0), x.get("top", 0), x.get("index", 0)))
    return rows


async def conversation_holder_state(cdp: CDP, session_id: str) -> dict[str, Any]:
    state = await page_eval(cdp, session_id, CONVERSATION_HOLDER_STATE_JS)
    return state if isinstance(state, dict) else {"ok": False}


async def restore_conversation_cursor(
    cdp: CDP,
    session_id: str,
    cursor: dict[str, Any] | None,
    max_scrolls: int,
    wait_s: float,
) -> dict[str, Any]:
    if not cursor:
        return {"attempted": False, "reason": "no-cursor"}
    holder = cursor.get("holder") or {}
    scroll_top = holder.get("scrollTop")
    if scroll_top is None:
        return {"attempted": False, "reason": "cursor-has-no-scroll-top"}

    set_result = await page_eval(cdp, session_id, set_conversation_scroll_js(float(scroll_top)))
    await asyncio.sleep(wait_s)
    target_key = str(cursor.get("lastConversationKey") or "")
    matched = False
    visible_keys: list[str] = []

    for attempt in range(max_scrolls + 1):
        visible = await page_eval(cdp, session_id, VISIBLE_CONVERSATIONS_JS)
        visible_keys = [conversation_key_for(conv) for conv in (visible or []) if not conv.get("isNotification")]
        if target_key and target_key in visible_keys:
            matched = True
            break
        if attempt >= max_scrolls:
            break
        scroll = await page_eval(cdp, session_id, SCROLL_CONVERSATIONS_JS)
        if not scroll or not scroll.get("ok") or scroll.get("before") == scroll.get("after"):
            break
        await asyncio.sleep(wait_s)

    return {
        "attempted": True,
        "matchedLastConversation": matched,
        "lastConversationKey": target_key,
        "setResult": set_result,
        "holder": await conversation_holder_state(cdp, session_id),
        "visibleConversationKeys": visible_keys[:12],
    }


async def run(args: argparse.Namespace) -> dict[str, Any]:
    account = args.account
    port = args.port or port_for_account(account)
    started_at = datetime.now().isoformat()
    version = http_json(port, "/json/version")
    browser_ws = version["webSocketDebuggerUrl"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = OUT_DIR / f"goofish-im-{account}-{stamp}"
    json_path = base.with_suffix(".json")
    jsonl_path = base.with_suffix(".jsonl")
    db_path = Path(args.db_path)
    existing_conversation_state = (
        {} if args.no_db or args.force_resync_existing else load_existing_conversation_state(db_path, account)
    )
    saved_conversation_cursor = None if args.no_db else load_conversation_cursor(db_path, account)
    db_writer = None if args.no_db else SQLiteRunWriter(db_path, account, port, started_at, json_path, jsonl_path)

    conversations: list[dict[str, Any]] = []
    flat_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    skipped_existing: list[dict[str, Any]] = []
    scanned_conversation_count = 0
    conversation_cursor: dict[str, Any] | None = None
    cursor_restore_result: dict[str, Any] | None = None
    progress_every = max(1, args.progress_every)
    progress(
        args,
        f"start account={account} port={port} max_conversations={args.max_conversations} "
        f"resume={bool(args.resume_conversation_cursor)} db={'off' if args.no_db else db_path}",
    )

    async with CDP(browser_ws) as cdp:
        target = (await cdp.cmd("Target.createTarget", {"url": GOOFISH_IM_URL}))["result"]["targetId"]
        attached = await cdp.cmd("Target.attachToTarget", {"targetId": target, "flatten": True})
        session_id = attached["result"]["sessionId"]
        await cdp.cmd("Page.enable", {}, session_id)
        await cdp.cmd("Runtime.enable", {}, session_id)
        await asyncio.sleep(args.initial_wait)

        page_state = await page_eval(
            cdp,
            session_id,
            "(() => ({url: location.href, title: document.title, bodyChars: document.body ? document.body.innerText.length : 0}))()",
        )
        if not page_state or "聊天" not in page_state.get("title", ""):
            raise RuntimeError(f"unexpected IM page state: {page_state}")

        if args.resume_conversation_cursor:
            cursor_restore_result = await restore_conversation_cursor(
                cdp,
                session_id,
                saved_conversation_cursor,
                args.cursor_restore_scrolls,
                args.after_scroll_wait,
            )
            progress(
                args,
                "cursor restore attempted="
                f"{cursor_restore_result.get('attempted')} matched="
                f"{cursor_restore_result.get('matchedLastConversation')}",
            )

        seen_conversations: set[str] = set()
        stagnant_scrolls = 0
        for _page in range(args.max_conversation_scrolls + 1):
            visible = await page_eval(cdp, session_id, VISIBLE_CONVERSATIONS_JS)
            holder_state = await conversation_holder_state(cdp, session_id)
            for conv in visible or []:
                if conv.get("isNotification"):
                    continue
                conv_key = conversation_key_for(conv)
                if conv_key in seen_conversations:
                    continue
                if len(conversations) >= args.max_conversations:
                    break
                seen_conversations.add(conv_key)
                scanned_conversation_count += 1
                conversation_cursor = {
                    "schema": "goofish-im-conversation-cursor/v1",
                    "account": account,
                    "updatedAt": datetime.now().isoformat(),
                    "lastConversationKey": conv_key,
                    "scannedConversationCount": scanned_conversation_count,
                    "holder": holder_state,
                    "restore": cursor_restore_result,
                }
                latest_message_id = latest_message_id_from_session_info(conv.get("sessionInfo") or {})
                existing_latest_message_id = existing_conversation_state.get(conv_key)
                if existing_latest_message_id is not None and (
                    not existing_latest_message_id
                    or (latest_message_id and latest_message_id == existing_latest_message_id)
                ):
                    skipped_existing.append(
                        {
                            "conversationKey": conv_key,
                            "reason": "already-in-db" if not existing_latest_message_id else "latest-message-unchanged",
                        }
                    )
                    if db_writer:
                        db_writer.save_cursor(redact_obj(conversation_cursor) if not args.no_redact else conversation_cursor)
                    if len(skipped_existing) == 1 or len(skipped_existing) % progress_every == 0:
                        progress(
                            args,
                            f"skip scanned={scanned_conversation_count} skipped={len(skipped_existing)} "
                            f"processed={len(conversations)} key={conv_key[:8]}",
                        )
                    continue
                visible_index = conv["visibleIndex"]
                clicked = await page_eval(
                    cdp,
                    session_id,
                    f"""(() => {{
                      const items = [...document.querySelectorAll('[class*=conversation-item]')];
                      const item = items[{visible_index}];
                      if (!item) return false;
                      item.scrollIntoView({{block:'nearest'}});
                      item.dispatchEvent(new MouseEvent('mouseover', {{bubbles:true}}));
                      item.click();
                      return true;
                    }})()""",
                )
                if not clicked:
                    errors.append({"conversationKey": conv_key, "error": "click failed"})
                    progress(args, f"error click-failed scanned={scanned_conversation_count} key={conv_key[:8]}")
                    continue
                await asyncio.sleep(args.after_click_wait)
                try:
                    messages = await collect_messages(
                        cdp,
                        session_id,
                        args.max_message_scrolls,
                        args.after_message_scroll_wait,
                        args.message_wheel_delta_y,
                    )
                except Exception as exc:  # keep going; one bad conversation should not lose the batch
                    errors.append({"conversationKey": conv_key, "error": repr(exc)})
                    messages = []
                record = {
                    "conversationKey": conv_key,
                    "conversationIndex": len(conversations),
                    "title": conv.get("title") or "",
                    "summary": conv.get("summary") or "",
                    "rawListText": conv.get("rawText") or "",
                    "sessionInfo": session_info_with_tokens(conv.get("sessionInfo") or {}),
                    "messageCount": len(messages),
                    "messages": messages,
                }
                add_message_fingerprints(account, conv_key, messages)
                conversations.append(record)
                db_write = None
                if db_writer:
                    db_record = redact_obj(record) if not args.no_redact else record
                    db_write = db_writer.upsert_conversation(db_record)
                    db_writer.save_cursor(redact_obj(conversation_cursor) if not args.no_redact else conversation_cursor)
                for msg_index, msg in enumerate(messages):
                    flat_rows.append(
                        {
                            "conversationKey": conv_key,
                            "conversationIndex": record["conversationIndex"],
                            "messageIndex": msg_index,
                            "messageFingerprint": msg.get("messageFingerprint"),
                            "role": msg.get("role"),
                            "kind": msg.get("kind"),
                            "text": msg.get("text") or msg.get("raw") or "",
                        }
                    )
                if len(conversations) == 1 or len(conversations) % progress_every == 0:
                    if db_write:
                        write_bits = (
                            f" insertedConv={int(bool(db_write['insertedConversation']))}"
                            f" insertedMsg={db_write['insertedMessages']}"
                            f" updatedMsg={db_write['updatedMessages']}"
                        )
                    else:
                        write_bits = ""
                    progress(
                        args,
                        f"processed={len(conversations)}/{args.max_conversations} "
                        f"scanned={scanned_conversation_count} skipped={len(skipped_existing)} "
                        f"messages={len(flat_rows)} errors={len(errors)} key={conv_key[:8]}{write_bits}",
                    )
            if len(conversations) >= args.max_conversations:
                break
            scroll = await page_eval(cdp, session_id, SCROLL_CONVERSATIONS_JS)
            await asyncio.sleep(args.after_scroll_wait)
            if not scroll or not scroll.get("ok") or scroll.get("before") == scroll.get("after"):
                stagnant_scrolls += 1
            else:
                stagnant_scrolls = 0
            if stagnant_scrolls >= 2:
                break

        try:
            await cdp.cmd("Target.closeTarget", {"targetId": target})
        except Exception:
            pass

    payload = {
        "schema": "goofish-im-export/v1",
        "account": account,
        "port": port,
        "collectedAt": datetime.now().isoformat(),
        "notes": [
            "Collected from a temporary logged-in /im tab via rendered DOM.",
            "Opening conversations in the web UI may mark them read.",
            "No messages were sent by this script.",
        ],
        "redacted": not args.no_redact,
        "conversationCursor": conversation_cursor,
        "scannedConversationCount": scanned_conversation_count,
        "skippedExistingConversationCount": len(skipped_existing),
        "skippedExistingConversations": skipped_existing,
        "conversationCount": len(conversations),
        "messageCount": len(flat_rows),
        "errors": errors,
        "conversations": conversations,
    }
    db_payload = payload
    if not args.no_redact:
        payload = redact_obj(payload)
        flat_rows = redact_obj(flat_rows)
        db_payload = payload

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in flat_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    db_result = None
    if db_writer:
        db_result = db_writer.finish(
            conversation_count=db_payload["conversationCount"],
            message_count=db_payload["messageCount"],
            error_count=len(db_payload.get("errors") or []),
            cursor_payload=db_payload.get("conversationCursor"),
        )
        db_writer.close()

    result = {
        "json": str(json_path),
        "jsonl": str(jsonl_path),
        "scannedConversationCount": scanned_conversation_count,
        "skippedExistingConversationCount": len(skipped_existing),
        "conversationCount": len(conversations),
        "messageCount": len(flat_rows),
        "errorCount": len(errors),
        "conversationCursorSaved": bool(conversation_cursor),
        "conversationCursorRestored": bool(cursor_restore_result and cursor_restore_result.get("attempted")),
    }
    if db_result:
        result.update(db_result)
    return result


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Export Goofish IM conversation text from a logged-in local Chrome.")
    ap.add_argument("--account", default="account-01")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--max-conversations", type=int, default=50)
    ap.add_argument("--max-conversation-scrolls", type=int, default=12)
    ap.add_argument("--max-message-scrolls", type=int, default=12)
    ap.add_argument("--initial-wait", type=float, default=14)
    ap.add_argument("--after-click-wait", type=float, default=3)
    ap.add_argument("--after-scroll-wait", type=float, default=1.5)
    ap.add_argument("--after-message-scroll-wait", type=float, default=1.2)
    ap.add_argument("--message-wheel-delta-y", type=float, default=-900)
    ap.add_argument("--db-path", default=str(OUT_DIR / "goofish-im.sqlite"))
    ap.add_argument("--no-db", action="store_true", help="Skip SQLite upsert.")
    ap.add_argument("--force-resync-existing", action="store_true", help="Deep-crawl conversations even when their latest message id is unchanged in SQLite.")
    ap.add_argument("--resume-conversation-cursor", action="store_true", help="Start the left conversation list near the last saved scan cursor instead of the top.")
    ap.add_argument("--cursor-restore-scrolls", type=int, default=4, help="Extra left-list scroll attempts while trying to make the saved cursor anchor visible.")
    ap.add_argument("--progress-every", type=int, default=10, help="Print a redacted progress line every N processed or skipped conversations.")
    ap.add_argument("--quiet", action="store_true", help="Suppress progress logs on stderr; stdout remains the final JSON result.")
    ap.add_argument("--no-redact", action="store_true", help="Keep raw phone/email/long-number patterns in exported text.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = asyncio.run(run(args))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
