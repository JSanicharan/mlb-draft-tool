from fastapi import FastAPI 
from app.services.mlb_client import search_player, get_career_offense_stats, get_career_fielding_stats, get_player_bundle
from app.services.scoring import get_draft_score
from fastapi.middleware.cors import CORSMiddleware
from app.services import league_references

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await league_references.refresh_reference_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def draft_score(player_id :int):
    bundle = await get_player_bundle(player_id)

    result = get_draft_score(bundle["offense_seasons"], bundle["fielding_seasons"], bundle["age"], bundle["position"])
    return result
     
@app.get("/players/{player_id}/profile")
async def profile(player_id :int):    
    bundle = await get_player_bundle(player_id)
    draft_score = get_draft_score(bundle["offense_seasons"], bundle["fielding_seasons"], bundle["age"], bundle["position"])
    headshot_url = (f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player_id}/headshot/67/current")

    return {
        "player": {
           "name": bundle["name"],
           "team": bundle["team"],
           "position": bundle["position"],
           "age": bundle["age"],
           "bat_side": bundle["bat_side"],
           "throw_side": bundle["throw_side"],
           "headshot_url": headshot_url,
       },
       "draft_score": draft_score,
       "ml_score": None,
       "ai_reasoning": None,
   }
