#!/bin/bash
# 同じモデルにある networkMode の説明文を38桁で折る。
python3 - <<'PY' | sed -e 's/<[^>]*>//g' | tr -s ' ' | fold -s -w 38 | head -9
from awscli.botocore.session import get_session
m = get_session().get_service_model('ecs')
s = m.operation_model('RegisterTaskDefinition').input_shape
print(s.members['networkMode'].documentation)
PY
