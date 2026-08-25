import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.schemas import CurrentUser
from app.auth.users import get_user
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme)) -> CurrentUser:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate session token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise unauthorized
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        raise unauthorized

    username = payload.get("sub")
    user = get_user(username) if username else None
    if not user:
        raise unauthorized

    return CurrentUser(
        username=username,
        role=user["role"],
        display_name=user["display_name"],
        department=user["department"],
    )
