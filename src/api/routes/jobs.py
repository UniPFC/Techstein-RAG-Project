"""
Job status endpoints for tracking background tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from shared.database.session import get_db
from shared.database.models.ingestion_job import IngestionJob
from src.api.schemas.ingestion import IngestionJobResponse
from config.logger import logger

router = APIRouter(prefix="/upload/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=IngestionJobResponse)
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get status of an ingestion job.
    
    Returns job details including:
    - status (pending, processing, completed, failed)
    - progress (processed_chunks / total_chunks)
    - error message if failed
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return job


@router.get("/", response_model=List[IngestionJobResponse])
def list_jobs(
    chat_type_id: int = None,
    status_filter: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    List ingestion jobs with optional filtering.
    """
    query = db.query(IngestionJob)
    
    if chat_type_id is not None:
        query = query.filter(IngestionJob.chat_type_id == chat_type_id)
    
    if status_filter is not None:
        query = query.filter(IngestionJob.status == status_filter)
    
    jobs = query.order_by(IngestionJob.created_at.desc()).offset(skip).limit(limit).all()
    return jobs


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a job record (only for completed or failed jobs).
    """
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    if job.status in ["pending", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a job that is still running"
        )
    
    db.delete(job)
    db.commit()
    
    logger.info(f"Deleted job {job_id}")
