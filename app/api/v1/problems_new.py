from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Dict, Any
import uuid
import logging
from datetime import datetime
from config.settings import settings
from app.models import ProblemOut, ProblemCreate, ErrorResponse, ProblemStatus
from app.dependencies import get_current_user, verify_file_type, verify_file_size
from app.services.firebase import firebase_service
from app.tasks import task_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/problems", tags=["problems"])


@router.post("", response_model=ProblemCreate, status_code=status.HTTP_201_CREATED)
async def create_problem(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Upload a math problem image/PDF and start processing
    
    - **file**: Image (JPG, PNG, GIF) or PDF file containing the math problem (required)
    - **X-API-Key**: API key in header (required)
    
    Returns problem_id for tracking the solution progress
    """
    try:
        # Validate file type
        if not verify_file_type(file.content_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Allowed: {', '.join(settings.allowed_file_types_list)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        if not verify_file_size(len(file_content)):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Upload file to storage
        file_url = await firebase_service.upload_file(
            file_content, 
            unique_filename, 
            file.content_type
        )
        
        # Create problem document
        problem_data = {
            'user_id': current_user.get('api_key', 'unknown'),
            'status': ProblemStatus.QUEUED,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'file_url': file_url,
            'original_filename': file.filename
        }
        
        problem_id = await firebase_service.create_problem(problem_data)
        
        # Queue background task for processing
        task_id = task_manager.start_problem_processing(
            problem_id, 
            file_url, 
            current_user.get('api_key', 'unknown')
        )
        
        # Update problem with task ID
        await firebase_service.update_problem(problem_id, {'task_id': task_id})
        
        logger.info(f"Created problem {problem_id} for file {file.filename}")
        
        return ProblemCreate(problem_id=problem_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating problem: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create problem"
        )


@router.get("/{problem_id}", response_model=ProblemOut)
async def get_problem(
    problem_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get problem details and solution status
    
    - **problem_id**: The ID of the problem to retrieve
    - **X-API-Key**: API key in header (required)
    
    Returns complete problem information including status and solution (if available)
    """
    try:
        # Get problem from storage
        problem_data = await firebase_service.get_problem(problem_id)
        
        if not problem_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )
        
        # Check if user owns this problem (in production, check API key ownership)
        if settings.environment == "production" and problem_data.get('user_id') != current_user.get('api_key'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't own this problem"
            )
        
        # Convert data to Pydantic model
        return ProblemOut(**problem_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving problem {problem_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve problem"
        )


@router.get("/{problem_id}/task-status")
async def get_task_status(
    problem_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get the background task status for a problem
    
    - **problem_id**: The ID of the problem
    - **X-API-Key**: API key in header (required)
    
    Returns task execution status and progress
    """
    try:
        # Get problem from storage
        problem_data = await firebase_service.get_problem(problem_id)
        
        if not problem_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Problem not found"
            )
        
        # Check if user owns this problem
        if settings.environment == "production" and problem_data.get('user_id') != current_user.get('api_key'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't own this problem"
            )
        
        task_id = problem_data.get('task_id')
        if not task_id:
            return {
                'problem_id': problem_id,
                'task_status': 'no_task',
                'result': None,
                'error': None
            }
        
        # Get task status from Celery
        task_status = task_manager.get_task_status(task_id)
        
        return {
            'problem_id': problem_id,
            'task_id': task_id,
            'task_status': task_status['status'],
            'result': task_status['result'],
            'error': task_status['traceback'] if task_status['traceback'] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task status for problem {problem_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve task status"
        )
