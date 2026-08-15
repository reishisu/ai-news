#!/usr/bin/env python3
"""記事に貼った原文が、公式ドキュメントに本当にあるかを機械照合する。"""
import re, sys, urllib.request

UA = {"User-Agent": "curl/8"}
BASE = "https://docs.aws.amazon.com"
PAGES = {
 "intro": "/IAM/latest/UserGuide/introduction.html",
 "elements": "/IAM/latest/UserGuide/reference_policies_elements.html",
 "best": "/IAM/latest/UserGuide/best-practices.html",
 "taskrole": "/AmazonECS/latest/developerguide/task-iam-roles.html",
 "execrole": "/AmazonECS/latest/developerguide/task_execution_IAM_role.html",
 "tdparams": "/AmazonECS/latest/developerguide/task_definition_parameters.html",
 "fargate": "/AmazonECS/latest/developerguide/AWS_Fargate.html",
 "mp": "/aws-managed-policy/latest/reference/AmazonECSTaskExecutionRolePolicy.html",
 "sdkcred": "/sdkref/latest/guide/feature-container-credentials.html",
 "users": "/IAM/latest/UserGuide/id_users.html",
 "groups": "/IAM/latest/UserGuide/id_groups.html",
 "roles": "/IAM/latest/UserGuide/id_roles.html",
 "policies": "/IAM/latest/UserGuide/access_policies.html",
 "version": "/IAM/latest/UserGuide/reference_policies_elements_version.html",
 "effect": "/IAM/latest/UserGuide/reference_policies_elements_effect.html",
 "evallogic": "/IAM/latest/UserGuide/reference_policies_evaluation-logic.html",
 "denyallow": "/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-denyallow.html",
 "sts": "/STS/latest/APIReference/API_AssumeRole.html",
 "principal": "/IAM/latest/UserGuide/reference_policies_elements_principal.html",
 "checks": "/IAM/latest/UserGuide/access-analyzer-reference-policy-checks.html",
}
CHECKS = [
 ("intro", "one sign-in identity called the AWS account root user that has complete access"),
 ("intro", "don't use the root user for everyday tasks"),
 ("intro", "control who is authenticated (signed in) and authorized (has permissions)"),
 ("intro", "offered at no additional charge"),
 ("intro", "is eventually consistent"),
 ("elements", "The order of the elements doesn't matter"),
 ("elements", "you cannot use both `Action` and `NotAction` in the same policy statement"),
 ("best", "also known as *least-privilege permissions*"),
 ("best", "You might start with broad permissions"),
 ("best", "might not grant least-privilege permissions for your specific use cases"),
 ("best", "no need to distribute long lived credentials"),
 ("taskrole", "This role allows your application code (running in the container) to use other AWS services."),
 ("taskrole", "These permissions aren't accessed by the Amazon ECS container and Fargate agents."),
 ("taskrole", "EC2 instance profiles are not available for containers in your tasks"),
 ("taskrole", "containers can potentially access credentials for other tasks"),
 ("taskrole", "ecs-tasks.amazonaws.com"),
 ("taskrole", "aws:SourceAccount"),
 ("taskrole", "my-task-secrets-bucket"),
 ("taskrole", "without calling `sts:AssumeRole`"),
 ("taskrole", "creating a role for each specific task definition or service"),
 ("execrole", "grants the Amazon ECS container and Fargate agents permission to make AWS API calls"),
 ("execrole", "they aren't directly accessible by the containers in the task"),
 ("execrole", "container agent version 1.16.0 and later"),
 ("tdparams", "`taskRoleArn`"),
 ("tdparams", "`executionRoleArn`"),
 ("fargate", "without having to manage servers or clusters of Amazon EC2 instances"),
 ("mp", "ecr:GetAuthorizationToken"),
 ("mp", "logs:PutLogEvents"),
 ("mp", "November 16, 2017"),
 ("mp", "v1 (default)"),
 ("sdkcred", "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"),
 ("sdkcred", "SDKs attempt to load credentials from the specified HTTP endpoint through a GET request"),
 ("users", "An IAM user consists of a name and credentials."),
 ("users", "only use IAM users for specific use cases not supported by federated users"),
 ("groups", "You cannot identify a user group as a Principal in a policy"),
 ("groups", "User groups can't be nested"),
 ("roles", "a role is intended to be assumable by anyone who needs it"),
 ("roles", "a role does not have standard long-term credentials"),
 ("roles", "The trust policy specifies which trusted account members are allowed to assume the role."),
 ("roles", "you cannot specify a wildcard"),
 ("roles", "temporarily gives up his or her own permissions"),
 ("policies", "The most common examples of resource-based policies are Amazon S3 bucket policies and IAM role trust policies."),
 ("policies", "The principal is implied as that user or role."),
 ("policies", "AWS applies a logical OR across the statements"),
 ("version", "This is the current version of the policy language"),
 ("version", "Do not use this version for any new policies"),
 ("effect", "The Effect value is case sensitive."),
 ("evallogic", "the resulting permissions are the intersection of the two categories"),
 ("denyallow", "An explicit deny overrides an explicit allow."),
 ("sts", "consist of an access key ID, a secret access key, and a security token"),
 ("sts", "up to the maximum session duration set for the role"),
 ("sts", "By default, the value is set to 3600 seconds."),
 # --- 編集時に追加（2026-08-15）: 信頼ポリシーのワイルドカードと INVALID_ACTION ---
 ("principal", "You can use a wildcard (*) to specify all principals in the `Principal` element of a resource-based policy"),
 ("principal", "We strongly recommend that you do not use a wildcard (*) in the `Principal` element of a resource-based policy with an `Allow` effect unless you intend to grant public or anonymous access."),
 ("principal", "This is especially true for IAM role trust policies, because they allow other principals to become a principal in your account."),
 ("principal", "Do not leave your role accessible to everyone"),
 ("checks", "INVALID_ACTION"),
 ("checks", "Invalid action: The action {{action}} does not exist. Did you mean {{valid_action}}?"),
 ("roles", "When you create a trust policy, you cannot specify a wildcard (*) as part of an ARN in the principal element."),
 ("taskrole", "The task role is required when your application accesses other AWS services, such as Amazon S3."),
 ("taskrole", "When creating your task IAM role, we recommend that you use the `aws:SourceAccount` or `aws:SourceArn` condition keys in the trust relationship policy associated with the role to scope the permissions further to prevent the confused deputy security issue."),
 ("taskrole", "without calling `sts:AssumeRole` to assume the same role that is already associated with the task."),
 ("execrole", "The task execution IAM role is required depending on the requirements of your task."),
]

cache = {}
def body(k):
    if k not in cache:
        url = BASE + PAGES[k].replace(".html", ".md")
        try:
            cache[k] = urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "replace")
        except Exception as e:
            print(f"取得失敗 {k}: {e}"); cache[k] = ""
    return cache[k]

def norm(s):
    # HTML版で消える Markdown 記法（強調・リンク・コード）を落としてから比べる
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = s.replace("*", "").replace("`", "").replace("\\", "")
    return re.sub(r"\s+", " ", s)

ng = 0
for k, q in CHECKS:
    hit = norm(q) in norm(body(k))
    if not hit: ng += 1
    print(f"{'OK ' if hit else 'NG '} {k:9s} {q[:44]}")
print(f"--- 不一致 {ng} 件")
sys.exit(1 if ng else 0)
