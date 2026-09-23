from fastapi import FastAPI,Request,Depends
from sqlalchemy.orm import Session
from database import Base,engine,get_db
from fpl_client import lifespan, fetch_bootstrap, fetch_history, fetch_fixtures
from typing import Optional
from crud import find_player_value, pos_price_match, under_budget, upsert_player, read_players, find_player_by_id, find_player_by_eltype, find_player_points, build_gameweek_rows, upsert_player_gameweek

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

@app.get("/players_ppm/{id}")
def points_by_id(id: int, db : Session = Depends(get_db)):
    points = find_player_points(id,db)
    value = find_player_value(id,db)
    return points


@app.post("/ingest-gameweeks/{player_id}")
async def ingest_gameweeks(player_id: int, season: str, request: Request, db: Session = Depends(get_db)):
    history_data = await fetch_history(request.app.state.client, player_id)
    fixtures = await fetch_fixtures(request.app.state.client)
    fixtures_by_id = {fixture["id"]: fixture for fixture in fixtures}

    rows = build_gameweek_rows(player_id, season, history_data["history"], fixtures_by_id)
    upsert_player_gameweek(db, rows)
    db.commit()

@app.post("/ingest-gameweeks")
async def ingest_all_gameweeks(season: str, request: Request, db: Session = Depends(get_db)):
    fixtures = await fetch_fixtures(request.app.state.client)
    fixtures_by_id = {fixture["id"]: fixture for fixture in fixtures}

    for player in read_players(db):
        history_data = await fetch_history(request.app.state.client, player.id)
        rows = build_gameweek_rows(player.id, season, history_data["history"], fixtures_by_id)
        upsert_player_gameweek(db, rows)

    db.commit()
