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

