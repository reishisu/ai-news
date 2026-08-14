# AIニュース デイリーダイジェスト

毎朝6:00 JSTに自動更新されるAIニュースまとめサイト

公開URL: https://reishisu.github.io/ai-news/

## 構成

```
├── index.html            # ホーム(記事一覧) — _build_index.py が自動生成
├── css/
│   ├── style.css         # ホーム用(検索・タグ・注目記事を含む)
│   ├── article.css       # 記事(号)ページ共通 — 可読性優先の1カラム
│   └── shared.css        # 全ページ共通(SNS共有バー)
├── js/
│   ├── shared.js         # 全ページ共通(SNS共有バー)
│   ├── home.js           # ホームの検索・タグ絞り込み
│   └── article.js        # 記事の仕掛け(進捗バー・コピー・クイズ等)
├── contents/
│   └── YYYY-MM-DD_連番/  # 各号
│       ├── index.html    # 記事本文
│       ├── meta.json     # 一覧カード用(category / tags / featured / title / summary / thumbnail)
│       ├── images/       # 記事内の画像(PNG)とサムネイル
│       └── _figures/     # 図版のSVGソース(非公開)
├── _templates/
│   └── home.html         # ホームのテンプレート
├── _build_index.py       # サイトビルダー(ホーム生成+共有バー注入)
├── _render_figures.py    # 図版レンダラー(SVG → PNG、ライト/ダーク2種)
├── favicon.svg           # サイトアイコン
└── ogp.png               # SNSシェア用OGP画像
```

`_` 始まりのファイル・ディレクトリはGitHub Pages(Jekyll)の公開対象から除外されます。

## 図版について

記事内の図版は**すべてPNG**です。`_figures/*.svg` をソースとして
`python3 _render_figures.py <号のディレクトリ名>` を実行すると、
ヘッドレスChromiumが2倍解像度でライト用 `name.png` とダーク用 `name-dark.png` を書き出します。
HTML側は `<picture>` で出し分けます。SVGソースは色を直書きせず、
`var(--fg)` `var(--sub)` `var(--new)` `var(--old)` `var(--track)` などの変数を使います。

## 記事のメタ情報

`contents/<記事>/meta.json` で一覧の見え方が決まります。

```json
{
  "category": "AIで作る技術",
  "tags": ["Claude Code", "入門"],
  "featured": true,
  "title": "記事タイトル",
  "summary": "3〜4文の概要",
  "thumbnail": "images/thumb.png"
}
```

- `tags` — ホームのタグ絞り込みに使われます(多い順に並びます)
- `featured` — `true` の記事が「🔥 注目の記事」に最大3件出ます(無ければ新しい順)
- 検索はタイトル・概要・タグ・**本文**が対象。`?q=` と `?tag=` でURLに状態が残ります

## 仕組み

毎朝6:00 JSTのスケジュールタスク(Claude Code)がニュースを収集し、
`contents/` に当日号を追加 → `_render_figures.py` で図版をPNG化 →
`_build_index.py` でホームを再生成 → mainへpush。
6:45 JSTのウォッチドッグが公開済みかを確認し、未公開なら生成からやり直します。
