#!/bin/bash
V() { printf '%-10s: %s\n' "$1" "$2"; }
V aws       "$(aws --version 2>&1 | cut -d' ' -f1 | cut -d/ -f2)"
V botocore  "$(python3 -c 'import awscli.botocore as b;print(b.__version__)')"
V terraform "$(terraform version -json | jq -r .terraform_version)"
V aws-prov  "$(cd tf && terraform version -json \
  | jq -r '.provider_selections|to_entries[0].value')"
V python3   "$(python3 -V | cut -d' ' -f2)"
V node      "$(node -v)"
V docker    "$(docker --version | cut -d' ' -f3 | tr -d ,)"
V chromium  "$(/opt/pw-browsers/chromium --version | cut -d' ' -f2)"
