# Math Homework Backend

A comprehensive FastAPI backend for processing mathematics homework problems with Firebase integration, OCR processing, and automated solving using SymPy.

## 🔓 Development Mode (Authentication Bypass)

**For easy development and testing, authentication is bypassed in development mode:**

- ✅ **No Authorization header required** for any endpoint
- ✅ **Special development endpoints** available at `/v1/problems/dev/`
- ✅ **Mock Firebase operations** - no real Firebase setup needed
- ✅ **Ownership checks disabled** - access any problem
- ✅ **Optional bypass tokens** - use `"dev"`, `"test"`, or `"bypass"` as Bearer token

### Quick Test Commands
```bash
# Test auth bypass
curl http://localhost:8000/v1/problems/dev/auth-test

# Create test problem (no file upload needed)
curl -X POST http://localhost:8000/v1/problems/dev/test

# Create custom problem
curl -X POST "http://localhost:8000/v1/problems/dev/test?text=solve x^2 + 5x + 6 = 0"

# Get any problem (no ownership check)
curl http://localhost:8000/v1/problems/{problem_id}
```

## Features

- 🔐 **Firebase Authentication** - Secure user authentication with Firebase ID tokens
- 📤 **File Upload** - Support for image (JPEG, PNG, GIF) and PDF uploads
- 🔍 **OCR Processing** - Math-aware OCR using Mathpix API with Tesseract fallback
- 🧮 **Math Solving** - Automated solving using SymPy for equations, integrals, derivatives
- 📱 **Push Notifications** - FCM notifications when solutions are ready
- ⚡ **Async Processing** - Background task processing with Celery and Redis
- 📊 **Real-time Status** - Track problem processing status in real-time
- 🐳 **Docker Ready** - Fully containerized with Docker Compose

## API Endpoints

### POST /v1/problems
Upload a math problem image/PDF for processing.

**Request:**
- `file`: Image or PDF file (max 10MB)
- `Authorization`: Bearer token (Firebase ID token)

**Response:**
```json
{
  "problem_id": "uuid-string"
}
```

### GET /v1/problems/{id}
Get problem details and solution status.

**Response:**
```json
{
  "problem_id": "uuid-string",
  "user_id": "firebase-uid",
  "status": "queued|processing|completed|failed",
  "created_at": "2025-08-16T10:00:00Z",
  "updated_at": "2025-08-16T10:05:00Z",
  "file_url": "https://storage.firebase.com/...",
  "ocr_result": {
    "text": "x^2 + 2x + 1 = 0",
    "latex": "x^2 + 2x + 1 = 0",
    "confidence": 0.95,
    "method": "mathpix"
  },
  "parsed_problem": {
    "type": "equation",
    "statement": "x^2 + 2x + 1 = 0",
    "asks": ["solve_for:x"],
    "variables": ["x"]
  },
  "solution": {
    "result": [-1],
    "steps": [
      {
        "step_number": 1,
        "description": "Given equation: x^2 + 2x + 1 = 0",
        "latex": "x^2 + 2x + 1 = 0",
        "explanation": "Starting with the given equation"
      }
    ],
    "confidence": 0.9,
    "method": "sympy_solve",
    "verification_passed": true
  }
}
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Firebase Admin SDK** - Authentication, Firestore, Storage, FCM
- **SymPy** - Symbolic mathematics library
- **Celery + Redis** - Async task processing
- **Mathpix API** - Math-aware OCR
- **Tesseract** - Fallback OCR
- **OpenAI API** - LLM for problem parsing
- **Docker** - Containerization

## Quick Start

### Prerequisites

- Python 3.11+
- Redis server
- Firebase project with service account key
- Mathpix API credentials (optional)
- OpenAI API key

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd math-homework-backend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Environment configuration:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Firebase setup:**
   - Create a Firebase project
   - Generate a service account key
   - Save as `config/firebase-service-account.json`
   - Update `.env` with your Firebase project ID

5. **Start Redis:**
```bash
redis-server
```

6. **Run the application:**
```bash
# Start FastAPI server
uvicorn main:app --reload

# Start Celery worker (in another terminal)
celery -A celery_app worker --loglevel=info

# Optional: Start Flower for monitoring
celery -A celery_app flower
```

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

Create `.env` file from `.env.example` and configure:

```env
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CREDENTIALS_PATH=./config/firebase-service-account.json

# OCR
MATHPIX_APP_ID=your-mathpix-app-id
MATHPIX_APP_KEY=your-mathpix-app-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## Processing Pipeline

1. **File Upload** → Firebase Storage
2. **OCR Processing** → Mathpix API or Tesseract
3. **Problem Parsing** → LLM-based structured extraction
4. **Math Solving** → SymPy solver routing
5. **Verification** → Solution validation
6. **Notification** → FCM push notification

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Monitoring

- **Flower (Celery)**: http://localhost:5555
- **Application Logs**: Check console output or configure external logging

## Project Structure

```
├── app/
│   ├── api/v1/          # API endpoints
│   ├── models.py        # Pydantic models
│   ├── dependencies.py  # FastAPI dependencies
│   ├── tasks.py         # Celery tasks
│   └── services/        # Business logic
│       ├── firebase.py  # Firebase integration
│       ├── ocr.py       # OCR processing
│       ├── parser.py    # Problem parsing
│       └── solver.py    # Math solving
├── config/
│   └── settings.py      # Application settings
├── tests/               # Test suite
├── main.py              # FastAPI application
├── celery_app.py        # Celery configuration
└── docker-compose.yml   # Docker services
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the test cases for usage examples
