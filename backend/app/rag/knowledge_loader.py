"""One-off / re-runnable script to (re)index medical knowledge PDFs into Qdrant.

Usage:
    python -m app.rag.knowledge_loader --docs-dir ./medical_docs
"""
import argparse
import logging

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_index(docs_dir: str) -> int:
    loader = DirectoryLoader(docs_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    if not documents:
        logger.warning("No PDF documents found in %s", docs_dir)
        return 0

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    store = get_vector_store()
    store.add_documents(chunks)
    logger.info("Indexed %d chunks from %d documents into Qdrant", len(chunks), len(documents))
    return len(chunks)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", default="medical_docs")
    args = parser.parse_args()
    load_and_index(args.docs_dir)