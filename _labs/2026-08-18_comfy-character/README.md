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
| `/view` から PNG を受け取って候補に置く | キャラ2人 × ポーズ2種 = 4枚受け取れた |
| 手元で書き出したワークフローへの差し替え | seed / サイズ / 肯定 / 否定 / 参照画像 の5つを差し替えられた |
| 参照画像を `POST /upload/image` で送る | 送って LoadImage に差し込めた（IPAdapter で顔を揃えるときの経路） |
| IPAdapter が入っているかの判定 | 無い / ノードだけ / モデルもある の3状態を出し分けられた |
| `--face`（顔揃え。ワークフローをこちらで組む） | 事前検証 → 参照画像の送信 → 生成 → 受け取りまで通った |
| IPAdapter が無いサーバーへの `--face` | 足りないノード3つを日本語で列挙して中止した（終了コード1） |
| 透過していない画像を弾く | 中止した（終了コード1） |
| `--matte` で単色背景を抜く | 全体の66%を透過にした。**服の中の白は残った** |
| 縦横比に合わせてサムネイルに収まる | 401×1030 → 257×660 で配置、文字幅が257px狭まった |
| カテゴリごとに担当キャラが選ばれる | デイリー3本はすべて hinata、担当未設定のカテゴリは日替わりで回った |
| 同じキャラの中でポーズが日替わりになる | 8/18 は point、8/17 は wave、8/16 は point（連続する日は別） |

`output.txt` が実行結果そのものです（加工していません）。

## 何を確かめて**いない**か

- **本物の ComfyUI では動かしていません。** この環境にGPUが無く（`nvidia-smi` 無し、
  `/dev/nvidia*` 無し）、モデルも入っていないためです
- したがって、生成の品質・所要時間・VRAM使用量については何も言えません
- 偽サーバーは、下記のソースを読んで**レスポンスの形だけを真似たもの**です
- **IPAdapter は動かしていません。** カスタムノードもモデルも入っていないので、
  確認したのは「ワークフローJSONの差し替え」と「参照画像の送信」までです

## 実機で起きた失敗（運営者の環境から報告されたもの）

**透過PNGを IPAdapter の基準に渡すと、縞模様や色の壊れた絵が出る。**
`--face` の初回実行で、髪と靴が青白の縞になった破綻画像が生成された。
基準にした `cast/hinata/wave.png` は rembg で背景除去済みの透過PNGで、
ComfyUI の LoadImage は RGB に変換するだけなので、透明部分の下に残った色が
そのまま参照に入ったためと考えられる。対処として `--face` は基準を
白背景に合成してから送るようにした（`flatten_reference()`。要 Pillow）。

## 背景除去モデルの選定（この環境で実測して決めた）

運営者から「切り抜きが雑」（外周の白いモヤ／髪と肩の間に囲まれた背景が残る）と
指摘を受け、3つを同じ画像で比較した。

| モデル | 外周 | 囲まれた背景(髪と肩の間など) | 白い服 | 速度(CPU) |
|---|---|---|---|---|
| u2net | 白いモヤが残る | 残る | 無傷 | 1.2秒/枚 |
| isnet-anime | 綺麗 | **残る** | 無傷 | 3.2秒/枚 |
| birefnet-general | 綺麗 | **抜ける** | **無傷** | 83秒/枚。ただし推論中に約14GB使い、**2枚目でOOMに殺された**(dmesgで確認) |
| **birefnet-general-lite(採用)** | 綺麗 | **抜ける** | **無傷** | 53秒/枚・約7.6GB。品質は general と見分けが付かなかった |

途中で「囲まれた背景を色で判別して消す」処理（`drop_pools`）も書いたが、**撤去した**。
測ってみると、囲まれた池も白衣の平坦部も**同じ色**（平均253〜254、標準偏差1.5未満）で、
色では原理的に区別できず、白衣に穴が開いた。低レベルな色ではなく境界の意味を見る
モデル（BiRefNet）でしか解けない問題だった。

文字側も同時に直した:
- 行間1.05のまま `overflow:hidden` で囲っていたため、**最終行の下端と縁取りが
  毎回数px切られていた**（黒帯があった頃はその位置に帯が重なって見えなかった）。
  padding をはみ出し側に確保して解消
- 発光（`drop-shadow(0 0 22px …)`）は輪郭がぼやけて見えるため外した（運営者の指摘）

## 実機での所要時間（運営者の環境から報告された値）

**この環境で測ったものではありません。** 手元のPCで実行した結果を貼ってもらったものです。

