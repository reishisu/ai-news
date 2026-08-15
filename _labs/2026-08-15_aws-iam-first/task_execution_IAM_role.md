

# Amazon ECS task execution IAM role
<a name="task_execution_IAM_role"></a>

The task execution role grants the Amazon ECS container and Fargate agents permission to make AWS API calls on your behalf. The task execution IAM role is required depending on the requirements of your task. You can have multiple task execution roles for different purposes and services associated with your account.

**Note**  
These permissions are made available to the agent running on your instance by Amazon ECS periodically sending it the role's temporary credentials, but they aren't directly accessible by the containers in the task. For the IAM permissions that your application code inside the container needs to run, see [Amazon ECS task IAM role](task-iam-roles.md). 

The following are common use cases for a task execution IAM role:
+ Your task is hosted on AWS Fargate, Amazon ECS Managed Instances, or an external instance and:
  + pulls a container image from an Amazon ECR private repository.
  + pulls a container image from an Amazon ECR private repository in a different account from the account that runs the task.
  + sends container logs to CloudWatch Logs using the `awslogs` log driver. For more information, see [Send Amazon ECS logs to CloudWatch](using_awslogs.md).
+ Your tasks are hosted on either AWS Fargate or Amazon EC2 instances and:
  + uses private registry authentication. For more information, see [Private registry authentication permissions](#task-execution-private-auth).
  + uses Runtime Monitoring.
  + the task definition references sensitive data using Secrets Manager secrets or AWS Systems Manager Parameter Store parameters. For more information, see [Secrets Manager or Systems Manager permissions](#task-execution-secrets).

**Note**  
The task execution role is supported by Amazon ECS container agent version 1.16.0 and later.

Amazon ECS provides the managed policy named `AmazonECSTaskExecutionRolePolicy` which contains the permissions the common use cases previously described require. For more information, see [AmazonECSTaskExecutionRolePolicy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonECSTaskExecutionRolePolicy.html) in the *AWS Managed Policy Reference Guide*. It might be necessary to add inline policies to your task execution role for special use cases

The Amazon ECS console creates a task execution role. You can manually attach the managed IAM policy for tasks to allow Amazon ECS to add permissions for future features and enhancements as they are introduced. You can use IAM console search to search for `ecsTaskExecutionRole` and see if your account already has the task execution role. For more information, see [IAM console search](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_search.html) in the *IAM user guide*.

If you pull images as an authenticated user, you're less likely to be impacted by the changes that occurred to [Docker Hub usage and limits](https://docs.docker.com/docker-hub/usage/). For more information see, [Private registry authentication for container instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/private-auth-container-instances.html).

By using Amazon ECR and Amazon ECR Public, you can avoid the limits imposed by Docker. If you pull images from Amazon ECR, this also helps shorten network pull times and reduces data transfer changes when traffic leaves your VPC.

When you use Fargate, you must authenticate to a private image registry using `repositoryCredentials`. It's not possible to set the Amazon ECS container agent environment variables `ECS_ENGINE_AUTH_TYPE` or `ECS_ENGINE_AUTH_DATA` or modify the `ecs.config` file for tasks hosted on Fargate. For more information, see [Private registry authentication for tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/private-auth.html).

## Creating the task execution role
<a name="create-task-execution-role"></a>

If your account doesn't already have a task execution role, use the following steps to create the role.

------
#### [ AWS Management Console ]

**To create the service role for Elastic Container Service (IAM console)**

1. Sign in to the AWS Management Console and open the IAM console at [https://console.aws.amazon.com/iam/](https://console.aws.amazon.com/iam/).

1. In the navigation pane of the IAM console, choose **Roles**, and then choose **Create role**.

1. For **Trusted entity type**, choose **AWS service**.

1. For **Service or use case**, choose **Elastic Container Service**, and then choose the **Elastic Container Service Task** use case.

1. Choose **Next**.

1. In the **Add permissions** section, search for **AmazonECSTaskExecutionRolePolicy**, then select the policy.

1. Choose **Next**.

1.  For **Role name**, enter **ecsTaskExecutionRole**.

1. Review the role, and then choose **Create role**.

------
#### [ AWS CLI ]

Replace all {{user input}} with your own information.

1. Create a file named `ecs-tasks-trust-policy.json` that contains the trust policy to use for the IAM role. The file should contain the following:

------
#### [ JSON ]

****  

   ```
   {
     "Version":"2012-10-17",		 	 	 
     "Statement": [
       {
         "Sid": "",
         "Effect": "Allow",
         "Principal": {
           "Service": "ecs-tasks.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

------

1. Create an IAM role named `ecsTaskExecutionRole` using the trust policy created in the previous step.

   ```
   aws iam create-role \
         --role-name {{ecsTaskExecutionRole}} \
         --assume-role-policy-document file://{{ecs-tasks-trust-policy.json}}
   ```

1. Attach the AWS managed `AmazonECSTaskExecutionRolePolicy` policy to the `ecsTaskExecutionRole` role.

   ```
   aws iam attach-role-policy \
         --role-name {{ecsTaskExecutionRole}} \
         --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
   ```

------

After you create the role, add additional permissions to the role for the following features.


|  Feature  |  Additional permissions  | 
| --- | --- | 
| Pull container images from private registries outside of AWS (such as Docker Hub, Quay.io, or your own private registry) using Secrets Manager credentials | [Private registry authentication permissions](#task-execution-private-auth) | 
| Pass sensitive data with Systems Manager or Secrets Manager | [Secrets Manager or Systems Manager permissions](#task-execution-secrets) | 
| Have Fargate tasks pull Amazon ECR images over interface endpoints | [Fargate tasks pulling Amazon ECR images over interface endpoints permissions](#task-execution-ecr-conditionkeys) | 
| Host configuration files in an Amazon S3 bucket | [Amazon S3 file storage permissions](#s3-required) | 
| Configure Container Insights to view Amazon ECS lifecycle events | [Permissions required for enabling Amazon ECS lifecycle events in Container Insights](console-permissions.md#required-permissions-configure) | 
| View Amazon ECS lifecycle events in Container Insights | [Permissions required to view Amazon ECS lifecycle events in Container Insights](console-permissions.md#required-permissions-view) | 

## Private registry authentication permissions
<a name="task-execution-private-auth"></a>

Private registry authentication allows your Amazon ECS tasks to pull container images from private registries outside of AWS (such as Docker Hub, Quay.io, or your own private registry) that require authentication credentials. This feature uses Secrets Manager to securely store your registry credentials, which are then referenced in your task definition using the `repositoryCredentials` parameter.

For more information about configuring private registry authentication, see [Using non-AWS container images in Amazon ECS](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/private-auth.html).

To provide access to the secrets that contain your private registry credentials, add the following permissions as an inline policy to the task execution role. For more information, see [Adding and Removing IAM Policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html).
+ `secretsmanager:GetSecretValue`—Required to retrieve the private registry credentials from Secrets Manager.
+ `kms:Decrypt`—Required only if your secret uses a custom KMS key and not the default key. The Amazon Resource Name (ARN) for your custom key must be added as a resource.

The following is an example inline policy that adds the permissions.

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
                "kms:Decrypt",
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-east-1:{{111122223333}}:secret:secret_name",
                "arn:aws:kms:us-east-1:{{111122223333}}:key/key_id"
            ]
        }
    ]
}
```

------

## Secrets Manager or Systems Manager permissions
<a name="task-execution-secrets"></a>

The permission to allow the container agent to pull the necessary AWS Systems Manager or Secrets Manager resources. For more information, see [Pass sensitive data to an Amazon ECS container](specifying-sensitive-data.md).

**Using Secrets Manager **

To provide access to the Secrets Manager secrets that you create, manually add the following permission to the task execution role. For information about how to manage permissions, see [Adding and Removing IAM identity permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html) in the *IAM User Guide*.
+ `secretsmanager:GetSecretValue`– Required if you are referencing a Secrets Manager secret. Adds the permission to retrieve the secret from Secrets Manager.

The following example policy adds the required permissions.

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
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:{{us-east-1}}:{{111122223333}}:secret:{{secret_name}}"
      ]
    }
  ]
}
```

------

**Using Systems Manager**

**Important**  
For tasks that use the EC2 launch type, you must use the ECS agent configuration variable `ECS_ENABLE_AWSLOGS_EXECUTIONROLE_OVERRIDE=true` to use this feature. You can add it to the `./etc/ecs/ecs.config` file during container instance creation or you can add it to an existing instance and then restart the ECS agent. For more information, see [Amazon ECS container agent configuration](ecs-agent-config.md).

To provide access to the Systems Manager Parameter Store parameters that you create, manually add the following permissions as a policy to the task execution role. For information about how to manage permissions, see [Adding and Removing IAM identity permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html) in the *IAM User Guide*.
+ `ssm:GetParameters` — Required if you are referencing a Systems Manager Parameter Store parameter in a task definition. Adds the permission to retrieve Systems Manager parameters.
+ `secretsmanager:GetSecretValue` — Required if you are referencing a Secrets Manager secret either directly or if your Systems Manager Parameter Store parameter is referencing a Secrets Manager secret in a task definition. Adds the permission to retrieve the secret from Secrets Manager.
+ `kms:Decrypt` — Required only if your secret uses a customer managed key and not the default key. The ARN for your custom key should be added as a resource. Adds the permission to decrypt the customer managed key .

The following example policy adds the required permissions:

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
        "ssm:GetParameters",
        "secretsmanager:GetSecretValue",
        "kms:Decrypt"
      ],
      "Resource": [
        "arn:aws:ssm:{{us-east-1}}:{{111122223333}}:parameter/{{parameter_name}}",
        "arn:aws:secretsmanager:{{us-east-1}}:{{111122223333}}:secret:{{secret_name}}",
        "arn:aws:kms:{{us-east-1}}:{{111122223333}}:key/{{key_id}}"
      ]
    }
  ]
}
```

