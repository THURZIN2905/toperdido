from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    ORIENTADOR = "orientador"

class QuestionType(enum.Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    BOOLEAN = "boolean"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    responses = relationship("QuestionnaireResponse", back_populates="user")
    results = relationship("RecommendationResult", back_populates="user")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    category = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    responses = relationship("QuestionnaireResponse", back_populates="question")

class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text = Column(String(500), nullable=False)
    value = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    
    # Pesos para cada curso
    weight_ti = Column(Float, default=0.0)
    weight_enfermagem = Column(Float, default=0.0)
    weight_logistica = Column(Float, default=0.0)
    weight_administracao = Column(Float, default=0.0)
    weight_estetica = Column(Float, default=0.0)
    
    # Relacionamentos
    question = relationship("Question", back_populates="options")

class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("question_options.id"), nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    option = relationship("QuestionOption")

class RecommendationResult(Base):
    __tablename__ = "recommendation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Pontuações por curso
    score_ti = Column(Float, nullable=False)
    score_enfermagem = Column(Float, nullable=False)
    score_logistica = Column(Float, nullable=False)
    score_administracao = Column(Float, nullable=False)
    score_estetica = Column(Float, nullable=False)
    
    # Curso recomendado
    recommended_course = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0-1
    
    # Metadados
    model_version = Column(String(50), nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User", back_populates="results")

