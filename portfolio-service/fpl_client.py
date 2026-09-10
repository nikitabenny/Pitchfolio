import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager 
async def lifespan(app: FastAPI):
    async_client = httpx.AsyncClient(base_url = 'https://fantasy.premierleague.com/api/')
    app.state.client = async_client
    try:
        yield

    finally:
        await async_client.aclose()


async def fetch_transfers(client : httpx.AsyncClient, team_id : str) -> dict:
    #retrieve response 
    response = await client.get('entry/{team_id}/transfers/')

    #error code checking
    response.raise_for_status()
    return response.json()


async def fetch_squad(client : httpx.AsyncClient, team_id : str, gameweek_id : str) -> dict:
    #retrieve response 
    response = await client.get(f'entry/{team_id}/event/{gameweek_id}/picks/')

    #error code checking
    response.raise_for_status()
    return response.json()

async def fetch_my_history(client : httpx.AsyncClient, team_id: str) -> dict:
    #retrieve response 
    response = await client.get(f'entry/{team_id}/history/')

    #error code checking
    response.raise_for_status()
    return response.json()

async def fetch_bootstrap(client : httpx.AsyncClient) -> dict:
    #retrieve response
    response = await client.get('bootstrap-static/')

    #error code checking
    response.raise_for_status()
    return response.json()

async def fetch_now_cost(client : httpx.AsyncClient, player_id: int) -> float:
    #now_cost isn't exposed per-player, so pull the full bootstrap list and find this player
    data = await fetch_bootstrap(client)

    for element in data["elements"]:
        if element["id"] == player_id:
            return element["now_cost"] * 0.1

    raise ValueError(f"player {player_id} not found in bootstrap data")