#!/usr/bin/env python3
"""公式ドキュメントから、記事の根拠にする文を機械的に抜き出す。

手で書き写すと誤りが入るので、必ずこのスクリプト経由で取る。
取得済みの .md は docs.aws.amazon.com が配信している
Markdown 版（HTMLページ内の "View a markdown version of this page"
と同じもの）。
"""
import datetime
import re

BASE_IAM = "https://docs.aws.amazon.com/IAM/latest/UserGuide/"
BASE_API_IAM = "https://docs.aws.amazon.com/IAM/latest/APIReference/"
BASE_API_STS = "https://docs.aws.amazon.com/STS/latest/APIReference/"

ITEMS = [
    ("Effectは大文字小文字を区別する",
     "reference_policies_elements_effect.md", BASE_IAM,
     r"The `Effect` element is required.*?case sensitive\."),
    ("既定は暗黙のDeny／明示Denyが明示Allowに勝つ",
     "reference_policies_evaluation-logic_policy-eval-denyallow.md", BASE_IAM,
     r"\+ By default, all requests are implicitly denied.*?"
     r"\+ An explicit deny overrides an explicit allow\."),
    ("アイデンティティベースと リソースベースは和集合",
     "reference_policies_evaluation-logic.md", BASE_IAM,
     r"If an action is allowed by an identity-based policy.*?overrides the allow\."),
    ("アクセス許可境界は積集合",
     "reference_policies_evaluation-logic.md", BASE_IAM,
     r"When AWS evaluates the identity-based policies and permissions boundary "
     r"for a user, the resulting permissions are the intersection of the two "
     r"categories\."),
    ("Versionは 2012-10-17 を書く",
     "reference_policies_elements_version.md", BASE_IAM,
     r"the current version of the policy language, and you should always "
     r"include a `Version` element and set it to `2012-10-17`\."),
    ("グループはPrincipalに書けない",
     "reference_policies_elements_principal.md", BASE_IAM,
     r"You cannot identify a user group as a principal in a policy.*?"
     r"authenticated IAM entities\."),
    ("ロールは長期の認証情報を持たない",
     "id_roles.md", BASE_IAM,
     r"Also, a role does not have standard long-term credentials.*?"
     r"for your role session\."),
    ("CreateRole は信頼ポリシーが必須",
     "API_CreateRole.md", BASE_API_IAM,
     r"The trust relationship policy document that grants an entity "
     r"permission to assume the role\."),
    ("AssumeRole の既定セッション時間は3600秒",
     "API_AssumeRole.md", BASE_API_STS,
     r"By default, the value is set to `3600` seconds\."),
    ("AssumeRole は900秒から最大12時間",
     "API_AssumeRole.md", BASE_API_STS,
     r"The value specified can range from 900 seconds \(15 minutes\) up to "
     r"the maximum session duration set for the role\."),
]


def main():
    today = datetime.date.today().isoformat()
    print(f"# 公式ドキュメントからの抜粋（取得日 {today}）\n")
    for title, fname, base, pat in ITEMS:
        s = open(fname, encoding="utf-8").read()
        m = re.search(pat, s, re.S)
        print(f"## {title}")
        print(f"- 出典: {base}{fname.replace('.md', '.html')}")
        if not m:
            print("- 抜粋: **見つからなかった**\n")
            continue
        text = re.sub(r"\s+", " ", m.group(0)).strip()
        print(f"- 原文: {text}\n")


if __name__ == "__main__":
    main()
