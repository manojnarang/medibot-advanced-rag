from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    role: str
    display_name: str
    department: str
    accessible_collections: list[str]


class CurrentUser(BaseModel):
    username: str
    role: str
    display_name: str
    department: str
