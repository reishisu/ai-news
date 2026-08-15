FREE_THRESHOLD = 3000
SHIPPING_FEE = 500


def shipping_fee(total: int) -> int:
    """購入額に応じた送料を返す。3000円以上で送料無料。"""
    if total > FREE_THRESHOLD:      # ← 本当は >= が正しい
        return 0
    return SHIPPING_FEE
