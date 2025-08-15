import os
from abc import ABC, abstractmethod

import fitz
from dotenv import load_dotenv
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from mistralai import Mistral

from src.utils.file_utils import encode_image_to_base64

load_dotenv()


class OcrStrategy(ABC):
    @abstractmethod
    def execute(self, file_path: str) -> str:
        """
        Performs OCR on the given file and returns the extracted text.
        """
        pass


class MarkerOcrStrategy(OcrStrategy):
    def execute(self, file_path: str) -> str:
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(file_path)
        text, _, _ = text_from_rendered(rendered)
        # TODO: Handle multiple pages better
        return text.split("2/26")[0]


class MistralOcrStrategy(OcrStrategy):
    def __init__(self):
        self.client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    def execute(self, file_path: str) -> str:
        base64_file = encode_image_to_base64(file_path)
        if not base64_file:
            return ""

        if file_path.lower().endswith(".pdf"):
            document = {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64_file}",
            }
        else:
            document = {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_file}",
            }

        ocr_response = self.client.ocr.process(
            model="mistral-ocr-latest", document=document, include_image_base64=True
        )
        return ocr_response.pages[0].markdown


class PyMuPdfOcrStrategy(OcrStrategy):
    def execute(self, file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
                break  # Only first page for now
            doc.close()
            return text
        except Exception as e:
            print(f"Error opening or reading PDF file with PyMuPDF: {e}")
            return ""
