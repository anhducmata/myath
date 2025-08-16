from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ProblemType(str, Enum):
    EQUATION = "equation"
    SYSTEM = "system"
    INTEGRAL = "integral"
    DERIVATIVE = "derivative"
    WORD_PROBLEM = "word_problem"
    MCQ = "mcq"
    OTHER = "other"


class ProblemStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SolutionStep(BaseModel):
    step_number: int
    description: str
    latex: Optional[str] = None
    explanation: str


class ParsedProblem(BaseModel):
    type: ProblemType
    statement: str
    asks: List[str]
    options: Optional[List[str]] = []
    variables: Optional[List[str]] = []


class Solution(BaseModel):
    result: Any
    steps: List[SolutionStep]
    confidence: float = Field(ge=0.0, le=1.0)
    method: str
    verification_passed: bool = False


class OCRResult(BaseModel):
    text: str
    latex: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    method: str


class ProblemIn(BaseModel):
    pass  # File upload will be handled separately


class ProblemOut(BaseModel):
    problem_id: str
    user_id: str
    status: ProblemStatus
    created_at: datetime
    updated_at: datetime
    file_url: Optional[str] = None
    ocr_result: Optional[OCRResult] = None
    parsed_problem: Optional[ParsedProblem] = None
    solution: Optional[Solution] = None
    error_message: Optional[str] = None


class ProblemCreate(BaseModel):
    problem_id: str


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
