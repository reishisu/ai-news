"""
run_contract_test.py
契約テストを実行するスクリプト。

1. consumer_expectation.json が契約(schema.json)に沿っているか
2. provider_v1.search() の出力が契約に沿っているか
3. provider_v2_broken.search() の出力が契約に沿っているか
   (故意に契約を破っているので、ここは失敗するはず)

出力は幅380pxのスマホで読める行の長さ
(全角20字/半角40字程度)に収めている。
"""

import json
import jsonschema

import provider_v1
import provider_v2_broken


def load_schema():
    with open("schema.json", encoding="utf-8") as f:
        return json.load(f)


def check(label: str, payload: dict, schema: dict) -> None:
    try:
        jsonschema.validate(instance=payload, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        first_line = str(e).split("\n")[0]
        # jsonschemaの1行目は長いので、要点だけ抜く
        short = first_line
        if len(short) > 40:
            short = short[:37] + "..."
        print(f"[NG] {label}")
        print(f"  {short}")
        return
    print(f"[OK] {label}")


def main() -> None:
    schema = load_schema()

    print("契約テスト: GET /api/search")
    print("-" * 24)

    with open("consumer_expectation.json", encoding="utf-8") as f:
        consumer_payload = json.load(f)
    check("consumer側の期待値", consumer_payload, schema)

    v1_payload = provider_v1.search("")
    check("provider v1", v1_payload, schema)

    v2_payload = provider_v2_broken.search("")
    check("provider v2(破壊的変更)", v2_payload, schema)


if __name__ == "__main__":
    main()
