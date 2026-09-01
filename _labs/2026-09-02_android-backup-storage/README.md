# Androidバックアップ保存容量変更の確認記録

## 何を確かめたか

- Google Oneの公式告知、Google Oneヘルプ、日本語報道、案内メールを扱った報道を保存し、記事中の事実を出所ごとに分けた。
- Android 15のPixel Tabletエミュレータで、Googleのバックアップ画面までの経路と表示を確認した。
- Google Oneの公式告知とヘルプをブラウザで開き、記事で参照する箇所を確認した。

公式告知には「45日」も「40MB」も書かれていない。「45日」はPC Watchが伝えた案内メール、「約40MB」はAndroid Authorityが伝えたGoogleの説明を根拠にする。

## 撮影環境と方法

### Androidエミュレータ

- ヘッドレスのAndroidエミュレータを使用した。端末プロファイルはPixel Tablet、API 35、Android 15、日本語、Googleアカウント未サインイン。
- `path_backup.sh` で `adb`、`uiautomator`、`input` を使い、設定からGoogleのバックアップ画面まで移動した。
- 操作は別途 `adb screenrecord` で録画した。`path_backup.sh` 自体には録画コマンドを含めていない。
- 記事に使う確認用静止画として、画面上部と「バックアップの詳細」を `shots/` に保存した。

未サインインのため、容量ゲージと、データ種別・アプリごとの切り替えはこの環境では見ていない。

### 公式ページ

- `rec_web.py` でGoogle Oneの公式告知とGoogle OneヘルプをPlaywrightのChromiumでheadless表示し、トップとスクロール後を録画・撮影した。
- `rec_help.py` でGoogle Oneヘルプの「容量を使用するファイル」を展開し、「Android デバイスのバックアップ」まで移動する操作をPlaywright headlessで録画・撮影した。
- 両スクリプトはPlaywrightの `record_video_dir` を使い、実行時の録画先を `takes/2026-09-02_android-backup-storage/` に設定している。録画ファイルは現在このリポジトリには残しておらず、確認用の静止画だけを `shots/` に保存している。

PlaywrightとChromiumの詳細なバージョン番号は記録していない。

## 再実行

Androidエミュレータを起動し、`adb` から接続できる状態で実行する。

```bash
bash path_backup.sh
```

公式ページの録画と静止画取得は、PlaywrightとChromiumを利用できる環境で実行する。

```bash
python rec_web.py
python rec_help.py
```

スクリプトの出力先は `takes/2026-09-02_android-backup-storage/`。記事の検証記録として残す静止画は `shots/` に置く。

## `sources/` の中身

- `androidauthority_2026-07-07_policy.txt` — 平均の増加量と、Googleフォトの写真・動画が以前から容量に数えられていたことを確認した抜粋。
- `androidauthority_2026-07-20_email.txt` — 容量超過時の自動バックアップ停止、個人ごとの見込み増加量、Android 9以降のコントロールを確認した抜粋。
- `google_one_thread_451067756_en.txt` — Community Manager MonikaによるGoogle One公式告知の保存本文。
- `help_9004014_ja_android_section.txt` — Google Oneヘルプの「Android デバイスのバックアップ」部分の抜粋。
- `help_9004014_ja_page.txt` — Google Oneヘルプ全体の保存本文。記事ではこのうち「既存の保存容量」と「Android デバイスのバックアップ」の箇所だけを参照した。
- `pcwatch_2026-07-17.txt` — 日本のアカウントへの案内、メールから45日後の適用、Android 9以降の切り替えを確認した抜粋。

## `shots/` の中身

- `emulator_backup_page_top.png` — 未サインインのバックアップ画面上部。「バックアップ」「ON にする」を記録。
- `emulator_backup_page_detail.png` — 「バックアップの詳細」「写真と動画」「その他のデバイスデータ」を記録。
- `google_one_thread_top.png` — Google One公式告知の上部。投稿者、役割、投稿日、見出しを記録。
- `google_one_thread_scrolled.png` — Google One公式告知のスクロール後。最終編集日の表示を記録。
- `help_9004014_ja_top.png` — Google Oneヘルプの上部を記録。
- `help_9004014_ja_scrolled.png` — Google Oneヘルプをスクロールした状態を記録。
- `help_9004014_ja_backup.png` — 「容量を使用するファイル」を展開し、「Android デバイスのバックアップ」を表示した状態を記録。

## やっていないこと

- Googleアカウントへサインインした後の容量ゲージと、項目別・アプリ別の切り替えは撮っていない。
- 案内メールの原文は自分では受け取っていない。メールの内容はPC WatchとAndroid Authorityの保存済み抜粋で確認した。
- 録画ファイルは現在このリポジトリには保存していない。
