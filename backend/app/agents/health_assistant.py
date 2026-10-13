"""Thin orchestration wrapper around the RAG pipeline for the /api/chat route.
Kept separate from the pipeline so Part 2 (LangGraph) can later replace only
this layer without touching retrieval/vector-store code."""

from app.rag.pipeline import get_rag_pipeline


class HealthAssistantAgent:
    def __init__(self) -> None:
        self.pipeline = get_rag_pipeline()

    def respond(self, question: str, history: list[str]) -> dict:
        return self.pipeline.answer(question, history)


def get_health_assistant() -> HealthAssistantAgent:
    return HealthAssistantAgent()