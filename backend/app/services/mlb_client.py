import httpx
import asyncio

async def search_player(name:str):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://statsapi.mlb.com/api/v1/people/search", params ={"names" : name})
        return response.json()
    
async def get_player_info(player_id:int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}", params ={"hydrate" : "currentTeam"})
        return response.json()
    
async def get_career_offense_stats(player_id:int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats", params={"stats": "yearByYear", "group": "hitting"})
        return response.json()
    
async def get_career_fielding_stats(player_id:int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats", params={"stats": "yearByYear", "group": "fielding"})
        return response.json()

async def get_player_bundle(player_id : int):
    player_info, offense, defense = await asyncio.gather(
    get_player_info(player_id),
    get_career_offense_stats(player_id),
    get_career_fielding_stats(player_id)
    )
    offense_seasons = offense["stats"][0]["splits"]
    fielding_seasons = defense["stats"][0]["splits"]
    age =  player_info["people"][0]["currentAge"]
    position =  player_info["people"][0]["primaryPosition"]["abbreviation"]
    name = player_info["people"][0]["fullName"]
    team = player_info["people"][0]["currentTeam"]["name"]
    bat_side = player_info["people"][0]["batSide"]
    throw_side = player_info["people"][0]["pitchHand"]


    return{
    "offense_seasons": offense_seasons,
    "fielding_seasons": fielding_seasons,
    "age": age,
    "position": position,
    "name": name,
    "team": team,
    "bat_side": bat_side,
    "throw_side": throw_side,
    }