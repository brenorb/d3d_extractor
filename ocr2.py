# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "transformers",
#     "torch",
#     "torchvision",
#     "pillow",
#     "marker-pdf",
#     "dspy-ai",
#     "pyarrow<15.0.0",
#     "datasets>=2.14.0",
#     "python-dotenv",
#     "numpy<2.0.0",
# ]
# ///

import os
import time

import dspy
import torch
from dotenv import load_dotenv
from transformers import AutoModelForImageTextToText, AutoProcessor

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


if torch.cuda.is_available():
    device = "cuda"  
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")
start_time = time.time()

model = AutoModelForImageTextToText.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf")
model = model.to(device)
processor = AutoProcessor.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf", use_fast=True)

# image = "https://huggingface.co/datasets/hf-internal-testing/fixtures_got_ocr/resolve/main/image_ocr.jpg"
# image = "https://i.sstatic.net/IiNz9.png"
image = "data/blank_table.png"
inputs = processor(image, return_tensors="pt").to(device)

generate_ids = model.generate(
    **inputs,
    do_sample=False,
    tokenizer=processor.tokenizer,
    stop_strings="<|im_end|>",
    max_new_tokens=4096,
)

result = processor.decode(generate_ids[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
extract_lab_data = dspy.Predict(LabResultSignature)

print(result)
print("--------------------------------")
print(extract_lab_data(document_text=result))

end_time = time.time()
print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")