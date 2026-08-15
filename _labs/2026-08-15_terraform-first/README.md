# Terraform を最初に動かす — init / validate / plan の実測

記事: `contents/2026-08-15_terraform-first/index.html`

## 何を確かめたか

1. `terraform validate` は `init` の前だと必ず落ちる
2. `init` が何をダウンロードし、何のファイルを作るか / 何秒かかるか
3. `plan` はダミー認証情報だけで通る。**ネットワークを遮断しても通る**
4. `data` ブロックを1つ足すと、本物のAWSに届いて 403 が返る
5. わざと壊したとき `validate` が何を言うか（5パターン）
6. 各コマンドの終了コード
7. **`apply` は一度も実行していない**

## 動かし方

```bash
./demo.sh          # 全ステップ。out/ に実出力が入る（約1分）
./init-timing.sh   # init の所要時間を3回測り、init 直後の ls -a を撮る（約40秒）
./offline-plan.sh  # ネットワークを切り離して plan を回す（init-timing.sh の後に実行）
```

`offline-plan.sh` は `init-timing.sh` が作る `hello-init/`（init 済み）を使います。
`hello/` `hello-init/` は生成物なのでコミットしていません。

## ファイル

| ファイル | 中身 |
|---|---|
| `demo.sh` | 全ステップの実行。設定の書き換えもこの中でやる |
| `init-timing.sh` | init の所要時間の測定と、init 直後のディレクトリの採取 |
| `offline-plan.sh` | `unshare -n` でネットワークを切り離した中で `plan` を実行 |
| `good.tf` | 正しい設定（`demo.sh` が生成）。`hello/main.tf` の元 |
| `summarize_plan.py` | `terraform show -json` の結果を短くまとめる |
| `fold40.py` | 表示幅40桁で折り返す（改行を足すだけ・文字は変えない） |
| `widthcheck.py` | 各行の表示幅を測る（全角=2桁） |
| `make_summary.py` | `out/*.exit` から終了コード表を作る |
| `verify_fold.py` | 折り返しで文字が変わっていないかの検算 |
| `out/*.txt` | Terraform の出力そのまま（幅40桁の擬似端末で実行） |
| `out/*.exit` | 各コマンドの終了コード |
| `out/fold40/*.txt` | 上を40桁で折り返した版。**記事に貼るのはこちら** |
| `refs/*.txt` | 記事に引用した公式ドキュメントの原文（下記） |
| `full-run.log` | `./demo.sh` の全出力 |

### out/ と記事の対応

| 記事の場所 | ファイル |
|---|---|
| 3章 validate（init前） | `out/fold40/01-validate-before-init.txt` |
| 3章 init | `out/fold40/02-init.txt` |
| 3章 所要時間 17.18 / 13.27 / 13.05 秒 | `out/20-init-time.txt` |
| 3章 `ls -a` / `du -sh` / `head -7` | `out/fold40/21-files-after-init.txt` |
| 3章 validate（init後） | `out/fold40/03-validate.txt` |
| 4章 `fmt -check -diff` | `out/fold40/11-fmt-check.txt` |
| 5章 plan（届かないアドレス） | `out/fold40/04b-offline-endpoints.txt` |
| 5章 plan（ネットワーク遮断） | `out/fold40/22-offline-plan.txt` |
| 5章 plan（data あり・403） | `out/fold40/17-data-source.txt` |
| 5章 plan（認証情報なし） | `out/fold40/16-no-credentials.txt` |
| 5章・8章 `state list` | `out/fold40/05-state-list.txt` / `out/19-no-apply.txt` |
| 6章 plan 全文 | `out/fold40/04-plan.txt` |
| 6章 `show -json` の要約 | `out/fold40/14-plan-json.txt` |
| 6章 `plan -out=tfplan` | `out/fold40/13-plan-out.txt` |
| 7章 エラー5種 | `out/fold40/06〜10, 15` |
| 7章 終了コード表 | `out/fold40/00-exitcodes.txt` |

### refs/ に置いた原文

記事に**逐語で引用した**外部資料のうち、折り返しが必要だったものだけ置いています。

