# AIニュース デイリーダイジェスト

毎朝6:00 JSTに自動更新されるAIニュースまとめサイト

公開URL: https://reishisu.github.io/ai-news/

## 構成

```
├── index.html            # ホーム(各号のカード一覧) — _build_index.py が自動生成
├── css/
│   ├── style.css         # ホーム用スタイル
│   └── shared.css        # 全ページ共通(SNS共有バー)
├── js/
│   └── shared.js         # 全ページ共通(SNS共有バー)
├── contents/
│   └── YYYY-MM-DD_id/    # 各号(日付ごと)
│       ├── index.html    # 号の本文(自己完結型HTML)
│       ├── meta.json     # カード用メタ情報(title / summary / thumbnail)
│       └── images/
│           └── thumb.png # ホームのカードに表示するサムネイル
├── _templates/
│   └── home.html         # ホームのテンプレート
├── _build_index.py       # サイトビルダー(トップ生成+共有バー注入)
├── favicon.svg           # サイトアイコン
└── ogp.png               # SNSシェア用OGP画像
```

`_` 始まりのファイルはGitHub Pages(Jekyll)の公開対象から除外されます。

## 仕組み

毎朝6:00 JSTのスケジュールタスク(Claude Code)がニュースを収集し、
`contents/` に当日号を追加 → `python3 _build_index.py` でトップページを再生成 → mainへpush。
6:45 JSTのウォッチドッグが公開済みかを確認し、未公開なら生成からやり直します。
