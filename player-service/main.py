from fastapi import FastAPI,Request,Depends
from sqlalchemy.orm import Session
from database import Base,engine,get_db
from fpl_client import lifespan, fetch_bootstrap
from crud import upsert_player

app = FastAPI(lifespan = lifespan)


Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest-bootstrap")
async def refresh_players(request : Request, db : Session = Depends(get_db), ):
    data = await fetch_bootstrap(request.app.state.client)
    upsert_player(db,data["elements"])
    db.commit()