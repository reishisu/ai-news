# Terraform を最初に動かす — init / validate / plan の実測

## 何を確かめたか

1. `terraform validate` は `init` の前だと必ず落ちる
2. `init` が何をダウンロードし、何のファイルを作るか
3. `plan` はダミー認証情報だけで通る。AWSに1回も繋がない
4. わざと壊したとき `validate` が何を言うか（6パターン）
5. 各コマンドの終了コード
6. **`apply` は一度も実行していない**

## 動かし方

```bash
./demo.sh          # 全部走る。out/ に実出力が入る
```

所要時間は約1分（うち `init` のプロバイダ取得が約12秒、840MB）。

## ファイル

| ファイル | 中身 |
|---|---|
| `demo.sh` | 全ステップの実行。設定の書き換えもこの中でやる |
| `good.tf` | 正しい設定（`demo.sh` が生成）。`hello/main.tf` の元 |
| `summarize_plan.py` | `terraform show -json` の結果を短くまとめる |
| `fold40.py` | 表示幅40桁で折り返す（改行を足すだけ・文字は変えない） |
| `widthcheck.py` | 各行の表示幅を測る（全角=2桁） |
| `make_summary.py` | `out/*.exit` から終了コード表を作る |
| `out/*.txt` | Terraform の出力そのまま（幅40桁の擬似端末で実行） |
| `out/*.exit` | 各コマンドの終了コード |
| `out/fold40/*.txt` | 上を40桁で折り返した版。記事に貼るのはこちら |
| `verify_fold.py` | 折り返しで文字が変わっていないかの検算 |
| `refs/*.html`, `refs/*.txt` | HashiCorp公式ドキュメントの取得物 |
| `full-run.log` | `./demo.sh` の全出力 |

## 出力の扱い

- 実行は `script -q -e -c "stty cols 40 ..."` で**幅40桁の擬似端末**の中で行う。
  Terraform は端末幅に合わせて折り返すので、`plan` や `validate` のエラーは
  そのままで40桁に収まる。
- ただし `init` の案内文と、エラーの位置表示（`on main.tf line 24, in ...`）は
  Terraform 側で78桁に固定されているため折り返されない。
  そのぶんだけ `fold40.py` を通した版を `out/fold40/` に用意した。
  **`fold40.py` は空白位置に改行を足すだけで、文字は1つも変更しない。**
- `verify_fold.py` で、空白をすべて取り除いた文字列が元と一致することを確認済み
  （22/22ファイルで一致 = 文字は1つも足していない・消していない）。
  ただし空白が無い長いURL（`registry.terraform.io/...`）は行の途中で折れる。

## 実行環境

```
terraform : 1.14.3
platform  : linux_amd64
provider  : registry.terraform.io/hashicorp/aws 6.60.0
python3   : Python 3.11.15
date(UTC) : 2026-08-15T05:39:49Z
```

## やっていないこと

- **`terraform apply` は実行していない。** AWSの本物の認証情報が無く、
  作れば課金も発生するため。`out/19-no-apply.txt` に、state ファイルが
  存在しないことを記録してある。
- `terraform destroy` も実行していない（作っていないので対象が無い）。
- リモートバックエンド（S3 backend など）は試していない。ローカル state のみ。
