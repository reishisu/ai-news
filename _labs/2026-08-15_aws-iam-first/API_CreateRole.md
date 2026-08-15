

# CreateRole
<a name="API_CreateRole"></a>

Creates a new role for your AWS account.

 For more information about roles, see [IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) in the *IAM User Guide*. For information about quotas for role names and the number of roles you can create, see [IAM and AWS STS quotas](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_iam-quotas.html) in the *IAM User Guide*.

## Request Parameters
<a name="API_CreateRole_RequestParameters"></a>

 For information about the parameters that are common to all actions, see [Common Parameters](CommonParameters.md).

 ** AssumeRolePolicyDocument **   
The trust relationship policy document that grants an entity permission to assume the role.  
In IAM, you must provide a JSON policy that has been converted to a string. However, for CloudFormation templates formatted in YAML, you can provide the policy in JSON or YAML format. CloudFormation always converts a YAML policy to JSON format before submitting it to IAM.  
The [regex pattern](http://wikipedia.org/wiki/regex) used to validate this parameter is a string of characters consisting of the following:  
+ Any printable ASCII character ranging from the space character (`\u0020`) through the end of the ASCII character range
+ The printable characters in the Basic Latin and Latin-1 Supplement character set (through `\u00FF`)
+ The special characters tab (`\u0009`), line feed (`\u000A`), and carriage return (`\u000D`)
 Upon success, the response includes the same trust policy in JSON format.  
Type: String  
Length Constraints: Minimum length of 1. Maximum length of 131072.  
Pattern: `[\u0009\u000A\u000D\u0020-\u00FF]+`   
Required: Yes

 ** Description **   
A description of the role.  
Type: String  
Length Constraints: Maximum length of 1000.  
Pattern: `[\u0009\u000A\u000D\u0020-\u007E\u00A1-\u00FF]*`   
Required: No

 ** MaxSessionDuration **   
The maximum session duration (in seconds) that you want to set for the specified role. If you do not specify a value for this setting, the default value of one hour is applied. This setting can have a value from 1 hour to 12 hours.  
Anyone who assumes the role from the AWS CLI or API can use the `DurationSeconds` API parameter or the `duration-seconds` AWS CLI parameter to request a longer session. The `MaxSessionDuration` setting determines the maximum duration that can be requested using the `DurationSeconds` parameter. If users don't specify a value for the `DurationSeconds` parameter, their security credentials are valid for one hour by default. This applies when you use the `AssumeRole*` API operations or the `assume-role*` AWS CLI operations but does not apply when you use those operations to create a console URL. For more information, see [Using IAM roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use.html) in the *IAM User Guide*.  
Type: Integer  
Valid Range: Minimum value of 3600. Maximum value of 43200.  
Required: No

 ** Path **   
 The path to the role. For more information about paths, see [IAM Identifiers](https://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html) in the *IAM User Guide*.  
This parameter is optional. If it is not included, it defaults to a slash (/).  
This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of either a forward slash (/) by itself or a string that must begin and end with forward slashes. In addition, it can contain any ASCII character from the \! (`\u0021`) through the DEL character (`\u007F`), including most punctuation characters, digits, and upper and lowercased letters.  
Type: String  
Length Constraints: Minimum length of 1. Maximum length of 512.  
Pattern: `(\u002F)|(\u002F[\u0021-\u007E]+\u002F)`   
Required: No

 ** PermissionsBoundary **   
The ARN of the managed policy that is used to set the permissions boundary for the role.  
A permissions boundary policy defines the maximum permissions that identity-based policies can grant to an entity, but does not grant permissions. Permissions boundaries do not define the maximum permissions that a resource-based policy can grant to an entity. To learn more, see [Permissions boundaries for IAM entities](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html) in the *IAM User Guide*.  
For more information about policy types, see [Policy types ](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#access_policy-types) in the *IAM User Guide*.  
Type: String  
Length Constraints: Minimum length of 20. Maximum length of 2048.  
Required: No

 ** RoleName **   
The name of the role to create.  
IAM user, group, role, and policy names must be unique within the account. Names are not distinguished by case. For example, you cannot create resources named both "MyResource" and "myresource".  
This parameter allows (through its [regex pattern](http://wikipedia.org/wiki/regex)) a string of characters consisting of upper and lowercase alphanumeric characters with no spaces. You can also include any of the following characters: \_\+=,.@-  
Type: String  
Length Constraints: Minimum length of 1. Maximum length of 64.  
Pattern: `[\w+=,.@-]+`   
Required: Yes

 **Tags.member.N**   
A list of tags that you want to attach to the new role. Each tag consists of a key name and an associated value. For more information about tagging, see [Tagging IAM resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_tags.html) in the *IAM User Guide*.  
If any one of the tags is invalid or if you exceed the allowed maximum number of tags, then the entire request fails and the resource is not created.
Type: Array of [Tag](API_Tag.md) objects  
Array Members: Maximum number of 50 items.  
Required: No

## Response Elements
<a name="API_CreateRole_ResponseElements"></a>

The following element is returned by the service.

 ** Role **   
A structure containing details about the new role.  
Type: [Role](API_Role.md) object

## Errors
<a name="API_CreateRole_Errors"></a>

For information about the errors that are common to all actions, see [Common Error Types](CommonErrors.md).

 ** ConcurrentModification **   
The request was rejected because multiple requests to change this object were submitted simultaneously. Wait a few minutes and submit your request again.  
HTTP Status Code: 409

 ** EntityAlreadyExists **   
The request was rejected because it attempted to create a resource that already exists.  
HTTP Status Code: 409

 ** InvalidInput **   
The request was rejected because an invalid or out-of-range value was supplied for an input parameter.  
HTTP Status Code: 400

 ** LimitExceeded **   
The request was rejected because it attempted to create resources beyond the current AWS account limits. The error message describes the limit exceeded.  
HTTP Status Code: 409

 ** MalformedPolicyDocument **   
The request was rejected because the policy document was malformed. The error message describes the specific error.  
HTTP Status Code: 400

 ** ServiceFailure **   
The request processing has failed because of an unknown error, exception or failure.  
HTTP Status Code: 500

## Examples
<a name="API_CreateRole_Examples"></a>

### Example
<a name="API_CreateRole_Example_1"></a>

This example illustrates one usage of CreateRole.

#### Sample Request
<a name="API_CreateRole_Example_1_Request"></a>

```
https://iam.amazonaws.com/?Action=CreateRole
&RoleName=S3Access
&Path=/application_abc/component_xyz/
&AssumeRolePolicyDocument={"Version":"2012-10-17",		 	 	 "Statement":[{"Effect":"Allow","Principal":{"Service":["ec2.amazonaws.com"]},"Action":["sts:AssumeRole"]}]}
&Version=2010-05-08
&AUTHPARAMS
```

#### Sample Response
<a name="API_CreateRole_Example_1_Response"></a>

```
<CreateRoleResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <CreateRoleResult>
    <Role>
      <Path>/application_abc/component_xyz/</Path>
      <Arn>arn:aws:iam::123456789012:role/application_abc/component_xyz/S3Access</Arn>
      <RoleName>S3Access</RoleName>
      <AssumeRolePolicyDocument>
        {"Version":"2012-10-17",		 	 	 "Statement":[{"Effect":"Allow",
        "Principal":{"Service":["ec2.amazonaws.com"]},"Action":["sts:AssumeRole"]}]}
      </AssumeRolePolicyDocument>
      <CreateDate>2012-05-08T23:34:01.495Z</CreateDate>
      <RoleId>AROADBQP57FF2AEXAMPLE</RoleId>
    </Role>
  </CreateRoleResult>
  <ResponseMetadata>
    <RequestId>4a93ceee-9966-11e1-b624-b1aEXAMPLE7c</RequestId>
  </ResponseMetadata>
</CreateRoleResponse>
```

## See Also
<a name="API_CreateRole_SeeAlso"></a>

For more information about using this API in one of the language-specific AWS SDKs, see the following:
+  [AWS Command Line Interface V2](https://docs.aws.amazon.com/goto/cli2/iam-2010-05-08/CreateRole) 
+  [AWS SDK for .NET V4](https://docs.aws.amazon.com/goto/DotNetSDKV4/iam-2010-05-08/CreateRole) 
+  [AWS SDK for C\+\+](https://docs.aws.amazon.com/goto/SdkForCpp/iam-2010-05-08/CreateRole) 
+  [AWS SDK for Go v2](https://docs.aws.amazon.com/goto/SdkForGoV2/iam-2010-05-08/CreateRole) 
+  [AWS SDK for Java V2](https://docs.aws.amazon.com/goto/SdkForJavaV2/iam-2010-05-08/CreateRole) 
+  [AWS SDK for JavaScript V3](https://docs.aws.amazon.com/goto/SdkForJavaScriptV3/iam-2010-05-08/CreateRole) 
+  [AWS SDK for Kotlin](https://docs.aws.amazon.com/goto/SdkForKotlin/iam-2010-05-08/CreateRole) 
+  [AWS SDK for PHP V3](https://docs.aws.amazon.com/goto/SdkForPHPV3/iam-2010-05-08/CreateRole) 
+  [AWS SDK for Python](https://docs.aws.amazon.com/goto/boto3/iam-2010-05-08/CreateRole) 
+  [AWS SDK for Ruby V3](https://docs.aws.amazon.com/goto/SdkForRubyV3/iam-2010-05-08/CreateRole) 