from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv() # Carrega as variáveis do arquivo .env

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "defaultsecret") # Default é ruim, mas para não quebrar se .env faltar
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()