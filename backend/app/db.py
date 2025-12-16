from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URL, DB_NAME

client = AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    maxPoolSize=50,
    minPoolSize=5,
    maxIdleTimeMS=45000,
    retryWrites=True,
    retryReads=True
)

db = client[DB_NAME]
