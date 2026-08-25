from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import handle_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, current_user: CurrentUser = Depends(get_current_user)) -> ChatResponse:
    # Role is taken from the verified session token, never trusted from the
    # request body, so the client cannot self-elevate access by claiming a
    # different role.
    return handle_chat(question=payload.question, role=current_user.role)