------

## Fargate tasks pulling Amazon ECR images over interface endpoints permissions
<a name="task-execution-ecr-conditionkeys"></a>

When launching tasks that use Fargate that pull images from Amazon ECR when Amazon ECR is configured to use an interface VPC endpoint, you can restrict the tasks access to a specific VPC or VPC endpoint. Do this by creating a task execution role for the tasks to use that use IAM condition keys.

Use the following IAM global condition keys to restrict access to a specific VPC or VPC endpoint. For more information, see [AWS Global Condition Context Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_condition-keys.html).
+ `aws:SourceVpc`—Restricts access to a specific VPC. You can restrict the VPC to the VPC that hosts the task and endpoint.
+ `aws:SourceVpce`—Restricts access to a specific VPC endpoint.

The following task execution role policy provides an example for adding condition keys:

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
                    "ecr:GetAuthorizationToken",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ],
                "Resource": "arn:aws:ecr:*:*:repository/*",
                "Condition": {
                    "StringEquals": {
                            "aws:sourceVpce": "vpce-0123456789abcdef0"
                    }
                }
            }
    ]
}
```

------

## Amazon ECR permissions
<a name="task-execution-ecr-permissions"></a>

The following permissions are required when you need to pull container images from Amazon ECR private repositories. The task execution role should have these permissions to allow the Amazon ECS container and Fargate agents to pull container images on your behalf. For basic ECS implementations, these permissions should be added to the task execution role rather than the task IAM role.

The Amazon ECS task execution role managed policy (`AmazonECSTaskExecutionRolePolicy`) includes the necessary permissions for pulling images from Amazon ECR. If you're using the managed policy, you don't need to add these permissions separately.

If you're creating a custom policy, include the following permissions to allow pulling images from Amazon ECR:

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
                "ecr:BatchGetImage",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        }
    ]
}
```

