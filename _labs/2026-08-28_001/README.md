# 2026-08-28_001（AI-news 8/28号）の検証記録

## 何を確かめたか

1. **Claude Code 2.1.248 の `--restricted` が実在し、宣伝どおりに振る舞うか**
   - `claude --version` が 2.1.248 であること（環境に最初から入っていたものを更新せず使用）
   - `claude --help` に `--restricted` の項があること
   - `--restricted` と `--permission-mode bypassPermissions` を同時に渡すと、
     **警告して続行するのではなく終了コード1で止まる**こと

2. **`git ls-files` で、追跡下にある認証情報らしきファイルを数えられるか**
   - この記事のリポジトリでは 0 件
   - 対照実験として、`prod.tfvars` を1つ `git add` した空リポジトリで 1 件になること

## 動かし方

```bash
export COLUMNS=40
claude --version
claude --help | sed -n '175,189p'
claude --restricted --permission-mode bypassPermissions -p "say hi"; echo "[exit $?]"

git ls-files | grep -cE '\.tfvars$|prod\.env|\.pem$|id_rsa'
```

出力は `restricted.txt`（記事に貼ったものと同一）。

## 実行環境

- 2026年8月28日 JST 午前、この記事を書いたコンテナ（Linux 6.18.44）
- Claude Code 2.1.248
- 幅は `COLUMNS=40` で取得

## 幅について（CLAUDE.md 第4節）

- `claude --help` は左に40桁の固定の溝を持つため、`COLUMNS=40` を指定しても幅40に収まらない。
  そのため**記事には `--help` の生出力を貼らず**、公式ドキュメント（`code.claude.com/docs/en/cli-reference`）の
  原文を引用した
- `Error: bypassPermissions not supported in restricted mode` は1行53桁で幅40を超えるが、
  **プログラムの出力なので書き換えていない**。`.code` は自分の中で横スクロールする

## やっていないこと

- `--restricted` で実際にAPIを叩くセッションは起こしていない（起動前に止まる挙動だけを確認した）
- `/ultrareview` もクラウドセッションも動かしていない。CHANGELOGの記述と、
  公式ドキュメントの「bundle には追跡下ファイルの未コミット変更が入る」という記述を
  突き合わせただけである
- AWS・Google Play Console・VRChat のいずれにもログインしていない。
  しきい値の表と日付は公式ページの本文から読み取ったもの

## 3. 引用が原文と一字一句合っているかの照合（`check_quotes.py`）

CLAUDE.md 第2節の「原文は一字も変えないこと」を、目視ではなくコードで確かめる。

```bash
python3 check_quotes.py ../../contents/2026-08-28_001/index.html <原典ファイル...>
```

**この号でこれを回したところ、3種類の改変が見つかった。**

| 改変 | 何をしていたか |
|---|---|
| 記号の置換 | Cowork の引用で、原文の `→` を `>` に書き換えていた |
| 記号の追加 | 公式ドキュメントの引用に、原文に無いバッククォート（`` `git add` ``）を足していた |
| 文字の正規化 | 3か所で、原文のアポストロフィ `’`（U+2019）を ASCII の `'` に置き換えていた |

**どれも読めば意味は通るので、目視では気づけない。** 修正後は不一致0件。

### 一次資料を `/tmp` にキャッシュして使い回すときの落とし穴

照合の途中で `/tmp/cc.md`（Claude Code の CHANGELOG）が、**先頭が 2.1.247 の
古い版に入れ替わっていた**。並行して走らせた調査エージェントが同じパスへ
書いた可能性が高い。そのままだと「2.1.248 の該当行が存在しない」という
誤った結論になる。

**照合の直前に、キャッシュではなく一次資料を取り直すこと。**
取り直した結果、2.1.248 のブロックは 49行（Fixed 30 / Added 7 / Improved 5 /
Changed 5 / [VSCode] 1 / Windows 1）で、引用した行も原文どおり存在した。

### 取り直しから照合までの一式

```bash
cd _labs/2026-08-28_001
./fetch_sources.sh                     # 一次資料13点を no-cache で取り直す
python3 check_quotes.py ../../contents/2026-08-28_001/index.html src/*
```

`creators.vrchat.com` と `ask.vrchat.com` は User-Agent が無いと403を返すので、
`fetch_sources.sh` が付けている。`www.php.net` は断続的にTLS接続リセットを返すので、
失敗したら数回やり直すこと。
