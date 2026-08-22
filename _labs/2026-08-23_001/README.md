# 2026-08-23_001（デイリーダイジェスト）の検証記録

## 何を確かめたか

### 1. Laravel の debounce は「リスナー側」が今回の新規である

記事の主張は「ジョブ側の debounce は前からあり、v13.26.0 で**リスナー側**に入った」。
これはリリースノートの1行（`[13.x] Add debounceable queued listeners #61169`）だけでは
「debounce 自体が新規」と読めてしまうため、ソースを直接数えて確かめた。

jsDelivr 経由で v13.25.0 と v13.26.1 の同じファイルを取り、`grep -ci debounce` した結果:

| ファイル | v13.25.0 | v13.26.1 |
|---|---|---|
| `Events/Dispatcher.php` | 0 | 14 |
| `Events/CallQueuedListener.php` | 0 | 9 |
| `Queue/CallQueuedHandler.php` | 11 | 11 |

ジョブ側（`CallQueuedHandler`）は前後で変わらず、リスナー側だけが 0 から増えている。
`DebounceFor` 属性・`DebounceLock`・`JobDebounced` の3ファイルは v13.25.0 にも存在した。

**この環境から github.com は403**なので、ソースは
`cdn.jsdelivr.net/gh/laravel/framework@<tag>/<path>` で取得している
（CLAUDE.md 第18節「アクセスできないことを『存在しない』の根拠にしない」）。

### 2. Claude Code 2.1.240 を落とした理由

CLAUDE.md 第16節に従い、対象版の変更行を機械的に全部並べてから判断した。
2.1.240 は `- ` で始まる行が**1行だけ**で、内容は
`Bug fixes and reliability improvements`。`- Added` / `- Changed` / `- Removed` は0件。
npm の公開時刻は 2026-08-22T13:03:23.566Z（日本時間 8/22 22:03）で対象期間内だが、
不具合修正だけの版なので項目にしていない。

### 3. 掲載URLの生存確認

`urls.txt` の9本すべてに `curl -sSL -o /dev/null -w '%{http_code}'` を飛ばし、
全て 200 であることを確認した。

## 動かし方

```bash
./verify_sources.sh
```

`urls.txt` を読むので、同じディレクトリに置いたまま実行すること。

## 実行環境

- 2026年8月23日 5:00〜6:00 JST に実行
- Linux 6.18 / curl 8.x / python3 / PHP 8.4.19 + Composer
- ネットワークは agent proxy 経由。github.com と api.github.com は403のため
  jsDelivr とレジストリ（packagist / npm）で迂回している

### 4. Laravel を実際に動かした debounce の再現

`laravel/` に、この検証のために書いたイベント・リスナー・artisanコマンドを置いた。
ひな形（`composer create-project` で取れるもの）はコミットしていない。手順は
`laravel/SETUP.md`。結果は `output.txt`（記事に貼ったものと同一、加工なし）。

- 属性なし: 発火4回 → 実行4回
- `#[DebounceFor(3)]`: 発火4回 → **実行1回**
- `DebounceFor` と `ShouldBeUnique` の併用: `event()` の時点で `LogicException`

**1プロセス・SQLite で確かめただけで、複数コンテナでの検証はしていない。**
記事の「共通キャッシュが要る」は公式ドキュメントの記述であって、当方の実測ではない。

## この号で「やらなかったこと」

- **複数コンテナでの debounce の挙動は確かめていない**（上記4のとおり）
- **AWS 上での実行はしていない**（認証情報が無い）。Bedrock の価格は
  AWS What's New と OpenAI の changelog の記述を突き合わせただけ
- **Slack + GitHub Copilot の連携も動かしていない**（Copilot Business/Enterprise が要る）。
  GitHub Changelog の記述のみ

## 対象期間を48時間に広げたこと

通常は「前日5:00〜当日5:00 JST」の24時間。今回は 8/22 が土曜で、
AWS What's New は 8/22 5:11 JST を最後に当日の新規投稿が無く、
GitHub Changelog も 8/22 2:28 JST が最後だった。
24時間では中身が立たないため 8/21 5:00〜8/23 5:00 JST に広げた（記事にも明記）。
