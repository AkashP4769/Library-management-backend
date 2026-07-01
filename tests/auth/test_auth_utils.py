import pytest
from auth.utils import hash_password, verify_password

@pytest.fixture
def hashed():
    return hash_password("Secret123")

def test_verify_password_accepts_correct_password(hashed):
    assert verify_password("Secret123", hashed)

def test_verify_password_rejects_wrong_password(hashed):
    assert not verify_password("wrong-pass", hashed)