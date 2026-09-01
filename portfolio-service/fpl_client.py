import httpx
from fastapi import FastAPI
from contextlib import asynccontextmanager

PLAYER_SERVICE_URL = "http://player-service:8000/"


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
    response = await client.get(f'entry/{team_id}/transfers/event/{gameweek_id}/picks/')

    #error code checking
    response.raise_for_status()
    return response.json()

async def fetch_my_history(client : httpx.AsyncClient, team_id: str) -> dict:
    #retrieve response 
    response = await client.get(f'entry/{team_id}/history/')

    #error code checking
    response.raise_for_status()
    return response.json()