from fastapi import FastAPI 
from app.services.mlb_client import search_player, get_career_offense_stats, get_career_fielding_stats, get_player_info
from app.services.scoring import get_draft_score
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

@app.get("/players/{player_id}/fielding")
async def fielding_stats(player_id : int):
    result = await get_career_fielding_stats(player_id)
    return result

@app.get("/players/{player_id}/draft-score")
async def draft_score(player_id: int):
    offense = await get_career_offense_stats(player_id)
    defense = await get_career_fielding_stats(player_id)
    offense_seasons = offense["stats"][0]["splits"]
    fielding_seasons = defense["stats"][0]["splits"]
    player_info = await get_player_info(player_id)

    age =  player_info["people"][0]["currentAge"]
    position =  player_info["people"][0]["primaryPosition"]["abbreviation"]

    result = get_draft_score(offense_seasons, fielding_seasons, age, position)
    return result
     

