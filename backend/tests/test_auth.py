import pytest
from api.auth import create_access_token, verify_token, hash_password, verify_password


def test_password_hashing():
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False


def test_jwt_token_creation_and_validation():
    payload = {"user_id": "123", "email": "test@example.com", "role": "user"}
    token = create_access_token(payload)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = verify_token(token)
    assert decoded["user_id"] == "123"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "user"


def test_invalid_token():
    invalid_token = "invalid.token.string"
    
    with pytest.raises(Exception):
        verify_token(invalid_token)
