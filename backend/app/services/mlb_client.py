import httpx

async def search_player(name:str):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://statsapi.mlb.com/api/v1/people/search", params ={"names" : name})
        return response.json()
    
async def get_career_offense_stats(player_id:int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats", params={"stats": "yearByYear", "group": "hitting"})
        return response.json()
    
async def get_career_fielding_stats(player_id:int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats", params={"stats": "yearByYear", "group": "fielding"})
        return response.json()