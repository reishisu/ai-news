# サムネイルのキャラクター

サムネイルの右側に置くキャラクターです。**画像を置くだけで入ります**（コード変更は不要）。
置いていない間はキャラ無しで組まれ、文字が広く使われます。

## 置き方は2つ

### A. カテゴリごとに担当を決めて、ポーズを日替わりにする（いまの形）

```
_assets/character/cast/<キャラ名>/<ポーズ名>.png
_assets/character/cast/cast.json        # カテゴリ→キャラの割り当て(任意)
```

- **カテゴリごとの担当**は `cast/cast.json`、無ければ `comfy/recipe.json` の
  `cast[].category` から決まります
- **その中のどれを使うか**は記事の日付で決まります。連続する日は必ず別のポーズになり、
  乱数は使わないので撮り直しても同じ絵です
- 担当が決まっていないカテゴリは、キャラ自体も日替わりで回します

`cast.json` はこう書きます（`comfy/recipe.json` と食い違うときはこちらが優先）。

```json
{
  "デイリーダイジェスト": "hinata",
  "AIで作る技術": "kurumi",
  "Web開発・インフラ": "shirase",
  "クライアント技術": "kotoha",
  "チームで作る技術": "aoi"
}
```

### B. 1枚だけ置く（従来の形）

```
_assets/character/default.png          # 全カテゴリ共通
_assets/character/クライアント技術.png   # カテゴリ別(あればこちらが優先)
```

`cast/` に画像があればそちらが優先され、無ければこの2つが使われます。

使えるカテゴリ名は `デイリーダイジェスト` / `AIで作る技術` / `Web開発・インフラ` /
`クライアント技術` / `チームで作る技術` の5つです。

`_` 始まりのディレクトリなので、GitHub Pages には公開されません。

---

## 置くときは必ず `_prepare_character.py` を通す

透過の確認・余白のトリム・縮小・**サムネイル上で実際に何pxで出るか**を一度に見ます。

```bash
python3 _prepare_character.py <画像> --cast hinata --as wave --rembg   # cast に入れる
python3 _prepare_character.py <画像>                                   # default.png として置く
python3 _prepare_character.py <画像> クライアント技術                    # カテゴリ別に置く
python3 _prepare_character.py --check                                  # いまの状態を見るだけ
```

このスクリプトだけ **Pillow が要ります**（`_comfy_character.py` は標準ライブラリのみ）。

```bash
python3 -m pip install pillow
```

- **背景が透過していない画像は受け付けません。** 右に四角い板が出るためです
- `--rembg` を付けると背景除去モデルで切り抜きます。**床の影も、脚の間のように
  囲まれた背景も抜けます**（`python3 -m pip install rembg onnxruntime`。
  初回だけモデル176MBを取得。1枚あたり約1.2秒）
- `--matte` は追加なしで動く簡易版です。単色背景の外周から繋がった部分だけを塗ります
  （服の白や目のハイライトに穴は開きませんが、**影と囲まれた白は残ります**）
- 収まる箱は **幅268px × 高さ660px**。縦横比は保ったまま、この箱に収まる大きさで置かれます
- 実際に占めた幅のぶんだけ、文字に使える幅が自動で狭まります

取り込んだらサムネイルを撮り直し、**Read で開いて目視確認**してください。

```bash
python3 _render_thumbs.py <記事ディレクトリ名>
```

---

## 画像をどう用意するか

### A. ComfyUI で作る（`comfy/` を参照）

**ComfyUI はGPUのある手元のPCで動かします。** この記事サイトの実行環境にGPUは無く、
生成はできません。`_comfy_character.py` は「動いている ComfyUI に投げて受け取る」だけです。

```bash
python3 _comfy_character.py --check                  # つながるか / モデルはあるか
python3 _comfy_character.py                          # cast 全員 × ポーズ全種
python3 _prepare_character.py _assets/character/_candidates/hinata/wave.png \
  --cast hinata --as wave --rembg
```

顔を揃えるための IPAdapter の手順も含めて、詳しくは `comfy/README.md` にあります。

#### 既定以外のポートで起動しているとき

`_comfy_character.py` の既定は ComfyUI の既定と同じ `http://127.0.0.1:8188` です。
別のポートなら `--url` か `COMFY_URL` で指定します。

```bash
python3 _comfy_character.py --check --url http://127.0.0.1:8001
COMFY_URL=http://127.0.0.1:8001 python3 _comfy_character.py
```

繋がらなかったときは、よく使うポート（8188 / 8000 / 8001 / 8080 / 8189）を探しに行き、
見つかれば指定するコマンドを表示します。

#### クラウド側のセッションからは実行できません

このリポジトリを開いている Claude のセッションは別のコンテナで動いていて、
**あなたのPCの `127.0.0.1` には到達できません**（実測済み）。
ComfyUI の `--listen` の既定値も `127.0.0.1` なので、同じLANの別PCからも繋がりません。

生成は手元で走らせ、**採用する1枚をリポジトリに入れて渡す**のがいちばん確実です。
`_candidates/` は `.gitignore` に入れてあるので、渡すときだけ `-f` を付けます。

```bash
git add -f _assets/character/_candidates/
git commit -m "キャラクターの候補を追加" && git push
```

透過・トリム・サムネイルの撮り直しは、そのあとクラウド側でまとめてできます
（`_prepare_character.py` は Pillow、`_render_thumbs.py` は Chromium が要るため、
手元に無ければ無理に入れなくて構いません）。

生成の設定は `comfy/recipe.json` にあります。**モデル名・プロンプト・seed を固定すれば、
同じ顔をあとから再現できます。** 採用した seed は `recipe.json` に書き戻してください。

**日次の自動処理には組み込みません。** サムネイル生成（`_render_thumbs.py`）は
置いてある画像を読むだけで、生成は一切しません。朝5時の無人実行で、誰も確認していない絵が
公開されるのを避けるためです。

### B. VRoid Studio で作る

無料でアニメ調のキャラクターを作れます。表情差分・ポーズ違いを何枚でも書き出せるので、
一度作れば同じ顔が何度でも出せます。書き出すときに**背景を透過**にしてください。

### C. 絵師に依頼する

ココナラ / Skeb など。権利が明確なものが一度の費用で手に入ります。

---

## 権利

**他人のイラストを持ち込まないこと。** 参考にしたチャンネルのキャラクターをコピーするのも、
特定の作品のキャラクターを狙って出すプロンプト・LoRA を使うのも不可です。
自作するか、権利が明確なものだけを置いてください（CLAUDE.md 第6節）。
