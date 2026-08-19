# 2026-08-19_laravel-cors の検証物

## 何を確かめたか

記事「LaravelのCORS設定はどこに書くか」のための実測。確かめたのは3つ。

1. **CORSを強制するのはブラウザで、サーバーは止めていない。**
   同じサーバー・同じ設定に対して、`curl` は 200 と本文を受け取り、
   Chromium は `TypeError: Failed to fetch` で止まる
2. **Laravelでは `config/cors.php` に書く。** ただし **ファイルが無くても
   CORSは効いている**（フレームワーク側に既定値がある）
3. `allowed_origins` の**件数**・`supports_credentials`・`config:cache` で
   出るヘッダーが変わる。ここは資料ではなく実測で確かめた

## ファイル

```
setup.sh          … Laravelを新規作成し、検証用ルートを置く
run_tests.sh      … curl で7つの実験を通す（本体）
browser_check.sh  … curl と Chromium を同じサーバーに当てて比べる
browser_check.js  … Chromium 側（playwright）
page/index.html   … 別オリジンから fetch する実験ページ
configs/*.php     … 差し替える config/cors.php の各パターン
                    （01番は無い。実験1は「ファイルを置かない」状態のため）
narrow.py         … 出力を40桁に折り返す（記事用。文言は変えない）
checkwidth.py     … 40桁を超えた行を報告する
output.txt        … run_tests.sh の結果（記事に貼ったものと同一）
output-raw.txt    … 同じ実行の、ヘッダー全部・折り返しなし
browser-output.txt… browser_check.sh の結果
```

## 動かし方

```bash
bash setup.sh /tmp/cors-lab          # Laravelを作る（数分）
bash run_tests.sh /tmp/cors-lab 8123 # 記事用（40桁に折り返す）
NARROW=0 bash run_tests.sh /tmp/cors-lab 8123   # 生のヘッダー全部
bash browser_check.sh /tmp/cors-lab 8123 8130   # ブラウザとの比較
python3 checkwidth.py output.txt     # 幅の確認
```

`run_tests.sh` と `browser_check.sh` は自分でサーバーを起こして、
終わったら止める。**アプリ本体はリポジトリに入れない**（`/tmp` に作る）。

## 実行環境（この数値を取ったときの構成）

| 何 | バージョン |
|---|---|
| PHP | 8.4.19 (cli) |
| Laravel Framework | **13.26.1** |
| fruitcake/php-cors | v1.4.0（CORSの実処理はこれ） |
| Composer | 2.8.12 |
| Chromium | 141.0.7390.37（`/opt/pw-browsers/chromium`） |
| playwright | 1.56.1（`/opt/node22/lib/node_modules`） |
| Node.js | v22.22.2（ブラウザ操作の道具としてのみ使用） |
| Python | 3.11.15（折り返しと実験ページの配信） |
| curl | 8.5.0 |
| 実行日 | 2026-08-19 |

- DBは使っていない（`install:api` が sqlite にマイグレーションを流すだけ）
- **記事の依頼は「Laravel 12」だったが、`composer create-project laravel/laravel`
  で実際に入ったのは Laravel 13.26.1。** 13で測ったと書くこと

## 出力の幅について（CLAUDE.md 第4節）

`output.txt` は全行が**表示幅40桁以内**（`checkwidth.py` で0件を確認）。
収めるためにやったのは次の3つで、**出力の文言は1文字も変えていない**。

1. コマンドの中でURLとオリジンを変数(`$API` / `$OK_ORIGIN`)にした。
   変数の中身は実行前に出力へ並べてある
2. `export COLUMNS=40` を付けて `php artisan config:show cors` の表を詰めた
3. それでも長い行（`Access-Control-Allow-Origin: https://...` など）は
   `narrow.py` が**40桁で折り返す**。継続行は2スペース字下げ

生のヘッダーが要るときは `output-raw.txt`（折り返しもgrepも無し）を見る。

## ハマった点（記事のネタになる）

### 1. 同じスクリプトを3回流したら3回とも違う結果が出た

`config/cors.php` を差し替えた直後に curl すると、**古い設定のまま**
返ってくることがある。原因は `php artisan serve` の実行環境。

```
$ curl -s "$SAPI" | jq -r ".[]"
sapi=cli-server
opcache.enable_cli=0
opcache.revalidate_freq=2
opcache_get_status=true
```

