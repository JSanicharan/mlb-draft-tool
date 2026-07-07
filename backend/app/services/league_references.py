import httpx
import asyncio
async def fetch_qualified_hitters(season : int):
    async with httpx.AsyncClient() as client:
        response = await  client.get("https://statsapi.mlb.com/api/v1/stats", params = {"stats" : "season", "group" : "hitting", "season" : season, "sportId" : "1", "limit" : "200"})
        return response.json()
    
def build_reference_distributions(raw_data: dict):
    players = raw_data["stats"][0]["splits"]
    ops = []
    discipline = []
    iso = []
    for i in range(len(players)):
        player = players[i]
        ops.append(float(player["stat"]["ops"]))
        walk = float(player["stat"]["baseOnBalls"])
        strikeout = float(player["stat"]["strikeOuts"])
        discipline.append(walk/strikeout)
        season_avg = float(player["stat"]["avg"])
        season_slg = float(player["stat"]["slg"])
        iso.append(season_slg - season_avg)

    return {
        "ops": ops,
        "discipline": discipline,
        "iso": iso,
    }