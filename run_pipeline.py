import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from tqdm import tqdm

from src.extraction.extractor import LabDataExtractor
from src.ocr.processor import OcrProcessor
from src.utils.file_utils import split_pdf_into_pages


def format_time_delta(seconds: float) -> str:
    """Format time delta to show minutes if >= 60 seconds, otherwise seconds."""
    if seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        return f"{seconds:.2f} seconds"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp to hh:mm:ss format."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d.%m.%y - %H:%M:%S")


def main(file_path: str):
    """
    Runs the full OCR and data extraction pipeline for a given file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    start_time = time.time()

    # --- Split PDF into pages ---
    print(f"{format_timestamp(start_time)} - Splitting PDF into pages...")
    pages = split_pdf_into_pages(file_path)
    split_time = time.time()
    print(f"PDF split into {len(pages)} pages in {format_time_delta(split_time - start_time)}.")

    # --- OCR Step ---
    print(f"{format_timestamp(split_time)} - Starting OCR process for each page...")
    ocr_processor = OcrProcessor()
    all_ocr_texts = []
    
    for page_path in tqdm(pages, desc="Processing pages for OCR"):
        ocr_result = ocr_processor.process(page_path)
        all_ocr_texts.append(ocr_result)
        
    ocr_time = time.time()
    print(f"{format_timestamp(ocr_time)} - OCR process finished in {format_time_delta(ocr_time - split_time)}.")

    # --- Extraction Step ---
    print("Starting data extraction...")
    extractor = LabDataExtractor()
    all_extracted_data = {}

    for ocr_result in tqdm(all_ocr_texts, desc="Processing OCR results"):
        for strategy in tqdm(ocr_result.keys(), desc="Processing strategies"):
            extracted_data = extractor.extract(ocr_result[strategy])
            if extracted_data:
                all_extracted_data.update(extracted_data)

    extract_time = time.time()
    print(f"{format_timestamp(extract_time)} - Extraction finished in {format_time_delta(extract_time - ocr_time)}.")


    # --- Save to JSON ---
    if all_extracted_data:
        patient_name = os.path.basename(file_path).split(" - ")[1] if " - " in os.path.basename(file_path) else "unknown_patient"
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_filename = f"lab_results_{patient_name.replace(' ', '_')}_{current_date}.json"
        
        output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, output_filename)

        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(all_extracted_data, f, ensure_ascii=False, indent=4)
        print(f"Results saved to {output_filepath}")


    end_time = time.time()
    print(f"{format_timestamp(end_time)} - Total pipeline time: {format_time_delta(end_time - start_time)}.")


if __name__ == "__main__":
    load_dotenv()
    # Make sure to set the TEST_FILE environment variable in your .env file
    test_file = os.getenv("TEST_FILE")
    if test_file:
        main(test_file)
    else:
        print("Please set the TEST_FILE environment variable in your .env file.")

