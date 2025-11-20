"""
FastAPI application entry point.
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db, init_db
from app.models import Task
from app.schemas import TaskCreate, TaskResponse
from app.worker import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI English Essay Polisher",
    description="AI-powered English essay analysis and polishing service",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down...")


@app.post("/submit", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def submit_essay(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Submit an essay for analysis.
    
    Args:
        task_data: Essay text and context
        db: Database session
    
    Returns:
        TaskResponse: Created task information
    """
    try:
        logger.info(f"Received essay submission, text length: {len(task_data.original_text)}")
        
        # Create task in database
        task = Task(
            original_text=task_data.original_text,
            context=task_data.context,
            status="processing"
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Created task {task.id}")
        
        # Trigger Celery task
        celery_app.send_task(
            "process_submission",
            args=[task.id],
            countdown=1  # Start after 1 second
        )
        
        logger.info(f"Triggered Celery task for task {task.id}")
        
        return TaskResponse(
            id=task.id,
            original_text=task.original_text,
            context=task.context,
            status=task.status,
            report_json=None,
            pdf_path=None
        )
    
    except Exception as e:
        logger.error(f"Error submitting essay: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit essay: {str(e)}"
        )


@app.get("/status/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: int,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Get task status and download link.
    
    Args:
        task_id: Task ID
        db: Database session
    
    Returns:
        TaskResponse: Task information with status and download link
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        # Build download URL if PDF is ready
        pdf_path = None
        if task.status == "completed" and task.pdf_path:
            pdf_path = f"/download/{task_id}"
        
        return TaskResponse(
            id=task.id,
            original_text=task.original_text,
            context=task.context,
            status=task.status,
            report_json=task.report_json,
            pdf_path=pdf_path
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )


@app.get("/download/{task_id}")
async def download_pdf(task_id: int, db: AsyncSession = Depends(get_db)) -> FileResponse:
    """
    Download the generated PDF report.
    
    Args:
        task_id: Task ID
        db: Database session
    
    Returns:
        FileResponse: PDF file
    """
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        if task.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Task {task_id} is not completed yet. Status: {task.status}"
            )
        
        if not task.pdf_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF not found for task {task_id}"
            )
        
        pdf_path = Path(task.pdf_path)
        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"PDF file not found at {pdf_path}"
            )
        
        return FileResponse(
            path=pdf_path,
            filename=f"essay_report_{task_id}.pdf",
            media_type="application/pdf"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download PDF: {str(e)}"
        )


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "AI English Essay Polisher API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "POST /submit",
            "status": "GET /status/{task_id}",
            "download": "GET /download/{task_id}"
        }
    }

