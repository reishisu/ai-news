#!/bin/bash
# AWS CLI が実際に読む ECS API モデルから列挙値を出す。
python3 - <<'PY'
from awscli.botocore.session import get_session
m = get_session().get_service_model('ecs')
for n in ('NetworkMode','Compatibility','LaunchType'):
    print(n + ':')
    for v in m.shape_for(n).enum:
        print('  ' + v)
PY
