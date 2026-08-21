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



    