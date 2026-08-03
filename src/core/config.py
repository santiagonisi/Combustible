import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Control de Vales de Combustible"
    app_version: str = "1.0.0"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./combustible.db")


settings = Settings()
