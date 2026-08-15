

# AmazonECSTaskExecutionRolePolicy
<a name="AmazonECSTaskExecutionRolePolicy"></a>

**Description**: Provides access to other AWS service resources that are required to run Amazon ECS tasks

`AmazonECSTaskExecutionRolePolicy` is an [AWS managed policy](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html#aws-managed-policies).

## Using this policy
<a name="AmazonECSTaskExecutionRolePolicy-how-to-use"></a>

You can attach `AmazonECSTaskExecutionRolePolicy` to your users, groups, and roles.

## Policy details
<a name="AmazonECSTaskExecutionRolePolicy-details"></a>
+ **Type**: Service role policy 
+ **Creation time**: November 16, 2017, 18:48 UTC 
+ **Edited time:** November 16, 2017, 18:48 UTC
+ **ARN**: `arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy`

## Policy version
<a name="AmazonECSTaskExecutionRolePolicy-version"></a>

**Policy version:** v1 (default)

The policy's default version is the version that defines the permissions for the policy. When a user or role with the policy makes a request to access an AWS resource, AWS checks the default version of the policy to determine whether to allow the request. 

## JSON policy document
<a name="AmazonECSTaskExecutionRolePolicy-json"></a>

```
{
  "Version" : "2012-10-17",
  "Statement" : [
    {
      "Effect" : "Allow",
      "Action" : [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource" : "*"
    }
  ]
}
```

## Learn more
<a name="AmazonECSTaskExecutionRolePolicy-learn-more"></a>
+ [Create a permission set using AWS managed policies in IAM Identity Center](https://docs.aws.amazon.com/singlesignon/latest/userguide/howtocreatepermissionset.html) 
+ [Adding and removing IAM identity permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html) 
+ [Understand versioning for IAM policies](https://docs.aws.amazon.com//IAM/latest/UserGuide/access_policies_managed-versioning.html)
+ [Get started with AWS managed policies and move toward least-privilege permissions](https://docs.aws.amazon.com//IAM/latest/UserGuide/best-practices.html#bp-use-aws-defined-policies)