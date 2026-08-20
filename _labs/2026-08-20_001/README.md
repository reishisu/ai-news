# 2026/08/20号の検証記録

## 何を確かめたか

- **表示検証**: `layout_qa.py` で幅380px/900pxを実測。
  `scrollWidth - innerWidth` は両幅とも0、`.code`/`.table` のはみ出し0、JS例外(pageerror)0件。
  console error 3件(goatcounter・giscus・faviconの外部読み込み失敗)は
  file://実行かつegress制限の環境起因で、公開済みの前号(2026-08-19_001)でも同一に出ることを確認した。
  初回実行では参考文献の注記にある長い連続トークン
  (`developer.android.com/reference/kotlin/...` のパス)が380pxで193pxはみ出した。
  折り返せる表現に書き換えて解消。
- **事実検証**: 掲載11件すべてを、収集担当(source-hunter役)と別の
  fact-verifier役エージェントが一次資料の本文で照合した。主な修正:
  - Agent Lightning: 「LangChain/CrewAIなど」は一次資料に登場しないため削除(公式の例はAutoGen)
  - androidx.webkit: `navigate()` 等は実験的(Opt-in)APIで `isFeatureSupported()` 必須、を追記
  - CoSnitch: 対象は個人向けCopilot限定(M365 Copilotは別件SearchLeak)、を明記
  - OpenAI ZDR/PSP: 公式ブログが403で未読のため、X公式投稿と添付図解で確認できた範囲だけを掲載
  - TiDB: 「これまでAWSのみ」という履歴の断定をやめ、現在の対応一覧の記述に変更
- **URL検証**: 掲載16 URLに `curl -sSL -o /dev/null -w '%{http_code}'`。
  15件が200、OpenAIブログのみ403(記事内で「未確認」ラベルとして明示)。

## 動かし方

```bash
python3 _labs/2026-08-20_001/layout_qa.py contents/2026-08-20_001/index.html
```

## 実行環境

- 2026-08-20 JST、リポジトリの定期実行コンテナ(Linux)
- Python 3 + playwright(pip) + chromium /opt/pw-browsers/chromium
- 実行結果は加工せずそのまま判定に使った(数値の手修正なし)
