from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

engine = create_async_engine(os.environ["DATABASE_URL"])
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        yield db