from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Configurações da aplicação
    app_name: str = "Caminhos Conscientes API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configurações do banco de dados
    database_url: str = "sqlite:///./app.db"
    
    # Configurações JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Configurações de email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    
    # Configurações de ML
    model_path: str = "./models/"
    retrain_interval_days: int = 7
    
    # Configurações CORS
    allowed_origins: List[str] = ["http://localhost:3000", "https://localhost:3000"]
    
    # Configurações de rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()

