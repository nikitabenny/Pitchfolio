from fpl_client import lifespan as fpl_lifespan, fetch_squad, fetch_now_cost, fetch_transfers
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager
from database import Base, engine, get_db
from crud import upsert_squad, read_squad, buy_cost, sell_cost, fetch_fk, process_transfers
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with fpl_lifespan(app):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield

app = FastAPI(lifespan = lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest-transfers")
async def add_transfers(request : Request, team_id: str, db : AsyncSession = Depends(get_db)):
    await process_transfers(request.app.state.client, db, team_id)
    await db.commit()

@app.post("/ingest-squad")
async def refresh_squad(request : Request, team_id: str, gameweek_id: str, db : AsyncSession = Depends(get_db)):
    data = await fetch_squad(request.app.state.client, team_id, gameweek_id)
    await upsert_squad(request.app.state.client, db, data["picks"])
    await db.commit()

@app.get("/squad")
async def get_squad(db : AsyncSession = Depends(get_db)):
    return await read_squad(db)


@app.get("/roi/{id}")
async def get_roi(request : Request, id : int, db : AsyncSession = Depends(get_db)):
    player_id = await fetch_fk(db, id)
    price = await buy_cost(db, id)

    sold = await sell_cost(db, id)
    if sold is None:
        curr_cost = await fetch_now_cost(request.app.state.client, player_id)

    else:
        curr_cost = sold

    roi = ((curr_cost - price) / price) * 100

    return roi
