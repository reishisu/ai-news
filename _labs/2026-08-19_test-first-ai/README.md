# 2026-08-19_test-first-ai — 弱いテストは突破される

記事「AIに実装を任せるときのテストの書き方」の実測一式。

## 何を確かめたか

送料計算 `shipping(subtotal)` を題材に、**同じ実装に対してテストの強さだけを変えて**
pytest を回し、結果がどう変わるかを実測した。

仕様: 合計 3000円以上は送料無料 / それ未満は 500円 / 負の金額は `ValueError`。

| # | テスト | 実装 | 結果 |
|---|---|---|---|
| 1 | 弱 (例1つ) | ズル (`return 0`) | **1 passed** ← 通ってしまう |
| 2 | 弱 (例1つ) | 正しい | 1 passed |
| 3 | (pytest不使用) | 2999円を直接呼ぶ | ズル=`0` / 正しい=`500` |
| 4 | 強 (境界値+例外) | ズル | 3 failed, 2 passed |
| 5 | 強 (1件だけ全文) | ズル | `assert 0 == 500` |
| 6 | 強 | 空 (`pass` だけ) | 5 failed ← red |
| 7 | 強 | 正しい | 5 passed ← green |
| 8 | 弱+強 | 正しい | 6 passed |

**1と2の出力は完全に同一。** 弱いテストはズルい実装と正しい実装を区別できない、
というのがこのラボの中心の事実。

## ファイル

| ファイル | 中身 |
|---|---|
| `shipping_ok.py` | 正しい実装(素直なif文) |
| `shipping_cheat.py` | `return 0` するだけ |
| `shipping_empty.py` | `pass` だけ(red を見るため) |
| `shipping.py` | **作業用のコピー。** `run_all.sh` が上の3つから上書きする(最後は ok に戻す) |
| `test_weak.py` | 弱いテスト(`shipping(5000) == 0` の1件) |
| `test_strong.py` | 強いテスト(境界値4件 + `pytest.raises`) |
| `run_all.sh` | 全シナリオを順に再実行 |
| `output.txt` | `run_all.sh` の生出力(記事に貼ったものと同一) |
| `check_width.py` | 出力の表示幅が40桁を超えていないか検査 |

テストは `from shipping import shipping` と書いてあるので、実装の差し替えは
`shipping.py` を上書きする形で行う（`use()` 関数）。差し替え時に `__pycache__` を
消しているのは、`.pyc` のキャッシュ判定が mtime(秒) + サイズなので、
同一秒内の入れ替えで古いバイトコードを掴む可能性を潰すため。

## 動かし方

```bash
pip install pytest
cd _labs/2026-08-19_test-first-ai
./run_all.sh            # 画面に出る
./run_all.sh > output.txt 2>&1   # 取り直す
python3 check_width.py output.txt
```

## 実行環境（実測）

```
$ python3 -V
Python 3.11.15
$ python3 -m pytest --version
pytest 9.1.1
```

実行日: 2026-08-18 / Linux 6.18.5

**PATH 上の `pytest` は別物だった。** この環境には uv が入れた
`/root/.local/bin/pytest`（pytest 9.0.2、専用のPythonを指す shebang）があり、
`pip install pytest` で入れたもの（9.1.1）とバージョンが違う。
最初は素の `pytest` で回して 9.0.2 の出力を取ってしまったので、
`run_all.sh` では `python3 -m pytest` に固定して取り直した。
出力の書式に差は見つからなかったが、記事に書くバージョンは
**実際に回したほう(9.1.1)** にしてある。

## 幅の話（CLAUDE.md 第4節）

- `export COLUMNS=40` を付けて実行。`output.txt` のラベル行（`####`）以外は
  **全行が表示幅40桁以内**（`check_width.py` で 0 件）
- そのために **ファイル名とテスト名を短くした**。
  `test_shipping_strong.py` → `test_strong.py`、
  テスト名は日本語をやめて `test_fee` / `test_negative`。
  `parametrize` には `ids=["2999","3000","3001","0"]` を付けて
  既定の `[2999-500]` 形式より短くしている
- `@pytest.mark.parametrize(...)` の**ソース行そのものがトレースバックに出る**ため、
  デコレータの改行位置も幅に効く。`ids=[...]` を1行に書くと 42 桁になったので2行に割った
- コマンド行が40桁を超えるものは `\` で2行に割って表示している
  （`run_all.sh` の echo と実行が同じ内容になるようにしてある）
- `FAILED test_strong.py::test_fee[0] - ...` の `- ...` は
  **pytest が幅40に合わせて理由を切った結果**。手で削ってはいない

## 前作との差分

連載前作 `_labs/2026-08-14_ai-basics/` は関数名が `shipping_fee(total)`。
本ラボは `shipping(subtotal)` に変えてある（仕様と閾値は同じ）。
記事で前作のコードを併記するときは名前の違いに注意。
