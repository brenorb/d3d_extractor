# Diabetes3D Lab Results API

A FastAPI-based service for processing medical lab results from PDF documents using OCR and AI extraction.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run the API:**
   ```bash
   uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc
   - Health check: http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually:**
   ```bash
   docker build -t diabetes3d-api .
   docker run -p 8000:8000 --env-file .env diabetes3d-api
   ```

## 📚 API Endpoints

### `POST /process-lab-results`
Process a single PDF file and extract lab results.

**Request:**
- File upload (multipart/form-data)
- Content-Type: `multipart/form-data`

**Response:**
```json
{
  "status": "success",
  "filename": "lab_results.pdf",
  "processed_at": "2024-01-01T12:00:00",
  "results": {
    "glucose": "120 mg/dL",
    "hemoglobin": "14.5 g/dL"
  },
  "processing_time": 15.2,
  "pages_processed": 3
}
```

### `POST /batch-process`
Process multiple PDF files in batch (max 10 files).

### `GET /health`
Health check endpoint.

## 🧪 Testing

### Using curl:
```bash
# Health check
curl http://localhost:8000/health

# Process a PDF file
curl -X POST "http://localhost:8000/process-lab-results" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_lab_results.pdf"
```

### Using Python requests:
```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Process PDF
with open("lab_results.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/process-lab-results",
        files={"file": f}
    )
print(response.json())
```

## 🔧 Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: Required for AI extraction
- `LOG_LEVEL`: Logging level (default: INFO)
- `MODEL_NAME`: AI model to use (optional)

### Docker Configuration
- Port: 8000
- Health check: `/health` endpoint
- Auto-restart: enabled
- Volume mounts: `./results` for output files

## 🏗️ Architecture

```
diabetes3d/
├── api/                    # FastAPI application
│   ├── main.py            # Main API routes
│   ├── models.py          # Pydantic models
│   └── __init__.py
├── src/                   # Core processing logic
│   ├── ocr/              # OCR strategies
│   ├── extraction/       # AI data extraction
│   └── utils/            # Utilities
├── Dockerfile            # Container definition
├── docker-compose.yml    # Docker deployment
└── pyproject.toml        # Dependencies
```

## 🔄 Processing Pipeline

1. **Upload**: PDF file received via API
2. **Split**: PDF split into individual pages
3. **OCR**: Multiple OCR strategies applied (PyMuPDF, Marker, Mistral)
4. **Extract**: AI extracts structured lab data
5. **Return**: JSON response with extracted results

## 🚀 Production Deployment

### Cloud Platforms
- **AWS**: Use ECS/Fargate with Application Load Balancer
- **Google Cloud**: Deploy to Cloud Run
- **Azure**: Use Container Instances or App Service
- **DigitalOcean**: App Platform or Droplets

### Scaling Considerations
- Add Redis for caching and job queues
- Use horizontal scaling for multiple replicas
- Consider async processing for large files
- Add rate limiting and authentication

## 📊 Monitoring

The API includes:
- Health checks at `/health`
- Structured logging
- Processing time metrics
- Error handling and reporting

## 🛠️ Development

### Adding New OCR Strategies
1. Create new strategy in `src/ocr/strategies.py`
2. Register in `OcrProcessor.strategies`

### Adding New Extraction Features
1. Update signatures in `src/extraction/signatures.py`
2. Modify extractor logic in `src/extraction/extractor.py`

### API Customization
1. Add new endpoints in `api/main.py`
2. Create corresponding models in `api/models.py`
