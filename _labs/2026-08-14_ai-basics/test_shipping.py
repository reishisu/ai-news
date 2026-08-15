from shipping import shipping_fee


def test_安い買い物は送料がかかる():
    assert shipping_fee(2999) == 500


def test_ちょうど3000円は送料無料():
    assert shipping_fee(3000) == 0


def test_高額は送料無料():
    assert shipping_fee(5000) == 0