| 条件 | 値 |
|---|---|
| GPU | NVIDIA GeForce RTX 3070 Ti（ComfyUI の表示で VRAM 7GB） |
| モデル | JANKU Trained + Chenkin & NoobAI v7.77（SDXL系） |
| 生成設定 | 768×1344 / 30ステップ / CFG 5 / Euler a / scheduler normal |
| 1枚あたり | **14〜22秒**（25枚で420秒、平均16.8秒） |
| 出力PNG | 424KB〜690KB |

キャラ5人 × ポーズ5種の25枚が7分で揃う計算です。

## サムネイル全数検査の結果（2026/8/18・サブエージェント6班）

25記事＋再検3の全サムネイルを、拡大込みで検査した。文字系の指摘は**すべて修正済み**。

| 系統 | 件数 | 状態 |
|---|---|---|
| 補足2行時のレイアウト衝突(下端切れ・札との重なり) | 5枚 | **修正済み**。高さ予算の数え漏れ(隙間8pxを6px、フッター46pxを40px、下地padding未計上)が原因 |
| 溢れた行の断片が覗く | 1枚 | **修正済み**。padding方式が line-clamp と干渉していた。行間1.16に広げる方式へ |
| 泣き別れ(GLM- / 5.3 など) | 1枚 | **修正済み**。line-break:strict + 英数トークンの nowrap。auto-phrase(文節折り)も試したが、行が埋まらず「…」潰れが7枚出たので **word-break:normal** に落ち着いた |
| タイトルが「…」で潰れる | 1枚 | **修正済み**。meta.json の thumb で決め文句を指定(hooks-guardrails) |
| **囲まれた背景の白の取り残し** | 8枚 | **既知・未修正**。白背景では原理的に取り切れない。**緑背景での再生成で解消する**(recipe変更済み) |
| 素材由来(Tシャツの文字化け・にじみ等) | 6枚 | 既知・未修正。再生成で入れ替わる |
| 同日同カテゴリの3記事が同じ絵 | 3枚 | 仕様(日付決定・乱数なし)。気になるなら要検討 |

取り残しが残る記事: 2026-08-14_001 / _002 / ai-basics / hooks-guardrails / loop-graph /
2026-08-16_001 / 17_001 / 18_001（いずれも髪・腕とからだの間の閉じた領域）。

## APIの根拠（一次資料）

comfyanonymous/ComfyUI の master を 2026年8月18日に取得して確認しました。

| ファイル | 確認した箇所 |
|---|---|
| `server.py` | `@routes.post("/prompt")`（リクエストとレスポンスの形、400のとき）、`@routes.get("/history/{prompt_id}")`、`@routes.get("/view")`（`filename` / `subfolder` / `type`）、`@routes.post("/upload/image")`（multipart の `image` / `type` / `subfolder` / `overwrite` と、戻り値の `name` / `subfolder` / `type`）、`@routes.get("/object_info")` |
| `execution.py` | `history_result` の中身（`outputs`）、`task_done()` が入れる `status`（`status_str` / `completed` / `messages`） |
| `nodes.py` | `SaveImage.save_images()` の戻り値 `{"ui": {"images": [{"filename","subfolder","type"}]}}`、`CLIPVisionLoader` の入力 `clip_name` |
| `cubiq/ComfyUI_IPAdapter_plus` の `IPAdapterPlus.py` | `IPAdapterUnifiedLoader` の `preset`、`IPAdapterModelLoader` の `ipadapter_file`（`--check` が見る項目） |

## 動かし方

```bash
bash _labs/2026-08-18_comfy-character/run_all.sh
```

偽サーバーを立て、1〜6を実行し、最後にダミーを消してサムネイルを撮り直します
（**リポジトリは元の状態に戻ります**。実際、撮り直したPNGは元のものと同一でした）。

## ファイル

| ファイル | 中身 |
|---|---|
| `fake_comfy.py` | ComfyUI のAPIだけを真似た偽サーバー。白背景の人型ダミーPNGを返す。`/upload/image` も受ける |
| `lab_recipe.json` | 偽サーバーに入っているモデル名を指した recipe |
| `bad_recipe.json` | 存在しないモデル名を指した recipe（400の確認用） |
| `cast_recipe.json` | キャラ2人 × ポーズ2種の recipe（本番と同じ形。名前は labhina / labkuru で、**本物の cast と衝突しない**） |
| `ipadapter_like.api.json` | 手元で書き出したワークフローの代わり。LoadImage を含む |
| `run_all.sh` | 通しで動かす |
| `output.txt` | 実行結果（`COLUMNS=40`） |

## 実行環境

- Python 3.11.15 / Pillow 12.3.0（`pip install pillow` で導入）
- CPU 4コア / メモリ 15GB / **GPU 無し**
- Chromium は `/opt/pw-browsers/chromium`（サムネイル撮影に使用）
