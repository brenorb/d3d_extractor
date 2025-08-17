from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ProcessingResult(BaseModel):
    """Response model for processed lab results"""
    status: str = Field(..., description="Processing status (success/error)")
    filename: str = Field(..., description="Original filename")
    processed_at: str = Field(..., description="Processing timestamp")
    results: Dict[str, Any] = Field(..., description="Extracted lab data")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    pages_processed: Optional[int] = Field(None, description="Number of pages processed")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field(default="error", description="Response status")
    message: str = Field(..., description="Error message")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
