try:
    from jose import jwt, JWTError
    from passlib.context import CryptContext
    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
