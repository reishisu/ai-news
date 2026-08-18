# 検証記録: デイリーダイジェストのYouTube動画パイプライン

2026年8月18日。この環境(リモート実行環境)で実際に動かして確かめた記録。
成果物は `_render_video.py` / `_upload_youtube.py` / `_video/`。

## 何を確かめたか

### 1. Playwright同梱のffmpegでは音声付き動画が作れない

```
$ /opt/pw-browsers/ffmpeg-1011/ffmpeg-linux -version
ffmpeg version n7.0.1-playwright-build-1011
configuration: ... --disable-everything --enable-muxer=webm --enable-libvpx ...
```

`-encoders` の一覧に音声エンコーダが1つも無い(vp8とpngのみ)。
スクリーンキャスト専用の削減ビルドのため。

### 2. imageio-ffmpeg(pip)のffmpegはフルビルド

```
$ pip install imageio-ffmpeg
$ ffmpeg-linux-x86_64-v7.0.2 -encoders | grep -E 'libx264|aac|libopus'
 V....D libx264   / A....D aac / A....D libmp3lame / A....D libopus
```

H.264 + AAC が使えるので、YouTube推奨のMP4をこれで組み立てる。

### 3. VOICEVOX EngineはこのCPU環境で実時間より速い

- voicevox_engine 0.25.2 linux-cpu-x64 (1.8GBの.7z、展開後3.3GB)
- CPU 4コア / メモリ15GB。GPUなし
- 起動後、35文字・5.87秒ぶんの合成が3.1秒(audio_query + synthesis)
- 5.1分の動画(ナレーション約1800字、10スライド)の合成+撮影+エンコードが
  通しで数分で終わる

### 4. スライドの語中改行は auto-phrase で直る

`overflow-wrap:anywhere` だと「レビュ/ー」「イン/ジェクション」のような
語中改行が出る(スモークテストのスクリーンショットで確認)。
`word-break:auto-phrase; line-break:strict` に替えると文節で折れる。
これはサムネイル(`_HANDOFF.md` 第5節)で実証済みの組み合わせと同じ。

### 5. YouTube API側の制約(公式ドキュメントを取得して確認)

- videos.insert: 未検証APIプロジェクト(2020/7/28以降作成)からのアップロードは
  **強制的にprivate**。解除は監査申請(リファレンスの注記)
- クォータ: デフォルトで videos.insert は100回/日(getting-startedページ)
- OAuth: 同意画面が「テスト」状態のExternalアプリのリフレッシュトークンは
  **7日で失効**(Google Identityのドキュメント)
- → 運用は「自動でprivateアップ→人が確認して公開」から始める。
  これは _HANDOFF.md 第2節の「無人実行で誰も見ていないものを公開しない」とも一致

### 6. 音声の権利(規約ページを取得して確認)

- VOICEVOX利用規約: 商用可、「VOICEVOXを利用したことがわかるクレジット表記」が必要
- 東北ずん子プロジェクト ガイドライン: 個人がYouTubeに広告を出す・スパチャを
  受け取る程度は「非商用の範囲」、コピーライト表示は「なくても大丈夫」
- → 説明欄テンプレート(`youtube.json`)に `VOICEVOX:ずんだもん` を必ず入れる

## 動かし方(再現手順)

```bash
# 1. VOICEVOX Engine (初回のみダウンロード)
curl -LO https://github.com/VOICEVOX/voicevox_engine/releases/download/0.25.2/voicevox_engine-linux-cpu-x64-0.25.2.7z.001
7z x voicevox_engine-linux-cpu-x64-0.25.2.7z.001 -ovv
./vv/linux-cpu-x64/run --host 127.0.0.1 --port 50021 &

# 2. 依存
pip install pillow imageio-ffmpeg

# 3. レンダリング(video.json は事前に書いてあること)
python3 _render_video.py 2026-08-18_001
```

## 実行していないこと(正直に)

- `_upload_youtube.py` は**一度も実行していない**(認証情報が無い)。
  トークン取得(--get-token)も未実行。公式リファレンスに沿って書いたのみ
- 実際のYouTubeチャンネルでの表示・音量感は未確認
- BGM・字幕(キャプション)は未実装

## 環境

- リモート実行環境 (Linux 6.18.5, CPU 4コア, GPUなし)
- Python 3.11.15 / Pillow(pip) / imageio-ffmpeg 7.0.2 / p7zip(apt)
- Chromium: /opt/pw-browsers/chromium (ビューポート補正87px、_render_thumbs.py の実測と一致)
- voicevox_engine 0.25.2 linux-cpu-x64
