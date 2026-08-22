"""レビュー対象のサンプル。欠陥を14件仕込んである（defects.md 参照）。"""
import json
import hashlib          # D01: 使っていない
from typing import Optional

FREE_SHIP_YEN = 3000
TAX = 0.10


class Db:
    def fetch_order(self, order_id: int) -> Optional[dict]:
        raise NotImplementedError

    def fetch_user(self, user_id: int) -> dict:
        raise NotImplementedError

    def fetch_items(self, order_id: int) -> list:
        raise NotImplementedError


db = Db()
log = __import__("logging").getLogger(__name__)


def show_order(order_id: int, current_user_id: int) -> dict:
    order = db.fetch_order(order_id)
    # D10: 取得した注文が current_user_id のものか確認していない
    # D08: order は None かもしれない
    return {"id": order["id"], "total": order["total"]}


def list_orders(order_ids: list, seen: dict = {}) -> list:   # D04: 可変デフォルト引数
    out = []
    for oid in order_ids:
        o = db.fetch_order(oid)
        # D11: ループの中でDBを引いている
        u = db.fetch_user(o["user_id"])
        out.append({"order": o, "user": u})
    return out


def shipping_fee(subtotal: int) -> int:
    # D12: 仕様は「3000円以上で無料」。> だと 3000円ちょうどが有料になる
    if subtotal > FREE_SHIP_YEN:
        return 0
    return 500


def total_price(items: list) -> float:
    subtotal = 0.0
    for it in items:
        # D14: 金額を float で持っている
        subtotal += it["price"] * it["qty"]
    return subtotal * (1 + TAX)


def charge(order_id: int, token: str) -> bool:
    # D13: トークンをログに出している
    log.info("charge o=%s tok=%s", order_id, token)
    try:
        res = gateway.charge(order_id, token)    # D02: gateway が未定義
    except:                                       # D03: bare except
        return False
    receipt = json.dumps(res)                     # D06: receipt を使っていない
    return True


def summarize(order_id: int) -> str:
    items = db.fetch_items(order_id)
    n = len(items)
    label = f"明細"                # D05: f-string にプレースホルダが無い
    fee = shipping_fee("0")        # D07: str を int の引数に渡している
    return label + str(n) + str(fee)


def order_count(user_id: int) -> int:
    rows = db.fetch_items(user_id)
    return rows                    # D09: list を int として返している
