# Claude Code 週間上限の実測

2026年9月1日11:54:41 JSTに、次のコマンドで Claude Code のローカル利用ログをブロック別に集計した。

```text
npx --yes ccusage@latest blocks --timezone Asia/Tokyo --json
```

使用版は `ccusage 20.0.20`。公開用の生データは [ccusage-completed-blocks.json](ccusage-completed-blocks.json) に置いた。元出力のうち、計算に使った `startTime` / `actualEndTime` / `entries` / `outputTokens` / `totalTokens` だけを抜き出している。値は書き換えていない。

取得時点で進行中のブロックが1件あった。値が増加中で再現性がないため、値ごと除外した。利用のない gap 行も除外した。選択条件は `isGap == false AND isActive == false`。

## 集計

```text
完了済みブロック              7
entries                         1,901
outputTokens                1,192,402
totalTokens               642,703,163
1ブロック平均 totalTokens     91,814,738
観測窓                     39:20:07.599
```

観測窓は、最初の `startTime` から最後の `actualEndTime` まで。141,607.599秒。

## 週への単純換算

```text
1週間                         604,800秒
週換算係数     604,800 / 141,607.599
                             = 4.270957239

ブロック数       7 * 4.270957239
                             = 29.8967
                             ≈ 30ブロック/週
```

現在を標準上限の150%、9月14日以降を125%とすると、現状比の減少は次のとおり。

```text
(1.50 - 1.25) / 1.50 = 1/6 = 16.666...%

29.8967 / 6          = 4.9828
                      ≈ 5ブロック/週
```

これは、同じ負荷と同じペースが続き、いまの週間上限を使い切る場合の試算。ccusage の `totalTokens` は契約上限の残量ではなく、ブロックは作業回数の保証でもない。そのため「実測した使い方を同じ比率で縮めた目安」として使う。

このディレクトリには、公開用の5フィールドと計算条件だけを収録している。
