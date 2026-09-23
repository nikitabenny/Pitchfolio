from fastapi import FastAPI,Request,Depends,HTTPException
from sqlalchemy.orm import Session
from database import Base,engine,get_db
from fpl_client import lifespan, fetch_bootstrap, fetch_history, fetch_fixtures, fetch_current_gameweek
from typing import Optional
from crud import find_player_value, pos_price_match, under_budget, upsert_player, read_players, find_player_by_id, find_player_by_eltype, find_player_points, build_gameweek_rows, upsert_player_gameweek, max_ingested_round, read_gameweeks
from historical import build_historical_rows
from auth import require_api_key

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
    player = find_player_by_id(player_id, db)
    if player is None:
        raise HTTPException(status_code=404, detail="player not found")

    current_gw = await fetch_current_gameweek(request.app.state.client)
    max_round = max_ingested_round(db, player.code, season)
    if max_round is not None and current_gw <= max_round:
        return

    #player_id is this season's FPL element id - still what the live API needs, even though
    #storage keys off player.code (stable across seasons) instead
    history_data = await fetch_history(request.app.state.client, player_id)
    fixtures = await fetch_fixtures(request.app.state.client)
    fixtures_by_id = {fixture["id"]: fixture for fixture in fixtures}

    new_history = [row for row in history_data["history"] if max_round is None or row["round"] > max_round]
    rows = build_gameweek_rows(player.code, season, new_history, fixtures_by_id)
    upsert_player_gameweek(db, rows)
    db.commit()

@app.get("/player-gameweeks", dependencies=[Depends(require_api_key)])
def get_gameweeks(db: Session = Depends(get_db), season: Optional[str] = None, player_code: Optional[int] = None):
    return read_gameweeks(db, season=season, player_code=player_code)

@app.post("/ingest-historical/{season}")
def ingest_historical(season: str, db: Session = Depends(get_db)):
    rows = build_historical_rows(season)
    upsert_player_gameweek(db, rows)
    db.commit()

@app.post("/ingest-gameweeks")
async def ingest_all_gameweeks(season: str, request: Request, db: Session = Depends(get_db)):
    current_gw = await fetch_current_gameweek(request.app.state.client)
    fixtures = await fetch_fixtures(request.app.state.client)
    fixtures_by_id = {fixture["id"]: fixture for fixture in fixtures}

    for player in read_players(db):
        max_round = max_ingested_round(db, player.code, season)
        if max_round is not None and current_gw <= max_round:
            continue

        history_data = await fetch_history(request.app.state.client, player.id)
        new_history = [row for row in history_data["history"] if max_round is None or row["round"] > max_round]
        rows = build_gameweek_rows(player.code, season, new_history, fixtures_by_id)
        upsert_player_gameweek(db, rows)

    db.commit()
