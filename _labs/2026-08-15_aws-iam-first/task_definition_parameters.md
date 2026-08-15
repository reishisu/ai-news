

# Amazon ECS task definition parameters for Fargate
<a name="task_definition_parameters"></a>

Task definitions are split into separate parts: the task family, the AWS Identity and Access Management (IAM) task role, the network mode, container definitions, volumes, and launch types. The family and container definitions are required in a task definition. In contrast, task role, network mode, volumes, and launch type are optional.

You can use these parameters in a JSON file to configure your task definition.

The following are more detailed descriptions for each task definition parameter for Fargate.

## Family
<a name="family"></a>

`family`  
Type: String  
Required: Yes  
When you register a task definition, you give it a family, which is similar to a name for multiple versions of the task definition, specified with a revision number. The first task definition that's registered into a particular family is given a revision of 1, and any task definitions registered after that are given a sequential revision number.

## Capacity
<a name="requires_compatibilities"></a>

When you register a task definition, you can specify the capacity that Amazon ECS should validate the task definition against. If the task definition doesn't validate against the compatibilities specified, a client exception is returned. 

The following parameter is allowed in a task definition.

`requiresCompatibilities`  
Type: String array  
Required: No  
Valid Values: `FARGATE`  
The capacity to validate the task definition against. This initiates a check to ensure that all of the parameters that are used in the task definition meet the requirements of Fargate

## Task role
<a name="task_role_arn"></a>

`taskRoleArn`  
Type: String  
Required: No  
When you register a task definition, you can provide a task role for an IAM role that allows the containers in the task permission to call the AWS APIs that are specified in its associated policies on your behalf. For more information, see [Amazon ECS task IAM role](task-iam-roles.md).

## Task execution role
<a name="execution_role_arn"></a>

`executionRoleArn`  
Type: String  
Required: Conditional  
The Amazon Resource Name (ARN) of the task execution role that grants the Amazon ECS container agent permission to make AWS API calls on your behalf.   
The task execution IAM role is required depending on the requirements of your task. For more information, see [Amazon ECS task execution IAM role](task_execution_IAM_role.md).

## Network mode
<a name="network_mode"></a>

`networkMode`  
Type: String  
Required: Yes  
The Docker networking mode to use for the containers in the task. For Amazon ECS tasks hosted on Fargate, the `awsvpc` network mode is required.

## Runtime platform
<a name="runtime-platform"></a>

`operatingSystemFamily`  
Type: String  
Required: Conditional  
Default: LINUX  
This parameter is required for Amazon ECS tasks that are hosted on Fargate.  
When you register a task definition, you specify the operating system family.   
The valid values are `LINUX`, `WINDOWS_SERVER_2025_FULL`, `WINDOWS_SERVER_2025_CORE`, `WINDOWS_SERVER_2022_FULL`, `WINDOWS_SERVER_2022_CORE`, `WINDOWS_SERVER_2019_FULL`, and `WINDOWS_SERVER_2019_CORE`.  
All task definitions that are used in a service must have the same value for this parameter.  
When a task definition is part of a service, this value must match the service `platformFamily` value.

`cpuArchitecture`  
Type: String  
Required: Conditional  
Default: X86\_64  
If the parameter is left as `null`, the default value is automatically assigned upon the initiation of a task hosted on Fargate.  
When you register a task definition, you specify the CPU architecture. The valid values are `X86_64` and `ARM64`.  
All task definitions that are used in a service must have the same value for this parameter.  
When you have Linux tasks, you can set the value to `ARM64`. For more information, see [Amazon ECS task definitions for 64-bit ARM workloads](ecs-arm64.md).

## Task size
<a name="task_size"></a>

When you register a task definition, you can specify the total CPU and memory used for the task. This is separate from the `cpu` and `memory` values at the container definition level. For tasks that are hosted on Fargate (both Linux and Windows), these fields are required and there are specific values for both `cpu` and `memory` that are supported.

The following parameter is allowed in a task definition:

`cpu`  
Type: String  
Required: Yes  
Task-level CPU and memory parameters are required and used to determine the instance type and size that tasks run on. For Windows tasks, these values aren’t enforced at runtime, because Windows doesn't have a native mechanism that can easily enforce collective resource limits on a group of containers. If you want to enforce resource limits, we recommend using the container-level resources for Windows containers.
The hard limit of CPU units to present for the task. You can specify CPU values in the JSON file as a string in CPU units or virtual CPUs (vCPUs). For example, you can specify a CPU value either as `1024` in CPU units or `1 vCPU` in vCPUs. When the task definition is registered, a vCPU value is converted to an integer indicating the CPU units.  
This field is required and you must use one of the following values, which determines your range of supported values for the `memory` parameter. The following table shows the valid combinations of task-level CPU and memory.      
[See the AWS documentation website for more details](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html)

`memory`  
Type: String  
Required: Yes  
Task-level CPU and memory parameters are required and used to determine the instance type and size that tasks run on. For Windows tasks, these values aren’t enforced at runtime, because Windows doesn't have a native mechanism that can easily enforce collective resource limits on a group of containers. If you want to enforce resource limits, we recommend using the container-level resources for Windows containers.
The hard limit of memory to present to the task. You can specify memory values in the task definition as a string in mebibytes (MiB) or gigabytes (GB). For example, you can specify a memory value either as `3072` in MiB or `3 GB`in GB. When the task definition is registered, a GB value is converted to an integer indicating the MiB.  
This field is required and you must use one of the following values, which determines your range of supported values for the `cpu` parameter:      
[See the AWS documentation website for more details](http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html)

## Container definitions
<a name="container_definitions"></a>

When you register a task definition, you must specify a list of container definitions that are passed to the Docker daemon on a container instance. The following parameters are allowed in a container definition.

