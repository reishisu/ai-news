#!/bin/bash
# 記事に貼る全ターミナル出力を、幅40桁の端末を想定して取り直す。
# pytest は COLUMNS を見てセパレータ行を詰める(40未満は無視され80に戻る)。
export COLUMNS=40
cd "$(dirname "$0")"
reset_bug(){ sed -i 's/if total >= FREE_THRESHOLD:/if total > FREE_THRESHOLD:/' shipping.py; }

echo "########## BLOCK 4: pytest 単体 ##########"
reset_bug
echo '$ COLUMNS=40 python3 -m pytest -q'
python3 -m pytest -q 2>&1

echo
echo "########## BLOCK 7: フック単体 ##########"
reset_bug
IN='{"tool_input":{"file_path":"shipping.py"}}'
echo '$ IN='"'"'{"tool_input":{"file_path":"shipping.py"}}'"'"''
echo '$ echo "$IN" | .claude/hooks/pytest.sh'
echo "$IN" | .claude/hooks/pytest.sh 2>&1
echo '$ echo $?'
echo "$IN" | .claude/hooks/pytest.sh >/dev/null 2>&1; echo $?
echo
echo '# バグを直して、もう一度叩く'
./fix_agent.sh
echo '$ echo "$IN" | .claude/hooks/pytest.sh'
echo "$IN" | .claude/hooks/pytest.sh 2>&1
echo '$ echo $?'
echo "$IN" | .claude/hooks/pytest.sh >/dev/null 2>&1; echo $?

echo
echo "########## BLOCK 9: loop.sh ##########"
reset_bug
echo '$ ./loop.sh'
./loop.sh 2>&1
echo '$ echo $?'
reset_bug; ./loop.sh >/dev/null 2>&1; echo $?

echo
echo "########## BLOCK 10: 壊れていた版 ##########"
reset_bug
echo '$ ./loop.sh   # if python3 -m pytest -q --tb=no | tail -1'
./loop_broken.sh 2>&1 | head -4

reset_bug
