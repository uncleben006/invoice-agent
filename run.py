import uvicorn
from dotenv import load_dotenv
from invoice_agent.core.config import settings

# 載入環境變數
load_dotenv()

if __name__ == "__main__":
    """
    啟動 FastAPI 應用程式
    使用方式: python run.py
    """
    uvicorn.run(
        "invoice_agent.main:app",
        host="0.0.0.0",
        port=8008,
        reload=settings.DEBUG
    )
