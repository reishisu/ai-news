#!/bin/bash
# create-service の雛形から、ALB とネットワークの
# 部分だけを取り出す。
aws ecs create-service --generate-cli-skeleton \
| jq '{loadBalancers, networkConfiguration}'
