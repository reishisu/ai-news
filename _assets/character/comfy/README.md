# ComfyUI でキャラクターを作る

**ComfyUI はGPUのある手元のPCで動かしてください。** この記事サイトの実行環境にGPUは無く、
生成はできません（`nvidia-smi` 無し、CPU 4コア）。`_comfy_character.py` は
「動いている ComfyUI にHTTPで投げて、出てきたPNGを受け取る」だけです。

```
recipe.json          # 何を作るか（モデル・プロンプト・seed・キャラ一覧・ポーズ一覧）
character.api.json   # 標準ノードだけの txt2img ワークフロー（--dump-workflow で書き出したもの）
```

---

## 1. まず素の txt2img で「顔」を決める

```bash
python3 _comfy_character.py --check --url http://127.0.0.1:8001   # つながるか・モデルはあるか
python3 _comfy_character.py --url http://127.0.0.1:8001           # cast 全員 × ポーズ全種
```

`_assets/character/_candidates/<キャラ名>/<ポーズ名>.png` に落ちます。

一部だけ作り直すとき:

```bash
python3 _comfy_character.py --who hinata                 # このキャラだけ
python3 _comfy_character.py --pose wave                  # このポーズだけ
python3 _comfy_character.py --who hinata --seed-offset 100   # 気に入らないので振り直す
```

seed は「そのキャラの seed ＋ ポーズの並び順」です。乱数は使わないので、
**同じ recipe なら何度でも同じ絵**が出ます。

---

## 2. 顔を揃えたいなら IPAdapter を入れる

**素の txt2img では、ポーズや衣装を変えると顔も少しずつ変わります。** タグと seed を
固定してもドリフトします。基準の1枚を参照させて揃えるのが IPAdapter です。

> 以下は配布元の README（`cubiq/ComfyUI_IPAdapter_plus`）を読んで書いています。
> **この環境では実行できないため、動作確認はしていません。**

### 入れるもの

ノード本体は ComfyUI-Manager から入れられます（`ComfyUI/custom_nodes/` に直接
clone してもよい）。配布元は「IPAdapter は常に最新の ComfyUI を要求する」としています。

モデルは手で置きます。**名前が合っていないと Unified Loader が見つけられません。**

| 置き場所 | ファイル |
|---|---|
| `ComfyUI/models/clip_vision` | `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`（h94/IP-Adapter の `models/image_encoder/model.safetensors` を落としてリネーム） |
| `ComfyUI/models/ipadapter` | `ip-adapter-plus-face_sdxl_vit-h.safetensors`（顔を寄せる用。SDXL系はこれか `ip-adapter-plus_sdxl_vit-h.safetensors`） |

Unified Loader は固定のファイル名ではなく**正規表現**で探します（配布元 `utils.py` の
`get_clipvision_file()` / `get_ipadapter_file()`）。PLUS FACE ＋ SDXL のときはこうです。

| 種類 | パターン |
|---|---|
| clip_vision | `(ViT.H.14.*s32B.b79K|ipadapter.*sd15|sd1.?5.*model)\.(bin|safetensors)` |
| ipadapter | `plus.face.sdxl.vit.h\.(safetensors|bin)$` |

**ここでハマりやすいのがサブフォルダです。** リポジトリごと落とすと
`CLIP-ViT-H-14-laion2B-s32B-b79K\model.safetensors` のような名前になり、
末尾が `b79K.safetensors` でないためパターンに合いません（実機で発生）。
`models/clip_vision/` の直下に、上の名前で置いてください。

配布元は「まず `weight` を 0.8 以下に下げ、ステップ数を増やすとよい。プロンプトへの
追従を上げたいなら `IPAdapter Advanced` の weight type を変える」としています。

### 入っているか確かめる

```bash
python3 _comfy_character.py --check --url http://127.0.0.1:8001
```

ノードの有無と、上の2つのモデルが見えているかを表示します。
**ノードだけ入れてもモデルが無いと動きません。**

### 手順（ワークフローを組む必要はありません）

以前はここに「ComfyUI の画面でノードを組んで API形式で書き出す」手順がありましたが、
**その作業は無くしました。** ワークフローは `_comfy_character.py` が組み立てて投げます。
打つのはこれだけです。

```bash
git pull
python3 _comfy_character.py --face --url http://127.0.0.1:8001
```

