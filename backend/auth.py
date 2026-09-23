import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User

SESSION_MINUTES = 15
LOCK_MINUTES = 5
MAX_FAILED = 3
TOKEN_SECRET = "ccms-local-dev-secret"

security = HTTPBearer(auto_error=False)


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    check = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return hmac.compare_digest(check, digest)


def create_token(username: str) -> str:
    expires = (datetime.utcnow() + timedelta(minutes=SESSION_MINUTES)).isoformat()
    payload = f"{username}|{expires}|{secrets.token_hex(8)}"
    sig = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{sig}"


def parse_token(token: str) -> str:
    parts = token.split("|")
    if len(parts) != 4:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    username, expires, _nonce, sig = parts
    payload = f"{username}|{expires}|{_nonce}"
    expected = hmac.new(TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    try:
        exp = datetime.fromisoformat(expires)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")
    if datetime.utcnow() > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired after 15 minutes of inactivity. Please log in again.",
        )
    return username


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    username = parse_token(creds.credentials)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    now = datetime.utcnow()
    if user.last_activity and now - user.last_activity > timedelta(minutes=SESSION_MINUTES):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired after 15 minutes of inactivity. Please log in again.",
        )
    user.last_activity = now
    db.commit()
    db.refresh(user)
    return user
