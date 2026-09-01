import os, time, shutil, pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path("takes/2026-09-02_android-backup-storage")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ.get("CHROMIUM") or None)
    ctx = b.new_context(viewport={"width":1224,"height":532}, locale="ja-JP",
                        record_video_dir=str(OUT/"_raw"), record_video_size={"width":1224,"height":532})
    pg = ctx.new_page()
    pg.goto("https://support.google.com/googleone/answer/9004014?hl=ja", wait_until="networkidle", timeout=60000)
    pg.add_style_tag(content="body{zoom:1.3}"); time.sleep(2)
    hd = pg.get_by_text("容量を使用するファイル", exact=True).first
    hd.scroll_into_view_if_needed(); time.sleep(1.2)
    hd.click(); time.sleep(1.5)
    tgt = pg.get_by_text("Android デバイスのバックアップ", exact=True).first
    # ゆっくり近づく
    for i in range(40):
        box = tgt.bounding_box()
        if box and box["y"] < 140: break
        pg.mouse.wheel(0, 160); time.sleep(0.7)
    time.sleep(3)
    pg.screenshot(path=str(OUT/"help_9004014_ja_backup.png"))
    v = pg.video.path(); ctx.close(); shutil.move(v, OUT/"help_9004014_ja.webm"); b.close()
print("ok")
