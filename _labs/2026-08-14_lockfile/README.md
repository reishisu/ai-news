# npmのロックファイルが固定しないもの — 検証物

記事: `contents/2026-08-14_lockfile/index.html`

## 何を確かめたか

package-lock.json が「何を固定して、何を固定していないか」を16通りの方法で測った。

| # | スクリプト | 確かめたこと |
|---|---|---|
| 1–13 | `run.sh` | lock 無しの揺れ / 6年前の lock を今日 ci / lock 有りの install / package.json だけ動かした ci / registry 差し替え / 中身すり替え（EINTEGRITY）/ postinstall の npm10 vs npm12 / tarball URL 依存 / `--legacy-peer-deps` で作った lock / `install-scripts approve` / npm-shrinkwrap.json |
| 14 | `run-2.sh` | **lock の `resolved` が `registry.npmjs.org` 以外のとき**、設定した registry ではなく lock の URL へ取りに行く |
| 15 | `run-2.sh` | peer 衝突でフラグ無し ci が出すエラーは、フィクスチャの名前で変わる（私設レジストリなら `ERESOLVE` で npm が `--legacy-peer-deps` を明示する） |
| 16 | `run-3.sh` | `github:` 指定の依存が npm12 で `EALLOWGIT` になる |

14 と 15 は、初版の記事が「lock の URL は取得先の固定ではない」「フラグ無し ci のエラーは `ETARGET`」と
一般化しすぎていたのを測り直したもの。どちらも**一般には成立しない**ことが分かったので記事を直した。

- 14: マジックバリューなのは文字列 `registry.npmjs.org` のときだけ（npm Docs の package-lock.json / File Format）
- 15: 記事の初版が使った `libx` は公開レジストリに実在し安定版の1系が無いため `ETARGET` になっていた

## 動かし方

```bash
bash run.sh                                   # 1–13
bash run-2.sh                                 # 14, 15（私設レジストリ2台を自前で起動する）
NPM12_BIN=/path/to/npm/bin/npm-cli.js bash run-3.sh   # 16（外向きのHTTPSが必要）
```

- `run.sh` は `tools/` に npm@12.0.2 を自前で入れる（初回のみ通信する）
- `run-2.sh` は `reg/registry.js` を 8871 と 8872 で起動する。最小の npm レジストリ実装で、
  `reg/src/<name>-<ver>/` から packument と tarball を組み立てて返す
- 出力は `fold -s -w 38` で折っている（記事の掲載幅に合わせるため。npm 側に折り返し幅の設定が無い）

## 実行環境

2026年8月15日（UTC）/ Linux 6.18.5 / Node.js v22.22.2 / npm 10.9.7 / npm 12.0.2 / Python 3.11.15

## 実行結果

- `output-2.txt` — 14/15/16 の出力（記事に貼ったものと同一）
- `output-1-old-round.txt` — 1回目のラウンド（exp1–exp10, exp5c）の生ログ。
  記事に貼った 1–13 の出力そのものではなく、同じ現象を別の組み立てで確認した記録

## 注意

- `EINTEGRITY` の `but got` 側の sha512 は、偽 tarball を作り直すたびに変わる
- `run-3.sh` は github.com へ実際に取りに行く。ネットワーク制限のある環境では npm 10 側が失敗する
