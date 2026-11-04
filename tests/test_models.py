from models import User


def test_user_password_hashing_behaves_correctly():
    user = User(username="tester")
    user.set_password("geheim123")

    assert user.password_hash != "geheim123"
    assert user.check_password("geheim123") is True
    assert user.check_password("falsch") is False