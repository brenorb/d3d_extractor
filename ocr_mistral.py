# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mistralai",
#     "requests",
#     "python-dotenv",
#     "dspy-ai",
# ]
# ///

import base64
import os
import time

import dspy
from dotenv import load_dotenv
from mistralai import Mistral

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


def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

start_time = time.time()
# Path to your image
file_path = "data/Lipoproteina A  06_06_2024 - Maria Emenilza Memoria - Emma.pdf"

# Getting the base64 string
base64_file = encode_image(file_path)

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

if file_path.endswith(".pdf"):
    document = {
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_file}"
    }
else: 
    document={
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_file}" 
    },

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document=document,
    include_image_base64=True
)

print("result:", ocr_response.pages[0].markdown)

ocr_time = time.time()
print(f"Time taken for ocr: {ocr_time - start_time:.2f} seconds")

extract_lab_data = dspy.Predict(LabResultSignature)
print(extract_lab_data(document_text=ocr_response.pages[0].markdown))
extract_time = time.time()
print(f"Time taken for extract: {extract_time - ocr_time:.2f} seconds")


end_time = time.time()
print(f"Time taken: {end_time - start_time:.2f} seconds")





