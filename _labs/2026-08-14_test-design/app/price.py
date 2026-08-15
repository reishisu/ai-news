"""単価と席数ボリューム割引。純粋関数だけ。"""

PRICE = 1000  # 1席あたり月額(税抜)


def volume_discount_rate(seats: int) -> float:
    """1-9席=0%, 10-49席=10%, 50席以上=20%"""
    if seats < 1:
        raise ValueError("seats must be >= 1")
    if seats >= 50:
        return 0.20
    if seats >= 10:
        return 0.10
    return 0.0


def monthly_subtotal(seats: int) -> int:
    """月額小計(税抜)。円未満切り捨て。"""
    rate = volume_discount_rate(seats)
    gross = PRICE * seats
    return int(gross * (1 - rate))
