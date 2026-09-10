from sqlalchemy import select, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from models import Squad

async def upsert_squad(db: AsyncSession, picks: list[dict]):
    result = await db.execute(select(Squad))
    squad_by_id = {row.id: row for row in result.scalars().all()}

    columns = inspect(Squad).columns

    for pick in picks:
        if pick["position"] in squad_by_id:
            queryPlayer = squad_by_id[pick["position"]]
        else:
            queryPlayer = Squad()

        for key, value in pick.items():
            if key == "element":
                setattr(queryPlayer, "player_id", columns["player_id"].type.python_type(value))

            elif key == "position":
                setattr(queryPlayer, "id", columns["id"].type.python_type(value))

            elif key in Squad.__table__.columns.keys():
                python_type = columns[key].type.python_type
                setattr(queryPlayer, key, python_type(value))

        db.add(queryPlayer)


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
