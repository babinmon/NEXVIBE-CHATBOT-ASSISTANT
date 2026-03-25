from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "supersecretkey"   # move to env later
ALGORITHM = "HS256"

def create_token(username: str, role: str):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