`php artisan serve` は `cli` ではなく **`cli-server` SAPI** で動く。
`opcache.enable_cli=0` でも**OPcacheは有効**で、`revalidate_freq=2` なので
**ファイルを書き換えても最大2秒は古い内容が使われる**。

対策として、サーバー自身に「いま見えている設定」を言わせる
`GET /api/corsconfig` を足し、**それが新しい値を返すまで待ってから測る**
ようにした（`wait_cfg`）。これで3回とも完全一致するようになった。

**「設定を直したのに変わらない」の原因は `config:cache` だけではない。**
開発中の `artisan serve` でも最大2秒ずれる。

### 2. `php artisan serve` を kill してもポートが空かない

真因は起動の書き方。
`( cd "$APP" && nohup php artisan serve ... & echo $! )` と書くと、
`$!` に入るのは**中間のシェルのPID**で、`kill "$!"` はその中間シェルに
しか当たらない。本体（artisan と子の `php -S`）は丸ごと生き残って
ポートを掴み続けていた。

`( cd "$APP" && exec php artisan serve ... ) &` と `exec` を付けて
`$!` が本体を指すようにし、止めるときは**親(artisan) → 子(`php -S`)**の
順に殺すようにした（`stop_server` に実装済み）。

これを直すまで、**前の実行のサーバーが応答して測定値が混ざっていた**。
いまは `start_server` が最初にポートの空きを確認し、埋まっていたら中止する。

なお、当初この記録には「親は子が死ぬと勝手に建て直す」と書いていたが、
**追検証(2026-08-19)で否定された**。`--port` 明示の `artisan serve` の
子(`php -S`)だけを kill すると親も終了し、ポートは解放された。
再起動が起きるのは `.env` 変更時と、`--port` 未指定で子が異常終了して
別ポートを試す経路のみ（13.26.1 の vendor の `ServeCommand.php` で確認）。

### 3. Laravel 11以降の骨格には `routes/api.php` が無い

`composer create-project` 直後の `routes/` は `web.php` と `console.php` の
2つだけ（HTTPルート用は `web.php` のみ。`console.php` はArtisanコマンド
定義用）。
`php artisan install:api` を実行すると `routes/api.php` が作られ、
`bootstrap/app.php` に `api: __DIR__.'/../routes/api.php'` が足される
（ついでに Laravel Sanctum が入り、マイグレーションが走る）。

ただし **CORSが効くかどうかはルートの置き場所ではなく URL のパスで決まる**。
`cors.paths` の既定が `['api/*', 'sanctum/csrf-cookie']` なので、
`api/` で始まるパスなら `routes/web.php` に書いても対象になる。

### 4. `playwright-core` 単体はこの環境に無い

フル版の `playwright` だけがグローバルに入っている
（`/opt/node22/lib/node_modules/playwright`）。
`browser_check.js` は `playwright-core` を試して、無ければ `playwright` に
フォールバックする。

### 5. ブラウザのコンソールに favicon の404が混ざった

`page/` に `favicon.ico` が無いと、実行タイミングによって
`Failed to load resource: ... 404` がコンソールに出たり出なかったりした。
**空の `favicon.ico` を置いて原因ごと消した**（出力から消したのではない）。
あわせて `waitUntil: 'networkidle'` にしてから読み取っている。

## 測って分かったこと（詳細は lab-summary.md）

- `config/cors.php` が**無くても** `api/*` には `Access-Control-Allow-Origin: *` が付く
- 許可していないオリジンにも**サーバーは 200 と本文を返す**
- `allowed_origins` が**1件だけ**のとき、許可していないオリジンにも
  その1件をそのまま返す（`Vary: Origin` は付かない）。2件以上にすると
  「合ったときだけ返す + `Vary: Origin`」に変わる
- `allowed_origins => ['*']` と `supports_credentials => true` を同時に書くと、
  `*` ではなく**リクエストのOriginをそのまま返し**、
  `Access-Control-Allow-Credentials: true` も付く（＝実質どのオリジンでも通る）
- `config:cache` の後は `config/cors.php` を直しても効かない

数値を書き換えるときは、**必ずここで測り直してから**直すこと。
出力を手で書き換えるのは禁止（それは嘘になります）。
