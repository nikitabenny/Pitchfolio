from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        yield db