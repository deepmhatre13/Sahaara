import uuid

from sqlalchemy.orm import Session

from app.models.chat import ChatSession, ChatMessage
from app.agents.health_assistant import get_health_assistant


def get_or_create_session(db: Session, user_id: uuid.UUID, session_id: uuid.UUID | None) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session:
            return session
    session = ChatSession(user_id=user_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def ask(db: Session, user_id: uuid.UUID, session_id: uuid.UUID | None, message: str) -> dict:
    session = get_or_create_session(db, user_id, session_id)

    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [f"{row.role}: {row.content}" for row in history_rows]

    user_msg = ChatMessage(session_id=session.id, role="user", content=message)
    db.add(user_msg)
    db.commit()

    agent = get_health_assistant()
    result = agent.respond(message, history)

    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["response"],
        sources=", ".join(result["sources"]) if result.get("sources") else None,
    )
    db.add(assistant_msg)
    db.commit()

    return {"session_id": session.id, "response": result["response"], "sources": result.get("sources", [])}


def list_messages(db: Session, session_id: uuid.UUID, user_id: uuid.UUID | None = None) -> list[ChatMessage]:
    if user_id is not None:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if not session:
            return []
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )