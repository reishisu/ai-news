# Laravel 13.25 の `queue:continue` と `queue:resume` は両方実在するのか

実測日: 2026-08-15 / 実行環境: Linux 6.18.5

## 結論(先に)

**公式ドキュメントの記述は正しい。誤記ではない。**

- 正式名は **`queue:resume`**
- **`queue:continue` は `queue:resume` の別名(alias)** として
  フレームワークに正式登録されている
- どちらの名前で叩いても同じ `ResumeCommand` が動く。
  `--all` も引数付きも、両方の名前で動作を実測した

ドキュメントは1ページ内で正式名と別名を混ぜて書いているため
「2つ別のコマンドがある」ように読めるが、実体は1つ。

---

## 実行環境

| 項目 | 値 |
|---|---|
| PHP | 8.4.19 (cli, NTS) |
| Composer | 2.8.12 |
| Laravel Framework | **13.25.0** (2026-08-11 リリース) |
| DB | SQLite (`database/database.sqlite` 実ファイル) |
| QUEUE_CONNECTION | database |
| CACHE_STORE | database |
| Python | 3.11.15 |
| Node | v22.22.2 (今回は未使用) |
| Chromium | 141.0.7390.37 (今回は未使用) |

プロジェクト作成:

```
composer create-project laravel/laravel \
  laravel-queue-test "13.*"
```

`php artisan --version` の出力:

```
Laravel Framework 13.25.0
```

---

## 1. コマンド一覧で実在を確認

`php artisan list queue` の既定の書式は1行が約70桁あり
記事の幅に入らない。**出力形式をスクリプト側で変えて**
名前と別名だけを出す(手での書き換えはしていない)。

```
$ php artisan list queue --format=json --no-ansi \
  | jq -r '.commands[]
    | select(.name|startswith("queue:"))
    | "\(.name)\n  alias: \(if (.usage|length)>1
      then (.usage[1:]|join(",")) else "-" end)"'
```

実出力(そのまま):

```
queue:clear
  alias: -
queue:failed
  alias: -
queue:flush
  alias: -
queue:forget
  alias: -
queue:listen
  alias: -
queue:monitor
  alias: -
queue:pause
  alias: -
queue:prune-batches
  alias: -
queue:prune-failed
  alias: -
queue:restart
  alias: -
queue:resume
  alias: queue:continue
queue:retry
  alias: -
queue:retry-batch
  alias: -
queue:work
  alias: -
```

**これが決定的。** `queue:pause` は別名なしの独立コマンド、
`queue:resume` は `queue:continue` という別名を持つ。
そして **`queue:continue` は独立した項目として出てこない。**
JSON 形式は正式名だけを列挙するため。

一方、既定のテキスト形式(`php artisan list queue`)では
別名も1行として並ぶので `queue:continue` が独立表示され、
`queue:resume` の行には `[queue:continue]` が付く。
**この表示差が「2つあるように見える」原因。**

なお `queue:table` / `queue:failed-table` /
`queue:batches-table` も同様に別名で、正式名は
`make:queue-table` などである(下記も実出力):

```
$ php artisan list --format=json --no-ansi | jq -r \
  '.commands[] | select((.usage|join(" "))
   | test("queue:(table|failed-table|batches-table)"))
   | "\(.name)\n  alias: \(.usage[1:]|join(","))"'
make:queue-batches-table
  alias: queue:batches-table
make:queue-failed-table
  alias: queue:failed-table
make:queue-table
  alias: queue:table
```

つまり Laravel では**別名の登録はよくある作法**であり、
`queue:continue` もその1つ。特殊事例ではない。

---

## 2. ソースで別名であることを確定

フレームワークのコマンドファイルは**2つしか無い**:

```
$ ls vendor/laravel/framework/src/Illuminate/\
Queue/Console/ | grep -iE "pause|continue|resume"
PauseCommand.php
ResumeCommand.php
```

`ContinueCommand.php` は存在しない。

`ResumeCommand.php` の該当箇所(そのまま):

