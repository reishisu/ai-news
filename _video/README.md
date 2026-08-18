# デイリーダイジェストのYouTube動画パイプライン

デイリー記事から読み上げ動画(MP4)を作り、YouTubeにアップロードするための一式。
`_` 始まりなのでGitHub Pagesには公開されません。

```
記事 index.html
   │  (毎朝のデイリーセッションが、記事と一緒に原稿を書く)
   ▼
contents/<記事>/video.json      … 読み上げ原稿。書き方は _video/SCRIPT_SPEC.md
   │  python3 _render_video.py <記事>
   │    1. VOICEVOX Engine (ローカル) でナレーション合成
   │    2. サムネイルと同じデザインでスライドを撮影 (headless Chromium)
   │    3. ffmpeg (imageio-ffmpeg) で H.264+AAC の MP4 に組み立て
   ▼
_video_out/<記事>.mp4           … 完成品 (コミットしない)
_video_out/<記事>/readings.json … 読み仮名。公開前に固有名詞の読みを確認する
_video_out/<記事>/youtube.json  … タイトル・説明欄・タグ (アップロード入力)
   │  python3 _upload_youtube.py <記事>
   ▼
YouTube (privateでアップ → 人が確認して公開)
```

## 想定視聴者

**サイトの読者より広い、一般視聴者向け**（運営者の指示。2026/8/18）。
専門用語には一言説明を挟む。詳細は SCRIPT_SPEC.md。

## セットアップ

### VOICEVOX Engine（音声合成。ローカルで動く、外部送信なし）

```bash
curl -LO https://github.com/VOICEVOX/voicevox_engine/releases/download/0.25.2/voicevox_engine-linux-cpu-x64-0.25.2.7z.001
7z x voicevox_engine-linux-cpu-x64-0.25.2.7z.001 -ovv   # 展開後 約3.3GB
./vv/linux-cpu-x64/run --host 127.0.0.1 --port 50021
```

- 1.8GBのダウンロード。**リポジトリにはコミットしない**
- CPUで実時間より速く合成できることを実測済み（5.9秒の音声を3.1秒で合成。
  この環境: CPU 4コア）
- エンジンは合成のたびに起動している必要がある。`_render_video.py` は
  繋がらないときにこのREADMEを案内して止まる

### Python依存

```bash
pip install pillow imageio-ffmpeg
```

**Playwright同梱のffmpeg（/opt/pw-browsers/ffmpeg-*）は使えない。**
音声コーデックを全部外した削減ビルドで、AACもOpusも入っていない（実測）。
imageio-ffmpeg のものは libx264 + AAC 入りのフルビルド（実測）。

## 日々の運用（想定）

1. 毎朝のデイリーセッションが、記事と一緒に `video.json` を書いてコミットする
   （書き方・検証の観点は SCRIPT_SPEC.md）
2. `python3 _render_video.py <記事>` でMP4を作る
3. **公開前チェック**（サムネイルの目視確認と同じ扱い。飛ばさない）
   - `_video_out/<記事>/slide-*.png` をReadで開き、文字切れ・はみ出しを見る
   - `readings.json` で固有名詞の読みを確認する（読み間違いはここが一番早い）
4. `python3 _upload_youtube.py <記事>` で **privateアップロード**
5. YouTube Studioで人が確認して公開する

手順4-5が「自動で非公開まで・公開は人」なのは方針であり、当面は制約でもある
（下記「YouTube API側の制約」）。

## YouTube API側の制約（2026/8/18に公式ドキュメントで確認）

1. **未監査プロジェクトのアップロードは強制private。**
   videos.insert のリファレンスに「2020年7月28日以降に作成された未検証APIプロジェクト
   からアップロードされた動画は、すべてprivate視聴モードに制限される」と明記。
   解除にはコンプライアンス監査（YouTube API Services の申請フォーム）が必要
2. **OAuth同意画面が「テスト」状態だとリフレッシュトークンが7日で失効する**
   （Google Identityのドキュメントに明記）。同意画面を「本番」に公開しておくこと
   （未検証の警告は出るが、自分のアカウントで使う分には進める）
3. クォータはデフォルトで videos.insert 100回/日。1日1本なら問題ない
4. カスタムサムネイル（thumbnails.set）にはチャンネルの電話番号認証が必要

## GCP側のセットアップ（運営者のGoogleアカウントで行う）

1. https://console.cloud.google.com でプロジェクト作成
2. 「APIとサービス」→ YouTube Data API v3 を有効化
3. OAuth同意画面: External で作成し、**「本番」に公開**（テストのままだと上記2）
4. 認証情報 → OAuthクライアントID → 種類は「デスクトップアプリ」
5. 手元のPCで `python3 _upload_youtube.py --get-token` を実行し、
   表示されるURLをブラウザで開いて許可 → リフレッシュトークンが表示される
6. 環境変数に設定（定期実行ならリポジトリ/環境のSecretsに）:
   `YT_CLIENT_ID` / `YT_CLIENT_SECRET` / `YT_REFRESH_TOKEN`
7. 公開アップロードまで自動化したくなったら、監査を申請する
   （YouTube API Services - Audit and Quota Extension Form）

**`_upload_youtube.py` はこの環境では実行していない**（認証情報が無い。
アップロードもトークン取得も未実行）。APIの仕様は公式リファレンスに沿って書いたが、
初回は必ず手元で動作確認すること。

## 音声まわりの権利（2026/8/18に規約ページを取得して確認）

- **VOICEVOX利用規約**: 商用・非商用問わず利用可。ただし
  「VOICEVOXを利用したことがわかるクレジット表記」が必要。
  `youtube.json` の説明欄テンプレートに `VOICEVOX:ずんだもん` を必ず入れている
- **東北ずん子プロジェクト ガイドライン**（ずんだもんの音源元）:
  個人がYouTubeに広告を出す・スーパーチャットを受け取る程度は「非商用の範囲」。
  コピーライト表示は「なくても大丈夫」
- つまり **個人チャンネルでの収益化までは現行規約の範囲内**。
  法人化・タイアップ等に進むときは両規約を読み直すこと
- BGMは入れていない（権利確認が要るため。入れるなら規約確認してから）
- フォント(Noto Sans JP)はSIL OFLで、動画への使用は問題ない

## 実行環境の制約メモ

- この環境にGPUは無いが、VOICEVOXはCPU版で足りる（実測済み）
- Dockerデーモンは動かないので、VOICEVOXのDocker版は使えない
- リモート環境は使い捨てなので、エンジン1.8GBは毎回ダウンロードになる。
  日次自動化するならGitHub Actions + actions/cache に載せ替えるのが良い
  （このパイプラインはリポジトリに依存しないので、動画専用リポジトリへの
  切り出しも「このディレクトリと `_render_video.py` 一式のコピー」で済む）
