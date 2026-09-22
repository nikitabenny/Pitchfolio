from datetime import datetime

import pytest

from models import Squad
from crud import upsert_squad, process_transfers, buy_cost, sell_cost, read_squad

TRANSFER_SELL_102_BUY_103 = [
    {"element_in": 103, "element_in_cost": 45, "element_out": 102, "element_out_cost": 62, "event": 2, "time": "2024-08-15T09:00:00Z"},
]
PICKS_AFTER_TRANSFER = {"picks": [
    {"element": 101, "position": 1, "multiplier": 1, "is_captain": True, "is_vice_captain": False},
    {"element": 103, "position": 2, "multiplier": 1, "is_captain": False, "is_vice_captain": True},
]}


async def seed_initial_squad(db_session):
    #bypasses upsert_squad's bootstrap branch on purpose (see crud.py:25 buy_date bug) - seeds rows directly
    db_session.add(Squad(player_id=101, squad_slot=1, is_captain=True, is_vice_captain=False,
                          buy_price=5.0, buy_date=datetime(2024, 8, 1), buy_gw=1, active_status=True))
    db_session.add(Squad(player_id=102, squad_slot=2, is_captain=False, is_vice_captain=True,
                          buy_price=6.0, buy_date=datetime(2024, 8, 1), buy_gw=1, active_status=True))
    await db_session.commit()


async def test_process_transfers_closes_sold_row_and_opens_bought_row(db_session, fake_client):
    await seed_initial_squad(db_session)
    fake_client.mock_responses["transfers"] = TRANSFER_SELL_102_BUY_103

    await process_transfers(fake_client, db_session, "999")
    await db_session.commit()

    squad = {row.player_id: row for row in await read_squad(db_session)}

    sold_row = squad[102]
    assert sold_row.active_status is False
    assert sold_row.sold == pytest.approx(6.2)
    assert sold_row.sold_gw == 2

    bought_row = squad[103]
    assert bought_row.active_status is True
    assert bought_row.buy_price == pytest.approx(4.5)
    assert bought_row.buy_gw == 2


async def test_sell_cost_reflects_active_status(db_session, fake_client):
    await seed_initial_squad(db_session)
    fake_client.mock_responses["transfers"] = TRANSFER_SELL_102_BUY_103
    await process_transfers(fake_client, db_session, "999")
    await db_session.commit()

    squad = {row.player_id: row for row in await read_squad(db_session)}
    assert await sell_cost(db_session, squad[101].id) is None
    assert await sell_cost(db_session, squad[102].id) == pytest.approx(6.2)


async def test_reingest_squad_updates_existing_row_without_duplicating(db_session, fake_client):
    await seed_initial_squad(db_session)
    fake_client.mock_responses["transfers"] = TRANSFER_SELL_102_BUY_103
    await process_transfers(fake_client, db_session, "999")
    await db_session.commit()

    await upsert_squad(fake_client, db_session, PICKS_AFTER_TRANSFER["picks"], "999")
    await db_session.commit()

    rows = await read_squad(db_session)
    assert len(rows) == 3

    row_103 = next(r for r in rows if r.player_id == 103)
    assert row_103.squad_slot == 2
    assert row_103.is_captain is False
    assert row_103.is_vice_captain is True


async def test_rebuy_opens_new_row_and_preserves_old_sale(db_session, fake_client):
    await seed_initial_squad(db_session)
    fake_client.mock_responses["transfers"] = TRANSFER_SELL_102_BUY_103
    await process_transfers(fake_client, db_session, "999")
    await db_session.commit()

    #later gameweek: sell 103, buy 102 back
    fake_client.mock_responses["transfers"] = TRANSFER_SELL_102_BUY_103 + [
        {"element_in": 102, "element_in_cost": 58, "element_out": 103, "element_out_cost": 46, "event": 3, "time": "2024-08-22T09:00:00Z"},
    ]
    await process_transfers(fake_client, db_session, "999")
    await db_session.commit()

    player_102_rows = [r for r in await read_squad(db_session) if r.player_id == 102]
    assert len(player_102_rows) == 2

    original_sale = next(r for r in player_102_rows if r.active_status is False)
    assert original_sale.sold == pytest.approx(6.2)
    assert original_sale.sold_gw == 2

    new_buy = next(r for r in player_102_rows if r.active_status is True)
    assert new_buy.buy_price == pytest.approx(5.8)
    assert new_buy.buy_gw == 3
