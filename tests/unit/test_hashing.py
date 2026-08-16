from app.auth.hashing import hash_password, verify_password


def test_hash_password_does_not_return_plaintext():
    password = "password123"

    hashed = hash_password(password)

    assert hashed != password


def test_verify_password_correct_password():
    password = "password123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_wrong_password():
    hashed = hash_password("password123")

    assert verify_password("wrong-password", hashed) is False


def test_hash_password_produces_different_hashes():
    password = "password123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2