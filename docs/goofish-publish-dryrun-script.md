# Goofish publish dry-run script

Purpose: prepare a Xianyu/Goofish publish draft from a local SZWego item package,
then stop before the final publish click.

The script is intentionally conservative:

- uploads at most 9 images, because Goofish accepts 9 item images;
- never clicks the final `发布` button;
- uses the existing logged-in Chrome session on this Mac;
- does not read or store cookies, tokens, orders, chats, or account secrets.

## Script

```bash
python3 scripts/goofish-publish-dryrun-macos.py --self-test
python3 scripts/goofish-publish-dryrun-macos.py --plan-json <package_dir>
python3 scripts/goofish-publish-dryrun-macos.py --doctor <package_dir>
python3 scripts/goofish-publish-dryrun-macos.py --write-summary out/goofish-publish-dryrun-summary.json <package_dir>
```

Current tested package:

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-items/shop__ZrYrYa-ptceiM4RqMj2tq8dibOVy7cWY/album__dKUrYqk-vbT7KijIbbG-20JG-TIVIk5CwTKDlgw/item__dt4rYmTugdEsiE6CRRPDZ072QnUFMdAppMPQjbA
```

## Chrome prerequisite

For low-token automation, Chrome must allow page JavaScript from Apple Events.
This lets the script fill text, locate upload controls, and verify upload counts
without repeatedly dumping the full screen state. The upload button itself is
clicked through a real macOS coordinate click so Chrome opens the native file
picker.

Enable it once in Chrome:

```text
View > Developer > Allow JavaScript from Apple Events
```

In Chinese Chrome this is usually:

```text
显示 > 开发者 > 允许 Apple 事件中的 JavaScript
```

Then run:

```bash
python3 scripts/goofish-publish-dryrun-macos.py --doctor <package_dir>
```

The doctor command should report `chrome_js returned title=...`.

You can also ask the script to click that Chrome menu item explicitly:

```bash
python3 scripts/goofish-publish-dryrun-macos.py --enable-chrome-js-menu --doctor <package_dir>
```

The script first checks whether the setting is already enabled. It only clicks
the menu item when Chrome JS from Apple Events is currently disabled.

## Token behavior

The expensive path is manual visual control: one screen dump and one click per
image. This script avoids that loop. It still may upload images one by one
through the macOS file picker, but the loop runs locally, so token usage is
mostly limited to starting the script and reading its final log.

## Latest local run

On 2026-07-08, the tested package completed a full dry-run in 36.9 seconds:

- selected images: `01.jpg` through `09.jpg`;
- final uploaded count: 9;
- description filled: yes;
- price signal present: yes;
- condition `全新` selected: yes;
- publish button present but not clicked.

Evidence file:

```bash
out/goofish-publish-dryrun-summary.json
```

## Useful flags

```bash
--self-test    Run local package/parser checks without touching Chrome.
--plan-json    Print selected package, price, description length, and the first
               up-to-9 image paths without touching Chrome.
--doctor       Check local package, Chrome tab, and Chrome JS permission.
--enable-chrome-js-menu
               Explicitly enable the Chrome menu item required by this script.
--max-images  Limit selected images. Default 9.
--no-upload   Fill text/price/condition only; do not open file dialogs.
--skip-open   Use the current Chrome tab instead of opening /publish.
--write-summary
               Write final run evidence as JSON after a successful dry run.
```

## Safety boundary

This is a draft preparation helper. Publishing remains a human action.
