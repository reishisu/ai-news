# AWSのアクセス制御の地図 — 実証メモ

記事「AWSのアクセス制御の地図 — IAMのユーザー・ロール・ポリシーは何が違うのか」
の裏付け。

## いちばん大事な前提

**AWSアカウントに対しては1回も実行していない。** この環境に有効な認証情報が
無いため、`aws iam create-user` などの実行は行っていない（行えない）。

ここで取れているのは次の3種類だけ。

1. 認証情報が要らない AWS CLI の動作
   （`--generate-cli-skeleton`、引数不足のクライアント側エラー、認証情報が
   無いときのエラー）
2. AWSが公開している**機械可読データ**の取得と照合
   （Service Reference API / 公式ドキュメントのMarkdown版）
3. ローカルだけで完結する検証
   （Terraform の `aws_iam_policy_document`、parliament の lint、
   判定順を書き写した自作スクリプト）

「AWS上でこう動いた」とは書けない。書いてよいのは
「AWSの公式データ／公式ドキュメントにこう書いてある」までです。

## 実行環境（2026年8月15日）

| 対象 | 版 |
|---|---|
| AWS CLI | 1.46.0 (botocore 1.43.62, Python 3.11.15) |
| Python | 3.11.15 |
| Terraform | v1.14.3 |
| terraform-provider-aws | 6.60.0 |
| parliament | 1.6.4 |
| pytest | 9.1.1 |

## 動かし方

```bash
pip install parliament            # 1.6.4
python3 fetch_refs.py             # 公式データを取り直す
(cd tf && terraform init)
(cd tf-bad && terraform init)
bash run_all.sh > output.txt 2>&1
```

`output.txt` が記事に貼った実出力そのもの。全201行、1行は最大でも
半角40桁に収めてある（`run_all.sh` の中で `fold -s -w 38` を掛けている
箇所があり、そこは**折り返しただけで文言は変えていない**）。

## ファイル

| ファイル | 何をするか |
|---|---|
| `run_all.sh` | 全部まとめて実行して `output.txt` を作る |
| `output.txt` | 実行結果（記事に貼ったものと同一） |
| `fetch_refs.py` | 公式の機械可読データ／ドキュメントを取得 |
| `check_actions.py` | アクション名が実在するかを公式データで照合 |
| `check_resources.py` | `Resource` に書くARNの形を公式データで確認 |
| `lint.py` | parliament で7本のポリシーJSONを検査 |
| `lint_community.py` | 既定lintと community auditors の差 |
| `eval_sim.py` | 判定順の**おもちゃ実装**（AWSの本物ではない） |
| `test_eval_sim.py` | 上の実装が意図どおりかを固定するpytest |
| `fold_diag.py` | `terraform validate -json` を38桁で折り返す |
| `extract_quotes.py` | 公式ドキュメントから引用文を機械抽出 |
| `quotes.md` | その出力（記事の引用はここからコピーする） |
| `policies/*.json` | 検査対象のポリシー7本 |
| `tf/main.tf` | 正しいポリシーをローカルでJSONに組み立てる |
| `tf-bad/main.tf` | `effect = "allow"` にして落とす版 |
| `tf/policy-rendered.json` | plan から取り出した組み立て後のJSON |
| `fetch-output.txt` | `fetch_refs.py` の実行結果 |

## 分かったこと

### 1. 認証情報が無いときのエラーは2種類ある

- 何も設定していない → `Unable to locate credentials.`（通信していない）
- 値はあるが無効 → `InvalidClientTokenId`（AWSまで届いて拒否された）

この環境は `AWS_ACCESS_KEY_ID=proxy-injected` が入っているため、素の
`aws sts get-caller-identity` は後者になる。前者を再現するには
`AWS_SHARED_CREDENTIALS_FILE=/dev/null AWS_CONFIG_FILE=/dev/null` と
`AWS_EC2_METADATA_DISABLED=true` を足し、環境変数を外す必要がある。

