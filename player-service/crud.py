from sqlalchemy.orm import Session
from sqlalchemy import inspect, func
from datetime import datetime
from models import Player, PlayerGameweek

SUMMED_INT_FIELDS = [
    "total_points", "minutes", "starts", "goals_scored", "assists",
    "clean_sheets", "goals_conceded", "bonus", "bps", "defensive_contribution",
]
SUMMED_FLOAT_FIELDS = ["ict_index", "expected_goals", "expected_assists", "expected_goals_conceded"]


def build_gameweek_rows(player_code: int, season: str, history: list[dict], fixtures_by_id: dict[int, dict]) -> list[dict]:
    by_round: dict[int, list[dict]] = {}
    for row in history:
        by_round.setdefault(row["round"], []).append(row)

    results = []
    for round_number, rows in by_round.items():
        fixture_count = len(rows)
        first = rows[0]
        last = rows[-1]

        #a double gameweek's fixtures are always for the same team, just different opponents,
        #so "team" is unambiguous even when opponent/was_home/kickoff_time aren't
        first_fixture = fixtures_by_id.get(first["fixture"])
        team = None
        if first_fixture is not None:
            team = first_fixture["team_h"] if first["was_home"] else first_fixture["team_a"]

        difficulties = []
        for row in rows:
            fixture = fixtures_by_id.get(row["fixture"])
            if fixture is not None:
                difficulties.append(fixture["team_h_difficulty"] if row["was_home"] else fixture["team_a_difficulty"])

        result = {
            "player_code": player_code,
            "element_id": first["element"],
            "season": season,
            "round": round_number,
            "team": team,
            "fixture_count": fixture_count,
            "fixture_difficulty": (sum(difficulties) / len(difficulties)) if difficulties else None,
            "opponent_team": first["opponent_team"] if fixture_count == 1 else None,
            "was_home": first["was_home"] if fixture_count == 1 else None,
            "kickoff_time": datetime.fromisoformat(first["kickoff_time"]).replace(tzinfo=None) if fixture_count == 1 else None,
            "price": last["value"] * 0.1,
            "selected": last["selected"],
        }

        for field in SUMMED_INT_FIELDS:
            result[field] = sum(int(row.get(field, 0)) for row in rows)

        for field in SUMMED_FLOAT_FIELDS:
            result[field] = sum(float(row.get(field, 0)) for row in rows)

        results.append(result)

    return results


def read_gameweeks(db: Session, season: str | None = None, player_code: int | None = None,
                    limit: int = 1000, offset: int = 0) -> list[PlayerGameweek]:
    query = db.query(PlayerGameweek)
    if season is not None:
        query = query.filter(PlayerGameweek.season == season)
    if player_code is not None:
        query = query.filter(PlayerGameweek.player_code == player_code)
    #stable ordering is required for offset-based paging to be consistent across calls
    return query.order_by(PlayerGameweek.id).limit(limit).offset(offset).all()


def max_ingested_round(db: Session, player_code: int, season: str) -> int | None:
    return db.query(func.max(PlayerGameweek.round)).filter(
        PlayerGameweek.player_code == player_code,
        PlayerGameweek.season == season,
    ).scalar()


def upsert_player_gameweek(db: Session, rows: list[dict]):
    for row in rows:
        existing = db.query(PlayerGameweek).filter(
            PlayerGameweek.player_code == row["player_code"],
            PlayerGameweek.season == row["season"],
            PlayerGameweek.round == row["round"],
        ).one_or_none()
        if existing is None:
            existing = PlayerGameweek()

        for key, value in row.items():
            setattr(existing, key, value)

        db.add(existing)



def upsert_player(db:Session, all_players:list[dict]):
    exists = db.query(Player).all()
    ids = {row.id: row for row in exists}

    for player in all_players:
        if player["id"] in ids:
            queryPlayer = ids.get(player["id"])

        else:
            queryPlayer = Player()

        columns = inspect(Player).columns
        for key,value in player.items():
            if key in Player.__table__.columns.keys():
                python_type = columns[key].type.python_type
                if key == "now_cost":
                    value *= 0.1

                setattr(queryPlayer,key,python_type(value))

        #allows sql alchemy to start tracking for commit
        db.add(queryPlayer)

    #forces caller to commit so recommit doesnt happen for each player

def read_players(db:Session) -> list[Player]:
    myPlayers = db.query(Player).all()
    return myPlayers

def find_player_by_id(id: int, db:Session) -> Player:
    myPlayer = db.get(Player, id)
    return myPlayer

def find_player_by_eltype(eltype: str, db:Session) -> list[Player]:
    if eltype == "GK":
        pos_int = 1
    elif eltype == "DEF" :
        pos_int = 2
    elif eltype == "MID":
        pos_int = 3
    else:
        pos_int = 4
    posPlayers = db.query(Player).filter(Player.element_type == pos_int).all()
    return posPlayers

def under_budget(price: float, db:Session) -> list[Player]:
    posPlayers = db.query(Player).filter(Player.now_cost <= price).all()
    return posPlayers

def pos_price_match(eltype: str, price:float, db:Session) -> list[Player]:
    if eltype == "GK":
        pos_int = 1
    elif eltype == "DEF" :
        pos_int = 2
    elif eltype == "MID":
        pos_int = 3
    else:
        pos_int = 4

    matches = db.query(Player).filter(Player.element_type == pos_int, Player.now_cost <= price).all()
    return matches

def find_player_points(id: int, db: Session) -> int:
    match = db.query(Player).filter(Player.id == id).first()
    return match.total_points()

def find_player_value(id: int, db: Session) -> int:
    match = db.query(Player).filter(Player.id == id).first()
    return match.now_cost()




    