# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marker-pdf",
# ]
# ///

import json
from pathlib import Path

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


def process_pdfs():
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
    
    # Initialize the PDF converter
    converter = PdfConverter(artifact_dict=create_model_dict())
    
    # Dictionary to store the mapping
    file_mapping = {}
    
    # Process each PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\nProcessing {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
            # Convert PDF to markdown
            rendered = converter(str(pdf_file))
            text, _, images = text_from_rendered(rendered)
            
            # Create output filename
            output_file = data_folder / f"text_{i}.md"
            
            # Save the markdown text
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Add to mapping
            file_mapping[f"text_{i}.md"] = pdf_file.name
            
            print(f"✓ Saved as {output_file.name}")
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    
    # Save the mapping as JSON
    mapping_file = data_folder / "file_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(file_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\nCompleted! Processed {len(pdf_files)} PDF files.")
    print(f"File mapping saved to: {mapping_file.name}")

if __name__ == '__main__':
    import time
    start_time = time.time()
    process_pdfs() 
    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")