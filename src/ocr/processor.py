from typing import Type

from src.ocr.strategies import (
    MarkerOcrStrategy,
    MistralOcrStrategy,
    OcrStrategy,
    PyMuPdfOcrStrategy,
)


class OcrProcessor:
    def __init__(self):
        self.strategies: dict[str, list[Type[OcrStrategy]]] = {
            "pdf": [PyMuPdfOcrStrategy, MarkerOcrStrategy, MistralOcrStrategy],
            "image": [MistralOcrStrategy],
        }

    def process(self, file_path: str) -> str:
        file_type = self._get_file_type(file_path)
        if not file_type:
            print(f"Unsupported file type for: {file_path}")
            return ""

        combined_text = ""
        for strategy_class in self.strategies.get(file_type, []):
            strategy_instance = strategy_class()
            print(f"Running {strategy_class.__name__}...")
            combined_text += f"\n\n--- OCR Result from {strategy_class.__name__} ---\n"
            combined_text += strategy_instance.execute(file_path)

        return combined_text

    def _get_file_type(self, file_path: str) -> str | None:
        if file_path.lower().endswith(".pdf"):
            return "pdf"
        elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            return "image"
        return None
