from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:0.00@localhost/tally_api_docker"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)
Base = declarative_base()

# Dependency
async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()