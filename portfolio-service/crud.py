from sqlalchemy.orm import Session
from sqlalchemy import inspect
from models import Squad

def upsert_squad(db:Session, squad:list[dict]):
    exists = db.query(Squad).all()
    squad_ids = {}
    for row in exists:
        squad_ids = row.id

    for pick in squad:
        if squad["id"] in squad_ids:
            queryPlayer = squad_ids.get(squad["id"])
        else:
            queryPlayer = Squad()

        columns = inspect(Squad).columns

        for key,value in pick.items():
            python_type = columns[key].type.python_type
            if key == "element":
                setattr(queryPlayer,"player_id",python_type(value))

            elif key == "position":
                setattr(queryPlayer,"id",python_type(value))

            else:
                if key in Squad.__table__.columns.keys():
                    setattr(queryPlayer,key,python_type(value))

        db.add(queryPlayer)
            

