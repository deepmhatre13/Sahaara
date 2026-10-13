import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import ChatAsk, ChatAskResponse, ChatMessageOut
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatAskResponse)
def ask(
    payload: ChatAsk,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, payload.user_id)
    result = chat_service.ask(db, current_user.id, payload.session_id, payload.message)
    return result


@router.get("/session/{session_id}/messages", response_model=list[ChatMessageOut])
def messages(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return chat_service.list_messages(db, session_id, user_id=current_user.id)