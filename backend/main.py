from fastapi import FastAPI 
from app.services.mlb_client import search_player
from app.services.mlb_client import get_career_offense_stats
app = FastAPI()
@app.get("/")
def read_root():
    return {"status": "ok"}
@app.get("/players/search")
async def search_players(name:str):
    result = await search_player(name)
    return result

@app.get("/players/{player_id}/stats")
async def hitting_stats(player_id : int):
    result = await get_career_offense_stats(player_id)
    return result

