from lib.auth import login, USERS


def test_login_valid_user():
    result = login("user", "user")
    assert result is not None
    assert result["username"] == "user"
    assert result["role"] == "USER"
    assert "password" not in result


def test_login_valid_admin():
    result = login("admin", "admin")
    assert result is not None
    assert result["username"] == "admin"
    assert result["role"] == "ADMIN"


def test_login_invalid_password():
    result = login("user", "wrong")
    assert result is None


def test_login_invalid_username():
    result = login("unknown", "password")
    assert result is None
