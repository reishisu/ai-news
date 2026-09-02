# Windows 11 24H2 サポート終了の確認記録

記事: `contents/2026-09-03_windows11-24h2-eos/`

## 何を確かめたか

1. Microsoft のライフサイクルページで、24H2 / 25H2 / 26H1 の終了日を自分で取得して読んだ。
2. 「サポート終了」が何を意味するのかを、ライフサイクル FAQ の本文で確かめた。
   （表の日付だけでは「何が止まるのか」が書かれていないため）
3. 25H2 が自動配信されること・受け取るための操作が不要であることを、
   Windows release health の原文で確かめた。
4. 記事に載せた既知の問題 2 件が、25H2 のページだけでなく 24H2 のページにも
   載っていることを、両ページを取得して照合した。
5. 手元の Windows 11 で、バージョンの確認場所と Windows Update の画面を撮った。

## 取得した一次資料

すべて 2026-09-03（日本時間 05:12 ごろ）に `curl` で取得した。
HTML の原本と、タグを除いたテキストを `sources/` に置いている。

| ファイル | URL | ページの更新日（`updated_at`） |
|---|---|---|
| `lifecycle_win11_home_pro_ja.*` | https://learn.microsoft.com/ja-jp/lifecycle/products/windows-11-home-and-pro | 2026-08-25T14:39:00Z |
| `lifecycle_faq_windows_ja.*` | https://learn.microsoft.com/ja-jp/lifecycle/faq/windows | 2026-08-21T12:39:00Z |
| `release_health_25h2_en.*` | https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-25h2 | 2026-09-02T02:17:00Z |
| `release_health_24h2_en.*` | https://learn.microsoft.com/en-us/windows/release-health/status-windows-11-24h2 | 2026-09-02T02:17:00Z |

取得コマンドは次の形。

```bash
curl -sSL -A "Mozilla/5.0" -o <出力> "<URL>"
```

### 記事で使った箇所

- **ライフサイクル（Home and Pro）** — 適用エディション、日付が太平洋時間（PT）である旨、
  リリース表（26H1・25H2・24H2・23H2・22H2 の開始日と終了日）、
  「24H2 は Windows 11 SE エディションでサポートされている最後のバージョンでした」の注記。
- **ライフサイクル FAQ** — サポート終了後に技術サポート・ソフトウェア更新プログラム・
  セキュリティ修正プログラムを受け取れなくなること。Windows 11 のサービスタイムライン
  （Home・Pro 系は「リリース日から 24 か月」）と、終了前に最新バージョンを入れる必要がある旨。
  Home Edition の脚注（「通常、表示されているサービス終了日より前に新しいバージョンを受け取ります」）。
- **release health（25H2）** — 全対象端末で利用可能になったこと、IT 部門が管理していない
  Home・Pro への intelligent rollout、`no action is required to receive it`、
  待ちたくない場合の `Check for updates` の手順、既知の問題 2 件。
- **release health（24H2）** — 既知の問題 2 件が 24H2 のページにも載っていることの照合だけ。

### 照合のしかた（既知の問題）

```bash
grep -n "Teams and Outlook\|Mouse customization" sources/release_health_24h2_en.txt
```

両方の見出しが 24H2 のページにも出ることを確認した。

## 撮った画面

手元の Windows 11 Pro（バージョン 25H2、OS ビルド 26200.9168、インストール日 2024/12/21）で、
2026-09-03 05:20（日本時間）に撮影した。`shots/` に置いている（記事の `images/` と同じもの）。

| ファイル | 何の場面か |
|---|---|
| `shots/about-version-25h2.png` | 設定 → システム → バージョン情報。「Windows の仕様」の段 |
| `shots/windows-update-uptodate.png` | 設定 → Windows Update。「最新の状態です」と任意の更新（KB5120998） |
| `shots/windows-update-checking.png` | 「更新プログラムのチェック」を押した直後。「更新プログラムを確認しています…」 |

操作の録画も 2 本撮った（バージョン情報を開くところ、更新プログラムのチェックを押すところ）。
録画ファイルはこのリポジトリには置いていない（動画側の素材置き場にある）。

スクリーンショットは、氏名・メールアドレス・デバイス ID が写らない範囲だけを使っている。
それ以外の加工はしていない。

## 図版

`contents/2026-09-03_windows11-24h2-eos/_figures/` に SVG を置き、
`python _render_figures.py 2026-09-03_windows11-24h2-eos` で PNG（ライト／ダーク）を焼いた。

- `eos-timeline.svg` — 24H2 の残り期間だけが極端に短いことを示す（流れ型）
- `check-version.svg` — バージョンの値で 2 つに分かれることを示す（分岐型）

このとき `_render_figures.py` の Chromium のパスが Linux 固定（`/opt/pw-browsers/chromium`）で、
Windows では見つからず落ちた。環境変数 `CHROMIUM` で上書きでき、無ければ既知のパスを
順に探すように直した（探索先は Chromium 系だけ。フォント自己診断は従来どおり動く）。

```bash
python _render_figures.py --selftest
# → フォント自己診断: OK(日本語の字形で描画されています)
```

## 確かめていないこと

- 24H2 の PC に 25H2 が自動で届く瞬間は撮っていない。手元の PC が既に 25H2 のため。
- 要件を満たさない PC への 25H2 導入は試していない（記事の対象外と決めた）。
- IT 部門が管理する端末（Intune・ドメイン参加）の挙動は確認していない。環境が無い。
- 既知の問題 2 件は自分で再現していない。両ページの記載を照合しただけ。
- 日本時間への換算（2026/10/14 6:59:59 AM PT → 同日 22:59:59 JST）は筆者の計算。
  Microsoft のページに日本時間の記載は無い。
