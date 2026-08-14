#!/usr/bin/env python3
"""ai-news-YYYY-MM-DD.html の最新号から index.html を生成するスクリプト。

- 同じディレクトリの ai-news-YYYY-MM-DD.html を日付降順で列挙
- 最新号のHTMLの </body> 直前に「📚 過去の号一覧」セクションを差し込む
- <title> を「AIニュース デイリーダイジェスト」に置換して index.html として保存
- 号が1つも無い場合は何もせず正常終了
"""

import datetime
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATTERN = re.compile(r"^ai-news-(\d{4})-(\d{2})-(\d{2})\.html$")
WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def collect_issues():
    """(date, filename) のリストを日付降順で返す。"""
    issues = []
    for path in HERE.iterdir():
        m = PATTERN.match(path.name)
        if not m:
            continue
        try:
            date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        issues.append((date, path.name))
    issues.sort(key=lambda x: x[0], reverse=True)
    return issues


def format_date_ja(date):
    return f"{date.year}年{date.month}月{date.day}日({WEEKDAYS_JA[date.weekday()]})"


def build_archive_section(issues):
    links = "\n".join(
        f'      <li><a href="{name}">{format_date_ja(date)} の号</a></li>'
        for date, name in issues
    )
    return f"""
<section id="archive" style="max-width:820px;margin:32px auto;padding:20px 24px;border:1px solid rgba(128,128,128,0.25);border-radius:14px;font-family:system-ui,sans-serif;">
  <h2 style="font-size:1.2em;margin:0 0 12px;">📚 過去の号一覧</h2>
  <ul style="margin:0;padding-left:1.4em;line-height:2;">
{links}
  </ul>
</section>
"""


def main():
    issues = collect_issues()
    if not issues:
        return

    latest = HERE / issues[0][1]
    html = latest.read_text(encoding="utf-8")

    section = build_archive_section(issues)
    if re.search(r"</body>", html, flags=re.IGNORECASE):
        html = re.sub(r"</body>", section + "</body>", html, count=1, flags=re.IGNORECASE)
    else:
        html += section

    html = re.sub(
        r"<title>.*?</title>",
        "<title>AIニュース デイリーダイジェスト</title>",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html を生成しました(最新号: {issues[0][1]}、全{len(issues)}号)")


if __name__ == "__main__":
    main()
