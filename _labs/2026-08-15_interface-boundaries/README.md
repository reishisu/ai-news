# 検証: 契約(JSON Schema)で破壊的変更を統合前に検出できるか

「チームで作る技術」新記事の裏付け用。
自社のフロント(consumer)と委託先サーバー(provider)が
`GET /api/search?q=...` を分担して並行開発するシナリオを、
実際にPythonコードとjsonschemaで再現した。

## 確かめたこと

1. 契約(`schema.json`)を先に決めておけば、
   consumer側の「これが返ってくるはず」という期待値(`consumer_expectation.json`)を
   実装前に契約と突き合わせられる
2. providerの最初の実装(`provider_v1.py`)は契約に適合する
3. providerが後日、consumerに知らせず
   `score` → `relevance_score` へのリネームと
   `id` の型変更(整数→文字列)を入れると(`provider_v2_broken.py`)、
   **契約テストが実際に失敗し**、jsonschemaが具体的なエラーを返す
4. `jsonschema.validate()` はデフォルトで代表的なエラーを1件返す。
   `Draft7Validator.iter_errors()` で全件見ると、
   実際には6件(3件の型違反 + 3件の必須プロパティ欠如)を検出していた
   (これは記事本文の参考情報。`run_contract_test.py` 自体は
   `validate()` を使い、代表1件を表示する設計にしている)

## ファイル

| ファイル | 内容 |
|---|---|
| `schema.json` | consumer/providerが事前に合意した契約(JSON Schema) |
| `consumer_expectation.json` | consumerチームが期待するレスポンス例 |
| `provider_v1.py` | providerの初期実装。契約に適合 |
| `provider_v2_broken.py` | providerが後日入れた破壊的変更(score→relevance_score, idの型変更) |
| `run_contract_test.py` | 契約テストを実行し、v1/v2それぞれの結果を表示するスクリプト |
| `output.txt` | `python3 run_contract_test.py` の実行結果そのまま |

## 動かし方

```bash
cd _labs/2026-08-15_interface-boundaries
python3 run_contract_test.py
```

## 実行環境

- `python3 -V` → `Python 3.11.15`
- jsonschema → `4.26.0`
  (`importlib.metadata.version("jsonschema")` で確認。
  `jsonschema.__version__` は非推奨警告が出るため使わなかった)

## 実行結果(output.txt そのまま)

```
契約テスト: GET /api/search
------------------------
[OK] consumer側の期待値
[OK] provider v1
[NG] provider v2(破壊的変更)
  'score' is a required property
```

## 出力幅について

記事は幅380pxのスマホで読まれる前提のため、1行を
全角20字/半角40字程度に収める必要がある。
`unicodedata.east_asian_width()` で実測したところ、
出力6行の表示幅は最大32(半角換算)で、全行が基準内に収まっていた。
手で行を短縮する加工は行っていない
(`run_contract_test.py` の print文自体を短く設計した結果)。

## 補足: なぜ `validate()` は1件しかエラーを返さないのか

`jsonschema.validate()` は内部で `best_match()` を使い、
複数の違反があっても代表的な1件を選んで例外にする仕様
(jsonschema自体のドキュメント上の既知の挙動。今回は実測で確認したのみで、
仕様書の該当箇所までは照合していない)。
全件を見るには `Draft7Validator(schema).iter_errors(payload)` を使う必要がある。
今回のケースでは以下の6件が実際に検出された(iter_errorsで確認、
記事本文用ではなく検証メモとして記録):

```
- 's-1' is not of type 'integer'  (results[0].id)
- 's-2' is not of type 'integer'  (results[1].id)
- 's-3' is not of type 'integer'  (results[2].id)
- 'score' is a required property  (results[0])
- 'score' is a required property  (results[1])
- 'score' is a required property  (results[2])
```

## 再現できなかったもの

なし。すべて `python3 run_contract_test.py` で実行・確認できた。
実際のHTTPサーバーは立てていない
(`provider_v1.search()` / `provider_v2_broken.search()` は
レスポンスの生成ロジックのみを模擬する関数で、
FlaskやFastAPI等での実サーバー化は行っていない。記事で
「実サーバーは検証していない」と明記すること)。
