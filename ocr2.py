# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "transformers",
#     "torch",
#     "torchvision",
#     "pillow",
#     "marker-pdf",
# ]
# ///

import time

import torch
from transformers import AutoModelForImageTextToText, AutoProcessor

if torch.cuda.is_available():
    device = "cuda"  
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

start_time = time.time()

model = AutoModelForImageTextToText.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf")
model = model.to(device)
processor = AutoProcessor.from_pretrained("stepfun-ai/GOT-OCR-2.0-hf", use_fast=True)

# image = "https://huggingface.co/datasets/hf-internal-testing/fixtures_got_ocr/resolve/main/image_ocr.jpg"
# image = "https://i.sstatic.net/IiNz9.png"
image = "data/table.png"
inputs = processor(image, return_tensors="pt").to(device)

generate_ids = model.generate(
    **inputs,
    do_sample=False,
    tokenizer=processor.tokenizer,
    stop_strings="<|im_end|>",
    max_new_tokens=4096,
)

result = processor.decode(generate_ids[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
print(result)

end_time = time.time()
print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")