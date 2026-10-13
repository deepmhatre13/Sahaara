import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are a health literacy assistant for an elder-care platform.
Your role is to explain health topics, symptoms, and general first-aid steps in plain
language, using the reference material provided below.

Rules:
- You are not a doctor and must never provide a diagnosis.
- Never claim certainty about what condition the user has.
- Always encourage the user to consult a qualified healthcare professional for any
  diagnosis or treatment decision.
- If the described situation sounds like a medical emergency (e.g. chest pain,
  difficulty breathing, stroke symptoms, severe bleeding, loss of consciousness),
  clearly and calmly recommend contacting emergency services or the SOS button
  immediately, before anything else.
- Base your answer primarily on the reference material. If the reference material
  does not cover the question, say so honestly rather than inventing facts.
- Keep the tone warm, clear, and appropriate for an elderly reader or their caregiver.
"""


class MedicalRAGPipeline:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_chat_model,
            google_api_key=settings.gemini_api_key,
            temperature=0.2,
        )
        self._store = None

    def _get_store(self):
        if self._store is None:
            self._store = get_vector_store()
        return self._store

    def answer(self, question: str, history: list[str] | None = None) -> dict:
        history = history or []
        store = self._get_store()

        try:
            docs = store.similarity_search(question, k=4)
        except Exception as exc:  # noqa: BLE001
            logger.error("Qdrant retrieval failed: %s", exc)
            docs = []

        context = "\n\n".join(d.page_content for d in docs) or "No reference material retrieved."
        sources = list({d.metadata.get("source", "unknown") for d in docs})

        history_block = "\n".join(history[-10:])
        prompt = f"""{SYSTEM_INSTRUCTIONS}

--- Reference Material ---
{context}

--- Conversation So Far ---
{history_block}

--- User Question ---
{question}

Respond helpfully and safely, following the rules above.
"""
        response = self.llm.invoke(prompt)
        return {"response": response.content, "sources": sources}


_pipeline: MedicalRAGPipeline | None = None


def get_rag_pipeline() -> MedicalRAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = MedicalRAGPipeline()
    return _pipeline