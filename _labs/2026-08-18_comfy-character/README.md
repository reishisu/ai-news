# ComfyUI 連携の検証（2026年8月18日）

サムネイルのキャラクターを ComfyUI に作らせる一式（`_comfy_character.py` /
`_prepare_character.py`）を、**偽の ComfyUI サーバー相手に通しで動かした記録**です。

## 何を確かめたか

| 確かめたこと | 結果 |
|---|---|
| ComfyUI のAPIの形 | 本体のソースで確認（下記） |
| ワークフローを投げて prompt_id を受け取る | 通った |
| 検証エラー（モデル名違い）の中身が読めるか | `node_errors` を日本語の見出し付きで表示できた |
| `/history` をポーリングして完了を待つ | 4秒の待ちを検知して抜けた |
| `/view` から PNG を受け取って候補に置く | 2枚受け取れた |
| 透過していない画像を弾く | 中止した（終了コード1） |
| `--matte` で単色背景を抜く | 全体の66%を透過にした。**服の中の白は残った** |
| 縦横比に合わせてサムネイルに収まる | 401×1030 → 257×660 で配置、文字幅が257px狭まった |

`output.txt` が実行結果そのものです（加工していません）。

## 何を確かめて**いない**か

- **本物の ComfyUI では動かしていません。** この環境にGPUが無く（`nvidia-smi` 無し、
  `/dev/nvidia*` 無し）、モデルも入っていないためです
- したがって、生成の品質・所要時間・VRAM使用量については何も言えません
- 偽サーバーは、下記のソースを読んで**レスポンスの形だけを真似たもの**です

## APIの根拠（一次資料）

comfyanonymous/ComfyUI の master を 2026年8月18日に取得して確認しました。

| ファイル | 確認した箇所 |
|---|---|
| `server.py` | `@routes.post("/prompt")`（リクエストとレスポンスの形、400のとき）、`@routes.get("/history/{prompt_id}")`、`@routes.get("/view")`（`filename` / `subfolder` / `type`）、`@routes.get("/object_info")` |
| `execution.py` | `history_result` の中身（`outputs`）、`task_done()` が入れる `status`（`status_str` / `completed` / `messages`） |
| `nodes.py` | `SaveImage.save_images()` の戻り値 `{"ui": {"images": [{"filename","subfolder","type"}]}}` |

## 動かし方

```bash
bash _labs/2026-08-18_comfy-character/run_all.sh
```

偽サーバーを立て、1〜6を実行し、最後にダミーを消してサムネイルを撮り直します
（**リポジトリは元の状態に戻ります**。実際、撮り直したPNGは元のものと同一でした）。

## ファイル

| ファイル | 中身 |
|---|---|
| `fake_comfy.py` | ComfyUI のAPIだけを真似た偽サーバー。白背景の人型ダミーPNGを返す |
| `lab_recipe.json` | 偽サーバーに入っているモデル名を指した recipe |
| `bad_recipe.json` | 存在しないモデル名を指した recipe（400の確認用） |
| `run_all.sh` | 通しで動かす |
| `output.txt` | 実行結果（`COLUMNS=40`） |

## 実行環境

- Python 3.11.15 / Pillow 12.3.0（`pip install pillow` で導入）
- CPU 4コア / メモリ 15GB / **GPU 無し**
- Chromium は `/opt/pw-browsers/chromium`（サムネイル撮影に使用）
