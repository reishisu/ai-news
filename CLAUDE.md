# このリポジトリで記事を書くときの決まり

このサイトの記事を作成・更新するときは、以下に必ず従ってください。
定期実行タスク（毎朝のダイジェスト、週次の連載）にも同じく適用されます。

---

## 1. 嘘を書かないための規律（最優先）

**読んでいない資料は引用しない。** 検索結果の要約スニペットだけを根拠に
「◯◯にはこう書いてある」と書くのは禁止です。

1. 根拠にする資料は、**必ず本文を取得して該当箇所を自分で読む**
   `WebFetch` がegress制限で失敗したら `curl` で取得し、該当箇所を抜き出して確認する
2. 読めなかったものは引用も要約もしない。言及が必要なら「未確認」「書誌のみ照合」と明記する
3. **一次資料を優先する。** 仕様（RFC / WHATWG / W3C）→ 公式ドキュメント → 公式ブログ →
   原論文 の順。まとめ記事・SEOブログ・AI生成記事は根拠にしない
4. 書誌情報は照合できるなら照合する
   - DOIがある論文: `https://api.crossref.org/works/<DOI>` で著者・誌名・ページを確認
   - 書籍: `https://openlibrary.org/api/books?bibkeys=ISBN:<ISBN>&format=json&jscmd=data`
5. 自分の測定結果と、資料に書いてあることは**分けて書く**
6. 数値・バージョン番号・日付は、必ず出どころを確認してから書く。確認できないものは書かない

### 記事末尾に参考文献セクションを必ず置く

```html
<section class="section section-d" id="refs">
  <h2>参考文献</h2>
  <article class="item">
    <p class="lead">この記事の主張は、次の資料と自分の実測だけに基づいています。<mark>読んでいない資料は引用しません。</mark></p>
    <ol class="refs">
      <li>
        <span class="flag primary">一次資料</span>
        著者名「タイトル」<i>媒体名・規格番号</i>, 発行年月.
        <span class="note">参照箇所: 章節番号と、何を根拠にしたか。</span>
        <a href="URL">URL</a>（YYYY年M月D日参照）
      </li>
      <li>
        <span class="flag unverified">未確認</span>
        …（回答の付いていないフォーラム投稿、本文を読めなかった有料論文など。なぜ未確認かを書く）
      </li>
      <li>
        <span class="flag self">自分の実測</span>
        …（環境・日時・測り方。「加工せずそのまま貼った」ことも書く）
      </li>
      <li>
        <span class="flag self">自分の意見</span>
        …（標準や規格ではなく筆者の運用上の目安であることを明記）
      </li>
    </ol>
  </article>
</section>
```

ラベルは3種類だけ: `primary`（一次資料）/ `unverified`（未確認・書誌のみ照合）/ `self`（自分の実測・自分の意見）。
目次（`.toc`）にも「参考文献」の行を足すこと。

---

## 2. 読ませる工夫は「装飾」ではなく「中身」で作る

読者は集中が続かないタイプです。ただし**飾りを足しても読まれません。**
次のやり方で引き込みます。

- **仕様や公式ドキュメントの原文を、実測結果のすぐ隣に貼る。**
  「実際にこうなった → 規格にこう書いてある」の並びが一番効く
- **見出しに結論を書く。**「〜について」ではなく「〜しても1日も縮まない」
- **意外な事実を早く出す。** 引っ張らない
- **失敗と事故を正直に書く。** うまくいかなかったログが一番読まれる
- **1段落3行以内。1文を短く**
- クイズ・チェックリスト・`next-up` は使ってよい（内容と結びついているため）

### 禁止（ノイズなので入れない）

- `<div class="stats">` のような**大きな数字を並べるだけのブロック**。`data-count` 属性も使わない
- 優先度やタグの意味を説明する文章
- 見出しの先頭に付ける `B.` のような記号
- 記事HTMLへの `<style>` の直書き
- 本文へのインラインSVG（図版はPNGのみ）

---

## 3. サイト構成

トップページ `index.html` は `_build_index.py` が自動生成します。**直接編集しないこと。**

```
index.html            # 自動生成
css/style.css         # ホーム用
css/article.css       # 記事共通 ← 記事HTMLはこれを読み込むだけ
css/shared.css        # 共有バー(自動注入)
js/home.js            # 検索・タグ絞り込み
js/article.js         # 記事の仕掛け(自動注入。記事側で読み込み不要)
contents/YYYY-MM-DD_スラッグ/
    index.html / meta.json / images/ / _figures/
_templates/home.html  # ホームのテンプレート
_build_index.py       # サイトビルダー
_render_figures.py    # SVG → PNG(ライト/ダーク)
_fetch_popular.py     # GoatCounterから閲覧数取得
```

