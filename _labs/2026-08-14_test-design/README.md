# 2026-08-14_test-design — 検証物

記事: `contents/2026-08-14_test-design/`
「カバレッジ100%のテストが、バグ4個中1個しか見つけなかった」

## 何を確かめたか

同じアプリ（席数割引つきの請求計算）に、同じ4つのバグを1行ずつ入れて、
粒度の違うテストがそれぞれ検出できるかを実測しました。

| スクリプト | 確かめたこと |
|---|---|
| `run_cov.py` | 行カバレッジ100%のセットと59.1%のセットで、検出数がどう違うか |
| `run_matrix.py` | 4通りの壊し方 × 3粒度の検出マトリクス |
| `run_isolate.py` | 同じバグで、ユニットとE2Eのスタックトレースがどう違うか |
| `run_time.py` | 同内容の検証200件を粒度[小]/[大]で書いたときの実行時間 |
| `run_flaky.py` | CPUを埋めたときに、素直なタイムアウトが何回超過するか |
| `run_covmap.py` | テストファイル × ソースファイルのカバレッジ（E2Eが0%になる） |
| `run_subproc_cov.py` | `COVERAGE_PROCESS_START` を渡してE2Eを測り直す |
| `run_diffcov.py` | 全体カバレッジと差分カバレッジの差（テストゼロのPRを注入） |
| `run_spec.py` | 割引ルール改定を入れたときに、good/bad がそれぞれ何を言うか |
| `run_mutation.py` | mutmut で53通りに書き換え、good/bad が何を殺せるか |

## 動かし方

```bash
# output.txt を取ったときの順番（run_diffcov.py が最後）
for s in run_cov run_matrix run_covmap run_subproc_cov run_isolate run_spec run_diffcov; do
  python3 $s.py
done
python3 run_mutation.py   # クーポン適用前の app/ で動かすこと
```

**実行順に依存があります。**

- **`run_diffcov.py` は必ず最後に動かしてください。** このスクリプトは `feature_coupon.py`
  を適用して `app/coupon.py` を新規作成し、`app/bill.py` を書き換えます。
  適用後の `app/` のまま他を動かすと、`run_subproc_cov.py` の総ステートメント数が変わり、
  `run_mutation.py` は `ImportError` で落ちます。
- 続けて動かすときは、毎回 `app/` を**クーポン適用前**（`app/coupon.py` が
  存在しない状態）に戻してください。`output.txt` はこの順で取っています。
- `run_diffcov.py` は `git diff HEAD -- app` で追加行を取るため、
  **このディレクトリが独立したgitリポジトリで、クーポン適用前の `app/` がコミット済み**
  である必要があります。そうでない場合は「追加行: 0行」と出ます。
- `run_mutation.py` は `mut_bad/` `mut_good/` を毎回作り直します（Git管理外）。

## 実行結果

- `output.txt` — 上記のうち、値が毎回同じもの（記事に貼ったものと同一）
- `output_mutation.txt` — `run_mutation.py` と `mutmut show` 2件
- `output_timing.txt` — `run_time.py` と `run_flaky.py`。**この2本は実行ごとに数値が動きます**

`run_flaky.py` の混雑時の超過率は、条件を変えない6回の実行で
43.5% / 41.0% / 23.0% / 16.5% / 16.5% / 14.5% でした。
「空いているときは 0/200」は6回とも再現します。
`run_time.py` の倍率は 16.4〜17.0倍で安定し、絶対値だけが15〜20%動きます。
**記事では、ぶれる数字は範囲で書き、ぶれない数字（倍率・0/200）だけを言い切っています。**

## 実行環境

Python 3.11.15 / pytest 9.1.1 / pytest-cov 7.1.0 / coverage 7.15.4 /
mutmut 3.7.0 / git 2.43.0 / Linux 6.18.5（4コア）。2026年8月14日実施、
2026年8月15日に全スクリプトを再実行して再現を確認。

## mutmut で詰まった点（3回失敗しています）

1. `setup.cfg` の `source_paths` はカンマ区切りが効かず「0 files mutated」になる
2. テストファイル名が `test` で始まらないと `mutants/` にコピーされない
   （`also_copy` の既定値が `Path(".").glob("test*.py")` のため）
3. それを直しても親ディレクトリの `pytest.ini` を pytest が拾って収集されない
   → 作業ディレクトリ内に専用の `pytest.ini` を置き、`also_copy=pytest.ini` を足す

## ターミナル出力の幅について（意図的に残している超過）

CLAUDE.md 第4節は「1行は半角40桁まで」ですが、この記事の
`run_isolate.py` の出力は**13行が超過しています（最長75桁）。意図的です。**

`run_isolate.py` は既に `COLUMNS=40` を渡しており、セパレータ行と進捗行は
40桁に詰まっています。残る超過は、E2Eテストが落ちたときに出る
標準ライブラリのフレームです。

```
/usr/lib/python3.11/json/decoder.py:355: in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
E   json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**この長さと、原因から遠いことが、記事の主張そのものです。**
記事の第3節は「E2Eは『壊れた』としか言わない ― ユニットは壊した行を、
E2Eは標準ライブラリを指した」という節で、本文でも
「知りたいのは一番下の、原因の場所です」と読み方を説明しています。

縮める手段は実測して比較しましたが、いずれも記事が成立しなくなります。

| 手段 | 結果 |
|---|---|
| `--tb=line` | 1行に潰れてスタックトレースが消える。さらにパスが絶対パスになり **112桁** と逆に長くなる |
| `--tb=native` | フレームが増え **102桁**。最悪 |
| `COLUMNS` をさらに小さく | pytest の下限に当たり80桁へ戻る（26/30/34 で実測） |
| 出力を手で切り詰める | **禁止**（CLAUDE.md 第1節・第4節。嘘になる） |

`.code` は自分の中で横スクロールするため、ページ全体は幅380pxでも崩れません。
