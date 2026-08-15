#!/bin/bash
# この環境から本物の CloudFront は触れない、という証拠を残す。
# (雛形の生成はローカルで完結するので触らない)
set -u
echo "\$ aws cloudfront list-distributions"
aws cloudfront list-distributions 2>&1 | tail -1 | fold -s -w 38
