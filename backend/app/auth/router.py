from fastapi import APIRouter, HTTPException, status

from app.auth.schemas import LoginRequest, LoginResponse
from app.auth.users import get_user
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.rbac.access_matrix import get_accessible_collections

router = APIRouter(tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = get_user(payload.username)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(data={"sub": payload.username, "role": user["role"]})

    return LoginResponse(
        access_token=token,
        expires_in_minutes=settings.access_token_expire_minutes,
        role=user["role"],
        display_name=user["display_name"],
        department=user["department"],
        accessible_collections=get_accessible_collections(user["role"]),
    )
