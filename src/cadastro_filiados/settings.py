from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE, env_file_encoding='utf-8', extra='ignore'
    )

    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_DB: str = 'cadastro_filiados'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/cadastro_filiados'