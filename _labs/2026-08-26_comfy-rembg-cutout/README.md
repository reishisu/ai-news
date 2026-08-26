# 検証記録: ComfyUI生成 → rembg切り抜き パイプライン

記事 `contents/2026-08-26_comfy-rembg-cutout/` の全数値の出どころ。
測定は 2026/8/25〜8/26 に、この開発リポジトリの実データ
（`_assets/character/_review/` の80枚、832×1216、黒背景）に対して行った。

## 実行環境

- コンテナ: Linux / Intel Xeon 2.10GHz 4コア / RAM 16GB / **GPUなし**
- Python 3.11.15 / rembg 2.0.81 / onnxruntime 1.29.0 / numpy 2.4.6 /
  scipy 1.17.1 / Pillow 12.3.0
- モデル(~/.rembg/models に自動DL):
  birefnet-general-lite.onnx **224,005,088 bytes** / isnet-anime.onnx **176,069,933 bytes**
- 生成側(ComfyUI + JANKU v7.77)は運営者の手元PC。このコンテナからはHTTP APIで
  投げた記録(`gen_operator_log.txt`)だけを解析した

## ファイル一覧（→ 記事のどの主張の根拠か）

### 生成（キューの詰まり）

| ファイル | 中身 |
|---|---|
| `gen_operator_log.txt` | 運営者が実行した180枚生成のログ(PowerShell貼り付け、無加工) |
| `gen_log_stats.py` | 上のログを数える。`python3 gen_log_stats.py gen_operator_log.txt` |
| `gen_stats_output.txt` | 実行結果。**総経過15.3h / 速い側だけなら1.4h / 諦めた22回で11.0hを捨てた / 諦めた直後の1枚は8回中8回が60秒超**。偽ComfyUI相手の新旧比較(repro)も含む |
| `_src_comfy_main.py` | ComfyUI本体 main.py（一次資料）。`prompt_worker` が**1本だけ**のスレッドで起動される(L350, L559) |
| `_src_comfy_server.py` | ComfyUI server.py（一次資料）。`POST /interrupt` が `prompt_id` を受け、実行中のものと一致した時だけ中断(L1160〜) |
| `_src_comfy_cli_args.py` | ComfyUI cli_args.py（一次資料）。`--lowvram` の原文(L170) |

※ 詰まりの再現一式(偽ComfyUIサーバー・repro)は `_labs/2026-08-25_comfy-stall/` にある。

### 切り抜き（各事故の実測）

| ファイル | 中身 |
|---|---|
| `stage3.py` | 段階別の「明るい(>55)画素の欠け」。rembg → 補助 → drop_islands の各段が何pxを消すか |
| `dist2.py` | drop_islands が消す塊の**大きさと本体からの距離**。切れた体の一部は1〜20px、装飾は50〜110px |
| `model_diff.py` / `isnet_diff_output.txt` | birefnet と isnet-anime の画素単位の差分。isnet が残す背景 **合計565,472px・73枚に400px以上の塊**(最大 hinata/celebrate 62,682px) |
| `union3.py` / `union3_output.txt` | 2モデル合成のしきい値スイープ(55〜150)。**100で「暗い画素の巻き込み」が0になる** |
| `union2.py` / `union2_output.txt` | **失敗した案**: 背景から自動でしきい値を決める → birefnetが消した髪(明るさ254)が背景見本に混ざり、しきい値266まで上がる循環 |
| `fix_check.py` | alpha だけ戻すと髪が真っ黒になる事故の修正確認。不透明画素の平均RGB差 25.75 → **1.81** |
| `grow.py` | dark_assist の広がり上限スイープ(2/4/8/16/32/無制限)。**無制限だけが消す画素を2〜4倍にする** |
| `arm_gap_check.py` / `arm_gap_output.txt` | **使えなかった指標の記録**。「囲まれた透明」は修復すると増える方向にも動く(ファイル冒頭の注記を読むこと) |
| `mem2.py` / `mem_arena_off_output.txt` | onnxruntime の CPU アリーナを切った時のRSS。**両モデルで1,014MiB・出力のalpha差は0**。既定(アリーナ有り)は birefnet 2推論で12,186MiB → isnet追加で13,611MiB(mem_arena_off_output.txt 冒頭コメントと記事本文参照) |
| `cutout_chunk.py` | 80枚一括の切り抜きドライバ(範囲指定可)。モデルのセッションを使い回す |
| `recut_final_log.txt` | 最終パイプラインでの80枚切り直しログ。1枚18〜28秒(中央20秒)、isnet補完が動いたのは**7枚** |
| `measure_cast.py` / `measure_cast_output.txt` | 最終 cast/ の監査。**本当の穴1枚(hinata/money 4,516px)・RGB差 最大2.12/中央値1.47** |
| `make_evidence.py` | 記事の前後比較画像を git 履歴の実物から組み立てる(画素は無加工) |

### 一次資料（2026/8/26 取得）

| ファイル | URL |
|---|---|
| `_src_ort_api.html` | https://onnxruntime.ai/docs/api/python/api_summary.html — `enable_cpu_mem_arena` の定義 |
| `_src_rembg_readme.md` | https://cdn.jsdelivr.net/gh/danielgatis/rembg@main/README.md — モデル一覧 |
| `_src_comfy_main.py` | https://cdn.jsdelivr.net/gh/comfyanonymous/ComfyUI@master/main.py |
| `_src_comfy_server.py` | https://cdn.jsdelivr.net/gh/comfyanonymous/ComfyUI@master/server.py |
| `_src_comfy_cli_args.py` | https://cdn.jsdelivr.net/gh/comfyanonymous/ComfyUI@master/comfy/cli_args.py |

（github.com はこの環境から403のため、jsdelivr のCDN経由で取得した）

## 再実行するときの注意

- `measure_cast.py` `arm_gap_check.py` `make_evidence.py` は数分で終わる
- `stage3.py` `dist2.py` `grow.py` は birefnet の推論を含むので**1本あたり数分〜十数分**
- `union3.py` `model_diff.py` は isnet の推論結果(.npy キャッシュ)を前提にしていた。
  キャッシュ無しで回すと isnet 80枚ぶんの推論が先に走る
- 一括で回すときはアリーナを切ること。**既定のままだと13.6GiBまで伸びてOOMで死ぬ**
  （このリポジトリの `_prepare_character.py` は `rembg_session()` で対処済み）
- 測るときは**明るい画素の欠けと暗い画素の欠けを両方**見ること。
  今回の記事の主要な見逃しは全部「明るい側しか測っていなかった」ことが原因
