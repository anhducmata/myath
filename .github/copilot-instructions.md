<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Math Homework Backend - Copilot Instructions

This is a **FastAPI backend** project for processing mathematics homework problems with Firebase integration.

## Project Context

- **Framework**: FastAPI with Python 3.11+
- **Authentication**: Firebase Admin SDK with ID token verification
- **Database**: Google Cloud Firestore
- **Storage**: Firebase Storage for file uploads
- **Task Queue**: Celery with Redis
- **Math Processing**: SymPy for symbolic mathematics
- **OCR**: Mathpix API (primary) + Tesseract (fallback)
- **AI Integration**: OpenAI API for problem parsing
- **Deployment**: Docker with docker-compose

## Code Style Guidelines

- Use **async/await** for all I/O operations
- Follow **Pydantic models** for data validation
- Use **dependency injection** with FastAPI dependencies
- Implement proper **error handling** with HTTP exceptions
- Add **comprehensive logging** for debugging
- Write **type hints** for all functions
- Follow **PEP 8** conventions

## Architecture Patterns

- **Service Layer Pattern**: Business logic in `app/services/`
- **Repository Pattern**: Firebase operations isolated in `firebase.py`
- **Background Tasks**: Use Celery for long-running operations
- **Configuration**: Environment-based settings with Pydantic
- **Testing**: Pytest with mocking for external services

## Key Components

1. **API Layer** (`app/api/v1/`): FastAPI endpoints with authentication
2. **Services** (`app/services/`): Core business logic
3. **Models** (`app/models.py`): Pydantic schemas for validation
4. **Tasks** (`app/tasks.py`): Celery background processing
5. **Config** (`config/settings.py`): Application configuration

## Math Processing Pipeline

1. File upload → Firebase Storage
2. OCR extraction → Mathpix/Tesseract
3. Problem parsing → OpenAI LLM
4. Math solving → SymPy
5. Solution verification → Symbolic validation
6. Result storage → Firestore
7. Notification → Firebase FCM

## Security Considerations

- Always verify Firebase ID tokens
- Validate file types and sizes
- Sanitize user inputs
- Use environment variables for secrets
- Implement rate limiting for production

## Testing Guidelines

- Mock external services (Firebase, OpenAI, Mathpix)
- Test both success and error scenarios
- Use realistic test data for math problems
- Test the complete processing pipeline
- Verify security measures

## Common Patterns

```python
# Service method pattern
async def process_data(self, input_data: InputModel) -> OutputModel:
    try:
        # Process logic here
        result = await self._internal_method(input_data)
        return OutputModel(**result)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

# API endpoint pattern
@router.post("/endpoint", response_model=ResponseModel)
async def endpoint(
    request: RequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        result = await service.process(request)
        return result
    except ServiceException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

When generating code:
- Prefer async operations for I/O
- Include proper error handling
- Add logging statements
- Use type hints consistently
- Follow the established patterns
