from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Player(Base):
    __tablename__ = "player"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    element_type: Mapped[int] = mapped_column(index=True)
    web_name: Mapped[str] = mapped_column(String(50), index=True)
    now_cost: Mapped[int] = mapped_column(index=True)
    goals_scored: Mapped[int] = mapped_column()
    assists: Mapped[int] = mapped_column()
    minutes: Mapped[int] = mapped_column()
    penalties_saved: Mapped[int] = mapped_column()
    penalties_missed: Mapped[int] = mapped_column()
    red_cards: Mapped[int] = mapped_column()
    creativity: Mapped[float] = mapped_column()
    expected_goals: Mapped[float] = mapped_column()
    expected_assists: Mapped[float] = mapped_column()
    expected_goals_conceded: Mapped[float] = mapped_column()
    clean_sheets: Mapped[int] = mapped_column()
    recoveries: Mapped[int] = mapped_column()
    tackles: Mapped[int] = mapped_column()
    points_per_game: Mapped[float] = mapped_column()
    defensive_contribution: Mapped[int] = mapped_column()
    bps: Mapped[int] = mapped_column()
