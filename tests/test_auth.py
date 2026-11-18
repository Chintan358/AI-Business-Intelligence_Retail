import pytest
from backend.services.auth_service import get_password_hash, verify_password, create_access_token, decode_access_token

def test_password_hashing():
    pwd = "SecurePassword@123"
    h = get_password_hash(pwd)
    assert h != pwd
    assert verify_password(pwd, h) is True
    assert verify_password("WrongPassword", h) is False

def test_jwt_tokens():
    payload = {"sub": "test@retailbi.com", "role": "manager", "id": 42}
    token = create_access_token(payload)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test@retailbi.com"
    assert decoded["role"] == "manager"
    assert decoded["id"] == 42
