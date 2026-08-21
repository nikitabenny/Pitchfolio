from sqlalchemy.orm import Session
from sqlalchemy import inspect
from models import Player



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



    