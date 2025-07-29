# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marker-pdf",
#     "mistralai",
#     "requests",
#     "python-dotenv",
# ]
# ///

import base64
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from mistralai import Mistral

load_dotenv()

# -------MISTRAL OCR-------
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

def ocr_mistral(file_path):
    """OCR using Mistral API - returns the extracted text"""
    base64_file = encode_image(file_path)
    if not base64_file:
        return None

    api_key = os.environ["MISTRAL_API_KEY"]
    client = Mistral(api_key=api_key)

    if str(file_path).endswith(".pdf"):
        document = {
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_file}"
        }
    else: 
        document = {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{base64_file}" 
        }

    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document=document,
            include_image_base64=True
        )
        return ocr_response.pages[0].markdown
    except Exception as e:
        print(f"Error with Mistral OCR: {e}")
        return None

#---------MARKER OCR-------
def ocr_marker(file_path):
    """OCR using Marker PDF converter - returns the extracted text"""
    try:
        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(file_path))
        text, _, images = text_from_rendered(rendered)
        return text
    except Exception as e:
        print(f"Error with Marker OCR: {e}")
        return None

def process_pdfs(ocr_function=ocr_mistral):
    """
    Process PDFs using the specified OCR function.
    
    Args:
        ocr_function: Function to use for OCR (ocr_mistral or ocr_marker)
    """
    # Get the data folder path
    data_folder = Path("data")
    
    # Find all PDF files in the data folder
    pdf_files = list(data_folder.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data folder")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"{i}. {pdf_file.name}")
    
    print(f"Using OCR function: {ocr_function.__name__}")
    
    # Dictionary to store the mapping
    file_mapping = {}
    successful_processes = 0
    
    # Process each PDF with the chosen OCR function
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\nProcessing {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
            # Extract text using the chosen OCR function
            text = ocr_function(pdf_file)
            
            if text:
                # Create output filename
                output_file = data_folder / f"text_{ocr_function.__name__}_{i}.md"
                
                # Save the markdown text
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                # Add to mapping
                file_mapping[f"text_{ocr_function.__name__}_{i}.md"] = pdf_file.name
                
                print(f"✓ Saved as {output_file.name}")
                successful_processes += 1
            else:
                print(f"✗ Failed to extract text from {pdf_file.name}")
                
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    
    # Save the mapping as JSON
    if file_mapping:
        mapping_file = data_folder / "file_mapping.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(file_mapping, f, indent=2, ensure_ascii=False)
        
        print(f"\nCompleted! Successfully processed {successful_processes}/{len(pdf_files)} PDF files.")
        print(f"File mapping saved to: {mapping_file.name}")
    else:
        print("\nNo files were successfully processed.")

if __name__ == '__main__':
    import time
    start_time = time.time()
    
    # Choose your OCR function here:
    # process_pdfs(ocr_marker)    # Use Marker (default)
    # process_pdfs(ocr_mistral)   # Use Mistral
    
    process_pdfs()  # Uses marker by default
    
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")