| ファイル | 出どころ |
|---|---|
| `docker-change-plan.txt` | HashiCorp Tutorials「Change infrastructure」のプラン出力（`-/+` の例）。**記事6章にはこれをそのまま貼っている**（折り返しは表示側の `white-space: pre-wrap` に任せた） |
| `terraform-LICENSE-params.txt` | hashicorp/terraform の LICENSE、Parameters 節の3項目（原文のまま） |
| `terraform-LICENSE-params.squeezed.txt` | 上の継続行の字下げ（22文字分の空白）を詰めて1項目1行にした版。**記事1章に貼ったもの** |

LICENSE のほうは「空白を除去した文字列が原文と完全一致する」ことを確認済みです
（`python3 -c "import re;n=lambda s:re.sub(r'\s+','',s);print(n(open(A).read())==n(open(B).read()))"`）。
Docker のほうは改行位置も含めて原文と完全一致します。

## 出力の扱い

- 実行は `script -q -e -c "stty cols 40 ..."` で**幅40桁の擬似端末**の中で行う。
  Terraform は端末幅に合わせて折り返すので、`plan` や `validate` のエラーは
  そのままで40桁に収まる。
- ただし `init` の案内文、エラーの位置表示（`on main.tf line 24, in ...`）、
  `Plan: 1 to add, ...` の集計行などは Terraform 側で78桁に固定されているため
  折り返されない。そのぶんだけ `fold40.py` を通した版を `out/fold40/` に用意した。
  **`fold40.py` は空白位置に改行を足すだけで、文字は1つも変更しない。**
- `verify_fold.py out out/fold40` で、空白をすべて取り除いた文字列が元と一致する
  ことを確認済み（24/24ファイルで一致）。
  ただし空白が無い長いURL（`registry.terraform.io/...`）は行の途中で折れる。
- 記事に貼るとき、**行を消したり並べ替えたりしない。**
  長さの都合で落とすときは `（前略）` `（中略）` `（後略）` を本文またはコードブロック内に
  明示する。

### 過去の不備（2026-08-15 修正済み）

- `demo.sh` の手順18（`out/18-files.txt`）の `ls -a` は
  `plan -out=tfplan` と `show -json` の**あと**に撮っており、
  `tfplan` / `tfplan.json` が写り込んでいた。
  記事はこれを「init が作ったもの」として3章に置いていたため、
  `init-timing.sh` で **init 直後に撮り直した**（`out/21-files-after-init.txt`）。
  `out/18-files.txt` はそのまま残してある。
- `out/16-no-credentials.txt` は2つの `Error:` の間に
  `Please see https://... credentials.` の5行がある。
  記事はこれを無印で落としていたため、実出力どおりに戻した。
- init の所要時間「約12秒」に測定記録が無かったため、`init-timing.sh` を追加して
  測り直した（17.18 / 13.27 / 13.05 秒。ダウンロード時間なので毎回ぶれる）。

## 実行環境

```
terraform : 1.14.3
platform  : linux_amd64
provider  : registry.terraform.io/hashicorp/aws 6.60.0
python3   : Python 3.11.15
date(UTC) : demo.sh        2026-08-15T05:39:49Z
            init-timing.sh 2026-08-15T09:23:53Z
            offline-plan.sh 2026-08-15T09:24Z
```

## やっていないこと

- **`terraform apply` は実行していない。** AWSの本物の認証情報が無く、
  作れば課金も発生するため。`out/19-no-apply.txt` に、state ファイルが
  存在しないことを記録してある。
- `terraform destroy` も実行していない（作っていないので対象が無い）。
- リモートバックエンド（S3 backend など）は試していない。ローカル state のみ。
- 記事9章の `local_file`（`hashicorp/local` プロバイダ）は**実行していない**。
  公式リポジトリの `docs/resources/file.md` からの引用のみ。
- **OpenTofu は実行していない。** 1章の記述はすべて OpenTofu 公式サイトの引用。
- ドリフト（Terraform を通さない手動変更）が次の plan に出るかは未検証。
  apply していないため、ずらす対象が存在しない。
