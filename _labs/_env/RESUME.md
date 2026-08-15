# ワークフローが利用上限で止まったときの再開手順

セッションの利用上限に当たると、エージェントが
`You've hit your session limit · resets <時刻>` で失敗します。
**成果は消えません。** 完了済みのエージェントはキャッシュに残っており、
失敗した工程だけを再実行できます。

## 再開のしかた

```
Workflow({
  scriptPath: "<タスク通知に出ている Script file のパス>",
  resumeFromRunId: "<同じく Run ID>"
})
```

同じ (prompt, opts) のエージェントはキャッシュから即座に復帰し、
失敗した工程と、それ以降だけが実際に動きます。

## 現在動かしているワークフロー

| 用途 | scriptPath | runId |
|---|---|---|
| 超基礎シリーズ(Laravel/TiDB/Terraform/AWS/ECS/連携) | `/root/.claude/projects/-home-user-ai-news/218add4d-91bf-5dd6-8681-3e6fbe7a6b0f/workflows/scripts/produce-stack-basics-wf_ab1350dd-825.js` | `wf_ab1350dd-825` |

## 注意

- 上限のリセット時刻はエラーメッセージに書かれている（例: `resets 2am (UTC)`）
- リセット後に再開すること。早すぎると同じ失敗を繰り返す
- 再開前に `git status` を確認し、途中まで書かれた成果があればコミットしておく
