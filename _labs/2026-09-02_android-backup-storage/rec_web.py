"""公式ページを Playwright(headless) の録画機能で撮る。運営者の画面には何も出ない。"""
import os, sys, time, shutil, pathlib
from playwright.sync_api import sync_playwright
OUT = pathlib.Path("takes/2026-09-02_android-backup-storage"); OUT.mkdir(parents=True, exist_ok=True)
PAGES = {
  "google_one_thread": ("https://support.google.com/googleone/thread/451067756/android-device-backup-storage-update-controls?hl=en", 1.3),
  "help_9004014_ja":   ("https://support.google.com/googleone/answer/9004014?hl=ja", 1.3),
}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=os.environ.get("CHROMIUM") or None)
    for name, (url, zoom) in PAGES.items():
        ctx = b.new_context(viewport={"width":1224,"height":532}, locale="ja-JP",
                            record_video_dir=str(OUT/"_raw"), record_video_size={"width":1224,"height":532})
        pg = ctx.new_page(); pg.goto(url, wait_until="networkidle", timeout=60000)
        pg.add_style_tag(content="body{zoom:%s}" % zoom); time.sleep(2.5)
        pg.screenshot(path=str(OUT/f"{name}_top.png"))
        for i in range(10):
            pg.mouse.wheel(0, 180); time.sleep(0.9)
        time.sleep(1.5)
        pg.screenshot(path=str(OUT/f"{name}_scrolled.png"))
        txt = pg.inner_text("body")
        (OUT/f"{name}.txt").write_text(txt, encoding="utf-8")
        vpath = pg.video.path(); ctx.close()
        shutil.move(vpath, OUT/f"{name}.webm"); print(name, "->", OUT/f"{name}.webm")
    b.close()
