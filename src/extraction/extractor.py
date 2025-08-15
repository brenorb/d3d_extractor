import os

import dspy
from dotenv import load_dotenv

from src.extraction.signatures import ExamsWithoutResult, LabResultSignature

load_dotenv()


class LabDataExtractor:
    def __init__(self, model="openrouter/deepseek/deepseek-r1-0528-qwen3-8b:free"):
        self.lm = dspy.LM(
            model=model,
            api_base="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        dspy.configure(lm=self.lm)
        self.extract_lab_data = dspy.Predict(LabResultSignature)
        self.check_exams_without_result = dspy.Predict(ExamsWithoutResult)

    def extract(self, document_text: str) -> dict:
        prediction = self.extract_lab_data(document_text=document_text)
        return prediction.results

    def check_exams_without_result(self, document_text: str) -> dict:
        prediction = self.check_exams_without_result(document_text=document_text)
        return prediction.exams_without_result


if __name__ == "__main__":
    extractor = LabDataExtractor()
    with open("data/text_ocr_marker_2.md", "r") as file:
        text = file.read()

    pages = text.split("Pág.")

    print(extractor.check_exams_without_result(document_text=pages[2]))
    print(extractor.extract(document_text=pages[2]))
    print("=" * 100)
    print(pages[2])
