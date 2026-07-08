# Goofish publish dry-run script

Purpose: prepare a Xianyu/Goofish publish draft from a local SZWego item package,
then stop before the final publish click.

The script is intentionally conservative:

- uploads at most 9 images, because Goofish accepts 9 item images;
- cleans supplier-only structure out of the buyer-facing description;
- prefers neutral/sports categories such as `运动T恤` or `运动外套`
  over gendered categories when Goofish exposes those options;
- searches/selects recognized brands such as `CHROME HEARTS`, `ADIDAS`,
  or `ARC'TERYX` when the brand field is available;
- parses `颜色：...` and size-table lines from the original copy, then fills SKU specs;
- fills each generated SKU with the item price and default stock `20`;
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

## Copy extraction

The source `copy.goofish.txt` often contains supplier-only structure that should
not be pasted into the public item description. By default the script now asks
the local CPA chat-completions proxy to extract structured listing data, then
falls back to deterministic rules if CPA is unavailable.

Current tested CPA endpoint and model:

```bash
http://100.84.194.46:8317
claude-sonnet-4-6
```

The model extractor must return the same contract as the rule extractor:

- buyer-facing `listing_description`;
- normalized `price`;
- `sku_specs`, such as color and size values;
- `removed_description_lines` for supplier-only rows.

The deterministic fallback builds a cleaned buyer-facing description before
filling the page:

- removes a leading price prefix when it matches `package.json` price, such as
  `85💰潮牌...` becoming `潮牌...`;
- removes color lines such as `颜色：白色 黑色`;
- removes size-list lines such as `M L XL XXL`;
- removes measurement-table lines such as `胸围 / 肩宽 / 衣长 ...`;
- still parses the removed color and size lines from the original copy for SKU
  generation.

`--plan-json` reports both `raw_description_chars` and `description_chars`, plus
`removed_description_lines`, so another agent can inspect what was stripped
before touching Chrome.

Use the old behavior only for debugging:

```bash
python3 scripts/goofish-publish-dryrun-macos.py --keep-raw-description <package_dir>
```

Use deterministic rules without CPA:

```bash
python3 scripts/goofish-publish-dryrun-macos.py --copy-extractor rule --plan-json <package_dir>
```

Force CPA and fail instead of falling back:

```bash
python3 scripts/goofish-publish-dryrun-macos.py --copy-extractor cpa --cpa-model grok-4.3 --plan-json <package_dir>
```

## Category preference

After images are uploaded and Goofish has generated its category select, the
script tries to replace gendered categories with neutral/sports categories:

- T-shirt / short-sleeve copy: prefer `运动T恤`, then `速干衣`, then `文化衫`;
- jacket / outerwear copy: prefer `运动外套`, then `防晒衣`, then `速干衣`;
- hoodie copy: prefer `运动卫衣`, then `运动外套`;
- polo copy: prefer `运动polo衫`, then `运动T恤`.

This is best-effort: if the preferred option is not visible in the category
dropdown, the script leaves Goofish's selected category unchanged and records
the reason in the summary. Category selection runs before condition and SKU
filling because changing category can refresh downstream fields.

## Brand preference

After category selection, the script tries to infer the brand from the original
and cleaned copy, searches the Goofish brand field, and selects the best match.
Known mappings include:

- `克罗心` / `Chrome Hearts` / `CH` -> `Chrome Hearts`, preferring `CHROME HEARTS`;
- `Adidas` / `阿迪达斯` / `三叶草` -> `Adidas`;
- `始祖鸟` / `Arc'teryx` -> `Arc'teryx`;
- `Nike` / `耐克` -> `Nike`;
- `lululemon` / `露露乐蒙` -> `lululemon`.

If the preferred exact match is not visible, the script selects the first
non-empty search result and records it in the summary. Use `--skip-brand` to
leave the field unchanged.

Current tested package:

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-items/shop__ZrYrYa-ptceiM4RqMj2tq8dibOVy7cWY/album__dKUrYqk-vbT7KijIbbG-20JG-TIVIk5CwTKDlgw/item__dt4rYmTugdEsiE6CRRPDZ072QnUFMdAppMPQjbA
```

## Chrome prerequisite

For low-token automation, Chrome must allow page JavaScript from Apple Events.
This lets the script fill text, locate upload controls, and verify upload counts
without repeatedly dumping the full screen state. Image upload defaults to
`file-input` mode: the script reads each local image, constructs a browser
`File` object, assigns it to the hidden upload input, and dispatches the same
events the page expects. This avoids fragile macOS file-picker coordinates.

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

The SKU enhancement was separately verified with `--no-upload` on 2026-07-08:

- parsed specs: `颜色 = 白色 / 黑色`, `尺码 = M / L / XL / XXL`;
- generated SKU combinations: 8;
- SKU price inputs filled: 8;
- SKU stock inputs filled: 8;
- condition `全新` selected: yes;
- publish button present but not clicked.

Evidence file:

```bash
out/goofish-publish-dryrun-no-upload-sku-summary.json
```

After switching upload to `file-input` mode, a full dry-run completed on
2026-07-08 in 22.5 seconds:

- upload mode: `file-input`;
- final uploaded count: 9;
- generated SKU combinations: 8;
- SKU price inputs filled: 8;
- SKU stock inputs filled: 8;
- publish button present but not clicked.

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
--skip-category
               Do not adjust Goofish category after text/image fill.
--skip-brand   Do not search/select brand after category selection.
--skip-sku-specs
               Do not parse/fill color and size SKU specs from the copy.
--sku-stock    Stock value to fill for each generated SKU. Default 20.
--original-price
               Optional original price to fill. Omitted by default.
--copy-extractor
               Copy analysis strategy: auto, cpa, or rule. Default auto.
--cpa-base-url CPA OpenAI-compatible base URL. Default http://100.84.194.46:8317.
--cpa-model    CPA chat model. Default claude-sonnet-4-6. grok-4.3 also tested.
--cpa-timeout  CPA request timeout in seconds. Default 45.
--keep-raw-description
               Fill the original supplier copy instead of the cleaned
               buyer-facing description.
--upload-mode  Image upload strategy. Default file-input. Use file-picker only
               as a fallback for debugging the old macOS picker path.
--skip-open   Use the current Chrome tab instead of opening /publish.
--write-summary
               Write final run evidence as JSON after a successful dry run.
```

## Safety boundary

This is a draft preparation helper. Publishing remains a human action.
