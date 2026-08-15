# 公式ドキュメントからの抜粋（取得日 2026-08-15）

## Effectは大文字小文字を区別する
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_effect.html
- 原文: The `Effect` element is required and specifies whether the statement results in an allow or an explicit deny. Valid values for `Effect` are `Allow` and `Deny`. The `Effect` value is case sensitive.

## 既定は暗黙のDeny／明示Denyが明示Allowに勝つ
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html
- 原文: + By default, all requests are implicitly denied with the exception of the AWS account root user, which has full access. + Requests must be explicitly allowed by a policy or set of policies following the evaluation logic below to be allowed. + An explicit deny overrides an explicit allow.

## アイデンティティベースと リソースベースは和集合
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- 原文: If an action is allowed by an identity-based policy, a resource-based policy, or both, then AWS allows the action. An explicit deny in either of these policies overrides the allow.

## アクセス許可境界は積集合
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
- 原文: When AWS evaluates the identity-based policies and permissions boundary for a user, the resulting permissions are the intersection of the two categories.

## Versionは 2012-10-17 を書く
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_version.html
- 原文: the current version of the policy language, and you should always include a `Version` element and set it to `2012-10-17`.

## グループはPrincipalに書けない
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html
- 原文: You cannot identify a user group as a principal in a policy (such as a resource-based policy) because groups relate to permissions, not authentication, and principals are authenticated IAM entities.

## ロールは長期の認証情報を持たない
- 出典: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html
- 原文: Also, a role does not have standard long-term credentials such as a password or access keys associated with it. Instead, when you assume a role, it provides you with temporary security credentials for your role session.

## CreateRole は信頼ポリシーが必須
- 出典: https://docs.aws.amazon.com/IAM/latest/APIReference/API_CreateRole.html
- 原文: The trust relationship policy document that grants an entity permission to assume the role.

## AssumeRole の既定セッション時間は3600秒
- 出典: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
- 原文: By default, the value is set to `3600` seconds.

## AssumeRole は900秒から最大12時間
- 出典: https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
- 原文: The value specified can range from 900 seconds (15 minutes) up to the maximum session duration set for the role.