**Topics**
+ [Standard container definition parameters](#standard_container_definition_params)
+ [Advanced container definition parameters](#advanced_container_definition_params)
+ [Other container definition parameters](#other_container_definition_params)

### Standard container definition parameters
<a name="standard_container_definition_params"></a>

The following task definition parameters are either required or used in most container definitions.

**Topics**
+ [Name](#container_definition_name)
+ [Image](#container_definition_image)
+ [Memory](#container_definition_memory)
+ [Port mappings](#container_definition_portmappings)
+ [Private Repository Credentials](#container_definition_repositoryCredentials)

#### Name
<a name="container_definition_name"></a>

`name`  
Type: String  
Required: Yes  
The name of a container. Up to 255 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed. If you're linking multiple containers in a task definition, the `name` of one container can be entered in the `links` of another container. This is to connect the containers.

#### Image
<a name="container_definition_image"></a>

`image`  
Type: String  
Required: Yes  
The image used to start a container. This string is passed directly to the Docker daemon. By default, images in the Docker Hub registry are available. You can also specify other repositories with either `{{repository-url}}/{{image}}:{{tag}}` or `{{repository-url}}/{{image}}@{{digest}}`. Up to 255 letters (uppercase and lowercase), numbers, hyphens, underscores, colons, periods, forward slashes, and number signs are allowed. This parameter maps to `Image` in the docker create-container command and the `IMAGE` parameter of the Docker run command.  
+ When a new task starts, the Amazon ECS container agent pulls the latest version of the specified image and tag for the container to use. However, subsequent updates to a repository image aren't propagated to already running tasks.
+ When you don't specify a tag or digest in the image path in the task definition, the Amazon ECS container agent uses the `latest` tag to pull the specified image. 
+  Subsequent updates to a repository image aren't propagated to already running tasks.
+ Images in private registries are supported. For more information, see [Using non-AWS container images in Amazon ECS](private-auth.md).
+ Images in Amazon ECR repositories can be specified by using either the full `registry/repository:tag` or `registry/repository@digest` naming convention (for example, `{{aws_account_id}}.dkr.ecr.{{region}}.amazonaws.com``/{{my-web-app}}:{{latest}}` or `{{aws_account_id}}.dkr.ecr.{{region}}.amazonaws.com``/{{my-web-app}}@{{sha256:94afd1f2e64d908bc90dbca0035a5b567EXAMPLE}}`).
+ Images in official repositories on Docker Hub use a single name (for example, `ubuntu` or `mongo`).
+ Images in other repositories on Docker Hub are qualified with an organization name (for example, `amazon/amazon-ecs-agent`).
+ Images in other online repositories are qualified further by a domain name (for example, `quay.io/assemblyline/ubuntu`).

`versionConsistency`  
Type: String  
Valid values: `enabled`\|`disabled`  
Required: No  
Specifies whether Amazon ECS will resolve the container image tag provided in the container definition to an image digest. By default, this behavior is `enabled`. If you set the value for a container as `disabled`, Amazon ECS will not resolve the container image tag to a digest and will use the original image URI specified in the container definition for deployment. For more information about container image resolution, see [Container image resolution](deployment-type-ecs.md#deployment-container-image-stability).

#### Memory
<a name="container_definition_memory"></a>

`memory`  
Type: Integer  
Required: No  
The amount (in MiB) of memory to present to the container. If your container attempts to exceed the memory specified here, the container is killed. The total amount of memory reserved for all containers within a task must be lower than the task `memory` value, if one is specified. This parameter maps to `Memory` in the docker create-container command and the `--memory` option to docker run.  
The Docker 20.10.0 or later daemon reserves a minimum of 6 MiB of memory for a container. So, don't specify less than 6 MiB of memory for your containers.  
The Docker 19.03.13-ce or earlier daemon reserves a minimum of 4 MiB of memory for a container. So, don't specify less than 4 MiB of memory for your containers.  
If you're trying to maximize your resource utilization by providing your tasks as much memory as possible for a particular instance type, see [Reserving Amazon ECS Linux container instance memory](memory-management.md).

`memoryReservation`  
Type: Integer  
Required: No  
The soft limit (in MiB) of memory to reserve for the container. When system memory is under contention, Docker attempts to keep the container memory to this soft limit. However, your container can use more memory when needed. The container can use up to the hard limit that's specified with the `memory` parameter (if applicable) or all of the available memory on the container instance, whichever comes first. This parameter maps to `MemoryReservation` in the docker create-container command and the `--memory-reservation` option to docker run.  
If a task-level memory value isn't specified, you must specify a non-zero integer for one or both of `memory` or `memoryReservation` in a container definition. If you specify both, `memory` must be greater than `memoryReservation`. If you specify `memoryReservation`, then that value is subtracted from the available memory resources for the container instance that the container is placed on. Otherwise, the value of `memory` is used.  
For example, suppose that your container normally uses 128 MiB of memory, but occasionally bursts to 256 MiB of memory for short periods of time. You can set a `memoryReservation` of 128 MiB, and a `memory` hard limit of 300 MiB. This configuration allows the container to only reserve 128 MiB of memory from the remaining resources on the container instance. At the same time, this configuration also allows the container to use more memory resources when needed.  
This parameter isn't supported for Windows containers.
The Docker 20.10.0 or later daemon reserves a minimum of 6 MiB of memory for a container. So, don't specify less than 6 MiB of memory for your containers.  
The Docker 19.03.13-ce or earlier daemon reserves a minimum of 4 MiB of memory for a container. So, don't specify less than 4 MiB of memory for your containers.  
If you're trying to maximize your resource utilization by providing your tasks as much memory as possible for a particular instance type, see [Reserving Amazon ECS Linux container instance memory](memory-management.md).

#### Port mappings
<a name="container_definition_portmappings"></a>

`portMappings`  
Type: Object array  
Required: No  
Port mappings expose your container's network ports to the outside world. this allows clients to access your application. It's also used for inter-container communication within the same task.  
For task definitions that use the `awsvpc` network mode, only specify the `containerPort`. The `hostPort` is always ignored, and the container port is automatically mapped to a random high-numbered port on the host.  
Port mappings on Windows use the `NetNAT` gateway address rather than `localhost`. There's no loopback for port mappings on Windows, so you can't access a container's mapped port from the host itself.   
Most fields of this parameter (including `containerPort`, `hostPort`, `protocol`) map to `PortBindings` in thedocker create-container command and the `--publish` option to docker run. If the network mode of a task definition is set to `host`, host ports must either be undefined or match the container port in the port mapping.  
After a task reaches the `RUNNING` status, manual and automatic host and container port assignments are visible in the following locations:  
+ Console: The **Network Bindings** section of a container description for a selected task.
+ AWS CLI: The `networkBindings` section of the **describe-tasks** command output.
+ API: The `DescribeTasks` response.
+ Metadata: The task metadata endpoint.  
`appProtocol`  
Type: String  
Required: No  
The application protocol that's used for the port mapping. This parameter only applies to Service Connect. We recommend that you set this parameter to be consistent with the protocol that your application uses. If you set this parameter, Amazon ECS adds protocol-specific connection handling to the service connect proxy. If you set this parameter, Amazon ECS adds protocol-specific telemetry in the Amazon ECS console and CloudWatch.  
If you don't set a value for this parameter, then TCP is used. However, Amazon ECS doesn't add protocol-specific telemetry for TCP.  
For more information, see [Use Service Connect to connect Amazon ECS services with short names](service-connect.md).  
Valid protocol values: `"http" | "http2" | "grpc" `  
`containerPort`  
Type: Integer  
Required: Yes, when `portMappings` are used  
The port number on the container that's bound to the user-specified or automatically assigned host port.  
For tasks that use the `awsvpc` network mode, you use `containerPort` to specify the exposed ports.  
For Windows containers on Fargate, you can't use port 3150 for the `containerPort`. This is because it's reserved.  
`containerPortRange`  
Type: String  
Required: No  
The port number range on the container that's bound to the dynamically mapped host port range.   
You can only set this parameter by using the `register-task-definition` API. The option is available in the `portMappings` parameter. For more information, see [register-task-definition](https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html) in the *AWS Command Line Interface Reference*.  
The following rules apply when you specify a `containerPortRange`:  
+ You must use the `awsvpc` network mode.
+ This parameter is available for both the Linux and Windows operating systems.
+ The container instance must have at least version 1.67.0 of the container agent and at least version 1.67.0-1 of the `ecs-init` package.
+ You can specify a maximum of 100 port ranges for each container.
+ You don't specify a `hostPortRange`. The value of the `hostPortRange` is set as follows:
  + For containers in a task with the `awsvpc` network mode, the `hostPort` is set to the same value as the `containerPort`. This is a static mapping strategy.
+ The `containerPortRange` valid values are between 1 and 65535.
+ A port can only be included in one port mapping for each container.
+ You can't specify overlapping port ranges.
+ The first port in the range must be less than last port in the range.
+ Docker recommends that you turn off the Docker-proxy in the Docker daemon config file when you have a large number of ports.

  For more information, see [ Issue \#11185](https://github.com/moby/moby/issues/11185) on GitHub.

  For information about how to turn off the docker-proxy in the Docker daemon config file, see [Docker daemon](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/bootstrap_container_instance.html#bootstrap_docker_daemon) in the *Amazon ECS Developer Guide*.
You can call [DescribeTasks](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DescribeTasks.html) to view the `hostPortRange`, which are the host ports that are bound to the container ports.  
The port ranges aren't included in the Amazon ECS task events, which are sent to EventBridge. For more information, see [Automate responses to Amazon ECS errors using EventBridge](cloudwatch_event_stream.md).  
`hostPortRange`  
Type: String  
Required: No  
The port number range on the host that's used with the network binding. This is assigned by Docker and delivered by the Amazon ECS agent.  
`hostPort`  
Type: Integer  
Required: No  
The port number on the container instance to reserve for your container.  
The `hostPort` can either be kept blank or be the same value as `containerPort`.  
The default ephemeral port range Docker version 1.6.0 and later is listed on the instance under `/proc/sys/net/ipv4/ip_local_port_range`. If this kernel parameter is unavailable, the default ephemeral port range from `49153–65535` is used. Don't attempt to specify a host port in the ephemeral port range. This is because these are reserved for automatic assignment. In general, ports under `32768` are outside of the ephemeral port range.   
The default reserved ports are `22` for SSH, the Docker ports `2375` and `2376`, and the Amazon ECS container agent ports `51678-51680`. Any host port that was previously user-specified for a running task is also reserved while the task is running. After a task stops, the host port is released. The current reserved ports are displayed in the `remainingResources` of **describe-container-instances** output. A container instance might have up to 100 reserved ports at a time, including the default reserved ports. Automatically assigned ports don't count toward the 100 reserved ports quota.  
`name`  
Type: String  
Required: No, required for Service Connect and VPC Lattice to be configured in a service  
The name that's used for the port mapping. This parameter only applies to Service Connect and VPC Lattice. This parameter is the name that you use in the Service Connect and VPC Lattice configuration of a service.  
For more information, see [Use Service Connect to connect Amazon ECS services with short names](service-connect.md).  
In the following example, both of the required fields for Service Connect and VPC Lattice are used.  

```
"portMappings": [
    {
        "name": {{string}},
        "containerPort": {{integer}}
    }
]
```  
`protocol`  
Type: String  
Required: No  
The protocol that's used for the port mapping. Valid values are `tcp` and `udp` (case-sensitive). The default is `tcp`. Amazon Amazon ECS treats any other specified value as `tcp`.  
Only `tcp` is supported for Service Connect. Remember that `tcp` is implied if this field isn't set. 
If you're specifying a host port, use the following syntax.  

```
"portMappings": [
    {
        "containerPort": integer,
        "hostPort": integer
    }
    ...
]
```
If you want an automatically assigned host port, use the following syntax.  

```
"portMappings": [
    {
        "containerPort": integer
    }
    ...
]
```

#### Private Repository Credentials
<a name="container_definition_repositoryCredentials"></a>

`repositoryCredentials`  
Type: [RepositoryCredentials](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_RepositoryCredentials.html) object  
Required: No  
The repository credentials for private registry authentication.  
For more information, see [Using non-AWS container images in Amazon ECS](private-auth.md).    
 `credentialsParameter`  
Type: String  
Required: Yes, when `repositoryCredentials` are used  
The Amazon Resource Name (ARN) of the secret containing the private repository credentials.  
For more information, see [Using non-AWS container images in Amazon ECS](private-auth.md).  
When you use the Amazon ECS API, AWS CLI, or AWS SDKs, if the secret exists in the same Region as the task that you're launching then you can use either the full ARN or the name of the secret. When you use the AWS Management Console, you must specify the full ARN of the secret.
The following is a snippet of a task definition that shows the required parameters:  

```
"containerDefinitions": [
    {
        "image": "{{private-repo/private-image}}",
        "repositoryCredentials": {
            "credentialsParameter": "{{arn:aws:secretsmanager:region:aws_account_id:secret:secret_name}}"
        }
    }
]
```

### Advanced container definition parameters
<a name="advanced_container_definition_params"></a>

The following advanced container definition parameters provide extended capabilities to the Docker run command that's used to launch containers on your Amazon ECS container instances.

**Topics**
+ [Restart policy](#container_definition_restart_policy)
+ [Health check](#container_definition_healthcheck)
+ [Environment](#container_definition_environment)
+ [Network settings](#container_definition_network)
+ [Storage and logging](#container_definition_storage)
+ [Security](#container_definition_security)
+ [Resource limits](#container_definition_limits)
+ [Docker labels](#container_definition_labels)

#### Restart policy
<a name="container_definition_restart_policy"></a>

`restartPolicy`  
The container restart policy and associated configuration parameters. When you set up a restart policy for a container, Amazon ECS can restart the container without needing to replace the task. For more information, see [Restart individual containers in Amazon ECS tasks with container restart policies](container-restart-policy.md).    
`enabled`  
Type: Boolean  
Required: Yes  
Specifies whether a restart policy is enabled for the container.  
`ignoredExitCodes`  
Type: Integer array  
Required: No  
A list of exit codes that Amazon ECS will ignore and not attempt a restart on. You can specify a maximum of 50 container exit codes. By default, Amazon ECS does not ignore any exit codes.  
`restartAttemptPeriod`  
Type: Integer  
Required: No  
A period of time (in seconds) that the container must run for before a restart can be attempted. A container can be restarted only once every `restartAttemptPeriod` seconds. If a container isn't able to run for this time period and exits early, it will not be restarted. You can set a minimum `restartAttemptPeriod` of 60 seconds and a maximum `restartAttemptPeriod` of 1800 seconds. By default, a container must run for 300 seconds before it can be restarted.

#### Health check
<a name="container_definition_healthcheck"></a>

`healthCheck`  
The container health check command and the associated configuration parameters for the container. For more information, see [Determine Amazon ECS task health using container health checks](healthcheck.md).    
`command`  
A string array that represents the command that the container runs to determine if it's healthy. The string array can start with `CMD` to run the command arguments directly, or `CMD-SHELL` to run the command with the container's default shell. If neither is specified, `CMD` is used.  
When registering a task definition in the AWS Management Console, use a comma separated list of commands. These commands are converted to a string after the task definition is created. An example input for a health check is the following.  

```
CMD-SHELL, curl -f http://localhost/ || exit 1
```
When registering a task definition using the AWS Management Console JSON panel, the AWS CLI, or the APIs, enclose the list of commands in brackets. An example input for a health check is the following.  

```
[ "CMD-SHELL", "curl -f http://localhost/ || exit 1" ]
```
An exit code of 0, with no `stderr` output, indicates success, and a non-zero exit code indicates failure.   
`interval`  
The period of time (in seconds) between each health check. You can specify between 5 and 300 seconds. The default value is 30 seconds.  
`timeout`  
The period of time (in seconds) to wait for a health check to succeed before it's considered a failure. You can specify between 2 and 60 seconds. The default value is 5 seconds.  
`retries`  
The number of times to retry a failed health check before the container is considered unhealthy. You can specify between 1 and 10 retries. The default value is three retries.  
`startPeriod`  
The optional grace period to provide containers time to bootstrap in before failed health checks count towards the maximum number of retries. You can specify a value between 0 and 300 seconds. By default, `startPeriod` is disabled.  
If a health check succeeds within the `startPeriod`, then the container is considered healthy and any subsequent failures count toward the maximum number of retries.

#### Environment
<a name="container_definition_environment"></a>

`cpu`  
Type: Integer  
Required: No  
The number of `cpu` units the Amazon ECS container agent reserves for the container. On Linux, this parameter maps to `CpuShares` in the [Create a container](https://docs.docker.com/reference/api/engine/version/v1.38/#operation/ContainerCreate) section.  
This field is optional for tasks that use Fargate. The total amount of CPU reserved for all the containers that are within a task must be lower than the task-level `cpu` value.  
Linux containers share unallocated CPU units with other containers on the container instance with the same ratio as their allocated amount. For example, assume that you run a single-container task on a single-core instance type with 512 CPU units specified for that container. Moreover, that task is the only task running on the container instance. In this example, the container can use the full 1,024 CPU unit share at any given time. However, assume then that you launched another copy of the same task on that container instance. Each task is guaranteed a minimum of 512 CPU units when needed. Similarly, if the other container isn't using the remaining CPU, each container can float to higher CPU usage. However, if both tasks were 100% active all of the time, they are limited to 512 CPU units.  
On Linux container instances, the Docker daemon on the container instance uses the CPU value to calculate the relative CPU share ratios for running containers. The minimum valid CPU share value that the Linux kernel allows is 2, and the maximum valid CPU share value that the Linux kernel allows is 262144. However, the CPU parameter isn't required, and you can use CPU values below two and above 262144 in your container definitions. For CPU values below two (including null) and above 262144, the behavior varies based on your Amazon ECS container agent version:  
On Windows container instances, the CPU quota is enforced as an absolute quota. Windows containers only have access to the specified amount of CPU that's defined in the task definition. A null or zero CPU value is passed to Docker as `0`. Windows then interprets this value as 1% of one CPU.  
For more examples, see [How Amazon ECS manages CPU and memory resources](https://aws.amazon.com/blogs/containers/how-amazon-ecs-manages-cpu-and-memory-resources/).

`gpu`  
This parameter isn't supported for containers that are hosted on Fargate.  
Type: [ResourceRequirement](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ResourceRequirement.html) object  
Required: No  
The number of physical `GPUs` that the Amazon ECS container agent reserves for the container. The number of GPUs reserved for all containers in a task must not exceed the number of available GPUs on the container instance the task is launched on. For more information, see [Amazon ECS task definitions for GPU workloads](ecs-gpu.md).

`Elastic Inference accelerator`  
This parameter isn't supported for containers that are hosted on Fargate.  
Type: [ResourceRequirement](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ResourceRequirement.html) object  
Required: No  
For the `InferenceAccelerator` type, the `value` matches the `deviceName` for an `InferenceAccelerator` specified in a task definition. For more information, see [Elastic Inference accelerator name (deprecated)](#elastic-Inference-accelerator).

`essential`  
Type: Boolean  
Required: No  
Suppose that the `essential` parameter of a container is marked as `true`, and that container fails or stops for any reason. Then, all other containers that are part of the task are stopped. If the `essential` parameter of a container is marked as `false`, then its failure doesn't affect the rest of the containers in a task. If this parameter is omitted, a container is assumed to be essential.  
All tasks must have at least one essential container. Suppose that you have an application that's composed of multiple containers. Then, group containers that are used for a common purpose into components, and separate the different components into multiple task definitions. For more information, see [Architect your application for Amazon ECS](application_architecture.md).  

```
"essential": true|false
```

`entryPoint`  
Early versions of the Amazon ECS container agent don't properly handle `entryPoint` parameters. If you have problems using `entryPoint`, update your container agent or enter your commands and arguments as `command` array items instead.
Type: String array  
Required: No  
The entry point that's passed to the container.   

```
"entryPoint": ["string", ...]
```

`command`  
Type: String array  
Required: No  
The command that's passed to the container. This parameter maps to `Cmd` in the create-container command and the `COMMAND` parameter to docker run. If there are multiple arguments, make sure that each argument is a separated string in the array.  

```
"command": ["string", ...]
```

`workingDirectory`  
Type: String  
Required: No  
The working directory to run commands inside the container in. This parameter maps to `WorkingDir` in the [Create a container](https://docs.docker.com/reference/api/engine/version/v1.38/#operation/ContainerCreate) section of the [Docker Remote API](https://docs.docker.com/reference/api/engine/version/v1.38/) and the `--workdir` option to [**docker run**](https://docs.docker.com/reference/cli/docker/container/run/).  

```
"workingDirectory": "string"
```

`environmentFiles`  
This isn't available for Windows containers on Fargate.  
Type: Object array  
Required: No  
A list of files containing the environment variables to pass to a container. This parameter maps to the `--env-file` option to the Docker run command.  
You can specify up to 10 environment files. The file must have a `.env` file extension. Each line in an environment file contains an environment variable in `VARIABLE=VALUE` format. Lines that start with `#` are treated as comments and are ignored.   
If there are individual environment variables specified in the container definition, they take precedence over the variables contained within an environment file. If multiple environment files are specified that contain the same variable, they're processed from the top down. We recommend that you use unique variable names. For more information, see [Pass an individual environment variable to an Amazon ECS container](taskdef-envfiles.md).    
`value`  
Type: String  
Required: Yes  
The Amazon Resource Name (ARN) of the Amazon S3 object containing the environment variable file.  
`type`  
Type: String  
Required: Yes  
The file type to use. The only supported value is `s3`.

`environment`  
Type: Object array  
Required: No  
The environment variables to pass to a container. This parameter maps to `Env` in the docker create-container command and the `--env` option to the docker run command.  
We do not recommend using plaintext environment variables for sensitive information, such as credential data.  
`name`  
Type: String  
Required: Yes, when `environment` is used  
The name of the environment variable.  
`value`  
Type: String  
Required: Yes, when `environment` is used  
The value of the environment variable.

```
"environment" : [
    { "name" : "string", "value" : "string" },
    { "name" : "string", "value" : "string" }
]
```

`secrets`  
Type: Object array  
Required: No  
An object that represents the secret to expose to your container. For more information, see [Pass sensitive data to an Amazon ECS container](specifying-sensitive-data.md).    
`name`  
Type: String  
Required: Yes  
The value to set as the environment variable on the container.  
`valueFrom`  
Type: String  
Required: Yes  
The secret to expose to the container. The supported values are either the full Amazon Resource Name (ARN) of the AWS Secrets Manager secret or the full ARN of the parameter in the AWS Systems Manager Parameter Store.  
If the Systems Manager Parameter Store parameter or Secrets Manager parameter exists in the same AWS Region as the task that you're launching, you can use either the full ARN or name of the secret. If the parameter exists in a different Region, then the full ARN must be specified.

```
"secrets": [
    {
        "name": "environment_variable_name",
        "valueFrom": "arn:aws:ssm:{{region}}:{{aws_account_id}}:parameter/{{parameter_name}}"
    }
]
```

#### Network settings
<a name="container_definition_network"></a>

`disableNetworking`  
This parameter is not supported for tasks running on Fargate.  
Type: Boolean  
Required: No  
When this parameter is true, networking is off within the container.  
The default is `false`.  

```
"disableNetworking": true|false
```

`links`  
This parameter isn't supported for tasks using the `awsvpc` network mode.  
Type: String array  
Required: No  
The `link` parameter allows containers to communicate with each other without the need for port mappings. This parameter is only supported if the network mode of a task definition is set to `bridge`. The `name:internalName` construct is analogous to `name:alias` in Docker links. Up to 255 letters (uppercase and lowercase), numbers, hyphens, and underscores are allowed..  
Containers that are collocated on the same container instance might communicate with each other without requiring links or host port mappings. The network isolation on a container instance is controlled by security groups and VPC settings.

```
"links": ["name:internalName", ...]
```

`hostname`  
Type: String  
Required: No  
The hostname to use for your container. This parameter maps to `Hostname` in the docker create-container and the `--hostname` option to docker run.  
If you're using the `awsvpc` network mode, the `hostname` parameter isn't supported.

```
"hostname": "string"
```

`dnsServers`  
This is not supported for tasks running on Fargate.  
Type: String array  
Required: No  
A list of DNS servers that are presented to the container.  

```
"dnsServers": ["string", ...]
```

`extraHosts`  
This parameter isn't supported for tasks that use the `awsvpc` network mode.  
Type: Object array  
Required: No  
A list of hostnames and IP address mappings to append to the `/etc/hosts` file on the container.   
This parameter maps to `ExtraHosts` in the docker create-container command and the `--add-host` option to docker run.  

```
"extraHosts": [
      {
        "hostname": "string",
        "ipAddress": "string"
      }
      ...
    ]
```  
`hostname`  
Type: String  
Required: Yes, when `extraHosts` are used  
The hostname to use in the `/etc/hosts` entry.  
`ipAddress`  
Type: String  
Required: Yes, when `extraHosts` are used  
The IP address to use in the `/etc/hosts` entry.

#### Storage and logging
<a name="container_definition_storage"></a>

`readonlyRootFilesystem`  
Type: Boolean  
Required: No  
When this parameter is true, the container is given read-only access to its root file system. This parameter maps to `ReadonlyRootfs` in the docker create-container command the `--read-only` option to docker run.  
This parameter is not supported for Windows containers.
The default is `false`.  

```
"readonlyRootFilesystem": true|false
```

`mountPoints`  
Type: Object array  
Required: No  
The mount points for the data volumes in your container. This parameter maps to `Volumes` in the create-container Docker API and the `--volume` option to docker run.  
Windows containers can mount whole directories on the same drive as `$env:ProgramData`. Windows containers cannot mount directories on a different drive, and mount points cannot be used across drives. You must specify mount points to attach an Amazon EBS volume directly to an Amazon ECS task.    
`sourceVolume`  
Type: String  
Required: Yes, when `mountPoints` are used  
The name of the volume to mount.  
`containerPath`  
Type: String  
Required: Yes, when `mountPoints` are used  
The path in the container where the volume will be mounted.  
`readOnly`  
Type: Boolean  
Required: No  
If this value is `true`, the container has read-only access to the volume. If this value is `false`, then the container can write to the volume. The default value is `false`.  
For tasks that run on EC2 instances running the Windows operating system, leave the value as the default of `false`.

`volumesFrom`  
Type: Object array  
Required: No  
Data volumes to mount from another container. This parameter maps to `VolumesFrom` in the docker create-container command and the `--volumes-from` option to docker run.    
`sourceContainer`  
Type: String  
Required: Yes, when `volumesFrom` is used  
The name of the container to mount volumes from.  
`readOnly`  
Type: Boolean  
Required: No  
If this value is `true`, the container has read-only access to the volume. If this value is `false`, then the container can write to the volume. The default value is `false`.

```
"volumesFrom": [
                {
                  "sourceContainer": "string",
                  "readOnly": true|false
                }
              ]
```

`logConfiguration`  
Type: [LogConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_LogConfiguration.html) Object  
Required: No  
The log configuration specification for the container.  
For example task definitions that use a log configuration, see [Example Amazon ECS task definitions](example_task_definitions.md).  
This parameter maps to `LogConfig` in the docker create-container command and the `--log-driver` option to docker run. By default, containers use the same logging driver that the Docker daemon uses. However, the container might use a different logging driver than the Docker daemon by specifying a log driver with this parameter in the container definition. To use a different logging driver for a container, the log system must be configured properly on the container instance (or on a different log server for remote logging options).   
Consider the following when specifying a log configuration for your containers:  
+ Amazon ECS supports a subset of the logging drivers that are available to the Docker daemon.
+ This parameter requires version 1.18 or later of the Docker Remote API on your container instance.
+ You must install any additional software outside of the task. For example, the Fluentd output aggregators or a remote host running Logstash to send Gelf logs to.

```
"logConfiguration": {
      "logDriver": "awslogs","fluentd","gelf","json-file","journald","splunk","syslog","awsfirelens",
      "options": {"{{string}}": "{{string}}"
        ...},
	"secretOptions": [{
		"name": "{{string}}",
		"valueFrom": "{{string}}"
	}]
}
```  
`logDriver`  
Type: String  
Valid values: `"awslogs","fluentd","gelf","json-file","journald","splunk","syslog","awsfirelens"`  
Required: Yes, when `logConfiguration` is used  
The log driver to use for the container. By default, the valid values that are listed earlier are log drivers that the Amazon ECS container agent can communicate with.  
The supported log drivers are `awslogs`, `splunk`, and `awsfirelens`.  
For more information about how to use the `awslogs` log driver in task definitions to send your container logs to CloudWatch Logs, see [Send Amazon ECS logs to CloudWatch](using_awslogs.md).  
For more information about using the `awsfirelens` log driver, see [Custom Log Routing](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/using_firelens.html).  
If you have a custom driver that isn't listed, you can fork the Amazon ECS container agent project that's [available on GitHub](https://github.com/aws/amazon-ecs-agent) and customize it to work with that driver. We encourage you to submit pull requests for changes that you want to have included. However, we don't currently support running modified copies of this software.
This parameter requires version 1.18 of the Docker Remote API or greater on your container instance.  
`options`  
Type: String to string map  
Required: No  
The key/value map of configuration options to send to the log driver.  
The options you can specify depend on the log driver. Some of the options you can specify when you use the `awslogs` router to route logs to Amazon CloudWatch include the following:    
`awslogs-create-group`  
Required: No  
Specify whether you want the log group to be created automatically. If this option isn't specified, it defaults to `false`.  
Your IAM policy must include the `logs:CreateLogGroup` permission before you attempt to use `awslogs-create-group`.  
`awslogs-region`  
Required: Yes  
Specify the AWS Region that the `awslogs` log driver is to send your Docker logs to. You can choose to send all of your logs from clusters in different Regions to a single region in CloudWatch Logs. This is so that they're all visible in one location. Otherwise, you can separate them by Region for more granularity. Make sure that the specified log group exists in the Region that you specify with this option.  
`awslogs-group`  
Required: Yes  
Make sure to specify a log group that the `awslogs` log driver sends its log streams to.  
`awslogs-stream-prefix`  
Required: Yes  
Use the `awslogs-stream-prefix` option to associate a log stream with the specified prefix, the container name, and the ID of the Amazon ECS task that the container belongs to. If you specify a prefix with this option, then the log stream takes the following format.  

```
{{prefix-name}}/{{container-name}}/{{ecs-task-id}}
```
If you don't specify a prefix with this option, then the log stream is named after the container ID that's assigned by the Docker daemon on the container instance. Because it's difficult to trace logs back to the container that sent them with just the Docker container ID (which is only available on the container instance), we recommend that you specify a prefix with this option.  
For Amazon ECS services, you can use the service name as the prefix. Doing so, you can trace log streams to the service that the container belongs to, the name of the container that sent them, and the ID of the task that the container belongs to.  
You must specify a stream-prefix for your logs to have your logs appear in the Log pane when using the Amazon ECS console.  
`awslogs-datetime-format`  
Required: No  
This option defines a multiline start pattern in Python `strftime` format. A log message consists of a line that matches the pattern and any following lines that don’t match the pattern. The matched line is the delimiter between log messages.  
One example of a use case for using this format is for parsing output such as a stack dump, which might otherwise be logged in multiple entries. The correct pattern allows it to be captured in a single entry.  
For more information, see [awslogs-datetime-format](https://docs.docker.com/engine/logging/drivers/awslogs/#awslogs-datetime-format).  
You cannot configure both the `awslogs-datetime-format` and `awslogs-multiline-pattern` options.  
Multiline logging performs regular expression parsing and matching of all log messages. This might have a negative impact on logging performance.  
`awslogs-multiline-pattern`  
Required: No  
This option defines a multiline start pattern that uses a regular expression. A log message consists of a line that matches the pattern and any following lines that don’t match the pattern. The matched line is the delimiter between log messages.  
For more information, see [awslogs-multiline-pattern](https://docs.docker.com/engine/logging/drivers/awslogs/#awslogs-multiline-pattern).  
This option is ignored if `awslogs-datetime-format` is also configured.  
You cannot configure both the `awslogs-datetime-format` and `awslogs-multiline-pattern` options.  
Multiline logging performs regular expression parsing and matching of all log messages. This might have a negative impact on logging performance.
The following options apply to all supported log drivers.    
`mode`  
Required: No  
Valid values: `non-blocking` \| `blocking`  
This option defines the delivery mode of log messages from the container to the log driver specified using `logDriver`. The delivery mode you choose affects application availability when the flow of logs from the container is interrupted.  
If you use the `blocking` mode and the flow of logs is interrupted, calls from container code to write to the `stdout` and `stderr` streams will block. The logging thread of the application will block as a result. This may cause the application to become unresponsive and lead to container healthcheck failure.   
If you use the `non-blocking` mode, the container's logs are instead stored in an in-memory intermediate buffer configured with the `max-buffer-size` option. This prevents the application from becoming unresponsive when logs cannot be sent. We recommend using this mode if you want to ensure service availability and are okay with some log loss. For more information, see [Preventing log loss with non-blocking mode in the `awslogs` container log driver](https://aws.amazon.com/blogs/containers/preventing-log-loss-with-non-blocking-mode-in-the-awslogs-container-log-driver/).  
You can set a default `mode` for all containers in a specific AWS Region by using the `defaultLogDriverMode` account setting. If you don't specify the `mode` option in the `logConfiguration` or configure the account setting, Amazon ECS will default to `non-blocking` mode. For more information about the account setting, see [Default log driver mode](ecs-account-settings.md#default-log-driver-mode).  
When `non-blocking` mode is used, the `max-buffer-size` log option controls the size of the buffer that's used for intermediate message storage. Make sure to specify an adequate buffer size based on your application. The total amount of memory allocated at the task level should be greater than the amount of memory that's allocated for all the containers in addition to the log driver memory buffer.  
On June 25, 2025, Amazon ECS changed the default log driver mode from `blocking` to `non-blocking` to prioritize task availability over logging. To continue using the `blocking` mode after this change, do one of the following:  
+ Set the `mode` option in your container definition's `logConfiguration` as `blocking`.
+ Set the `defaultLogDriverMode` account setting to `blocking`.  
`max-buffer-size`  
Required: No  
Default value: `10m`  
When `non-blocking` mode is used, the `max-buffer-size` log option controls the size of the buffer that's used for intermediate message storage. Make sure to specify an adequate buffer size based on your application. When the buffer fills up, further logs cannot be stored. Logs that cannot be stored are lost. 
To route logs using the `splunk` log router, you need to specify a `splunk-token` and a `splunk-url`.  
When you use the `awsfirelens` log router to route logs to an AWS service or AWS Partner Network destination for log storage and analytics, you can set the `log-driver-buffer-limit` option to limit the number of log lines that are buffered in memory, before being sent to the log router container. It can help to resolve potential log loss issue because high throughput might result in memory running out for the buffer inside of Docker. For more information, see [Configuring Amazon ECS logs for high throughput](firelens-docker-buffer-limit.md).  
Other options you can specify when using `awsfirelens` to route logs depend on the destination. When you export logs to Amazon Data Firehose, you can specify the AWS Region with `region` and a name for the log stream with `delivery_stream`.  
When you export logs to Amazon Kinesis Data Streams, you can specify an AWS Region with `region` and a data stream name with `stream`.  
 When you export logs to Amazon OpenSearch Service, you can specify options like `Name`, `Host` (OpenSearch Service endpoint without protocol), `Port`, `Index`, `Type`, `Aws_auth`, `Aws_region`, `Suppress_Type_Name`, and `tls`.  
When you export logs to Amazon S3, you can specify the bucket using the `bucket` option. You can also specify `region`, `total_file_size`, `upload_timeout`, and `use_put_object` as options.  
This parameter requires version 1.19 of the Docker Remote API or greater on your container instance.  
`secretOptions`  
Type: Object array  
Required: No  
An object that represents the secret to pass to the log configuration. Secrets that are used in log configuration can include an authentication token, certificate, or encryption key. For more information, see [Pass sensitive data to an Amazon ECS container](specifying-sensitive-data.md).    
`name`  
Type: String  
Required: Yes  
The value to set as the environment variable on the container.  
`valueFrom`  
Type: String  
Required: Yes  
The secret to expose to the log configuration of the container.

```
"logConfiguration": {
	"logDriver": "splunk",
	"options": {
		"splunk-url": "https://cloud.splunk.com:8080",
		"splunk-token": "...",
		"tag": "...",
		...
	},
	"secretOptions": [{
		"name": "{{splunk-token}}",
		"valueFrom": "{{/ecs/logconfig/splunkcred}}"
	}]
}
```

`firelensConfiguration`  
Type: [FirelensConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_FirelensConfiguration.html) Object  
Required: No  
The FireLens configuration for the container. This is used to specify and configure a log router for container logs. For more information, see [Send Amazon ECS logs to an AWS service or AWS Partner](using_firelens.md).  

```
{
    "firelensConfiguration": {
        "type": "fluentd",
        "options": {
            "KeyName": ""
        }
    }
}
```  
`options`  
Type: String to string map  
Required: No  
The key/value map of options to use when configuring the log router. This field is optional and can be used to specify a custom configuration file or to add additional metadata, such as the task, task definition, cluster, and container instance details to the log event. If specified, the syntax to use is `"options":{"enable-ecs-log-metadata":"true|false","config-file-type:"s3|file","config-file-value":"arn:aws:s3:::{{amzn-s3-demo-bucket}}/fluent.conf|filepath"}`. For more information, see [Example Amazon ECS task definition: Route logs to FireLens](firelens-taskdef.md).  
`type`  
Type: String  
Required: Yes  
The log router to use. The valid values are `fluentd` or `fluentbit`.

#### Security
<a name="container_definition_security"></a>

For more information about container security, see [Amazon ECS task and container security best practices](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-tasks-containers.html).

`credentialSpecs`  
Type: String array  
Required: No  
A list of ARNs in SSM or Amazon S3 to a credential spec (`CredSpec`) file that configures the container for Active Directory authentication. We recommend that you use this parameter instead of the `dockerSecurityOptions`. The maximum number of ARNs is 1.  
There are two formats for each ARN.    
credentialspecdomainless:MyARN  
You use `credentialspecdomainless:MyARN` to provide a `CredSpec` with an additional section for a secret in Secrets Manager. You provide the login credentials to the domain in the secret.  
Each task that runs on any container instance can join different domains.  
You can use this format without joining the container instance to a domain.  
credentialspec:MyARN  
You use `credentialspec:MyARN` to provide a `CredSpec` for a single domain.  
You must join the container instance to the domain before you start any tasks that use this task definition.
In both formats, replace `MyARN` with the ARN in SSM or Amazon S3.  
The `credspec` must provide a ARN in Secrets Manager for a secret containing the username, password, and the domain to connect to. For better security, the instance isn't joined to the domain for domainless authentication. Other applications on the instance can't use the domainless credentials. You can use this parameter to run tasks on the same instance, even it the tasks need to join different domains. For more information, see [Using gMSAs for Windows Containers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/windows-gmsa.html) and [Using gMSAs for Linux Containers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/linux-gmsa.html).

`user`  
Type: String  
Required: No  
The user to use inside the container. This parameter maps to `User` in the docker create-container command and the `--user` option to docker run.  
When running tasks that use the `host` network mode, don't run containers using the root user (UID 0). As a security best practice, always use a non-root user.
You can specify the `user` using the following formats. If specifying a UID or GID, you must specify it as a positive integer.  
+ `user`
+ `user:group`
+ `uid`
+ `uid:gid`
+ `user:gid`
+ `uid:group`
This parameter is not supported for Windows containers.

```
"user": "string"
```

#### Resource limits
<a name="container_definition_limits"></a>

`ulimits`  
Type: Object array  
Required: No  
A list of `ulimit` values to define for a container. This value overwrites the default resource quota setting for the operating system. This parameter maps to `Ulimits` in the docker create-container command and the `--ulimit` option to docker run.  
Amazon ECS tasks hosted on Fargate use the default resource limit values set by the operating system with the exception of the `nofile` resource limit parameter. The `nofile` resource limit sets a restriction on the number of open files that a container can use. On Fargate, the default `nofile` soft limit is ` 65535` and hard limit is `65535`. You can set the values of both limits up to `1048576`. For more information, see [Task resource limits](fargate-tasks-services.md#fargate-resource-limits).  
This parameter requires version 1.18 of the Docker Remote API or greater on your container instance.  
This parameter is not supported for Windows containers.

```
"ulimits": [
      {
        "name": "core"|"cpu"|"data"|"fsize"|"locks"|"memlock"|"msgqueue"|"nice"|"nofile"|"nproc"|"rss"|"rtprio"|"rttime"|"sigpending"|"stack",
        "softLimit": integer,
        "hardLimit": integer
      }
      ...
    ]
```  
`name`  
Type: String  
Valid values: `"core" | "cpu" | "data" | "fsize" | "locks" | "memlock" | "msgqueue" | "nice" | "nofile" | "nproc" | "rss" | "rtprio" | "rttime" | "sigpending" | "stack"`  
Required: Yes, when `ulimits` are used  
The `type` of the `ulimit`.  
`hardLimit`  
Type: Integer  
Required: Yes, when `ulimits` are used  
The hard limit for the `ulimit` type. The value can be specified in bytes, seconds, or as a count, depending on the `type` of the `ulimit`.  
`softLimit`  
Type: Integer  
Required: Yes, when `ulimits` are used  
The soft limit for the `ulimit` type. The value can be specified in bytes, seconds, or as a count, depending on the `type` of the `ulimit`.

#### Docker labels
<a name="container_definition_labels"></a>

`dockerLabels`  
Type: String to string map  
Required: No  
A key/value map of labels to add to the container. This parameter maps to `Labels` in the docker create-container command and the `--label` option to docker run.   
This parameter requires version 1.18 of the Docker Remote API or greater on your container instance.  

```
"dockerLabels": {"string": "string"
      ...}
```

### Other container definition parameters
<a name="other_container_definition_params"></a>

The following container definition parameters can be used when registering task definitions in the Amazon ECS console by using the **Configure via JSON** option. For more information, see [Creating an Amazon ECS task definition using the console](create-task-definition.md).

**Topics**
+ [Linux parameters](#container_definition_linuxparameters)
+ [Container dependency](#container_definition_dependson)
+ [Container timeouts](#container_definition_timeout)
+ [System controls](#container_definition_systemcontrols)
+ [Interactive](#container_definition_interactive)
+ [Pseudo terminal](#container_definition_pseudoterminal)

#### Linux parameters
<a name="container_definition_linuxparameters"></a>

`linuxParameters`  
Type: [LinuxParameters](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_LinuxParameters.html) object  
Required: No  
Linux-specific options that are applied to the container, such as [KernelCapabilities](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_KernelCapabilities.html).  
This parameter isn't supported for Windows containers.

```
"linuxParameters": {
      "capabilities": {
        "add": ["string", ...],
        "drop": ["string", ...]
        }
      }
```  
`capabilities`  
Type: [KernelCapabilities](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_KernelCapabilities.html) object  
Required: No  
The Linux capabilities for the container that are dropped from the default configuration provided by Docker. For more information about these Linux capabilities, see the [capabilities(7)](http://man7.org/linux/man-pages/man7/capabilities.7.html) Linux manual page.    
`add`  
Type: String array  
Valid values: `"SYS_PTRACE"`  
Required: No  
The Linux capabilities for the container to add to the default configuration that's provided by Docker. This parameter maps to `CapAdd` in the docker create-container command and the `--cap-add` option to docker run.  
`drop`  
Type: String array  
Valid values: `"ALL" | "AUDIT_CONTROL" | "AUDIT_WRITE" | "BLOCK_SUSPEND" | "CHOWN" | "DAC_OVERRIDE" | "DAC_READ_SEARCH" | "FOWNER" | "FSETID" | "IPC_LOCK" | "IPC_OWNER" | "KILL" | "LEASE" | "LINUX_IMMUTABLE" | "MAC_ADMIN" | "MAC_OVERRIDE" | "MKNOD" | "NET_ADMIN" | "NET_BIND_SERVICE" | "NET_BROADCAST" | "NET_RAW" | "SETFCAP" | "SETGID" | "SETPCAP" | "SETUID" | "SYS_ADMIN" | "SYS_BOOT" | "SYS_CHROOT" | "SYS_MODULE" | "SYS_NICE" | "SYS_PACCT" | "SYS_PTRACE" | "SYS_RAWIO" | "SYS_RESOURCE" | "SYS_TIME" | "SYS_TTY_CONFIG" | "SYSLOG" | "WAKE_ALARM"`  
Required: No  
The Linux capabilities for the container to remove from the default configuration that's provided by Docker. This parameter maps to `CapDrop` in the docker create-container command and the `--cap-drop` option to docker run.  
`devices`  
Any host devices to expose to the container. This parameter maps to `Devices` in the docker create-container command and the `--device` option to Docker run.  
The `devices` parameter isn't supported when you use the Fargate launch type.
Type: Array of [Device](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_Device.html) objects  
Required: No    
`hostPath`  
The path for the device on the host container instance.  
Type: String  
Required: Yes  
`containerPath`  
The path inside the container to expose the host device at.  
Type: String  
Required: No  
`permissions`  
The explicit permissions to provide to the container for the device. By default, the container has permissions for `read`, `write`, and `mknod` on the device.  
Type: Array of strings  
Valid Values: `read` \| `write` \| `mknod`  
`initProcessEnabled`  
Run an `init` process inside the container that forwards signals and reaps processes. This parameter maps to the `--init` option to docker run.  
This parameter requires version 1.25 of the Docker Remote API or greater on your container instance.  
`maxSwap`  
This is not supported for tasks running on Fargate.  
The total amount of swap memory (in MiB) a container can use. This parameter is translated to the `--memory-swap` option to docker run where the value is the sum of the container memory plus the `maxSwap` value.  
If a `maxSwap` value of `0` is specified, the container doesn't use swap. Accepted values are `0` or any positive integer. If the `maxSwap` parameter is omitted, the container uses the swap configuration for the container instance that it's running on. A `maxSwap` value must be set for the `swappiness` parameter to be used.  
`sharedMemorySize`  
The value for the size (in MiB) of the `/dev/shm` volume. This parameter maps to the `--shm-size` option to docker run.  
If you're using tasks that use Fargate, the `sharedMemorySize` parameter isn't supported.
Type: Integer  
`tmpfs`  
The container path, mount options, and maximum size (in MiB) of the tmpfs mount. This parameter maps to the `--tmpfs` option to docker run.  
Type: Array of [Tmpfs](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_Tmpfs.html) objects  
Required: No    
`containerPath`  
The absolute file path where the tmpfs volume is to be mounted.  
Type: String  
Required: Yes  
`mountOptions`  
The list of tmpfs volume mount options.  
Type: Array of strings  
Required: No  
Valid Values: `"defaults" | "ro" | "rw" | "suid" | "nosuid" | "dev" | "nodev" | "exec" | "noexec" | "sync" | "async" | "dirsync" | "remount" | "mand" | "nomand" | "atime" | "noatime" | "diratime" | "nodiratime" | "bind" | "rbind" | "unbindable" | "runbindable" | "private" | "rprivate" | "shared" | "rshared" | "slave" | "rslave" | "relatime" | "norelatime" | "strictatime" | "nostrictatime" | "mode" | "uid" | "gid" | "nr_inodes" | "nr_blocks" | "mpol"`  
`size`  
The maximum size (in MiB) of the tmpfs volume.  
Type: Integer  
Required: Yes

#### Container dependency
<a name="container_definition_dependson"></a>

`dependsOn`  
Type: Array of [ContainerDependency](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ContainerDependency.html) objects  
Required: No  
The dependencies defined for container startup and shutdown. A container can contain multiple dependencies. When a dependency is defined for container startup, for container shutdown it is reversed. For an example, see [Container dependency](example_task_definitions.md#example_task_definition-containerdependency).  
If a container doesn't meet a dependency constraint or times out before meeting the constraint, Amazon ECS doesn't progress dependent containers to their next state.
This parameter requires that the task or service uses platform version `1.3.0` or later (Linux) or `1.0.0` (Windows).  

```
"dependsOn": [
    {
        "containerName": "{{string}}",
        "condition": "{{string}}"
    }
]
```  
`containerName`  
Type: String  
Required: Yes  
The container name that must meet the specified condition.  
`condition`  
Type: String  
Required: Yes  
The dependency condition of the container. The following are the available conditions and their behavior:  
+ `START` – This condition emulates the behavior of links and volumes today. The condition validates that a dependent container is started before permitting other containers to start.
+ `COMPLETE` – This condition validates that a dependent container runs to completion (exits) before permitting other containers to start. This can be useful for non-essential containers that run a script and then exit. This condition can't be set on an essential container.
+ `SUCCESS` – This condition is the same as `COMPLETE`, but it also requires that the container exits with a `zero` status. This condition can't be set on an essential container.
+ `HEALTHY` – This condition validates that the dependent container passes its container health check before permitting other containers to start. This requires that the dependent container has health checks configured in the task definition. This condition is confirmed only at task startup.

#### Container timeouts
<a name="container_definition_timeout"></a>

`startTimeout`  
Type: Integer  
Required: No  
Example values: `120`  
Time duration (in seconds) to wait before giving up on resolving dependencies for a container.  
For example, you specify two containers in a task definition with `containerA` having a dependency on `containerB` reaching a `COMPLETE`, `SUCCESS`, or `HEALTHY` status. If a `startTimeout` value is specified for `containerB` and it doesn't reach the desired status within that time, then `containerA` doesn't start.  
If a container doesn't meet a dependency constraint or times out before meeting the constraint, Amazon ECS doesn't progress dependent containers to their next state.
This parameter requires that the task or service uses platform version `1.3.0` or later (Linux). The maximum value is 120 seconds.

`stopTimeout`  
Type: Integer  
Required: No  
Example values: `120`  
Time duration (in seconds) to wait before the container is forcefully killed if it doesn't exit normally on its own.  
This parameter requires that the task or service uses platform version `1.3.0` or later (Linux). If the parameter isn't specified, then the default value of 30 seconds is used. The maximum value is 120 seconds.

#### System controls
<a name="container_definition_systemcontrols"></a>

`systemControls`  
Type: [SystemControl](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_SystemControl.html) object  
Required: No  
A list of namespace kernel parameters to set in the container. This parameter maps to `Sysctls` in the docker create-container commandand the `--sysctl` option to docker run. For example, you can configure `net.ipv4.tcp_keepalive_time` setting to maintain longer lived connections.  
We don't recommend that you specify network-related `systemControls` parameters for multiple containers in a single task that also uses either the `awsvpc` or `host` network mode. Doing this has the following disadvantages:  
+ If you set `systemControls` for any container, it applies to all containers in the task. If you set different `systemControls` for multiple containers in a single task, the container that's started last determines which `systemControls` take effect.
If you're setting an IPC resource namespace to use for the containers in the task, the following conditions apply to your system controls. For more information, see [IPC mode](#task_definition_ipcmode).  
+ For tasks that use the `host` IPC mode, IPC namespace `systemControls` aren't supported.
+ For tasks that use the `task` IPC mode, IPC namespace `systemControls` values apply to all containers within a task.
This parameter is not supported for Windows containers.
This parameter is only supported for tasks that are hosted on AWS Fargate if the tasks are using platform version `1.4.0` or later (Linux). This isn't supported for Windows containers on Fargate.

```
"systemControls": [
    {
         "namespace":"{{string}}",
         "value":"{{string}}"
    }
]
```  
`namespace`  
Type: String  
Required: No  
The namespace kernel parameter to set a `value` for.  
Valid IPC namespace values: `"kernel.msgmax" | "kernel.msgmnb" | "kernel.msgmni" | "kernel.sem" | "kernel.shmall" | "kernel.shmmax" | "kernel.shmmni" | "kernel.shm_rmid_forced"`, and `Sysctls` that start with `"fs.mqueue.*"`  
Valid network namespace values: `Sysctls` that start with `"net.*"`. On Fargate, only namespaced `Sysctls` that exist within the container are accepted.  
All of these values are supported by Fargate.  
`value`  
Type: String  
Required: No  
The value for the namespace kernel parameter that's specified in `namespace`.

#### Interactive
<a name="container_definition_interactive"></a>

`interactive`  
Type: Boolean  
Required: No  
When this parameter is `true`, you can deploy containerized applications that require `stdin` or a `tty` to be allocated. This parameter maps to `OpenStdin` in the docker create-container command and the `--interactive` option to docker run.  
The default is `false`.

#### Pseudo terminal
<a name="container_definition_pseudoterminal"></a>

`pseudoTerminal`  
Type: Boolean  
Required: No  
When this parameter is `true`, a TTY is allocated. This parameter maps to `Tty` in the docker create-container command and the `--tty` option to docker run.  
The default is `false`.

## Elastic Inference accelerator name (deprecated)
<a name="elastic-Inference-accelerator"></a>

The Elastic Inference accelerator resource requirement for your task definition. 

**Note**  
Amazon Elastic Inference (EI) is no longer available to customers.

The following parameters are allowed in a task definition:

`deviceName`  
Type: String  
Required: Yes  
The Elastic Inference accelerator device name. The `deviceName` must also be referenced in a container definition see [Elastic Inference accelerator](#ContainerDefinition-elastic-inference).

`deviceType`  
Type: String  
Required: Yes  
The Elastic Inference accelerator to use.

## Proxy configuration
<a name="proxyConfiguration"></a>

`proxyConfiguration`  
Type: [ProxyConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_ProxyConfiguration.html) object  
Required: No  
The configuration details for the App Mesh proxy.  
This parameter is not supported for Windows containers.

```
"proxyConfiguration": {
    "type": "APPMESH",
    "containerName": "{{string}}",
    "properties": [
        {
           "name": "{{string}}",
           "value": "{{string}}"
        }
    ]
}
```  
`type`  
Type: String  
Value values: `APPMESH`  
Required: No  
The proxy type. The only supported value is `APPMESH`.  
`containerName`  
Type: String  
Required: Yes  
The name of the container that serves as the App Mesh proxy.  
`properties`  
Type: Array of [KeyValuePair](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_KeyValuePair.html) objects  
Required: No  
The set of network configuration parameters to provide the Container Network Interface (CNI) plugin, specified as key-value pairs.  
+ `IgnoredUID` – (Required) The user ID (UID) of the proxy container as defined by the `user` parameter in a container definition. This is used to ensure the proxy ignores its own traffic. If `IgnoredGID` is specified, this field can be empty.
+ `IgnoredGID` – (Required) The group ID (GID) of the proxy container as defined by the `user` parameter in a container definition. This is used to ensure the proxy ignores its own traffic. If `IgnoredUID` is specified, this field can be empty.
+ `AppPorts` – (Required) The list of ports that the application uses. Network traffic to these ports is forwarded to the `ProxyIngressPort` and `ProxyEgressPort`.
+ `ProxyIngressPort` – (Required) Specifies the port that incoming traffic to the `AppPorts` is directed to.
+ `ProxyEgressPort` – (Required) Specifies the port that outgoing traffic from the `AppPorts` is directed to.
+ `EgressIgnoredPorts` – (Required) The outbound traffic going to these specified ports is ignored and not redirected to the `ProxyEgressPort`. It can be an empty list.
+ `EgressIgnoredIPs` – (Required) The outbound traffic going to these specified IP addresses is ignored and not redirected to the `ProxyEgressPort`. It can be an empty list.  
`name`  
Type: String  
Required: No  
The name of the key-value pair.  
`value`  
Type: String  
Required: No  
The value of the key-value pair.

## Volumes
<a name="volumes"></a>

When you register a task definition, you can optionally specify a list of volumes to be passed to the Docker daemon on a container instance, which then becomes available for access by other containers on the same container instance.

The following are the types of data volumes that can be used:
+ Amazon EBS volumes — Provides cost-effective, durable, high-performance block storage for data intensive containerized workloads. You can attach 1 Amazon EBS volume per Amazon ECS task when running a standalone task, or when creating or updating a service. Amazon EBS volumes are supported for Linux tasks hosted on Fargate. For more information, see [Use Amazon EBS volumes with Amazon ECS](ebs-volumes.md).
+ Amazon EFS volumes — Provides simple, scalable, and persistent file storage for use with your Amazon ECS tasks. With Amazon EFS, storage capacity is elastic. It grows and shrinks automatically as you add and remove files. Your applications can have the storage that they need and when they need it. Amazon EFS volumes are supported for tasks that are hosted on Fargate. For more information, see [Use Amazon EFS volumes with Amazon ECS](efs-volumes.md).
+ FSx for Windows File Server volumes — Provides fully managed Microsoft Windows file servers. These file servers are backed by a Windows file system. When using FSx for Windows File Server together with Amazon ECS, you can provision your Windows tasks with persistent, distributed, shared, and static file storage. For more information, see [Use FSx for Windows File Server volumes with Amazon ECS](wfsx-volumes.md).

  Windows containers on Fargate do not support this option.
+ Bind mounts – A file or directory on the host machine that is mounted into a container. Bind mount host volumes are supported when running tasks. To use bind mount host volumes, specify a `host` and optional `sourcePath` value in your task definition.

For more information, see [Storage options for Amazon ECS tasks](using_data_volumes.md).

The following parameters are allowed in a container definition.

`name`  
Type: String  
Required: No  
The name of the volume. Up to 255 letters (uppercase and lowercase), numbers, hyphens (`-`), and underscores (`_`) are allowed. This name is referenced in the `sourceVolume` parameter of the container definition `mountPoints` object.

`host`  
Required: No  
The `host` parameter is used to tie the lifecycle of the bind mount to the host Amazon EC2 instance, rather than the task, and where it is stored. If the `host` parameter is empty, then the Docker daemon assigns a host path for your data volume, but the data is not guaranteed to persist after the containers associated with it stop running.  
Windows containers can mount whole directories on the same drive as `$env:ProgramData`.  
The `sourcePath` parameter is supported only when using tasks that are hosted on Amazon EC2 instances or Amazon ECS Managed Instances.  
`sourcePath`  
Type: String  
Required: No  
When the `host` parameter is used, specify a `sourcePath` to declare the path on the host Amazon EC2 instance that is presented to the container. If this parameter is empty, then the Docker daemon assigns a host path for you. If the `host` parameter contains a `sourcePath` file location, then the data volume persists at the specified location on the host Amazon EC2 instance until you delete it manually. If the `sourcePath` value does not exist on the host Amazon EC2 instance, the Docker daemon creates it. If the location does exist, the contents of the source path folder are exported.

`configuredAtLaunch`  
Type: Boolean  
Required: No  
Specifies whether a volume is configurable at launch. When set to `true`, you can configure the volume when running a standalone task, or when creating or updating a service. When set to `true`, you won't be able to provide another volume configuration in the task definition. This parameter must be set to `true` to configure an Amazon EBS volume for attachment to a task. Setting `configuredAtLaunch` to `true` and deferring volume configuration to the launch phase allows you to create task definitions that aren't constrained to a volume type or to specific volume settings. Doing this makes your task definition reusable across different execution environments. For more information, see [Amazon EBS volumes](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ebs-volumes.html).

`dockerVolumeConfiguration`  
Type: [DockerVolumeConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_DockerVolumeConfiguration.html) Object  
Required: No  
This parameter is specified when using Docker volumes. Docker volumes are supported only when running tasks on EC2 instances. Windows containers support only the use of the `local` driver. To use bind mounts, specify a `host` instead.    
`scope`  
Type: String  
Valid Values: `task` \| `shared`  
Required: No  
The scope for the Docker volume, which determines its lifecycle. Docker volumes that are scoped to a `task` are automatically provisioned when the task starts and destroyed when the task stops. Docker volumes that are scoped as `shared` persist after the task stops.  
`autoprovision`  
Type: Boolean  
Default value: `false`  
Required: No  
If this value is `true`, the Docker volume is created if it doesn't already exist. This field is used only if the `scope` is `shared`. If the `scope` is `task`, then this parameter must be omitted.  
`driver`  
Type: String  
Required: No  
The Docker volume driver to use. The driver value must match the driver name provided by Docker because this name is used for task placement. If the driver was installed by using the Docker plugin CLI, use `docker plugin ls` to retrieve the driver name from your container instance. If the driver was installed by using another method, use Docker plugin discovery to retrieve the driver name.  
`driverOpts`  
Type: String  
Required: No  
A map of Docker driver-specific options to pass through. This parameter maps to `DriverOpts` in the Create a volume section of Docker.  
`labels`  
Type: String  
Required: No  
Custom metadata to add to your Docker volume.

`efsVolumeConfiguration`  
Type: [EFSVolumeConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_EFSVolumeConfiguration.html) Object  
Required: No  
This parameter is specified when using Amazon EFS volumes.    
`fileSystemId`  
Type: String  
Required: Yes  
The Amazon EFS file system ID to use.  
`rootDirectory`  
Type: String  
Required: No  
The directory within the Amazon EFS file system to mount as the root directory inside the host. If this parameter is omitted, the root of the Amazon EFS volume will be used. Specifying `/` has the same effect as omitting this parameter.  
If an EFS access point is specified in the `authorizationConfig`, the root directory parameter must either be omitted or set to `/`, which will enforce the path set on the EFS access point.  
`transitEncryption`  
Type: String  
Valid values: `ENABLED` \| `DISABLED`  
Required: No  
Specifies whether to enable encryption for Amazon EFS data in transit between the Amazon ECS host and the Amazon EFS server. If Amazon EFS IAM authorization is used, transit encryption must be enabled. If this parameter is omitted, the default value of `DISABLED` is used. For more information, see [Encrypting Data in Transit](https://docs.aws.amazon.com/efs/latest/ug/encryption-in-transit.html) in the *Amazon Elastic File System User Guide*.  
`transitEncryptionPort`  
Type: Integer  
Required: No  
The port to use when sending encrypted data between the Amazon ECS host and the Amazon EFS server. If you don't specify a transit encryption port, the task will use the port selection strategy that the Amazon EFS mount helper uses. For more information, see [EFS Mount Helper](https://docs.aws.amazon.com/efs/latest/ug/efs-mount-helper.html) in the *Amazon Elastic File System User Guide*.  
`authorizationConfig`  
Type: [EFSAuthorizationConfig](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_EFSAuthorizationConfig.html) Object  
Required: No  
The authorization configuration details for the Amazon EFS file system.    
`accessPointId`  
Type: String  
Required: No  
The access point ID to use. If an access point is specified, the root directory value in the `efsVolumeConfiguration` must either be omitted or set to `/`, which will enforce the path set on the EFS access point. If an access point is used, transit encryption must be enabled in the `EFSVolumeConfiguration`. For more information, see [Working with Amazon EFS Access Points](https://docs.aws.amazon.com/efs/latest/ug/efs-access-points.html) in the *Amazon Elastic File System User Guide*.  
`iam`  
Type: String  
Valid values: `ENABLED` \| `DISABLED`  
Required: No  
Specifies whether to use the Amazon ECS task IAM role that's defined in a task definition when mounting the Amazon EFS file system. If enabled, transit encryption must be enabled in the `EFSVolumeConfiguration`. If this parameter is omitted, the default value of `DISABLED` is used. For more information, see [IAM Roles for Tasks](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html).

`FSxWindowsFileServerVolumeConfiguration`  
Type: [FSxWindowsFileServerVolumeConfiguration](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_FSxWindowsFileServerVolumeConfiguration.html) Object  
Required: Yes  
This parameter is specified when you're using an [Amazon FSx for Windows File Server](https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html) file system for task storage.    
`fileSystemId`  
Type: String  
Required: Yes  
The FSx for Windows File Server file system ID to use.  
`rootDirectory`  
Type: String  
Required: Yes  
The directory within the FSx for Windows File Server file system to mount as the root directory inside the host.  
`authorizationConfig`    
`credentialsParameter`  
Type: String  
Required: Yes  
The authorization credential options.  

**options:**
+ Amazon Resource Name (ARN) of an [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html) secret.
+ ARN of an [AWS Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/integration-ps-secretsmanager.html) parameter.  
`domain`  
Type: String  
Required: Yes  
A fully qualified domain name hosted by an [AWS Directory Service for Microsoft Active Directory](https://docs.aws.amazon.com/directoryservice/latest/admin-guide/directory_microsoft_ad.html) (AWS Managed Microsoft AD) directory or a self-hosted EC2 Active Directory.

## Tags
<a name="tags"></a>

When you register a task definition, you can optionally specify metadata tags that are applied to the task definition. Tags help you categorize and organize your task definition. Each tag consists of a key and an optional value. You define both of them. For more information, see [Tagging Amazon ECS resources](ecs-using-tags.md).

**Important**  
Don't add personally identifiable information or other confidential or sensitive information in tags. Tags are accessible to many AWS services, including billing. Tags aren't intended to be used for private or sensitive data.

The following parameters are allowed in a tag object.

`key`  
Type: String  
Required: No  
One part of a key-value pair that make up a tag. A key is a general label that acts like a category for more specific tag values.

`value`  
Type: String  
Required: No  
The optional part of a key-value pair that make up a tag. A value acts as a descriptor within a tag category (key).

## Other task definition parameters
<a name="other_task_definition_params"></a>

The following task definition parameters can be used when registering task definitions in the Amazon ECS console by using the **Configure via JSON** option. For more information, see [Creating an Amazon ECS task definition using the console](create-task-definition.md).

**Topics**
+ [Ephemeral storage](#task_definition_ephemeralStorage)
+ [IPC mode](#task_definition_ipcmode)
+ [PID mode](#task_definition_pidmode)
+ [Fault injection](#task_definition_faultInjection)

### Ephemeral storage
<a name="task_definition_ephemeralStorage"></a>

`ephemeralStorage`  
Type: [EphemeralStorage](https://docs.aws.amazon.com/AmazonECS/latest/APIReference/API_EphemeralStorage.html) object  
Required: No  
The amount of ephemeral storage (in GB) to allocate for the task. This parameter is used to expand the total amount of ephemeral storage available, beyond the default amount, for tasks that are hosted on AWS Fargate. For more information, see [Use bind mounts with Amazon ECS](bind-mounts.md).  
This parameter is only supported on platform version `1.4.0` or later (Linux) or `1.0.0` or later (Windows).

### IPC mode
<a name="task_definition_ipcmode"></a>

`ipcMode`  
This is not supported for tasks running on Fargate.  
Type: String  
Required: No  
The IPC resource namespace to use for the containers in the task. The valid values are `host`, `task`, or `none`. If `host` is specified, then all the containers that are within the tasks that specified the `host` IPC mode on the same container instance share the same IPC resources with the host Amazon EC2 instance. If `task` is specified, all the containers that are within the specified task share the same IPC resources. If `none` is specified, then IPC resources within the containers of a task are private and not shared with other containers in a task or on the container instance. If no value is specified, then the IPC resource namespace sharing depends on the Docker daemon setting on the container instance.  
If the `host` IPC mode is used, there's a heightened risk of undesired IPC namespace exposure.  
If you're setting namespaced kernel parameters that use `systemControls` for the containers in the task, the following applies to your IPC resource namespace.   
+ For tasks that use the `host` IPC mode, IPC namespace that's related `systemControls` aren't supported.
+ For tasks that use the `task` IPC mode, `systemControls` that relate to the IPC namespace apply to all containers within a task.

**Note**  
This parameter is not supported for Windows containers or tasks using the Fargate launch type.

### PID mode
<a name="task_definition_pidmode"></a>

`pidMode`  
Type: String  
Valid Values: `host` \| `task`  
Required: No  
The process namespace to use for the containers in the task. The valid values are `host` or `task`. On Linux containers, the only valid value is `task`. For example, monitoring sidecars might need `pidMode` to access information about other containers running in the same task.  
If `task` is specified, all containers within the specified task share the same process namespace.  
If no value is specified, the default is a private namespace for each container. 

**Note**  
This parameter is only supported for tasks that are hosted on AWS Fargate if the tasks are using platform version `1.4.0` or later (Linux). This isn't supported for Windows containers on Fargate.

### Fault injection
<a name="task_definition_faultInjection"></a>

`enableFaultInjection`  
Type: Boolean  
Valid Values: `true` \| `false`  
Required: No  
If this parameter is set to `true`, in a task's payload, Amazon ECS and Fargate accept fault injection requests from the task’s containers. By default, this parameter is set to `false`.