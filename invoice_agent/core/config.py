from pydantic import BaseModel
import os
from typing import Optional
from pathlib import Path

# 獲取專案根目錄路徑
PROJECT_ROOT = Path(__file__).parent.parent.parent

class Settings(BaseModel):
    """
    應用程式設定模型
    """
    APP_NAME: str = "Invoice Agent API"
    API_V1_PREFIX: str = "/api/v1"
    
    # MongoDB 設定
    MONGO_USER: str = "root"
    MONGO_PASSWORD: str = "root"
    MONGO_HOST: str = "localhost"
    MONGO_PORT: int = 27017
    MONGO_DB: str = "invoice_db"
    
    # OCR 設定
    GOOGLE_VISION_CREDENTIALS_PATH: str = str(PROJECT_ROOT / "config" / "vision-credentials.json")
    
    # 建構 MongoDB 連接 URI
    @property
    def MONGO_URI(self) -> str:
        return f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}"
    
    # 其他設定可在此添加
    DEBUG: bool = True

# 從環境變數加載設定
def get_settings() -> Settings:
    """
    獲取應用程式設定
    """
    return Settings(
        APP_NAME=os.getenv("APP_NAME", "Invoice Agent API"),
        API_V1_PREFIX=os.getenv("API_V1_PREFIX", "/api/v1"),
        MONGO_USER=os.getenv("MONGO_USER", "root"),
        MONGO_PASSWORD=os.getenv("MONGO_PASSWORD", "root"),
        MONGO_HOST=os.getenv("MONGO_HOST", "localhost"),
        MONGO_PORT=int(os.getenv("MONGO_PORT", "27017")),
        MONGO_DB=os.getenv("MONGO_DB", "invoice_db"),
        GOOGLE_VISION_CREDENTIALS_PATH=os.getenv(
            "GOOGLE_APPLICATION_CREDENTIALS", 
            str(PROJECT_ROOT / "config" / "vision-credentials.json")
        ),
        DEBUG=os.getenv("DEBUG", "True").lower() in ("true", "1", "t"),
    )

settings = get_settings()
