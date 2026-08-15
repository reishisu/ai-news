#!/bin/bash
# クラスタ作成に必要なものはどれだけあるか。
aws ecs create-cluster --generate-cli-skeleton \
| jq '{clusterName, capacityProviders,
       settings, serviceConnectDefaults}'
