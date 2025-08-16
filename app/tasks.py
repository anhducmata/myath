from celery import Celery
from celery.result import AsyncResult
import uuid
import logging
from datetime import datetime
from typing import Dict, Any
from config.settings import settings
from app.services.firebase import firebase_service
from app.services.ocr import ocr_service
from app.services.parser import parser_service
from app.services.solver import solver_service
from app.models import ProblemStatus

logger = logging.getLogger(__name__)

# Import shared Celery app
from celery_app import celery_app


@celery_app.task(bind=True, name='process_math_problem')
def process_math_problem(self, problem_id: str, file_url: str, user_id: str):
    """
    Background task to process a math problem through the complete pipeline
    """
    import asyncio
    
    async def _async_process():
        try:
            logger.info(f"Starting processing for problem {problem_id}")
            
            # Update status to processing
            await firebase_service.update_problem(problem_id, {
                'status': ProblemStatus.PROCESSING,
                'updated_at': datetime.utcnow()
            })
            
            # Step 1: Download file and perform OCR
            logger.info(f"Step 1: OCR processing for problem {problem_id}")
            file_content = _download_file(file_url)
            ocr_result = await ocr_service.process_image(file_content)
            
            # Update with OCR result
            await firebase_service.update_problem(problem_id, {
                'ocr_result': ocr_result.dict(),
                'updated_at': datetime.utcnow()
            })
            
            # Step 2: Parse the problem (with image fallback for low confidence)
            logger.info(f"Step 2: Parsing problem {problem_id}")
            parsed_problem = await parser_service.parse_problem(
                ocr_result.text, 
                ocr_result.latex,
                image_content=file_content,  # Pass original image content for fallback
                image_url=file_url  # Pass image URL for enhanced vision parsing
            )
            
            # Update with parsed result
            await firebase_service.update_problem(problem_id, {
                'parsed_problem': parsed_problem.dict(),
                'updated_at': datetime.utcnow()
            })
            
            # Step 3: Solve the problem
            logger.info(f"Step 3: Solving problem {problem_id}")
            solution = await solver_service.solve_problem(parsed_problem)
            
            # Step 4: Update final result
            logger.info(f"Step 4: Finalizing problem {problem_id}")
            await firebase_service.update_problem(problem_id, {
                'solution': solution.dict(),
                'status': ProblemStatus.COMPLETED,
                'updated_at': datetime.utcnow()
            })
            
            # Step 5: Send notification
            logger.info(f"Step 5: Sending notification for problem {problem_id}")
            try:
                # Note: In a real implementation, you'd need to store user FCM tokens
                # await firebase_service.send_notification(
                #     user_token="user_fcm_token",
                #     title="Solution Ready",
                #     body="Your math problem has been solved!",
                #     data={'problem_id': problem_id}
                # )
                pass
            except Exception as e:
                logger.warning(f"Failed to send notification: {e}")
            
            logger.info(f"Successfully processed problem {problem_id}")
            return {
                'problem_id': problem_id,
                'status': 'completed',
                'solution_confidence': solution.confidence
            }
        except Exception as e:
            logger.error(f"Error processing problem {problem_id}: {e}")
            
            # Update status to failed
            try:
                await firebase_service.update_problem(problem_id, {
                    'status': ProblemStatus.FAILED,
                    'error_message': str(e),
                    'updated_at': datetime.utcnow()
                })
            except Exception as update_error:
                logger.error(f"Failed to update error status: {update_error}")
            
            # Re-raise the exception for Celery to handle
            raise
    
    # Run the async function
    try:
        return asyncio.run(_async_process())
    except Exception as e:
        logger.error(f"Error processing problem {problem_id}: {e}")
        
        # Update status to failed (sync version)
        try:
            import asyncio
            asyncio.run(firebase_service.update_problem(problem_id, {
                'status': ProblemStatus.FAILED,
                'error_message': str(e),
                'updated_at': datetime.utcnow()
            }))
        except Exception as update_error:
            logger.error(f"Failed to update error status: {update_error}")
        
        # Don't retry - just fail the task
        return {
            'problem_id': problem_id,
            'status': 'failed',
            'error': str(e)
        }
        
    except Exception as e:
        logger.error(f"Error processing problem {problem_id}: {e}")
        
        # Update status to failed
        try:
            import asyncio
            asyncio.run(firebase_service.update_problem(problem_id, {
                'status': ProblemStatus.FAILED,
                'error_message': str(e),
                'updated_at': datetime.utcnow()
            }))
        except Exception as update_error:
            logger.error(f"Failed to update error status: {update_error}")
        
        # Don't retry - just fail the task
        return {
            'problem_id': problem_id,
            'status': 'failed',
            'error': str(e)
        }


def _download_file(url: str) -> bytes:
    """Download file from URL"""
    import requests
    response = requests.get(url)
    response.raise_for_status()
    return response.content


class TaskManager:
    """Manager for background tasks"""
    
    @staticmethod
    def start_problem_processing(problem_id: str, file_url: str, user_id: str) -> str:
        """Start background processing of a math problem"""
        task = process_math_problem.delay(problem_id, file_url, user_id)
        logger.info(f"Started task {task.id} for problem {problem_id}")
        return task.id
    
    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get status of a background task"""
        result = AsyncResult(task_id, app=celery_app)
        return {
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'traceback': result.traceback if result.failed() else None
        }
    
    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """Cancel a background task"""
        celery_app.control.revoke(task_id, terminate=True)
        return True


# Global instance
task_manager = TaskManager()
