#!/usr/bin/env bash
# ComfyUI 連携の一式を、偽サーバー相手に通しで動かす。
#
#   bash _labs/2026-08-18_comfy-character/run_all.sh
#
# 本物の ComfyUI ではありません(この環境にGPUは無い)。確かめているのは
# 「投げる → 待つ → 受け取る → 透過にする → 日付でポーズが選ばれる」の筋道だけです。
# 最後にダミーを消してサムネイルを撮り直すので、リポジトリは元の状態に戻ります。
set -u
cd "$(dirname "$0")/../.."
export COLUMNS=40
LAB=_labs/2026-08-18_comfy-character

python3 "$LAB/fake_comfy.py" 8188 >/tmp/fake_comfy.log 2>&1 &
FAKE=$!
trap 'kill $FAKE 2>/dev/null' EXIT
sleep 2

echo "### 1) つながるか / モデルはあるか"
python3 _comfy_character.py --check
echo "-- 終了コード $?"

echo
echo "### 2) recipe.json のモデルが無いとき"
python3 _comfy_character.py \
  --recipe $LAB/bad_recipe.json 2>&1
echo "-- 終了コード $?"

echo
echo "### 3) キャラ2人 × ポーズ2種"
python3 _comfy_character.py \
  --recipe $LAB/cast_recipe.json
echo "-- 終了コード $?"

echo
echo "### 4) 自分で書き出したワークフロー＋参照画像"
python3 _comfy_character.py \
  --recipe $LAB/cast_recipe.json \
  --who hinata --pose wave \
  --workflow $LAB/ipadapter_like.api.json \
  --reference _assets/character/_candidates/hinata/wave.png 2>&1 | tail -4

echo
echo "### 5) 差し替えの中身(単体で確認)"
python3 - <<'PY'
import json
import _comfy_character as c
recipe = json.load(open("_labs/2026-08-18_comfy-character/cast_recipe.json",
                        encoding="utf-8"))
job = c.jobs_from(recipe, who="hinata", pose="point")[0]
wf = json.load(open("_labs/2026-08-18_comfy-character/ipadapter_like.api.json",
                    encoding="utf-8"))
hit = c.patch_workflow(wf, recipe, job, reference="base.png")
print("差し替えた:", " ".join(sorted(hit)))
print("seed    :", wf["15"]["inputs"]["seed"])
print("size    :", wf["14"]["inputs"]["width"], "x", wf["14"]["inputs"]["height"])
print("参照画像:", wf["11"]["inputs"]["image"])
print("肯定    :", wf["12"]["inputs"]["text"][:60], "…")
print("否定    :", wf["13"]["inputs"]["text"][:60])
PY

echo
echo "### 6) 透過していない画像は受け付けない"
python3 _prepare_character.py \
  _assets/character/_candidates/hinata/wave.png >/tmp/reject.txt 2>&1
echo "-- 終了コード $?"
head -3 /tmp/reject.txt

echo
echo "### 7) --matte で背景を抜いて cast に入れる"
for f in hinata/wave hinata/point kurumi/wave kurumi/point; do
  python3 _prepare_character.py \
    "_assets/character/_candidates/$f.png" \
    --cast "${f%/*}" --as "${f#*/}" --matte | grep -E "保存|サムネイル上"
done

echo
echo "### 8) 記事ごとに誰のどのポーズが選ばれるか"
python3 - <<'PY'
import _render_thumbs as t
rows = [("2026-08-18_001", "デイリーダイジェスト"),
        ("2026-08-17_001", "デイリーダイジェスト"),
        ("2026-08-16_001", "デイリーダイジェスト"),
        ("2026-08-15_laravel-first", "Web開発・インフラ")]
for d, cat in rows:
    p = t.character_path(cat, d)
    print(f"{d:24s} → {p.relative_to(t.HERE / '_assets/character/cast') if p else 'なし'}")
PY

echo
echo "### 9) サムネイルを撮る"
python3 _render_thumbs.py 2026-08-18_001 2>&1 | tail -2

echo
echo "### 10) 後片付け(ダミーを消して撮り直す)"
rm -rf _assets/character/cast _assets/character/_candidates
python3 _render_thumbs.py 2026-08-18_001 2>&1 | tail -2
python3 _prepare_character.py --check
