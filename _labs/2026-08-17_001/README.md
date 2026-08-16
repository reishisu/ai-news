# 2026-08-17 デイリーダイジェスト — 裏取りの記録

この号は**実行を伴う検証がありません**（コードもテストも書いていない）。
代わりに、記事の主張ごとにどのURLをどう取得して確認したかを残します。

## 実行環境

- 取得日: 2026年8月17日 JST
- 手段: `curl`（HTTPS プロキシ経由）
- Android実機・VRChatクライアント・Unity は**いずれも動かしていない**

## 取得したURLと、確認したこと

| # | URL | 確認した内容 |
|---|---|---|
| 1 | https://support.google.com/product-documentation/answer/14343500 | `Android WebView v152 (2026-08-12)` の本文が定型文3行のみ。v151 は定型文の前に2行、v150 は3行。v149 / v148 / v146 / v145 / v144 は定型文のみ。**ページに v147 の項は存在しない** |
| 2 | https://chromereleases.googleblog.com/2026/08/stable-channel-update-for-desktop_01815628406.html | 151.0.7922.137/.138、`This update includes 5 security fixes.`、CVE-2026-19556〜19560 がすべて High / Use after free。著者 Daniel Yip |
| 3 | https://chromereleases.googleblog.com/2026/08/chrome-for-android-update_0633903601.html | `Android releases contain the same security fixes as their corresponding Desktop releases`。著者 Harry Souders |
| 4 | https://chromereleases.googleblog.com/2026/08/chrome-for-android-update_0318651269.html | Chrome 152 (152.0.7977.42) を `to a small percentage of users`。著者 Krishna Govind |
| 5 | https://chromestatus.com/api/v0/features/5175745573945344 | Connection Allowlists。desktop/android/webview = 152、`status.text = "Proposed"`、`is_released = false`、`accurate_as_of = 2026-07-23`、summary / motivation / debuggability の原文 |
| 6 | https://chromium.googlesource.com/chromium/src/+/HEAD/docs/security/severity-guidelines.md | 重大度が Critical(S0) / High(S1) / Medium(S2) / Low(S3) の4段階であること、High の定義文 |
| 7 | https://docs.vrchat.com/docs/vrchat-202631 | Build 1885 / Live。VRC_Pickup の再導入と `The SDK ... is *not* shipping with this patch`、Prop Abilities、rtspt→rtsp、VRCObjectSync、SDF、Bug Report |
| 8 | https://docs.vrchat.com/docs/vrchat-202631p1 | Build 1886。不具合修正と表示調整のみ（記事で扱わない判断の根拠） |
| 9 | https://creators.vrchat.com/releases/ | 最新は Release 3.10.4 / `datePublished: 2026-06-17` / Momo the Monster。以降 3.10.3(2026-04-16)、3.10.2(2026-02-05) |

## 取得時のつまずき

- Chrome Status API は先頭に XSSI 除けの `)]}'` が付く。`json.loads` の前に最初の `{` まで捨てる
- `creators.vrchat.com` は既定の User-Agent だと **403（`waf_code: 13799`）**。
  連絡先入りの UA を `-A` で渡すと通る
- `chromium.googlesource.com` の `?format=TEXT` は `main` 指定だと
  `INVALID_ARGUMENT` になる。`HEAD` を使うか、HTML をそのまま取る

## 0件にした4カテゴリについて

実務者向けAI開発ツール / Web開発・インフラ / 技術・研究 / モデル・業界 は、
対象期間（8/16 05:00 〜 8/17 05:00 JST）に該当する一次情報が無く0件。
クライアント技術のみ「直近1週間」枠（前号 2026-08-16_001 から継続している運用）で
8/12 の2件を拾っている。