### 2. ロール作成は信頼ポリシーを省略できない（通信前に落ちる）

`aws iam create-role --role-name my-role` は AWS に到達する前に
argparse が止める。`--assume-role-policy-document` は必須。
API リファレンスでも `AssumeRolePolicyDocument: Required=Yes`。

### 3. `s3:ListBucket` と `s3:GetObject` は書くARNが違う

公式の Service Reference データがそう言っている。

```
s3:ListBucket -> arn:aws:s3:::${BucketName}
s3:GetObject  -> arn:aws:s3:::${BucketName}/${ObjectName}
```

バケットARNだけ書いて `GetObject` を許可したつもりになる事故は、
これで説明できる。

### 4. `Effect` の大文字小文字は本当に効く

`effect = "allow"` にすると terraform-provider-aws が
`expected statement.0.effect to be one of ["Allow" "Deny"], got allow`
で落ちる。公式ドキュメントも "The `Effect` value is case sensitive." と
書いている。

### 5. lint は「全許可ポリシー」を既定では見逃す

`{"Action": "*", "Resource": "*"}` に対し parliament の既定は
指摘0件。`include_community_auditors=True` にして初めて24件出る。

### 6. lint は「そのJSONが何のポリシーか」を知らない

- ロールの信頼ポリシー（`Resource` が無いのが正しい）を
  `MALFORMED: Statement contains neither Resource nor NotResource` と誤検出する
- アイデンティティベースのポリシーに `Principal` を書いても素通りする

つまり lint に通ったことは正しさの証明にならない。

## 再現できなかったもの / やっていないこと

- **AWS上での実行は一切していない。** ユーザー作成、ロール作成、
  `sts assume-role`、ポリシーシミュレータ（`iam simulate-principal-policy`）
  のいずれも実行していない。
- `aws <command> help` は最初 `Could not find executable named "groff or mandoc"`
  で失敗した。`apt-get install -y groff` を入れて動くようになったが、
  出力幅は78桁固定で `MANWIDTH` も `COLUMNS` も効かなかった。
  記事にはヘルプ全文は載せず、`--generate-cli-skeleton` を使う。
- `parliament --file <path>` は端末が無い環境だと
  `You cannot pass a file with --file and use stdin together` で必ず落ちる。
  `sys.stdin.isatty()` が偽になるため。ライブラリAPIを直接呼んで回避した。
- `aws sts assume-role --generate-cli-skeleton output` は AWS CLI v1 では
  未対応（`output` が位置引数として解釈されずエラー）。レスポンスの形は
  取れていない。
- `terraform console` は state が無いと `(known after apply)` しか返さない。
  組み立て後のJSONは `terraform plan -out` → `terraform show -json` から取った。
- 最初に一度 `terraform apply -auto-approve` を実行してしまった。対象は
  data source と output だけで `Apply complete! Resources: 0 added, 0 changed,
  0 destroyed.` であり、AWS上には何も作られていない。以後は plan のみ。
  生成された `terraform.tfstate` は削除済み。
- `eval_sim.py` は**AWSの評価エンジンではない**。公式ドキュメントに書かれた
  順序を単一アカウント・アイデンティティベースに絞って書き写した自作品で、
  Condition は `Bool` 演算子しか実装していない。SCP / RCP / リソースベース
  ポリシー / セッションポリシー / クロスアカウントは扱っていない。

## 出典（本文を取得して読んだもの）

`quotes.md` に、抜き出した原文とURLをまとめてある。取得は
`fetch_refs.py`（2026年8月15日）。

- AWS Service Reference API
  `https://servicereference.us-east-1.amazonaws.com/`
- IAM User Guide: Policy evaluation logic / Effect / Version / Principal /
  IAM roles
- IAM API Reference: `CreateRole`
- AWS STS API Reference: `AssumeRole`

---

## 追記（記事執筆時 2026-08-15）