これで **cast 全員 × 全ポーズ（5人×5種=25枚）** を、それぞれの基準の顔に
寄せながら作り直します。1人あたり基準にするのは、いま採用されている
`_assets/character/cast/<キャラ名>/wave.png` です（自動で選ばれます）。

投げる前に、相手の ComfyUI に必要なノードとモデルが揃っているかを確かめ、
足りなければ**何が無いのかを日本語で表示して止まります**（400 の英語を読む必要はありません）。

#### 中で何が起きているか

組み立てているのは、素の txt2img に IPAdapter を1つ挟んだだけの形です。

```
チェックポイント読込 ─┬→ IPAdapterUnifiedLoader → IPAdapter → KSampler → VAE → 保存
                      └→ プロンプト(肯定/否定) ──────────────────↗
基準の顔(LoadImage) → PrepImageForClipVision(頭側を切り出す) ──↗
```

- 基準の顔は `POST /upload/image` で ComfyUI に送ってから使います
- `PrepImageForClipVision` を挟むのは、基準が**全身の立ち絵**だからです。
  IPAdapter は画像を正方形にして読むため、全身のまま渡すと顔の情報が薄まります。
  `crop_position="top"` で頭の側だけを渡しています
- preset は `PLUS FACE (portraits)`、weight は 0.8
  （配布元が「まず 0.8 以下に下げるとよい」としている値）

#### 思いどおりにならないときの調整

| 症状 | やること |
|---|---|
| **縞模様や色の壊れた絵が出る** | 基準が透過PNGのときに起きます（実機で発生）。いまは `--face` が自動で白背景に埋めるので、`git pull` して再実行してください（合成に Pillow が要ります） |
| 顔は揃ったがポーズ指示が効かなくなった | `--weight 0.6` のように下げる（プロンプトが勝つようになる） |
| まだ顔がばらつく | `--weight 1.0` のように上げる |
| 1人だけやり直したい | `--face --who hinata` |
| 基準の顔を変えたい | `--face --reference <その画像> --who hinata`、または recipe の cast に `"face": "point"` のようにポーズ名を書く |
| 構図ごと変えたい | `--seed-offset 100` で振り直す（顔は基準に寄ったまま） |

できた候補は `_assets/character/_candidates/<キャラ名>/<ポーズ名>.png` に入ります。
よければ push してください（取り込みと撮り直しはクラウド側でできます）。

```bash
git add -f _assets/character/_candidates/
git commit -m "顔を揃えた候補" && git push
```

#### 自分で組んだワークフローを使いたいとき（上級者向け・任意）

独自のノード構成（LoRA を挟む等）を使いたいときだけ、ComfyUI の画面で組んで
**「ワークフロー → API形式でエクスポート」**（UI形式ではありません）した JSON を渡します。

```bash
python3 _comfy_character.py \
  --workflow ipadapter.api.json \
  --reference _assets/character/cast/hinata/wave.png \
  --who hinata
```

`--workflow` を渡すと、JSON の中の次の4つを今回の値に差し替えてから投げます。

| ノード | 差し替えるもの |
|---|---|
| `KSampler` | `seed` |
| `EmptyLatentImage` / `EmptySD3LatentImage` | `width` / `height` |
| `CLIPTextEncode` | プロンプト（KSampler の positive / negative の繋がりを見て、どちらかを判定） |
| `LoadImage` | `--reference` で渡した画像（`POST /upload/image` で ComfyUI に送ってから差し込む） |

---

## 3. 選んで取り込む

```bash
python3 _prepare_character.py \
  _assets/character/_candidates/hinata/wave.png --cast hinata --as wave --rembg
```

**`--rembg` を使ってください。** ComfyUI の素の出力には床の影が入ることが多く、
`--matte`（単色の塗りつぶし）では影と、脚の間のように囲まれた白が残ります（実測）。

`_assets/character/cast/<キャラ名>/<ポーズ名>.png` に入り、記事の日付で自動的に選ばれます。
詳しくは1つ上の階層の `README.md` を見てください。

---

## 日次の自動処理には組み込みません

サムネイル生成（`_render_thumbs.py`）は置いてある画像を読むだけで、生成は一切しません。
朝5時の無人実行で、誰も確認していない絵が公開されるのを避けるためです。
