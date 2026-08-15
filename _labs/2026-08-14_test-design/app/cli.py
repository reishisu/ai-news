"""E2E 用の実行可能な入口。JSON を argv で受け、JSON を stdout に出す。"""

import json
import sys

from app import api


def main(argv):
    req = json.loads(argv[1])
    res = api.handle(req)
    sys.stdout.write(json.dumps(res["body"], ensure_ascii=False))
    return 0 if res["status"] == 200 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv))
