# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "markitdown[pdf]",
#     "dspy-ai",
#     "openai",
#     "python-dotenv",
# ]
# ///

import glob
import os

import dspy
from dotenv import load_dotenv
from markitdown import MarkItDown

load_dotenv()

lm = dspy.LM(
    model="openrouter/deepseek/deepseek-r1-0528-qwen3-8b:free",
    # model="openrouter/moonshotai/kimi-dev-72b:free",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

dspy.configure(lm=lm)


# 1. Define the signature for the task.
class LabResultSignature(dspy.Signature):
    """Extract result information from a lab result document."""

    document_text = dspy.InputField(desc="The full text of a lab result PDF.")
    results: dict[str, str] = dspy.OutputField(
        desc="The results of the lab test. The key is the name of the test and the value is the result. "
        "The result can be something like 'Inferior a 7 nmol/L' or 'Desprezível' or just regular number with units."
    )


def main() -> None:
    md = MarkItDown(enable_plugins=False)
    extract_lab_data = dspy.Predict(LabResultSignature)

    for pdf_path in glob.glob("data/*.pdf"):
        print(f"--- Processing: {pdf_path} ---")
        result = md.convert(pdf_path)
        document_text = result.text_content

        prediction = extract_lab_data(document_text=document_text)

        print("--- Extracted Lab Data ---")
        print(prediction.results)
        print("--------------------------\n")


if __name__ == "__main__":
    main()
