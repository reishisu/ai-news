#!/bin/bash
# 記事に貼る全出力を、幅40桁の端末を想定して取り直す。
# pytest は COLUMNS を見てセパレータ行を詰める(40未満は無視され80に戻る)。
export COLUMNS=40
cd "$(dirname "$0")" || exit 1

# PATH 上に別バージョンの pytest が居ることがあるので、
# python3 と同じ環境の pytest を明示的に使う。
PYTEST="python3 -m pytest"

# shipping.py は作業用のコピー。中身を差し替えて回す。
use() { rm -rf __pycache__; cp "shipping_$1.py" shipping.py; }

echo "########## 0. 環境 ##########"
echo '$ python3 -V'
python3 -V
echo '$ python3 -m pytest --version'
$PYTEST --version
echo '$ export COLUMNS=40'

echo
echo "########## 1. 弱 x ズル ##########"
use cheat
echo '$ python3 -m pytest -q test_weak.py'
$PYTEST -q test_weak.py 2>&1

echo
echo "########## 2. 弱 x 正しい実装 ##########"
use ok
echo '$ python3 -m pytest -q test_weak.py'
$PYTEST -q test_weak.py 2>&1

echo
echo "########## 3. 2999円で確かめる ##########"
echo "\$ python3 -c 'import shipping_cheat as m"
echo "print(m.shipping(2999))'"
python3 -c 'import shipping_cheat as m
print(m.shipping(2999))' 2>&1
echo "\$ python3 -c 'import shipping_ok as m"
echo "print(m.shipping(2999))'"
python3 -c 'import shipping_ok as m
print(m.shipping(2999))' 2>&1

echo
echo "########## 4. 強 x ズル(要約) ##########"
use cheat
echo '$ python3 -m pytest -q --tb=no \'
echo '    test_strong.py'
$PYTEST -q --tb=no test_strong.py 2>&1

echo
echo "########## 5. 落ちた1件だけ全文 ##########"
use cheat
echo '$ python3 -m pytest -q -k 2999 \'
echo '    test_strong.py'
$PYTEST -q -k 2999 test_strong.py 2>&1

echo
echo "########## 6. 空実装 x 強(red) ##########"
use empty
echo '$ python3 -m pytest -q --tb=no \'
echo '    test_strong.py'
$PYTEST -q --tb=no test_strong.py 2>&1

echo
echo "########## 7. 正しい実装 x 強(green) ##########"
use ok
echo '$ python3 -m pytest -q test_strong.py'
$PYTEST -q test_strong.py 2>&1

echo
echo "########## 8. 両方まとめて ##########"
use ok
echo '$ python3 -m pytest -q'
$PYTEST -q 2>&1

use ok
rm -rf __pycache__ .pytest_cache
