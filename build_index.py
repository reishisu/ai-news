#!/usr/bin/env python3
"""ai-news-YYYY-MM-DD.html の最新号から index.html を生成するスクリプト。

- 同じディレクトリの ai-news-YYYY-MM-DD.html を日付降順で列挙
- 最新号のHTMLに以下を差し込んで index.html として保存:
  - <head>: favicon / OGP・Twitterカードメタ(未設定の場合のみ)
  - </body> 直前: 「📚 過去の号一覧」セクション + SNS共有フローティングバー
  - <title> を「AIニュース デイリーダイジェスト」に置換
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
  <style>
    #ai-news-archive {{
      max-width: 820px; margin: 40px auto 32px; padding: 0 16px;
      font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
      --an-card: #fcfcfb; --an-text: #0b0b0b; --an-muted: #52514e;
      --an-border: rgba(11,11,11,0.10); --an-accent: #2a78d6;
      color: var(--an-text);
    }}
    @media (prefers-color-scheme: dark) {{
      #ai-news-archive {{
        --an-card: #1a1a19; --an-text: #ffffff; --an-muted: #c3c2b7;
        --an-border: rgba(255,255,255,0.10); --an-accent: #3987e5;
      }}
    }}
    #ai-news-archive h2 {{ font-size: 1.25em; margin: 0 0 14px; }}
    #ai-news-archive .an-grid {{ display: grid; gap: 10px; }}
    #ai-news-archive .an-item {{
      display: flex; align-items: center; gap: 10px;
      padding: 14px 18px; border-radius: 14px;
      background: var(--an-card); border: 1px solid var(--an-border);
      border-left: 5px solid var(--an-accent);
      color: var(--an-text); text-decoration: none;
      transition: transform .16s ease, box-shadow .16s ease;
    }}
    #ai-news-archive .an-item:hover {{
      transform: translateX(4px);
      box-shadow: 0 8px 22px -14px rgba(23,43,88,.55);
    }}
    #ai-news-archive .an-date {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
    #ai-news-archive .an-label {{ color: var(--an-muted); font-size: .92em; }}
    #ai-news-archive .an-new {{
      margin-left: 8px; padding: 2px 9px; border-radius: 999px;
      background: var(--an-accent); color: #fff; font-size: .72em; font-weight: 800;
      vertical-align: 1px;
    }}
    #ai-news-archive .an-arrow {{ margin-left: auto; color: var(--an-accent); font-weight: 700; }}
    @media (max-width: 600px) {{
      #ai-news-archive .an-item {{ flex-wrap: wrap; padding: 12px 14px; }}
      #ai-news-archive .an-arrow {{ display: none; }}
    }}
  </style>
  <h2>📚 過去の号一覧</h2>
  <nav class="an-grid">
{links}
  </nav>
</section>
"""


