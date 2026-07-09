# SZWego keyword gallery to Goofish runbook

用途：把微购相册/SZWego 中某个店铺的商品，按关键词抓出文案、价格、时间、详情链接和图片，生成可快速筛选的缩略图看板；后续可作为闲鱼选品、上架文案整理或另一个项目任务的输入。

当前沉淀自 2026-07-08 的实测流程：`潮六六档口 开工啦` 相册，关键词 `克罗心` + `Chrome Hearts`。

## 关键结论

- 只抓文案、价格、时间、图片链接、缩略图看板：通常 30-60 秒，几百条以内很快。
- 完整到“打开相册、关键词检索、翻页、去重、分类、生成本地看板、简单验证”：约 1-2 分钟。
- 如果下载原图，耗时主要取决于图片数和大小：
  - 10 张：几秒到十几秒。
  - 100 张：约 1-3 分钟。
  - 1000 张：约 10-30 分钟。
- 本次潮六六实测：两组关键词各抓前 8 页，去重后 275 条商品，275 条都有缩略图；其中标题粗分 `衣服优先` 265 条、`饰品可能` 6 条、`其他/待判断` 4 条。

## 本地路径

主要工作目录：

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit
```

本次预览输出：

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-chao66-chromehearts-preview
```

关键产物：

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-chao66-chromehearts-preview/index.html
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-chao66-chromehearts-preview/items.json
```

本地预览服务：

```bash
cd /Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-chao66-chromehearts-preview
python3 -m http.server 8765 --bind 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:8765/index.html
```

## 输入信息

潮六六相册 URL：

```text
https://www.szwego.com/static/index.html?link_type=pc_home&shop_id=_ZrYrYa-ptceiM4RqMj2tq8dibOVy7cWY&shop_name=%E5%AF%B0%E7%90%83%E5%A5%A5%E8%8E%B1%E4%BB%A3+GO#/shop_detail/_dKUrYqk-vbT7KijIbbG-20JG-TIVIk5CwTKDlgw
```

目标相册 ID：

```text
_dKUrYqk-vbT7KijIbbG-20JG-TIVIk5CwTKDlgw
```

关键词：

```text
克罗心
Chrome Hearts
```

注意：`CH` 太泛，会误伤很多非克罗心商品；判断品牌时优先用 `克罗心` + `Chrome Hearts`。

## 数据接口

商品列表接口：

```text
POST https://www.szwego.com/album/personal/all
```

核心参数：

```text
albumId=<相册 ID>
searchValue=<关键词>
searchImg=
startDate=
endDate=
sourceId=
slipType=1
timestamp=<上一页 pagination.pageTimestamp>
requestDataType=<必要时 itemName>
```

请求体：

```text
tagList=[]
```

分页字段：

```text
result.pagination.isLoadMore
result.pagination.pageTimestamp
result.pagination.dataFromGoodsNumAndMarkCode
```

商品字段中图片常见位置：

```text
imgs
imgsSrc
searchImgs
searchImgsSrc
images
searchImages
```

本次确认首图字段可从 `imgs[0]` 或 `imgsSrc[0]` 取。缩略图 URL 可以使用：

```text
<原图>?imageMogr2/auto-orient/thumbnail/!360x360r/quality/90/format/jpg
```

原图 URL 通常是去掉 `?imageMogr2/...` 后的部分。

## 标准步骤

1. 使用浏览器登录态打开目标相册。
2. 调用商品列表接口按关键词搜索。
3. 每个关键词翻页，建议先取 8 页验证，后续按需要扩展。
4. 去重时优先使用业务指纹，而不是只信 `goods_id`：
   - 首选 `business_dedupe_id`：把完整供货商原文案规范化后做 hash。规范化包括去 emoji、统一空白、把 `D家` 归一为 `迪桑特`、移除开头价格前缀。
   - 次选 `goods_id` / `selfGoodsId`：作为平台追踪 ID。它能标识当前这条相册内容，但如果供货商复制重发，同一个商品可能换 ID。
   - 兜底 `media_fingerprint`：对原图 URL 或本地图片内容做 hash。适合标题小改但图片基本一致的重复商品。
   - 本地 ledger 用 `out/szwego-goofish-dedupe-ledger.json`，可用脚本补齐业务指纹：

```bash
python3 scripts/szwego-dedupe-ledger.py \
  --ledger out/szwego-goofish-dedupe-ledger.json \
  --selected out/szwego-batch5-selected-groups.json \
  out/manual-szwego-packages/batch5_01_demrYcekt0
```

5. 提取字段：
   - `id`
   - `title`
   - `price`
   - `time_stamp` / `new_send_time` / `update_time`
   - `imgs` / `imgsSrc`
   - `link`
6. 用标题关键词粗分类：
   - 衣服优先：短袖、T恤、长袖、卫衣、外套、夹克、防晒、背心、吊带、衬衫、polo、裤、短裤、冰球服、棒球服、球服、上衣、衣服、套装、毛衣、针织、华夫格、圆领、V领、帽衫等。
   - 饰品可能：项链、戒指、手链、手串、耳环、吊坠、锁骨链、银饰、珠宝、珍珠、饰品、挂坠、胸针、眼镜、发夹、钥匙扣、皮带扣等。
7. 写出 `items.json`。
8. 生成 `index.html` 缩略图看板，支持：
   - 全部
   - 只看衣服
   - 饰品可能
   - 其他/待判断
   - 标题搜索
   - 原图链接
   - 详情链接
9. 启本地 HTTP 服务预览。
10. 验证卡片数、图片数、首屏图片加载。

## 本次实测结果

输出目录：

```bash
/Users/gpfs/Desktop/coding/wechat-local-service-kit/out/szwego-chao66-chromehearts-preview
```

统计：

```json
{
  "total": 275,
  "clothing": 265,
  "accessory": 6,
  "other": 4,
  "with_images": 275
}
```

抓取页数：

```text
克罗心：8 页，每页 32 条，仍有更多
Chrome Hearts：8 页，每页 32 条，仍有更多
```

说明：这不是全量极限抓取，只是快速选品预览；如果要全量，可继续按 `pagination.isLoadMore` 往后翻。

## 后续接闲鱼项目时的边界

这个 runbook 只负责从 SZWego 只读采集商品素材。进入闲鱼侧时，遵守 `goofish` 项目的安全边界：

- 优先只读、预览、整理，不默认发布。
- 不记录或导出 token、cookie、验证码、真实账号、订单、地址、聊天等敏感材料。
- 任何发布、发送消息、删除、下架、支付、退款、切号都需要用户在当前任务里明确确认。

## 可复制给新任务的启动提示

```text
请在 /Users/gpfs/Desktop/coding/goofish 中读取 docs/szwego-keyword-gallery-to-goofish-runbook.md。
目标是沿用里面的 SZWego 关键词商品采集流程：打开指定相册，按关键词抓文案、价格、时间、详情链接和图片，生成 items.json 与缩略图看板。先只读采集和预览，不做闲鱼发布或发送动作。
```
