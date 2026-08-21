from fastapi import FastAPI,Request,Depends
from sqlalchemy.orm import Session
from database import Base,engine,get_db
from fpl_client import lifespan, fetch_bootstrap
from typing import Optional
from crud import pos_price_match, under_budget, upsert_player, read_players, find_player_by_id, find_player_by_eltype

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

@app.get("/players")
def get_player_info(db : Session = Depends(get_db),
                    el_type: Optional[str] = None,
                    price: Optional[float] = None
):
    if el_type and price:
        return pos_price_match(el_type,price,db)

    elif el_type:
        return find_player_by_eltype(el_type,db)

    elif price:
        return under_budget(price,db)

    else:
        return read_players(db)

    
@app.get("/players/{id}")
def id_search(id: int, db : Session = Depends(get_db)):
    player = find_player_by_id(id,db)
    return player