```php
#[AsCommand(name: 'queue:resume', aliases: ['queue:continue'])]
class ResumeCommand extends Command
{
    protected $signature = 'queue:resume
                            {queue? : The name of the queue that should resume processing}
                            {--all : Resume job processing for all queues on all connections}';

    /**
     * The console command name aliases.
     *
     * @var list<string>
     */
    protected $aliases = ['queue:continue'];
```

`name:` が `queue:resume`、`aliases:` が `queue:continue`。
**正式名は `queue:resume`。**

### ヘルプでも確認できる

```
$ php artisan queue:continue --help --no-ansi
```

```
Description:
  Resume job processing for a paused queue

Usage:
  queue:resume [options] [--] [<queue>]
  queue:continue
```

`queue:continue` を指定したのに Usage の先頭が
`queue:resume` になっている = 別名として解決されている。

---

## 3. 実際に一時停止 → 再開まで動かす

ジョブは `storage/done.log` に1行追記するだけのもの
(`app/Jobs/RecordJob.php`)。

### 3-1. `queue:pause` → `queue:continue`(別名)

```
$ php artisan queue:pause database:default

 INFO Job processing on queue [database:default] has been paused. 


$ php artisan tinker (dispatch job A)
dispatched

$ queue:work --stop-when-empty (paused)
[exit=0]

$ cat storage/done.log
(空 = 未処理)

$ php artisan queue:continue database:default

 INFO Job processing on queue [database:default] has been resumed. 


$ queue:work --stop-when-empty (resumed)
 2026-08-15 21:16:31 App\Jobs\RecordJob  RUNNING
 2026-08-15 21:16:31 App\Jobs\RecordJob  3.68ms DONE
[exit=0]

$ cat storage/done.log
A
```

一時停止中はワーカーを起動しても**ジョブを拾わない**
(ログが空のまま、worker は即終了 exit=0)。
`queue:continue` で再開すると処理された。

### 3-2. `queue:pause --all` → `queue:resume --all`

```
$ php artisan queue:pause --all

 INFO Job processing on all queues across all connections has been paused. 


$ tinker (dispatch job B)
dispatched

$ queue:work --stop-when-empty (paused)

$ cat storage/done.log
(空 = 未処理)

$ php artisan queue:resume --all

 INFO Job processing on all queues across all connections has been resumed. 


$ queue:work --stop-when-empty (resumed)
 2026-08-15 21:16:54 App\Jobs\RecordJob  RUNNING
 2026-08-15 21:16:54 App\Jobs\RecordJob  4.20ms DONE

$ cat storage/done.log
B
```

### 3-3. 4通りの組み合わせが全部通る

```
$ php artisan queue:continue --all

 INFO Job processing on all queues across all connections has been resumed. 


$ php artisan queue:resume database:default

 INFO Job processing on queue [database:default] has been resumed.
```

`queue:continue --all` も `queue:resume <queue>` も動く。
**名前と引数の組み合わせに制限は無い。**

### 出力幅について(正直に記録)

`COLUMNS=40` を付けても、Laravel の `INFO` バナーと
`queue:work` の進捗行は**折り返されない**。実測した桁数:

```
$ php artisan queue:resume --all --no-ansi \
  | awk '{print length"\t"$0}'
0	
76	 INFO Job processing on all queues across all connections has been resumed. 
0
```

```
$ php artisan queue:work database \
  --stop-when-empty --no-ansi | awk '{print length"\t"$0}'
48	 2026-08-15 21:21:05 App\Jobs\RecordJob  RUNNING
52	 2026-08-15 21:21:05 App\Jobs\RecordJob  4.25ms DONE
```

INFO 行は 76 桁、worker の行は 48〜52 桁。
**これは Laravel 側(termwind)の出力で、こちらでは縮められない。**
記事に貼るときは `.code` の横スクロールに任せるか、
`INFO` 行を省いて `done.log` の中身だけを見せるとよい。
**手で短く書き換えるのは禁止**なので、この事実をそのまま残す。

---

## 4. おまけ: 公式が書いている「地味だが重要な落とし穴」も実測した

