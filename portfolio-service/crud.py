import httpx
from datetime import datetime
from sqlalchemy import select, inspect, func
from sqlalchemy.ext.asyncio import AsyncSession
from models import Squad
from fpl_client import fetch_transfers, fetch_now_cost, fetch_myinfo

async def upsert_squad(client: httpx.AsyncClient, db: AsyncSession, picks: list[dict], team_id: str):
    result = await db.execute(select(Squad).where(Squad.active_status == True))
    squad_by_player_id = {row.player_id: row for row in result.scalars().all()}

    columns = inspect(Squad).columns

    for pick in picks:
        #in squad
        if pick["element"] in squad_by_player_id:
            queryPlayer = squad_by_player_id[pick["element"]]

        #never been through a recorded transfer (e.g. initial season-draft squad)
        else:
            my_info = await fetch_myinfo(client,team_id)
            queryPlayer = Squad()
            queryPlayer.buy_price = await fetch_now_cost(client, pick["element"])
            queryPlayer.buy_gw = my_info["started_event"]
            queryPlayer.buy_date = datetime.fromisoformat(my_info["joined_time"]).replace(tzinfo=None)

        for key, value in pick.items():
            if key == "element":
                setattr(queryPlayer, "player_id", columns["player_id"].type.python_type(value))

            elif key == "position":
                setattr(queryPlayer, "squad_slot", columns["squad_slot"].type.python_type(value))

            elif key in Squad.__table__.columns.keys():
                python_type = columns[key].type.python_type
                setattr(queryPlayer, key, python_type(value))

        setattr(queryPlayer, "active_status", True)

        db.add(queryPlayer)

async def latest_transfer_time(db: AsyncSession) -> datetime | None:
    latest_buy = (await db.execute(select(func.max(Squad.buy_date)))).scalar()
    latest_sold = (await db.execute(select(func.max(Squad.sold_date)))).scalar()

    seen = [d for d in (latest_buy, latest_sold) if d is not None]
    return max(seen) if seen else None

async def process_transfers(client: httpx.AsyncClient, db: AsyncSession, team_id: str):
    transfers = await fetch_transfers(client, team_id)
    watermark = await latest_transfer_time(db)

    for transfer in transfers:
        transfer_time = datetime.fromisoformat(transfer["time"]).replace(tzinfo=None)

        #already recorded this one on a previous ingest
        if watermark is not None and transfer_time <= watermark:
            continue

        result = await db.execute(
            select(Squad).where(Squad.player_id == transfer["element_out"], Squad.active_status == True)
        )
        sold_row = result.scalar_one_or_none()
        if sold_row is not None:
            sold_row.sold = transfer["element_out_cost"] * 0.1
            sold_row.sold_date = transfer_time
            sold_row.sold_gw = transfer["event"]
            sold_row.active_status = False

        db.add(Squad(
            player_id=transfer["element_in"],
            buy_price=transfer["element_in_cost"] * 0.1,
            buy_date=transfer_time,
            buy_gw=transfer["event"],
            active_status=True,
        ))


async def read_squad(db: AsyncSession) -> list[Squad]:
    result = await db.execute(select(Squad))
    return result.scalars().all()

async def buy_cost(db: AsyncSession, id: int) -> float:
    match = await db.get(Squad, id)
    return match.buy_price

async def sell_cost(db: AsyncSession, id: int) -> float | None:
    match = await db.get(Squad, id)
    if match.active_status:
        return None

    else:
        return match.sold

async def fetch_fk(db: AsyncSession, id: int) -> int:
    match = await db.get(Squad, id)
    return match.player_id