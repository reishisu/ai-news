# debounce の再現手順

Laravel のひな形そのものはコミットしていません（`composer create-project` で
毎回同じものが取れるうえ、90ファイル増えて差分が読めなくなるため）。
ここに置いてあるのは**この検証のために書いたファイルだけ**です。

```bash
export COMPOSER_ALLOW_SUPERUSER=1
composer create-project laravel/laravel app --no-interaction
cp -r app/Events app/Listeners app/Console ../app/app/      # ここのファイルを流し込む
cp run_all.sh ../app/

cd ../app
sed -i 's/^QUEUE_CONNECTION=.*/QUEUE_CONNECTION=database/' .env
sed -i 's/^CACHE_STORE=.*/CACHE_STORE=file/' .env
php artisan migrate --force
./run_all.sh
```

`output.txt`（記事に貼ったもの）と同じ結果になれば再現できています。

## 何を確かめる構成か

- `ProductUpdated` → `UpdateProductSearchIndex`（`#[DebounceFor(3)]` あり）
- `ProductUpdatedPlain` → `PlainSearchIndex`（属性なし。比較用）
- `ProductUpdatedBoth` → `BothAttributes`（`DebounceFor` と `ShouldBeUnique` を併用。例外を出す用）

イベントを分けてあるのは、Laravel のリスナー自動検出が `app/Listeners` を
全部拾ってしまい、1つのイベントだと両方のリスナーが動いてしまうためです。

`demo:debounce` が4秒待つのは、debounce されたジョブが `debounceFor` 秒だけ
遅延して積まれるからです。待たずに `queue:work --stop-when-empty` を流すと
**まだ実行可能になっていないので実行0回**になります（最初これで嵌まりました）。

## 実行時の環境

- Laravel Framework 13.26.1 / PHP 8.4.19 / Composer
- SQLite、1プロセス。**複数コンテナでの検証はしていません**
