#!/bin/bash
# 記事に貼る出力を全部作り直す。
# AWSへの書き込みは一切していない。apply もしない。
cd "$(dirname "$0")"
sec() { echo; echo "########## $1"; }

sec "0. バージョン"
./versions.sh

sec "1. クラスタの雛形"
./cluster-shape.sh

sec "2. タスク定義の雛形"
./taskdef-shape.sh

sec "3. APIモデルの列挙値"
./enums.sh

sec "4. モデルの networkMode 説明"
./model-doc.sh

sec "4b. 雛形の enum は毎回変わる"
./skeleton-random.sh
./skeleton-src.sh

sec "5. タスク定義を段階的に投げる"
./step.sh td-1.json td-2.json td-3.json

sec "6. サービスの雛形(ALB/NW)"
./shape.sh

sec "7. plan が作るもの"
(cd tf && ./summarize.sh)

sec "8. plan が示す配線"
(cd tf && ./wiring.sh)

sec "9. container_name を消すと"
(cd tf-bad && terraform validate -no-color 2>&1 | fold -s -w 38)

sec "10. コンテナ名をずらすと"
(cd tf && ./mismatch.sh)

sec "11. 誤り4種を検出できるか"
./silent.sh ./tf

sec "12. docker build は動かない"
docker build -t demo-web . 2>&1 | fold -s -w 38
