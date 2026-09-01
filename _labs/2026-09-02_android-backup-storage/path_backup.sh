#!/bin/bash
# 設定 → Google → すべてのサービス → バックアップ までを adb で操作する（録画は別途）
# スクロール位置は毎回ずれるので、uiautomator で要素を探してからタップする
export MSYS_NO_PATHCONV=1
P=${PAUSE:-1.2}
bounds() {  # $1=text  → "x y"(中心) を返す。無ければ空
  adb shell uiautomator dump /sdcard/ui.xml >/dev/null 2>&1
  adb shell cat /sdcard/ui.xml | tr '>' '\n' | grep -F "text=\"$1\"" | head -1 \
   | grep -oE 'bounds="\[[0-9]+,[0-9]+\]\[[0-9]+,[0-9]+\]"' \
   | sed -E 's/.*\[([0-9]+),([0-9]+)\]\[([0-9]+),([0-9]+)\]"/\1 \2 \3 \4/' \
   | awk '{ if ($2>=110 && $4<=520) print int(($1+$3)/2), int(($2+$4)/2) }'
}
scroll_tap() {  # $1=text  見えるまで下へスクロールしてタップ
  for i in 1 2 3 4 5 6 7 8 9 10; do
    xy=$(bounds "$1")
    if [ -n "$xy" ]; then sleep 0.6; adb shell input tap $xy; return 0; fi
    adb shell input swipe 600 420 600 200 500; sleep $P
  done
  echo "NOT FOUND: $1" >&2; return 1
}
adb shell am force-stop com.android.settings
adb shell am force-stop com.google.android.gms
adb shell input keyevent 3; sleep 1.5
adb shell am start -a android.settings.SETTINGS --activity-clear-task >/dev/null; sleep 2.5
scroll_tap "Google"; sleep 2.5
scroll_tap "すべてのサービス"; sleep 2
scroll_tap "バックアップ"; sleep 2.5
