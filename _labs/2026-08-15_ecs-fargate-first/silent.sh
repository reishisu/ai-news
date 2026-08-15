#!/bin/bash
# Fargate でよくある4つの誤りを、
# terraform validate / plan が捕まえるか調べる。
# ラベルは全角を2桁として揃える。
SRC=$1; W=$(mktemp -d)
cp $SRC/.terraform.lock.hcl $W/
cp -r $SRC/.terraform $W/
pad() { python3 -c '
import sys,unicodedata
s=sys.argv[1]; n=int(sys.argv[2])
w=sum(2 if unicodedata.east_asian_width(c) in "WFA" else 1 for c in s)
sys.stdout.write(s+" "*(n-w))' "$1" "$2"; }
run() {
  local label="$1" expr="$2"
  cp $SRC/main.tf $W/main.tf
  python3 - "$W/main.tf" "$expr" <<'PY'
import sys
p,expr=sys.argv[1],sys.argv[2]
a,b=expr.split('=>')
s=open(p).read(); assert a in s, a
open(p,'w').write(s.replace(a,b,1))
PY
  ( cd $W
    v=$(terraform validate -no-color 2>&1)
    echo "$v" | grep -q Success && vr=通過 || vr=検出
    terraform plan -no-color -out=/dev/null >/dev/null 2>&1 \
      && pr=通過 || pr=検出
    pad "$label" 16; echo "validate:$vr plan:$pr" )
}
run "コンテナ名 typo" 'container_name   = var.lb_container_name=>container_name   = "wev"'
run "network_mode"   'network_mode             = "awsvpc"=>network_mode             = "bridge"'
run "target_type"    'target_type = "ip"=>target_type = "instance"'
run "cpu に 300"     'cpu                      = "256"=>cpu                      = "300"'
rm -rf $W
