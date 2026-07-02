from fastapi import FastAPI 
from app.services.mlb_client import search_player

app = FastAPI()
@app.get("/")
def read_root():
    return {"status": "ok"}
@app.get("/players/search")
async def search_players(name:str):
    result = await search_player(name)
    return result