from fpl_client import lifespan
from fastapi import FastAPI
from database import Base,engine,get_db

app = FastAPI(lifespan = lifespan)
Base.metadata.create_all(bind=engine)