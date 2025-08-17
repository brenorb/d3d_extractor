import logging
import os
import tempfile
import time
from datetime import datetime
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.models import ErrorResponse, HealthResponse, ProcessingResult
from src.extraction.extractor import LabDataExtractor
from src.ocr.processor import OcrProcessor
from src.utils.file_utils import split_pdf_into_pages

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Diabetes3D Lab Results API",
    description="API for processing medical lab results from PDF documents using OCR and AI extraction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors (lazy loading)
_ocr_processor = None
_extractor = None


def get_ocr_processor() -> OcrProcessor:
    """Get or create OCR processor instance"""
    global _ocr_processor
    if _ocr_processor is None:
        logger.info("Initializing OCR processor...")
        _ocr_processor = OcrProcessor()
    return _ocr_processor


def get_extractor() -> LabDataExtractor:
    """Get or create lab data extractor instance"""
    global _extractor
    if _extractor is None:
        logger.info("Initializing lab data extractor...")
        _extractor = LabDataExtractor()
    return _extractor


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.post("/process-lab-results", response_model=ProcessingResult)
async def process_lab_results(file: UploadFile = File(...)):
    """
    Process uploaded PDF file and extract lab results
    
    - **file**: PDF file containing lab results
    
    Returns extracted medical data in JSON format
    """
    start_time = time.time()
    temp_files = []
    
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        logger.info(f"Processing file: {file.filename}")
        
        # Create temporary file for uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
            temp_files.append(temp_path)
        
        logger.info(f"Saved uploaded file to: {temp_path}")
        
        # Split PDF into pages
        logger.info("Splitting PDF into pages...")
        pages = split_pdf_into_pages(temp_path)
        temp_files.extend(pages)  # Track page files for cleanup
        logger.info(f"PDF split into {len(pages)} pages")
        
        # Process each page with OCR
        logger.info("Starting OCR process...")
        ocr_processor = get_ocr_processor()
        all_ocr_texts = []
        
        for i, page_path in enumerate(pages, 1):
            logger.info(f"Processing page {i}/{len(pages)}")
            ocr_result = ocr_processor.process(page_path)
            if ocr_result:
                all_ocr_texts.append(ocr_result)
        
        logger.info(f"OCR completed for {len(all_ocr_texts)} pages")
        
        # Extract lab data from OCR results
        logger.info("Starting data extraction...")
        extractor = get_extractor()
        all_extracted_data = {}
        
        for ocr_result in all_ocr_texts:
            for strategy_name, text in ocr_result.items():
                if text and text.strip():
                    logger.info(f"Extracting data using {strategy_name}")
                    try:
                        extracted_data = extractor.extract(text)
                        if extracted_data and isinstance(extracted_data, dict):
                            all_extracted_data.update(extracted_data)
                    except Exception as e:
                        logger.warning(f"Extraction failed for {strategy_name}: {e}")
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        return ProcessingResult(
            status="success",
            filename=file.filename,
            processed_at=datetime.now().isoformat(),
            results=all_extracted_data,
            processing_time=round(processing_time, 2),
            pages_processed=len(pages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during processing: {str(e)}"
        )
    
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")


@app.post("/batch-process", response_model=List[ProcessingResult])
async def batch_process_lab_results(files: List[UploadFile] = File(...)):
    """
    Process multiple PDF files in batch
    
    - **files**: List of PDF files containing lab results
    
    Returns list of extracted medical data for each file
    """
    if len(files) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files allowed per batch"
        )
    
    results = []
    for file in files:
        try:
            # Process each file individually
            result = await process_lab_results(file)
            results.append(result)
        except Exception as e:
            # Add error result for failed files
            results.append(ProcessingResult(
                status="error",
                filename=file.filename or "unknown",
                processed_at=datetime.now().isoformat(),
                results={"error": str(e)},
                processing_time=0,
                pages_processed=0
            ))
    
    return results


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            details={"error": str(exc)}
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
