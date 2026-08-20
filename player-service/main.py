from fastapi import FastAPI
from models import Player
from database import Base,engine
app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    return "Pitchfolio"

@app.get("/health")
def health_check():
    return {"status": "ok"}
