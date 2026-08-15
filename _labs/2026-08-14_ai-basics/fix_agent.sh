#!/bin/bash
# 記事では「AIの呼び出し」に差し替える箇所。検証では sed で1文字直すだけにする。
sed -i 's/if total > FREE_THRESHOLD:/if total >= FREE_THRESHOLD:/' shipping.py
