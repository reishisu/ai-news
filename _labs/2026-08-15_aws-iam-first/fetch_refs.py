#!/usr/bin/env python3
"""記事の根拠にする公式データを取り直す。

1. AWS Service Reference API（アクション名・条件キーの機械可読データ）
2. AWS公式ドキュメントの Markdown 版
   （HTMLページ上部の "View a markdown version of this page" と同じもの。
     .html を .md に変えたURLで取れる）
"""
import subprocess
import sys

SVCREF = "https://servicereference.us-east-1.amazonaws.com"
IAM_UG = "https://docs.aws.amazon.com/IAM/latest/UserGuide"
IAM_API = "https://docs.aws.amazon.com/IAM/latest/APIReference"
STS_API = "https://docs.aws.amazon.com/STS/latest/APIReference"
ECS_DG = "https://docs.aws.amazon.com/AmazonECS/latest/developerguide"
SDKREF = "https://docs.aws.amazon.com/sdkref/latest/guide"
MANAGED = "https://docs.aws.amazon.com/aws-managed-policy/latest/reference"

JOBS = [
    (f"{SVCREF}/", "svcref-index.json"),
    (f"{SVCREF}/v1/s3/s3.json", "svcref-s3.json"),
    (f"{SVCREF}/v1/sts/sts.json", "svcref-sts.json"),
    (f"{SVCREF}/v1/iam/iam.json", "svcref-iam.json"),
]
for page in [
    "introduction",
    "reference_policies_evaluation-logic",
    "reference_policies_evaluation-logic_policy-eval-denyallow",
    "reference_policies_elements",
    "reference_policies_elements_effect",
    "reference_policies_elements_version",
    "reference_policies_elements_principal",
    "reference_policies_condition-keys",
    "access-analyzer-reference-policy-checks",
    "access_policies",
    "best-practices",
    "id_users",
    "id_groups",
    "id_roles",
    "id_credentials_access-keys",
]:
    JOBS.append((f"{IAM_UG}/{page}.md", f"{page}.md"))
for page in [
    "task-iam-roles",
    "task_execution_IAM_role",
    "task_definition_parameters",
]:
    JOBS.append((f"{ECS_DG}/{page}.md", f"{page}.md"))
JOBS.append((f"{IAM_API}/API_CreateRole.md", "API_CreateRole.md"))
JOBS.append((f"{STS_API}/API_AssumeRole.md", "API_AssumeRole.md"))
JOBS.append((f"{SDKREF}/feature-container-credentials.md",
             "feature-container-credentials.md"))
JOBS.append((f"{MANAGED}/AmazonECSTaskExecutionRolePolicy.md",
             "AmazonECSTaskExecutionRolePolicy.md"))


def main():
    ng = 0
    for url, out in JOBS:
        r = subprocess.run(
            ["curl", "-sS", "-m", "60", "-L", url, "-o", out,
             "-w", "%{http_code} %{size_download}"],
            capture_output=True, text=True,
        )
        code, size = (r.stdout.split() + ["?", "?"])[:2]
        mark = "OK" if code == "200" else "NG"
        if code != "200":
            ng += 1
        print(f"{mark} {code} {size:>7} {out}")
    print(f"失敗 {ng} 件")
    return 1 if ng else 0


if __name__ == "__main__":
    sys.exit(main())
