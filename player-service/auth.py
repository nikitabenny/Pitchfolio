import os
from fastapi import Header, HTTPException

API_KEY = os.environ["PLAYER_SERVICE_API_KEY"]

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid or missing API key")
