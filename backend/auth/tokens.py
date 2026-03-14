from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from backend.core.config import settings

ALGORITHM = settings.jwt_algorithm
SECRET = settings.secret_key


def _build_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,  # subject — always the user id as a string
        "type": token_type,  # "access" or "refresh" — checked on decode
        "iat": now,  # issued-at — useful for audit logs
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _build_token(
        subject=str(user_id),
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> str:
    return _build_token(
        subject=str(user_id),
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str) -> int:
    """
    Decode and validate a JWT.
    Returns the user_id (int) on success.
    Raises ValueError with a safe message on any failure.
    """
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")

    if payload.get("type") != expected_type:
        raise ValueError(f"Expected {expected_type} token")

    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Token missing subject")

    return int(sub)
