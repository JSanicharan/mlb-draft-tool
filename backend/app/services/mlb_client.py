import httpx

async def search_player(name:str):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://statsapi.mlb.com/api/v1/people/search", params ={"names" : name})
        return response.json()
