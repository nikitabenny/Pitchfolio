from sqlalchemy import String, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Squad(Base):
    __tablename__ = "squad"
    id: Mapped[int] = mapped_column(primary_key=True, index=True) #PK
    player_id: Mapped[int] = mapped_column(primary_key=True, index=True) #FK
    squad_slot: Mapped[int] = mapped_column()
    is_captain: Mapped[bool] = mapped_column()
    is_vice_captain: Mapped[bool] = mapped_column()

    buy_price: Mapped[float] = mapped_column()
    buy_date: Mapped[datetime] = mapped_column(DateTime)
    buy_gw: Mapped[int] = mapped_column(int)

    sold: Mapped[float] = mapped_column()
    sold_date: Mapped[datetime] = mapped_column(DateTime)
    sold_gw: Mapped[int] = mapped_column(int)
    active_status: Mapped[bool] = mapped_column(bool)


# class Squad_Info(Base):
#     __tablename__ = "squad_info"
#     event : Mapped[int] = mapped_column()
#     event_points : Mapped[int] = mapped_column