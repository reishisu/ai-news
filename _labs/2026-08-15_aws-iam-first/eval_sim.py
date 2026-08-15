#!/usr/bin/env python3
"""IAMの判定順を目で見るためのおもちゃ実装。

AWSの本物のエンジンではない。公式ドキュメント
"How AWS enforcement code logic evaluates requests to
allow or deny access" に書かれた順序
  1. 明示的なDenyがあれば Deny
  2. どこかに明示的なAllowが無ければ Deny(暗黙)
  3. アクセス許可境界があれば、そこでもAllowが要る
を、単一アカウント・アイデンティティベースのみに
絞って自分で書き写しただけのもの。
条件(Condition)は Bool 演算子だけ実装している。
"""
import fnmatch


def matches(pattern, value):
    if isinstance(pattern, str):
        pattern = [pattern]
    return any(fnmatch.fnmatchcase(value, p) for p in pattern)


def cond_ok(cond, ctx):
    for op, kv in (cond or {}).items():
        if op != "Bool":
            raise NotImplementedError(f"未実装の演算子: {op}")
        for k, want in kv.items():
            got = ctx.get(k)
            if got is None:
                return False
            if str(got).lower() != str(want).lower():
                return False
    return True


def scan(policies, req, ctx):
    """(明示Denyがあるか, 明示Allowがあるか)"""
    deny = allow = False
    for pol in policies:
        for st in pol.get("Statement", []):
            if not matches(st["Action"], req["action"]):
                continue
            if not matches(st["Resource"], req["resource"]):
                continue
            if not cond_ok(st.get("Condition"), ctx):
                continue
            if st["Effect"] == "Deny":
                deny = True
            elif st["Effect"] == "Allow":
                allow = True
    return deny, allow


def evaluate(identity, boundary, req, ctx):
    d, a = scan(identity, req, ctx)
    if d:
        return "Deny", "明示的なDeny"
    if boundary is not None:
        bd, ba = scan(boundary, req, ctx)
        if bd:
            return "Deny", "境界の明示的なDeny"
        if not ba:
            return "Deny", "境界が許可していない"
    if not a:
        return "Deny", "暗黙のDeny(許可が無い)"
    return "Allow", "許可あり・拒否なし"


def stmt(effect, action, resource, cond=None):
    s = {"Effect": effect, "Action": action, "Resource": resource}
    if cond:
        s["Condition"] = cond
    return {"Version": "2012-10-17", "Statement": [s]}


OBJ = "arn:aws:s3:::logs/report.csv"
ALL = "arn:aws:s3:::logs/*"
GET = "s3:GetObject"

read_ok = stmt("Allow", GET, ALL)
deny_csv = stmt("Deny", "s3:*", OBJ)
mfa_only = stmt("Allow", GET, ALL,
                {"Bool": {"aws:MultiFactorAuthPresent": "true"}})
boundary_ro = stmt("Allow", "s3:Get*", "*")
boundary_none = stmt("Allow", "dynamodb:*", "*")

CASES = [
    ("何も付けない", [], None, {}),
    ("読取Allowだけ", [read_ok], None, {}),
    ("Allow+Deny", [read_ok, deny_csv], None, {}),
    ("境界:s3:Get*", [read_ok], [boundary_ro], {}),
    ("境界:dynamodbのみ", [read_ok], [boundary_none], {}),
    ("MFA必須/MFAなし", [mfa_only], None,
     {"aws:MultiFactorAuthPresent": "false"}),
    ("MFA必須/MFAあり", [mfa_only], None,
     {"aws:MultiFactorAuthPresent": "true"}),
]

REQ = {"action": GET, "resource": OBJ}


def main():
    print(f"要求 {GET}")
    print("対象 logs/report.csv")
    print("-" * 38)
    for name, ident, bnd, ctx in CASES:
        res, why = evaluate(ident, bnd, REQ, ctx)
        print(f"{name}")
        print(f"  -> {res} : {why}")
    print("-" * 38)


if __name__ == "__main__":
    main()
