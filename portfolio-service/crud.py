from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from models import Squad
from fpl_client import fetch_now_cost

async def upsert_squad(db: AsyncSession, picks: list[dict]):
    result = await db.execute(select(Squad))
    squad_by_player_id = {row.player_id: row for row in result.scalars().all()}

    columns = inspect(Squad).columns

    for pick in picks:
        if pick["element"] in squad_by_player_id:
            queryPlayer = squad_by_player_id[pick["element"]]
        else:
            queryPlayer = Squad()
            setattr(queryPlayer, "buy_price", set_live_data(db,pick['element'])[0])

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

async def set_live_data(db:AsyncSession, player_id: int) -> list[int]:
    ans = []
    now_cost = await fetch_now_cost(db,player_id)
    ans.append(now_cost)



async def read_squad(db: AsyncSession) -> list[Squad]:
    result = await db.execute(select(Squad))
    return result.scalars().all()

async def buy_cost(db: AsyncSession, id: int) -> float:
    match = await db.get(Squad, id)
    return match.buy_price

async def sell_cost(db: AsyncSession, id: int) -> float | None:
    match = await db.get(Squad, id)
    if not match.active_status:
        return None

    else:
        return match.sold

async def fetch_fk(db: AsyncSession, id: int) -> int:
    match = await db.get(Squad, id)
    return match.player_id
