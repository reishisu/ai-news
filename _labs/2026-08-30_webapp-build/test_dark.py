#!/usr/bin/env python3
"""ダークモードの切替と保持をPlaywrightで確かめる。"""
import subprocess, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen(['python3','-m','http.server','8899','--directory','app'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
        pg = b.new_page(viewport={'width':1280,'height':800})
        pg.goto('http://127.0.0.1:8899/'); pg.wait_for_timeout(400)
        bg1 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        pg.click('text=🌙'); pg.wait_for_timeout(400)
        bg2 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        pg.screenshot(path='shot6_dark.png')
        pg.reload(); pg.wait_for_timeout(400)
        bg3 = pg.evaluate("getComputedStyle(document.body).backgroundColor")
        print('背景:', bg1, '→', bg2, '/ リロード後:', bg3,
              'theme=', pg.evaluate("localStorage['simple-memo-app-theme']"))
        b.close()
finally:
    srv.terminate()
