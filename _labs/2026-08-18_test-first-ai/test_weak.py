from shipping import shipping


def test_5000_free():
    assert shipping(5000) == 0
