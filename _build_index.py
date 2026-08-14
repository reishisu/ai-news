#!/usr/bin/env python3
"""ai-news-YYYY-MM-DD.html の最新号から index.html を生成するスクリプト。

- 同じディレクトリの ai-news-YYYY-MM-DD.html を日付降順で列挙
- 各号のページに favicon / OGPメタ / shared.css / SNS共有バー(shared.js)を注入(未注入の号のみ)
- 最新号のHTMLの </body> 直前に「📚 過去の号一覧」セクションを差し込み、
  <title> を「AIニュース デイリーダイジェスト」に置換して index.html として保存
- 号が1つも無い場合は何もせず正常終了
"""

import datetime
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATTERN = re.compile(r"^ai-news-(\d{4})-(\d{2})-(\d{2})\.html$")
WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]
SITE_URL = "https://reishisu.github.io/ai-news/"
SITE_TITLE = "AIニュース デイリーダイジェスト"


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


def head_extras(page_url, title):
    return f"""
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="apple-touch-icon" href="favicon.svg">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="世界のAIニュースを日本語で、毎朝6:00にお届け">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{SITE_URL}ogp.png">
<meta name="twitter:card" content="summary_large_image">
"""

SHARED_CSS_LINK = '\n<link rel="stylesheet" href="shared.css">\n'


def build_archive_section(issues):
    items = []
    for i, (date, name) in enumerate(issues):
        badge = '<span class="an-new">NEW</span>' if i == 0 else ""
        items.append(
            f'      <a class="an-item" href="{name}">'
            f'<span class="an-date">{format_date_ja(date)}</span>'
            f'<span class="an-label">の号を読む{badge}</span>'
            f'<span class="an-arrow" aria-hidden="true">→</span></a>'
        )
    links = "\n".join(items)
    return f"""
<!-- ai-news-archive -->
<section id="ai-news-archive">
  <h2>📚 過去の号一覧</h2>
  <nav class="an-grid">
{links}
  </nav>
</section>
"""


SHARE_BAR = """
<!-- ai-news-sharebar -->
<div id="ai-news-sharebar" aria-label="SNSでシェア">
  <div class="sb-menu">
    <a class="sb-btn" data-share="x" target="_blank" rel="noopener" title="Xで共有"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.41l-5.8-7.58-6.64 7.58H.47l8.6-9.83L0 1.15h7.59l5.24 6.93 6.07-6.93Zm-1.29 19.5h2.04L6.49 3.24H4.3l13.31 17.41Z"/></svg></a>
    <a class="sb-btn" data-share="line" target="_blank" rel="noopener" title="LINEで送る"><svg viewBox="0 0 24 24" fill="#06C755"><path d="M12 2C6.48 2 2 5.64 2 10.12c0 4.02 3.57 7.39 8.39 8.03.33.07.77.22.89.5.1.26.07.66.03.92l-.14.86c-.04.26-.2 1 .88.55 1.08-.46 5.8-3.42 7.92-5.85C21.53 13.55 22 11.92 22 10.12 22 5.64 17.52 2 12 2Z"/></svg></a>
    <a class="sb-btn" data-share="fb" target="_blank" rel="noopener" title="Facebookで共有"><svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.09 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.7 4.53-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.61 23.09 24 18.1 24 12.07Z"/></svg></a>
    <a class="sb-btn" data-share="hatena" target="_blank" rel="noopener" title="はてなブックマーク"><svg viewBox="0 0 24 24" fill="#00A4DE"><path d="M20.47 0H3.53A3.53 3.53 0 0 0 0 3.53v16.94A3.53 3.53 0 0 0 3.53 24h16.94A3.53 3.53 0 0 0 24 20.47V3.53A3.53 3.53 0 0 0 20.47 0ZM12.1 17.1c-.9.99-2.28 1.2-3.36 1.2H5.18V5.72h3.4c1.09 0 2.32.13 3.13 1 .65.7.77 1.51.77 2.19 0 .84-.34 1.64-1.11 2.13 1.02.42 1.62 1.4 1.62 2.66 0 .96-.28 2.4-.9 3.4Zm5.32 1.2a1.53 1.53 0 1 1 0-3.06 1.53 1.53 0 0 1 0 3.06Zm1.24-4.3h-2.48V5.72h2.48V14Z"/></svg></a>
    <button class="sb-btn" data-share="copy" type="button" title="リンクをコピー"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
  </div>
  <button class="sb-toggle" type="button" title="シェア" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg></button>
  <div class="sb-toast" role="status"></div>
</div>
<script src="shared.js" defer></script>
"""


def inject_before_body(html, snippet):
    if re.search(r"</body>", html, flags=re.IGNORECASE):
        return re.sub(r"</body>", lambda m: snippet + "</body>", html, count=1, flags=re.IGNORECASE)
    return html + snippet


def inject_into_head(html, snippet):
    if re.search(r"</head>", html, flags=re.IGNORECASE):
        return re.sub(r"</head>", lambda m: snippet + "</head>", html, count=1, flags=re.IGNORECASE)
    return snippet + html


def enhance(html, page_url, title):
    """favicon/OGPメタ・shared.css・共有バーを未注入なら差し込む。"""
    if "favicon.svg" not in html:
        html = inject_into_head(html, head_extras(page_url, title))
    if "shared.css" not in html:
        html = inject_into_head(html, SHARED_CSS_LINK)
    if "ai-news-sharebar" not in html:
        html = inject_before_body(html, SHARE_BAR)
    return html


def main():
    issues = collect_issues()
    if not issues:
        return

    # 各号のページ自体にも favicon/OGP/共有バーを注入(未注入の号のみ更新)
    for date, name in issues:
        path = HERE / name
        original = path.read_text(encoding="utf-8")
        enhanced = enhance(original, SITE_URL + name, f"{SITE_TITLE} {format_date_ja(date)}")
        if enhanced != original:
            path.write_text(enhanced, encoding="utf-8")
            print(f"{name} に共有バー/メタ情報を注入しました")

    latest = HERE / issues[0][1]
    html = latest.read_text(encoding="utf-8")

    html = enhance(html, SITE_URL, SITE_TITLE)
    html = inject_before_body(html, build_archive_section(issues))

    # index.html はサイトのトップとして og:url / og:title を上書き
    html = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{SITE_URL}\g<2>", html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{SITE_TITLE}\g<2>", html, count=1)

    html = re.sub(
        r"<title>.*?</title>",
        f"<title>{SITE_TITLE}</title>",
        html,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )

    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html を生成しました(最新号: {issues[0][1]}、全{len(issues)}号)")


if __name__ == "__main__":
    main()
