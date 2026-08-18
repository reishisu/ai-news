FREE = 3000  # この額以上は送料無料
FEE = 500    # それ未満の送料


def shipping(subtotal: int) -> int:
    """送料を返す。負の金額は ValueError。"""
    if subtotal < 0:
        raise ValueError("負の金額")
    if subtotal >= FREE:
        return 0
    return FEE
