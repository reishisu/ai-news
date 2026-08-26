#!/bin/bash
# 記事に載せた3つの実験を、この順で全部走らせる。
set -e
cd "$(dirname "$0")"
echo "### 実験1: ディレクトリ名 release-check (説明だけを変える)"
./setup.sh  /home/user/skilllab  > /dev/null
python3 run_trials.py /home/user/skilllab  10 release-check
echo
echo "### 実験2: ディレクトリ名 memo-1 (説明だけを変える)"
./setup2.sh /home/user/skilllab2 > /dev/null
python3 run_trials.py /home/user/skilllab2 10 memo-1
echo
echo "### 実験3: 良い説明のまま自動起動を切る"
./setup3.sh /home/user/skilllab3 > /dev/null
python3 run_trials.py /home/user/skilllab3 10 memo-1 "A 自動ON" "B 自動OFF"
