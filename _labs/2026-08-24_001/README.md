# 2026-08-24_001 の検証一式

## 何を確かめたか

この号は掲載2件の小さな号です。**「探さなかった」のではなく「探したが無かった」**
ことを示すための実測を、記事の `#quiet` 節に載せています。その再現手順がここです。

| 確かめたこと | 結論 | 手順 |
|---|---|---|
| AWS に対象期間の告知があるか | 0件（最新は8/22 5:11 JST） | `verify_sources.sh` 手順1 |
| Chrome に対象期間の新規リリースがあるか | 0件（最新は8/21のDev channel） | `verify_sources.sh` 手順2 |
| Claude Code 2.1.241 は載せるべきか | 載せない（変更行1・Added等0） | `verify_sources.sh` 手順3 |

対象期間: **2026-08-23 05:00 〜 2026-08-24 05:00 JST**
（＝ 2026-08-22 20:00 〜 2026-08-23 20:00 UTC）。日本時間の日曜まるごと。

## 動かし方

```bash
bash _labs/2026-08-24_001/verify_sources.sh   # 出典の確認
python3 _labs/2026-08-24_001/qa.py            # 幅380px/900pxの表示検証
```

`qa.py` は号のディレクトリ名を1箇所書き換えるだけで使い回せます。

## つまずいた点（次回への申し送り）

### 1. AWS の RSS は、先頭の `<pubDate>` を見てはいけない

フィードの先頭にある `<pubDate>` は**チャンネル自身の生成時刻**で、取得するたびに
「今」になります。今回の取得では `Sun, 23 Aug 2026 20:03:01 GMT` が返り、
これを最新記事の日付と読むと**「期間内に新着あり」と誤判定します。**
必ず `<item>` の中の `<pubDate>` だけを見ること。`verify_sources.sh` は
item だけを抜くように直してあります。

### 2. github.com は403。jsDelivr を使う

Claude Code の CHANGELOG は
`https://cdn.jsdelivr.net/gh/anthropics/claude-code@main/CHANGELOG.md` で取れます。
403は「到達できなかった」であって「無い」ではありません（CLAUDE.md 第18節）。

### 3. X(旧Twitter)のタイムラインが取得できなかった

`cdn.syndication.twimg.com` 系の経路が、今回は**本文0バイトまたは429**を返しました。
そのため本号の「0件」は X を含みません。記事の参考文献に `unverified` として明記済みです。
**次回も同じなら、取得経路を作り直す必要があります。**

### 4. `_fetch_popular.py` が HTTP 404

`GOATCOUNTER_TOKEN` は設定されているのに404が返ります。`popular.json` は
8/21 のものが残ったままです。ビルドは通るので非致命ですが、放置すると
ホームの閲覧数が古いままになります。

## 実行環境

- Linux / Python 3
- 取得はすべて `curl`（この環境からの実行。2026年8月24日）

## 追記: Chromeの「Stable Cut」と「Stable Release」を取り違えないこと

2週サイクルの告知ページ（`developer.chrome.com/blog/chrome-two-week-release`）の表は
**5段**ある。上から3段目までで読むのをやめると、日付を1つずらして読んでしまう。

```
Stage                  M153 (Old)   M153 (New)   M154 (Old)   M154 (New)
Branch                 Mon, Aug 24  Mon, Aug 17  Mon, Sep 21  Mon, Aug 31
Beta Promotion         Wed, Aug 26  Wed, Aug 19  Wed, Sep 23  Wed, Sep 2
Stable Cut             Tue, Sep 8   Tue, Aug 25  Tue, Oct 6   Tue, Sep 8
Early Stable Release   Wed, Sep 9   Wed, Aug 26  Wed, Oct 7   Wed, Sep 9
Stable Release         Tue, Sep 22  Tue, Sep 8   Tue, Oct 20  Tue, Sep 22
```

**記事が言う「安定版の日付」は最下段の `Stable Release`** で、M153(New)=9月8日、
M154(New)=9月22日。Chromium Dashboard の `stable_date`（`2026-09-08` / `2026-09-22`）と一致する。
`Stable Cut`（M153新=8月25日）を安定版の日付と読むと**2週間ずれる**。

本文の「Chrome 153 の安定版は9月8日」は、次の2つが一致することを確認して書いた。

```bash
curl -s 'https://chromiumdash.appspot.com/fetch_milestone_schedule?mstone=153' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['mstones'][0]['stable_date'])"
# -> 2026-09-08T00:00:00
```

同ページの本文にも "starting from the stable release of Chrome 153 on September 8th" とある。
なお Extended Stable は**8週サイクルのまま据え置き**と明記されている。
