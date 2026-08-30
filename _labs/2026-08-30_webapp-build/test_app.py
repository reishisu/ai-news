#!/usr/bin/env python3
"""作成→リロードで残る→削除、をPlaywrightで確かめる。
**保存の検査は同じブラウザセッション内のリロードで行うこと**
(起動し直すと新品のプロファイルで localStorage が空になり、
「消えた」と誤判定する。段5で実際にやりかけた)。"""
import subprocess, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen(['python3','-m','http.server','8899','--directory','app'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg = b.new_page(viewport={'width':1280,'height':800})
        pg.on('dialog', lambda d: d.accept())
        pg.goto('http://127.0.0.1:8899/'); pg.wait_for_timeout(400)
        pg.click('text=＋ 新しいメモを作成'); pg.wait_for_timeout(300)
        pg.query_selector('textarea').fill('実測メモ: これはテストです')
        pg.wait_for_timeout(600)
        print('作成後一覧:', pg.eval_on_selector_all('#memo-list > *',
              'els=>els.map(e=>e.textContent.trim().slice(0,40))'))
        pg.screenshot(path='shot2_created.png')
        pg.reload(); pg.wait_for_timeout(500)
        print('リロード後一覧:', pg.eval_on_selector_all('#memo-list > *',
              'els=>els.map(e=>e.textContent.trim().slice(0,30))'))
        pg.eval_on_selector('#memo-list > *:first-child','e=>e.click()')
        pg.wait_for_timeout(300)
        pg.click('text=このメモを削除'); pg.wait_for_timeout(400)
        print('削除後 localStorage:', pg.evaluate("localStorage['simple-memo-app-notes']"))
        b.close()
finally:
    srv.terminate()
