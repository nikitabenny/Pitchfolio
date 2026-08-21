from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = 'postgresql+psycopg2://pitchfolio:pitchfolio@localhost:5432/player_service'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

#db generator
def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()