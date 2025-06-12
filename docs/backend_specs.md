# Especificações Técnicas do Backend
## API "Caminhos Conscientes"

**Autor:** Manus AI  
**Data:** 6 de novembro de 2025  
**Versão:** 1.0

---

## 1. Visão Geral da API

A API do sistema "Caminhos Conscientes" é construída com FastAPI, oferecendo uma interface RESTful robusta e bem documentada para todas as funcionalidades do sistema. A API segue os princípios REST e implementa autenticação JWT, validação de dados com Pydantic, e documentação automática via Swagger UI.

### 1.1 Características Principais

- **Framework:** FastAPI 0.104+
- **Linguagem:** Python 3.11+ com type hints
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **ORM:** SQLAlchemy 2.0+ com async support
- **Autenticação:** JWT com refresh tokens
- **Validação:** Pydantic v2 para schemas
- **Documentação:** Swagger UI automático
- **Testes:** pytest com coverage

---

## 2. Modelos de Dados

### 2.1 Modelo User

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    responses: Mapped[List["QuestionnaireResponse"]] = relationship(back_populates="user")
    results: Mapped[List["RecommendationResult"]] = relationship(back_populates="user")
```

### 2.2 Modelo Question

```python
class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    category: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relacionamentos
    options: Mapped[List["QuestionOption"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    responses: Mapped[List["QuestionnaireResponse"]] = relationship(back_populates="question")
```

### 2.3 Modelo QuestionOption

```python
class QuestionOption(Base):
    __tablename__ = "question_options"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    text: Mapped[str] = mapped_column(String(500))
    value: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column()
    
    # Pesos para cada curso
    weight_ti: Mapped[float] = mapped_column(default=0.0)
    weight_enfermagem: Mapped[float] = mapped_column(default=0.0)
    weight_logistica: Mapped[float] = mapped_column(default=0.0)
    weight_administracao: Mapped[float] = mapped_column(default=0.0)
    weight_estetica: Mapped[float] = mapped_column(default=0.0)
    
    # Relacionamentos
    question: Mapped["Question"] = relationship(back_populates="options")
```

### 2.4 Modelo QuestionnaireResponse

```python
class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    selected_option_id: Mapped[int] = mapped_column(ForeignKey("question_options.id"))
    response_time_ms: Mapped[int] = mapped_column()  # Tempo para responder
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relacionamentos
    user: Mapped[Optional["User"]] = relationship(back_populates="responses")
    question: Mapped["Question"] = relationship(back_populates="responses")
    option: Mapped["QuestionOption"] = relationship()
```

### 2.5 Modelo RecommendationResult

```python
class RecommendationResult(Base):
    __tablename__ = "recommendation_results"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    
    # Pontuações por curso
    score_ti: Mapped[float] = mapped_column()
    score_enfermagem: Mapped[float] = mapped_column()
    score_logistica: Mapped[float] = mapped_column()
    score_administracao: Mapped[float] = mapped_column()
    score_estetica: Mapped[float] = mapped_column()
    
    # Curso recomendado
    recommended_course: Mapped[str] = mapped_column(String(100))
    confidence_score: Mapped[float] = mapped_column()  # 0-1
    
    # Metadados
    model_version: Mapped[str] = mapped_column(String(50))
    processing_time_ms: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relacionamentos
    user: Mapped[Optional["User"]] = relationship(back_populates="results")
```

---

## 3. Schemas Pydantic

### 3.1 User Schemas

```python
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
    
    model_config = ConfigDict(from_attributes=True)
```

### 3.2 Question Schemas

```python
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
    
    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)
```

### 3.3 Questionnaire Schemas

```python
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
    
    model_config = ConfigDict(from_attributes=True)
```

---

## 4. Endpoints da API

### 4.1 Autenticação (/auth)

```python
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registra um novo usuário"""
    pass

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Autentica usuário e retorna tokens JWT"""
    pass

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Renova access token usando refresh token"""
    pass

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Invalida tokens do usuário"""
    pass

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    pass
```

### 4.2 Questionário (/questionnaire)

```python
@router.get("/questions", response_model=List[QuestionResponse])
async def get_active_questions(db: AsyncSession = Depends(get_db)):
    """Retorna todas as perguntas ativas ordenadas"""
    pass

@router.post("/submit", response_model=RecommendationResultResponse)
async def submit_questionnaire(
    submission: QuestionnaireSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Submete respostas do questionário e retorna recomendação"""
    pass

@router.get("/result/{session_id}", response_model=RecommendationResultResponse)
async def get_result(session_id: str, db: AsyncSession = Depends(get_db)):
    """Retorna resultado de uma sessão específica"""
    pass

@router.post("/result/{session_id}/email")
async def email_result(
    session_id: str,
    email_data: EmailResultRequest,
    db: AsyncSession = Depends(get_db)
):
    """Envia resultado por email"""
    pass
```

### 4.3 Administração (/admin)

```python
@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Retorna estatísticas do dashboard"""
    pass

@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Lista todas as perguntas (admin)"""
    pass

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria nova pergunta"""
    pass

@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza pergunta existente"""
    pass

@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Remove pergunta"""
    pass

@router.get("/responses", response_model=List[QuestionnaireResponseAnalytics])
async def get_responses_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    course: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Retorna analytics de respostas com filtros"""
    pass

@router.get("/export/{format}")
async def export_data(
    format: ExportFormat,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Exporta dados em formato especificado (CSV, Excel, Word)"""
    pass
```

### 4.4 Machine Learning (/ml)

```python
@router.post("/classify", response_model=ClassificationResult)
async def classify_responses(
    responses: List[QuestionnaireResponseCreate],
    session_id: str
):
    """Classifica respostas e retorna pontuações por curso"""
    pass

@router.post("/retrain")
async def retrain_model(
    current_user: User = Depends(get_admin_user)
):
    """Retreina modelo com novos dados"""
    pass

@router.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Retorna informações sobre o modelo atual"""
    pass

@router.get("/model/metrics", response_model=ModelMetrics)
async def get_model_metrics(
    current_user: User = Depends(get_admin_user)
):
    """Retorna métricas de performance do modelo"""
    pass
```

---

## 5. Serviços de Negócio

### 5.1 AuthService

```python
class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Cria novo usuário com senha hasheada"""
        pass
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Autentica usuário por email e senha"""
        pass
    
    async def create_access_token(self, user_id: int) -> str:
        """Cria access token JWT"""
        pass
    
    async def create_refresh_token(self, user_id: int) -> str:
        """Cria refresh token JWT"""
        pass
    
    async def verify_token(self, token: str) -> Optional[int]:
        """Verifica token e retorna user_id"""
        pass
```

### 5.2 QuestionnaireService

```python
class QuestionnaireService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_active_questions(self) -> List[Question]:
        """Retorna perguntas ativas ordenadas"""
        pass
    
    async def submit_responses(
        self, 
        submission: QuestionnaireSubmission,
        user_id: Optional[int] = None
    ) -> RecommendationResult:
        """Processa respostas e gera recomendação"""
        pass
    
    async def calculate_scores(self, responses: List[QuestionnaireResponse]) -> Dict[str, float]:
        """Calcula pontuações por curso baseado nas respostas"""
        pass
    
    async def get_result_by_session(self, session_id: str) -> Optional[RecommendationResult]:
        """Busca resultado por session_id"""
        pass
```

### 5.3 MLService

```python
class MLService:
    def __init__(self):
        self.model = self._load_model()
        self.scaler = self._load_scaler()
    
    def classify_responses(self, responses: List[Dict]) -> Dict[str, float]:
        """Classifica respostas usando modelo ML"""
        pass
    
    def _preprocess_responses(self, responses: List[Dict]) -> np.ndarray:
        """Preprocessa respostas para o modelo"""
        pass
    
    async def retrain_model(self, db: AsyncSession):
        """Retreina modelo com novos dados"""
        pass
    
    def get_model_info(self) -> Dict:
        """Retorna informações sobre o modelo"""
        pass
```

### 5.4 EmailService

```python
class EmailService:
    def __init__(self):
        self.smtp_config = self._load_smtp_config()
    
    async def send_result_email(
        self, 
        email: str, 
        result: RecommendationResult,
        user_name: Optional[str] = None
    ):
        """Envia resultado por email com template HTML"""
        pass
    
    async def send_welcome_email(self, email: str, name: str):
        """Envia email de boas-vindas"""
        pass
    
    def _generate_result_html(self, result: RecommendationResult) -> str:
        """Gera HTML do resultado para email"""
        pass
```

### 5.5 ExportService

```python
class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_to_csv(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BytesIO:
        """Exporta dados para CSV"""
        pass
    
    async def export_to_excel(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BytesIO:
        """Exporta dados para Excel com gráficos"""
        pass
    
    async def export_to_word(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> BytesIO:
        """Exporta relatório para Word"""
        pass
```

---

## 6. Configuração e Middleware

### 6.1 Configurações

```python
class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./app.db"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Email
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_password: str
    
    # ML
    model_path: str = "./models/"
    retrain_interval_days: int = 7
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    model_config = SettingsConfigDict(env_file=".env")
```

### 6.2 Middleware

```python
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Implementa rate limiting por IP"""
    pass

# Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log de todas as requisições"""
    pass

# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Adiciona headers de segurança"""
    pass
```

---

## 7. Testes

### 7.1 Estrutura de Testes

```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    """Fixture para sessão de banco de dados de teste"""
    pass

@pytest.fixture
async def client():
    """Fixture para cliente de teste FastAPI"""
    pass

@pytest.fixture
async def admin_user():
    """Fixture para usuário admin de teste"""
    pass

# tests/test_auth.py
class TestAuth:
    async def test_register_user(self, client):
        """Testa registro de usuário"""
        pass
    
    async def test_login_user(self, client):
        """Testa login de usuário"""
        pass
    
    async def test_refresh_token(self, client):
        """Testa renovação de token"""
        pass

# tests/test_questionnaire.py
class TestQuestionnaire:
    async def test_get_questions(self, client):
        """Testa busca de perguntas"""
        pass
    
    async def test_submit_questionnaire(self, client):
        """Testa submissão de questionário"""
        pass
    
    async def test_get_result(self, client):
        """Testa busca de resultado"""
        pass
```

---

## 8. Deploy e Configuração

### 8.1 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 Requirements.txt

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiofiles==23.2.1
pandas==2.1.3
openpyxl==3.1.2
python-docx==1.1.0
matplotlib==3.8.2
scikit-learn==1.3.2
joblib==1.3.2
fastapi-mail==1.4.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### 8.3 Alembic Configuration

```python
# alembic/env.py
from app.core.config import settings
from app.models import Base

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

---

## 9. Documentação da API

A API utiliza FastAPI que gera automaticamente documentação interativa via Swagger UI, acessível em `/docs`. A documentação inclui:

- Todos os endpoints com parâmetros e responses
- Schemas de dados com exemplos
- Autenticação JWT integrada
- Possibilidade de testar endpoints diretamente

### 9.1 Exemplo de Response

```json
{
  "id": 1,
  "session_id": "sess_123456789",
  "score_ti": 85.5,
  "score_enfermagem": 45.2,
  "score_logistica": 62.8,
  "score_administracao": 71.3,
  "score_estetica": 38.9,
  "recommended_course": "Tecnologia da Informação",
  "confidence_score": 0.89,
  "model_version": "v1.2.0",
  "processing_time_ms": 245,
  "created_at": "2025-11-06T10:30:00Z"
}
```

---

## 10. Monitoramento e Logs

### 10.1 Logging Configuration

```python
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 10.2 Health Check

```python
@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

Esta especificação técnica do backend fornece uma base sólida para implementação da API do sistema "Caminhos Conscientes", seguindo as melhores práticas de desenvolvimento com FastAPI e garantindo escalabilidade, segurança e manutenibilidade.

