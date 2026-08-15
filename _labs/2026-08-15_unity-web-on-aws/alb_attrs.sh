#!/bin/bash
U=https://docs.aws.amazon.com\
/elasticloadbalancing/latest/application
curl -sS "$U/load-balancer-listeners.md" \
  | grep -o 'routing\.http\.response\.[a-z_]*' \
  | sed 's/routing.http.response.//'
echo "--- cross-origin- を含む行数 ---"
curl -sS "$U/load-balancer-listeners.md" \
  | grep -ci 'cross-origin-'
