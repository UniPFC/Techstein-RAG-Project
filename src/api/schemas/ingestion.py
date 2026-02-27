"""
Pydantic schemas for ingestion job endpoints.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class IngestionJobResponse(BaseModel):
    """Schema for ingestion job response."""
    id: int
    chat_type_id: int
    filename: str
    status: str
    total_chunks: int
    processed_chunks: int
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UploadResponseAsync(BaseModel):
    """Schema for async upload response."""
    job_id: int
    chat_type_id: int
    message: str
    status_url: str