- `verify_quotes.py` / `verify-output.txt`
  記事に貼った引用の**断片63件**が公式ドキュメントに実在するかを機械照合する。
  各ページのMarkdown版を取得し、Markdownの強調・リンク記法・バックスラッシュ
  だけ落として部分一致を見る。実行結果は「不一致 0 件」。
  **これは「断片が存在した」ことの確認で、「引用ブロック全文が一字一句同じ」
  ことの証明ではない。** 途中の省略やJSONの整形はこの方法では検出できない。
- `extra-output.txt`
  `run_all.sh` の 6.（`head -8` で `DurationSeconds` が切れていた）と
  2.（ロール名が長く380px幅に収まらなかった）を、記事用に取り直したもの。
  文言は無加工。

---

## 追記2（編集時 2026-08-15・editor-in-chief）

事実検証で挙がった指摘を反映した。

### 直した誤り（重大）

1. **「信頼ポリシーには『誰でもいい』と書けない」は誤りだった。**
   ARNの**一部**をワイルドカードにできないだけで、`"Principal": {"AWS": "*"}`
   は書ける。根拠は `reference_policies_elements_principal.md`:
   - `You can use a wildcard (*) to specify all principals in the Principal
     element of a resource-based policy`
   - `We strongly recommend that you do not use a wildcard (*) ... This is
     especially true for IAM role trust policies`
   - `Do not leave your role accessible to everyone!`
   記事は「IAMが防いでいる」→「書けてしまうので書かないこと」に反転させた。
2. **「存在しないアクション名を書いてもIAMはエラーにならない」は無出典だった。**
   公式には `INVALID_ACTION` / Finding type `ERROR` がある
   （`access-analyzer-reference-policy-checks.md`）。断定を削り、
   「検証機能は ERROR を返す（公式）／API受理時の挙動は未確認」に書き分けた。

### 直した細かい点

- 8章の並び順は公式 `best-practices.md` の `##` 見出し順ではない
  （公式は federation → workloads → MFA → access keys → root user）。
  記事側に「並べ替えているのは筆者」と明記した。
- 引用の未表示の中略を解消（タスクロール／実行ロールの "required" の一文、
  confused deputy の文頭 `When creating your task IAM role,`、
  `without calling sts:AssumeRole` の後続節）。
- 公式JSONの `"Version":"2012-10-17",`（コロン後スペースなし）を原文どおりに戻し、
  見出しに「原文のまま・行末の空白のみ除去」と書いた。
- `fold_diag.py` は 13 行、`eval_sim.py` は 114 行（`wc -l`）。記事の
  「15行」「70行ほど」を実測値に直した。
- `check_resources.py` が `accesspoint` / `accesspointobject` を黙って
  落としていたので、**省略したことを出力自身に印字する**ように直して実行し直した。
- 「ロールには必ずポリシーが2枚付く」は一般化しすぎ。必須なのは信頼ポリシーだけ
  （`CreateRole` の `AssumeRolePolicyDocument: Required: Yes`）。

### 保存した一次資料を増やした

`fetch_refs.py` の取得対象に、以前メモリ上でしか読んでいなかった
`introduction` / `id_groups` / `reference_policies_elements` / `best-practices` /
`access-analyzer-reference-policy-checks` / ECS 3ページ /
`feature-container-credentials` / `AmazonECSTaskExecutionRolePolicy` を追加した。
26件すべて HTTP 200、失敗 0 件（`fetch-output.txt`）。

### 今回も確認できなかったこと

- **存在しないアクション名を含むポリシーをIAM APIが受理するかどうか。**
  認証情報が無く `CreatePolicy` を呼べない。記事にも「未確認」と書いた。
- **IAM Access Analyzer のポリシー検証の実行結果。** 同上。
- **Terraform の再現。** `/` の空きが少なくプロバイダを取り直せない場合がある。
  既存の `tf/` `tf-bad/` の `.terraform` を消さないこと。
