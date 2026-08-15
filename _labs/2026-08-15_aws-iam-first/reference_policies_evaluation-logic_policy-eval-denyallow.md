

# How AWS enforcement code logic evaluates requests to allow or deny access
<a name="reference_policies_evaluation-logic_policy-eval-denyallow"></a>

The AWS enforcement code decides whether a request sent to AWS should be allowed or denied. AWS evaluates all policies that are applicable to the request context. The following is a summary of the AWS policy evaluation logic.
+ By default, all requests are implicitly denied with the exception of the AWS account root user, which has full access.
+ Requests must be explicitly allowed by a policy or set of policies following the evaluation logic below to be allowed.
+ An explicit deny overrides an explicit allow.

Policy evaluation can differ depending on whether the request is within a single account or a cross-account request. For details about how a policy evaluation decision is made for an IAM role or user within a single account, see [Policy evaluation for requests within a single account](reference_policies_evaluation-logic_policy-eval-basics.md). For details about how a policy evaluation decision is made for cross-account requests, see [Cross-account policy evaluation logic](reference_policies_evaluation-logic-cross-account.md).
+ **Deny evaluation** – By default, all requests are denied. This is called an [implicit deny](reference_policies_evaluation-logic_AccessPolicyLanguage_Interplay.md). The AWS enforcement code evaluates all policies within the account that apply to the request. These include AWS Organizations SCPs and RCPs, resource-based policies, identity-based policies, IAM permissions boundaries, and session policies. In all those policies, the enforcement code looks for a `Deny` statement that applies to the request. This is called an [explicit deny](reference_policies_evaluation-logic_AccessPolicyLanguage_Interplay.md). If the enforcement code finds even one explicit deny that applies, the enforcement code returns a final decision of **Deny**. If there is no explicit deny, the enforcement code evaluation continues.
+ **AWS Organizations RCPs** – The enforcement code evaluates AWS Organizations resource control policies (RCPs) that apply to the request. RCPs apply to resources of the account where the RCPs are attached. If the enforcement code does not find any applicable `Allow` statements in the RCPs, the enforcement code returns a final decision of **Deny**. Note that an AWS managed policy called `RCPFullAWSAccess` is automatically created and attached to every entity in your organization including the root, each OU, and AWS account when RCPs are enabled. `RCPFullAWSAccess` can't be detached, so there will always be an `Allow` statement. If there is no RCP, or if the RCP allows the requested action, the enforcement code evaluation continues.
+ **AWS Organizations SCPs** – The enforcement code evaluates AWS Organizations service control policies (SCPs) that apply to the request. SCPs apply to principals of the account where the SCPs are attached. If the enforcement code does not find any applicable `Allow` statements in the SCPs, the enforcement code returns a final decision of **Deny**. If there is no SCP, or if the SCP allows the requested action, the enforcement code evaluation continues.
+ **Resource-based policies** – Within the same account, resource-based policies impact policy evaluation differently depending on the type of principal accessing the resource, and the principal that is allowed in the resource-based policy. Depending on the type of principal, an `Allow` in a resource-based policy can result in a final decision of `Allow`, even if an implicit deny in an identity-based policy, permissions boundary, or session policy is present.

  For most resources, you only need an explicit `Allow` for the principal in either an identity-based policy or a resource-based policy to grant access. [IAM role trust policies](access_policies-cross-account-resource-access.md#access_policies-cross-account-delegating-resource-based-policies) and [KMS key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html) are exceptions to this logic, because they must explicitly allow access for [principals](reference_policies_elements_principal.md). Resource-based policies for services other than IAM and AWS KMS may also require an explicit `Allow` statement within the same account to grant access. For more information, see the documentation for the specific service you're working with.

  For single account policy evaluation requests, resource-based policy logic differs from other policy types if the specified principal is an IAM user, an IAM role, or a session principal. Session principals include [IAM role sessions](reference_policies_elements_principal.md#principal-role-session) or an [AWS STS federated user principals](reference_policies_elements_principal.md#sts-session-principals). If a resource-based policy grants permission directly to the IAM user or the session principal that is making the request, then an implicit deny in an identity-based policy, a permissions boundary, or a session policy does not impact the final decision.
  + **IAM role** – Resource-based policies that grant permissions to an IAM role ARN are limited by an implicit deny in a permissions boundary or session policy. You can specify the role ARN in the Principal element or the `aws:PrincipalArn` condition key. In both cases, the principal that makes the request is the **IAM role session**.

    Permissions boundaries and session policies do not limit permissions granted using the `aws:PrincipalArn` condition key with a wildcard(\*) in the Principal element, unless the identity-based policies contain an explicit deny. For more information, see [IAM role principals](reference_policies_elements_principal.md#principal-roles).

    **Example role ARN**

    ```
    arn:aws:iam::111122223333:role/examplerole
    ```
  + **IAM role session** – Within the same account, resource-based policies that grant permissions to an IAM role session ARN grant permissions directly to the assumed role session. Permissions granted directly to a session are not limited by an implicit deny in an identity-based policy, a permissions boundary, or session policy. When you assume a role and make a request, the principal making the request is the IAM role session ARN and not the ARN of the role itself. For more information, see [Role session principals](reference_policies_elements_principal.md#principal-role-session).

    **Example role session ARN**

    ```
    arn:aws:sts::111122223333:assumed-role/examplerole/examplerolesessionname
    ```
  + **IAM user** – Within the same account, resource-based policies that grant permissions to an IAM user ARN (that is not a federated user session) are not limited by an implicit deny in an identity-based policy or permissions boundary.

    **Example IAM user ARN**

    ```
    arn:aws:iam::111122223333:user/exampleuser
    ```
  + **AWS STS federated user principal** – A federated user session is a session created by calling [`GetFederationToken`](id_credentials_temp_request.md#api_getfederationtoken). When a federated user makes a request, the principal making the request is the federated user ARN and not the ARN of the IAM user who federated. Within the same account, resource-based policies that grant permissions to a federated user ARN grant permissions directly to the session. Permissions granted directly to a session are not limited by an implicit deny in an identity-based policy, a permissions boundary, or session policy.

    However, if a resource-based policy grants permission to the ARN of the IAM user who federated, then requests made by the federated user during the session are limited by an implicit deny in a permission boundary or session policy.

    **Example federated user session ARN**

    ```
    arn:aws:sts::111122223333:federated-user/exampleuser
    ```
+ **Identity-based policies** – The enforcement code checks the identity-based policies for the principal. For an IAM user, these include user policies and policies from groups to which the user belongs. If there are no identity-based policies or no statements in identity-based policies that allow the requested action, then the request is implicitly denied and the enforcement code returns a final decision of **Deny**. If any statement in any applicable identity-based policies allows the requested action, the code evaluation continues.
+ **IAM permissions boundaries** – The enforcement code checks whether the IAM entity that is used by the principal has a permissions boundary. If the policy that is used to set the permissions boundary does not allow the requested action, then the request is implicitly denied. The enforcement code returns a final decision of **Deny**. If there is no permissions boundary, or if the permissions boundary allows the requested action, the code evaluation continues.
+ **Session policies** – The enforcement code checks whether the principal is a session principal. Session principals include an IAM role session or an AWS STS federated user session. If the principal is not a session principal, the enforcement code returns a final decision of **Allow**.

  For session principals, the enforcement code checks whether a session policy was passed in the request. You can pass a session policy while using the AWS CLI or AWS API to get temporary credentials for a role or an AWS STS federated user principal. If you didn't pass a session policy, a default session policy is created and the enforcement code returns a final decision of **Allow**.
  + If a session policy is present and does not allow the requested action, then the request is implicitly denied. The enforcement code returns a final decision of **Deny**.
  + The enforcement code checks whether the principal is a role session. If the principal is a role session, then the request is **Allowed**. Otherwise, the request is implicitly denied and the enforcement code returns a final decision of **Deny**.
  + If a session policy is present and allows the requested action, then the enforcement code returns a final decision of **Allow**.