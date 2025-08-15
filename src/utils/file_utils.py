import base64
import os
from pathlib import Path

import fitz  # pymupdf


def get_pdf_page_count(pdf_path: str) -> int:
    """
    Returns the number of pages in a PDF file.
    Args:
        pdf_path: The path to the PDF file.
    Returns:
        The number of pages in the PDF file.
    """
    try:
        doc = fitz.open(pdf_path)
        page_count = doc.page_count
        doc.close()
        return page_count
    except Exception as e:
        print(f"Error opening or reading PDF file: {e}")
        return 0


def encode_image_to_base64(image_path: str) -> str | None:
    """Encode the image to base64.
    Args:
        image_path: The path to the image file.
    Returns:
        The base64 encoded string or None if an error occurs.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def split_pdf_into_pages(pdf_path: str, output_dir: str | None = None) -> list[str]:
    """
    Split a multipage PDF into individual single-page PDF files.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to save the split PDF files. If None, creates a subdirectory
                   next to the input file with '_pages' suffix
    
    Returns:
        List of paths to the created single-page PDF files
    
    Raises:
        FileNotFoundError: If the input PDF file doesn't exist
        Exception: If there's an error processing the PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Set up output directory
    if output_dir is None:
        pdf_path_obj = Path(pdf_path)
        output_dir = pdf_path_obj.parent / f"{pdf_path_obj.stem}_pages"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    created_files = []
    
    try:
        # Open the source PDF
        doc = fitz.open(pdf_path)
        
        # Get the base filename without extension
        base_name = Path(pdf_path).stem
        
        # Split each page into a separate PDF
        for page_num in range(doc.page_count):
            # Create a new PDF document for this page
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            # Create output filename with page number (1-indexed)
            output_filename = f"{base_name}_page_{page_num + 1:03d}.pdf"
            output_filepath = output_path / output_filename
            
            # Save the single-page PDF
            new_doc.save(str(output_filepath))
            new_doc.close()
            
            created_files.append(str(output_filepath))
            print(f"Created: {output_filepath}")
        
        doc.close()
        print(f"Successfully split {pdf_path} into {len(created_files)} pages")
        
    except Exception as e:
        # Clean up any partially created files on error
        for file_path in created_files:
            try:
                os.remove(file_path)
            except OSError:
                pass
        raise Exception(f"Error splitting PDF: {e}")
    
    return created_files


def split_pdf_and_get_first_page(pdf_path: str, output_dir: str | None = None) -> str:
    """
    Split a PDF and return the path to the first page only.
    Useful when you only need to process the first page of a multipage PDF.
    
    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to save the split PDF files. If None, creates a subdirectory
                   next to the input file with '_pages' suffix
    
    Returns:
        Path to the first page PDF file
    
    Raises:
        FileNotFoundError: If the input PDF file doesn't exist
        Exception: If there's an error processing the PDF or the PDF has no pages
    """
    created_files = split_pdf_into_pages(pdf_path, output_dir)
    
    if not created_files:
        raise Exception("PDF splitting resulted in no pages")
    
    return created_files[0]
