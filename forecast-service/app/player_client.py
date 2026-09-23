import os
import httpx

PLAYER_SERVICE_URL = os.environ["PLAYER_SERVICE_URL"]
PLAYER_SERVICE_API_KEY = os.environ["PLAYER_SERVICE_API_KEY"]

PAGE_SIZE = 1000


def fetch_all_gameweeks() -> list[dict]:
    #pages through player-service's bulk endpoint until a short page signals the end
    all_rows = []
    offset = 0
    headers = {"X-API-Key": PLAYER_SERVICE_API_KEY}

    with httpx.Client(base_url=PLAYER_SERVICE_URL, headers=headers, timeout=30) as client:
        while True:
            response = client.get("/player-gameweeks", params={"limit": PAGE_SIZE, "offset": offset})
            response.raise_for_status()

            page = response.json()
            all_rows.extend(page)

            if len(page) < PAGE_SIZE:
                break

            offset += PAGE_SIZE

    return all_rows
