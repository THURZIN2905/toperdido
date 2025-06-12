from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import uvicorn
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.routing import Mount

# Configuração da aplicação
app = FastAPI(
    title="Caminhos Conscientes API",
    description="API para sistema de orientação vocacional inteligente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Modelos Pydantic básicos
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Criar um roteador para a versão 1 da API
api_v1_router = APIRouter(prefix="/api/v1")

# Endpoints básicos
@api_v1_router.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Caminhos Conscientes API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@api_v1_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

# Placeholder para rotas de autenticação
@api_v1_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Registra um novo usuário"""
    # TODO: Implementar lógica de registro
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

@api_v1_router.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Autentica usuário e retorna tokens JWT"""
    # TODO: Implementar lógica de login
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

# Placeholder para rotas do questionário
@api_v1_router.get("/questionnaire/questions")
async def get_questions():
    """Retorna todas as perguntas ativas"""
    # TODO: Implementar busca de perguntas
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

@api_v1_router.post("/questionnaire/submit")
async def submit_questionnaire():
    """Submete respostas do questionário"""
    # TODO: Implementar submissão de questionário
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

# Placeholder para rotas administrativas
@api_v1_router.get("/admin/dashboard")
async def get_dashboard():
    """Retorna dados do dashboard administrativo"""
    # TODO: Implementar dashboard
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint em desenvolvimento"
    )

# Incluir o roteador na aplicação principal
app.include_router(api_v1_router)

# Montar arquivos estáticos do frontend
app.mount("/", StaticFiles(directory="/home/ubuntu/caminhos-conscientes/backend/static_frontend", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


