from sqlalchemy import String, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from database import Base

class Player(Base):
    __tablename__ = "player"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[int] = mapped_column(index=True) #stable across seasons, unlike id
    element_type: Mapped[int] = mapped_column(index=True)
    web_name: Mapped[str] = mapped_column(String(50), index=True)
    now_cost: Mapped[float] = mapped_column(index=True)
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
    total_points: Mapped[int] = mapped_column()


class PlayerGameweek(Base):
    __tablename__ = "player_gameweek"
    __table_args__ = (
        UniqueConstraint("player_code", "season", "round", name="uq_player_gameweek_code_season_round"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    player_code: Mapped[int] = mapped_column(index=True) #stable across seasons - the real join key
    element_id: Mapped[int] = mapped_column() #that season's FPL element id, not stable across seasons
    season: Mapped[str] = mapped_column(String(9))
    round: Mapped[int] = mapped_column(index=True)

    team: Mapped[Optional[int]] = mapped_column()
    opponent_team: Mapped[Optional[int]] = mapped_column()
    was_home: Mapped[Optional[bool]] = mapped_column()
    kickoff_time: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fixture_count: Mapped[int] = mapped_column()
    fixture_difficulty: Mapped[Optional[float]] = mapped_column()

    total_points: Mapped[int] = mapped_column()

    minutes: Mapped[int] = mapped_column()
    starts: Mapped[int] = mapped_column()

    goals_scored: Mapped[int] = mapped_column()
    assists: Mapped[int] = mapped_column()
    clean_sheets: Mapped[int] = mapped_column()
    goals_conceded: Mapped[int] = mapped_column()
    bonus: Mapped[int] = mapped_column()
    bps: Mapped[int] = mapped_column()
    ict_index: Mapped[float] = mapped_column()
    defensive_contribution: Mapped[int] = mapped_column()

    expected_goals: Mapped[float] = mapped_column()
    expected_assists: Mapped[float] = mapped_column()
    expected_goals_conceded: Mapped[float] = mapped_column()

    price: Mapped[float] = mapped_column()
    selected: Mapped[int] = mapped_column()