------

Note that these permissions are different from the permissions that might be required in the task IAM role if your application code needs to interact with Amazon ECR APIs directly. For information about task IAM role permissions for Amazon ECR, see [Amazon ECR permissions](task-iam-roles.md#ecr-required-iam-permissions).

## Amazon S3 file storage permissions
<a name="s3-required"></a>

When you specify a configuration file that's hosted in Amazon S3, the task execution role must include the `s3:GetObject` permission for the configuration file and the `s3:GetBucketLocation` permission on the Amazon S3 bucket that the file is in. For more information, see [Policy actions for Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security_iam_service-with-iam.html#security_iam_service-with-iam-id-based-policies-actions) in the *Amazon Simple Storage Service User Guide*.

The following example policy adds the required permissions for retrieving a file from Amazon S3. Specify the name of your Amazon S3 bucket and configuration file name.

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
        "{{s3:GetObject}}"
      ],
      "Resource": [
        "arn:aws:s3:::{{amzn-s3-demo-bucket}}/{{folder_name}}/{{config_file_name}}"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::{{amzn-s3-demo-bucket}}"
      ]
    }
  ]
}
```

------

### Important Security Consideration
<a name="s3-required-considerations"></a>

 When using Amazon ECS features that integrate with Amazon S3 buckets, implement bucket ownership validation to prevent bucket takeover attacks. Without proper validation, if an Amazon S3 bucket is deleted and recreated by a malicious actor with the same name, your tasks may unknowingly load malicious configurations or send sensitive data to attacker-controlled buckets. 

**Recommended IAM Policy Condition:**

```
               "Condition": {
                 "StringEquals": {
                   "aws:ResourceAccount": "{{TRUSTED-ACCOUNT-ID}}"
                 }
               }
```

Replace {{TRUSTED-ACCOUNT-ID}} with the AWS account ID that owns the S3 bucket.

This condition ensures your task execution role can only access Amazon S3 buckets owned by the specified trusted account.