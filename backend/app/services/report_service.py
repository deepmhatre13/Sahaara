import os
import uuid
import logging

from sqlalchemy.orm import Session
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.models.medical_document import MedicalDocument
from app.integrations.ocr.mistral_provider import build_ocr_provider

logger = logging.getLogger(__name__)

EXPLAIN_PROMPT = """You are a health literacy assistant helping an elderly patient (or their
caregiver) understand a medical report. You are not a doctor and must not diagnose.

Report text (may contain OCR noise):
---
{report_text}
---

Explain in plain, reassuring language:
- What kinds of information appear to be in this report
- Anything that looks like it may be worth discussing with a doctor (flag gently,
  do not alarm)
- General lifestyle notes if relevant
- A clear reminder to confirm everything with a qualified healthcare professional

Respond in clear markdown.
"""


def analyze_report(db: Session, user_id: uuid.UUID, file_path: str, filename: str) -> MedicalDocument:
    settings = get_settings()
    ocr = build_ocr_provider()
    extracted_text = ocr.extract_text(file_path)

    explanation = None
    if settings.gemini_api_key:
        llm = ChatGoogleGenerativeAI(
            model=settings.gemini_chat_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.2,
        )
        response = llm.invoke(EXPLAIN_PROMPT.format(report_text=extracted_text))
        explanation = response.content
    else:
        logger.warning("GEMINI_API_KEY not set; skipping explanation generation")

    doc = MedicalDocument(
        user_id=user_id,
        filename=filename,
        extracted_text=extracted_text,
        explanation=explanation,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        os.remove(file_path)
    except OSError:
        pass

    return doc


def list_documents(db: Session, user_id: uuid.UUID) -> list[MedicalDocument]:
    return (
        db.query(MedicalDocument)
        .filter(MedicalDocument.user_id == user_id)
        .order_by(MedicalDocument.created_at.desc())
        .all()
    )