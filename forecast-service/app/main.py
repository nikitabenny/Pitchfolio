from fastapi import FastAPI
from app.database import Base, engine
from app.player_client import fetch_all_gameweeks

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/debug/history-count")
def history_count():
    rows = fetch_all_gameweeks()
    return {"count": len(rows)}
