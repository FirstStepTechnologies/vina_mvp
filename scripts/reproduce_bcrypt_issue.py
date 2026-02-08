from vina_backend.core.security import get_password_hash
from passlib.context import CryptContext

try:
    print("Testing 'secure_password_123'...")
    h = get_password_hash("secure_password_123")
    print(f"Success: {h[:10]}...")
except Exception as e:
    print(f"Failed with normal password: {e}")

try:
    long_pw = "x" * 73
    print(f"Testing 73 char password...")
    h = get_password_hash(long_pw)
    print(f"Success long: {h[:10]}...")
except Exception as e:
    print(f"Failed with long password: {e}")
