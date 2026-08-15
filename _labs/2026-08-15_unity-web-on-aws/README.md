# 2026-08-15_unity-web-on-aws の検証物

「Unity Web のビルドを、インフラ担当の会社にどう配ってもらうか」の裏付け。

## 何を確かめたか

配信側のヘッダーだけを変えて、ブラウザ側で何が起きるかを実測した。

1. COOP + COEP の有無で `crossOriginIsolated` / `SharedArrayBuffer` /
   共有メモリの Worker 受け渡しがどう変わるか（前回記事の追試）
2. **http:// の IP 直打ち**では、COOP+COEP を正しく付けても
   `isSecureContext=false` → `crossOriginIsolated=false` になること
3. `.wasm` の `Content-Type` と `Content-Encoding` を間違えたときの
   ブラウザの実エラー（MIME 違い / br 素のまま / br と嘘を付く / gzip）
4. **平文 HTTP では Chromium が `br` を要求しない**こと
   （`Accept-Encoding` の実測。Unity のドキュメントの記述と一致）
5. COEP ページから別オリジンの資産を読むとき、
   `fetch` には CORS が要り、`<script src>` には CORP で足りること
6. `aws s3 cp` が `.wasm.br` に何を付けるか
   （**S3 には上げていない**。AWS CLI の関数をローカルで呼んだだけ）
7. CloudFront の `SecurityHeadersConfig` に COOP/COEP/CORP の枠が無いこと
   （`--generate-cli-skeleton` の実出力）
8. Terraform で `custom_headers_config` に3本書いたときの `plan`
   （**apply はしていない**）

## 確かめていないこと

- 実際の S3 バケット / CloudFront ディストリビューションでの動作。
  この環境に有効な AWS 認証情報が無い（`output.txt` の
  「本物のAWSは触れない」節に実エラーを残してある）
- `terraform apply`
- 本物の Unity ビルド出力（`.data` / `.framework.js` / `.loader.js`）。
  検証には手書きの最小 wasm（`add(i32,i32)`）を使っている
- HTTPS での挙動。この環境ではオリジン証明書を用意していないので、
  「安全な文脈」の比較は localhost と IP 直打ちで代用した

## ファイル

```
run_all.sh       全部まとめて実行(出力は output.txt)
make_assets.py   最小 wasm と gzip/brotli 版を作る
serve.py         配信側。8821=ページ, 8822=別オリジン
probe.js         Chromium で実測
check_headers.sh curl でヘッダーだけ見る
s3_guess.py      aws s3 cp が付ける Content-Type を CLI の関数で確認
aws_creds.sh     本物の AWS を触れないことの証拠
aws_check.sh     CloudFront の雛形(--generate-cli-skeleton)
main.tf          CloudFront レスポンスヘッダーポリシー
tf_check.sh      init / validate / plan
plan_summary.sh  plan を幅の狭い画面向けに要約
output.txt       実行結果(記事に貼ったものと同一)
tf-output.txt    terraform の実行結果
retest/          前回記事(2026-08-14_unity-web-threads)の追試
```

## 動かし方

```bash
npm i playwright-core
./run_all.sh
```

`probe.js` は `NODE_PATH` に playwright-core のある場所を入れて動かす。
`serve.py` は 8821 と 8822 を使う。空いていること。
IP 直打ちの検証は `LAN_IP` 環境変数で上書きできる（既定 192.0.2.2）。

## 実行環境

Python 3.11.15 / Node.js v22.22.2 / Chromium 141.0.7390.37 /
Terraform v1.14.3 / aws-cli 1.46.0 (botocore 1.43.62)
実行日: 2026年8月15日

## 注意

数値を書き換えるときは、必ずここで測り直してから直すこと。
出力を手で書き換えるのは禁止。

## 追加（記事執筆時）

`alb_attrs.sh` — ALB のレスポンス側リスナー属性を AWS 公式ドキュメントの
Markdown 版から抜き出し、`cross-origin-` の出現回数を数える。
出力は `alb-attrs-out.txt`（記事2章に貼ったものと同一）。

記事本文で引用した一次資料は、いずれも本文を取得して該当箇所を読んでいる。
AWS ドキュメントは URL 末尾を `.md` にすると装飾なしで取得できる。
