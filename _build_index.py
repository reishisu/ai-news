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
import hashlib
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

# CSS/JSはブラウザに強くキャッシュされるため、内容が変わったら別URLになるようにする
VERSIONS = {}
ANALYTICS = ""
COMMENTS = ""
ASSETS = ["css/style.css", "css/article.css", "css/shared.css",
          "js/shared.js", "js/article.js", "js/home.js"]


def asset_versions():
    """{'css/article.css': 'a1b2c3d4', ...} を返す(内容ハッシュの先頭8桁)。"""
    versions = {}
    for rel in ASSETS:
        path = HERE / rel
        if path.is_file():
            versions[rel] = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return versions


PRE_BLOCK = re.compile(r"<pre\b[^>]*>.*?</pre>", re.S | re.I)


def add_cache_busting(html, versions):
    """既存の ?v=... を捨てて、現在の内容ハッシュを付け直す。

    <pre> の中(記事に載せたコード例)は書き換えない。ここを書き換えると
    「変更前」と「変更後」が同じ行になるなど、説明そのものが壊れる。
    """
    def bust(chunk):
        for rel, ver in versions.items():
            name = rel.split("/")[-1]
            chunk = re.sub(
                r'((?:href|src)="[^"]*' + re.escape(name) + r')(?:\?v=[0-9a-f]+)?(")',
                lambda m: f"{m.group(1)}?v={ver}{m.group(2)}",
                chunk,
            )
        return chunk

    out, last = [], 0
    for m in PRE_BLOCK.finditer(html):
        out.append(bust(html[last:m.start()]))
        out.append(m.group(0))          # コード例はそのまま残す
        last = m.end()
    out.append(bust(html[last:]))
    return "".join(out)


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def analytics_snippet():
    """site.json にサイトコードがあればアクセス解析タグを返す(無ければ空)。"""
    conf = load_json(HERE / "site.json", {}).get("analytics") or {}
    code = str(conf.get("code") or "").strip()
    if not code or conf.get("provider") != "goatcounter":
        return ""
    return ('\n<script data-goatcounter="https://' + code + '.goatcounter.com/count"'
            ' async src="//gc.zgo.at/count.js"></script>\n')


def load_popular():
    """_fetch_popular.py が書き出した閲覧数。{dirname: count}"""
    data = load_json(HERE / "popular.json", {})
    counts = {}
    for item in data.get("items", []):
        # 末尾スラッシュ付き・無し・index.html付き・クエリ付きのどれでも拾う
        m = re.search(r"contents/([^/?#]+)", str(item.get("path", "")))
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + int(item.get("count", 0))
    return counts, data.get("updated", "")


def comments_snippet():
    """site.json で有効なら、記事末尾に置くコメント欄(giscus)を返す(無効なら空)。

    GitHub Discussions を保存先にする。バックエンド不要で、投稿内容は
    リポジトリの Discussions にそのまま残るため、あとから移行もできる。
    """
    conf = load_json(HERE / "site.json", {}).get("comments") or {}
    if not conf.get("enabled") or conf.get("provider") != "giscus":
        return ""
    repo = str(conf.get("repo") or "").strip()
    repo_id = str(conf.get("repoId") or "").strip()
    if not repo or not repo_id:
        return ""
    category = str(conf.get("category") or "").strip()
    category_id = str(conf.get("categoryId") or "").strip()
    cat_attrs = ""
    if category:
        cat_attrs += f'\n        data-category="{category}"'
    if category_id:
        cat_attrs += f'\n        data-category-id="{category_id}"'
    return f"""
  <!-- ai-news-comments -->
  <section class="section section-d" id="comments">
    <h2>コメント</h2>
    <article class="item">
      <p class="lead">気づいた点・間違いの指摘・補足があれば書いてください。<mark>特に事実の誤りは歓迎します。</mark></p>
      <p class="lead comment-note">投稿には GitHub アカウントが必要です。書き込みはこのサイトのリポジトリの
        <a href="https://github.com/{repo}/discussions">GitHub Discussions</a> に保存されます。</p>
      <script src="https://giscus.app/client.js"
        data-repo="{repo}"
        data-repo-id="{repo_id}"{cat_attrs}
        data-mapping="pathname"
        data-strict="1"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        data-theme="preferred_color_scheme"
        data-lang="ja"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
      </script>
    </article>
  </section>
"""


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
    meta.setdefault("category", "デイリーダイジェスト")
    tags = meta.get("tags")
    meta["tags"] = ([str(t).replace("|", " ").strip() for t in tags if str(t).strip()]
                    if isinstance(tags, list) else [])
    meta["featured"] = bool(meta.get("featured"))
    meta["_body"] = plain_text(html)
    return meta


TAG_RE = re.compile(r"<(script|style|svg)[^>]*>.*?</\1>", flags=re.DOTALL | re.IGNORECASE)


