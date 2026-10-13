from app.integrations.ocr.base import OCRProvider


class MockOCRProvider(OCRProvider):
    """Used when no OCR provider is configured, so uploads still work in dev."""

    def extract_text(self, file_path: str) -> str:
        return (
            "[Mock OCR] No OCR provider configured. This is placeholder text "
            f"standing in for the content of '{file_path}'."
        )