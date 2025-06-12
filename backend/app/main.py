from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1 import auth, questionnaire, admin
from app.schemas import HealthResponse
from datetime import datetime
import uvicorn

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Configuração da aplicação
app = FastAPI(
    title=settings.app_name,
    description="API para sistema de orientação vocacional inteligente",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Incluir routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(questionnaire.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Endpoints básicos
@app.get("/", tags=["root"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "Caminhos Conscientes API",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version
    )

# Middleware para logging (opcional)
@app.middleware("http")
async def log_requests(request, call_next):
    """Middleware para log de requisições"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    print(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response

# Handler para erros não tratados
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    print(f"Erro não tratado: {exc}")
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro interno do servidor"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )

