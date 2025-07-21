# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "dspy-ai",
#     "marker-pdf",
# ]
# ///

import os
import time

import dspy
from dotenv import load_dotenv
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

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


if __name__ == '__main__':
    start_time = time.time()

    # Convert PDF to Markdown
    converter = PdfConverter(artifact_dict=create_model_dict())
    rendered = converter(os.getenv("TEST_FILE"))
    text, _, images = text_from_rendered(rendered)

    primeira_pagina = text.split("2/26")[0]
    # Print the Markdown
    # print(primeira_pagina)

    extract_lab_data = dspy.Predict(LabResultSignature)
    prediction = extract_lab_data(document_text=primeira_pagina)

    print("--- Extracted Lab Data ---")
    print(prediction.results)
    print("--------------------------\n")

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if elapsed_time > 60:
        minutes = elapsed_time / 60
        print(f"\nTotal execution time: {minutes:.2f} minutes")
    else:
        print(f"\nTotal execution time: {elapsed_time:.2f} seconds")