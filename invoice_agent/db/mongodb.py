"""
MongoDB 連接處理模組
"""
from motor.motor_asyncio import AsyncIOMotorClient
from invoice_agent.core.config import settings

class MongoDB:
    """
    MongoDB 連接管理類
    """
    client: AsyncIOMotorClient = None
    db = None

mongo_db = MongoDB()

async def connect_to_mongo():
    """
    連接到 MongoDB 資料庫
    """
    mongo_db.client = AsyncIOMotorClient(settings.MONGO_URI)
    mongo_db.db = mongo_db.client[settings.MONGO_DB]
    print(f"已連接到 MongoDB: {settings.MONGO_HOST}:{settings.MONGO_PORT}")

async def close_mongo_connection():
    """
    關閉 MongoDB 連接
    """
    if mongo_db.client:
        mongo_db.client.close()
        print("MongoDB 連接已關閉")

def get_database():
    """
    獲取資料庫實例
    """
    return mongo_db.db
