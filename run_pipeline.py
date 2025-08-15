import os
import time
from pprint import pprint

from dotenv import load_dotenv

from src.extraction.extractor import LabDataExtractor
from src.ocr.processor import OcrProcessor


def main(file_path: str):
    """
    Runs the full OCR and data extraction pipeline for a given file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    start_time = time.time()

    # --- OCR Step ---
    print("Starting OCR process...")
    ocr_processor = OcrProcessor()
    ocr_text = ocr_processor.process(file_path)
    ocr_time = time.time()
    print(f"OCR process finished in {ocr_time - start_time:.2f} seconds.")
    # print("\n--- Combined OCR Text ---")
    # print(ocr_text)
    # print("-------------------------\n")

    # --- Extraction Step ---
    print("Starting data extraction...")
    extractor = LabDataExtractor()
    extracted_data = extractor.extract(ocr_text)
    extract_time = time.time()
    print(f"Extraction finished in {extract_time - ocr_time:.2f} seconds.")

    print("\n--- Extracted Lab Data ---")
    pprint(extracted_data)
    print("--------------------------\n")

    end_time = time.time()
    print(f"Total pipeline time: {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    load_dotenv()
    # Make sure to set the TEST_FILE environment variable in your .env file
    test_file = os.getenv("TEST_FILE")
    if test_file:
        main(test_file)
    else:
        print("Please set the TEST_FILE environment variable in your .env file.")

