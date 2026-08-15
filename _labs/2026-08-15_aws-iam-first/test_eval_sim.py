#!/usr/bin/env python3
# eval_sim.py のおもちゃ実装が、公式ドキュメントに書かれた
# 判定順どおりに動くかを固定する。
# 「AWSが本当にこう動く」ことの証明ではない。あくまで
# 自分の書き写しが自分の意図どおりかを確認するテスト。
import pytest

from eval_sim import ALL, GET, OBJ, evaluate, stmt

REQ = {"action": GET, "resource": OBJ}


def run(identity, boundary=None, ctx=None):
    return evaluate(identity, boundary, REQ, ctx or {})[0]


def test_no_policy_is_deny():
    assert run([]) == "Deny"


def test_allow_only_is_allow():
    assert run([stmt("Allow", GET, ALL)]) == "Allow"


def test_explicit_deny_beats_allow():
    p = [stmt("Allow", GET, ALL), stmt("Deny", "s3:*", OBJ)]
    assert run(p) == "Deny"


def test_deny_order_does_not_matter():
    a, d = stmt("Allow", GET, ALL), stmt("Deny", "s3:*", OBJ)
    assert run([a, d]) == run([d, a]) == "Deny"


def test_boundary_must_also_allow():
    a = [stmt("Allow", GET, ALL)]
    assert run(a, [stmt("Allow", "s3:Get*", "*")]) == "Allow"
    assert run(a, [stmt("Allow", "dynamodb:*", "*")]) == "Deny"


def test_boundary_alone_grants_nothing():
    assert run([], [stmt("Allow", "s3:*", "*")]) == "Deny"


@pytest.mark.parametrize("mfa,want", [("true", "Allow"), ("false", "Deny")])
def test_condition_bool(mfa, want):
    p = [stmt("Allow", GET, ALL,
              {"Bool": {"aws:MultiFactorAuthPresent": "true"}})]
    assert run(p, ctx={"aws:MultiFactorAuthPresent": mfa}) == want


def test_missing_context_key_fails_condition():
    p = [stmt("Allow", GET, ALL,
              {"Bool": {"aws:MultiFactorAuthPresent": "true"}})]
    assert run(p, ctx={}) == "Deny"


def test_bucket_arn_does_not_cover_objects():
    # arn:aws:s3:::logs は object を含まない
    p = [stmt("Allow", GET, "arn:aws:s3:::logs")]
    assert run(p) == "Deny"
