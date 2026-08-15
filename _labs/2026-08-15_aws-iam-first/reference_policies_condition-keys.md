

# AWS global condition context keys
<a name="reference_policies_condition-keys"></a>

When a [principal](https://docs.aws.amazon.com/glossary/latest/reference/glos-chap.html?icmpid=docs_homepage_addtlrcs#principal) makes a [request](intro-structure.md#intro-structure-request) to AWS, AWS gathers the request information into a [request context](intro-structure.md#intro-structure-request). You can use the `Condition` element of a JSON policy to compare keys in the request context with key values that you specify in your policy. Request information is provided by different sources, including the principal making the request, the resource the request is made against, and the metadata about the request itself.

**Global condition keys** can be used across all AWS services. While these condition keys can be used in all policies, the key is not available in every request context. For example, the `aws:SourceAccount` condition key is only available when the call to your resource is made directly by an [AWS service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-services). To learn more about the circumstances under which a global key is included in the request context, see the **Availability** information for each key.

Some individual services create their own condition keys that are available in the request context for other services. **Cross-service condition keys** are a type of global condition key that include a prefix matching the name of the service, such as `ec2:` or `lambda:`, but are available across other services.

**Service-specific condition keys** are defined for use with an individual AWS service. For example, Amazon S3 lets you write a policy with the `s3:VersionId` condition key to limit access to a specific version of an Amazon S3 object. This condition key is unique to the service, meaning it only works with requests to the Amazon S3 service. For condition keys that are service-specific, see [Actions, Resources, and Condition Keys for AWS Services](https://docs.aws.amazon.com/service-authorization/latest/reference/reference_policies_actions-resources-contextkeys.html) and choose the service whose keys you want to view. 

**Note**  
If you use condition keys that are available only in some circumstances, you can use the [IfExists](reference_policies_elements_condition_operators.md#Conditions_IfExists) versions of the condition operators. If the condition keys are missing from a request context, the policy can fail the evaluation. For example, use the following condition block with `...IfExists` operators to match when a request comes from a specific IP range or from a specific VPC. If either or both keys are not included in the request context, the condition still returns `true`. The values are only checked if the specified key is included in the request context. For more information about how a policy is evaluated when a key is not present for other operators, see [ Condition operators](reference_policies_elements_condition_operators.md).  

```
"Condition": {
    "IpAddressIfExists": {"aws:SourceIp" : ["xxx"] },
    "StringEqualsIfExists" : {"aws:SourceVpc" : ["yyy"]} 
}
```

**Important**  
To compare your condition against a request context with multiple key values, you must use the `ForAllValues` or `ForAnyValue` set operators. Use set operators only with multivalued condition keys. Do not use set operators with single-valued condition keys. For more information, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).


| Properties of the principal | Properties of a role session | Properties of the network | Properties of the resource | Properties of the request | 
| --- | --- | --- | --- | --- | 
| `aws:PrincipalArn`<br />`aws:PrincipalAccount`<br />`aws:PrincipalOrgPaths`<br />`aws:PrincipalOrgID`<br />`aws:PrincipalTag/*tag-key*`<br />`aws:PrincipalIsAWSService`<br />`aws:PrincipalServiceName`<br />`aws:PrincipalServiceNamesList`<br />`aws:PrincipalType`<br />`aws:userid`<br />`aws:username` | `aws:AssumedRoot`<br />`aws:FederatedProvider`<br />`aws:TokenIssueTime`<br />`aws:SignInSessionArn`<br />`aws:MultiFactorAuthAge`<br />`aws:MultiFactorAuthPresent`<br />`aws:ChatbotSourceArn`<br />`aws:Ec2InstanceSourceVpc`<br />`aws:Ec2InstanceSourcePrivateIPv4`<br />`aws:SourceIdentity`<br />`ec2:RoleDelivery`<br />`ec2:SourceInstanceArn`<br />`glue:RoleAssumedBy`<br />`glue:CredentialIssuingService`<br />`codebuild:BuildArn`<br />`codebuild:ProjectArn`<br />`lambda:SourceFunctionArn`<br />`ssm:SourceInstanceArn`<br />`identitystore:UserId` | `aws:SourceIp`<br />`aws:SourceVpc`<br />`aws:SourceVpcArn`<br />`aws:SourceVpce`<br />`aws:VpceAccount`<br />`aws:VpceOrgID`<br />`aws:VpceOrgPaths`<br />`aws:VpcSourceIp` | `aws:ResourceAccount`<br />`aws:ResourceOrgID`<br />`aws:ResourceOrgPaths`<br />`aws:ResourceTag/*tag-key*` | `aws:CalledVia`<br />`aws:CalledViaFirst`<br />`aws:CalledViaLast`<br />`aws:CalledViaAWSMCP`<br />`aws:ViaAWSService`<br />`aws:ViaAWSMCPService`<br />`aws:CurrentTime`<br />`aws:EpochTime`<br />`aws:referer`<br />`aws:RequestedRegion`<br />`aws:RequestTag/*tag-key*`<br />`aws:TagKeys`<br />`aws:SecureTransport`<br />`aws:SourceAccount`<br />`aws:SourceArn`<br />`aws:SourceOrgID`<br />`aws:SourceOrgPaths`<br />`aws:UserAgent`<br />`aws:IsMcpServiceAction` | 

## Sensitive condition keys
<a name="condition-keys-sensitive"></a>

The following condition keys are considered sensitive. The use of wildcards in these condition keys does not have any valid use cases, even with a substring of the key value with a wildcard. This is because the wildcard might match the condition key to any value, which could pose a security risk.
+ `aws:PrincipalAccount`
+ `aws:PrincipalOrgID`
+ `aws:ResourceAccount`
+ `aws:ResourceOrgID`
+ `aws:SourceAccount`
+ `aws:SourceOrgID`
+ `aws:SourceVpc`
+ `aws:SourceVpce`
+ `aws:VpceAccount`
+ `aws:VpceOrgID`

## Properties of the principal
<a name="condition-keys-principal-properties"></a>

Use the following condition keys to compare details about the principal making the request with the principal properties that you specify in the policy. For a list of principals that can make requests, see [How to specify a principal](reference_policies_elements_principal.md#Principal_specifying).

### aws:PrincipalArn
<a name="condition-keys-principalarn"></a>

Use this key to compare the [Amazon Resource Name](reference_identifiers.md#identifiers-arns) (ARN) of the principal that made the request with the ARN that you specify in the policy. For IAM roles, the request context returns the ARN of the role, not the ARN of the user that assumed the role. 
+ **Availability** – This key is included in the request context for all signed requests. Anonymous requests do not include this key. You can specify the following types of principals in this condition key: 
  + IAM role
  + IAM user
  + AWS STS federated user principal
  + AWS account root user
+ **Data type** – ARN

  AWS recommends that you use [ARN operators](reference_policies_elements_condition_operators.md#Conditions_ARN) instead of [string operators](reference_policies_elements_condition_operators.md#Conditions_String) when comparing ARNs.
+ **Value type** – Single-valued
+ **Example values** The following list shows the request context value returned for different types of principals that you can specify in the `aws:PrincipalArn` condition key:
  + **IAM role** – The request context contains the following value for condition key `aws:PrincipalArn`. Do not specify the assumed role session ARN as a value for this condition key. For more information about the assumed role session principal, see [Role session principals](reference_policies_elements_principal.md#principal-role-session).

    ```
    arn:aws:iam::123456789012:role/role-name
    ```
  + **IAM user** – The request context contains the following value for condition key `aws:PrincipalArn`.

    ```
    arn:aws:iam::123456789012:user/{{user-name}}
    ```
  + **AWS STS federated user principals** – The request context contains the following value for condition key `aws:PrincipalArn`.

    ```
    arn:aws:sts::123456789012:federated-user/{{user-name}}
    ```
  + **AWS account root user** – The request context contains the following value for condition key `aws:PrincipalArn`. When you specify the root user ARN as the value for the `aws:PrincipalArn` condition key, it limits permissions only for the root user of the AWS account. This is different from specifying the root user ARN in the principal element of a resource-based policy, which delegates authority to the AWS account. For more information about specifying the root user ARN in the principal element of a resource-based policy, see [AWS account principals](reference_policies_elements_principal.md#principal-accounts). 

    ```
    arn:aws:iam::123456789012:root
    ```

You can specify the root user ARN as a value for condition key `aws:PrincipalArn` in AWS Organizations service control policies (SCPs). SCPs are a type of organization policy used to manage permissions in your organization and affect only member accounts in the organization. An SCP restricts permissions for IAM users and roles in member accounts, including the member account's root user. For more information about the effect of SCPs on permissions, see [SCP effects on permissions](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html#scp-effects-on-permissions) in the *AWS Organizations User Guide*.

### aws:PrincipalAccount
<a name="condition-keys-principalaccount"></a>

Use this key to compare the account to which the requesting principal belongs with the account identifier that you specify in the policy. For anonymous requests, the request context returns `anonymous`.
+ **Availability** – This key is included in the request context for all requests, including anonymous requests.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

In the following example, access is denied except to principals with the account number `123456789012`.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "DenyAccessFromPrincipalNotInSpecificAccount",
      "Action": "{{service}}:*",
      "Effect": "Deny",
      "Resource": [
        "arn:aws:{{service:us-east-1:111122223333:resource}}"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalAccount": [
            "123456789012"
          ]
        }
      }
    }
  ]
}
```

------

### aws:PrincipalOrgPaths
<a name="condition-keys-principalorgpaths"></a>

Use this key to compare the AWS Organizations path for the principal who is making the request to the path in the policy. That principal can be an IAM user, IAM role, AWS STS federated user principal, or AWS account root user. In a policy, this condition key ensures that the requester is an account member within the specified organization root or organizational units (OUs) in AWS Organizations. An AWS Organizations path is a text representation of the structure of an AWS Organizations entity. For more information about using and understanding paths, see [Understand the AWS Organizations entity path](access_policies_last-accessed-view-data-orgs.md#access_policies_last-accessed-viewing-orgs-entity-path).
+ **Availability** – This key is included in the request context only if the principal is a member of an organization. Anonymous requests do not include this key.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

**Note**  
Organization IDs are globally unique but OU IDs and root IDs are unique only within an organization. This means that no two organizations share the same organization ID. However, another organization might have an OU or root with the same ID as yours. We recommend that you always include the organization ID when you specify an OU or root.

For example, the following condition returns `true` for principals in accounts that are attached directly to the `ou-ab12-22222222` OU, but not in its child OUs.

```
"Condition" : { "ForAnyValue:StringEquals" : {
     "aws:PrincipalOrgPaths":["o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/"]
}}
```

The following condition returns `true` for principals in an account that is attached directly to the OU or any of its child OUs. When you include a wildcard, you must use the `StringLike` condition operator.

```
"Condition" : { "ForAnyValue:StringLike" : {
     "aws:PrincipalOrgPaths":["o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/*"]
}}
```

The following condition returns `true` for principals in an account that is attached directly to any of the child OUs, but not directly to the parent OU. The previous condition is for the OU or any children. The following condition is for only the children (and any children of those children).

```
"Condition" : { "ForAnyValue:StringLike" : {
     "aws:PrincipalOrgPaths":["o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/ou-*"]
}}
```

The following condition allows access for every principal in the `o-a1b2c3d4e5` organization, regardless of their parent OU.

```
"Condition" : { "ForAnyValue:StringLike" : {
     "aws:PrincipalOrgPaths":["o-a1b2c3d4e5/*"]
}}
```

`aws:PrincipalOrgPaths` is a multivalued condition key. Multivalued keys can have multiple values in the request context. When you use multiple values with the `ForAnyValue` condition operator, the principal's path must match one of the paths listed in the policy. For more information about multivalued condition keys, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).

```
    "Condition": {
        "ForAnyValue:StringLike": {
            "aws:PrincipalOrgPaths": [
                "o-a1b2c3d4e5/r-ab12/ou-ab12-33333333/*",
                "o-a1b2c3d4e5/r-ab12/ou-ab12-22222222/*"
            ]
        }
    }
```

### aws:PrincipalOrgID
<a name="condition-keys-principalorgid"></a>

Use this key to compare the identifier of the organization in AWS Organizations to which the requesting principal belongs with the identifier specified in the policy.
+ **Availability** – This key is included in the request context only if the principal is a member of an organization. Anonymous requests do not include this key.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

This global key provides an alternative to listing all the account IDs for all AWS accounts in an organization. You can use this condition key to simplify specifying the `Principal` element in a [resource-based policy](access_policies_identity-vs-resource.md). You can specify the [organization ID](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_details.html) in the condition element. When you add and remove accounts, policies that include the `aws:PrincipalOrgID` key automatically include the correct accounts and don't require manual updating.

For example, the following Amazon S3 bucket policy allows members of any account in the `o-xxxxxxxxxxx` organization to add an object into the `amzn-s3-demo-bucket` bucket. 

------
#### [ JSON ]

****  

```
 {
  "Version":"2012-10-17",		 	 	 
  "Statement": {
    "Sid": "AllowPutObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
    "Condition": {"StringEquals":
      {"aws:PrincipalOrgID":"o-xxxxxxxxxxx"}
    }
  }
}
```

------

**Note**  
This global condition also applies to the management account of an AWS organization. This policy prevents all principals outside of the specified organization from accessing the Amazon S3 bucket. This includes any AWS services that interact with your internal resources, such as AWS CloudTrail sending log data to your Amazon S3 buckets. To learn how you can safely grant access for AWS services, see [aws:PrincipalIsAWSService](#condition-keys-principalisawsservice).

For more information about AWS Organizations, see [What Is AWS Organizations?](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html) in the *AWS Organizations User Guide*.

### aws:PrincipalTag/*tag-key*
<a name="condition-keys-principaltag"></a>

Use this key to compare the tag attached to the principal making the request with the tag that you specify in the policy. If the principal has more than one tag attached, the request context includes one `aws:PrincipalTag` key for each attached tag key.
+ **Availability** – This key is included in the request context if the principal is using an IAM user with attached tags. It is included for a principal using an IAM role with attached tags or [session tags](id_session-tags.md). Anonymous requests do not include this key.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can add custom attributes to a user or role in the form of a key-value pair. For more information about IAM tags, see [Tags for AWS Identity and Access Management resources](id_tags.md). You can use `aws:PrincipalTag` to [control access](access_iam-tags.md#access_iam-tags_control-principals) for AWS principals.

This example shows how you might create an identity-based policy that allows users with the **department=hr** tag to manage IAM users, groups, or roles. To use this policy, replace the {{italicized placeholder text}} in the example policy with your own information. Then, follow the directions in [create a policy](access_policies_create.md) or [edit a policy](access_policies_manage-edit.md).

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:Get*",
        "iam:List*",
        "iam:Generate*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/{{department}}": "{{hr}}"
        }
      }
    }
  ]
}
```

------

### aws:PrincipalIsAWSService
<a name="condition-keys-principalisawsservice"></a>

Use this key to check whether the call to your resource is being made directly by an AWS [service principal](reference_policies_elements_principal.md#principal-services). For example, AWS CloudTrail uses the service principal `cloudtrail.amazonaws.com` to write logs to your Amazon S3 bucket. The request context key is set to true when a service uses a service principal to perform a direct action on your resources. The context key is set to false if the service uses the credentials of an IAM principal to make a request on the principal's behalf. It is also set to false if the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf.
+ **Availability** – This key is present in the request context for all signed API requests that use AWS credentials. Anonymous requests do not include this key.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

You can use this condition key to limit access to your trusted identities and expected network locations while safely granting access to AWS services.

In the following Amazon S3 bucket policy example, access to the bucket is restricted unless the request originates from `vpc-111bbb22` or is from a service principal, such as CloudTrail.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "ExpectedNetworkServicePrincipal",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::{{amzn-s3-demo-bucket1}}/AWSLogs/{{AccountNumber}}/*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:SourceVpc": "vpc-111bbb22"
        },
        "BoolIfExists": {
          "aws:PrincipalIsAWSService": "false"
        }
      }
    }
  ]
}
```

------

In the following video, learn more about how you might use the `aws:PrincipalIsAWSService` condition key in a policy.

[![AWS Videos](http://img.youtube.com/vi/gv-_H8a42G4/0.jpg)](http://www.youtube.com/watch?v=gv-_H8a42G4)


### aws:PrincipalServiceName
<a name="condition-keys-principalservicename"></a>

Use this key to compare the [service principal](reference_policies_elements_principal.md#principal-services) name in the policy with the service principal that is making requests to your resources. You can use this key to check whether this call is made by a specific service principal. When a service principal makes a direct request to your resource, the `aws:PrincipalServiceName` key contains the name of the service principal. For example, the AWS CloudTrail service principal name is `cloudtrail.amazonaws.com`.
+ **Availability** – This key is present in the request when the call is made by an AWS service principal. This key is not present in any other situation, including the following:
  + If the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf.
  + If the service uses the credentials of an IAM principal to make a request on the principal's behalf.
  + If the call is made directly by an IAM principal.
  + If the call is made by an anonymous requester.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can use this condition key to limit access to your trusted identities and expected network locations while safely granting access to an AWS service.

In the following Amazon S3 bucket policy example, access to the bucket is restricted unless the request originates from `vpc-111bbb22` or is from a service principal, such as CloudTrail.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "ExpectedNetworkServicePrincipal",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::{{amzn-s3-demo-bucket1}}/AWSLogs/{{AccountNumber}}/*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:SourceVpc": "vpc-111bbb22",
          "aws:PrincipalServiceName": "cloudtrail.amazonaws.com"
        }
      }
    }
  ]
}
```

------

### aws:PrincipalServiceNamesList
<a name="condition-keys-principalservicenameslist"></a>

This key provides a list of all [service principal](reference_policies_elements_principal.md#principal-services) names that belong to the service. This is an advanced condition key. You can use it to restrict the service from accessing your resource from a specific Region only. Some services might create Regional service principals to indicate a particular instance of the service within a specific Region. You can limit access to a resource to a particular instance of the service. When a service principal makes a direct request to your resource, the `aws:PrincipalServiceNamesList` contains an unordered list of all service principal names associated with the Regional instance of the service.
+ **Availability** – This key is present in the request when the call is made by an AWS service principal. This key is not present in any other situation, including the following:
  + If the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf.
  + If the service uses the credentials of an IAM principal to make a request on the principal's behalf.
  + If the call is made directly by an IAM principal.
  + If the call is made by an anonymous requester.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

`aws:PrincipalServiceNamesList` is a multivalued condition key. Multivalued keys can have multiple values in the request context. You must use the `ForAnyValue` or `ForAllValues` set operators with [string condition operators](reference_policies_elements_condition_operators.md#Conditions_String) for this key. For more information about multivalued condition keys, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).

### aws:PrincipalType
<a name="condition-keys-principaltype"></a>

Use this key to compare the type of principal making the request with the principal type that you specify in the policy. For more information, see [How to specify a principal](reference_policies_elements_principal.md#Principal_specifying). For specific examples of `principal` key values, see [Principal key values](reference_policies_variables.md#principaltable).
+ **Availability** – This key is included in the request context for all requests, including anonymous requests.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

### aws:userid
<a name="condition-keys-userid"></a>

Use this key to compare the requester's principal identifier with the ID that you specify in the policy. For IAM users, the request context value is the user ID. For IAM roles, this value format can vary. For details about how the information appears for different principals, see [How to specify a principal](reference_policies_elements_principal.md#Principal_specifying). For specific examples of `principal` key values, see [Principal key values](reference_policies_variables.md#principaltable).
+ **Availability** – This key is included in the request context for all requests, including anonymous requests.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

### aws:username
<a name="condition-keys-username"></a>

Use this key to compare the requester's user name with the user name that you specify in the policy. For details about how the information appears for different principals, see [How to specify a principal](reference_policies_elements_principal.md#Principal_specifying). For specific examples of `principal` key values, see [Principal key values](reference_policies_variables.md#principaltable).
+ **Availability** – This key is always included in the request context for IAM users. Anonymous requests and requests that are made using the AWS account root user or IAM roles do not include this key. Requests made using IAM Identity Center credentials do not include this key in the context.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

## Properties of a role session
<a name="condition-keys-role-session-properties"></a>

Use the following condition keys to compare properties of the role session at the time the session was generated. These condition keys are only available when a request is made by a principal with role session or federated user principal credentials. The values for these condition keys are embedded in the role’s session token.

A [role](reference_policies_elements_principal.md#principal-roles) is a type of principal. You can also use the condition keys from the [Properties of the principal](#condition-keys-principal-properties) section to evaluate the properties of a role when a role is making a request.

### aws:AssumedRoot
<a name="condition-keys-assumedroot"></a>

Use this key to check whether the request was made using [AssumeRoot](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoot.html). `AssumeRoot` returns short term credentials for a privileged root user session you can use to take privileged actions on member accounts in your organization. For more information, see [Centrally manage root access for member accounts](id_root-user.md#id_root-user-access-management).
+ **Availability** – This key is included in the request context only when the principal uses credentials from [AssumeRoot](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRoot.html) to make the request.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

In the following example, when used as a service control policy, denies the usage of the long term credentials of a root user in an AWS Organizations member account. The policy does not deny `AssumeRoot` sessions from taking the actions allowed by an `AssumeRoot` session.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement":[
       {
          "Effect":"Deny",
          "Action":"*",
          "Resource": "*",
          "Condition":{
             "ArnLike":{
                "aws:PrincipalArn":[
                   "arn:aws:iam::*:root"
                ]
             },
             "Null":{
                "aws:AssumedRoot":"true"
             }
          }
       }
    ]
 }
```

------

### aws:FederatedProvider
<a name="condition-keys-federatedprovider"></a>

Use this key to compare the principal's issuing identity provider (IdP) with the IdP that you specify in the policy. This means that an IAM role assumed using the [`AssumeRoleWithWebIdentity`](https://docs.aws.amazon.com//STS/latest/APIReference/API_AssumeRoleWithWebIdentity) AWS STS operation. When the resulting role session's temporary credentials are used to make a request, the request context identifies the IdP that authenticated the original federated identity.
+ **Availability** – This key is present in the role-session of a role that was assumed using OpenID Connect (OIDC) provider, and in the role-trust policy when an OIDC provider is used to call `AssumeRoleWithWebIdentity`.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)\*
+ **Value type** – Single-valued

\* The data type depends on your IdP:
+ If you're using a built-in AWS IdP, like [Amazon Cognito](https://docs.aws.amazon.com/cognito/latest/developerguide/iam-roles.html), the key value will be a **string**. The key value might look like: `cognito-identity.amazonaws.com`.
+ If you're using an IdP that is not built-in to AWS, like [GitHub](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) or [Amazon EKS](https://docs.aws.amazon.com//eks/latest/userguide/associate-service-account-role.html), the key value will be **ARN**. The key value might look like: `arn:aws:iam::{{111122223333}}:oidc-provider/oidc.eks.{{region}}.amazonaws.com/id/{{OIDC_Provider_ID}}`.

For more information on external IdPs and `AssumeRoleWithWebIdentity`, see [Common scenarios](id_federation_common_scenarios.md). For more information, see [Role session principals](reference_policies_elements_principal.md#principal-role-session).

### aws:TokenIssueTime
<a name="condition-keys-tokenissuetime"></a>

Use this key to compare the date and time that temporary security credentials were issued with the date and time that you specify in the policy. 
+ **Availability** – This key is included in the request context only when the principal uses temporary credentials to make the request. The key is not present in AWS CLI, AWS API, or AWS SDK requests that are made using access keys.
+ **Data type** – [Date](reference_policies_elements_condition_operators.md#Conditions_Date)
+ **Value type** – Single-valued

To learn which services support using temporary credentials, see [AWS services that work with IAM](reference_aws-services-that-work-with-iam.md).

### aws:SignInSessionArn
<a name="condition-keys-signinsessionarn"></a>

Use this key to compare your AWS Sign-In OAuth session with the session that you specify in the policy.

When you use an OAuth-based flow such as AWS CLI login (`aws login`) or AWS MCP Server, AWS Sign-In includes a sign-in session ARN in the issued credentials. AWS Sign-In propagates that ARN to subsequent requests made using OAuth access tokens. With this key, you can correlate API activity with the originating sign-in session and apply IAM policies to individual sessions.

For interactive OAuth flows, the refresh token determines the sign-in session ARN lifecycle. A new access token issued during a refresh continues to carry the same sign-in session ARN.

For non-interactive OAuth flows, the access token determines the sign-in session ARN lifecycle. Each new access token contains a new sign-in session ARN.
+ **Availability** – This key is included in the request context when the request originates from an AWS Sign-In OAuth session. This key is not available for console sessions.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued

Use ARN operators instead of string operators when you compare ARNs.

The following policy denies all actions associated with a specific AWS Sign-In session, although requests from other active sessions continue:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenySpecificSignInSession",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "ArnEquals": {
          "aws:SignInSessionArn": "arn:aws:signin:us-east-1:111122223333:session/session-id"
        }
      }
    }
  ]
}
```

### aws:MultiFactorAuthAge
<a name="condition-keys-multifactorauthage"></a>

Use this key to compare the number of seconds since the requesting principal was authorized using MFA with the number that you specify in the policy. For more information about MFA, see [AWS Multi-factor authentication in IAM](id_credentials_mfa.md).

**Important**  
This condition key is not present for federated identities or requests made using access keys to sign AWS CLI, AWS API, or AWS SDK requests. To learn more about adding MFA protection to API operations with temporary security credentials, see [Secure API access with MFA](id_credentials_mfa_configure-api-require.md).  
To check whether MFA is used to validate IAM federated identities, you can pass the authentication method from your identity provider to AWS as a session tag. For details, see [Pass session tags in AWS STS](id_session-tags.md). To enforce MFA for IAM Identity Center identities, you can [ enable attributes for access control](https://docs.aws.amazon.com/singlesignon/latest/userguide/configure-abac.html) to pass a SAML assertion claim with the authentication method from your identity provider to IAM Identity Center.
+ **Availability** – This key is included in the request context only when the principal uses [temporary security credentials](id_credentials_temp.md) to make the request. Policies with MFA conditions can be attached to:
  + An IAM user or group
  + A resource such as an Amazon S3 bucket, Amazon SQS queue, or Amazon SNS topic
  + The trust policy of an IAM role that can be assumed by a user
+ **Data type** – [Numeric](reference_policies_elements_condition_operators.md#Conditions_Numeric)
+ **Value type** – Single-valued

### aws:MultiFactorAuthPresent
<a name="condition-keys-multifactorauthpresent"></a>

Use this key to check whether multi-factor authentication (MFA) was used to validate the [temporary security credentials](id_credentials_temp.md) that made the request.

**Important**  
This condition key is not present for federated identities or requests made using access keys to sign AWS CLI, AWS API, or AWS SDK requests. To learn more about adding MFA protection to API operations with temporary security credentials, see [Secure API access with MFA](id_credentials_mfa_configure-api-require.md).  
To check whether MFA is used to validate IAM federated identities, you can pass the authentication method from your identity provider to AWS as a session tag. For details, see [Pass session tags in AWS STS](id_session-tags.md). To enforce MFA for IAM Identity Center identities, you can [ enable attributes for access control](https://docs.aws.amazon.com/singlesignon/latest/userguide/configure-abac.html) to pass a SAML assertion claim with the authentication method from your identity provider to IAM Identity Center.
+ **Availability** – This key is included in the request context only when the principal uses temporary credentials to make the request. Policies with MFA conditions can be attached to:
  + An IAM user or group
  + A resource such as an Amazon S3 bucket, Amazon SQS queue, or Amazon SNS topic
  + The trust policy of an IAM role that can be assumed by a user
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

Temporary credentials are used to authenticate IAM roles and IAM users with temporary tokens from [AssumeRole](https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html) or [GetSessionToken](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetSessionToken.html), and users of the AWS Management Console.

IAM user access keys are long-term credentials, but in some cases, AWS creates temporary credentials on behalf of IAM users to perform operations. In these cases, the `aws:MultiFactorAuthPresent` key is present in the request and set to a value of `false`. There are two common cases where this can happen:
+ IAM users in the AWS Management Console unknowingly use temporary credentials. Users sign into the console using their user name and password, which are long-term credentials. However, in the background, the console generates temporary credentials on behalf of the user. 
+ If an IAM user makes a call to an AWS service, the service re-uses the user's credentials to make another request to a different service. For example, when calling Athena to access an Amazon S3 bucket, or when using CloudFormation to create an Amazon EC2 instance. For the subsequent request, AWS uses temporary credentials.

To learn which services support using temporary credentials, see [AWS services that work with IAM](reference_aws-services-that-work-with-iam.md).

The `aws:MultiFactorAuthPresent` key is not present when an API or CLI command is called with long-term credentials, such as user access key pairs. Therefore we recommend that when you check for this key that you use the `...IfExists` versions of the condition operators.

It is important to understand that the following `Condition` element is ***not*** a reliable way to check whether a request is authenticated using MFA.

```
#####   WARNING: NOT RECOMMENDED   #####
"Effect" : "Deny",
"Condition" : { "Bool" : { "aws:MultiFactorAuthPresent" : "false" } }
```

This combination of the `Deny` effect, `Bool` element, and `false` value denies requests that can be authenticated using MFA, but were not. This applies only to temporary credentials that support using MFA. This statement does not deny access to requests that are made using long-term credentials, or to requests that are authenticated using MFA. Use this example with caution because its logic is complicated and it does not test whether MFA-authentication was actually used. 

Also do not use the combination of the `Deny` effect, `Null` element, and `true` because it behaves the same way and the logic is even more complicated.

**Recommended Combination**  
We recommend that you use the [`BoolIfExists`](reference_policies_elements_condition_operators.md#Conditions_IfExists) operator to check whether a request is authenticated using MFA.

```
"Effect" : "Deny",
"Condition" : { "BoolIfExists" : { "aws:MultiFactorAuthPresent" : "false" } }
```

This combination of `Deny`, `BoolIfExists`, and `false` denies requests that are not authenticated using MFA. Specifically, it denies requests from temporary credentials that do not include MFA. It also denies requests that are made using long-term credentials, such as AWS CLI or AWS API operations made using access keys. The `*IfExists` operator checks for the presence of the `aws:MultiFactorAuthPresent` key and whether or not it could be present, as indicated by its existence. Use this when you want to deny any request that is not authenticated using MFA. This is more secure, but can break any code or scripts that use access keys to access the AWS CLI or AWS API. 

**Alternative Combinations**  
You can also use the [`BoolIfExists`](reference_policies_elements_condition_operators.md#Conditions_IfExists) operator to allow MFA-authenticated requests and AWS CLI or AWS API requests that are made using long-term credentials.

```
"Effect" : "Allow",
"Condition" : { "BoolIfExists" : { "aws:MultiFactorAuthPresent" : "true" } }
```

This condition matches either if the key exists and is present **or** if the key does not exist. This combination of `Allow`, `BoolIfExists`, and `true` allows requests that are authenticated using MFA, or requests that cannot be authenticated using MFA. This means that AWS CLI, AWS API, and AWS SDK operations are allowed when the requester uses their long-term access keys. This combination does not allow requests from temporary credentials that could, but do not include MFA. 

When you create a policy using the IAM console visual editor and choose **MFA required**, this combination is applied. This setting requires MFA for console access, but allows programmatic access with no MFA. 

Alternatively, you can use the `Bool` operator to allow programmatic and console requests only when authenticated using MFA.

```
"Effect" : "Allow",
"Condition" : { "Bool" : { "aws:MultiFactorAuthPresent" : "true" } }
```

This combination of the `Allow`, `Bool`, and `true` allows only MFA-authenticated requests. This applies only to temporary credentials that support using MFA. This statement does not allow access to requests that were made using long-term access keys, or to requests made using temporary credentials without MFA. 

***Do not*** use a policy construct similar to the following to check whether the MFA key is present:

```
#####   WARNING: USE WITH CAUTION   #####

"Effect" : "Allow",
"Condition" : { "Null" : { "aws:MultiFactorAuthPresent" : "false" } }
```

This combination of the `Allow` effect, `Null` element, and `false` value allows only requests that can be authenticated using MFA, regardless of whether the request is actually authenticated. This allows all requests that are made using temporary credentials, and denies access for long-term credentials. Use this example with caution because it does not test whether MFA-authentication was actually used. 

### aws:ChatbotSourceArn
<a name="condition-keys-chatbotsourcearn"></a>

Use this key to compare the source chat configuration ARN set by the principal to the chat configuration ARN you specify in the policy of the IAM role associated with your channel configuration. You can authorize requests based on the assume role session initiated by Amazon Q Developer in chat applications.
+ **Availability** – This key is included in the request context by the Amazon Q Developer in chat applications service whenever a role session is assumed. The key value is the chat configuration ARN, such as when you [run an AWS CLI command from a chat channel](https://docs.aws.amazon.com/chatbot/latest/adminguide/chatbot-cli-commands.html).
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – `arn:aws::chatbot::123456789021:chat-configuration/slack-channel/private_channel`

The following policy denies Amazon S3 put requests on the specified bucket for all requests originating from a Slack channel.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "ExampleS3Deny",
            "Effect": "Deny",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
            "Condition": {
                "ArnLike": {
                      "aws:ChatbotSourceArn": "arn:aws:chatbot::*:chat-configuration/slack-channel/*"
                }
            }
        }
    ]
}
```

------

### aws:Ec2InstanceSourceVpc
<a name="condition-keys-ec2instancesourcevpc"></a>

This key identifies the VPC to which Amazon EC2 IAM role credentials were delivered to. You can use this key in a policy with the [`aws:SourceVPC`](#condition-keys-sourcevpc) global key to check if a call is made from a VPC (`aws:SourceVPC`) that matches the VPC where a credential was delivered to (`aws:Ec2InstanceSourceVpc`).
+ **Availability** – This key is included in the request context whenever the requester is signing requests with an Amazon EC2 role credential. It can be used in IAM policies, service control policies, VPC endpoint policies, and resource policies.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

This key can be used with VPC identifier values, but is most useful when used as a variable combined with the `aws:SourceVpc` context key. The `aws:SourceVpc` context key is included in the request context only if the requester uses a VPC endpoint to make the request. Using `aws:Ec2InstanceSourceVpc` with `aws:SourceVpc` allows you to use `aws:Ec2InstanceSourceVpc` more broadly since it compares values that typically change together.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "RequireSameVPC",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
            "aws:SourceVpc": "${aws:Ec2InstanceSourceVpc}"
        },
        "Null": {
          "ec2:SourceInstanceARN": "false"
        },
        "BoolIfExists": {
          "aws:ViaAWSService": "false"
        }
      }
    }
  ]
}
```

------

In the example above, access is denied if the `aws:SourceVpc` value isn’t equal to the `aws:Ec2InstanceSourceVpc` value. The policy statement is limited to only roles used as Amazon EC2 instance roles by testing for the existence of the `ec2:SourceInstanceARN` condition key.

The policy uses `aws:ViaAWSService` to allow AWS to authorize requests when requests are made on behalf of your Amazon EC2 instance roles. For example, when you make a request from an Amazon EC2 instance to an encrypted Amazon S3 bucket, Amazon S3 makes a call to AWS KMS on your behalf. Some of the keys are not present when the request is made to AWS KMS.

### aws:Ec2InstanceSourcePrivateIPv4
<a name="condition-keys-ec2instancesourceprivateip4"></a>

This key identifies the private IPv4 address of the primary elastic network interface to which Amazon EC2 IAM role credentials were delivered. You must use this condition key with its companion key `aws:Ec2InstanceSourceVpc` to make sure that you have a globally unique combination of VPC ID and source private IP. Use this key with `aws:Ec2InstanceSourceVpc` to make sure that a request was made from the same private IP address that the credentials were delivered to.
+ **Availability** – This key is included in the request context whenever the requester is signing requests with an Amazon EC2 role credential. It can be used in IAM policies, service control policies, VPC endpoint policies, and resource policies.
+ **Data type** – [IP address](reference_policies_elements_condition_operators.md#Conditions_IPAddress)
+ **Value type** – Single-valued

**Important**  
This key should not be used alone in an `Allow` statement. Private IP addresses are by definition not globally unique. You should use the `aws:Ec2InstanceSourceVpc` key every time you use the `aws:Ec2InstanceSourcePrivateIPv4` key to specify the VPC your Amazon EC2 instance credentials can be used from.

The following example is a service control policy (SCP) that denies access to all resources unless the request arrives through a VPC Endpoint in the same VPC as the as the role credentials. In this example, `aws:Ec2InstanceSourcePrivateIPv4` limits the credential source to a particular instance based on the source IP.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Effect": "Deny",
            "Action":  "*",
            "Resource": "*",
            "Condition": {
                "StringNotEquals": {
                    "aws:Ec2InstanceSourceVpc": "${aws:SourceVpc}"
                },                
                "Null": {
                    "ec2:SourceInstanceARN": "false"
                },
                "BoolIfExists": {
                    "aws:ViaAWSService": "false"
                }
            }
        },
        {
            "Effect": "Deny",
            "Action":  "*",
            "Resource": "*",
            "Condition": {
                "StringNotEquals": {
                    "aws:Ec2InstanceSourcePrivateIPv4": "${aws:VpcSourceIp}"
                },                               
                "Null": {
                    "ec2:SourceInstanceARN": "false"
                },
                "BoolIfExists": {
                    "aws:ViaAWSService": "false"
                }
            }
        }
    ]
}
```

------

### aws:SourceIdentity
<a name="condition-keys-sourceidentity"></a>

Use this key to compare the source identity that was set by the principal with the source identity that you specify in the policy. 
+ **Availability** – This key is included in the request context after a source identity has been set when a role is assumed using any AWS STS assume-role CLI command, or AWS STS `AssumeRole` API operation.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can use this key in a policy to allow actions in AWS by principals that have set a source identity when assuming a role. Activity for the role's specified source identity appears in [AWS CloudTrail](cloudtrail-integration.md#cloudtrail-integration_signin-tempcreds). This makes it easier for administrators to determine who or what performed actions with a role in AWS.

Unlike [`sts:RoleSessionName`](reference_policies_iam-condition-keys.md#ck_rolesessionname), after the source identity is set, the value cannot be changed. It is present in the request context for all actions taken by the role. The value persists into subsequent role sessions when you use the session credentials to assume another role. Assuming one role from another is called [role chaining](id_roles.md#iam-term-role-chaining). 

The [`sts:SourceIdentity`](reference_policies_iam-condition-keys.md#ck_sourceidentity) key is present in the request when the principal initially sets a source identity while assuming a role using any AWS STS assume-role CLI command, or AWS STS `AssumeRole` API operation. The `aws:SourceIdentity` key is present in the request for any actions that are taken with a role session that has a source identity set.

The following role trust policy for `CriticalRole` in account `111122223333` contains a condition for `aws:SourceIdentity` that prevents a principal without a source identity that is set to Saanvi or Diego from assuming the role.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "AssumeRoleIfSourceIdentity",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::123456789012:role/CriticalRole"},
            "Action": [
                "sts:AssumeRole",
                "sts:SetSourceIdentity"
            ],
            "Condition": {
                "StringLike": {
                    "aws:SourceIdentity": ["Saanvi","Diego"]
                }
            }
        }
    ]
}
```

------

To learn more about using source identity information, see [Monitor and control actions taken with assumed roles](id_credentials_temp_control-access_monitor.md).

### ec2:RoleDelivery
<a name="condition-keys-ec2-role-delivery"></a>

Use this key to compare the version of the instance metadata service in the signed request with the IAM role credentials for Amazon EC2. The instance metadata service distinguishes between IMDSv1 and IMDSv2 requests based on whether, for any given request, either the `PUT` or `GET` headers, which are unique to IMDSv2, are present in that request.
+ **Availability** – This key is included in the request context whenever the role session is created by an Amazon EC2 instance.
+ **Data type** – [Numeric](reference_policies_elements_condition_operators.md#Conditions_Numeric)
+ **Value type** – Single-valued
+ **Example values** – 1.0, 2.0

You can configure the Instance Metadata Service (IMDS) on each instance so that local code or users must use IMDSv2. When you specify that IMDSv2 must be used, IMDSv1 no longer works.
+ Instance Metadata Service Version 1 (IMDSv1) – A request/response method 
+ Instance Metadata Service Version 2 (IMDSv2) – a session-oriented method

For information about how to configure your instance to use IMDSv2, see [Configure the instance metadata options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html).

In the following example, access is denied if the ec2:RoleDelivery value in the request context is 1.0 (IMDSv1). This policy statement can be applied generally because, if the request is not signed by Amazon EC2 role credentials, it has no effect.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
               {
            "Sid": "RequireAllEc2RolesToUseV2",
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "NumericLessThan": {
                    "ec2:RoleDelivery": "2.0"
                }
            }
        }
    ]
}
```

------

For more information, see [Example policies for working with instance metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ExamplePolicies_EC2.html#iam-example-instance-metadata).

### ec2:SourceInstanceArn
<a name="condition-keys-ec2-source-instance-arn"></a>

Use this key to compare the ARN of the instance from which the role’s session was generated.
+ **Availability** – This key is included in the request context whenever the role session is created by an Amazon EC2 instance.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – arn:aws:ec2:us-west-2:111111111111:instance/instance-id

For policy examples, see [Allow a specific instance to view resources in other AWS services](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ExamplePolicies_EC2.html#iam-example-source-instance).

### glue:RoleAssumedBy
<a name="condition-keys-glue-role-assumed-by"></a>

The AWS Glue service sets this condition key for each AWS API request where AWS Glue makes a request using a service role on the customer's behalf (not by a job or developer endpoint, but directly by the AWS Glue service). Use this key to verify whether a call to an AWS resource came from the AWS Glue service.
+ **Availability** – This key is included in the request context when AWS Glue makes a request using a service role on the customer's behalf.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued
+ **Example value** – This key is always set to `glue.amazonaws.com`.

The following example adds a condition to allow the AWS Glue service to get an object from an Amazon S3 bucket.

```
{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
    "Condition": {
        "StringEquals": {
            "glue:RoleAssumedBy": "glue.amazonaws.com"
        }
    }
}
```

### glue:CredentialIssuingService
<a name="condition-keys-glue-credential-issuing"></a>

The AWS Glue service sets this key for each AWS API request using a service role that comes from a job or developer endpoint. Use this key to verify whether a call to an AWS resource came from an AWS Glue job or developer endpoint.
+ **Availability** – This key is included in the request context when AWS Glue makes a request that comes from a job or developer endpoint.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued
+ **Example value** – This key is always set to `glue.amazonaws.com`.

The following example adds a condition that is attached to an IAM role that is used by an AWS Glue job. This ensures certain actions are allowed/denied based on whether the role session is used for an AWS Glue job runtime environment.

```
{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
    "Condition": {
        "StringEquals": {
            "glue:CredentialIssuingService": "glue.amazonaws.com"
        }
    }
}
```

### codebuild:BuildArn
<a name="condition-keys-codebuild-build-arn"></a>

This key identifies the CodeBuild build ARN that IAM role credentials were delivered to. Use this key to verify whether a call to an AWS resource came from a specific CodeBuild build.

**Note**  
The full value of `codebuild:BuildArn` is not known in advance because it contains the dynamically generated build ID.
+ **Availability** – This key is included in the request context whenever a request is made by a role assumed by CodeBuild.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – arn:aws:codebuild:us-east-1:123456789012:build/MyBuildProject:12345678-1234-1234-1234-123456789012

The following example allows a specific CodeBuild build to have `s3:GetObject` access to the specified bucket.

```
{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
    "Condition": {
        "ArnLike": {
            "codebuild:BuildArn": "arn:aws:codebuild:us-east-1:123456789012:build/MyBuildProject:*"
        }
    }
}
```

### codebuild:ProjectArn
<a name="condition-keys-codebuild-project-arn"></a>

This key identifies the CodeBuild project ARN that IAM role credentials were delivered to an CodeBuild build. Use this key to verify whether a call to an AWS resource came from a specific CodeBuild project.
+ **Availability** – This key is included in the request context whenever a request is made by a role assumed by CodeBuild.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – arn:aws:codebuild:us-east-1:123456789012:project/MyBuildProject

The following example allows any build from a specific CodeBuild project to have `s3:GetObject` access to the specified bucket.

```
{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
    "Condition": {
        "ArnEquals": {
            "codebuild:ProjectArn": "arn:aws:codebuild:us-east-1:123456789012:project/MyBuildProject"
        }
    }
}
```

### lambda:SourceFunctionArn
<a name="condition-keys-lambda-source-function-arn"></a>

Use this key to identify the Lambda function ARN that IAM role credentials were delivered to. The Lambda service sets this key for each AWS API request that comes from your function's execution environment. Use this key to verify whether a call to an AWS resource came from a specific Lambda function’s code. Lambda also sets this key for some requests that come from outside the execution environment, such as writing logs to CloudWatch and sending traces to X-Ray.
+ **Availability** – This key is included in the request context whenever Lambda function code is invoked.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – arn:aws:lambda:us-east-1:123456789012:function:TestFunction

The following example allows one specific Lambda function to have `s3:PutObject` access the specified bucket.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "ExampleSourceFunctionArn",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::amzn-s3-demo-bucket/*",
            "Condition": {
                "ArnEquals": {
                    "lambda:SourceFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:source_lambda"
                }
            }
        }
    ]
}
```

------

For more information, see [Working with Lambda execution environment credentials](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html#permissions-executionrole-source-function-arn) in the *AWS Lambda Developer Guide*.

### ssm:SourceInstanceArn
<a name="condition-keys-ssm-source-instance-arn"></a>

Use this key to identify the AWS Systems Manager managed instance ARN that IAM role credentials were delivered to. This condition key is not present when the request comes from a managed instance with an IAM role associated with an Amazon EC2 instance profile.
+ **Availability** – This key is included in the request context whenever role credentials are delivered to an AWS Systems Manager managed instance.
+ **Data type** – [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN)
+ **Value type** – Single-valued
+ **Example value** – arn:aws:ec2:us-west-2:111111111111:instance/instance-id

### identitystore:UserId
<a name="condition-keys-identity-store-user-id"></a>

Use this key to compare IAM Identity Center workforce identity in the signed request with the identity specified in the policy. 
+ **Availability** – This key is included when the caller of the request is a user in IAM Identity Center.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued
+ **Example value** – 94482488-3041-7026-18f3-be45837cd0e4

You can find the UserId of a user in IAM Identity Center by making a request to the [GetUserId](https://docs.aws.amazon.com//singlesignon/latest/IdentityStoreAPIReference/API_GetUserId.html) API using the AWS CLI, AWS API, or AWS SDK.

## Properties of the network
<a name="condition-keys-network-properties"></a>

Use the following condition keys to compare details about the network that the request originated from or passed through with the network properties that you specify in the policy.

### aws:SourceIp
<a name="condition-keys-sourceip"></a>

Use this key to compare the requester's IP address with the IP address that you specify in the policy. The `aws:SourceIp` condition key can only be used for public IP address ranges.
+ **Availability** – This key is included in the request context, except when the requester uses a VPC endpoint to make the request.
+ **Data type** – [IP address](reference_policies_elements_condition_operators.md#Conditions_IPAddress)
+ **Value type** – Single-valued

The `aws:SourceIp` condition key can be used in a policy to allow principals to make requests only from within a specified IP range.

**Note**  
`aws:SourceIp` supports both IPv4 and IPv6 address or range of IP addresses. For a list of AWS services that support IPv6, see [AWS services that support IPv6](https://docs.aws.amazon.com/vpc/latest/userguide/aws-ipv6-support.html) in the *Amazon VPC User Guide*.

For example, you can attach the following identity-based policy to an IAM role. This policy allows the user to put objects into the `amzn-s3-demo-bucket3` Amazon S3 bucket if they make the call from the specified IPv4 address range. This policy also allows an AWS service that uses [Forward access sessions](access_forward_access_sessions.md) to perform this operation on your behalf.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "PrincipalPutObjectIfIpAddress",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::amzn-s3-demo-bucket3/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": "{{203.0.113.0/24}}"
                }
            }
        }
    ]
}
```

------

If you need to restrict access from networks that support both IPv4 and IPv6 addressing, you can include the IPv4 and IPv6 address or ranges of IP addresses in the IAM policy condition. The following identity-based policy will allow the user to put objects into the `amzn-s3-demo-bucket3` Amazon S3 bucket if the user makes the call from either specified IPv4 or IPv6 address ranges. Before you include IPv6 address ranges in your IAM policy, verify that the AWS service you are working with supports IPv6. For a list of AWS services that support IPv6, see [AWS services that support IPv6](https://docs.aws.amazon.com/vpc/latest/userguide/aws-ipv6-support.html) in the *Amazon VPC User Guide*.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "PrincipalPutObjectIfIpAddress",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::amzn-s3-demo-bucket3/*",
            "Condition": {
                "IpAddress": {
                    "aws:SourceIp": [
                        "{{203.0.113.0/24}}",
                        "{{2001:DB8:1234:5678::/64}}"
                    ]
                }
            }
        }
    ]
}
```

------

If the request comes from a host that uses an Amazon VPC endpoint, then the `aws:SourceIp` key is not available. You should instead use a VPC-specific key such as [aws:VpcSourceIp](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html#condition-keys-vpcsourceip). For more information about using VPC endpoints, see [Identity and access management for VPC endpoints and VPC endpoint services](https://docs.aws.amazon.com/vpc/latest/privatelink/vpc-endpoints-iam.html) in the *AWS PrivateLink Guide*.

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

### aws:SourceVpc
<a name="condition-keys-sourcevpc"></a>

Use this key to check whether the request travels through the VPC that the VPC endpoint is attached to. In a policy, you can use this key to allow access to only a specific VPC. For more information, see [Restricting Access to a Specific VPC](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html#example-bucket-policies-restrict-access-vpc) in the *Amazon Simple Storage Service User Guide*. 
+ **Availability** – This key is included in the request context only if the requester uses a VPC endpoint to make the request.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

In a policy, you can use this key to allow or restrict access to a specific VPC.

For example, you can attach the following identity-based policy to an IAM role to deny `PutObject` to the `amzn-s3-demo-bucket3` Amazon S3 bucket, unless the request is made from the specified VPC ID or by AWS services that use [forward access sessions (FAS)](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_forward_access_sessions.html) to make requests on behalf of the role. Unlike with [aws:SourceIp](#condition-keys-sourceip), you must use [aws:ViaAWSService](#condition-keys-viaawsservice) or [aws:CalledVia](#condition-keys-calledvia) to allow FAS requests, because the source VPC of the initial request is not preserved.

**Note**  
This policy does not allow any actions. Use this policy in combination with other policies that allow specific actions.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "PutObjectIfNotVPCID",
      "Effect": "Deny",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::amzn-s3-demo-bucket3/*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:SourceVpc": "vpc-1234567890abcdef0"
        },
        "Bool": {
          "aws:ViaAWSService": "false"
        }
      }
    }
  ]
}
```

------

**Note**  
AWS recommends to use `aws:SourceVpcArn` instead of `aws:SourceVpc` if `aws:SourceVpcArn` is supported by the service you are targeting. Please refer to [aws:SourceVpcArn](#condition-keys-sourcevpcarn) for the list of supported services.

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

### aws:SourceVpcArn
<a name="condition-keys-sourcevpcarn"></a>

Use this key to verify the ARN of the VPC that a request passed through using a VPC endpoint. This key returns the ARN of the VPC to which the VPC endpoint is attached.
+ **Availability** – This key is included in the request context for supported services when a request is made through a VPC endpoint. The key is not included for requests made through public service endpoints. The following services support this key:
  + AWS App Runner (prefix: [`apprunner`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapprunner.html))
  + AWS Application Discovery Service (prefix: [`discovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationdiscoveryservice.html))
  + Amazon Athena (prefix: [`athena`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonathena.html))
  + AWS Cloud Map (prefix: [`servicediscovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudmap.html))
  + Amazon CloudWatch Application Insights (prefix: [`applicationinsights`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationinsights.html))
  + AWS CloudFormation (prefix: [`cloudformation`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudformation.html))
  + Amazon Comprehend Medical (prefix: [`comprehendmedical`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehendmedical.html))
  + AWS Compute Optimizer (prefix: [`compute-optimizer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscomputeoptimizer.html))
  + Amazon; Elastic Container Registry (prefix: [`ecr`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistry.html))
  + Amazon Elastic Container Service (prefix: [`ecs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerservice.html))
  + Amazon Kinesis Analytics (prefix: [`kinesisanalytics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalytics.html))
  + Amazon Route 53 (prefix: [`route53`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53.html))
  + AWS DataSync (prefix: [`datasync`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatasync.html))
  + Amazon Elastic Block Store (prefix: [`ebs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticblockstore.html))
  + Amazon EventBridge Scheduler (prefix: [`scheduler`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgescheduler.html))
  + Amazon Data Firehose (prefix: [`firehose`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisfirehose.html))
  + AWS HealthImaging (prefix: [`medical-imaging`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthimaging.html))
  + AWS HealthLake (prefix: [`healthlake`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthlake.html))
  + AWS HealthOmics (prefix: [`omics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthomics.html))
  + AWS Identity and Access Management (except for the `iam:PassRole` action) (prefix: [`iam`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementiam.html))
  + AWS IoT FleetWise (prefix: [`iotfleetwise`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleetwise.html))
  + AWS IoT Wireless (prefix: [`iotwireless`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotwireless.html))
  + AWS Key Management Service (prefix: [`kms`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awskeymanagementservice.html))
  + AWS Lambda (prefix: [`lambda`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslambda.html))
  + AWS Payment Cryptography (prefix: [`payment-cryptography`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspaymentcryptography.html))
  + Amazon Polly (prefix: [`polly`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpolly.html))
  + AWS Private Certificate Authority (prefix: [`acm-pca`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecertificateauthority.html))
  + AWS Recycle Bin (prefix: [`rbin`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrecyclebin.html))
  + Amazon Rekognition (prefix: [`rekognition`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrekognition.html))
  + Service Quotas (prefix: [`servicequotas`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_servicequotas.html))
  + Amazon Simple Storage Service (prefix: [`s3`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html))
  + AWS Storage Gateway (prefix: [`storagegateway`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstoragegateway.html))
  + AWS Systems Manager Incident Manager Contacts (prefix: [`ssm-contacts`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanagercontacts.html))
  + Amazon Textract (prefix: [`textract`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html))
  + Amazon Transcribe (prefix: [`transcribe`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranscribe.html))
  + AWS Transfer Family (prefix: [`transfer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstransferfamily.html))
+ **Data type** – ARN

  AWS recommends that you use [ARN operators](reference_policies_elements_condition_operators.md#Conditions_ARN) instead of [string operators](reference_policies_elements_condition_operators.md#Conditions_String) when comparing ARNs.
+ **Value type** – Single-valued
+ **Example value** – `arn:aws:ec2:us-east-1:123456789012:vpc/vpc-0e9801d129EXAMPLE`

The following is an example of a bucket policy that denies access to `amzn-s3-demo-bucket` and its objects from anywhere outside VPC `vpc-1a2b3c4d`.

```
{
   "Version":"2012-10-17",		 	 	 
   "Statement": [
     {
       "Sid": "Access-to-specific-VPC-only",
       "Principal": "*",
       "Action": "s3:*",
       "Effect": "Deny",
       "Resource": ["arn:aws:s3:::amzn-s3-demo-bucket",
                    "arn:aws:s3:::amzn-s3-demo-bucket/*"],
       "Condition": {
         "ArnNotEquals": {
           "aws:SourceVpcArn": "arn:aws:ec2:us-east-1:*:vpc/vpc-1a2b3c4d"
         }
       }
     }
   ]
}
```

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

### aws:SourceVpce
<a name="condition-keys-sourcevpce"></a>

Use this key to compare the VPC endpoint identifier of the request with the endpoint ID that you specify in the policy.
+ **Availability** – This key is included in the request context only if the requester uses a VPC endpoint to make the request.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

In a policy, you can use this key to restrict access to a specific VPC endpoint. For more information, see [Restricting access to a specific VPC](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies-vpc-endpoint.html#example-bucket-policies-restrict-access-vpc) in the *Amazon Simple Storage Service User Guide*. Similarly to using [aws:SourceVpc](#condition-keys-sourcevpc), you must use [aws:ViaAWSService](#condition-keys-viaawsservice) or [aws:CalledVia](#condition-keys-calledvia) to allow requests made by AWS services using [forward access sessions (FAS)](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_forward_access_sessions.html). This is because the source VPC endpoint of the initial request is not preserved.

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

### aws:VpceAccount
<a name="condition-keys-vpceaccount"></a>

Use this key to compare the AWS account ID that owns the VPC endpoint through which the request was made with the account ID that you specify in the policy. This condition key helps you establish network perimeter controls by ensuring requests come through VPC endpoints owned by specific accounts.
+ **Availability** – This key is included in the request context when a request is made through a VPC endpoint. The key is not included for requests made through public service endpoints.

  The following services support this key:
  + AWS App Runner (prefix: [`apprunner`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapprunner.html))
  + AWS Application Discovery Service (prefix: [`discovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationdiscoveryservice.html))
  + Amazon Athena (prefix: [`athena`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonathena.html))
  + AWS Cloud Map (prefix: [`servicediscovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudmap.html))
  + Amazon CloudWatch Application Insights (prefix: [`applicationinsights`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationinsights.html))
  + AWS CloudFormation (prefix: [`cloudformation`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudformation.html))
  + Amazon Comprehend Medical (prefix: [`comprehendmedical`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehendmedical.html))
  + AWS Compute Optimizer (prefix: [`compute-optimizer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscomputeoptimizer.html))
  + Amazon; Elastic Container Registry (prefix: [`ecr`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistry.html))
  + Amazon Elastic Container Service (prefix: [`ecs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerservice.html))
  + Amazon Kinesis Analytics (prefix: [`kinesisanalytics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalytics.html))
  + Amazon Route 53 (prefix: [`route53`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53.html))
  + AWS DataSync (prefix: [`datasync`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatasync.html))
  + Amazon DynamoDB (prefix: [`dynamodb`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html))
  + Amazon Elastic Block Store (prefix: [`ebs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticblockstore.html))
  + Amazon EventBridge Scheduler (prefix: [`scheduler`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgescheduler.html))
  + Amazon Data Firehose (prefix: [`firehose`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisfirehose.html))
  + Amazon GameLift (prefix: [`gamelift`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazongameliftservers.html))
  + AWS HealthImaging (prefix: [`medical-imaging`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthimaging.html))
  + AWS HealthLake (prefix: [`healthlake`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthlake.html))
  + AWS HealthOmics (prefix: [`omics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthomics.html))
  + AWS Identity and Access Management (except for the `iam:PassRole` action) (prefix: [`iam`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementiam.html))
  + AWS IoT FleetWise (prefix: [`iotfleetwise`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleetwise.html))
  + AWS IoT Wireless (prefix: [`iotwireless`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotwireless.html))
  + AWS Key Management Service (prefix: [`kms`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awskeymanagementservice.html))
  + AWS Lambda (prefix: [`lambda`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslambda.html))
  + AWS Payment Cryptography (prefix: [`payment-cryptography`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspaymentcryptography.html))
  + Amazon Polly (prefix: [`polly`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpolly.html))
  + AWS Private Certificate Authority (prefix: [`acm-pca`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecertificateauthority.html))
  + AWS Recycle Bin (prefix: [`rbin`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrecyclebin.html))
  + Amazon Rekognition (prefix: [`rekognition`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrekognition.html))
  + Service Quotas (prefix: [`servicequotas`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_servicequotas.html))
  + Amazon Simple Storage Service (prefix: [`s3`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html))
  + AWS Shield (prefix: [`shield`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsshield.html))
  + AWS Storage Gateway (prefix: [`storagegateway`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstoragegateway.html))
  + AWS Systems Manager Incident Manager Contacts (prefix: [`ssm-contacts`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanagercontacts.html))
  + Amazon Textract (prefix: [`textract`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html))
  + Amazon Transcribe (prefix: [`transcribe`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranscribe.html))
  + AWS Transfer Family (prefix: [`transfer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstransferfamily.html))
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued
+ **Example value** – `123456789012`

You can use this condition key to restrict access to resources so that requests must come through VPC endpoints owned by your account. The following Amazon S3 bucket policy example allows access when the request comes through a VPC endpoint owned by the specified account:

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "AccessToSpecificVpceAccountOnly",
            "Principal": {
                "AWS": "arn:aws:iam::{{111122223333}}:role/{{RoleName}}"
            },
            "Action": "s3:GetObject",
            "Effect": "Allow",
            "Resource": "arn:aws:s3:::{{amzn-s3-demo-bucket1}}/*",
            "Condition": {
                "StringEquals": {
                    "aws:VpceAccount": "111122223333"
                }
            }
        }
    ]
}
```

------

**Note**  
This condition key is currently supported for a select set of AWS services. Using this key with unsupported services can lead to unintended authorization results. Always scope the condition key to supported services in your policies.

Some AWS services access your resources from their networks when they act on your behalf. If you use such services, you will need to edit the above policy example to allow AWS services access your resources from outside your network. For more information on access patterns that need to be accounted for when enforcing access controls based on the request origin, see [Establish permissions guardrails using data perimeters](access_policies_data-perimeters.md).

### aws:VpceOrgID
<a name="condition-keys-vpceorgid"></a>

Use this key to compare the identifier of the organization in AWS Organizations that owns the VPC endpoint from which the request was made with the identifier that you specify in the policy. This condition key provides the most scalable approach to network perimeter controls, automatically including all VPC endpoints owned by accounts within your organization.
+ **Availability** – This key is included in the request context when a request is made through a VPC endpoint and the VPC endpoint owner account is a member of an AWS organization. The key is not included for requests made through other network paths or when the VPC endpoint owner account is not part of an organization.

  The following services support this key:
  + AWS App Runner (prefix: [`apprunner`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapprunner.html))
  + AWS Application Discovery Service (prefix: [`discovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationdiscoveryservice.html))
  + Amazon Athena (prefix: [`athena`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonathena.html))
  + AWS B2B Data Interchange (prefix: [`b2bi`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsb2bdatainterchange.html))
  + AWS Cloud Map (prefix: [`servicediscovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudmap.html))
  + Amazon CloudWatch Application Insights (prefix: [`applicationinsights`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationinsights.html))
  + AWS CloudFormation (prefix: [`cloudformation`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudformation.html))
  + Amazon Cognito (prefix: [`cognito-identity`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncognitoidentity.html))
  + Amazon Comprehend Medical (prefix: [`comprehendmedical`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehendmedical.html))
  + AWS Compute Optimizer (prefix: [`compute-optimizer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscomputeoptimizer.html))
  + AWS Database Migration Service (prefix: [`dms`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatabasemigrationservice.html))
  + AWS Directory Service Data (prefix: [`ds-data`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdirectoryservicedata.html))
  + Amazon DynamoDB (prefix: [`dynamodb`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html))
  + Amazon; Elastic Container Registry (prefix: [`ecr`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistry.html))
  + Amazon Elastic Container Service (prefix: [`ecs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerservice.html))
  + Amazon Kinesis Analytics (prefix: [`kinesisanalytics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalytics.html))
  + Amazon Route 53 (prefix: [`route53`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53.html))
  + AWS DataSync (prefix: [`datasync`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatasync.html))
  + Amazon Elastic Block Store (prefix: [`ebs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticblockstore.html))
  + Amazon EventBridge Scheduler (prefix: [`scheduler`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgescheduler.html))
  + Amazon Data Firehose (prefix: [`firehose`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisfirehose.html))
  + Amazon GameLift (prefix: [`gamelift`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazongameliftservers.html))
  + AWS HealthImaging (prefix: [`medical-imaging`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthimaging.html))
  + AWS HealthLake (prefix: [`healthlake`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthlake.html))
  + AWS HealthOmics (prefix: [`omics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthomics.html))
  + AWS Identity and Access Management (except for the `iam:PassRole` action) (prefix: [`iam`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementiam.html))
  + AWS Identity Store (prefix: [`identitystore`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentitystore.html))
  + AWS IoT FleetWise (prefix: [`iotfleetwise`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleetwise.html))
  + AWS IoT TwinMaker (prefix: [`iottwinmaker`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiottwinmaker.html))
  + AWS IoT Wireless (prefix: [`iotwireless`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotwireless.html))
  + Amazon Keyspaces (for Apache Cassandra) (prefix: [`cassandra`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkeyspacesforapachecassandra.html))
  + AWS Key Management Service (prefix: [`kms`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awskeymanagementservice.html))
  + AWS Lambda (prefix: [`lambda`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslambda.html))
  + AWS Network Firewall (prefix: [`network-firewall`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsnetworkfirewall.html))
  + AWS Payment Cryptography (prefix: [`payment-cryptography`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspaymentcryptography.html))
  + Amazon Pinpoint SMS and Voice Service (prefix: [`sms-voice`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpinpointsmsandvoiceservice.html))
  + Amazon Polly (prefix: [`polly`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpolly.html))
  + AWS Price List (prefix: [`pricing`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspricelist.html))
  + AWS Private Certificate Authority (prefix: [`acm-pca`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecertificateauthority.html))
  + AWS Recycle Bin (prefix: [`rbin`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrecyclebin.html))
  + Amazon Rekognition (prefix: [`rekognition`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrekognition.html))
  + Service Quotas (prefix: [`servicequotas`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_servicequotas.html))
  + Amazon Simple Email Service (prefix: [`ses`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonses.html))
  + AWS Shield (prefix: [`shield`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsshield.html))
  + Amazon Simple Storage Service (prefix: [`s3`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html))
  + Amazon Simple Queue Service (prefix: [`sqs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonsqs.html))
  + AWS Storage Gateway (prefix: [`storagegateway`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstoragegateway.html))
  + AWS Systems Manager Incident Manager Contacts (prefix: [`ssm-contacts`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanagercontacts.html))
  + Amazon Textract (prefix: [`textract`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html))
  + Amazon Transcribe (prefix: [`transcribe`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranscribe.html))
  + AWS Transfer Family (prefix: [`transfer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstransferfamily.html))
  + Amazon WorkMail (prefix: [`workmail`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonworkmail.html))
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued
+ **Example values** – `o-a1b2c3d4e5`

The following resource control policy example denies access to your Amazon S3 and AWS Key Management Service resources unless the request comes through VPC endpoints owned by the specified organization or from networks of AWS services that act on your behalf. Some organizations might need to further edit this policy to meet the needs of their organization, for example, allow third-party partner access. For more information on access patterns that need to be accounted for when enforcing access controls based on the request origin, see [Establish permissions guardrails using data perimeters](access_policies_data-perimeters.md).

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "EnforceNetworkPerimeterVpceOrgID",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:*",
        "kms:*"
      ],
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:PrincipalIsAWSService": "false",
          "aws:ViaAWSService": "false"
        },
        "StringNotEqualsIfExists": {
            "aws:VpceOrgID": "{{o-abcdef0123}}",
            "aws:PrincipalTag/{{network-perimeter-exception}}": "true"
        }
      }
    }
  ]
}
```

------

**Note**  
This condition key is currently supported for a select set of AWS services. Using this key with unsupported services can lead to unintended authorization results. Always scope the condition key to supported services in your policies.

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

### aws:VpceOrgPaths
<a name="condition-keys-vpceorgpaths"></a>

Use this key to compare the AWS Organizations path for the VPC endpoint from which the request was made with the path that you specify in the policy. This condition key enables you to implement network perimeter controls at the organizational unit (OU) level, automatically scaling with your VPC endpoint usage as you add new endpoints within the specified OUs.
+ **Availability** – This key is included in the request context when a request is made through a VPC endpoint and the VPC endpoint owner account is a member of an organization. The key is not included for requests made through other network paths or when the VPC endpoint owner account is not part of an organization.

  The following services support this key:
  + AWS App Runner (prefix: [`apprunner`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapprunner.html))
  + AWS Application Discovery Service (prefix: [`discovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsapplicationdiscoveryservice.html))
  + Amazon Athena (prefix: [`athena`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonathena.html))
  + AWS Cloud Map (prefix: [`servicediscovery`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudmap.html))
  + Amazon CloudWatch Application Insights (prefix: [`applicationinsights`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncloudwatchapplicationinsights.html))
  + AWS CloudFormation (prefix: [`cloudformation`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscloudformation.html))
  + Amazon Comprehend Medical (prefix: [`comprehendmedical`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoncomprehendmedical.html))
  + AWS Compute Optimizer (prefix: [`compute-optimizer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awscomputeoptimizer.html))
  + Amazon; Elastic Container Registry (prefix: [`ecr`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerregistry.html))
  + Amazon Elastic Container Service (prefix: [`ecs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticcontainerservice.html))
  + Amazon Kinesis Analytics (prefix: [`kinesisanalytics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisanalytics.html))
  + Amazon Route 53 (prefix: [`route53`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonroute53.html))
  + AWS DataSync (prefix: [`datasync`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsdatasync.html))
  + Amazon DynamoDB (prefix: [`dynamodb`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazondynamodb.html))
  + Amazon Elastic Block Store (prefix: [`ebs`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonelasticblockstore.html))
  + Amazon EventBridge Scheduler (prefix: [`scheduler`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazoneventbridgescheduler.html))
  + Amazon Data Firehose (prefix: [`firehose`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonkinesisfirehose.html))
  + Amazon GameLift (prefix: [`gamelift`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazongameliftservers.html))
  + AWS HealthImaging (prefix: [`medical-imaging`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthimaging.html))
  + AWS HealthLake (prefix: [`healthlake`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthlake.html))
  + AWS HealthOmics (prefix: [`omics`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awshealthomics.html))
  + AWS Identity and Access Management (except for the `iam:PassRole` action) (prefix: [`iam`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsidentityandaccessmanagementiam.html))
  + AWS IoT FleetWise (prefix: [`iotfleetwise`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotfleetwise.html))
  + AWS IoT Wireless (prefix: [`iotwireless`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsiotwireless.html))
  + AWS Key Management Service (prefix: [`kms`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awskeymanagementservice.html))
  + AWS Lambda (prefix: [`lambda`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awslambda.html))
  + AWS Payment Cryptography (prefix: [`payment-cryptography`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awspaymentcryptography.html))
  + Amazon Polly (prefix: [`polly`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonpolly.html))
  + AWS Private Certificate Authority (prefix: [`acm-pca`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsprivatecertificateauthority.html))
  + AWS Recycle Bin (prefix: [`rbin`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsrecyclebin.html))
  + Amazon Rekognition (prefix: [`rekognition`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonrekognition.html))
  + Service Quotas (prefix: [`servicequotas`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_servicequotas.html))
  + Amazon Simple Storage Service (prefix: [`s3`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html))
  + AWS Shield (prefix: [`shield`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsshield.html))
  + AWS Storage Gateway (prefix: [`storagegateway`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awsstoragegateway.html))
  + AWS Systems Manager Incident Manager Contacts (prefix: [`ssm-contacts`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awssystemsmanagerincidentmanagercontacts.html))
  + Amazon Textract (prefix: [`textract`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html))
  + Amazon Transcribe (prefix: [`transcribe`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontranscribe.html))
  + AWS Transfer Family (prefix: [`transfer`](https://docs.aws.amazon.com/service-authorization/latest/reference/list_awstransferfamily.html))
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued
+ **Example values** – `o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/`

Since `aws:VpceOrgPaths` is a multivalued condition key, you must use the `ForAnyValue` or `ForAllValues` set operators with [string condition operators](reference_policies_elements_condition_operators.md#Conditions_String) for this key. The following Amazon S3 bucket policy example allows access only when requests come through VPC endpoints owned by accounts in specific organizational units:

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "AllowAccessFromSpecificOrgPaths",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::{{111122223333}}:role/RoleName"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::{{amzn-s3-demo-bucket1}}/*",
      "Condition": {
        "ForAnyValue:StringLike": {
          "aws:VpceOrgPaths": [
            "{{o-a1b2c3d4e5}}/{{r-ab12}}/{{ou-ab12-11111111}}/{{ou-ab12-22222222}}/*",
            "{{o-a1b2c3d4e5}}/{{r-ab12}}/{{ou-ab12-11111111}}/{{ou-ab12-33333333}}/*"
          ]
        }
      }
    }
  ]
}
```

------

**Note**  
This condition key is currently supported for a select set of AWS services. Using this key with unsupported services can lead to unintended authorization results. Always scope the condition key to supported services in your policies.

Some AWS services access your resources from their networks when they act on your behalf. If you use such services, you will need to edit the above policy example to allow AWS services access your resources from outside your network. For more information on access patterns that need to be accounted for when enforcing access controls based on the request origin, see [Establish permissions guardrails using data perimeters](access_policies_data-perimeters.md).

### aws:VpcSourceIp
<a name="condition-keys-vpcsourceip"></a>

Use this key to compare the IP address from which a request was made with the IP address that you specify in the policy. In a policy, the key matches only if the request originates from the specified IP address and it goes through a VPC endpoint.
+ **Availability** – This key is included in the request context only if the request is made using a VPC endpoint.
+ **Data type** – [IP address](reference_policies_elements_condition_operators.md#Conditions_IPAddress)
+ **Value type** – Single-valued

For more information, see [Control access to VPC endpoints using endpoint policies](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints-access.html) in the *Amazon VPC User Guide*. Similarly to using [aws:SourceVpc](#condition-keys-sourcevpc), you must use [aws:ViaAWSService](#condition-keys-viaawsservice) or [aws:CalledVia](#condition-keys-calledvia) to allow requests made by AWS services using [forward access sessions (FAS)](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_forward_access_sessions.html). This is because the source IP of the initial request made using a VPC endpoint is not preserved in FAS requests.

**Note**  
`aws:VpcSourceIp` supports both IPv4 and IPv6 address or range of IP addresses. For a list of AWS services that support IPv6, see [AWS services that support IPv6](https://docs.aws.amazon.com/vpc/latest/userguide/aws-ipv6-support.html) in the *Amazon VPC User Guide*.  
Always use the `aws:VpcSourceIp` condition key with the `aws:SourceVpc`, `aws:SourceVpce`, or `aws:SourceVpcArn` condition keys. If you don't, a policy might permit API calls from an unexpected VPC that uses the same or overlapping IP CIDR. This can happen because IP CIDRs from two unrelated VPCs can be the same or overlap.

**Note**  
When AWS services make calls to other AWS services on your behalf (service-to-service calls), certain network-specific authorization context is redacted. If your policy uses this condition key with `Deny` statements, AWS service principals might be unintentionally blocked. To allow AWS services to work properly while maintaining your security requirements, exclude service principals from your `Deny` statements by adding the `aws:PrincipalIsAWSService` condition key with a value of `false`.

## Properties of the resource
<a name="condition-keys-resource-properties"></a>

Use the following condition keys to compare details about the resource that is the target of the request with the resource properties that you specify in the policy.

### aws:ResourceAccount
<a name="condition-keys-resourceaccount"></a>

Use this key to compare the requested resource owner's [AWS account ID](https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html) with the resource account in the policy. You can then allow or deny access to that resource based on the account that owns the resource.
+ **Availability** – This key is always included in the request context for most service actions. The following actions don't support this key:
  + AWS Audit Manager
    + `auditmanager:UpdateAssessmentFrameworkShare`
  + Amazon Detective
    + `detective:AcceptInvitation`
  + AWS Directory Service
    + `ds:AcceptSharedDirectory`
  + Amazon Elastic Block Store – All actions
  + Amazon EC2
    + `ec2:AcceptTransitGatewayPeeringAttachment`
    + `ec2:AcceptVpcEndpointConnections`
    + `ec2:AcceptVpcPeeringConnection`
    + `ec2:CreateTransitGatewayPeeringAttachment`
    + `ec2:CreateVpcEndpoint`
    + `ec2:CreateVpcPeeringConnection`
  + Amazon EventBridge
    + `events:PutEvents` – EventBridge `PutEvents` calls on an event bus in another account, if that event bus was configured as a cross-account EventBridge target before March 2, 2023. For more information, see [Grant permissions to allow events from other AWS accounts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html#eb-receiving-events-from-another-account) in the *Amazon EventBridge User Guide*.
  + Amazon GuardDuty
    + `guardduty:AcceptAdministratorInvitation`
  + Amazon Macie
    + `macie2:AcceptInvitation`
  + Amazon OpenSearch Service
    + `es:AcceptInboundConnection`
  + Amazon Route 53
    + `route53:AssociateVpcWithHostedZone`
    + `route53:CreateVPCAssociationAuthorization`
  + AWS Security Hub CSPM
    + `securityhub:AcceptAdministratorInvitation`
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

**Note**  
For additional considerations for the above unsupported actions, see the [Data Perimeter Policy Examples](https://github.com/aws-samples/data-perimeter-policy-examples) repository.

This key is equal to the AWS account ID for the account with the resources evaluated in the request.

For most resources in your account, the [ARN](reference_policies_elements_condition_operators.md#Conditions_ARN) contains the owner account ID for that resource. For certain resources, such as Amazon S3 buckets, the resource ARN does not include the account ID. The following two examples show the difference between a resource with an account ID in the ARN, and an Amazon S3 ARN without an account ID:
+ `arn:aws:iam::123456789012:role/AWSExampleRole` – IAM role created and owned within the account 123456789012. 
+ `arn:aws:s3:::amzn-s3-demo-bucket2` – Amazon S3 bucket created and owned within the account `111122223333`, not displayed in the ARN.

Use the AWS console, or API, or CLI, to find all of your resources and corresponding ARNs.

You write a policy that denies permissions to resources based on the resource owner's account ID. For example, the following identity-based policy denies access to the *specified resource* if the resource does not belong to the *specified account*.

To use this policy, replace the *italicized placeholder text* with your account information. 

**Important**  
This policy does not allow any actions. Instead, it uses the `Deny` effect which explicitly denies access to all of the resources listed in the statement that do not belong to the listed account. Use this policy in combination with other policies that allow access to specific resources.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "DenyInteractionWithResourcesNotInSpecificAccount",
      "Action": "{{service}}:*",
      "Effect": "Deny",
      "Resource": [
        "arn:aws:{{service}}:{{us-east-1}}:{{111122223333}}:{{*}}"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:ResourceAccount": [
            "{{111122223333}}"
          ]
        }
      }
    }
  ]
}
```

------

This policy denies access to all resources for a specific AWS service unless the specified AWS account owns the resource. 

**Note**  
Some AWS services require access to AWS owned resources that are hosted in another AWS account. Using `aws:ResourceAccount` in your identity-based policies might impact your identity's ability to access these resources.

Certain AWS services, such as AWS Data Exchange, rely on access to resources outside of your AWS accounts for normal operations. If you use the element `aws:ResourceAccount` in your policies, include additional statements to create exemptions for those services. The example policy [AWS: Deny access to Amazon S3 resources outside your account except AWS Data Exchange](reference_policies_examples_resource_account_data_exch.md) demonstrates how to deny access based on the resource account while defining exceptions for service-owned resources.

Use this policy example as a template for creating your own custom policies. Refer to your service [documentation](https://docs.aws.amazon.com/index.html) for more information.

### aws:ResourceOrgPaths
<a name="condition-keys-resourceorgpaths"></a>

Use this key to compare the AWS Organizations path for the accessed resource to the path in the policy. In a policy, this condition key ensures that the resource belongs to an account member within the specified organization root or organizational units (OUs) in AWS Organizations. An AWS Organizations path is a text representation of the structure of an Organizations entity. For more information about using and understanding paths, see [Understand the AWS Organizations entity path](access_policies_last-accessed-view-data-orgs.md#access_policies_last-accessed-viewing-orgs-entity-path) 
+ **Availability** – This key is included in the request context only if the account that owns the resource is a member of an organization. This global condition key does not support the following actions:
  + AWS Audit Manager
    + `auditmanager:UpdateAssessmentFrameworkShare`
  + Amazon Detective
    + `detective:AcceptInvitation`
  + AWS Directory Service
    + `ds:AcceptSharedDirectory`
  + Amazon Elastic Block Store – All actions
  + Amazon EC2
    + `ec2:AcceptTransitGatewayPeeringAttachment`
    + `ec2:AcceptVpcEndpointConnections`
    + `ec2:AcceptVpcPeeringConnection`
    + `ec2:CreateTransitGatewayPeeringAttachment`
    + `ec2:CreateVpcEndpoint`
    + `ec2:CreateVpcPeeringConnection`
  + Amazon EventBridge
    + `events:PutEvents` – EventBridge `PutEvents` calls on an event bus in another account, if that event bus was configured as a cross-account EventBridge target before March 2, 2023. For more information, see [Grant permissions to allow events from other AWS accounts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html#eb-receiving-events-from-another-account) in the *Amazon EventBridge User Guide*.
  + Amazon GuardDuty
    + `guardduty:AcceptAdministratorInvitation`
  + Amazon Macie
    + `macie2:AcceptInvitation`
  + Amazon OpenSearch Service
    + `es:AcceptInboundConnection`
  + Amazon Route 53
    + `route53:AssociateVpcWithHostedZone`
    + `route53:CreateVPCAssociationAuthorization`
  + AWS Security Hub CSPM
    + `securityhub:AcceptAdministratorInvitation`
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

**Note**  
For additional considerations for the above unsupported actions, see the [Data Perimeter Policy Examples](https://github.com/aws-samples/data-perimeter-policy-examples) repository.

`aws:ResourceOrgPaths` is a multivalued condition key. Multivalued keys can have multiple values in the request context. You must use the `ForAnyValue` or `ForAllValues` set operators with [string condition operators](reference_policies_elements_condition_operators.md#Conditions_String) for this key. For more information about multivalued condition keys, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).

For example, the following condition returns `True` for resources that belong to the organization `o-a1b2c3d4e5`. When you include a wildcard, you must use the [StringLike](reference_policies_elements_condition_operators.md) condition operator.

```
"Condition": { 
      "ForAnyValue:StringLike": {
             "aws:ResourceOrgPaths":["o-a1b2c3d4e5/*"]
   }
}
```

The following condition returns `True` for resources with the OU ID `ou-ab12-11111111`. It will match resources owned by accounts attached to the OU ou-ab12-11111111 or any of the child OUs.

```
"Condition": { "ForAnyValue:StringLike" : {
     "aws:ResourceOrgPaths":["o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/*"]
}}
```

The following condition returns `True` for resources owned by accounts attached directly to the OU ID `ou-ab12-22222222`, but not the child OUs. The following example uses the [StringEquals](reference_policies_elements_condition_operators.md) condition operator to specify the exact match requirement for the OU ID and not a wildcard match.

```
"Condition": { "ForAnyValue:StringEquals" : {
     "aws:ResourceOrgPaths":["o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/"]
}}
```

**Note**  
Some AWS services require access to AWS owned resources that are hosted in another AWS account. Using `aws:ResourceOrgPaths` in your identity-based policies might impact your identity's ability to access these resources.

Certain AWS services, such as AWS Data Exchange, rely on access to resources outside of your AWS accounts for normal operations. If you use the `aws:ResourceOrgPaths` key in your policies, include additional statements to create exemptions for those services. The example policy [AWS: Deny access to Amazon S3 resources outside your account except AWS Data Exchange](reference_policies_examples_resource_account_data_exch.md) demonstrates how to deny access based on the resource account while defining exceptions for service-owned resources. You can create a similar policy to restrict access to resources within an organizational unit (OU) using the `aws:ResourceOrgPaths` key, while accounting for service-owned resources.

Use this policy example as a template for creating your own custom policies. Refer to your service [documentation](https://docs.aws.amazon.com/index.html) for more information.

### aws:ResourceOrgID
<a name="condition-keys-resourceorgid"></a>

Use this key to compare the identifier of the organization in AWS Organizations to which the requested resource belongs with the identifier specified in the policy.
+ **Availability** – This key is included in the request context only if the account that owns the resource is a member of an organization. This global condition key does not support the following actions:
  + AWS Audit Manager
    + `auditmanager:UpdateAssessmentFrameworkShare`
  + Amazon Detective
    + `detective:AcceptInvitation`
  + AWS Directory Service
    + `ds:AcceptSharedDirectory`
  + Amazon Elastic Block Store – All actions
  + Amazon EC2
    + `ec2:AcceptTransitGatewayPeeringAttachment`
    + `ec2:AcceptVpcEndpointConnections`
    + `ec2:AcceptVpcPeeringConnection`
    + `ec2:CreateTransitGatewayPeeringAttachment`
    + `ec2:CreateVpcEndpoint`
    + `ec2:CreateVpcPeeringConnection`
  + Amazon EventBridge
    + `events:PutEvents` – EventBridge `PutEvents` calls on an event bus in another account, if that event bus was configured as a cross-account EventBridge target before March 2, 2023. For more information, see [Grant permissions to allow events from other AWS accounts](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cross-account.html#eb-receiving-events-from-another-account) in the *Amazon EventBridge User Guide*.
  + Amazon GuardDuty
    + `guardduty:AcceptAdministratorInvitation`
  + Amazon Macie
    + `macie2:AcceptInvitation`
  + Amazon OpenSearch Service
    + `es:AcceptInboundConnection`
  + Amazon Route 53
    + `route53:AssociateVpcWithHostedZone`
    + `route53:CreateVPCAssociationAuthorization`
  + AWS Security Hub CSPM
    + `securityhub:AcceptAdministratorInvitation`
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

**Note**  
For additional considerations for the above unsupported actions, see the [Data Perimeter Policy Examples](https://github.com/aws-samples/data-perimeter-policy-examples) repository.

This global key returns the resource organization ID for a given request. It allows you to create rules that apply to all resources in an organization that are specified in the `Resource` element of an [identity-based policy](access_policies_identity-vs-resource.md). You can specify the [organization ID](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_details.html) in the condition element. When you add and remove accounts, policies that include the `aws:ResourceOrgID` key automatically include the correct accounts and you don't have to manually update it.

For example, the following policy prevents the principal from adding objects to the `policy-genius-dev` resource unless the Amazon S3 resource belongs to the same organization as the principal making the request.

**Important**  
This policy does not allow any actions. Instead, it uses the `Deny` effect which explicitly denies access to all of the resources listed in the statement that do not belong to the listed account. Use this policy in combination with other policies that allow access to specific resources.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": {
        "Sid": "DenyPutObjectToS3ResourcesOutsideMyOrganization",
        "Effect": "Deny",
        "Action": "s3:PutObject",
        "Resource": "arn:aws:s3:::policy-genius-dev/*",
        "Condition": {
            "StringNotEquals": {
                "aws:ResourceOrgID": "${aws:PrincipalOrgID}"
            }
        }
    }
}
```

------

**Note**  
Some AWS services require access to AWS owned resources that are hosted in another AWS account. Using `aws:ResourceOrgID` in your identity-based policies might impact your identity's ability to access these resources.

Certain AWS services, such as AWS Data Exchange, rely on access to resources outside of your AWS accounts for normal operations. If you use the `aws:ResourceOrgID` key in your policies, include additional statements to create exemptions for those services. The example policy [AWS: Deny access to Amazon S3 resources outside your account except AWS Data Exchange](reference_policies_examples_resource_account_data_exch.md) demonstrates how to deny access based on the resource account while defining exceptions for service-owned resources. You can create a similar policy to restrict access to resources within your organization using the `aws:ResourceOrgID` key, while accounting for service-owned resources.

Use this policy example as a template for creating your own custom policies. Refer to your service [documentation](https://docs.aws.amazon.com/index.html) for more information.

In the following video, learn more about how you might use the `aws:ResourceOrgID` condition key in a policy.

[![AWS Videos](http://img.youtube.com/vi/cWVW0xAiWwc/0.jpg)](http://www.youtube.com/watch?v=cWVW0xAiWwc)


### aws:ResourceTag/*tag-key*
<a name="condition-keys-resourcetag"></a>

Use this key to compare the tag key-value pair that you specify in the policy with the key-value pair attached to the resource. For example, you could require that access to a resource is allowed only if the resource has the attached tag key `"Dept"` with the value `"Marketing"`. For more information, see [Controlling access to AWS resources](access_tags.md#access_tags_control-resources).
+ **Availability** – This key is included in the request context when the requested resource already has attached tags or in requests that create a resource with an attached tag. This key is returned only for resources that [support authorization based on tags](reference_aws-services-that-work-with-iam.md). There is one context key for each tag key-value pair.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

This context key is formatted `"aws:ResourceTag/{{tag-key}}":"{{tag-value}}"` where {{tag-key}} and {{tag-value}} are a tag key and value pair. Tag keys are not case-sensitive. This means that if you specify `"aws:ResourceTag/TagKey1": "Value1"` in the condition element of your policy, then the condition matches a resource tag key named either `TagKey1` or `tagkey1`, but not both. Values in these tag key/value pairs are case-sensitive. This means that if you specify `"aws:ResourceTag/TagKey1": "Production"` in the condition element of your policy, then the condition matches a resource tag value named `Production` but it would not match `production` or `PRODUCTION`.

For examples of using the `aws:ResourceTag` key to control access to IAM resources, see [Controlling access to AWS resources](access_tags.md#access_tags_control-resources).

For examples of using the `aws:ResourceTag` key to control access to other AWS resources, see [Controlling access to AWS resources using tags](access_tags.md).

For a tutorial on using the `aws:ResourceTag` condition key for attribute based access control (ABAC), see [IAM tutorial: Define permissions to access AWS resources based on tags](tutorial_attribute-based-access-control.md).

## Properties of the request
<a name="condition-keys-request-properties"></a>

Use the following condition keys to compare details about the request itself and the contents of the request with the request properties that you specify in the policy. 

### aws:CalledVia
<a name="condition-keys-calledvia"></a>

Use this key to compare the services in the policy with the services that made requests on behalf of the IAM principal (user or role). When a principal makes a request to an AWS service, that service might use the principal's credentials to make subsequent requests to other services. When the request is made using forward access sessions (FAS), this key is set with the value of the service principal. The `aws:CalledVia` key contains an ordered list of each service in the chain that made requests on the principal's behalf.

For more information, see [Forward access sessions](access_forward_access_sessions.md).
+ **Availability** – This key is present in the request when a service that supports `aws:CalledVia` uses the credentials of an IAM principal to make a request to another service. This key is not present if the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf. This key is also not present when the principal makes the call directly.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

To use the `aws:CalledVia` condition key in a policy, you must provide the service principals to allow or deny AWS service requests. For example, you can use AWS CloudFormation to read and write from an Amazon DynamoDB table. DynamoDB then uses encryption supplied by AWS Key Management Service (AWS KMS).

To allow or deny access when *any* service makes a request using the principal's credentials, use the `aws:ViaAWSService` condition key. That condition key supports AWS services.

The `aws:CalledVia` key is a [multivalued key](reference_policies_condition-single-vs-multi-valued-context-keys.md). However, you can't enforce order using this key in a condition. Using the example above, **User 1** makes a request to CloudFormation, which calls DynamoDB, which calls AWS KMS. These are three separate requests. The final call to AWS KMS is performed by User 1 through CloudFormation and then DynamoDB. 

![Example using aws:CalledVia.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/condition-key-calledvia-example-diagram.png)


In this case, the `aws:CalledVia` key in the request context includes `cloudformation.amazonaws.com` and `dynamodb.amazonaws.com`, in that order. If you care only that the call was made through DynamoDB somewhere in the chain of requests, you can use this condition key in your policy. 

For example, the following policy allows managing the AWS KMS key named `my-example-key`, but only if DynamoDB is one of the requesting services. The `ForAnyValue:StringEquals` condition operator ensures that DynamoDB is one of the calling services. If the principal makes the call to AWS KMS directly, the condition returns `false` and the request is not allowed by this policy.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "KmsActionsIfCalledViaDynamodb",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey",
                "kms:DescribeKey"
            ],
            "Resource": "arn:aws:kms:{{us-east-1}}:{{111122223333}}:key/{{my-example-key}}",
            "Condition": {
                "ForAnyValue:StringEquals": {
                    "aws:CalledVia": [
                        "dynamodb.amazonaws.com"
                    ]
                }
            }
        }
    ]
}
```

------

If you want to enforce which service makes the first or last call in the chain, you can use the `aws:CalledViaFirst` and `aws:CalledViaLast` keys. For example, the following policy allows managing the key named `my-example-key` in AWS KMS. These AWS KMS operations are allowed only if multiple requests were included in the chain. The first request must be made through CloudFormation and the last through DynamoDB. If other services make requests in the middle of the chain, the operation is still allowed.

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "KmsActionsIfCalledViaChain",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey",
                "kms:DescribeKey"
            ],
            "Resource": "arn:aws:kms:{{us-east-1}}:{{111122223333}}:key/{{my-example-key}}",
            "Condition": {
                "StringEquals": {
                    "aws:CalledViaFirst": "cloudformation.amazonaws.com",
                    "aws:CalledViaLast": "dynamodb.amazonaws.com"
                }
            }
        }
    ]
}
```

------

The `aws:CalledViaFirst` and `aws:CalledViaLast` keys are present in the request when a service uses an IAM principal's credentials to call another service. They indicate the first and last services that made calls in the chain of requests. For example, assume that CloudFormation calls another service named `X Service`, which calls DynamoDB, which then calls AWS KMS. The final call to AWS KMS is performed by `User 1` through CloudFormation, then `X Service`, and then DynamoDB. It was first called through CloudFormation and last called through DynamoDB. 

![Example using aws:CalledViaFirst and aws:CalledViaLast.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/condition-key-calledviafirstlast-example-diagram.png)


### aws:CalledViaFirst
<a name="condition-keys-calledviafirst"></a>

Use this key to compare the services in the policy with the ***first service*** that made a request on behalf of the IAM principal (user or role). For more information, see `aws:CalledVia`.
+ **Availability** – This key is present in the request when a service uses the credentials of an IAM principal to make at least one other request to a different service. This key is not present if the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf. This key is also not present when the principal makes the call directly.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

### aws:CalledViaLast
<a name="condition-keys-calledvialast"></a>

Use this key to compare the services in the policy with the *last service* that made a request on behalf of the IAM principal (user or role). For more information, see `aws:CalledVia`.
+ **Availability** – This key is present in the request when a service uses the credentials of an IAM principal to make at least one other request to a different service. This key is not present if the service uses a [service role or service-linked role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html#id_roles_terms-and-concepts) to make a call on the principal's behalf. This key is also not present when the principal makes the call directly.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

### aws:ViaAWSService
<a name="condition-keys-viaawsservice"></a>

Use this key to check whether an AWS service makes a request to another service on your behalf using [forward access sessions (FAS)](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_forward_access_sessions.html).

The request context key returns `true` when a service uses forward access sessions to make a request on behalf of the original IAM principal. The request context key also returns `false` when the principal makes the call directly.
+ **Availability** – This key is always included in the request context.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

### aws:CalledViaAWSMCP
<a name="condition-keys-calledviaawasmcp"></a>

Use this key to compare the services in the policy with the AWS MCP services that made requests on behalf of the IAM principal (user or role). When a principal makes a request to an AWS MCP service, that service uses the principal's credentials to make subsequent requests to other services. When the request is made using an AWS MCP service, this key is set with the value of the service principal. The `aws:CalledViaAWSMCP` key contains the service principal name of the MCP service that made requests on the principal's behalf.
+ **Availability** – This key is present in the request when an AWS MCP service uses the credentials of an IAM principal to make a request to an AWS service. This key is also not present when the principal makes the call directly.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can use this condition key to allow or deny access based on which specific MCP server initiated the request. For example, the following policy denies sensitive delete operations when they are initiated through a specific MCP server:

```
{
    "Version": "2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "DenySensitiveActionsViaSpecificMCP",
            "Effect": "Deny",
            "Action": [
                "s3:DeleteBucket",
                "s3:DeleteObject",
                "dynamodb:DeleteTable"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:CalledViaAWSMCP": "aws-mcp.amazonaws.com"
                }
            }
        }
    ]
}
```

### aws:ViaAWSMCPService
<a name="condition-keys-viaawsmcpservice"></a>

Use this key to check whether an AWS MCP service makes a request to another AWS service on your behalf using forward access sessions (FAS). The request context key returns `true` when an AWS MCP service forwards a request to an AWS service on behalf of the original IAM principal. The request context key also returns `false` when the principal makes the call directly.
+ **Availability** – This key is included in the request context when an AWS MCP server makes a request to a downstream AWS service on behalf of an IAM principal.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

You can use this key to restrict specific actions when they come through MCP servers. For example, the following policy denies sensitive delete operations when initiated through any AWS MCP server:

```
{
    "Version": "2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "DenySensitiveActionsViaMCP",
            "Effect": "Deny",
            "Action": [
                "s3:DeleteBucket",
                "s3:DeleteObject",
                "dynamodb:DeleteTable"
            ],
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "aws:ViaAWSMCPService": "true"
                }
            }
        }
    ]
}
```

### aws:CurrentTime
<a name="condition-keys-currenttime"></a>

Use this key to compare the date and time of the request with the date and time that you specify in the policy. To view an example policy that uses this condition key, see [AWS: Allows access based on date and time](reference_policies_examples_aws-dates.md).
+ **Availability** – This key is always included in the request context.
+ **Data type** – [Date](reference_policies_elements_condition_operators.md#Conditions_Date)
+ **Value type** – Single-valued

### aws:EpochTime
<a name="condition-keys-epochtime"></a>

Use this key to compare the date and time of the request in epoch or Unix time with the value that you specify in the policy. This key also accepts the number of seconds since January 1, 1970. 
+ **Availability** – This key is always included in the request context.
+ **Data type** – [Date](reference_policies_elements_condition_operators.md#Conditions_Date), [Numeric](reference_policies_elements_condition_operators.md#Conditions_Numeric)
+ **Value type** – Single-valued

### aws:referer
<a name="condition-keys-referer"></a>

Use this key to compare who referred the request in the client browser with the referer that you specify in the policy. The `aws:referer` request context value is provided by the caller in an HTTP header. The `Referer` header is included in a web browser request when you select a link on a web page. The `Referer` header contains the URL of the web page where the link was selected.
+ **Availability** – This key is included in the request context only if the request to the AWS resource was invoked by linking from a web page URL in the browser. This key is not included for programmatic requests because it doesn't use a browser link to access the AWS resource.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

For example, you can access an Amazon S3 object directly using a URL or using direct API invocation. For more information, see [Amazon S3 API operations directly using a web browser](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-bucket-policies.html#example-bucket-policies-use-case-4). When you access an Amazon S3 object from a URL that exists in a webpage, the URL of the source web page is in used in `aws:referer`. When you access an Amazon S3 object by typing the URL into your browser, `aws:referer` is not present. When you invoke the API directly, `aws:referer` is also not present. You can use the `aws:referer` condition key in a policy to allow requests made from a specific referer, such as a link on a web page in your company's domain. 

**Warning**  
This key should be used carefully. It is dangerous to include a publicly known referer header value. Unauthorized parties can use modified or custom browsers to provide any `aws:referer` value that they choose. As a result, `aws:referer` should not be used to prevent unauthorized parties from making direct AWS requests. It is offered only to allow customers to protect their digital content, such as content stored in Amazon S3, from being referenced on unauthorized third-party sites.

### aws:RequestedRegion
<a name="condition-keys-requestedregion"></a>

Use this key to compare the AWS Region that was called in the request with the Region that you specify in the policy. You can use this global condition key to control which Regions can be requested. To view the AWS Regions for each service, see [Service endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html) in the *Amazon Web Services General Reference*.
+ **Availability** – This key is always included in the request context.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

Some global services, such as IAM, have a single endpoint. Because this endpoint is physically located in the US East (N. Virginia) Region, IAM calls are always made to the us-east-1 Region. For example, if you create a policy that denies access to all services if the requested Region is not us-west-2, then IAM calls always fail. To view an example of how to work around this, see [NotAction with Deny](reference_policies_elements_notaction.md). 

**Note**  
The `aws:RequestedRegion` condition key allows you to control which endpoint of a service is invoked but does not control the impact of the operation. Some services have cross-Region impacts.  
For example, Amazon S3 has API operations that extend across regions.  
You can invoke `s3:PutBucketReplication` in one Region (which is affected by the `aws:RequestedRegion` condition key), but other Regions are affected based on the replications configuration settings.
You can invoke `s3:CreateBucket` to create a bucket in another region, and use the `s3:LocationConstraint` condition key to control the applicable regions.

You can use this context key to limit access to AWS services within a given set of Regions. For example, the following policy allows a user to view all of the Amazon EC2 instances in the AWS Management Console. However it only allows them to make changes to instances in Ireland (eu-west-1), London (eu-west-2), or Paris (eu-west-3).

------
#### [ JSON ]

****  

```
{
    "Version":"2012-10-17",		 	 	 
    "Statement": [
        {
            "Sid": "InstanceConsoleReadOnly",
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "ec2:Export*",
                "ec2:Get*",
                "ec2:Search*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "InstanceWriteRegionRestricted",
            "Effect": "Allow",
            "Action": [
                "ec2:Associate*",
                "ec2:Import*",
                "ec2:Modify*",
                "ec2:Monitor*",
                "ec2:Reset*",
                "ec2:Run*",
                "ec2:Start*",
                "ec2:Stop*",
                "ec2:Terminate*"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": [
                        "eu-west-1",
                        "eu-west-2",
                        "eu-west-3"
                    ]
                }
            }
        }
    ]
}
```

------

### aws:RequestTag/*tag-key*
<a name="condition-keys-requesttag"></a>

Use this key to compare the tag key-value pair that was passed in the request with the tag pair that you specify in the policy. For example, you could check whether the request includes the tag key `"Dept"` and that it has the value `"Accounting"`. For more information, see [Controlling access during AWS requests](access_tags.md#access_tags_control-requests).
+ **Availability** – This key is included in the request context when tag key-value pairs are passed in the request. When multiple tags are passed in the request, there is one context key for each tag key-value pair.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

This context key is formatted `"aws:RequestTag/{{tag-key}}":"{{tag-value}}"` where {{tag-key}} and {{tag-value}} are a tag key and value pair. Tag keys are not case-sensitive. This means that if you specify `"aws:RequestTag/TagKey1": "Value1"` in the condition element of your policy, then the condition matches a request tag key named either `TagKey1` or `tagkey1`, but not both. Values in these tag key/value pairs are case-sensitive. This means that if you specify `"aws:RequestTag/TagKey1": "Production"` in the condition element of your policy, then the condition matches a request tag value named `Production` but it would not match `production` or `PRODUCTION`.

This example shows that while the key is single-valued, you can still use multiple key-value pairs in a request if the keys are different.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": {
    "Effect": "Allow",
    "Action": "ec2:CreateTags",
    "Resource": "arn:aws:ec2::{{111122223333}}:instance/*",
    "Condition": {
      "StringEquals": {
        "aws:RequestTag/environment": [
          "preprod",
          "production"
        ],
        "aws:RequestTag/team": [
          "engineering"
        ]
      }
    }
  }
}
```

------

### aws:TagKeys
<a name="condition-keys-tagkeys"></a>

Use this key to compare the tag keys in a request with the keys that you specify in the policy. We recommend that when you use policies to control access using tags, use the `aws:TagKeys` condition key to define what tag keys are allowed. For example policies and more information, see [Controlling access based on tag keys](access_tags.md#access_tags_control-tag-keys).
+ **Availability** – This key is included in the request context if the operation supports passing tags in the request.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

This context key is formatted `"aws:TagKeys":"{{tag-key}}"` where {{tag-key}} is a list of tag keys without values (for example, `["Dept","Cost-Center"]`).

Because you can include multiple tag key-value pairs in a request, the request content could be a [multivalued](reference_policies_condition-single-vs-multi-valued-context-keys.md) request. In this case, you must use the `ForAllValues` or `ForAnyValue` set operators. For more information, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).

Some services support tagging with resource operations, such as creating, modifying, or deleting a resource. To allow tagging and operations as a single call, you must create a policy that includes both the tagging action and the resource-modifying action. You can then use the `aws:TagKeys` condition key to enforce using specific tag keys in the request. For example, to limit tags when someone creates an Amazon EC2 snapshot, you must include the `ec2:CreateSnapshot` creation action ***and*** the `ec2:CreateTags` tagging action in the policy. To view a policy for this scenario that uses `aws:TagKeys`, see [Creating a Snapshot with Tags](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ExamplePolicies_EC2.html#iam-creating-snapshot-with-tags) in the *Amazon EC2 User Guide*. 

### aws:SecureTransport
<a name="condition-keys-securetransport"></a>

Use this key to check whether the request was sent using TLS. The request context returns `true` or `false`. In a policy, you can allow specific actions only if the request is sent using TLS.
+ **Availability** – This key is always included in the request context.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

### aws:SourceAccount
<a name="condition-keys-sourceaccount"></a>

Use this key to compare the account ID of the resource making a service-to-service request with the account ID that you specify in the policy, but only when the request is made by an AWS service principal.
+ **Availability** – This key is included in the request context only when the call to your resource is being made directly by an [AWS service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-services) on behalf of a resource for which the configuration triggered the service-to-service request. The calling service passes the account ID of the original resource to the called service.
**Note**  
This key provides a uniform mechanism for enforcing cross-service confused deputy control across AWS services. However, not all service integrations require the use of this global condition key. See the documentation of the AWS services you use for more information about service-specific mechanisms for mitigating cross-service confused deputy risks.  
![aws:SourceAccount.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/sourceAccount.png)
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can use this condition key to help make sure that a calling service can access your resource only when the request originates from a specific account. For example, you can attach the following resource control policy (RCP) to deny requests by service principals against Amazon S3 buckets, unless they were triggered by a resource in the specified account. This policy applies the control only on requests by service principals (`"Bool": {"aws:PrincipalIsAWSService": "true"}`) that have the `aws:SourceAccount` key present (`"Null": {"aws:SourceAccount": "false"}`), so that service integrations that don't require the use of this key and calls by your principals aren't impacted. If the `aws:SourceAccount` key is present in the request context, the `Null` condition will evaluate to `true`, causing the `aws:SourceAccount` key to be enforced.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "RCPEnforceConfusedDeputyProtection",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:SourceAccount": "111122223333"
        },
        "Null": {
          "aws:SourceAccount": "false"
        },
        "Bool": {
          "aws:PrincipalIsAWSService": "true"
        }
      }
    }
  ]
}
```

------

In resource-based policies where the principal is an AWS service principal, use the key to limit permissions granted to the service. For example, when an Amazon S3 bucket is configured to send notifications to an Amazon SNS topic, the Amazon S3 service invokes the `sns:Publish` API operation for all configured events. In the topic policy that allows the `sns:Publish` operation, set the value of the condition key to the account ID of the Amazon S3 bucket.

### aws:SourceArn
<a name="condition-keys-sourcearn"></a>

Use this key to compare the [Amazon Resource Name (ARN)](reference_identifiers.md#identifiers-arns) of the resource making a service-to-service request with the ARN that you specify in the policy, but only when the request is made by an AWS service principal. When the source's ARN includes the account ID, it is not necessary to use `aws:SourceAccount` with `aws:SourceArn`.

This key does not work with the ARN of the principal making the request. Instead, use `aws:PrincipalArn`.
+ **Availability** – This key is included in the request context only when the call to your resource is being made directly by an [AWS service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-services) on behalf of a resource for which the configuration triggered the service-to-service request. The calling service passes the ARN of the original resource to the called service.
**Note**  
This key provides a uniform mechanism for enforcing cross-service confused deputy control across AWS services. However, not all service integrations require the use of this global condition key. See the documentation of the AWS services you use for more information about service-specific mechanisms for mitigating cross-service confused deputy risks.  
![aws:SourceArn.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/sourceArn.png)
+ **Data type** – ARN

  AWS recommends that you use [ARN operators](reference_policies_elements_condition_operators.md#Conditions_ARN) instead of [string operators](reference_policies_elements_condition_operators.md#Conditions_String) when comparing ARNs.
+ **Value type** – Single-valued

You can use this condition key to help make sure that a calling service can access your resource only when the request originates from a specific resource. When using a resource-based policy with an AWS service principal as the `Principal`, set this condition key's value to the ARN of the resource you want to restrict access to. For example, when an Amazon S3 bucket is configured to send notifications to an Amazon SNS topic, the Amazon S3 service invokes the `sns:Publish` API operation for all configured events. In the topic policy that allows the `sns:Publish` operation, set the value of the condition key to the ARN of the Amazon S3 bucket. For recommendations on when to use this condition key in resource-based policies, see the documentation for the AWS services you are using.

### aws:SourceOrgID
<a name="condition-keys-sourceorgid"></a>

Use this key to compare the [organization ID](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_org_details.html) of the resource making a service-to-service request with the organization ID that you specify in the policy, but only when the request is made by an AWS service principal. When you add and remove accounts to an organization in AWS Organizations, policies that include the `aws:SourceOrgID` key automatically include the correct accounts and you don't have to manually update the policies.
+ **Availability** – This key is included in the request context only when the call to your resource is being made directly by an [AWS service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-services) on behalf of a resource owned by an account which is a member of an organization. The calling service passes the organization ID of the original resource to the called service.
**Note**  
This key provides a uniform mechanism for enforcing cross-service confused deputy control across AWS services. However, not all service integrations require the use of this global condition key. See the documentation of the AWS services you use for more information about service-specific mechanisms for mitigating cross-service confused deputy risks.  
![aws:SourceOrgID.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/sourceOrgID.png)
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

You can use this condition key to help make sure that a calling service can access your resource only when the request originates from a specific organization. For example, you can attach the following resource control policy (RCP) to deny requests by service principals against Amazon S3 buckets, unless they were triggered by a resource in the specified AWS organization. This policy applies the control only on requests by service principals (`"Bool": {"aws:PrincipalIsAWSService": "true"}`) that have the `aws:SourceAccount` key present (`"Null": {"aws:SourceAccount": "false"}`), so that service integrations that don't require the use of the key and calls by your principals aren't impacted. If the `aws:SourceAccount` key is present in the request context, the `Null` condition will evaluate to `true`, causing the `aws:SourceOrgID` key to be enforced. We use `aws:SourceAccount` instead of `aws:SourceOrgID` in the `Null` condition operator so that the control still applies if the request originates from an account that doesn’t belong to an organization.

------
#### [ JSON ]

****  

```
{
  "Version":"2012-10-17",		 	 	 
  "Statement": [
    {
      "Sid": "RCPEnforceConfusedDeputyProtection",
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEqualsIfExists": {
          "aws:SourceOrgID": "o-xxxxxxxxxx"
        },
        "Null": {
          "aws:SourceAccount": "false"
        },
        "Bool": {
          "aws:PrincipalIsAWSService": "true"
        }
      }
    }
  ]
}
```

------

### aws:SourceOrgPaths
<a name="condition-keys-sourceorgpaths"></a>

Use this key to compare the AWS Organizations path of the resource making a service-to-service request with the organizations path that you specify in the policy, but only when the request is made by an AWS service principal. An AWS Organizations path is a text representation of the structure of an AWS Organizations entity. For more information about using and understanding paths, see [Understand the AWS Organizations entity path](access_policies_last-accessed-view-data-orgs.md#access_policies_last-accessed-viewing-orgs-entity-path).
+ **Availability** – This key is included in the request context only when the call to your resource is being made directly by an [AWS service principal](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html#principal-services) on behalf of a resource owned by an account which is a member of an organization. The calling service passes the organization path of the original resource to the called service.
**Note**  
This key provides a uniform mechanism for enforcing cross-service confused deputy control across AWS services. However, not all service integrations require the use of this global condition key. See the documentation of the AWS services you use for more information about service-specific mechanisms for mitigating cross-service confused deputy risks.  
![aws:SourceOrgPaths.](http://docs.aws.amazon.com/IAM/latest/UserGuide/images/sourceOrgPaths.png)
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String) (list)
+ **Value type** – Multivalued

Use this condition key to help make sure that a calling service can access your resource only when the request originates from a specific organizational unit (OU) in AWS Organizations.

Similarly to `aws:SourceOrgID`, to help prevent impact on service integrations that don't require the use of this key, use the `Null` condition operator with the `aws:SourceAccount` condition key so that the control still applies if the request originates from an account that doesn’t belong to an organization.

```
{
      "Condition": {
        "ForAllValues:StringNotLikeIfExists": {
            "aws:SourceOrgPaths": "o-a1b2c3d4e5/r-ab12/ou-ab12-11111111/ou-ab12-22222222/"
        },
        "Null": {
          "aws:SourceAccount": "false"
        },
        "Bool": {
          "aws:PrincipalIsAWSService": "true"
        }
      }
}
```

`aws:SourceOrgPaths` is a multivalued condition key. Multivalued keys can have multiple values in the request context. You must use the `ForAnyValue` or `ForAllValues` set operators with [string condition operators](reference_policies_elements_condition_operators.md#Conditions_String) for this key. For more information about multivalued condition keys, see [Set operators for multivalued context keys](reference_policies_condition-single-vs-multi-valued-context-keys.md#reference_policies_condition-multi-valued-context-keys).

### aws:UserAgent
<a name="condition-keys-useragent"></a>

Use this key to compare the requester's client application with the application that you specify in the policy.
+ **Availability** – This key is always included in the request context.
+ **Data type** – [String](reference_policies_elements_condition_operators.md#Conditions_String)
+ **Value type** – Single-valued

**Warning**  
This key should be used carefully. Since the `aws:UserAgent` value is provided by the caller in an HTTP header, unauthorized parties can use modified or custom browsers to provide any `aws:UserAgent` value that they choose. As a result, `aws:UserAgent` should not be used to prevent unauthorized parties from making direct AWS requests. You can use it to allow only specific client applications, and only after testing your policy.

### aws:IsMcpServiceAction
<a name="condition-keys-ismcpserviceaction"></a>

Use this key to verify that the action being authorized is an MCP Service action. This key does not refer to actions taken by the MCP service to other AWS services.
+ **Availability** – This key is included in the request context and set to True only when the MCP service is authorizing an MCP service action.
+ **Data type** – [Boolean](reference_policies_elements_condition_operators.md#Conditions_Boolean)
+ **Value type** – Single-valued

## Other cross-service condition keys
<a name="condition-keys-other"></a>

AWS STS supports [SAML-based federation condition keys](reference_policies_iam-condition-keys.md#condition-keys-saml) and cross-service condition keys for [OIDC federation](reference_policies_iam-condition-keys.md#condition-keys-wif). These keys are available when a user who was federated using OIDC or SAML performs AWS operations in other services.