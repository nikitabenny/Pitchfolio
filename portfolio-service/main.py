from fpl_client import lifespan, fetch_squad
from fastapi import FastAPI
from database import Base,engine,get_db
from crud import fetch_squad

app = FastAPI(lifespan = lifespan)
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest-squad")
async def refresh_squad(request : Request, db : Session = Depends(get_db), ):
    data = await fetch_squad(request.app.state.client)
    upsert_player(db,data["elements"])
    db.commit()  