# ECS on Fargate の登場人物 — 実証メモ

実行日: 2026年8月15日

## 前提: このテーマは「実行できない」

AWSアカウントも認証情報も無い。Dockerデーモンも動いていない。
そのため **ECSにデプロイする一連の操作は一切実行していない。**

| やったこと | 実行 |
|---|---|
| `aws ecs *-generate-cli-skeleton` | した |
| AWS CLI のクライアント側パラメータ検証 | した |
| AWS CLI 同梱の ECS APIモデル(列挙値・説明文)の読み出し | した |
| `terraform init` / `validate` / `plan` | した |
| `docker build` | **していない**(デーモン無し。エラーだけ記録) |
| `terraform apply` | **していない** |
| `aws ecs create-cluster` / `register-task-definition` / `create-service` | **していない** |
| タスクの起動、ALB経由のHTTPアクセス、ヘルスチェックの確認 | **していない** |

`aws ecs list-clusters` と `register-task-definition`(td-2.json) は
実際にAWSのエンドポイントへ到達したが、認証情報が無効なため
`UnrecognizedClientException` で失敗した。**書き込みは発生していない。**

## 動かし方

```bash
./run-all.sh > output.txt 2>&1
```

`tf/` と `tf-bad/` は `terraform init` 済みの前提。未実行なら:

```bash
(cd tf && terraform init && terraform plan -out=plan.bin)
(cd tf-bad && terraform init)
```

## ファイル

| ファイル | 何をするか |
|---|---|
| `run-all.sh` | 下記を全部実行して `output.txt` を作る |
| `versions.sh` | 版の一覧 |
| `cluster-shape.sh` | `create-cluster` の雛形 |
| `taskdef-shape.sh` | `register-task-definition` の雛形 |
| `shape.sh` | `create-service` の雛形から ALB/NW 部分 |
| `enums.sh` | APIモデルの NetworkMode / Compatibility / LaunchType |
| `model-doc.sh` | APIモデルの networkMode 説明文 |
| `skeleton-random.sh` | 雛形の enum を10回出して分布を見る |
| `skeleton-src.sh` | その値を決めている AWS CLI のソース行 |
| `step.sh` | td-1/2/3.json を順に投げてエラーを見る |
| `td-1.json` | family だけ |
| `td-2.json` | family + containerDefinitions(name なし) |
| `td-3.json` | containerPort を文字列 `"80"` にした版 |
| `tf/main.tf` | クラスタ/タスク定義/サービス/ALB を一式書いたもの |
| `tf/summarize.sh` | plan が作るリソース一覧 |
| `tf/wiring.sh` | plan から配線の値を抜く |
| `tf/mismatch.sh` | コンテナ名をずらして plan する |
| `tf-bad/main.tf` | `container_name` を消した版 |
| `silent.sh` | 誤り4種を validate/plan が捕まえるか |
| `Dockerfile` | `docker build` が失敗することの確認用 |
| `output.txt` | 上記の実出力(記事に貼るのはこれ) |

## 分かったこと

1. **`--generate-cli-skeleton` の enum 値は毎回ランダムに変わる。**
   `awscli/botocore/utils.py` の L1243 が `random.choice(shape.enum)`。
   雛形の `"networkMode": "host"` は既定値ではない。
   APIモデルの説明文では既定は `bridge`、Fargate では `awsvpc` が必須。

2. **クラスタは名前だけで作れる。** `create-cluster` の雛形に
   必須らしきものは `clusterName` しかない。「箱」でしかないことが形に出ている。

3. **タスク定義に最低限必要なのは `family` と `containerDefinitions`。**
   これはクライアント側で検証されるので、認証情報が無くても確かめられる。

4. **サービスとALBは `containerName` と `containerPort` で結ばれる。**
   `create-service` の `loadBalancers[]` に `targetGroupArn` /
   `containerName` / `containerPort` が並ぶ。

5. **Terraform はその結び目を検証しない。**
   タスク定義のコンテナ名 `web` に対してサービス側を `wev` にしても
   `validate` も `plan` も通る。`network_mode = "bridge"` + FARGATE、
   `target_type = "instance"`、`cpu = "300"` も同様に通る。
   4件すべて「通過」。これらは ECS 側がデプロイ時に弾く。

## 版

`output.txt` の先頭を参照。
aws 1.46.0 / botocore 1.43.62 / terraform 1.14.3 /
hashicorp/aws 6.60.0 / python 3.11.15 / docker CLI 29.3.1(デーモン無し)。

## 編集時の再検証（2026年8月15日・公開前）

事実検証の担当が同じ環境で `run-all.sh` を再実行し、記事に貼った12ブロックの
実行結果がすべて再現することを確認した（捏造なし）。
編集担当はそのうえで、`aws ecs create-cluster --generate-cli-skeleton` と
公式ドキュメント3ページを自分で取り直し、次の3点を訂正した。

1. **Fargate の CPU/メモリ組み合わせは8段階**（記事初稿は「7段階」）。
   `fargate-tasks-services.html` の「Task CPU and memory」表の CPU 値は
   256 / 512 / 1024 / 2048 / 4096 / 8192 / 16384 / 32768 の8行。
   本文の表は8行すべてを写した。

2. **「起動タイプが3つになった」は誤り。**
   `clusters.html` が3つと言っているのは **infrastructure type**
   （`Amazon ECS offers three infrastructure types for your clusters`）。
   `ecs_services.html` は `There are two compute options that distribute your tasks.`
   とし、launch type は `either Fargate or on the EC2 instances` の2択のままで、
   Managed Instances は `you must use the Capacity provider strategy option` と書いている。
   なお `LaunchType` の列挙には以前から `EXTERNAL` もあるため、
   「2択」は Managed Instances 以前から厳密ではない。

3. **`create-cluster` の雛形のトップレベルキーは7個。**
   `capacityProviders` / `clusterName` / `configuration` /
   `defaultCapacityProviderStrategy` / `serviceConnectDefaults` / `settings` / `tags`。
   記事に貼っているのは `jq` で4個抜いたもの。見出しは
   「必須なのは名前だけだった」に直した（API モデル上 `CreateCluster` の
   required は `None`）。

再確認コマンド:

```bash
aws ecs create-cluster --generate-cli-skeleton | jq -r 'keys[]'
curl -sS https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html
curl -sS https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html
curl -sS https://docs.aws.amazon.com/AmazonECS/latest/developerguide/clusters.html
```

`tf/.terraform` と `tf-bad/.terraform`（プロバイダ 6.60.0）は
リポジトリ直下の `.gitignore` で除外済み。再実行時は `terraform init` から。