`_` 始まりはGitHub Pages（Jekyll）の公開対象外です。

### 使えるクラス（css/article.css）

| 用途 | 書き方 |
|---|---|
| 本文 | `<p class="lead">`、強調は `<mark>` |
| 要点 | `<ul class="points"><li><b>見出し。</b>説明</li></ul>` |
| コード | `<div class="code"><div class="code-head">名前</div><pre>…</pre></div>` |
| 実行結果 | `<div class="code term">` ＋ `<span class="ok-line">` / `<span class="ng-line">` |
| 日本語の塊 | `<div class="code wrap">`（折り返す） |
| 表 | `<div class="table"><table>…</table></div>` |
| クイズ | `<div class="quiz">` ＋ `<button class="opt" data-correct="true">` ＋ `<p class="ans" hidden>` |
| チェックリスト | `<ul class="checklist" data-key="一意なキー">` ＋ `<span class="cl-count">0 / 3</span>` |
| 次の記事 | `<a class="next-up">` |

**表は2列目以降の `<td>` に必ず `data-label="列名"` を付けること。**
幅620px以下では見出し行が消えて縦積みになるため、これが無いと何の値か分からなくなります。

`<pre>` 内では `<` を `&lt;`、`>` を `&gt;`、`&` を `&amp;` にエスケープします。

---

## 4. ターミナル出力の幅

**1行を短くすること。** 幅380pxの画面で横スクロールせずに読める長さ
（全角なら20文字程度、半角なら40文字程度）に収める。

長くなる場合は、**スクリプト側の出力形式を先に直してから実行し直す**こと。
出力を手で書き換えるのは禁止（それは嘘になります）。列を減らす、2行に分ける、
ラベルを短くする、で対応します。

---

## 5. 図版は必ずPNG

1. `contents/<記事>/_figures/名前.svg` を作る。色は直書きせず
   `var(--fg)` `var(--sub)` `var(--new)` `var(--old)` `var(--track)` `var(--b)/--c/--a/--d` を使う
2. `python3 _render_figures.py <記事ディレクトリ名>` でライト用とダーク用のPNGを生成
3. HTMLは `<picture>` で出し分ける

```html
<figure>
  <picture>
    <source srcset="images/名前-dark.png" media="(prefers-color-scheme: dark)">
    <img src="images/名前.png" alt="図が示していること" loading="lazy">
  </picture>
  <figcaption>読み取れることを1行</figcaption>
</figure>
```

生成したPNGは **Read で開いて目視確認**すること（文字のはみ出し・重なりがないか）。
図版は2〜3点。装飾イラストは作らない。

---

## 6. meta.json

```json
{
  "category": "カテゴリ名",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "featured": true,
  "title": "記事のh1と同じ",
  "summary": "3〜4文(120〜200字)",
  "thumbnail": "images/thumb.png"
}
```

- `category`: デイリーダイジェスト / AIで作る技術 / Web開発・インフラ / クライアント技術 / チームで作る技術
- `tags`: 3〜6個。**既存タグを優先して使い回す**（`cat contents/*/meta.json | grep -A8 '"tags"'`）。`|` は使わない
- サムネイル生成:
  ```
  /opt/pw-browsers/chromium --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --window-size=1200,630 --screenshot=contents/<記事>/images/thumb.png \
    "file://$PWD/contents/<記事>/index.html"
  ```

---

## 7. 公開前の検証（必須）

ヘッドレスブラウザで記事を**幅380pxと900px**で開き、実測する。

- `document.documentElement.scrollWidth - window.innerWidth` が 0
- `.code` と `.table` が画面外にはみ出していない
- `.code pre` に背景色が付いている（CSSが効いている）
- JSエラーが0件（`pageerror` と console error を拾う）
- クイズをクリックすると解説が出る／チェックを入れるとカウントが動く

崩れていたら直してから公開すること。

---

## 8. 公開手順

コミットメッセージは**日本語**で書きます。

```bash
git checkout main && git pull origin main
python3 _render_figures.py <記事ディレクトリ名>
python3 _build_index.py
git add -A && git commit -m "日本語のメッセージ"
git push -u origin main
```

- push が失敗したら 2/4/8/16秒 間隔で最大4回リトライ
- `rejected (fetch first)` なら `git pull origin main --no-edit` してから再push
- **検証必須**: `git ls-remote origin main` と `git rev-parse HEAD` の一致を確認する。
  一致するまで未完了

定期実行タスクは main へ直接pushします（リポジトリ所有者が明示的に許可済み）。
システム側で別の作業ブランチが指定されていても、main へpushしてください。PRは作りません。