def plain_text(html, limit=4000):
    """検索用に本文をざっくり平文化する。"""
    text = TAG_RE.sub(" ", html)
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text.replace("&lt;", "<").replace("&gt;", ">")
                .replace("&quot;", '"').replace("&amp;", "&").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", text).strip()[:limit]


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
    # 記事の小物(コピーボタン・進捗バー・クイズ等)
    if "js/article.js" not in html:
        html = inject_before_body(html, f'<script src="{ISSUE_PREFIX}js/article.js" defer></script>\n')
    # コメント欄(site.json で有効なときだけ)。記事の本文の最後に置く
    if COMMENTS and "ai-news-comments" not in html:
        # 本文の直後・フッターの前に置く(フッターが無ければ </main> の直前)
        if re.search(r'<footer class="article-foot">', html):
            html = re.sub(r'<footer class="article-foot">',
                          lambda m: COMMENTS + '\n  <footer class="article-foot">',
                          html, count=1)
        elif re.search(r"</main>", html, flags=re.IGNORECASE):
            html = re.sub(r"</main>", lambda m: COMMENTS + "</main>", html,
                          count=1, flags=re.IGNORECASE)
        else:
            html = inject_before_body(html, COMMENTS)
    # アクセス解析(site.json にコードがあるときだけ)
    if ANALYTICS and "goatcounter" not in html:
        html = inject_before_body(html, ANALYTICS)

    html = add_cache_busting(html, VERSIONS)

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
    tag_chips = "".join(
        f'<span class="post-tag">#{escape(t)}</span>' for t in meta["tags"][:4]
    )
    # タグ名に空白が入るため、区切りは "|"(タグ側の "|" は除去済み)
    tags_attr = escape("|".join(meta["tags"]))
    haystack = escape(" ".join([meta["title"], meta["summary"], meta["category"],
                                " ".join(meta["tags"]), meta["_body"]]).lower())
    return f"""      <a class="post-card" href="{href}"
         data-tags="{tags_attr}" data-category="{escape(meta['category'])}"
         data-date="{issue['date'].isoformat()}" data-search="{haystack}">
        {thumb}
        <div class="post-body">
          <div class="post-date"><span class="post-cat">{escape(meta["category"])}</span>{date_ja}{new_badge}</div>
          <h3 class="post-title">{escape(meta["title"])}</h3>
          <p class="post-summary">{escape(meta["summary"])}</p>
          <div class="post-tags">{tag_chips}</div>
          <span class="post-more">続きを読む →</span>
        </div>
      </a>"""


def build_featured(issues_meta, popular, updated):
    """人気の記事(閲覧数がある場合)。無ければ注目の記事(featured)。どちらも最大3件。"""
    if popular:
        ranked = sorted(
            [x for x in issues_meta if popular.get(x[0]["dirname"])],
            key=lambda x: -popular[x[0]["dirname"]],
        )[:3]
    else:
        ranked = []

    if ranked:
        heading = "🔥 よく読まれている記事"
        note = f'<span class="posts-count">{escape(updated)} 時点</span>' if updated else ""
        cards = []
        for i, (issue, meta) in enumerate(ranked, 1):
            href = f"contents/{issue['dirname']}/"
            views = popular[issue["dirname"]]
            cards.append(f"""        <a class="pick-card" href="{href}">
          <span class="pick-rank">{i}</span>
          <span class="pick-cat">{escape(meta["category"])}</span>
          <span class="pick-title">{escape(meta["title"])}</span>
          <span class="pick-date">{format_date_ja(issue["date"])} ・ {views:,} 回</span>
        </a>""")
    else:
        picked = [x for x in issues_meta if x[1]["featured"]][:3] or issues_meta[:3]
        if not picked:
            return ""
        heading, note = "🔥 注目の記事", ""
        cards = []
        for issue, meta in picked:
            href = f"contents/{issue['dirname']}/"
            cards.append(f"""        <a class="pick-card" href="{href}">
          <span class="pick-cat">{escape(meta["category"])}</span>
          <span class="pick-title">{escape(meta["title"])}</span>
          <span class="pick-date">{format_date_ja(issue["date"])}</span>
        </a>""")

    return f"""  <section class="featured">
    <div class="posts-head"><h2>{heading}</h2>{note}</div>
    <div class="pick-grid">
{chr(10).join(cards)}
    </div>
  </section>
"""


def build_tagbar(issues_meta):
    """出現数の多い順にタグを並べる。"""
    counts = {}
    for _, meta in issues_meta:
        for t in meta["tags"]:
            counts[t] = counts.get(t, 0) + 1
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    chips = ['      <button class="tag-chip is-on" type="button" data-tag="">すべて</button>']
    for tag, n in ordered:
        chips.append(
            f'      <button class="tag-chip" type="button" data-tag="{escape(tag)}">'
            f'#{escape(tag)}<i>{n}</i></button>'
        )
    return "\n".join(chips)


def main():
    global VERSIONS, ANALYTICS, COMMENTS
    VERSIONS = asset_versions()
    ANALYTICS = analytics_snippet()
    COMMENTS = comments_snippet()
    popular, popular_updated = load_popular()
    issues = collect_issues()
    cards = []
    issues_meta = []
    for i, issue in enumerate(issues):
        meta = load_meta(issue)
        enhance_issue(issue, meta)
        cards.append(build_card(issue, meta, i == 0))
        issues_meta.append((issue, meta))

    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("{{CARDS}}", "\n".join(cards) if cards else
                            '      <p class="posts-empty">まだ記事がありません。明日の朝6:00をお楽しみに。</p>')
    html = html.replace("{{COUNT}}", str(len(issues)))
    html = html.replace("{{FEATURED}}", build_featured(issues_meta, popular, popular_updated))
    html = html.replace("{{TAGBAR}}", build_tagbar(issues_meta))
    if ANALYTICS and "goatcounter" not in html:
        html = inject_before_body(html, ANALYTICS)
    html = add_cache_busting(html, VERSIONS)
    (HERE / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html を生成しました(全{len(issues)}号)")


if __name__ == "__main__":
    main()
