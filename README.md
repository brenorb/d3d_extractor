# Diabetes3D Lab Results Extractor

AI-powered medical lab results extraction from PDF documents using OCR and DSPy.

## Features

- **Multi-strategy OCR**: PyMuPDF, Marker, and Mistral OCR for robust text extraction
- **AI-powered extraction**: Uses DSPy to extract structured medical data from unstructured text
- **REST API**: FastAPI server for processing lab results
- **Batch processing**: Handle multiple PDFs simultaneously
- **Docker support**: Containerized deployment

## Quick Start

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run the pipeline on a single file
uv run run_pipeline.py

# Start the API server
uv run api/main.py
```

## API Usage

### Endpoints

- `GET /health` - Health check endpoint
- `POST /process-lab-results` - Process a single PDF file
- `POST /batch-process` - Process multiple PDF files (max 10)
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

### Examples

```bash
# Health check
curl http://localhost:8000/health

# Process a single PDF
curl -X POST "http://localhost:8000/process-lab-results" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@lab_results.pdf"

# Batch process multiple PDFs
curl -X POST "http://localhost:8000/batch-process" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@lab_results_1.pdf" \
  -F "files=@lab_results_2.pdf"
```

## Docker

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000` with docs at `/docs`.

---

**TODO**:
- [ ] Add logging
- [ ] Create tests
- [ ] Create automatic evals
- [ ] Optimize the pipeline, maybe save the NN