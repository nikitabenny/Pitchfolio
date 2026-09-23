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


async def fetch_bootstrap(client : httpx.AsyncClient) -> dict:
    #retrieve response 
    response = await client.get('bootstrap-static/')

    #error code checking
    response.raise_for_status()
    return response.json()

async def fetch_history(client : httpx.AsyncClient, player_id : int) -> dict:
    response = await client.get(f'element-summary/{player_id}/')

    response.raise_for_status()
    return response.json()

async def fetch_fixtures(client : httpx.AsyncClient) -> list[dict]:
    response = await client.get('fixtures/')

    response.raise_for_status()
    return response.json()

async def fetch_current_gameweek(client : httpx.AsyncClient) -> int:
    data = await fetch_bootstrap(client)

    for event in data["events"]:
        if event["is_current"]:
            return event["id"]

    raise ValueError("no current gameweek found in bootstrap data")