SHARE_BAR = f"""
<!-- ai-news-sharebar -->
<div id="ai-news-sharebar" aria-label="SNSでシェア">
  <style>
    #ai-news-sharebar {{
      position: fixed; right: 16px; bottom: 16px; z-index: 9999;
      display: flex; flex-direction: column; gap: 8px;
      font-family: system-ui, -apple-system, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
      --sb-bg: rgba(255,255,255,0.92); --sb-border: rgba(11,11,11,0.12); --sb-text: #0b0b0b;
    }}
    @media (prefers-color-scheme: dark) {{
      #ai-news-sharebar {{ --sb-bg: rgba(26,26,25,0.92); --sb-border: rgba(255,255,255,0.14); --sb-text: #ffffff; }}
    }}
    #ai-news-sharebar .sb-toggle, #ai-news-sharebar .sb-btn {{
      width: 48px; height: 48px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      background: var(--sb-bg); border: 1px solid var(--sb-border); color: var(--sb-text);
      cursor: pointer; text-decoration: none;
      box-shadow: 0 8px 24px -10px rgba(0,0,0,.45);
      backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
      transition: transform .16s ease;
      font-size: 0;
    }}
    #ai-news-sharebar .sb-toggle:hover, #ai-news-sharebar .sb-btn:hover {{ transform: scale(1.1); }}
    #ai-news-sharebar .sb-btn svg, #ai-news-sharebar .sb-toggle svg {{ width: 20px; height: 20px; }}
    #ai-news-sharebar .sb-menu {{ display: none; flex-direction: column; gap: 8px; }}
    #ai-news-sharebar.open .sb-menu {{ display: flex; animation: sb-pop .22s ease both; }}
    @keyframes sb-pop {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    #ai-news-sharebar .sb-toast {{
      position: fixed; right: 76px; bottom: 28px;
      padding: 8px 14px; border-radius: 10px;
      background: var(--sb-bg); border: 1px solid var(--sb-border); color: var(--sb-text);
      font-size: 13px; font-weight: 600; white-space: nowrap;
      opacity: 0; pointer-events: none; transition: opacity .25s ease;
    }}
    #ai-news-sharebar .sb-toast.show {{ opacity: 1; }}
  </style>
  <div class="sb-menu">
    <a class="sb-btn" data-share="x" target="_blank" rel="noopener" title="Xで共有"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.9 1.15h3.68l-8.04 9.19L24 22.85h-7.41l-5.8-7.58-6.64 7.58H.47l8.6-9.83L0 1.15h7.59l5.24 6.93 6.07-6.93Zm-1.29 19.5h2.04L6.49 3.24H4.3l13.31 17.41Z"/></svg></a>
    <a class="sb-btn" data-share="line" target="_blank" rel="noopener" title="LINEで送る"><svg viewBox="0 0 24 24" fill="#06C755"><path d="M12 2C6.48 2 2 5.64 2 10.12c0 4.02 3.57 7.39 8.39 8.03.33.07.77.22.89.5.1.26.07.66.03.92l-.14.86c-.04.26-.2 1 .88.55 1.08-.46 5.8-3.42 7.92-5.85C21.53 13.55 22 11.92 22 10.12 22 5.64 17.52 2 12 2Z"/></svg></a>
    <a class="sb-btn" data-share="fb" target="_blank" rel="noopener" title="Facebookで共有"><svg viewBox="0 0 24 24" fill="#1877F2"><path d="M24 12.07C24 5.4 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.09 10.13 24v-8.44H7.08v-3.49h3.05V9.41c0-3.02 1.79-4.7 4.53-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.51c-1.49 0-1.96.93-1.96 1.89v2.26h3.33l-.53 3.49h-2.8V24C19.61 23.09 24 18.1 24 12.07Z"/></svg></a>
    <a class="sb-btn" data-share="hatena" target="_blank" rel="noopener" title="はてなブックマーク"><svg viewBox="0 0 24 24" fill="#00A4DE"><path d="M20.47 0H3.53A3.53 3.53 0 0 0 0 3.53v16.94A3.53 3.53 0 0 0 3.53 24h16.94A3.53 3.53 0 0 0 24 20.47V3.53A3.53 3.53 0 0 0 20.47 0ZM12.1 17.1c-.9.99-2.28 1.2-3.36 1.2H5.18V5.72h3.4c1.09 0 2.32.13 3.13 1 .65.7.77 1.51.77 2.19 0 .84-.34 1.64-1.11 2.13 1.02.42 1.62 1.4 1.62 2.66 0 .96-.28 2.4-.9 3.4Zm5.32 1.2a1.53 1.53 0 1 1 0-3.06 1.53 1.53 0 0 1 0 3.06Zm1.24-4.3h-2.48V5.72h2.48V14Z"/></svg></a>
    <button class="sb-btn" data-share="copy" type="button" title="リンクをコピー"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></button>
  </div>
  <button class="sb-toggle" type="button" title="シェア" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></svg></button>
  <div class="sb-toast" role="status"></div>
  <script>
  (function () {{
    var bar = document.getElementById("ai-news-sharebar");
    var toggle = bar.querySelector(".sb-toggle");
    var toast = bar.querySelector(".sb-toast");
    var url = location.href.split("#")[0];
    var title = document.title || {SITE_TITLE!r};
    var u = encodeURIComponent(url), t = encodeURIComponent(title);
    var links = {{
      x: "https://twitter.com/intent/tweet?text=" + t + "&url=" + u,
      line: "https://social-plugins.line.me/lineit/share?url=" + u,
      fb: "https://www.facebook.com/sharer/sharer.php?u=" + u,
      hatena: "https://b.hatena.ne.jp/entry/panel/?url=" + u + "&btitle=" + t
    }};
    bar.querySelectorAll("[data-share]").forEach(function (el) {{
      var kind = el.getAttribute("data-share");
      if (links[kind]) el.href = links[kind];
    }});
    function showToast(msg) {{
      toast.textContent = msg; toast.classList.add("show");
      setTimeout(function () {{ toast.classList.remove("show"); }}, 2000);
    }}
    bar.querySelector('[data-share="copy"]').addEventListener("click", function () {{
      (navigator.clipboard ? navigator.clipboard.writeText(url) : Promise.reject())
        .then(function () {{ showToast("リンクをコピーしました ✓"); }})
        .catch(function () {{ window.prompt("このURLをコピーしてください", url); }});
    }});
    toggle.addEventListener("click", function () {{
      if (navigator.share && !bar.classList.contains("open")) {{
        navigator.share({{ title: title, url: url }}).catch(function () {{
          bar.classList.add("open"); toggle.setAttribute("aria-expanded", "true");
        }});
        return;
      }}
      var open = bar.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    }});
  }})();
  </script>
</div>
"""


def inject_before_body(html, snippet):
    if re.search(r"</body>", html, flags=re.IGNORECASE):
        return re.sub(r"</body>", lambda m: snippet + "</body>", html, count=1, flags=re.IGNORECASE)
    return html + snippet


def enhance(html, page_url, title):
    """favicon/OGPメタと共有バーを未注入なら差し込む。"""
    if "favicon.svg" not in html and re.search(r"</head>", html, flags=re.IGNORECASE):
        html = re.sub(
            r"</head>",
            lambda m: head_extras(page_url, title) + "</head>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
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
