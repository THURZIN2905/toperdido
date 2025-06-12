from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import UserRole, QuestionType

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Question Schemas
class QuestionOptionBase(BaseModel):
    text: str
    value: str
    order: int
    weight_ti: float = 0.0
    weight_enfermagem: float = 0.0
    weight_logistica: float = 0.0
    weight_administracao: float = 0.0
    weight_estetica: float = 0.0

class QuestionOptionCreate(QuestionOptionBase):
    pass

class QuestionOptionResponse(QuestionOptionBase):
    id: int
    question_id: int
    
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    text: str
    question_type: QuestionType
    category: str
    order: int
    is_active: bool = True

class QuestionCreate(QuestionBase):
    options: List[QuestionOptionCreate]

class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    category: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None
    options: Optional[List[QuestionOptionCreate]] = None

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    options: List[QuestionOptionResponse]
    
    class Config:
        from_attributes = True

# Questionnaire Schemas
class QuestionnaireResponseCreate(BaseModel):
    question_id: int
    selected_option_id: int
    response_time_ms: int

class QuestionnaireSubmission(BaseModel):
    session_id: str
    responses: List[QuestionnaireResponseCreate]

class RecommendationResultResponse(BaseModel):
    id: int
    session_id: str
    score_ti: float
    score_enfermagem: float
    score_logistica: float
    score_administracao: float
    score_estetica: float
    recommended_course: str
    confidence_score: float
    model_version: str
    processing_time_ms: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Email Schemas
class EmailResultRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# Dashboard Schemas
class DashboardStats(BaseModel):
    total_responses: int
    total_users: int
    responses_today: int
    most_recommended_course: str
    average_confidence: float

# Health Check Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

# ML Schemas
class ClassificationResult(BaseModel):
    scores: dict
    recommended_course: str
    confidence_score: float
    processing_time_ms: int

class ModelInfo(BaseModel):
    version: str
    last_trained: datetime
    accuracy: float
    total_samples: int

class ModelMetrics(BaseModel):
    accuracy: float
    precision: dict
    recall: dict
    f1_score: dict

