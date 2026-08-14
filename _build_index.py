#!/usr/bin/env python3
"""AIニュース デイリーダイジェスト — サイトビルダー。

- contents/YYYY-MM-DD_id/index.html を号として日付降順で列挙
- 各号のメタ情報を contents/*/meta.json(無ければHTMLのtitle/og:description)から取得
- 各号のページに favicon/OGP・css/shared.css・SNS共有バー(js/shared.js)を
  相対パスで注入(未注入の号のみ更新)
- _templates/home.html から、サムネイル+タイトル+概要のカード一覧を持つ
  トップページ index.html を生成
- 号が1つも無い場合はカード0件のトップページを生成して正常終了
"""

import datetime
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTENTS = HERE / "contents"
TEMPLATE = HERE / "_templates" / "home.html"
DIR_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})_[A-Za-z0-9-]+$")
WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]
SITE_URL = "https://reishisu.github.io/ai-news/"
SITE_TITLE = "AIニュース デイリーダイジェスト"

# 号ページ(contents/<dir>/index.html)からサイトルートへの相対プレフィックス
ISSUE_PREFIX = "../../"


def format_date_ja(date):
    return f"{date.year}年{date.month}月{date.day}日({WEEKDAYS_JA[date.weekday()]})"


def collect_issues():
    """[{date, dirname, dirpath, html_path}] を日付降順で返す。"""
    issues = []
    if not CONTENTS.is_dir():
        return issues
    for path in CONTENTS.iterdir():
        m = DIR_RE.match(path.name)
        if not m or not (path / "index.html").is_file():
            continue
        try:
            date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            continue
        issues.append({
            "date": date,
            "dirname": path.name,
            "dirpath": path,
            "html_path": path / "index.html",
        })
    issues.sort(key=lambda x: (x["date"], x["dirname"]), reverse=True)
    return issues


def load_meta(issue):
    """meta.json 優先、無ければHTMLから title / og:description を抽出。"""
    meta = {}
    meta_path = issue["dirpath"] / "meta.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            meta = {}

    html = issue["html_path"].read_text(encoding="utf-8")
    if not meta.get("title"):
        m = re.search(r'<meta property="og:title" content="([^"]*)"', html) or \
            re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        meta["title"] = (m.group(1).strip() if m else issue["dirname"])
    if not meta.get("summary"):
        m = re.search(r'<meta (?:property="og:description"|name="description") content="([^"]*)"', html)
        meta["summary"] = m.group(1).strip() if m else ""

    thumb = meta.get("thumbnail") or "images/thumb.png"
    meta["thumbnail"] = thumb if (issue["dirpath"] / thumb).is_file() else None
    return meta


def head_extras(prefix, page_url, title):
    return f"""
<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
<link rel="apple-touch-icon" href="{prefix}favicon.svg">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="世界のAIニュースを日本語で、毎朝6:00にお届け">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{SITE_URL}ogp.png">
<meta name="twitter:card" content="summary_large_image">
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
"""


def inject_before_body(html, snippet):
    if re.search(r"</body>", html, flags=re.IGNORECASE):
        return re.sub(r"</body>", lambda m: snippet + "</body>", html, count=1, flags=re.IGNORECASE)
    return html + snippet


def inject_into_head(html, snippet):
    if re.search(r"</head>", html, flags=re.IGNORECASE):
        return re.sub(r"</head>", lambda m: snippet + "</head>", html, count=1, flags=re.IGNORECASE)
    return snippet + html


def enhance_issue(issue, meta):
    """号ページに favicon/OGP・shared.css・共有バーを未注入なら差し込む。"""
    html = original = issue["html_path"].read_text(encoding="utf-8")
    page_url = f"{SITE_URL}contents/{issue['dirname']}/"
    title = f"{SITE_TITLE} {format_date_ja(issue['date'])}"

    if "favicon.svg" not in html:
        html = inject_into_head(html, head_extras(ISSUE_PREFIX, page_url, title))
    if "shared.css" not in html:
        html = inject_into_head(html, f'\n<link rel="stylesheet" href="{ISSUE_PREFIX}css/shared.css">\n')
    if "ai-news-sharebar" not in html:
        html = inject_before_body(
            html, SHARE_BAR + f'<script src="{ISSUE_PREFIX}js/shared.js" defer></script>\n'
        )

    if html != original:
        issue["html_path"].write_text(html, encoding="utf-8")
        print(f"contents/{issue['dirname']}/index.html に共有バー/メタ情報を注入しました")


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def build_card(issue, meta, is_latest):
    href = f"contents/{issue['dirname']}/"
    date_ja = format_date_ja(issue["date"])
    new_badge = '<span class="post-new">NEW</span>' if is_latest else ""
    if meta["thumbnail"]:
        thumb = (f'<img class="post-thumb" src="{href}{meta["thumbnail"]}" '
                 f'alt="" loading="lazy" '
                 "onerror=\"this.outerHTML='<div class=&quot;post-thumb-ph&quot;>📰</div>'\">")
    else:
        thumb = '<div class="post-thumb-ph">📰</div>'
    return f"""      <a class="post-card" href="{href}">
        {thumb}
        <div class="post-body">
          <div class="post-date">{date_ja}{new_badge}</div>
          <h3 class="post-title">{escape(meta["title"])}</h3>
          <p class="post-summary">{escape(meta["summary"])}</p>
          <span class="post-more">続きを読む →</span>
        </div>
      </a>"""


def main():
    issues = collect_issues()
    cards = []
    for i, issue in enumerate(issues):
        meta = load_meta(issue)
        enhance_issue(issue, meta)
        cards.append(build_card(issue, meta, i == 0))

    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("{{CARDS}}", "\n".join(cards) if cards else
                            '      <p class="posts-empty">まだ号がありません。明日の朝6:00をお楽しみに。</p>')
    html = html.replace("{{COUNT}}", str(len(issues)))
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html を生成しました(全{len(issues)}号)")


if __name__ == "__main__":
    main()
