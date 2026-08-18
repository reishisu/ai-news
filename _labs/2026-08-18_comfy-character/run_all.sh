#!/usr/bin/env bash
# ComfyUI 連携の一式を、偽サーバー相手に通しで動かす。
#
#   bash _labs/2026-08-18_comfy-character/run_all.sh
#
# 本物の ComfyUI ではありません(この環境にGPUは無い)。確かめているのは
# 「投げる → 待つ → 受け取る → 透過にする → サムネイルに入る」の筋道だけです。
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
echo "### 3) 候補を2枚もらう"
python3 _comfy_character.py \
  --recipe $LAB/lab_recipe.json --batch 2
echo "-- 終了コード $?"

echo
echo "### 4) 透過していない画像は受け付けない"
python3 _prepare_character.py \
  _assets/character/_candidates/seed100-7-0.png 2>&1
echo "-- 終了コード $?"

echo
echo "### 5) --matte で背景を抜いて取り込む"
python3 _prepare_character.py \
  _assets/character/_candidates/seed100-7-0.png --matte
echo "-- 終了コード $?"

echo
echo "### 6) サムネイルを撮る"
python3 _render_thumbs.py 2026-08-18_001 2>&1 | tail -2

echo
echo "### 7) 後片付け(ダミーを消して撮り直す)"
rm -f _assets/character/default.png
rm -rf _assets/character/_candidates
python3 _render_thumbs.py 2026-08-18_001 2>&1 | tail -2
python3 _prepare_character.py --check
