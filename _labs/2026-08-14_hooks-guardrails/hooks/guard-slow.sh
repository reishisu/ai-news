#!/bin/bash
# timeout より長くかかるフック（タイムアウト時にどちらへ倒れるか）
sleep 5
echo "guard: 遅れて到着 (exit 2)" >&2
exit 2
