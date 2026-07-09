import httpx
import asyncio
from app.services.scoring import get_draft_score , get_position_multiplier, get_percentile_score
from app.services import league_references
TRAINING_SEASONS = [2018, 2019, 2021, 2022, 2023, 2024, 2025]

async def fetch_all_hitters(season: int):
    all_splits = []
    offset = 0
    limit = 1000
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get("https://statsapi.mlb.com/api/v1/stats", params={"stats": "season", "group": "hitting", "season": season, "sportId": "1", "playerPool": "All", "limit": str(limit), "offset": str(offset)})
            data = response.json()
            splits = data["stats"][0]["splits"]
            all_splits.extend(splits)
            total = data["stats"][0]["totalSplits"]
            offset += limit
            if offset >= total:
                break
    data["stats"][0]["splits"] = all_splits
    return data
    
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

async def fetch_all_fielders(season: int):
    all_splits = []
    offset = 0
    limit = 1000
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get("https://statsapi.mlb.com/api/v1/stats", params={"stats": "season", "group": "fielding", "season": season, "sportId": "1", "playerPool": "All", "limit": str(limit), "offset": str(offset)})
            data = response.json()
            splits = data["stats"][0]["splits"]
            all_splits.extend(splits)
            total = data["stats"][0]["totalSplits"]
            offset += limit
            if offset >= total:
                break
    data["stats"][0]["splits"] = all_splits
    return data
    
def build_fielding_lookup(raw_data: dict) -> dict:
    entries = raw_data["stats"][0]["splits"]
    lookup = {}
    for i in range(len(entries)):
        entry = entries[i]
        player_id = entry["player"]["id"]
        season = entry["season"]
        key = (player_id,season)
        innings = float(entry["stat"]["innings"])
        if key not in lookup:
            lookup[key]=entry
        else:
            existing_innings = float(lookup[key]["stat"]["innings"])
            if innings > existing_innings:
                lookup[key] = entry
    return lookup

def add_labels(pairs:list , fielding_lookup: dict) -> list:
    for i in range(len(pairs)):
        pair = pairs[i]
        label_season = pair["label_source"]
        player_id = label_season["player"]["id"]
        season = label_season["season"]
        age = int(label_season["stat"]["age"])
        position = label_season["position"]["abbreviation"]
        key = (player_id, season)

        if key in fielding_lookup:
            fielding_seasons = [fielding_lookup[key]]
        else:
            fielding_seasons = [{"stat" : {}}]
        offense_seasons = [label_season]

        score = get_draft_score(offense_seasons, fielding_seasons, age, position)
        pair["label"] = score
    return pairs

def extract_features(season_entry: dict) -> dict:
    ops = float(season_entry["stat"]["ops"])
    walks = float(season_entry ["stat"]["baseOnBalls"])
    strikeouts = float(season_entry["stat"]["strikeOuts"])
    if strikeouts == 0:
        discipline = 0    
    else:
        discipline = walks/strikeouts
    slg = float(season_entry["stat"]["slg"])
    avg = float(season_entry["stat"]["avg"])
    iso = slg - avg
    age = float(season_entry["stat"]["age"])
    position = season_entry["position"]["abbreviation"]
    position_value = get_position_multiplier(position)
    ops_scaled = get_percentile_score(ops, league_references.reference_distributions["ops"])
    discipline_scaled = get_percentile_score(discipline, league_references.reference_distributions["discipline"])
    iso_scaled = get_percentile_score(iso, league_references.reference_distributions["iso"])
    return {
        "ops" : ops_scaled,
        "discipline" : discipline_scaled,
        "iso" : iso_scaled, 
        "age" : age,
        "position" : position_value,
        }
