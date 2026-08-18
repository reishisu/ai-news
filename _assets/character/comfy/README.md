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

モデルは手で置きます。**ファイル名を下記のとおりにしないと Unified Model Loader が認識しません。**

| 置き場所 | ファイル |
|---|---|
| `ComfyUI/models/clip_vision` | `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`（h94/IP-Adapter の `models/image_encoder/model.safetensors` を落としてリネーム） |
| `ComfyUI/models/ipadapter` | `ip-adapter-plus-face_sdxl_vit-h.safetensors`（顔を寄せる用。SDXL系はこれか `ip-adapter-plus_sdxl_vit-h.safetensors`） |

配布元は「まず `weight` を 0.8 以下に下げ、ステップ数を増やすとよい。プロンプトへの
追従を上げたいなら `IPAdapter Advanced` の weight type を変える」としています。

### 入っているか確かめる

```bash
python3 _comfy_character.py --check --url http://127.0.0.1:8001
```

ノードの有無と、上の2つのモデルが見えているかを表示します。
**ノードだけ入れてもモデルが無いと動きません。**

### 手順

1. ComfyUI の画面で、txt2img のワークフローに IPAdapter のノードを足して組む
   （`Load Image` → IPAdapter → `KSampler` の model 経路に挟む形）
2. 画面で1回動かして、狙いどおり顔が寄ることを確かめる
3. **「ワークフロー → API形式でエクスポート」** で JSON を書き出す（UI形式ではありません）
4. その JSON を渡して回す

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
  _assets/character/_candidates/hinata/wave.png --cast hinata --as wave --matte
```

`_assets/character/cast/<キャラ名>/<ポーズ名>.png` に入り、記事の日付で自動的に選ばれます。
詳しくは1つ上の階層の `README.md` を見てください。

---

## 日次の自動処理には組み込みません

サムネイル生成（`_render_thumbs.py`）は置いてある画像を読むだけで、生成は一切しません。
朝5時の無人実行で、誰も確認していない絵が公開されるのを避けるためです。
