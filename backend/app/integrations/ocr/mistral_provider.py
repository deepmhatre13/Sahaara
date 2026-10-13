import base64
import io
import logging

from PIL import Image

from app.core.config import get_settings
from app.integrations.ocr.base import OCRProvider
from app.integrations.ocr.mock_provider import MockOCRProvider

logger = logging.getLogger(__name__)


class MistralOCRProvider(OCRProvider):
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    def _get_client(self):
        if self._client is None:
            from mistralai import Mistral

            if not self.settings.mistral_api_key:
                raise RuntimeError("MISTRAL_API_KEY is not configured")
            self._client = Mistral(api_key=self.settings.mistral_api_key)
        return self._client

    def _prepare_image(self, file_path: str) -> str:
        img = Image.open(file_path).convert("RGB")
        max_width = 1000
        if img.width > max_width:
            ratio = max_width / float(img.width)
            img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def extract_text(self, file_path: str) -> str:
        client = self._get_client()
        base64_image = self._prepare_image(file_path)
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"},
        )
        text = str(response)
        if not text.strip():
            raise RuntimeError("OCR result is empty")
        return text


def build_ocr_provider() -> OCRProvider:
    settings = get_settings()
    if settings.ocr_provider == "mistral":
        return MistralOCRProvider()
    return MockOCRProvider()