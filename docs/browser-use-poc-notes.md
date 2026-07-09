# Browser Use POC Notes

Date: 2026-07-09

Purpose: evaluate whether `browser-use/browser-use` should become a browser-control backend for the Goofish workflow.

## Setup

- Installed `browser-use==0.13.3` into local `.venv-browser-use/`.
- Install size: about 328 MB.
- System Python 3.9 is too old; the bundled Codex Python 3.12 works.
- No `BROWSER_USE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY` was present in the shell.
- CPA endpoint works with the local proxy key used by the existing publish script.

## Results

### Browser Harness / Direct CDP

Using an existing CDP Chrome endpoint:

```bash
BU_CDP_URL=http://127.0.0.1:9221 .venv-browser-use/bin/browser-use
```

worked for direct browser control.

Observed timings:

- `page_info()` through CDP: about 3.6s cold call.
- Open Goofish personal page and read first page state: about 3.6-7.0s.
- Detect account page after login: read `在售499 / 已售出164` and 20 initial item links.

This route is useful for other agents because it does not depend on Codex's Chrome extension. It does require a Chrome instance with CDP enabled or an explicit `BU_CDP_URL`.

### Normal Chrome Profile

Default local mode failed until Chrome remote debugging is enabled:

```text
chrome://inspect/#remote-debugging
tick "Allow remote debugging for this browser instance"
```

This means normal Chrome reuse is feasible but needs a one-time manual browser setting. For unattended use, a dedicated profile launched with `--remote-debugging-port` is cleaner.

### Browser Use Agent + LLM

Agent mode was tested with:

- `ChatOpenAI(model="claude-sonnet-4-6")`
- `base_url=http://100.84.194.46:8317/v1`
- `use_vision=False`
- `allowed_domains=["goofish.com", "*.goofish.com"]`

The small CPA test completed in about 2.4s and reported usage:

```json
{"prompt_tokens":307,"completion_tokens":5,"total_tokens":312}
```

The browser-use agent task then hit repeated CPA `502` errors and took about 117s before being interrupted. This makes LLM-agent mode unsuitable as the main deterministic collector.

## Risk Notes

- Direct CDP scripts only return the values we explicitly print, so data return is controllable.
- Agent mode sends page state, task instructions, and possibly screenshots/DOM summaries to the LLM provider. Keep it off for private/account-heavy pages unless the task really needs visual reasoning.
- Browser-use uses anonymized telemetry by default; disable it before production if required.
- Browser-use Cloud should not be used for Goofish account sessions unless there is an explicit decision to sync cookies to a remote browser.

## Recommendation

Use browser-use in two layers:

1. Browser harness direct-CDP backend for other agents that need a Codex-independent browser surface.
2. LLM agent mode only as a fallback for brittle UI flows, not for metrics collection.

Keep current deterministic scripts for:

- metrics collection,
- Feishu sync,
- dedupe,
- pricing,
- SKU/template logic.

For Goofish metrics, prefer clicking `在售N` before scrolling. A list-only harness confirmed `scripts/goofish-collect-v3.py` now loads exactly 499 onsale items for the current account without enumerating 164 sold items first.