公式ドキュメントにこう書いてある(原文):

> Resuming all queues does not resume queues that were
> paused individually.

「`--all` で再開しても、**個別に止めたキューは再開しない**」
という意味。これも実測した。

```
$ queue:pause database:default (個別)

 INFO Job processing on queue [database:default] has been paused. 


$ tinker (dispatch job C)
dispatched

$ queue:resume --all (全体で再開)

 INFO Job processing on all queues across all connections has been resumed. 


$ queue:work --stop-when-empty

$ cat storage/done.log
(空 = 未処理)

$ queue:resume database:default (個別に再開)

 INFO Job processing on queue [database:default] has been resumed. 


$ queue:work --stop-when-empty
 2026-08-15 21:18:16 App\Jobs\RecordJob  RUNNING
 2026-08-15 21:18:17 App\Jobs\RecordJob  3.51ms DONE

$ cat storage/done.log
C
```

**記述どおりだった。** 個別に止めたキューは `--all` では戻らず、
個別に `queue:resume database:default` を打つまで止まったまま。

運用上の注意として、これは事故になりやすい。
「全部再開したはずなのに1本だけ動いていない」が起きる。

---

## 5. 公式ドキュメントの原文(該当箇所)

`https://laravel.com/docs/13.x/queues` を curl で取得し、
該当セクションを抽出した実文:

> Laravel provides the queue:pause and queue:continue Artisan
> commands to pause and resume queue workers.

> To resume processing jobs on a paused queue, use the
> queue:continue command:
> php artisan queue:continue database:default

> To resume job processing for every queue on every connection,
> use the --all option with the queue:resume command:
> php artisan queue:resume --all

親エージェントから渡された引用と**一致した**(自分で取得して確認済み)。

---

## 6. 評価

| 論点 | 結果 |
|---|---|
| `queue:pause` は実在するか | ✅ 実在(正式名) |
| `queue:continue` は実在するか | ✅ 実在(**別名**) |
| `queue:resume` は実在するか | ✅ 実在(**正式名**) |
| どちらかが誤記か | ❌ 誤記ではない |
| ドキュメントは正しいか | ✅ 動作としては正しい |

ただし**ドキュメントの書き方には改善余地がある**:
同じページで正式名と別名を混在させ、かつ
「`queue:continue` は `queue:resume` の別名です」という
説明がどこにも無い。読者は2つ別コマンドがあると誤解する。

これは筆者の意見であって、バグではない。

### 確認できなかったこと(未確認として明記する)

**`queue:continue` という別名がいつ追加されたかは特定できなかった。**
同梱の `vendor/laravel/framework/CHANGELOG.md` は
v13.0.0(2026-03-17)〜 v13.24.0(2026-08-04)を収録しているが、
`queue:continue` に言及する項目は**1件も無い**
(`grep -i continue` が0件)。

よって「13.x のどの版で入ったか」は書かない。
別名が現行 13.25.0 に**存在すること**だけが実測済み。

---

## 7. 再現用ファイル

- `work/laravel-queue-test/` … Laravel 13.25.0 プロジェクト
- `work/laravel-queue-test/app/Jobs/RecordJob.php` … 検証用ジョブ
- `work/run_queue_test.sh` … 3-1 の再現
- `work/run_all_test.sh` … 3-2 の再現
- `work/run_scope_test.sh` … 4 の再現

- `queues.html` … 公式ドキュメントの取得物(curl, 1,824,738 bytes)

各スクリプトは冒頭で `queue:clear` と `queue:resume --all` を
実行して初期化するので、順不同で何度でも回せる。
`export COLUMNS=40` で出力幅を絞っている
(ただし前述のとおり INFO 行には効かない)。

一時停止の状態は**キャッシュ**に保存される
(`CACHE_STORE=database`)。`Worker::$pausable` の既定値は
`true`(`Worker.php:175` で実測確認)。
`config/queue.php` の追加設定は一切していない。
`.env` も `composer create-project` が生成したまま
(`DB_CONNECTION=sqlite` / `QUEUE_CONNECTION=database`)。
