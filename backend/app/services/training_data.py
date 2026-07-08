import httpx
import asyncio
TRAINING_SEASONS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]

async def fetch_all_hitters(season : int):
    async with httpx.AsyncClient() as client:
        response = await  client.get("https://statsapi.mlb.com/api/v1/stats", params = {"stats" : "season", "group" : "hitting", "season" : season, "sportId" : "1", "playerPool" : "All", "limit" : "1000"})
        return response.json()
    
def filter_by_min_pa(raw_data: dict, min_pa: int = 275) -> list:
    players = raw_data["stats"][0]["splits"]
    filtered_players = []
    for i in range(len(players)):
        player = players[i]
        if float(player["stat"]["plateAppearances"]) >= min_pa:
            filtered_players.append(player)

    return filtered_players

async def fetch_all_seasons(seasons: list) -> list :
    total_data = []
    for i in range(len(seasons)):
        raw_data = await fetch_all_hitters(seasons[i])
        raw_filtered_data = filter_by_min_pa(raw_data)
        total_data.extend(raw_filtered_data)

    return total_data

def group_by_player(all_seasons: list) -> dict:
    all_data = {}
    for i in range(len(all_seasons)):
        current_player = all_seasons[i]
        all_data.setdefault(current_player["player"]["id"], []).append(current_player)
    for player_id in all_data:
        all_data[player_id].sort(key=lambda entry: entry["season"])
    return all_data

def build_training_pairs(all_data : dict) -> list:
    pairs = []
    for player_id in all_data:
        seasons = all_data[player_id]
        for i in range(len(seasons)-1):
            pair = {}
            current_year = int(seasons[i]["season"])
            next_year = int(seasons[i+1]["season"])
            if next_year - current_year == 1 :
                pair["input"] = seasons[i]
                pair["label_source"] = seasons[i+1]
        pairs.append(pair)
    return pairs

