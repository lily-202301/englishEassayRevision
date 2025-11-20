"""
Celery worker for processing essay analysis tasks.
"""
import os
import logging
from pathlib import Path
from celery import Celery
from asgiref.sync import async_to_sync
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.models import Task
from app.services.ai_service import analyze_essay
from app.services.pdf_service import generate_pdf
from app.schemas import FullReport

# Configure logging
logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery(
    "essay_polisher",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Database configuration for Celery worker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./essay_polisher.db")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# PDF storage directory
PDF_STORAGE_DIR = Path("pdfs")
PDF_STORAGE_DIR.mkdir(exist_ok=True)


async def _process_task_async(task_id: int) -> None:
    """
    Async function to process a task.
    
    Args:
        task_id: The task ID to process
    """
    async with AsyncSessionLocal() as session:
        try:
            # Read task from database
            result = await session.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            
            if not task:
                logger.error(f"Task {task_id} not found")
                return
            
            logger.info(f"Processing task {task_id}")
            
            # Update status to processing
            task.status = "processing"
            await session.commit()
            
            # Call AI service (async function in async context)
            logger.info(f"Calling AI service for task {task_id}")
            report: FullReport = await analyze_essay(
                text=task.original_text,
                context=task.context
            )
            
            # Generate PDF
            logger.info(f"Generating PDF for task {task_id}")
            pdf_bytes = generate_pdf(report_data=report, original_text=task.original_text)
            
            # Save PDF file
            pdf_filename = f"report_{task_id}.pdf"
            pdf_path = PDF_STORAGE_DIR / pdf_filename
            with open(pdf_path, "wb") as f:
                f.write(pdf_bytes)
            
            logger.info(f"PDF saved to {pdf_path}")
            
            # Update task in database
            task.status = "completed"
            task.report_json = report.model_dump()
            task.pdf_path = str(pdf_path)
            await session.commit()
            
            logger.info(f"Task {task_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
            
            # Update task status to failed
            async with AsyncSessionLocal() as error_session:
                result = await error_session.execute(select(Task).where(Task.id == task_id))
                task = result.scalar_one_or_none()
                if task:
                    task.status = "failed"
                    await error_session.commit()
            
            raise


@celery_app.task(name="process_submission")
def process_submission(task_id: int) -> dict:
    """
    Celery task to process essay submission.
    
    Args:
        task_id: The task ID to process
    
    Returns:
        dict: Task processing result
    """
    try:
        logger.info(f"Starting Celery task for task_id: {task_id}")
        
        # Run async function in sync context using async_to_sync
        async_to_sync(_process_task_async)(task_id)
        
        return {"status": "success", "task_id": task_id}
    
    except Exception as e:
        logger.error(f"Celery task failed for task_id {task_id}: {str(e)}", exc_info=True)
        return {"status": "failed", "task_id": task_id, "error": str(e)}

