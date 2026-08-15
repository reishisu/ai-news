"""入口。dict を受けて dict を返す(HTTPハンドラ相当)。"""

from app import bill


def handle(req: dict) -> dict:
    """{"seats":int,"plan":str} -> {"status":int,"body":dict}"""
    seats = req.get("seats")
    plan = req.get("plan")
    if not isinstance(seats, int) or seats < 1:
        return {"status": 400, "body": {"error": "bad seats"}}
    if plan not in ("monthly", "annual"):
        return {"status": 400, "body": {"error": "bad plan"}}

    inv = bill.make_invoice(seats, plan)
    return {
        "status": 200,
        "body": {
            "seats": inv["seats"],
            "plan": inv["plan"],
            "amount_due": inv["total"],   # 税込
            "tax": inv["tax"],
        },
    }
