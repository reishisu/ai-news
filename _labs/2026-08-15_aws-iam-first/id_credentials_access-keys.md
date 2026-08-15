

# Manage access keys for IAM users
<a name="id_credentials_access-keys"></a>

**Important**  
As a [best practice](best-practices.md), use temporary security credentials (such as IAM roles) instead of creating long-term credentials like access keys. Before creating access keys, review the [alternatives to long-term access keys](security-creds-programmatic-access.md#security-creds-alternatives-to-long-term-access-keys).

Access keys are long-term credentials for an IAM user or the AWS account root user. You can use access keys to sign programmatic requests to the AWS CLI or AWS API (directly or using the AWS SDK). For more information, see [Programmatic access with AWS security credentials](security-creds-programmatic-access.md).

Access keys consist of two parts: an access key ID (for example, `AKIAIOSFODNN7EXAMPLE`) and a secret access key (for example, `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`). You must use both the access key ID and secret access key together to authenticate your requests.



When you create an access key pair, save the access key ID and secret access key in a secure location. The secret access key can be retrieved only at the time you create it. If you lose your secret access key, you must delete the access key and create a new one. For more instructions, see [Update access keys](id-credentials-access-keys-update.md).

You can have a maximum of two access keys per user.

**Important**  
IAM users with access keys are an account security risk. Manage your access keys securely. Do not provide your access keys to unauthorized parties, even to help [find your account identifiers](https://docs.aws.amazon.com/general/latest/gr/acct-identifiers.html). By doing this, you might give someone permanent access to your account.  
When working with access keys, be aware of the following:  
**Do NOT** use your account's root credentials to create access keys.
**Do NOT** put access keys or credential information in your application files. 
**Do NOT** include files that contain access keys or credential information in your project area.
Access keys or credential information stored in the shared AWS credentials file are stored in plaintext.

## Monitoring recommendations
<a name="monitor-access-keys"></a>

After creating access keys:
+ Use AWS CloudTrail to monitor access key usage and detect any unauthorized access attempts. For more information, see [Logging IAM and AWS STS API calls with AWS CloudTrail](cloudtrail-integration.md).
+ Set up CloudWatch alarms to notify administrators for denied access attempts to help detect malicious activities. For more information, see the [Amazon CloudWatch User Guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/).
+ Regularly review, update, and delete access keys as needed.

The following topics detail management tasks associated with access keys.

**Topics**
+ [Monitoring recommendations](#monitor-access-keys)
+ [Control the use of access keys by attaching an inline policy to an IAM user](access-keys_inline-policy.md)
+ [Permissions required to manage access keys](access-keys_required-permissions.md)
+ [How IAM users can manage their own access keys](access-key-self-managed.md)
+ [How an IAM administrator can manage IAM user access keys](access-keys-admin-managed.md)
+ [Update access keys](id-credentials-access-keys-update.md)
+ [Secure access keys](securing_access-keys.md)