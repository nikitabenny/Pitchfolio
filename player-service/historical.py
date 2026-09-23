import csv
import io
import httpx
from crud import build_gameweek_rows

RAW_BASE_URL = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data"


def fetch_id_code_map(season: str) -> dict[int, int]:
    #maps that season's FPL element id -> the stable player code, from vaastav's players_raw.csv
    url = f"{RAW_BASE_URL}/{season}/players_raw.csv"
    response = httpx.get(url, timeout=15)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    return {int(row["id"]): int(row["code"]) for row in reader}


def fetch_historical_gameweeks(season: str) -> list[dict]:
    #normalized into the same shape build_gameweek_rows already expects from the live API
    url = f"{RAW_BASE_URL}/{season}/gws/merged_gw.csv"
    response = httpx.get(url, timeout=30)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    rows = []
    for row in reader:
        rows.append({
            "element": int(row["element"]),
            "fixture": int(row["fixture"]),
            "opponent_team": int(row["opponent_team"]),
            "total_points": int(row["total_points"]),
            "was_home": row["was_home"] == "True",
            "kickoff_time": row["kickoff_time"],
            "round": int(row["round"]),
            "minutes": int(row["minutes"]),
            "goals_scored": int(row["goals_scored"]),
            "assists": int(row["assists"]),
            "clean_sheets": int(row["clean_sheets"]),
            "goals_conceded": int(row["goals_conceded"]),
            "bonus": int(row["bonus"]),
            "bps": int(row["bps"]),
            "defensive_contribution": int(row["defensive_contribution"]) if row.get("defensive_contribution") else 0,
            "starts": int(row["starts"]),
            "ict_index": float(row["ict_index"]),
            "expected_goals": float(row["expected_goals"]),
            "expected_assists": float(row["expected_assists"]),
            "expected_goals_conceded": float(row["expected_goals_conceded"]),
            "value": int(row["value"]),
            "selected": int(row["selected"]),
        })
    return rows


def fetch_historical_fixtures(season: str) -> dict[int, dict]:
    url = f"{RAW_BASE_URL}/{season}/fixtures.csv"
    response = httpx.get(url, timeout=30)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    fixtures_by_id = {}
    for row in reader:
        fixture_id = int(row["id"])
        fixtures_by_id[fixture_id] = {
            "team_h": int(row["team_h"]),
            "team_a": int(row["team_a"]),
            "team_h_difficulty": int(row["team_h_difficulty"]),
            "team_a_difficulty": int(row["team_a_difficulty"]),
        }
    return fixtures_by_id


def build_historical_rows(season: str) -> list[dict]:
    id_code_map = fetch_id_code_map(season)
    fixtures_by_id = fetch_historical_fixtures(season)
    gameweeks = fetch_historical_gameweeks(season)

    rows_by_element: dict[int, list[dict]] = {}
    for row in gameweeks:
        rows_by_element.setdefault(row["element"], []).append(row)

    all_rows = []
    for element_id, history in rows_by_element.items():
        player_code = id_code_map.get(element_id)
        if player_code is None:
            continue #shouldn't happen, but don't let one bad row sink the whole season's backfill

        all_rows.extend(build_gameweek_rows(player_code, season, history, fixtures_by_id))

    return all_rows
